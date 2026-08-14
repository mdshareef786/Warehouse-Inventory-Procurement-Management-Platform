import math

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.alert import InventoryAlert
from app.models.inventory import Inventory
from app.models.product import Product

from app.repositories.alert_repository import (
    AlertRepository,
)

from app.exceptions.custom_exceptions import (
    AlertNotFoundException,
    AlertAlreadyAcknowledgedException,
)

from app.core.websocket_manager import manager


class AlertService:

    # =========================================================
    # INVENTORY ALERT CHECK
    # =========================================================

    @staticmethod
    def check_inventory_alert(
        db: Session,
        inventory: Inventory,
    ):
        """
        Check inventory level and create/update an alert.

        Rules:
        - quantity <= 0
            -> OUT_OF_STOCK

        - quantity <= reorder_level
            -> LOW_STOCK

        - quantity > reorder_level
            -> No alert

        Existing unacknowledged alerts are updated
        instead of creating duplicate alerts.

        A WebSocket notification is published whenever
        an alert is created or updated.
        """

        # -----------------------------------------------------
        # Get product
        # -----------------------------------------------------

        product = (
            db.query(Product)
            .filter(
                Product.id == inventory.product_id
            )
            .first()
        )

        if not product:
            return None

        # -----------------------------------------------------
        # Current inventory values
        # -----------------------------------------------------

        quantity = float(
            inventory.available_quantity or 0
        )

        reorder_level = float(
            product.reorder_level or 0
        )

        # -----------------------------------------------------
        # Determine alert type
        # -----------------------------------------------------

        if quantity <= 0:

            alert_type = "OUT_OF_STOCK"

        elif quantity <= reorder_level:

            alert_type = "LOW_STOCK"

        else:

            # Inventory level is healthy.
            return None

        # -----------------------------------------------------
        # Check existing unacknowledged alert
        # -----------------------------------------------------

        existing_alert = (
            db.query(InventoryAlert)
            .filter(
                InventoryAlert.product_id
                == inventory.product_id,

                InventoryAlert.warehouse_id
                == inventory.warehouse_id,

                InventoryAlert.alert_type
                == alert_type,

                InventoryAlert.is_acknowledged
                == False,
            )
            .first()
        )

        # =====================================================
        # UPDATE EXISTING ALERT
        # =====================================================

        if existing_alert:

            existing_alert.current_quantity = quantity

            db.flush()

            # -------------------------------------------------
            # Real-time WebSocket notification
            # -------------------------------------------------

            manager.publish(
                {
                    "type": "inventory_alert_updated",

                    "alert_id": existing_alert.id,

                    "alert_type": existing_alert.alert_type,

                    "product_id": existing_alert.product_id,

                    "warehouse_id": existing_alert.warehouse_id,

                    "current_quantity": float(
                        existing_alert.current_quantity or 0
                    ),

                    "reorder_level": reorder_level,

                    "is_acknowledged": (
                        existing_alert.is_acknowledged
                    ),
                }
            )

            return existing_alert

        # =====================================================
        # CREATE NEW ALERT
        # =====================================================

        alert = InventoryAlert(
            product_id=inventory.product_id,
            warehouse_id=inventory.warehouse_id,
            current_quantity=quantity,
            alert_type=alert_type,
            is_acknowledged=False,
        )

        AlertRepository.create(
            db,
            alert,
        )

        # Make sure the database-generated ID is available
        db.flush()

        # -----------------------------------------------------
        # Real-time WebSocket notification
        # -----------------------------------------------------

        manager.publish(
            {
                "type": "inventory_alert",

                "alert_id": alert.id,

                "alert_type": alert.alert_type,

                "product_id": alert.product_id,

                "warehouse_id": alert.warehouse_id,

                "current_quantity": float(
                    alert.current_quantity or 0
                ),

                "reorder_level": reorder_level,

                "is_acknowledged": (
                    alert.is_acknowledged
                ),
            }
        )

        return alert

    # =========================================================
    # GET ALERTS
    # =========================================================

    @staticmethod
    def get_alerts(
        db: Session,
        page: int,
        page_size: int,
        alert_type: str | None = None,
        is_acknowledged: bool | None = None,
        warehouse_id: int | None = None,
        product_id: int | None = None,
    ):

        items, total = (
            AlertRepository.get_all(
                db=db,
                page=page,
                page_size=page_size,
                alert_type=alert_type,
                is_acknowledged=is_acknowledged,
                warehouse_id=warehouse_id,
                product_id=product_id,
            )
        )

        total_pages = (
            math.ceil(total / page_size)
            if total
            else 0
        )

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    # =========================================================
    # ACKNOWLEDGE ALERT
    # =========================================================

    @staticmethod
    def acknowledge(
        db: Session,
        alert_id: int,
    ):

        alert = AlertRepository.get_by_id(
            db,
            alert_id,
        )

        if not alert:
            raise AlertNotFoundException(
                "Alert not found"
            )

        if alert.is_acknowledged:

            raise AlertAlreadyAcknowledgedException(
                "Alert is already acknowledged"
            )

        # -----------------------------------------------------
        # Acknowledge
        # -----------------------------------------------------

        alert.is_acknowledged = True

        alert.acknowledged_at = (
            datetime.now(timezone.utc)
        )

        db.commit()

        db.refresh(alert)

        # -----------------------------------------------------
        # Real-time WebSocket notification
        # -----------------------------------------------------

        manager.publish(
            {
                "type": "inventory_alert_acknowledged",

                "alert_id": alert.id,

                "alert_type": alert.alert_type,

                "product_id": alert.product_id,

                "warehouse_id": alert.warehouse_id,

                "current_quantity": float(
                    alert.current_quantity or 0
                ),

                "is_acknowledged": True,

                "acknowledged_at": (
                    alert.acknowledged_at
                ),
            }
        )

        return alert