from __future__ import annotations

import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from ..models import Payment, User


DEFAULT_OUTPUT_DIR = "invoices"


def _seller_details() -> Dict[str, str]:
    return {
        "name": os.getenv("INVOICE_SELLER_NAME", "Lucy World Search"),
        "company": os.getenv("INVOICE_SELLER_COMPANY", "Lucy World Search BV"),
        "address": os.getenv("INVOICE_SELLER_ADDRESS", "Keizersgracht 123\n1015 CJ Amsterdam\nThe Netherlands"),
        "tax_id": os.getenv("INVOICE_SELLER_TAX_ID", "NL000000000B01"),
        "email": os.getenv("INVOICE_SELLER_EMAIL", "finance@lucy.world"),
    }


def _format_decimal(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.01')):,.2f}"


def generate_invoice_pdf(payment: Payment, user: User, *, output_dir: str | None = None) -> str:
    """Generate a PDF invoice for a captured payment. Returns the relative file path."""

    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    base_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    target_dir = base_path / output_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    invoice_number = payment.invoice_number or f"INV-{payment.created_at.strftime('%Y%m%d')}-{payment.id:05d}"
    filename = target_dir / f"{invoice_number}.pdf"

    seller = _seller_details()
    billing_lines = [
        x for x in [
            user.billing_name or user.name or user.email,
            user.billing_company,
            user.billing_address_line1,
            user.billing_address_line2,
            (user.billing_postal_code or "", user.billing_city or ""),
            user.billing_region,
            user.billing_country,
            f"VAT ID: {user.billing_tax_id}" if user.billing_tax_id else None,
        ]
    ]

    billing_text_lines: list[str] = []
    for line in billing_lines:
        if isinstance(line, tuple):
            joined = " ".join(part for part in line if part)
            if joined:
                billing_text_lines.append(joined)
        elif line:
            billing_text_lines.append(str(line))
    if not billing_text_lines:
        billing_text_lines = [user.email]

    c = canvas.Canvas(str(filename), pagesize=A4)
    width, height = A4
    margin = 20 * mm

    text = c.beginText(margin, height - margin)
    text.setFont("Helvetica-Bold", 16)
    text.textLine(seller["company"])
    text.setFont("Helvetica", 10)
    text.textLine(seller["address"])
    text.textLine(f"VAT ID: {seller['tax_id']}")
    text.textLine(seller["email"])
    text.moveCursor(0, 20)
    text.setFont("Helvetica-Bold", 14)
    text.textLine("Invoice")
    text.setFont("Helvetica", 10)
    text.textLine(f"Invoice number: {invoice_number}")
    text.textLine(f"Invoice date: {datetime.utcnow().strftime('%Y-%m-%d')}")
    text.textLine(f"Payment reference: {payment.order_id}")
    text.moveCursor(0, 20)

    text.setFont("Helvetica-Bold", 12)
    text.textLine("Bill to")
    text.setFont("Helvetica", 10)
    for line in billing_text_lines:
        text.textLine(line)
    text.moveCursor(0, 20)

    amount = payment.amount_decimal
    tax_amount = payment.tax_amount_decimal
    net_amount = payment.net_amount_decimal
    currency = payment.currency

    text.setFont("Helvetica-Bold", 12)
    text.textLine("Summary")
    text.setFont("Helvetica", 10)
    text.textLine(f"Description: Lucy World Search Pro subscription (monthly)")
    text.textLine(f"Subtotal: {_format_decimal(net_amount)} {currency}")
    text.textLine(f"Tax: {_format_decimal(tax_amount)} {currency}")
    text.textLine(f"Total: {_format_decimal(amount)} {currency}")
    if metadata := payment.metadata or {}:
        invoice_note = metadata.get("note")
        if invoice_note:
            text.moveCursor(0, 10)
            text.textLine(f"Note: {invoice_note}")

    text.moveCursor(0, 30)
    text.setFont("Helvetica", 8)
    text.textLine("Please retain this invoice for your records.")

    c.drawText(text)
    c.showPage()
    c.save()

    relative_path = os.path.relpath(filename, base_path)
    payment.invoice_number = invoice_number
    payment.invoice_path = relative_path
    return relative_path
