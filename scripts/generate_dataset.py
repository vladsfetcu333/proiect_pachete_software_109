"""Generate the retail dataset used by the Python and SAS project."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT = DATA_DIR / "online_retail_project.csv"


def main() -> None:
    rng = np.random.default_rng(26)
    DATA_DIR.mkdir(exist_ok=True)

    countries = [
        "United Kingdom", "Germany", "France", "EIRE", "Spain", "Netherlands",
        "Belgium", "Switzerland", "Portugal", "Australia", "Norway", "Italy",
        "Finland", "Sweden", "Austria", "Denmark", "Poland", "USA",
        "Canada", "Greece", "Czech Republic", "Japan",
    ]
    country_weights = np.array([
        0.48, 0.10, 0.09, 0.07, 0.045, 0.04, 0.03, 0.025, 0.023, 0.02, 0.018,
        0.017, 0.014, 0.013, 0.012, 0.011, 0.010, 0.009, 0.008, 0.006, 0.005, 0.005,
    ])
    country_weights = country_weights / country_weights.sum()

    product_catalog = [
        ("GFT001", "Decorative candle set", "Home decor", 7.90),
        ("GFT002", "Ceramic mug floral", "Kitchen", 5.50),
        ("GFT003", "Handmade greeting card", "Stationery", 2.40),
        ("GFT004", "Vintage photo frame", "Home decor", 12.80),
        ("GFT005", "Tea towel cotton", "Kitchen", 4.20),
        ("GFT006", "Gift bag medium", "Packaging", 1.20),
        ("GFT007", "Aroma diffuser", "Home fragrance", 16.90),
        ("GFT008", "Notebook botanical", "Stationery", 6.30),
        ("GFT009", "Decorative pillow cover", "Home decor", 10.40),
        ("GFT010", "Glass storage jar", "Kitchen", 8.70),
        ("GFT011", "Wooden ornament", "Seasonal", 3.60),
        ("GFT012", "Premium hamper box", "Packaging", 18.50),
        ("GFT013", "Scented wax melts", "Home fragrance", 4.80),
        ("GFT014", "Desk calendar", "Stationery", 9.90),
        ("GFT015", "Mini plant pot", "Home decor", 6.80),
        ("GFT016", "Kitchen apron", "Kitchen", 13.20),
        ("GFT017", "Ribbon roll", "Packaging", 2.10),
        ("GFT018", "Holiday light string", "Seasonal", 14.70),
        ("GFT019", "Porcelain plate", "Kitchen", 11.30),
        ("GFT020", "Room spray lavender", "Home fragrance", 7.40),
    ]

    n_customers = 780
    customers = np.arange(10001, 10001 + n_customers)
    customer_country = dict(zip(customers, rng.choice(countries, size=n_customers, p=country_weights)))

    rows = []
    invoice_no = 530000
    start = pd.Timestamp("2024-01-02 08:00:00")
    end = pd.Timestamp("2025-12-20 19:00:00")
    total_seconds = int((end - start).total_seconds())

    for _ in range(1850):
        invoice_no += 1
        invoice = f"INV{invoice_no}"
        customer_id = int(rng.choice(customers))
        country = customer_country[customer_id]
        invoice_dt = start + pd.to_timedelta(int(rng.integers(0, total_seconds)), unit="s")
        line_count = int(rng.integers(1, 6))
        product_indexes = rng.choice(len(product_catalog), size=line_count, replace=False)

        for product_index in product_indexes:
            stock_code, description, category, base_price = product_catalog[product_index]
            quantity = int(max(1, rng.poisson(8)))
            if rng.random() < 0.035:
                quantity = -int(rng.integers(1, 8))
            if rng.random() < 0.012:
                quantity = int(rng.integers(80, 220))

            price = round(max(0.25, rng.normal(base_price, base_price * 0.12)), 2)
            if rng.random() < 0.01:
                price = round(price * rng.uniform(4.0, 7.0), 2)

            discount = round(float(rng.choice([0, 0.05, 0.10, 0.15, 0.20], p=[0.58, 0.18, 0.14, 0.07, 0.03])), 2)
            shipping = round(float(max(0, rng.normal(4.5, 1.4))), 2)
            acquisition_channel = rng.choice(["Organic", "Ads", "Email", "Marketplace", "Referral"],
                                             p=[0.34, 0.24, 0.20, 0.15, 0.07])

            rows.append({
                "Invoice": invoice,
                "StockCode": stock_code,
                "Description": description,
                "Category": category,
                "Quantity": quantity,
                "InvoiceDate": invoice_dt,
                "Price": price,
                "Discount": discount,
                "ShippingCost": shipping,
                "CustomerID": customer_id,
                "Country": country,
                "AcquisitionChannel": acquisition_channel,
                "RevenueNet": round(quantity * price * (1 - discount) + shipping, 2),
            })

    df = pd.DataFrame(rows).sort_values("InvoiceDate").reset_index(drop=True)

    missing_description = rng.choice(df.index, size=int(len(df) * 0.012), replace=False)
    df.loc[missing_description, "Description"] = np.nan

    missing_customers = rng.choice(df.index, size=int(len(df) * 0.045), replace=False)
    df.loc[missing_customers, "CustomerID"] = np.nan

    df.to_csv(OUTPUT, index=False)
    print(f"Generated {len(df)} rows at {OUTPUT}")


if __name__ == "__main__":
    main()
