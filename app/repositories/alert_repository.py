from sqlalchemy.orm import Session

from app.models.alert import InventoryAlert


class AlertRepository:

    @staticmethod
    def create(
        db: Session,
        alert: InventoryAlert,
    ):
        db.add(alert)
        db.flush()
        return alert

    @staticmethod
    def get_by_id(
        db: Session,
        alert_id: int,
    ):
        return (
            db.query(InventoryAlert)
            .filter(
                InventoryAlert.id == alert_id
            )
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        page: int,
        page_size: int,
        alert_type: str | None = None,
        is_acknowledged: bool | None = None,
        warehouse_id: int | None = None,
        product_id: int | None = None,
    ):
        query = db.query(InventoryAlert)

        if alert_type:
            query = query.filter(
                InventoryAlert.alert_type
                == alert_type.upper()
            )

        if is_acknowledged is not None:
            query = query.filter(
                InventoryAlert.is_acknowledged
                == is_acknowledged
            )

        if warehouse_id is not None:
            query = query.filter(
                InventoryAlert.warehouse_id
                == warehouse_id
            )

        if product_id is not None:
            query = query.filter(
                InventoryAlert.product_id
                == product_id
            )

        total = query.count()

        items = (
            query
            .order_by(
                InventoryAlert.id.desc()
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total