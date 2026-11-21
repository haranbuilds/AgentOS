import pytest
import pytest_asyncio

from agentos.storage.db import pool
from agentos.tools.raw_lookup import (
    get_customer_details,
    get_invoice_details,
    get_payment_history,
    get_ticket_details,
)


@pytest_asyncio.fixture(scope="module", loop_scope="module", autouse=True)
async def database_pool() -> None:
    await pool.open(wait=True)

    yield

    await pool.close()


@pytest.mark.asyncio(loop_scope="module")
async def test_get_invoice_details_found() -> None:
    result = await get_invoice_details("INV-101")

    assert result["invoice_number"] == "INV-101"
    assert result["status"] == "pending"
    assert result["total_amount"] == 4500


@pytest.mark.asyncio(loop_scope="module")
async def test_get_invoice_details_not_found() -> None:
    result = await get_invoice_details("INV-999")

    assert result == {"error": "Invoice not found"}


@pytest.mark.asyncio(loop_scope="module")
async def test_get_customer_details_found() -> None:
    result = await get_customer_details("CUST-101")

    assert result["customer_code"] == "CUST-101"
    assert "name" in result
    assert "tenant_id" in result


@pytest.mark.asyncio(loop_scope="module")
async def test_get_customer_details_not_found() -> None:
    result = await get_customer_details("CUST-999")

    assert result == {"error": "Customer not found"}


@pytest.mark.asyncio(loop_scope="module")
async def test_get_payment_history_found() -> None:
    result = await get_payment_history("CUST-101")

    assert len(result) == 2
    assert all(payment["customer_id"] for payment in result)


@pytest.mark.asyncio(loop_scope="module")
async def test_get_payment_history_empty() -> None:
    result = await get_payment_history("CUST-999")

    assert result == []


@pytest.mark.asyncio(loop_scope="module")
async def test_get_ticket_details_found() -> None:
    result = await get_ticket_details("TKT-101")

    assert result["ticket_number"] == "TKT-101"
    assert result["priority"] == "high"


@pytest.mark.asyncio(loop_scope="module")
async def test_get_ticket_details_not_found() -> None:
    result = await get_ticket_details("TKT-999")

    assert result == {"error": "Ticket not found"}