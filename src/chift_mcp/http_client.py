from chift.api.client import ChiftAuth
from httpx import AsyncClient, Auth, Request

from chift_mcp.config import Chift


class ClientAuth(Auth):
    def __init__(
        self,
        chift_config: Chift,
    ):
        self.chift_auth = ChiftAuth(
            chift_config.client_id,
            chift_config.client_secret,
            chift_config.account_id,
            chift_config.url_base,
            None,
            None,
        )

    def auth_flow(self, request: Request):
        request.headers.update(self.chift_auth.get_auth_header())
        yield request


def get_http_client(
    chift_config: Chift | None,
    url_base: str,
) -> AsyncClient:
    return AsyncClient(base_url=url_base, auth=ClientAuth(chift_config) if chift_config else None)
