# This file will should not be checked in as-is. It's for prototyping async usage of the SDK.
import anyio
from tollbit import currencies, licences, content_formats, use_content
from tollbit._apis.token_api import AsyncTokenAPI
from tollbit._apis.content_retrieval_api import AsyncContentRetrievalAPI
from tollbit._apis.models import CreateSubdomainAccessTokenRequest
from tollbit.tokens import TollbitToken
import os

from tollbit._environment import env_from_vars

api_key = os.getenv("TOLLBIT_ORG_API_KEY", "YOUR_API_KEY_HERE")
user_agent = os.getenv("TOLLBIT_USER_AGENT", "tollbit-python-sdk-example/0.1.0")


async def run_individual_apis():
    print("====== RUNNING INDIVIDUAL APIS ======")
    env = env_from_vars()
    async_token_api = AsyncTokenAPI(
        api_key=api_key,
        user_agent=user_agent,
        env=env,
    )

    async_content_retrieval_api = AsyncContentRetrievalAPI(
        user_agent=user_agent,
        env=env,
    )

    req = CreateSubdomainAccessTokenRequest(
        url="https://pioneervalleygazette.com/daydream",
        user_agent=user_agent,
        max_price_micros=11000000,
        currency=currencies.USD,
        license_type=licences.types.ON_DEMAND_LICENSE,
        license_cuid="",
    )

    resp = await async_token_api.get_content_token(req)
    print("Async token response:", resp)

    content = await async_content_retrieval_api.get_content(
        content_url="https://pioneervalleygazette.com/daydream",
        token=TollbitToken(resp.token),
        format=content_formats.MARKDOWN,
    )
    print("Async content response:", content)
    print("====== END RUNNING INDIVIDUAL APIS ======")


async def run_client():
    print("====== RUNNING CLIENT ======")
    client = use_content.create_async_client(secret_key=api_key, user_agent=user_agent)

    data = await client.get_sanctioned_content(
        url="https://pioneervalleygazette.com/daydream",
        max_price_micros=11000000,
        currency=currencies.USD,
        license_type=licences.types.ON_DEMAND_LICENSE,
    )
    print("Async client content response:", data)
    print("====== END RUNNING CLIENT ======")


async def main():
    await run_individual_apis()
    await run_client()


anyio.run(main)
