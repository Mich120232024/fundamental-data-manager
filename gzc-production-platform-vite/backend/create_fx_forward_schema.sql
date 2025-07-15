-- FX Forward Trades Database Schema
-- Based on industry standard terminology for foreign exchange forward contracts

CREATE TABLE IF NOT EXISTS fx_forward_trades (
    -- Primary identifiers
    id VARCHAR(20) PRIMARY KEY,
    trade_reference VARCHAR(50) UNIQUE NOT NULL,
    deal_number VARCHAR(30),
    
    -- Contract type and classification
    product_type VARCHAR(20) NOT NULL DEFAULT 'FX_FORWARD', -- FX_FORWARD, NDF, FX_SWAP
    contract_type VARCHAR(20) NOT NULL, -- OUTRIGHT, SWAP_NEAR, SWAP_FAR
    settlement_type VARCHAR(15) NOT NULL, -- DELIVERABLE, NON_DELIVERABLE
    
    -- Date fields (critical for FX forwards)
    trade_date DATE NOT NULL,
    value_date DATE NOT NULL, -- Settlement date
    spot_date DATE, -- Usually T+2 from trade date
    fixing_date DATE, -- For NDFs only
    maturity_date DATE,
    
    -- Currency pair information
    base_currency CHAR(3) NOT NULL, -- ISO 4217 currency code (bought currency)
    quote_currency CHAR(3) NOT NULL, -- ISO 4217 currency code (sold currency)
    currency_pair VARCHAR(7) NOT NULL, -- e.g., 'EUR/USD'
    settlement_currency CHAR(3), -- For NDFs
    
    -- Position and direction
    buy_sell_indicator VARCHAR(4) NOT NULL, -- BUY or SELL (from client perspective)
    position_type VARCHAR(5) NOT NULL, -- LONG or SHORT
    
    -- Amounts and notionals
    base_currency_amount DECIMAL(18,4) NOT NULL, -- Amount in base currency
    quote_currency_amount DECIMAL(18,4) NOT NULL, -- Amount in quote currency
    notional_amount DECIMAL(18,4) NOT NULL, -- Primary notional
    notional_currency CHAR(3) NOT NULL, -- Currency of the notional
    settlement_amount DECIMAL(18,4), -- For cash settlement
    
    -- Rates and pricing
    spot_rate DECIMAL(12,6) NOT NULL, -- Current market rate at trade initiation
    forward_rate DECIMAL(12,6) NOT NULL, -- Agreed forward rate
    forward_points DECIMAL(8,4), -- Forward rate - spot rate
    market_rate DECIMAL(12,6), -- Current market rate for revaluation
    
    -- P&L and risk metrics
    unrealized_pnl DECIMAL(15,4) DEFAULT 0, -- Mark-to-market P&L
    realized_pnl DECIMAL(15,4) DEFAULT 0, -- Actual P&L on settlement
    pnl_currency CHAR(3) DEFAULT 'USD', -- Currency for P&L reporting
    
    -- Interest rate information (for forward pricing)
    base_interest_rate DECIMAL(8,4), -- Interest rate for base currency
    quote_interest_rate DECIMAL(8,4), -- Interest rate for quote currency
    tenor_days INTEGER, -- Number of days to maturity
    tenor_description VARCHAR(10), -- e.g., '3M', '6M', '1Y'
    
    -- Counterparty and execution details
    counterparty VARCHAR(100) NOT NULL,
    counterparty_id VARCHAR(20),
    internal_trader VARCHAR(50) NOT NULL,
    trader_book VARCHAR(30),
    sales_person VARCHAR(50),
    client_reference VARCHAR(50),
    
    -- Execution and confirmation
    execution_venue VARCHAR(30), -- VOICE, ELECTRONIC, BLOOMBERG, etc.
    confirmation_status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, CONFIRMED, FAILED
    confirmation_method VARCHAR(20), -- SWIFT, EMAIL, ELECTRONIC
    
    -- Settlement instructions
    base_currency_account VARCHAR(50),
    quote_currency_account VARCHAR(50),
    settlement_instructions TEXT,
    nostro_account VARCHAR(50), -- Bank's account with correspondent
    vostro_account VARCHAR(50), -- Correspondent's account with bank
    
    -- Status and lifecycle
    trade_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, SETTLED, CANCELLED, MATURED
    lifecycle_status VARCHAR(20) DEFAULT 'LIVE', -- LIVE, EXPIRED, EXERCISED
    cancellation_reason VARCHAR(100),
    
    -- Risk and compliance
    credit_limit_utilization DECIMAL(15,4),
    risk_weight DECIMAL(5,2) DEFAULT 1.0,
    regulatory_capital DECIMAL(15,4),
    basel_risk_weight DECIMAL(5,2),
    
    -- Pricing and valuation
    valuation_model VARCHAR(30) DEFAULT 'FORWARD_POINTS',
    discount_curve VARCHAR(30),
    volatility_surface VARCHAR(30),
    
    -- Commission and fees
    brokerage_amount DECIMAL(10,4) DEFAULT 0,
    brokerage_currency CHAR(3) DEFAULT 'USD',
    commission_rate DECIMAL(6,4) DEFAULT 0,
    spread_bps DECIMAL(6,2) DEFAULT 0, -- Spread in basis points
    
    -- Documentation and legal
    master_agreement VARCHAR(50), -- ISDA, CSA, etc.
    trade_confirmation_id VARCHAR(50),
    legal_entity VARCHAR(100),
    
    -- System and audit fields
    source_system VARCHAR(30) DEFAULT 'GZC_PLATFORM',
    external_trade_id VARCHAR(50),
    booking_system VARCHAR(30),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) NOT NULL,
    updated_by VARCHAR(50),
    version INTEGER DEFAULT 1,
    
    -- Additional metadata
    business_purpose VARCHAR(100), -- HEDGE, SPECULATION, ARBITRAGE
    hedge_relationship VARCHAR(50), -- Links to hedged item
    hedge_effectiveness DECIMAL(5,2), -- For hedge accounting
    fair_value_adjustment DECIMAL(15,4) DEFAULT 0,
    accrued_interest DECIMAL(15,4) DEFAULT 0,
    
    -- Constraints
    CONSTRAINT chk_currency_pair CHECK (base_currency != quote_currency),
    CONSTRAINT chk_value_date CHECK (value_date >= trade_date),
    CONSTRAINT chk_amounts CHECK (base_currency_amount > 0 AND quote_currency_amount > 0),
    CONSTRAINT chk_rates CHECK (spot_rate > 0 AND forward_rate > 0),
    CONSTRAINT chk_trade_status CHECK (trade_status IN ('ACTIVE', 'SETTLED', 'CANCELLED', 'MATURED', 'EXPIRED')),
    CONSTRAINT chk_position_type CHECK (position_type IN ('LONG', 'SHORT')),
    CONSTRAINT chk_buy_sell CHECK (buy_sell_indicator IN ('BUY', 'SELL'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_fx_forward_trade_date ON fx_forward_trades(trade_date);
CREATE INDEX IF NOT EXISTS idx_fx_forward_value_date ON fx_forward_trades(value_date);
CREATE INDEX IF NOT EXISTS idx_fx_forward_currency_pair ON fx_forward_trades(currency_pair);
CREATE INDEX IF NOT EXISTS idx_fx_forward_counterparty ON fx_forward_trades(counterparty);
CREATE INDEX IF NOT EXISTS idx_fx_forward_trader ON fx_forward_trades(internal_trader);
CREATE INDEX IF NOT EXISTS idx_fx_forward_status ON fx_forward_trades(trade_status);
CREATE INDEX IF NOT EXISTS idx_fx_forward_updated ON fx_forward_trades(updated_at);

-- Sample data with proper FX forward terminology
INSERT INTO fx_forward_trades (
    id, trade_reference, contract_type, settlement_type,
    trade_date, value_date, spot_date,
    base_currency, quote_currency, currency_pair,
    buy_sell_indicator, position_type,
    base_currency_amount, quote_currency_amount, notional_amount, notional_currency,
    spot_rate, forward_rate, forward_points, market_rate,
    unrealized_pnl, pnl_currency,
    base_interest_rate, quote_interest_rate, tenor_days, tenor_description,
    counterparty, internal_trader, trader_book,
    execution_venue, confirmation_status,
    trade_status, created_by
) VALUES 
(
    'FWD2025070001', 'GZC-EUR-USD-20250701-001', 'OUTRIGHT', 'DELIVERABLE',
    '2025-07-01', '2025-09-01', '2025-07-03',
    'EUR', 'USD', 'EUR/USD',
    'BUY', 'LONG',
    10000000.00, 10950000.00, 10000000.00, 'EUR',
    1.0920, 1.0950, 30.0, 1.0987,
    37000.00, 'USD',
    3.25, 4.75, 62, '2M',
    'Goldman Sachs International', 'John Smith', 'FX_SPOT_BOOK',
    'VOICE', 'CONFIRMED',
    'ACTIVE', 'system'
),
(
    'FWD2025062801', 'GZC-GBP-USD-20250628-001', 'OUTRIGHT', 'DELIVERABLE',
    '2025-06-28', '2025-08-28', '2025-07-02',
    'GBP', 'USD', 'GBP/USD',
    'SELL', 'SHORT',
    5000000.00, 6375000.00, 5000000.00, 'GBP',
    1.2780, 1.2750, -30.0, 1.2723,
    -13500.00, 'USD',
    4.85, 4.75, 61, '2M',
    'JP Morgan Chase Bank', 'Sarah Johnson', 'FX_FORWARD_BOOK',
    'ELECTRONIC', 'CONFIRMED',
    'ACTIVE', 'system'
),
(
    'FWD2025062501', 'GZC-USD-JPY-20250625-001', 'OUTRIGHT', 'DELIVERABLE',
    '2025-06-25', '2025-12-25', '2025-06-27',
    'USD', 'JPY', 'USD/JPY',
    'BUY', 'LONG',
    8000000.00, 1268000000.00, 8000000.00, 'USD',
    158.20, 158.50, 30.0, 159.25,
    37841.00, 'USD',
    4.75, 0.25, 183, '6M',
    'Deutsche Bank AG', 'Mike Chen', 'FX_FORWARD_BOOK',
    'BLOOMBERG', 'CONFIRMED',
    'ACTIVE', 'system'
),
(
    'FWD2025062001', 'GZC-AUD-USD-20250620-001', 'OUTRIGHT', 'DELIVERABLE',
    '2025-06-20', '2025-07-20', '2025-06-24',
    'AUD', 'USD', 'AUD/USD',
    'SELL', 'SHORT',
    3000000.00, 2055000.00, 3000000.00, 'AUD',
    0.6870, 0.6850, -20.0, 0.6835,
    -4500.00, 'USD',
    4.35, 4.75, 30, '1M',
    'UBS AG', 'David Wilson', 'FX_SPOT_BOOK',
    'VOICE', 'CONFIRMED',
    'SETTLED', 'system'
),
(
    'FWD2025061501', 'GZC-USD-CHF-20250615-001', 'OUTRIGHT', 'DELIVERABLE',
    '2025-06-15', '2025-09-15', '2025-06-17',
    'USD', 'CHF', 'USD/CHF',
    'BUY', 'LONG',
    6000000.00, 5232000.00, 6000000.00, 'USD',
    0.8700, 0.8720, 20.0, 0.8735,
    10338.00, 'USD',
    4.75, 1.25, 92, '3M',
    'Credit Suisse AG', 'Anna Rodriguez', 'FX_FORWARD_BOOK',
    'ELECTRONIC', 'CONFIRMED',
    'ACTIVE', 'system'
);

-- Trigger to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_fx_forward_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER fx_forward_updated_at_trigger
    BEFORE UPDATE ON fx_forward_trades
    FOR EACH ROW
    EXECUTE FUNCTION update_fx_forward_updated_at();