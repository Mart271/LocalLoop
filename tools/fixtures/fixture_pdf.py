"""Render synthetic invoices as text-layer PDFs with reportlab (LL-012).

`reportlab.rl_config.invariant` is set so that output is byte-identical for the same input
(fixed creation dates and document IDs). Only the standard Helvetica fonts are used, so no font
file is embedded and the text layer extracts cleanly.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reportlab import rl_config
from reportlab.lib import pdfencrypt
from reportlab.lib.colors import black, white
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from fixture_model import CUSTOMER, Invoice, fmt_amount

rl_config.invariant = 1
# Uncompressed content streams: zlib implementations (classic zlib vs zlib-ng, which Python 3.14
# on Windows uses) produce different bytes for the same input, which would break reproducibility.
rl_config.pageCompression = 0

PAGE_W, PAGE_H = letter


@dataclass(frozen=True)
class Labels:
    """Field labels printed on a document. F1 uses DEFAULT_LABELS; F3 varies them."""

    vendor: str = "Vendor:"
    number: str = "Invoice No.:"
    date: str = "Invoice Date:"
    currency: str = "Currency:"
    subtotal: str = "Subtotal"
    tax: str = "VAT"
    total: str = "Total Due"
    value_below: bool = False  # False: value to the right of the label; True: on the next line


DEFAULT_LABELS = Labels()


@dataclass(frozen=True)
class Extras:
    """Optional content for adversarial fixtures."""

    white_text: tuple[str, ...] = ()
    title: str | None = None
    subject: str | None = None
    keywords: str | None = None
    user_password: str | None = None
    extra_pages: int = 0
    date_format: str | None = None


def _fields(c: canvas.Canvas, x: float, y: float, pairs: list[tuple[str, str]], width: float, below: bool) -> float:
    step = 28 if below else 16
    for label, value in pairs:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, label)
        c.setFont("Helvetica", 10)
        if below:
            c.drawString(x, y - 12, value)
        else:
            c.drawString(x + width, y, value)
        y -= step
    return y


def _items(c: canvas.Canvas, invoice: Invoice, x: float, y: float) -> float:
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "Description")
    c.drawRightString(x + 320, y, "Qty")
    c.drawRightString(x + 410, y, "Unit Price")
    c.drawRightString(x + 500, y, "Amount")
    c.line(x, y - 4, x + 500, y - 4)
    c.setFont("Helvetica", 10)
    for item in invoice.items:
        y -= 18
        c.drawString(x, y, item.description)
        c.drawRightString(x + 320, y, str(item.quantity))
        c.drawRightString(x + 410, y, fmt_amount(item.unit_price))
        c.drawRightString(x + 500, y, fmt_amount(item.amount))
    c.line(x, y - 8, x + 500, y - 8)
    return y - 30


def _header_pairs(invoice: Invoice, labels: Labels, date_format: str | None) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if "invoice_number" not in invoice.omit:
        pairs.append((labels.number, invoice.number))
    if "invoice_date" not in invoice.omit:
        pairs.append((labels.date, invoice.date_text(date_format)))
    if "currency" not in invoice.omit:
        pairs.append((labels.currency, invoice.vendor.currency))
    return pairs


def _total_pairs(invoice: Invoice, labels: Labels) -> list[tuple[str, str]]:
    pairs = [(labels.subtotal, fmt_amount(invoice.subtotal)), (labels.tax, fmt_amount(invoice.tax))]
    if "total" not in invoice.omit:
        pairs.append((labels.total, fmt_amount(invoice.total)))
    return pairs


def _totals(c: canvas.Canvas, x: float, y: float, pairs: list[tuple[str, str]], right: float, below: bool) -> None:
    for label, value in pairs:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, label)
        c.setFont("Helvetica", 10)
        if below:
            c.drawString(x, y - 12, value)
            y -= 28
        else:
            c.drawRightString(right, y, value)
            y -= 16


def _vendor_block(c: canvas.Canvas, invoice: Invoice, x: float, y: float, align: str) -> None:
    draw = {"left": c.drawString, "center": c.drawCentredString, "right": c.drawRightString}[align]
    c.setFont("Helvetica-Bold", 16)
    draw(x, y, invoice.display_vendor)
    c.setFont("Helvetica", 9)
    for offset, line in enumerate(invoice.vendor.address, start=1):
        draw(x, y - 13 * offset, line)


def _customer(c: canvas.Canvas, x: float, y: float) -> None:
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "Bill to:")
    c.setFont("Helvetica", 10)
    for offset, line in enumerate(CUSTOMER, start=1):
        c.drawString(x, y - 13 * offset, line)


def _page(c: canvas.Canvas, invoice: Invoice, layout: str, labels: Labels, extras: Extras) -> None:
    below = labels.value_below
    header = _header_pairs(invoice, labels, extras.date_format)
    vendor_pair = (labels.vendor, invoice.display_vendor)
    totals = _total_pairs(invoice, labels)
    if layout == "A":
        _vendor_block(c, invoice, 50, 740, "left")
        c.setFont("Helvetica-Bold", 20)
        c.drawString(440, 740, "INVOICE")
        _fields(c, 330, 700, header, 90, below)
        _fields(c, 50, 650, [vendor_pair], 60, below)
        _customer(c, 50, 615)
        y = _items(c, invoice, 50, 540)
        _totals(c, 380, y, totals, 550, below)
    elif layout == "B":
        _vendor_block(c, invoice, PAGE_W / 2, 750, "center")
        _fields(c, 50, 690, [*header, vendor_pair], 85, below)
        _customer(c, 340, 690)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 590, "Tax Invoice")
        y = _items(c, invoice, 50, 565)
        _totals(c, 50, y, totals, 250, below)
    else:  # "C"
        _vendor_block(c, invoice, 562, 745, "right")
        c.rect(50, 615, 512, 85)
        left, right = header[:2], [vendor_pair, *header[2:]]
        _fields(c, 60, 680, left, 85, below)
        _fields(c, 320, 680, right, 65, below)
        _customer(c, 50, 590)
        y = _items(c, invoice, 50, 520)
        _totals(c, 50, y, totals, 220, below)
    c.setFont("Helvetica", 9)
    note_y = 110
    for note in invoice.notes:
        c.drawString(50, note_y, note)
        note_y -= 12
    if extras.white_text:
        c.setFillColor(white)
        for offset, line in enumerate(extras.white_text):
            c.drawString(50, 70 - 10 * offset, line)
        c.setFillColor(black)
    c.setFont("Helvetica-Oblique", 7)
    c.drawString(50, 40, "Synthetic test document generated for LocalLoop. All names and amounts are fictitious.")


def render_invoice(
    path: Path, invoice: Invoice, layout: str, labels: Labels = DEFAULT_LABELS, extras: Extras = Extras()
) -> None:
    encrypt = None
    if extras.user_password is not None:
        encrypt = pdfencrypt.StandardEncryption(extras.user_password, ownerPassword=extras.user_password + "-owner")
    c = canvas.Canvas(str(path), pagesize=letter, invariant=1, pageCompression=0, encrypt=encrypt)
    c.setAuthor("LocalLoop fixture generator")
    c.setCreator("LocalLoop fixture generator")
    c.setTitle(extras.title if extras.title is not None else f"Invoice {invoice.number}")
    if extras.subject is not None:
        c.setSubject(extras.subject)
    if extras.keywords is not None:
        c.setKeywords(extras.keywords)
    _page(c, invoice, layout, labels, extras)
    c.showPage()
    for number in range(2, extras.extra_pages + 2):
        c.setFont("Helvetica", 10)
        c.drawString(50, 740, f"Continuation page {number} of {extras.extra_pages + 1} (synthetic)")
        c.showPage()
    c.save()
