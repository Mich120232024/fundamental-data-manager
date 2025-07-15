import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.portfolio import PortfolioPosition, LiveQuote


async def create_sample_portfolio_data():
    """Create sample portfolio positions for testing"""
    
    symbols = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD", "EURJPY", "GBPJPY", "EURGBP"]
    traders = ["John Smith", "Sarah Connor", "Mike Johnson", "Lisa Wang", "David Brown"]
    positions = ["Long", "Short"]
    strategies = ["Momentum", "Mean Reversion", "Arbitrage", "Carry Trade", "Scalping"]
    
    sample_positions = []
    
    for i in range(50):  # Create 50 sample positions
        symbol = random.choice(symbols)
        position = random.choice(positions)
        trader = random.choice(traders)
        strategy = random.choice(strategies)
        
        # Generate realistic prices for FX pairs
        base_price = random.uniform(0.8, 1.8)  # Typical FX range
        current_price = base_price + random.uniform(-0.05, 0.05)
        order_qty = random.randint(10000, 1000000)  # Position size
        
        # Calculate P&L
        if position == "Long":
            pnl = (current_price - base_price) * order_qty
        else:
            pnl = (base_price - current_price) * order_qty
        
        pnl_percent = (pnl / (base_price * order_qty)) * 100 if order_qty > 0 else 0
        
        # Generate Greeks (simplified)
        delta_equiv = order_qty * (1 if position == "Long" else -1)
        
        sample_position = PortfolioPosition(
            TradeID=1000 + i,
            Symbol=symbol,
            Position=position,
            OrderQty=order_qty,
            Price=round(base_price, 5),
            CurrentPrice=round(current_price, 5),
            PnL=round(pnl, 2),
            PnLPercent=round(pnl_percent, 2),
            PnLYTD=round(pnl * random.uniform(0.8, 1.2), 2),
            PnLMTD=round(pnl * random.uniform(0.5, 1.0), 2),
            PnLDTD=round(pnl * random.uniform(0.1, 0.3), 2),
            Bid=round(current_price - 0.0001, 5),
            Ask=round(current_price + 0.0001, 5),
            Spread=0.0002,
            Volume=random.randint(100000, 5000000),
            FundID=random.randint(1, 5),
            Trader=trader,
            Strategy=strategy,
            DeltaEquivalent=delta_equiv,
            Gamma=random.uniform(-1000, 1000),
            Theta=random.uniform(-50, 50),
            Vega=random.uniform(-100, 100),
            EntryTime=datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
            IsActive=True,
            Notes=f"Sample position for {symbol}"
        )
        
        sample_positions.append(sample_position)
    
    return sample_positions


async def create_sample_quotes():
    """Create sample live quotes for testing"""
    
    symbols = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD", "EURJPY", "GBPJPY", "EURGBP"]
    
    sample_quotes = []
    
    for symbol in symbols:
        # Generate realistic FX quotes
        if "JPY" in symbol:
            base_price = random.uniform(100, 150)
        else:
            base_price = random.uniform(0.8, 1.8)
        
        bid = base_price - 0.0001
        ask = base_price + 0.0001
        
        sample_quote = LiveQuote(
            Symbol=symbol,
            Bid=round(bid, 5),
            Ask=round(ask, 5),
            Last=round(base_price, 5),
            Volume=random.randint(1000000, 10000000),
            Change=round(random.uniform(-0.01, 0.01), 5),
            ChangePercent=round(random.uniform(-1.0, 1.0), 2),
            High=round(base_price + random.uniform(0, 0.02), 5),
            Low=round(base_price - random.uniform(0, 0.02), 5),
            Open=round(base_price + random.uniform(-0.01, 0.01), 5),
            Close=round(base_price, 5)
        )
        
        sample_quotes.append(sample_quote)
    
    return sample_quotes


async def seed_database():
    """Seed the database with sample data"""
    async with AsyncSessionLocal() as db:
        try:
            print("🌱 Seeding database with sample data...")
            
            # Create sample portfolio positions
            positions = await create_sample_portfolio_data()
            db.add_all(positions)
            print(f"✅ Created {len(positions)} sample portfolio positions")
            
            # Create sample quotes
            quotes = await create_sample_quotes()
            db.add_all(quotes)
            print(f"✅ Created {len(quotes)} sample live quotes")
            
            # Commit all changes
            await db.commit()
            print("🎉 Database seeding completed successfully!")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Database seeding failed: {e}")
            raise


if __name__ == "__main__":
    # Run the seeding script
    asyncio.run(seed_database())