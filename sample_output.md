# Portfolio risk & CLO waterfall (synthetic data)

Produced by `scripts/run_analysis.py`. All data is synthetic.

## Portfolio summary

- Loans: **500**, total balance **$2,101,150,000**
- Balance-weighted coupon: **7.24%**
- Balance-weighted PD: **2.96%**, LGD: **43.21%**
- 1-year expected loss (balance x PD x LGD): **$28,416,637**

## Delinquency buckets

| Status | Loans | Balance |
|---|---|---|
| current | 454 | $1,927,220,000 |
| d30 | 21 | $80,910,000 |
| d60 | 16 | $55,530,000 |
| d90plus | 9 | $37,490,000 |

## Top sectors by balance

| Sector | Balance | Expected loss |
|---|---|---|
| Technology | $348,300,000 | $4,224,676 |
| Healthcare | $308,030,000 | $4,055,173 |
| Industrials | $279,020,000 | $3,885,279 |
| Consumer | $247,100,000 | $3,081,735 |
| Financials | $233,350,000 | $3,414,071 |

## One-period waterfall

- Interest collections: $147,050,312
- Scheduled principal (25% of performing): $509,721,318
- Recoveries on expected defaults: $33,848,092
- **Total collections: $690,619,722**

| Tranche | Start balance | Coupon | Interest paid | Principal paid | Residual | Loss absorbed | End balance |
|---|---|---|---|---|---|---|---|
| senior | $1,680,920,000 | 5.0% | $84,046,000 | $587,663,372 | - | $0 | $1,680,920,000 |
| mezzanine | $210,115,000 | 9.0% | $18,910,350 | $0 | - | $0 | $210,115,000 |
| equity | $210,115,000 | residual | $0 | $0 | $0 | $28,416,637 | $181,698,363 |

Cash distributed: $690,619,722 = collections $690,619,722 (conserved).
Equity net (residual - loss): $-28,416,637 on $210,115,000 invested (-13.5%).
