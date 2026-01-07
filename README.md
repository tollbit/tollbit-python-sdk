<p align="center">
  <img alt="Tollbit" src="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExaThrOTR0MGRwNzVubDhqYmJ0eHF4OXg3dXk2aXF4Nm1vdDY4NHZ1cCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/LQpFMg2ZY648ndTv0r/giphy.gif" width="500">
</p>

<h3 align="center">Tollbit: Front Door Access for AI Agents</h2>

<p align="center">Web automation, API access, and content access all through a standard entry point.</p>

<br>

<p align="center">
  <a href="https://github.com/tollbit/tollbit-python-sdk/stargazers"><img src="https://img.shields.io/github/stars/tollbit/tollbit-python-sdk?style=social" alt="GitHub stars"></a>
  <a href="https://docs.tollbit.com"><img src="https://img.shields.io/badge/Documentation-📗-green" alt="Documentation"></a>
  <a href="https://twitter.com/tollbitofficial"><img src="https://img.shields.io/twitter/follow/TollbitOffical?style=social" alt="Twitter Follow"></a>
</p>

# Tollbit

A managed entry point to any web app, specifically meant for AI agents. Direct, authorized, and reliable agent <-> service interactions for any web service on the internet. Built for web automation, API access, and content access.

## Why Tollbit Exists

It's no secret that AI agents are going to run the web in the near future. However, for that to become a reality, the way agents interact with the internet needs to change. Currently, agent builders' options are limited to typical developer APIs and/or web automation. While great for demos, these patterns seem like the initial "hack" waiting for a more long term solution.

Developer APIs work well, but there is a very short list beyond the overused Google Drive, Slack, etc. Web automation is extremely slow, unreliable and insecure. Not only that, but most websites don't want bots on them, leading to doing all the grunt work of solving captchas and avoiding getting blocked.

The main reason for all this trouble? The web was not built for agents to be first class citzens.

Tollbit aims to build critical infrastructure that opens up new pathways for agents to act on the web, at native speed, and to actually bring real value to their users.

We are building on one ethical principle: **agents shouldn't (need to) pretend to be humans on the internet**.

This approach solves problems for both sides: website owners gain a reliable way to identify legitimate AI agents, manage their access privileges, and monetize their usage, while AI developers get stable, authorized access to first-party APIs, content, or web UI.

## How Tollbit Works

Tollbit creates a gateway for AI agents through a simple convention:

**Any service with a `tollbit` subdomain (`tollbit.example.com`) explicitly welcomes agent access with standardized authorization, permissions, and monetization.**

We call this subdomain the "front door" - a dedicated entry point built specifically for AI agents, separate from human traffic.

```mermaid
flowchart LR
    %% Define the AI agent client
    A[AI Agent with<br>Tollbit Client]

    %% Define the Tollbit front doors
    B1[tollbit.service-a.com]
    B2[tollbit.service-b.com]
    B3[tollbit.service-c.com]

    %% Define the actual services
    C1[service-a.com]
    C2[service-b.com]
    C3[service-c.com]

    %% Define the human user (simple)
    H[Human User]

    %% Connect AI agent to Tollbit front doors
    A -->|"HTTP"| B1
    A -->|"HTTP"| B2
    A -->|"HTTP"| B3

    %% Connect human to just service-a
    H -->|"Browser"| C1

    %% Connect Tollbit front doors to actual services - no labels
    B1 --- C1
    B2 --- C2
    B3 --- C3
```

## For Service Providers

Tollbit lets you monetize AI agent access to your service without building custom infrastructure:

- Implement once, work with any agent
- Set different pricing tiers and usage limits
- Separate human and bot traffic transparently
- Prevent abuse through standardized authentication

## For AI Developers

Tollbit gives your agents reliable access to services:

- One consistent pattern for authentication and access
- No more brittle web automation that breaks with UI changes
- Clear permissions model designed for non-human users
- Focus on building intelligence, not maintaining integration code

# tollbit-python-sdk

Tollbit's python SDK for interacting with Tollbit's services. Pull this directly into your code to make requests; no need to write your own clients. The SDK supports both synchronous and asynchronous calls.

The SDK currently supports the following operations:

