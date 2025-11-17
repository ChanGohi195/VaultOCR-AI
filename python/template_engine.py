"""
Phase 9: Custom Template Engine
Provides structured extraction for common document types (receipts, business cards, contracts)
"""

from typing import Dict, Any, Optional, List
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TemplateEngine:
    """Extract structured data from documents using custom templates"""

    def __init__(self):
        """Initialize template engine with built-in templates"""
        self.templates = {
            'receipt': ReceiptTemplate(),
            'business_card': BusinessCardTemplate(),
            'contract': ContractTemplate(),
            'invoice': InvoiceTemplate(),
            'form': FormTemplate()
        }
        logger.info("TemplateEngine initialized with 5 built-in templates")

    def detect_template(self, text: str) -> str:
        """
        Auto-detect document type from text

        Args:
            text: OCR extracted text

        Returns:
            Template name ('receipt', 'business_card', 'contract', etc.)
        """
        text_lower = text.lower()

        # Receipt detection
        receipt_keywords = ['receipt', 'total', 'tax', 'subtotal', 'payment', '領収書', '合計', '小計']
        if any(kw in text_lower for kw in receipt_keywords):
            # Check for typical receipt patterns
            if re.search(r'total|合計|¥|￥|\$', text_lower, re.IGNORECASE):
                return 'receipt'

        # Business card detection
        card_keywords = ['tel', 'email', 'fax', 'mobile', '電話', 'メール', 'FAX', '携帯']
        if any(kw in text_lower for kw in card_keywords):
            # Check for contact info patterns
            if re.search(r'\b\d{2,4}[-\s]?\d{2,4}[-\s]?\d{3,4}\b', text):  # Phone pattern
                return 'business_card'

        # Contract detection
        contract_keywords = ['agreement', 'contract', 'party', 'whereas', 'hereby', '契約', '甲', '乙', '本契約']
        if sum(kw in text_lower for kw in contract_keywords) >= 2:
            return 'contract'

        # Invoice detection
        invoice_keywords = ['invoice', 'bill to', 'invoice number', 'due date', '請求書', '請求番号']
        if any(kw in text_lower for kw in invoice_keywords):
            return 'invoice'

        return 'generic'

    def extract(self, text: str, template_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract structured data using template

        Args:
            text: OCR extracted text
            template_name: Template to use (auto-detect if None)

        Returns:
            Structured data dictionary based on template
        """
        if template_name is None:
            template_name = self.detect_template(text)

        template = self.templates.get(template_name)
        if not template:
            return {
                'error': f'Template not found: {template_name}',
                'raw_text': text
            }

        try:
            result = template.extract(text)
            result['template_used'] = template_name
            result['extraction_timestamp'] = datetime.now().isoformat()
            return result
        except Exception as e:
            logger.error(f"Template extraction failed: {e}")
            return {
                'error': str(e),
                'template_used': template_name,
                'raw_text': text
            }

    def list_templates(self) -> List[Dict[str, str]]:
        """Get list of available templates"""
        return [
            {'name': name, 'description': template.description}
            for name, template in self.templates.items()
        ]


class ReceiptTemplate:
    """Template for extracting receipt/invoice data"""

    description = "Extract structured data from receipts (store, date, total, items)"

    def extract(self, text: str) -> Dict[str, Any]:
        """Extract receipt information"""
        result = {
            'store_name': self._extract_store_name(text),
            'date': self._extract_date(text),
            'total': self._extract_total(text),
            'subtotal': self._extract_subtotal(text),
            'tax': self._extract_tax(text),
            'items': self._extract_items(text),
            'payment_method': self._extract_payment_method(text)
        }

        return result

    def _extract_store_name(self, text: str) -> Optional[str]:
        """Extract store/merchant name (usually first line)"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # First non-empty line is often the store name
            return lines[0]
        return None

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract transaction date"""
        # Common date patterns
        patterns = [
            r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?',  # 2024-01-15 or 2024年1月15日
            r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',  # 01/15/2024
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2}',  # 01/15/24
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        return None

    def _extract_total(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract total amount"""
        # Look for total indicators
        patterns = [
            r'total[:\s]+[\$¥￥]?\s*([0-9,]+\.?\d*)',
            r'合計[:\s]+[\$¥￥]?\s*([0-9,]+\.?\d*)',
            r'[\$¥￥]\s*([0-9,]+\.?\d*)\s*total',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                    currency = self._detect_currency(text)
                    return {'amount': amount, 'currency': currency}
                except ValueError:
                    pass

        return None

    def _extract_subtotal(self, text: str) -> Optional[float]:
        """Extract subtotal amount"""
        patterns = [
            r'subtotal[:\s]+[\$¥￥]?\s*([0-9,]+\.?\d*)',
            r'小計[:\s]+[\$¥￥]?\s*([0-9,]+\.?\d*)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    pass

        return None

    def _extract_tax(self, text: str) -> Optional[float]:
        """Extract tax amount"""
        patterns = [
            r'tax[:\s]+[\$¥￥]?\s*([0-9,]+\.?\d*)',
            r'消費税[:\s]+[\$¥￥]?\s*([0-9,]+\.?\d*)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    pass

        return None

    def _extract_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract line items (simplified)"""
        # This is a simplified version - real implementation would be more complex
        items = []

        # Look for lines with item name and price
        pattern = r'(.+?)\s+[\$¥￥]\s*([0-9,]+\.?\d*)'
        matches = re.findall(pattern, text)

        for name, price_str in matches:
            try:
                price = float(price_str.replace(',', ''))
                items.append({
                    'name': name.strip(),
                    'price': price
                })
            except ValueError:
                pass

        return items

    def _extract_payment_method(self, text: str) -> Optional[str]:
        """Extract payment method"""
        methods = {
            'cash': ['cash', '現金', 'cash paid'],
            'credit': ['credit', 'visa', 'mastercard', 'amex', 'クレジット', 'カード'],
            'debit': ['debit', 'デビット'],
            'electronic': ['paypay', 'suica', 'pasmo', '電子マネー']
        }

        text_lower = text.lower()
        for method_type, keywords in methods.items():
            if any(kw in text_lower for kw in keywords):
                return method_type

        return None

    def _detect_currency(self, text: str) -> str:
        """Detect currency from text"""
        if '¥' in text or '￥' in text or '円' in text:
            return 'JPY'
        elif '$' in text:
            return 'USD'
        elif '€' in text:
            return 'EUR'
        elif '£' in text:
            return 'GBP'
        return 'UNKNOWN'


class BusinessCardTemplate:
    """Template for extracting business card data"""

    description = "Extract contact information from business cards (name, company, phone, email)"

    def extract(self, text: str) -> Dict[str, Any]:
        """Extract business card information"""
        return {
            'name': self._extract_name(text),
            'company': self._extract_company(text),
            'title': self._extract_title(text),
            'phone': self._extract_phone(text),
            'email': self._extract_email(text),
            'address': self._extract_address(text),
            'website': self._extract_website(text)
        }

    def _extract_name(self, text: str) -> Optional[str]:
        """Extract person name (usually larger/first line)"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # First or second line is often the name
            return lines[0] if len(lines[0]) < 30 else lines[1] if len(lines) > 1 else lines[0]
        return None

    def _extract_company(self, text: str) -> Optional[str]:
        """Extract company name"""
        # Look for company indicators
        patterns = [
            r'(.+?)\s*(?:inc\.|corp\.|ltd\.|llc|株式会社|有限会社)',
            r'(?:株式会社|有限会社)\s*(.+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()

        return None

    def _extract_title(self, text: str) -> Optional[str]:
        """Extract job title"""
        titles = ['ceo', 'cto', 'cfo', 'manager', 'director', 'president', 'engineer',
                  '社長', '部長', '課長', '主任', '取締役', 'エンジニア', 'マネージャー']

        text_lower = text.lower()
        for title in titles:
            if title in text_lower:
                # Extract the line containing the title
                for line in text.split('\n'):
                    if title in line.lower():
                        return line.strip()

        return None

    def _extract_phone(self, text: str) -> List[str]:
        """Extract phone numbers"""
        patterns = [
            r'\b\d{2,4}[-\s]?\d{2,4}[-\s]?\d{3,4}\b',  # General phone
            r'\+\d{1,3}[-\s]?\d{1,4}[-\s]?\d{1,4}[-\s]?\d{1,4}',  # International
        ]

        phones = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)

        return list(set(phones))  # Remove duplicates

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(pattern, text)
        return match.group(0) if match else None

    def _extract_address(self, text: str) -> Optional[str]:
        """Extract address (simplified)"""
        # Look for address patterns (zip codes, street numbers)
        patterns = [
            r'\d{3}-\d{4}[^\n]+',  # Japanese zip code + address
            r'\d+\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd|boulevard|blvd)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()

        return None

    def _extract_website(self, text: str) -> Optional[str]:
        """Extract website URL"""
        pattern = r'https?://[^\s]+|www\.[^\s]+'
        match = re.search(pattern, text)
        return match.group(0) if match else None


class ContractTemplate:
    """Template for extracting contract data"""

    description = "Extract key information from contracts (parties, dates, terms)"

    def extract(self, text: str) -> Dict[str, Any]:
        """Extract contract information"""
        return {
            'title': self._extract_title(text),
            'parties': self._extract_parties(text),
            'effective_date': self._extract_effective_date(text),
            'termination_date': self._extract_termination_date(text),
            'key_terms': self._extract_key_terms(text),
            'signatures': self._extract_signatures(text)
        }

    def _extract_title(self, text: str) -> Optional[str]:
        """Extract contract title"""
        # First line or line with "agreement" or "contract"
        for line in text.split('\n')[:5]:
            if 'agreement' in line.lower() or 'contract' in line.lower() or '契約' in line:
                return line.strip()

        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return lines[0] if lines else None

    def _extract_parties(self, text: str) -> List[str]:
        """Extract contracting parties"""
        parties = []

        # Look for party indicators
        patterns = [
            r'party\s+(?:a|b|1|2)[:\s]+(.+)',
            r'between\s+(.+?)\s+and\s+(.+)',
            r'甲[:\s]+(.+)',
            r'乙[:\s]+(.+)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    parties.extend([m.strip() for m in match])
                else:
                    parties.append(match.strip())

        return list(set(parties))

    def _extract_effective_date(self, text: str) -> Optional[str]:
        """Extract effective date"""
        patterns = [
            r'effective\s+date[:\s]+(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            r'dated\s+(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_termination_date(self, text: str) -> Optional[str]:
        """Extract termination date"""
        patterns = [
            r'termination\s+date[:\s]+(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            r'expires?\s+(?:on\s+)?(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms/clauses"""
        # Look for numbered sections or article markers
        pattern = r'(?:article|section|clause)\s+\d+[:\s]+(.+?)(?=\n|article|section|clause|$)'
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)

        return [match.strip()[:200] for match in matches]  # Limit to 200 chars each

    def _extract_signatures(self, text: str) -> List[str]:
        """Extract signature lines"""
        signatures = []

        # Look for signature indicators
        pattern = r'signature[:\s]+(.+)|signed[:\s]+(.+)'
        matches = re.findall(pattern, text, re.IGNORECASE)

        for match in matches:
            for m in match:
                if m:
                    signatures.append(m.strip())

        return signatures


class InvoiceTemplate:
    """Template for extracting invoice data (extends ReceiptTemplate)"""

    description = "Extract structured data from invoices (vendor, client, items, totals)"

    def extract(self, text: str) -> Dict[str, Any]:
        """Extract invoice information"""
        receipt_template = ReceiptTemplate()
        base_result = receipt_template.extract(text)

        # Add invoice-specific fields
        base_result.update({
            'invoice_number': self._extract_invoice_number(text),
            'bill_to': self._extract_bill_to(text),
            'due_date': self._extract_due_date(text),
        })

        return base_result

    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number"""
        pattern = r'invoice\s*#?\s*:?\s*([A-Z0-9-]+)|請求番号\s*:?\s*([A-Z0-9-]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1) or match.group(2)
        return None

    def _extract_bill_to(self, text: str) -> Optional[str]:
        """Extract billing recipient"""
        pattern = r'bill\s+to[:\s]+(.+?)(?=\n\n|invoice|due)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _extract_due_date(self, text: str) -> Optional[str]:
        """Extract payment due date"""
        pattern = r'due\s+date[:\s]+(\d{4}[-/]\d{1,2}[-/]\d{1,2})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None


class FormTemplate:
    """Generic template for forms with labeled fields"""

    description = "Extract key-value pairs from generic forms"

    def extract(self, text: str) -> Dict[str, Any]:
        """Extract form fields (key-value pairs)"""
        fields = {}

        # Look for label: value patterns
        pattern = r'([^:\n]+?):\s*([^:\n]+?)(?=\n|$)'
        matches = re.findall(pattern, text)

        for label, value in matches:
            label_clean = label.strip()
            value_clean = value.strip()

            if label_clean and value_clean and len(label_clean) < 50:
                fields[label_clean] = value_clean

        return {'fields': fields}
