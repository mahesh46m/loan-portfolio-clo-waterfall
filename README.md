# Loan Portfolio Risk & CLO-Style Waterfall

A portfolio project by **Mahesh M**: credit-risk metrics for a synthetic leveraged-loan portfolio, plus a simplified one-period CLO cash-flow waterfall (senior / mezzanine / equity).

> **Demo project.** All data is synthetic and randomly generated (fixed seed). It does not come from any real lender, servicer, CLO or employer, and the numbers are not real-world metrics.

## What it does

1. **Generate** (`scripts/generate_portfolio.py`): 500 synthetic loans with sector, balance, coupon, 1-year PD, LGD and delinquency status (riskier loans carry higher PD, LGD and coupon), plus a simple 80/10/10 senior/mezz/equity capital structure.
2. **Risk metrics** (`scripts/run_analysis.py`): balance-weighted coupon, PD and LGD; expected loss (balance x PD x LGD); delinquency buckets; sector concentration.
3. **Waterfall**: one annual period of expected cash flows. Collections = interest on performing balance + 25% scheduled principal + recoveries on expected defaults. Cash pays senior interest, mezzanine interest, senior principal, mezzanine principal, then the residual to equity. Losses write tranches down in reverse order: equity, then mezzanine, then senior. The run asserts cash is conserved (distributions equal collections).

## The model, honestly

This is a deterministic, expected-value waterfall - one period, no Monte Carlo, no reinvestment, no OC/IC trigger mechanics. Those are the natural extensions; the point here is a clean, verifiable waterfall that conserves cash and respects priority of payments.

## Run it

Requires Python 3.8+ only (built-in `sqlite3`, no installs).

```bash
python scripts/run_analysis.py   # builds portfolio.db on first run
```

Full output in [`sample_output.md`](sample_output.md). Headline numbers (seed 21): 500 loans, $2.10B balance, WA coupon 7.24%, WA PD 2.96%, WA LGD 43.21%, expected loss $28.4M.

## Example

| Tranche | Start balance | Coupon | Interest paid | Principal paid | Residual | Loss absorbed | End balance |
|---|---|---|---|---|---|---|---|
| senior | $1,680,920,000 | 5.0% | $84,046,000 | $587,663,372 | - | $0 | $1,680,920,000 |
| mezzanine | $210,115,000 | 9.0% | $18,910,350 | $0 | - | $0 | $210,115,000 |
| equity | $210,115,000 | residual | $0 | $0 | $0 | $28,416,637 | $181,698,363 |

## Layout

```
sql/schema.sql               loans + tranches tables
scripts/generate_portfolio.py  deterministic synthetic portfolio
scripts/run_analysis.py      risk metrics + waterfall, writes sample_output.md
```

## Possible extensions

Monte Carlo default simulation with correlation, OC/IC coverage tests and trigger diversion, multiple periods with reinvestment, and a rating-agency-style break-even default-rate analysis.

---
Author: Mahesh M. Released under the MIT License.
