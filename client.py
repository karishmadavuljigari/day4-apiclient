
import httpx
import time
import random

from datetime import date
from pydantic import BaseModel


# Pydantic model for validating ticket records
class Ticket(BaseModel):
    id: int
    name: str
    status: str | None = None
    category: str | None = None
    created: date


# Function to make API requests with retries
def get_with_retries(client, url, max_attempts=3):

    for attempt in range(1, max_attempts + 1):

        try:
            response = client.get(url, timeout=5)

            if response.status_code == 429 or response.status_code >= 500:

                if attempt == max_attempts:
                    return response

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")

                    if retry_after is not None:
                        delay = float(retry_after)
                    else:
                        delay = (2 ** (attempt - 1)) + random.uniform(0, 1)

                else:
                    delay = (2 ** (attempt - 1)) + random.uniform(0, 1)

                print(f"Request failed. Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
                continue

            return response

        except httpx.TimeoutException:

            if attempt == max_attempts:
                print("Request timed out after all attempts.")
                raise

            delay = (2 ** (attempt - 1)) + random.uniform(0, 1)

            print(f"Request timed out. Retrying in {delay:.2f} seconds...")
            time.sleep(delay)


# Pagination iterator to fetch tickets one at a time
def get_all_tickets(client):

    page = 1

    while True:

        url = f"http://127.0.0.1:9000/v1/tickets?page={page}"

        response = get_with_retries(client, url)
        response.raise_for_status()

        data = response.json()

        tickets = data["items"]

        for ticket in tickets:
            yield Ticket.model_validate(ticket)

        if not data["has_more"]:
            break

        page += 1


# Main program
if __name__ == "__main__":

    with httpx.Client() as client:

        for ticket in get_all_tickets(client):
            print(ticket)
