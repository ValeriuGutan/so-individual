from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    fiscal_code = Column(String)
    address = Column(String)
    created_at = Column(Date, default=datetime.utcnow)

    invoices = relationship("Invoice", back_populates="organization") 