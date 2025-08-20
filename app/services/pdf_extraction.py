"""
PDF Extraction Service for Vouchers
Handles PDF processing and data extraction for various voucher types
"""

import logging
import os
import uuid
from typing import Dict, Any, Optional, List
from fastapi import UploadFile, HTTPException, status
import tempfile
import fitz  # PyMuPDF for PDF processing
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class PDFExtractionService:
    """Service for extracting structured data from PDF documents"""
    
    UPLOAD_DIR = "temp/pdf_uploads"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self):
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
    
    async def extract_voucher_data(self, file: UploadFile, voucher_type: str) -> Dict[str, Any]:
        """
        Extract structured data from PDF based on voucher type
        
        Args:
            file: Uploaded PDF file
            voucher_type: Type of voucher (purchase_voucher, sales_order, etc.)
            
        Returns:
            Dictionary containing extracted voucher data
        """
        
        # Validate file
        await self._validate_pdf_file(file)
        
        # Save file temporarily
        temp_file_path = await self._save_temp_file(file)
        
        try:
            # Extract text from PDF
            text_content = await self._extract_text_from_pdf(temp_file_path)
            
            # Parse text based on voucher type
            if voucher_type == "purchase_voucher":
                return await self._extract_purchase_voucher_data(text_content)
            elif voucher_type == "sales_order":
                return await self._extract_sales_order_data(text_content)
            elif voucher_type == "vendor":
                return await self._extract_vendor_data(text_content)
            elif voucher_type == "customer":
                return await self._extract_customer_data(text_content)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported voucher type: {voucher_type}"
                )
                
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"PDF extraction failed: {str(e)}"
            )
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    async def _validate_pdf_file(self, file: UploadFile) -> None:
        """Validate uploaded PDF file"""
        
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file uploaded"
            )
        
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed"
            )
        
        if file.size and file.size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must be less than 10MB"
            )
    
    async def _save_temp_file(self, file: UploadFile) -> str:
        """Save uploaded file temporarily"""
        
        file_extension = os.path.splitext(file.filename or "")[1]
        temp_filename = f"{uuid.uuid4()}{file_extension}"
        temp_file_path = os.path.join(self.UPLOAD_DIR, temp_filename)
        
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return temp_file_path
    
    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from PDF using PyMuPDF"""
        
        try:
            doc = fitz.open(file_path)
            text_content = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += page.get_text() + "\n"
            
            doc.close()
            return text_content
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to read PDF content"
            )
    
    async def _extract_purchase_voucher_data(self, text: str) -> Dict[str, Any]:
        """Extract data specific to Purchase Voucher"""
        
        # Use regex patterns to extract common fields
        patterns = {
            'invoice_number': r'(?:invoice|bill|voucher)[\s#]*:?\s*([A-Z0-9\-\/]+)',
            'invoice_date': r'(?:date|dated)[\s:]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            'vendor_name': r'(?:vendor|supplier|from)[\s:]*([A-Za-z\s&\.,]+?)(?:\n|address|phone)',
            'amount': r'(?:total|amount|sum)[\s:]*(?:rs\.?|₹)?\s*([0-9,]+\.?\d{0,2})',
            'gst_number': r'(?:gstin|gst\s*no?)[\s:]*([0-9A-Z]{15})',
        }
        
        extracted_data = {
            "vendor_name": self._extract_with_pattern(text, patterns['vendor_name']),
            "invoice_number": self._extract_with_pattern(text, patterns['invoice_number']),
            "invoice_date": self._parse_date(self._extract_with_pattern(text, patterns['invoice_date'])),
            "payment_terms": "Net 30",  # Default
            "notes": "Extracted from PDF invoice",
            "total_amount": self._parse_amount(self._extract_with_pattern(text, patterns['amount'])),
            "items": self._extract_line_items(text, "purchase")
        }
        
        return extracted_data
    
    async def _extract_sales_order_data(self, text: str) -> Dict[str, Any]:
        """Extract data specific to Sales Order"""
        
        patterns = {
            'order_number': r'(?:order|so|sales)[\s#]*:?\s*([A-Z0-9\-\/]+)',
            'order_date': r'(?:date|dated)[\s:]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            'customer_name': r'(?:customer|client|to|bill\s*to)[\s:]*([A-Za-z\s&\.,]+?)(?:\n|address|phone)',
            'amount': r'(?:total|amount|sum)[\s:]*(?:rs\.?|₹)?\s*([0-9,]+\.?\d{0,2})',
        }
        
        extracted_data = {
            "customer_name": self._extract_with_pattern(text, patterns['customer_name']),
            "order_number": self._extract_with_pattern(text, patterns['order_number']),
            "order_date": self._parse_date(self._extract_with_pattern(text, patterns['order_date'])),
            "payment_terms": "Net 15",  # Default
            "notes": "Extracted from PDF sales order",
            "total_amount": self._parse_amount(self._extract_with_pattern(text, patterns['amount'])),
            "items": self._extract_line_items(text, "sales")
        }
        
        return extracted_data
    
    async def _extract_vendor_data(self, text: str) -> Dict[str, Any]:
        """Extract vendor/supplier data from GST certificate or business document"""
        
        patterns = {
            'legal_name': r'1\.\s*Legal Name\s*([\s\S]*?)\s*2\.',
            'trade_name': r'2\.\s*Trade Name, if any\s*([\s\S]*?)\s*3\.',
            'gst_number': r'(?:GSTIN|Registration Number|GST Number)[\s:]*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})',
            'address_block': r'5\.\s*Address of Principal Place of\s*Business\s*([\s\S]*?)\s*6\.',
            'phone': r'(?:Phone|Mobile|Contact Number|Telephone)[\s:]*([+]?[0-9\s\-\(\)]{10,15})',
            'email': r'(?:Email|E-mail|Mail)[\s:]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            'pan_number': r'(?:PAN|Pan Number)[\s:]*([A-Z]{5}[0-9]{4}[A-Z]{1})',
            'state_code': r'(?:State Code)[\s:]*(\d{2})',
            'pin_code': r'(?:PIN Code|Pincode|Postal Code)[\s:]*(\d{6})',
            'state': r'(?:State)[\s:]*([A-Za-z\s]+)(?:PIN|Pin Code|Code|\n)',
        }
        
        legal_name = self._extract_with_pattern(text, patterns['legal_name'])
        trade_name = self._extract_with_pattern(text, patterns['trade_name'])
        gst_number = self._extract_with_pattern(text, patterns['gst_number'])
        address_block = self._extract_with_pattern(text, patterns['address_block'])
        pan_number = self._extract_with_pattern(text, patterns['pan_number']) or (gst_number[2:12] if gst_number else None)
        state_code = self._extract_with_pattern(text, patterns['state_code']) or (gst_number[:2] if gst_number else None)
        
        extracted_data = {
            "name": trade_name.strip() if trade_name and trade_name.strip() else legal_name.strip() if legal_name else None,
            "gst_number": gst_number,
            "address1": None,
            "address2": None,
            "city": None,
            "phone": self._extract_with_pattern(text, patterns['phone']),
            "email": self._extract_with_pattern(text, patterns['email']),
            "pan_number": pan_number,
            "state_code": state_code,
            "pin_code": self._extract_with_pattern(text, patterns['pin_code']),
            "state": self._extract_with_pattern(text, patterns['state']),
            "is_active": True
        }
        
        # Parse address block if available
        if address_block:
            address_patterns = {
                'building_no': r'Building No./Flat No.:\s*([\s\S]*?)(?=\s*Name Of Premises/Building|$)',
                'premises': r'Name Of Premises/Building:\s*([\s\S]*?)(?=\s*Road/Street|$)',
                'road': r'Road/Street:\s*([\s\S]*?)(?=\s*City/Town/Village|$)',
                'city_village': r'City/Town/Village:\s*([\s\S]*?)(?=\s*District|$)',
                'district': r'District:\s*([\s\S]*?)(?=\s*State|$)',
                'state': r'State:\s*([\s\S]*?)(?=\s*PIN Code|$)',
                'pin_code': r'PIN Code:\s*([\s\S]*?)$',
            }
            
            building_no = self._extract_with_pattern(address_block, address_patterns['building_no'])
            premises = self._extract_with_pattern(address_block, address_patterns['premises'])
            road = self._extract_with_pattern(address_block, address_patterns['road'])
            city_village = self._extract_with_pattern(address_block, address_patterns['city_village'])
            district = self._extract_with_pattern(address_block, address_patterns['district'])
            state = self._extract_with_pattern(address_block, address_patterns['state']) or extracted_data["state"]
            pin_code = self._extract_with_pattern(address_block, address_patterns['pin_code']) or extracted_data["pin_code"]
            
            # Construct address1 and address2
            address_parts1 = [part.strip() for part in [building_no, premises, road] if part and part.strip()]
            extracted_data["address1"] = ', '.join(address_parts1) if address_parts1 else None
            
            address_parts2 = [part.strip() for part in [city_village] if part and part.strip()]
            extracted_data["address2"] = ', '.join(address_parts2) if address_parts2 else None
            
            # Set city to district or last part of city_village
            if city_village:
                city_parts = [part.strip() for part in city_village.split(',') if part.strip()]
                extracted_data["city"] = city_parts[-1] if city_parts else district
            else:
                extracted_data["city"] = district
            
            extracted_data["state"] = state
            extracted_data["pin_code"] = pin_code
        
        return {k: v for k, v in extracted_data.items() if v is not None}
    
    async def _extract_customer_data(self, text: str) -> Dict[str, Any]:
        """Extract customer data from business document"""
        
        # Use similar patterns as vendor
        patterns = {
            'legal_name': r'1\.\s*Legal Name\s*([\s\S]*?)\s*2\.',
            'trade_name': r'2\.\s*Trade Name, if any\s*([\s\S]*?)\s*3\.',
            'gst_number': r'(?:GSTIN|Registration Number|GST Number)[\s:]*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})',
            'address_block': r'5\.\s*Address of Principal Place of\s*Business\s*([\s\S]*?)\s*6\.',
            'phone': r'(?:Phone|Mobile|Contact Number|Telephone)[\s:]*([+]?[0-9\s\-\(\)]{10,15})',
            'email': r'(?:Email|E-mail|Mail)[\s:]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            'pan_number': r'(?:PAN|Pan Number)[\s:]*([A-Z]{5}[0-9]{4}[A-Z]{1})',
            'state_code': r'(?:State Code)[\s:]*(\d{2})',
            'pin_code': r'(?:PIN Code|Pincode|Postal Code)[\s:]*(\d{6})',
            'state': r'(?:State)[\s:]*([A-Za-z\s]+)(?:PIN|Pin Code|Code|\n)',
        }
        
        legal_name = self._extract_with_pattern(text, patterns['legal_name'])
        trade_name = self._extract_with_pattern(text, patterns['trade_name'])
        gst_number = self._extract_with_pattern(text, patterns['gst_number'])
        address_block = self._extract_with_pattern(text, patterns['address_block'])
        pan_number = self._extract_with_pattern(text, patterns['pan_number']) or (gst_number[2:12] if gst_number else None)
        state_code = self._extract_with_pattern(text, patterns['state_code']) or (gst_number[:2] if gst_number else None)
        
        extracted_data = {
            "name": trade_name.strip() if trade_name and trade_name.strip() else legal_name.strip() if legal_name else None,
            "gst_number": gst_number,
            "address1": None,
            "address2": None,
            "city": None,
            "phone": self._extract_with_pattern(text, patterns['phone']),
            "email": self._extract_with_pattern(text, patterns['email']),
            "pan_number": pan_number,
            "state_code": state_code,
            "pin_code": self._extract_with_pattern(text, patterns['pin_code']),
            "state": self._extract_with_pattern(text, patterns['state']),
            "is_active": True
        }
        
        # Parse address block if available
        if address_block:
            address_patterns = {
                'building_no': r'Building No./Flat No.:\s*([\s\S]*?)(?=\s*Name Of Premises/Building|$)',
                'premises': r'Name Of Premises/Building:\s*([\s\S]*?)(?=\s*Road/Street|$)',
                'road': r'Road/Street:\s*([\s\S]*?)(?=\s*City/Town/Village|$)',
                'city_village': r'City/Town/Village:\s*([\s\S]*?)(?=\s*District|$)',
                'district': r'District:\s*([\s\S]*?)(?=\s*State|$)',
                'state': r'State:\s*([\s\S]*?)(?=\s*PIN Code|$)',
                'pin_code': r'PIN Code:\s*([\s\S]*?)$',
            }
            
            building_no = self._extract_with_pattern(address_block, address_patterns['building_no'])
            premises = self._extract_with_pattern(address_block, address_patterns['premises'])
            road = self._extract_with_pattern(address_block, address_patterns['road'])
            city_village = self._extract_with_pattern(address_block, address_patterns['city_village'])
            district = self._extract_with_pattern(address_block, address_patterns['district'])
            state = self._extract_with_pattern(address_block, address_patterns['state']) or extracted_data["state"]
            pin_code = self._extract_with_pattern(address_block, address_patterns['pin_code']) or extracted_data["pin_code"]
            
            # Construct address1 and address2
            address_parts1 = [part.strip() for part in [building_no, premises, road] if part and part.strip()]
            extracted_data["address1"] = ', '.join(address_parts1) if address_parts1 else None
            
            address_parts2 = [part.strip() for part in [city_village] if part and part.strip()]
            extracted_data["address2"] = ', '.join(address_parts2) if address_parts2 else None
            
            # Set city to district or last part of city_village
            if city_village:
                city_parts = [part.strip() for part in city_village.split(',') if part.strip()]
                extracted_data["city"] = city_parts[-1] if city_parts else district
            else:
                extracted_data["city"] = district
            
            extracted_data["state"] = state
            extracted_data["pin_code"] = pin_code
        
        return {k: v for k, v in extracted_data.items() if v is not None}
    
    def _extract_with_pattern(self, text: str, pattern: str) -> Optional[str]:
        """Extract text using regex pattern"""
        
        try:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                result = match.group(1).strip()
                # Clean up extra whitespace and newlines
                result = re.sub(r'\s+', ' ', result)
                return result if result else None
        except Exception as e:
            logger.warning(f"Pattern extraction failed for pattern '{pattern}': {str(e)}")
        
        return None
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse and format date string"""
        
        if not date_str:
            return None
        
        try:
            # Try common date formats
            for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y', '%Y-%m-%d', '%m/%d/%Y']:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        except Exception as e:
            logger.warning(f"Date parsing failed: {str(e)}")
        
        return date_str  # Return original if parsing fails
    
    def _parse_amount(self, amount_str: Optional[str]) -> float:
        """Parse amount string to float"""
        
        if not amount_str:
            return 0.0
        
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[₹$,\s]', '', amount_str)
            return float(cleaned)
        except Exception as e:
            logger.warning(f"Amount parsing failed: {str(e)}")
            return 0.0
    
    def _extract_pin_from_address(self, address: Optional[str]) -> Optional[str]:
        """Extract 6-digit PIN code from address string if not found separately"""
        if not address:
            return None
        match = re.search(r'\b(\d{6})\b', address)
        return match.group(1) if match else None
    
    def _extract_line_items(self, text: str, voucher_type: str) -> List[Dict[str, Any]]:
        """Extract line items from the document"""
        
        # Simple table extraction - look for lines with quantity, price, etc.
        items = []
        # Pattern for line items: Description HSN Qty Unit Rate Amount
        line_pattern = r'([A-Za-z\s\-]+)\s+([0-9]{4})\s+([0-9.]+)\s+([A-Za-z]+)\s+([0-9.,]+)\s+([0-9.,]+)'
        
        matches = re.finditer(line_pattern, text, re.MULTILINE)
        
        for match in matches:
            items.append({
                "product_name": match.group(1).strip(),
                "hsn_code": match.group(2),
                "quantity": float(match.group(3)),
                "unit": match.group(4),
                "unit_price": self._parse_amount(match.group(5)),
                "total_amount": self._parse_amount(match.group(6))
            })
        
        if not items:
            logger.warning(f"No line items found in {voucher_type} document")
        
        return items

# Global service instance
pdf_extraction_service = PDFExtractionService()