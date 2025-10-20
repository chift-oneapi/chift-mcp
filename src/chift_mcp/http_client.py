import typing

from datetime import datetime

from chift.api.client import httplib
from httpx import AsyncClient, Auth, Request, Response

from chift_mcp.config import Chift


class ClientAuth(Auth):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        account_id: str,
        url_base: str,
        marketplace_id: str | None = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.account_id = account_id
        self.url_base = url_base
        self.marketplace_id = marketplace_id
        self.access_token: str | None = None
        self.expires_at: datetime | None = None
        self.request_engine = AsyncClient(base_url=url_base)

    def _parse_token(self, token: dict):
        self.access_token = token.get("access_token")
        self.expires_at = datetime.fromtimestamp(token.get("expires_on", 0))

    async def get_access_token(self):
        if self.access_token and self.expires_at and datetime.now() < self.expires_at:
            return self.access_token

        payload = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret,
            "accountId": self.account_id,
        }
        if self.marketplace_id:
            payload["marketplaceId"] = self.marketplace_id

        response = await self.request_engine.post(self.url_base + "/token", json=payload)

        if not response.status_code == httplib.OK:
            raise ValueError(
                f"Error while authenticating '{response.status_code}': {response.text}"
            )

        self._parse_token(response.json())

        return self.access_token

    async def get_auth_header(self):
        return {
            "Authorization": f"Bearer {await self.get_access_token()}",
        }

    async def async_auth_flow(self, request: Request) -> typing.AsyncGenerator[Request, Response]:
        print("async_auth_flow")
        if self.requires_request_body:
            await request.aread()

        flow = self.auth_flow(request)
        request = await anext(flow)

        while True:
            response = yield request
            if self.requires_response_body:
                await response.aread()

            try:
                request = await flow.asend(response)
            except StopAsyncIteration:
                break

    async def auth_flow(self, request: Request):
        request.headers.update(await self.get_auth_header())
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
            chift_config.client_id,
            chift_config.client_secret.get_secret_value(),
            chift_config.account_id,
            url_base,
            chift_config.marketplace_id,
        )
        if chift_config
        else None,
    )
