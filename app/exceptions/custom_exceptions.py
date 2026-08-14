class AppException(Exception):
    """Base exception for the application."""
    pass


class EmailAlreadyExistsException(AppException):
    pass


class InvalidCredentialsException(AppException):
    pass


class UserNotFoundException(AppException):
    pass


class RoleNotFoundException(AppException):
    pass


class InvalidTokenException(AppException):
    pass


class InvalidRefreshTokenException(AppException):
    pass


class RefreshTokenExpiredException(AppException):
    pass

class PasswordResetTokenInvalidException(AppException):
    pass


class PasswordResetTokenExpiredException(AppException):
    pass

class WarehouseNotFoundException(AppException):
    pass


class WarehouseCodeAlreadyExistsException(AppException):
    pass


class WarehouseDisabledException(AppException):
    pass

class WarehouseAlreadyActiveException(AppException):
    pass


class InvalidWarehouseCapacityException(AppException):
    pass

class WarehouseManagerNotFoundException(AppException):
    pass


class InvalidWarehouseManagerException(AppException):
    pass


class ManagerAlreadyAssignedException(AppException):
    pass

class SupplierNotFoundException(AppException):
    pass


class SupplierEmailAlreadyExistsException(AppException):
    pass


class SupplierGSTAlreadyExistsException(AppException):
    pass


class SupplierSuspendedException(AppException):
    pass


class SupplierAlreadyActiveException(AppException):
    pass

class CategoryNotFoundException(AppException):
    pass


class CategoryAlreadyExistsException(AppException):
    pass


class CategoryArchivedException(AppException):
    pass


class CategoryAlreadyActiveException(AppException):
    pass

class ProductNotFoundException(AppException):
    pass


class ProductSKUAlreadyExistsException(AppException):
    pass


class ProductBarcodeAlreadyExistsException(AppException):
    pass


class ProductCategoryNotFoundException(AppException):
    pass


class ProductArchivedException(AppException):
    pass


class ProductAlreadyActiveException(AppException):
    pass

class InventoryNotFoundException(AppException):
    pass

class InsufficientReservedStockException(AppException):
    pass


class ProductNotAvailableException(AppException):
    pass


class WarehouseNotAvailableException(AppException):
    pass


class InsufficientStockException(AppException):
    pass


class InvalidStockQuantityException(AppException):
    pass

class PurchaseOrderNotFoundException(AppException):
    pass


class PurchaseOrderAlreadyExistsException(AppException):
    pass


class InvalidPurchaseOrderStatusException(AppException):
    pass

class PurchaseOrderAlreadyReceivedException(AppException):
    pass


class InvalidPurchaseOrderReceiveException(AppException):
    pass


class PurchaseOrderAlreadyApprovedException(AppException):
    pass


class PurchaseOrderRejectedException(AppException):
    pass


class PurchaseOrderCancelledException(AppException):
    pass


class InvalidPurchaseOrderItemException(AppException):
    pass


class SupplierNotAvailableException(AppException):
    pass

class TransferNotFoundException(AppException):
    pass


class InvalidTransferException(AppException):
    pass


class TransferAlreadyApprovedException(AppException):
    pass


class TransferAlreadyRejectedException(AppException):
    pass


class TransferNotReadyException(AppException):
    pass


class InsufficientStockException(AppException):
    pass


class SameWarehouseTransferException(AppException):
    pass

class AlertNotFoundException(AppException):
    pass


class AlertAlreadyAcknowledgedException(AppException):
    pass