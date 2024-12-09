from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.models import Organization, Invoice, InvoiceItem
from pydantic import BaseModel, condecimal
from datetime import date
from decimal import Decimal

router = APIRouter()

# Scheme Pydantic
class OrganizationBase(BaseModel):
    name: str
    fiscal_code: Optional[str] = None
    address: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: int
    created_at: date

    class Config:
        from_attributes = True

class InvoiceItemBase(BaseModel):
    description: str
    quantity: float
    unit_price: float

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItemResponse(BaseModel):
    id: int
    description: str
    quantity: float
    unit_price: float
    total_price: float

    class Config:
        from_attributes = True

class InvoiceBase(BaseModel):
    organization_id: int
    invoice_number: str
    issue_date: date
    due_date: date
    notes: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]

class InvoiceResponse(BaseModel):
    id: int
    organization_id: int
    organization_name: str
    invoice_number: str
    issue_date: date
    due_date: date
    total_amount: float
    notes: Optional[str] = None
    created_at: date
    items: List[InvoiceItemResponse]

    class Config:
        from_attributes = True

# Rute pentru organizații
@router.post("/organizations/", response_model=OrganizationResponse)
def create_organization(org: OrganizationCreate, db: Session = Depends(get_db)):
    db_org = Organization(**org.dict())
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

@router.get("/organizations/", response_model=List[OrganizationResponse])
def get_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Organization).offset(skip).limit(limit).all()

@router.get("/organizations/{org_id}", response_model=OrganizationResponse)
def get_organization(org_id: int, db: Session = Depends(get_db)):
    db_org = db.query(Organization).filter(Organization.id == org_id).first()
    if db_org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_org

@router.delete("/organizations/{org_id}")
def delete_organization(org_id: int, db: Session = Depends(get_db)):
    db_org = db.query(Organization).filter(Organization.id == org_id).first()
    if db_org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    db.delete(db_org)
    db.commit()
    return {"message": "Organization deleted successfully"}

@router.put("/organizations/{org_id}", response_model=OrganizationResponse)
def update_organization(org_id: int, org: OrganizationCreate, db: Session = Depends(get_db)):
    db_org = db.query(Organization).filter(Organization.id == org_id).first()
    if db_org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Actualizăm câmpurile
    for key, value in org.dict().items():
        setattr(db_org, key, value)
    
    db.commit()
    db.refresh(db_org)
    return db_org

# Rute pentru facturi
@router.post("/invoices/", response_model=InvoiceResponse)
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    try:
        # Verificăm dacă organizația există
        org = db.query(Organization).filter(Organization.id == invoice.organization_id).first()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Calculăm suma totală
        total_amount = Decimal('0')
        invoice_dict = invoice.dict()
        items = invoice_dict.pop('items')
        
        # Creăm factura
        db_invoice = Invoice(**invoice_dict, total_amount=total_amount)
        db.add(db_invoice)
        db.flush()
        
        # Adăugăm items și calculăm totalul
        for item in items:
            item_total = Decimal(str(item['quantity'] * item['unit_price']))
            total_amount += item_total
            
            db_item = InvoiceItem(
                invoice_id=db_invoice.id,
                description=item['description'],
                quantity=Decimal(str(item['quantity'])),
                unit_price=Decimal(str(item['unit_price'])),
                total_price=item_total
            )
            db.add(db_item)
        
        # Actualizăm suma totală
        db_invoice.total_amount = total_amount
        db.commit()
        db.refresh(db_invoice)
        
        return {
            'id': db_invoice.id,
            'organization_id': db_invoice.organization_id,
            'organization_name': org.name,
            'invoice_number': db_invoice.invoice_number,
            'issue_date': db_invoice.issue_date,
            'due_date': db_invoice.due_date,
            'total_amount': float(db_invoice.total_amount),
            'notes': db_invoice.notes,
            'created_at': db_invoice.created_at,
            'items': [{
                'id': item.id,
                'description': item.description,
                'quantity': float(item.quantity),
                'unit_price': float(item.unit_price),
                'total_price': float(item.total_price)
            } for item in db_invoice.items]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create invoice: {str(e)}"
        )

@router.get("/invoices/", response_model=List[InvoiceResponse])
def get_invoices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        invoices = db.query(Invoice).offset(skip).limit(limit).all()
        response_invoices = []
        for invoice in invoices:
            # Convertim explicit valorile Decimal în float pentru serializare
            invoice_dict = {
                'id': invoice.id,
                'organization_id': invoice.organization_id,
                'organization_name': invoice.organization.name,
                'invoice_number': invoice.invoice_number,
                'issue_date': invoice.issue_date,
                'due_date': invoice.due_date,
                'total_amount': float(invoice.total_amount),
                'notes': invoice.notes,
                'created_at': invoice.created_at,
                'items': [{
                    'id': item.id,
                    'description': item.description,
                    'quantity': float(item.quantity),
                    'unit_price': float(item.unit_price),
                    'total_price': float(item.total_price)
                } for item in invoice.items]
            }
            response_invoices.append(invoice_dict)
        return response_invoices
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading invoices: {str(e)}"
        )

@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if db_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return db_invoice

@router.put("/invoices/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(invoice_id: int, invoice: InvoiceCreate, db: Session = Depends(get_db)):
    try:
        # Verificăm dacă factura există
        db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if db_invoice is None:
            raise HTTPException(status_code=404, detail="Invoice not found")
            
        # Verificăm dacă organizația există
        org = db.query(Organization).filter(Organization.id == invoice.organization_id).first()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Ștergem items existente
        for item in db_invoice.items:
            db.delete(item)
            
        # Actualizăm câmpurile de bază
        invoice_dict = invoice.dict()
        items = invoice_dict.pop('items')
        
        for key, value in invoice_dict.items():
            setattr(db_invoice, key, value)
            
        # Calculăm suma totală și adăugăm items noi
        total_amount = Decimal('0')
        for item in items:
            item_total = Decimal(str(item['quantity'] * item['unit_price']))
            total_amount += item_total
            
            db_item = InvoiceItem(
                invoice_id=db_invoice.id,
                description=item['description'],
                quantity=Decimal(str(item['quantity'])),
                unit_price=Decimal(str(item['unit_price'])),
                total_price=item_total
            )
            db.add(db_item)
            
        db_invoice.total_amount = total_amount
        db.commit()
        db.refresh(db_invoice)
        
        return {
            'id': db_invoice.id,
            'organization_id': db_invoice.organization_id,
            'organization_name': org.name,
            'invoice_number': db_invoice.invoice_number,
            'issue_date': db_invoice.issue_date,
            'due_date': db_invoice.due_date,
            'total_amount': float(db_invoice.total_amount),
            'notes': db_invoice.notes,
            'created_at': db_invoice.created_at,
            'items': [{
                'id': item.id,
                'description': item.description,
                'quantity': float(item.quantity),
                'unit_price': float(item.unit_price),
                'total_price': float(item.total_price)
            } for item in db_invoice.items]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not update invoice: {str(e)}"
        )

@router.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    try:
        db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if db_invoice is None:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        db.delete(db_invoice)
        db.commit()
        return {"message": "Invoice deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete invoice: {str(e)}"
        )