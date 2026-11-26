"""Portfolio risk metrics + a simplified one-period CLO cash-flow waterfall.

Runs generate_portfolio.py first if the database is missing.
Writes sample_output.md.

Waterfall model (deliberately simple, documented in the README):
- One annual period, expected cash flows (deterministic, not Monte Carlo).
- Collections = interest on performing balance + scheduled principal
  (25% of performing balance) + recoveries from expected defaults.
- Expected defaults = balance * PD; recoveries = defaults * (1 - LGD);
  losses = defaults * LGD.
- Cash pays: senior interest -> mezzanine interest -> senior principal
  -> mezzanine principal -> residual to equity.
- Losses write tranches down in reverse: equity -> mezzanine -> senior.
"""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "portfolio.db"
AMORTIZATION = 0.25  # share of performing balance repaid in the period


def money(x: float) -> str:
    return f"${x:,.0f}"


def main() -> None:
    if not DB.exists():
        import generate_portfolio  # noqa: PLC0415 - sibling script

        generate_portfolio.main()
    con = sqlite3.connect(DB)

    # --- portfolio risk metrics -----------------------------------------
    (n, total) = con.execute("SELECT COUNT(*), SUM(balance) FROM loans").fetchone()
    (wa_coupon,) = con.execute(
        "SELECT SUM(balance * coupon) / SUM(balance) FROM loans").fetchone()
    (wa_pd,) = con.execute(
        "SELECT SUM(balance * pd) / SUM(balance) FROM loans").fetchone()
    (wa_lgd,) = con.execute(
        "SELECT SUM(balance * lgd) / SUM(balance) FROM loans").fetchone()
    (expected_loss,) = con.execute(
        "SELECT SUM(balance * pd * lgd) FROM loans").fetchone()

    delinq = con.execute(
        "SELECT delinquency, COUNT(*), SUM(balance) FROM loans "
        "GROUP BY delinquency ORDER BY SUM(balance) DESC").fetchall()
    sectors = con.execute(
        "SELECT sector, SUM(balance), SUM(balance * pd * lgd) FROM loans "
        "GROUP BY sector ORDER BY SUM(balance) DESC LIMIT 5").fetchall()

    # --- one-period expected cash flows ---------------------------------
    (interest,) = con.execute(
        "SELECT SUM(balance * (1 - pd) * coupon) FROM loans").fetchone()
    (sched_principal,) = con.execute(
        f"SELECT SUM(balance * (1 - pd)) * {AMORTIZATION} FROM loans").fetchone()
    (recoveries,) = con.execute(
        "SELECT SUM(balance * pd * (1 - lgd)) FROM loans").fetchone()
    collections = interest + sched_principal + recoveries

    tranches = [
        {"name": name, "pct": pct, "coupon": cpn,
         "balance": pct * total, "interest": 0.0, "principal": 0.0,
         "loss": 0.0, "end_balance": pct * total}
        for name, pct, cpn in con.execute(
            "SELECT tranche, pct, coupon FROM tranches").fetchall()
    ]
    by_name = {t["name"]: t for t in tranches}

    # Interest and principal down the waterfall.
    cash = collections
    for name in ("senior", "mezzanine"):
        t = by_name[name]
        due = t["balance"] * t["coupon"]
        t["interest"] = min(due, cash)
        cash -= t["interest"]
    for name in ("senior", "mezzanine"):
        t = by_name[name]
        pay = min(t["balance"], cash)
        t["principal"] = pay
        cash -= pay
    by_name["equity"]["residual"] = cash  # whatever is left

    # Losses write tranches down in reverse seniority.
    loss_left = expected_loss
    for name in ("equity", "mezzanine", "senior"):
        t = by_name[name]
        t["loss"] = min(t["balance"], loss_left)
        loss_left -= t["loss"]
        t["end_balance"] = t["balance"] - t["loss"]

    distributed = (sum(t["interest"] for t in tranches)
                   + sum(t["principal"] for t in tranches)
                   + by_name["equity"]["residual"])
    assert abs(distributed - collections) < 1.0, "waterfall does not conserve cash"

    eq = by_name["equity"]
    equity_return = ((eq["interest"] + eq["principal"] + eq["residual"] - eq["loss"])
                     / eq["balance"])

    # --- report -----------------------------------------------------------
    out = [
        "# Portfolio risk & CLO waterfall (synthetic data)",
        "",
        "Produced by `scripts/run_analysis.py`. All data is synthetic.",
        "",
        "## Portfolio summary",
        "",
        f"- Loans: **{n}**, total balance **{money(total)}**",
        f"- Balance-weighted coupon: **{wa_coupon:.2%}**",
        f"- Balance-weighted PD: **{wa_pd:.2%}**, LGD: **{wa_lgd:.2%}**",
        f"- 1-year expected loss (balance x PD x LGD): **{money(expected_loss)}**",
        "",
        "## Delinquency buckets",
        "",
        "| Status | Loans | Balance |",
        "|---|---|---|",
        *[f"| {d} | {c} | {money(b)} |" for d, c, b in delinq],
        "",
        "## Top sectors by balance",
        "",
        "| Sector | Balance | Expected loss |",
        "|---|---|---|",
        *[f"| {s} | {money(b)} | {money(el)} |" for s, b, el in sectors],
        "",
        "## One-period waterfall",
        "",
        f"- Interest collections: {money(interest)}",
        f"- Scheduled principal (25% of performing): {money(sched_principal)}",
        f"- Recoveries on expected defaults: {money(recoveries)}",
        f"- **Total collections: {money(collections)}**",
        "",
        "| Tranche | Start balance | Coupon | Interest paid | Principal paid | Residual | Loss absorbed | End balance |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for name in ("senior", "mezzanine", "equity"):
        t = by_name[name]
        cpn = f"{t['coupon']:.1%}" if t["coupon"] else "residual"
        res = money(t.get("residual", 0.0)) if name == "equity" else "-"
        out.append(
            f"| {name} | {money(t['balance'])} | {cpn} | {money(t['interest'])} "
            f"| {money(t['principal'])} | {res} | {money(t['loss'])} | {money(t['end_balance'])} |"
        )
    out += [
        "",
        f"Cash distributed: {money(distributed)} = collections {money(collections)} (conserved).",
        f"Equity net (residual - loss): {money(eq['residual'] - eq['loss'])} "
        f"on {money(eq['balance'])} invested ({equity_return:.1%}).",
        "",
    ]
    (ROOT / "sample_output.md").write_text("\n".join(out) + "\n")
    print("\n".join(out[:18]))
    print(f"waterfall conserved: {distributed:,.2f} == {collections:,.2f}")


if __name__ == "__main__":
    main()
