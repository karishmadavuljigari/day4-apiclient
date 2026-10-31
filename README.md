\# Day 4 - Resilient HTTP API Client



\## Project Overview



This project demonstrates how to build a resilient API client using Python, HTTPX, and Pydantic.



The client communicates with the Training Mock API and retrieves ticket records using HTTP requests.



\## Features



\- HTTP requests using HTTPX.

\- Request timeouts.

\- Automatic retries for 5xx errors and 429 rate limits.

\- Exponential backoff with jitter.

\- Support for the Retry-After header.

\- Pagination using a generator.

\- Response validation using Pydantic.

\- Unit tests using HTTPX MockTransport without real network requests.



\## Technologies Used



\- Python

\- HTTPX

\- Pydantic

\- Pytest



\## Run the Project



Install dependencies:



```bash

uv sync

```



Start the Mock API server separately, then run:



```bash

uv run python client.py

```



\## Run Tests



```bash

uv run pytest -v

```



\## Test Coverage



The tests cover server-error retries, rate-limit retries, timeout retries, Pydantic validation, optional and required fields, and pagination.



\## SDK vs REST API



Refer to \[sdk\_vs\_rest.md](sdk\_vs\_rest.md) for the explanation.

