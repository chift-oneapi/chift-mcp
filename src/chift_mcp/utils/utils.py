import chift

from chift_mcp.config import Chift


def configure_chift(chift_config: Chift) -> None:
    """Configure global Chift client settings."""
    chift.client_secret = chift_config.client_secret
    chift.client_id = chift_config.client_id
    chift.account_id = chift_config.account_id
    chift.url_base = chift_config.url_base


def get_connection_types(consumer_id: str | None = None) -> list[str]:
    """
    Get the connection types for a consumer.

    Args:
        consumer_id (str): The consumer ID

    Returns:
        list[str]: The connection types
    """
    if consumer_id is None:
        return list(CONNECTION_TYPES.values())

    consumer = chift.Consumer.get(chift_id=consumer_id)

    connections = consumer.Connection.all()

    return [CONNECTION_TYPES[connection.api] for connection in connections]


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
