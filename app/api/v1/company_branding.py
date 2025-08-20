from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.base import User, Company
from app.core.tenant import TenantQueryFilter
from typing import Optional
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/branding")
async def get_company_branding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get company branding information for PDF generation
    """
    try:
        # Get the user's company
        company = TenantQueryFilter.apply_organization_filter(
            db.query(Company), Company, current_user.organization_id
        ).first()

        if not company:
            # Return default branding if no company configured
            return {
                "name": "Your Company Name",
                "address": "Company Address",
                "contact_number": "Contact Number",
                "email": "company@email.com",
                "website": "www.yourcompany.com",
                "logo_path": None,
                "gstin": None
            }

        return {
            "name": company.name,
            "address": company.address or "Company Address",
            "contact_number": company.contact_number,
            "email": company.email or "company@email.com",
            "website": company.website,
            "logo_path": company.logo_path,
            "gstin": getattr(company, 'gstin', None),
            "business_type": company.business_type,
            "industry": company.industry
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve company branding: {str(e)}"
        )

@router.post("/audit/pdf-generation")
async def log_pdf_generation(
    audit_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log PDF generation for audit purposes
    """
    try:
        logger.info(
            f"PDF Generated - User: {getattr(current_user, 'username', getattr(current_user, 'email', 'unknown'))}, "
            f"Organization: {getattr(current_user, 'organization_id', 'unknown')}, "
            f"Voucher Type: {audit_data.get('voucher_type')}, "
            f"Voucher Number: {audit_data.get('voucher_number')}, "
            f"Timestamp: {audit_data.get('timestamp')}"
        )
        return {"status": "logged"}

    except Exception as e:
        logger.warning(f"Failed to log PDF generation: {str(e)}")
        return {"status": "warning", "message": "Audit logging failed but PDF generation succeeded"}