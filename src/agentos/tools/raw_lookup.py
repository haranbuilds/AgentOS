
from typing import Any

from agentos.storage.db import pool


async def get_invoice_details(invoice_id: str) -> dict[str, Any]:
    async with pool.connection() as conn, conn.cursor() as cur:
        await cur.execute(
            """
            SELECT
                id,
                tenant_id,
                vendor_id,
                purchase_order_id,
                invoice_number,
                total_amount,
                currency,
                status,
                invoice_date,
                due_date
            FROM invoices
            WHERE invoice_number = %s
            """,
            (invoice_id,),
        )

        row = await cur.fetchone()

        if row is None:
            return {"error": "Invoice not found"}

        if cur.description is None:
            return {"error": "Query returned no column metadata"}

        columns = [column.name for column in cur.description]

        return dict(zip(columns, row, strict=True))


async def get_customer_details(customer_id: str) -> dict[str, Any]:
    async with pool.connection() as conn, conn.cursor() as cur:
        await cur.execute(
            """
            SELECT
                id,
                tenant_id,
                customer_code,
                name,
                email,
                status
            FROM customers
            WHERE customer_code = %s
            """,
            (customer_id,),
        )

        row = await cur.fetchone()

        if row is None:
            return {"error": "Customer not found"}

        if cur.description is None:
            return {"error": "Query returned no column metadata"}

        columns = [column.name for column in cur.description]

        return dict(zip(columns, row, strict=True))


async def get_payment_history(
    customer_id: str,
) -> list[dict[str, Any]]:
    async with pool.connection() as conn, conn.cursor() as cur:
        await cur.execute(
            """
            SELECT
                p.id,
                p.tenant_id,
                p.customer_id,
                p.order_id,
                p.transaction_reference,
                p.amount,
                p.currency,
                p.status,
                p.payment_method,
                p.paid_at
            FROM customer_payments AS p
            JOIN customers AS c
                ON c.id = p.customer_id
                AND c.tenant_id = p.tenant_id
            WHERE c.customer_code = %s
            ORDER BY p.paid_at DESC NULLS LAST
            """,
            (customer_id,),
        )

        rows = await cur.fetchall()

        if cur.description is None:
            return []

        columns = [column.name for column in cur.description]

        return [
            dict(zip(columns, row, strict=True))
            for row in rows
        ]


async def get_ticket_details(ticket_id: str) -> dict[str, Any]:
    async with pool.connection() as conn, conn.cursor() as cur:
        await cur.execute(
            """
            SELECT
                t.id,
                t.tenant_id,
                t.customer_id,
                t.ticket_number,
                t.subject,
                t.description,
                t.category,
                t.priority,
                t.status
            FROM support_tickets AS t
            WHERE t.ticket_number = %s
            """,
            (ticket_id,),
        )

        row = await cur.fetchone()

        if row is None:
            return {"error": "Ticket not found"}

        if cur.description is None:
            return {"error": "Query returned no column metadata"}

        columns = [column.name for column in cur.description]

        return dict(zip(columns, row, strict=True))
