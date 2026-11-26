"""Generate a deterministic synthetic loan portfolio.

All data is randomly generated with a fixed seed. It does not come from any
real lender, servicer, CLO or employer, and the numbers are not real-world
metrics.
"""
import random
import sqlite3
from pathlib import Path

SEED = 21
N_LOANS = 500
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "portfolio.db"

SECTORS = [
    ("Technology", 0.16), ("Healthcare", 0.14), ("Industrials", 0.14),
    ("Consumer", 0.12), ("Energy", 0.10), ("Financials", 0.10),
    ("Retail", 0.08), ("Telecom", 0.08), ("Utilities", 0.08),
]
DELINQ = [("current", 0.90), ("d30", 0.05), ("d60", 0.03), ("d90plus", 0.02)]


def pick(rng, table):
    r = rng.random()
    acc = 0.0
    for value, p in table:
        acc += p
        if r <= acc:
            return value
    return table[-1][0]


def main() -> None:
    rng = random.Random(SEED)
    con = sqlite3.connect(DB)
    con.executescript((ROOT / "sql" / "schema.sql").read_text())
    con.execute("DELETE FROM loans")
    con.execute("DELETE FROM tranches")

    for i in range(1, N_LOANS + 1):
        sector = pick(rng, SECTORS)
        delinq = pick(rng, DELINQ)
        # Riskier loans get higher PD, coupon and LGD.
        risk = rng.uniform(0.0, 1.0) + {"current": 0.0, "d30": 0.3, "d60": 0.6, "d90plus": 0.9}[delinq]
        pd_ = round(min(0.005 + 0.045 * risk, 0.25), 4)
        lgd = round(min(0.35 + 0.15 * risk, 0.7), 4)
        coupon = round(0.045 + 0.05 * risk, 4)
        balance = round(rng.uniform(0.5, 8.0), 2) * 1_000_000
        con.execute(
            "INSERT INTO loans VALUES (?, ?, ?, ?, ?, ?, ?)",
            (f"L{i:04d}", sector, balance, coupon, pd_, lgd, delinq),
        )

    # Classic simple CLO structure.
    con.executemany(
        "INSERT INTO tranches VALUES (?, ?, ?)",
        [("senior", 0.80, 0.05), ("mezzanine", 0.10, 0.09), ("equity", 0.10, None)],
    )
    con.commit()
    con.close()
    print(f"wrote {DB}: {N_LOANS} loans + 3 tranches")


if __name__ == "__main__":
    main()
