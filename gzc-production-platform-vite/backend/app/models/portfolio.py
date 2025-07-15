from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base


class PortfolioPosition(Base):
    __tablename__ = "portfolio_positions"
    
    # Primary Fields (matching frontend PortfolioItem type)
    Id = Column(Integer, primary_key=True, index=True)
    TradeID = Column(Integer, index=True)
    Symbol = Column(String(50), index=True, nullable=False)
    Position = Column(String(50))  # "Long" or "Short"
    OrderQty = Column(Float, nullable=False)
    Price = Column(Float, nullable=False)
    
    # Financial Metrics
    CurrentPrice = Column(Float)
    PnL = Column(Float)
    PnLPercent = Column(Float)
    PnLYTD = Column(Float, default=0.0)
    PnLMTD = Column(Float, default=0.0)
    PnLDTD = Column(Float, default=0.0)
    
    # Market Data
    Bid = Column(Float)
    Ask = Column(Float)
    Spread = Column(Float)
    Volume = Column(Float)
    
    # Trade Details
    FundID = Column(Integer, index=True)
    Trader = Column(String(100), index=True)
    Strategy = Column(String(100))
    
    # Risk Metrics
    DeltaEquivalent = Column(Float)
    Gamma = Column(Float)
    Theta = Column(Float)
    Vega = Column(Float)
    
    # Timestamps
    EntryTime = Column(DateTime(timezone=True), server_default=func.now())
    LastUpdate = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Status
    IsActive = Column(Boolean, default=True)
    Notes = Column(Text)
    
    def to_dict(self):
        """Convert to dictionary format expected by frontend"""
        return {
            "Id": self.Id,
            "TradeID": self.TradeID,
            "Symbol": self.Symbol,
            "Position": self.Position,
            "OrderQty": self.OrderQty,
            "Price": self.Price,
            "CurrentPrice": self.CurrentPrice,
            "PnL": self.PnL,
            "PnLPercent": self.PnLPercent,
            "PnLYTD": self.PnLYTD,
            "PnLMTD": self.PnLMTD,
            "PnLDTD": self.PnLDTD,
            "Bid": self.Bid,
            "Ask": self.Ask,
            "Spread": self.Spread,
            "Volume": self.Volume,
            "FundID": self.FundID,
            "Trader": self.Trader,
            "Strategy": self.Strategy,
            "DeltaEquivalent": self.DeltaEquivalent,
            "Gamma": self.Gamma,
            "Theta": self.Theta,
            "Vega": self.Vega,
            "EntryTime": self.EntryTime.isoformat() if self.EntryTime else None,
            "LastUpdate": self.LastUpdate.isoformat() if self.LastUpdate else None,
            "IsActive": self.IsActive,
            "Notes": self.Notes
        }


class LiveQuote(Base):
    __tablename__ = "live_quotes"
    
    Id = Column(Integer, primary_key=True, index=True)
    Symbol = Column(String(50), index=True, nullable=False, unique=True)
    Bid = Column(Float, nullable=False)
    Ask = Column(Float, nullable=False)
    Last = Column(Float)
    Volume = Column(Float)
    Change = Column(Float)
    ChangePercent = Column(Float)
    High = Column(Float)
    Low = Column(Float)
    Open = Column(Float)
    Close = Column(Float)
    Timestamp = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary format"""
        return {
            "Symbol": self.Symbol,
            "Bid": self.Bid,
            "Ask": self.Ask,
            "Last": self.Last,
            "Volume": self.Volume,
            "Change": self.Change,
            "ChangePercent": self.ChangePercent,
            "High": self.High,
            "Low": self.Low,
            "Open": self.Open,
            "Close": self.Close,
            "Timestamp": self.Timestamp.isoformat() if self.Timestamp else None
        }