- [Indexing content to assist with knowledge graphs](#indexing-content)
- [Checking rates for paid content](#checking-rates)
- [Access paid content using your organization's API key](#accessing-paid-content)

## Installing

```shell
pip install tollbit-python-sdk
```

## Indexing Content

### Synchronous

```python
from tollbit import crawl_content
from tollbit import content_formats

client = crawl_content.create_client(
    secret_key="YOUR API KEY",
    user_agent="YOUR USER AGENT"
)

pages = client.list_content_catalog(
    url="https://pioneervalleygazette.com",
    page_size=5,
)

for page in page:
    print(f"URL: {page.page_url} Last Modified: {page.last_mod}")
    data = client.crawl_content(url=page.page_url)
    print(data.content.main)
```

For more examples please see [examples/crawl_content.py](examples/crawl_content.py)

### Asynchronous

```python
from tollbit import crawl_content
from tollbit import content_formats

client = crawl_content.create_async_client(
    secret_key="YOUR API KEY",
    user_agent="YOUR USER AGENT"
)

pages = await client.list_content_catalog(
    url="https://pioneervalleygazette.com",
    page_size=5,
)
```

For more examples please see [examples/get_rates_async.py](examples/get_content_async.py)


## Checking Rates

### Synchronous

```python
from tollbit import use_content

client = use_content.create_client(
    secret_key="YOUR API KEY", 
    user_agent="YOUR USER AGENT"
)
rate_info = client.get_rate(url="https://pioneervalleygazette.com/daydream")
```

For more examples please see [examples/get_rates.py](examples/get_rates.py).

### Asynchronous

```python
from tollbit import use_content

client = use_content.create_async_client(
    secret_key="YOUR API KEY", 
    user_agent="YOUR USER AGENT"
)
rate_info = await client.get_rate(url="https://pioneervalleygazette.com/daydream")
```

For more examples please see [examples/get_rates_async.py](examples/get_rates_async.py)

## Accessing sanctioned content

### Synchronous

```python
from tollbit import use_content
from tollbit import licenses
from tollbit import currencies

client = use_content.create_client(
    secret_key="YOUR API KEY", 
    user_agent="YOUR USER AGENT"
)

data = client.get_sanctioned_content(
    url="https://pioneervalleygazette.com/daydream",
    max_price_micros=11000000,
    currency=currencies.USD,
    license_type=licenses.types.ON_DEMAND_LICENSE
)

print(data.content.main)
```

For more examples please see [examples/get_content.py](examples/get_content.py).

### Asynchronous

```python
from tollbit import use_content
from tollbit import licenses
from tollbit import currencies

client = use_content.create_async_client(
    secret_key="YOUR API KEY", 
    user_agent="YOUR USER AGENT"
)

data = await client.get_sanctioned_content(
    url="https://pioneervalleygazette.com/daydream",
    max_price_micros=11000000,
    currency=currencies.USD,
    license_type=licenses.types.ON_DEMAND_LICENSE
)

print(data.content.main)
```

For more examples please see [examples/get_content_async.py](examples/get_content_async.py).

## Self reporting usage

### Synchronous

```python
from tollbit import self_reporting
from tollbit import licenses
from tollbit import use_content

reporting_client = self_reporting.create_client(
    secret_key="YOUR API KEY", 
    user_agent="YOUR USER AGENT"
)


# Create an array of your usages
usages = [self_reporting.usage(
        url="https://pioneervalleygazette.com/daydream",
        times_used=1,
        license_permissions=[licenses.permissions.LICENSE_PERMISSION_PARTIAL_USE],
        license_id="licenses-id-123",
        license_type=licenses.types.ON_DEMAND_LICENSE,
    )]

# Create an idempotent transaction block
transaction_block = reporting_client.create_transaction_block(usages)

# Report usages
result = reporting_client.report(transaction_block)
```

For more examples please see [examples/self_reporting.py](examples/self_reporting.py)

### Asynchronous

```python
from tollbit import self_reporting
from tollbit import licenses
from tollbit import use_content

reporting_client = self_reporting.create_async_client(
    secret_key="YOUR API KEY", 
    user_agent="YOUR USER AGENT"
)


# Create an array of your usages
usages = [self_reporting.usage(
        url="https://pioneervalleygazette.com/daydream",
        times_used=1,
        license_permissions=[licenses.permissions.LICENSE_PERMISSION_PARTIAL_USE],
        license_id="licenses-id-123",
        license_type=licenses.types.ON_DEMAND_LICENSE,
    )]

# Create an idempotent transaction block
transaction_block = reporting_client.create_transaction_block(usages)

# Report usages
result = await reporting_client.report(transaction_block)
```

For more examples please see [examples/self_reporting_async.py](examples/self_reporting_async.py)

## Search

### Synchronous

```python
from tollbit import search

search_client = search.create_client(
    secret_key="YOUR API KEY", 
    user_agent="YOUR USER AGENT"
)

results = client.search(q="DIY home projects for millenials")
```

For more examples please see [examples/search.py](examples/search.py)

### Asynchronous

```python
from tollbit import search

search_client = search.create_async_client(
    secret_key="YOUR API KEY", 
    user_agent="YOUR USER AGENT"
)

results = await client.search(q="DIY home projects for millenials")
```

For more examples please see [examples/search_async.py](examples/search_async.py)


## Issues
We have disabled issues for the time being. Please reach out directly to tollbit

## Contributions
We are not currently accepting contributions at this time. Thank you for your interest.

## Local setup
_For internal development teams only_

### Requirements

- [pyenv](https://formulae.brew.sh/formula/pyenv)
- poetry
    
    ```shell
    pipx install poetry
    ```

### Setup

```shell
make install
```

### Tests

Run standard tests
```shell
make tests
```

Run on all pythons
```shell
make matrix-tests
```

## Examples

Example code is available in [examples](./examples/)
