from chift.api.client import ChiftAuth
from httpx import AsyncClient, Auth, Request

from chift_mcp.config import Chift


class ClientAuth(Auth):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        account_id: str,
        url_base: str,
    ):
        self.chift_auth = ChiftAuth(
            client_id,
            client_secret,
            account_id,
            url_base,
            None,
            None,
        )

    def auth_flow(self, request: Request):
        request.headers.update(self.chift_auth.get_auth_header())
        yield request


def get_http_client(
    chift_config: Chift | None,
    url_base: str,
    is_remote: bool,
) -> AsyncClient:
    if not is_remote and not chift_config:
        raise ValueError("Chift config is not set for local mode")
    if is_remote and chift_config:
        raise ValueError("Chift config is set for remote mode")

    return AsyncClient(
        base_url=url_base,
        auth=ClientAuth(
            chift_config.client_id, chift_config.client_secret, chift_config.account_id, url_base
        )
        if chift_config
        else None,
    )
