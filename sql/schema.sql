-- Schema for the loan portfolio / CLO waterfall demo (SQLite dialect).

CREATE TABLE loans (
    loan_id     TEXT PRIMARY KEY,
    sector      TEXT NOT NULL,
    balance     REAL NOT NULL CHECK (balance > 0),
    coupon      REAL NOT NULL,          -- annual rate, e.g. 0.072
    pd          REAL NOT NULL,          -- 1-year probability of default
    lgd         REAL NOT NULL,          -- loss given default, 0-1
    delinquency TEXT NOT NULL           -- current, d30, d60, d90plus
);

CREATE TABLE tranches (
    tranche     TEXT PRIMARY KEY,       -- senior, mezzanine, equity
    pct         REAL NOT NULL,          -- share of total portfolio balance
    coupon      REAL                    -- annual coupon; NULL for equity (residual)
);
