from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    fiscal_code = Column(String)
    address = Column(Text)
    created_at = Column(Date, default=datetime.utcnow)

    invoices = relationship("Invoice", back_populates="organization", cascade="all, delete-orphan")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    invoice_number = Column(String, nullable=False, unique=True)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    notes = Column(Text)
    created_at = Column(Date, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    description = Column(Text, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(Date, default=datetime.utcnow)

    invoice = relationship("Invoice", back_populates="items") 