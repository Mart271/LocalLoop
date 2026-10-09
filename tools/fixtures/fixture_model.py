"""Synthetic invoice data for LocalLoop fixtures (LL-012, A-19).

Every vendor, customer, product, and amount here is invented. Nothing is copied from a real
company's documents or branding.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def fmt_amount(value: Decimal) -> str:
    """1234.5 -> '1,234.50' (how amounts are printed on the documents)."""
    return f"{money(value):,.2f}"


def derived_rng(seed: int, name: str) -> random.Random:
    """Independent, reproducible random stream per fixture set, so sets don't affect each other."""
    digest = hashlib.sha256(f"{seed}:{name}".encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


@dataclass(frozen=True)
class Vendor:
    key: str
    name: str
    prefix: str
    currency: str
    tax_rate: Decimal
    date_format: str
    layout: str
    address: tuple[str, ...]
    products: tuple[str, ...]


VENDORS: tuple[Vendor, ...] = (
    Vendor(
        "bluefin",
        "Bluefin Office Supplies Co.",
        "BOS",
        "PHP",
        Decimal("0.12"),
        "%Y-%m-%d",
        "A",
        ("Unit 4B, 18 Sampaguita Lane", "Barangay Halimaw, Fictiva City 1099"),
        ("A4 copy paper (ream)", "Ballpoint pens (box of 50)", "Stapler, heavy duty", "Toner cartridge K-200",
         "Archive box, large", "Sticky notes (pack of 12)", "Whiteboard markers (set)", "Desk organizer"),
    ),
    Vendor(
        "maraval",
        "Maraval Printing Services",
        "MPS",
        "USD",
        Decimal("0.08"),
        "%d/%m/%Y",
        "B",
        ("2700 Quillfeather Avenue, Suite 12", "Lantern Bay, ZZ 00042"),
        ("Business cards (500)", "Tri-fold brochure (1000)", "Poster, A2 gloss", "Letterhead (ream)",
         "Envelope printing (500)", "Banner, 2 m vinyl", "Booklet binding", "Design proof revision"),
    ),
    Vendor(
        "tanglewood",
        "Tanglewood Logistics Ltd.",
        "TGL",
        "EUR",
        Decimal("0.20"),
        "%B %d, %Y",
        "C",
        ("Unit 9, Hollowmere Trading Estate", "Brackenford, Imaginaria 4410"),
        ("Pallet delivery, zone 2", "Same-day courier", "Warehouse storage (week)", "Customs paperwork fee",
         "Fuel surcharge", "Container handling", "Express parcel (10 kg)", "Insurance cover"),
    ),
)

CUSTOMER = ("Calderon Trading Co. (fictitious)", "45 Larkspur Road", "Fictiva City 1100")


@dataclass(frozen=True)
class LineItem:
    description: str
    quantity: int
    unit_price: Decimal

    @property
    def amount(self) -> Decimal:
        return money(self.unit_price * self.quantity)


@dataclass(frozen=True)
class Invoice:
    vendor: Vendor
    number: str
    issued: date
    items: tuple[LineItem, ...]
    # Overrides used by invalid and adversarial sets. None means "computed normally".
    vendor_name: str | None = None
    printed_total: Decimal | None = None
    omit: frozenset[str] = field(default_factory=frozenset)
    notes: tuple[str, ...] = ()

    @property
    def display_vendor(self) -> str:
        return self.vendor_name if self.vendor_name is not None else self.vendor.name

    @property
    def subtotal(self) -> Decimal:
        return money(sum((item.amount for item in self.items), Decimal(0)))

    @property
    def tax(self) -> Decimal:
        return money(self.subtotal * self.vendor.tax_rate)

    @property
    def total(self) -> Decimal:
        return self.printed_total if self.printed_total is not None else money(self.subtotal + self.tax)

    def date_text(self, fmt: str | None = None) -> str:
        return self.issued.strftime(fmt or self.vendor.date_format)

    def truth(self) -> dict[str, object]:
        """Ground-truth record matching the example workflow's recordSchema (fields left out are None)."""
        record: dict[str, object] = {
            "vendor_name": self.display_vendor,
            "invoice_number": self.number,
            "invoice_date": self.issued.isoformat(),
            "currency": self.vendor.currency,
            "subtotal": str(self.subtotal),
            "tax": str(self.tax),
            "total": str(self.total),
        }
        for name in self.omit:
            record[name] = None
        return record

    def with_changes(self, **changes: object) -> Invoice:
        return replace(self, **changes)  # type: ignore[arg-type]


def make_invoice(rng: random.Random, vendor: Vendor, sequence: int, year: int = 2026) -> Invoice:
    start = date(year, 1, 5)
    issued = start + timedelta(days=rng.randrange(0, 235))  # 2026-01-05 .. 2026-08-27, never in the future
    count = rng.randint(2, 5)
    items = tuple(
        LineItem(
            description=rng.choice(vendor.products),
            quantity=rng.randint(1, 20),
            unit_price=money(Decimal(rng.randint(500, 50_000)) / 100),
        )
        for _ in range(count)
    )
    return Invoice(vendor=vendor, number=f"{vendor.prefix}-{year}-{sequence:04d}", issued=issued, items=items)
