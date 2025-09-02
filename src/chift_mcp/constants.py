CHIFT_OPERATION_TYPES = {"get", "create", "update", "add"}

CONNECTION_TYPES = {
    "Accounting": "accounting",
    "Point of Sale": "pos",
    "eCommerce": "ecommerce",
    "Invoicing": "invoicing",
    "Banking": "banking",
    "Payment": "payment",
    "Property Management System": "pms",
    "Custom": "custom",
}

CHIFT_DOMAINS = set(CONNECTION_TYPES.values())

DEFAULT_CONFIG = {domain: list(CHIFT_OPERATION_TYPES) for domain in CHIFT_DOMAINS}
