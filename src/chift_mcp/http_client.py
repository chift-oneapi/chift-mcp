from chift.api.client import ChiftAuth
from httpx import AsyncClient, Auth, Request


class ClientAuth(Auth):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        account_id: str,
        base_url: str | None = None,
        env_id: str | None = None,
        test_client: bool | None = None,
    ):
        self.chift_auth = ChiftAuth(
            client_id, client_secret, account_id, base_url, env_id, test_client
        )

    def auth_flow(self, request: Request):
        request.headers.update(self.chift_auth.get_auth_header())
        yield request


def get_http_client(
    client_id: str, client_secret: str, account_id: str, base_url: str
) -> AsyncClient:
    return AsyncClient(
        base_url=base_url,
        auth=ClientAuth(
            client_id=client_id,
            client_secret=client_secret,
            account_id=account_id,
            base_url=base_url,
        ),
    )
