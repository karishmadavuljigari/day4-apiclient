
import httpx
import pytest
from pydantic import ValidationError
from client import Ticket, get_with_retries, get_all_tickets

def test_retry_after_server_error(monkeypatch):

    attempts = {"count": 0}

    # Simulate server responses
    def fake_server(request):

        attempts["count"] += 1

        if attempts["count"] == 1:
            return httpx.Response(
                500,
                json={"error": "Server error"},
                request=request
            )

        return httpx.Response(
            200,
            json={"status": "ok"},
            request=request
        )

    # Prevent actual waiting during the test
    monkeypatch.setattr("client.time.sleep", lambda delay: None)

    # Create a fake HTTP transport
    transport = httpx.MockTransport(fake_server)

    with httpx.Client(transport=transport) as client:

        response = get_with_retries(
            client,
            "https://fake-api.example.com",
            max_attempts=3
        )

    assert response.status_code == 200
    assert attempts["count"] == 2



def test_retry_after_429(monkeypatch):

    attempts = {"count": 0}
    wait_times = []

    # Simulate server responses
    def fake_server(request):

        attempts["count"] += 1

        if attempts["count"] == 1:
            return httpx.Response(
                429,
                headers={"Retry-After": "3"},
                json={"error": "Too many requests"},
                request=request
            )

        return httpx.Response(
            200,
            json={"status": "ok"},
            request=request
        )

    # Record waiting time without actually sleeping
    monkeypatch.setattr(
        "client.time.sleep",
        lambda delay: wait_times.append(delay)
    )

    transport = httpx.MockTransport(fake_server)

    with httpx.Client(transport=transport) as client:

        response = get_with_retries(
            client,
            "https://fake-api.example.com",
            max_attempts=3
        )

    assert response.status_code == 200
    assert attempts["count"] == 2
    assert wait_times == [3.0]


def test_retry_after_timeout(monkeypatch):

    attempts = {"count": 0}
    wait_times = []

    def fake_server(request):

        attempts["count"] += 1

        if attempts["count"] == 1:
            raise httpx.ReadTimeout(
                "Request timed out",
                request=request
            )

        return httpx.Response(
            200,
            json={"status": "ok"},
            request=request
        )

    monkeypatch.setattr(
        "client.time.sleep",
        lambda delay: wait_times.append(delay)
    )

    transport = httpx.MockTransport(fake_server)

    with httpx.Client(transport=transport) as client:

        response = get_with_retries(
            client,
            "https://fake-api.example.com",
            max_attempts=3
        )

    assert response.status_code == 200
    assert attempts["count"] == 2
    assert len(wait_times) == 1


def test_ticket_validation():

    ticket = Ticket(
        id=1,
        name="Test Ticket",
        status="active",
        category="alpha",
        created="2026-01-24"
    )

    assert ticket.id == 1
    assert ticket.name == "Test Ticket"
    assert ticket.status == "active"

def test_ticket_with_missing_optional_fields():

    ticket = Ticket(
        id=21,
        name="Dune 0021",
        created="2026-01-24"
    )

    assert ticket.id == 21
    assert ticket.status is None
    assert ticket.category is None


def test_ticket_missing_required_field():

    with pytest.raises(ValidationError):

        Ticket(
            name="Test Ticket",
            status="active",
            category="alpha",
            created="2026-01-24"
        )

def test_get_all_tickets():

    def fake_server(request):

        page = int(request.url.params["page"])

        if page == 1:
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "id": 1,
                            "name": "Ticket 1",
                            "created": "2026-01-24"
                        }
                    ],
                    "has_more": True
                },
                request=request
            )

        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "id": 2,
                        "name": "Ticket 2",
                        "created": "2026-01-25"
                    }
                ],
                "has_more": False
            },
            request=request
        )

    transport = httpx.MockTransport(fake_server)

    with httpx.Client(transport=transport) as client:

        tickets = list(get_all_tickets(client))

    assert len(tickets) == 2
    assert tickets[0].id == 1
    assert tickets[1].id == 2