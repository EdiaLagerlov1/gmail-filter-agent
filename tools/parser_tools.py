"""
Parser Tools for Gmail Filter Agent

This module provides FunctionTools for extracting and parsing data from emails:
- amount_extractor: Extract currency amounts from email content

Features:
- Multi-currency support ($, €, £, ¥, USD, EUR, GBP, JPY)
- Multiple format recognition (1000, 1,000, 1,000.00)
- Min/max filtering
- Extraction from subject and body
"""

import re
from typing import Dict, List, Any, Optional

from google.genai.types import FunctionDeclaration


# Currency patterns for amount extraction
CURRENCY_PATTERNS = [
    # Symbol-based: $100, $100.00, $1,000.00, $1,000,000.00
    r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
    r'€\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
    r'£\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
    r'¥\s*(\d{1,3}(?:,\d{3})*(?:\.\d{0,2})?)',

    # Code-based: 100 USD, 50.00 EUR, 25 GBP
    r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*USD',
    r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*EUR',
    r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*GBP',
    r'(\d{1,3}(?:,\d{3})*(?:\.\d{0,2})?)\s*JPY',

    # Generic amount with currency words
    r'(?:amount|total|sum|payment|charge|price|cost|fee)[\s:]+\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',

    # Numbers with currency context
    r'(?:paid|received|sent|transferred|charged|billed)[\s:]+\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
]


def extract_amounts_from_text(text: str) -> List[float]:
    """
    Extract all currency amounts from text using regex patterns.

    Supports multiple currencies and formats:
    - $100, $100.00, $1,000.00, $1,000,000.00
    - €50, £25, ¥1000
    - 100 USD, 50.00 EUR, 25 GBP, 1000 JPY
    - Context-aware: "payment: $500", "total $1,234.56"

    Args:
        text: Text to search for amounts

    Returns:
        List[float]: List of extracted amounts (as float values)
    """
    amounts = []

    if not text:
        return amounts

    # Convert to string if needed
    text = str(text)

    # Apply all currency patterns
    for pattern in CURRENCY_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                # Extract the numeric part
                amount_str = match.group(1)

                # Remove commas and convert to float
                amount = float(amount_str.replace(',', ''))

                amounts.append(amount)
            except (ValueError, IndexError):
                continue

    # Remove duplicates while preserving order
    seen = set()
    unique_amounts = []
    for amount in amounts:
        if amount not in seen:
            seen.add(amount)
            unique_amounts.append(amount)

    return unique_amounts


def filter_amounts_by_range(
    amounts: List[float],
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
) -> List[float]:
    """
    Filter amounts by min/max range.

    Args:
        amounts: List of amounts to filter
        min_amount: Minimum amount (inclusive)
        max_amount: Maximum amount (inclusive)

    Returns:
        List[float]: Filtered amounts
    """
    filtered = amounts

    if min_amount is not None:
        filtered = [amt for amt in filtered if amt >= min_amount]

    if max_amount is not None:
        filtered = [amt for amt in filtered if amt <= max_amount]

    return filtered


def extract_amounts_from_email(
    email: Dict[str, Any],
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
) -> Dict[str, Any]:
    """
    Extract and filter amounts from email subject and body.

    Args:
        email: Email dict with 'subject' and 'body' keys
        min_amount: Minimum amount to include
        max_amount: Maximum amount to include

    Returns:
        Dict with extracted amounts and filtering results
    """
    subject = email.get('subject', '')
    body = email.get('body', '')
    snippet = email.get('snippet', '')

    # Extract from all text sources
    subject_amounts = extract_amounts_from_text(subject)
    body_amounts = extract_amounts_from_text(body)
    snippet_amounts = extract_amounts_from_text(snippet)

    # Combine all amounts (remove duplicates)
    all_amounts = list(set(subject_amounts + body_amounts + snippet_amounts))
    all_amounts.sort(reverse=True)  # Sort descending

    # Apply filtering
    filtered_amounts = filter_amounts_by_range(all_amounts, min_amount, max_amount)

    return {
        'email_id': email.get('id', ''),
        'subject': subject,
        'all_amounts': all_amounts,
        'filtered_amounts': filtered_amounts,
        'has_amounts': len(all_amounts) > 0,
        'matches_filter': len(filtered_amounts) > 0,
        'total_found': len(all_amounts),
        'total_matching': len(filtered_amounts)
    }


# FunctionDeclaration for amount_extractor
amount_extractor = FunctionDeclaration(
    name="amount_extractor",
    description=(
        "Extract currency amounts from email content (subject, body, snippet). "
        "Supports multiple currencies ($, €, £, ¥, USD, EUR, GBP, JPY) and formats. "
        "Can filter by min/max amount range. "
        "Use this tool to find emails with specific payment amounts or to analyze transaction values. "
        "Returns all detected amounts and filtering results."
    ),
    parameters={
        "type": "object",
        "properties": {
            "email": {
                "type": "object",
                "description": "Email object with 'id', 'subject', 'body', and 'snippet' fields",
                "properties": {
                    "id": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                    "snippet": {"type": "string"}
                }
            },
            "min_amount": {
                "type": "number",
                "description": "Minimum amount to include (optional, filters out amounts below this value)"
            },
            "max_amount": {
                "type": "number",
                "description": "Maximum amount to include (optional, filters out amounts above this value)"
            }
        },
        "required": ["email"]
    }
)


# Python function implementation for amount_extractor
def amount_extractor_impl(
    email: Dict[str, Any],
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
) -> Dict[str, Any]:
    """
    Implementation of amount_extractor FunctionTool.

    Args:
        email: Email dict with subject, body, snippet
        min_amount: Minimum amount to include
        max_amount: Maximum amount to include

    Returns:
        Dict with extraction results
    """
    try:
        result = extract_amounts_from_email(email, min_amount, max_amount)
        result['success'] = True
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'email_id': email.get('id', ''),
            'all_amounts': [],
            'filtered_amounts': [],
            'has_amounts': False,
            'matches_filter': False,
            'total_found': 0,
            'total_matching': 0
        }


# Utility function for batch processing
def extract_amounts_from_multiple_emails(
    emails: List[Dict[str, Any]],
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Extract amounts from multiple emails and filter.

    Args:
        emails: List of email dicts
        min_amount: Minimum amount filter
        max_amount: Maximum amount filter

    Returns:
        List[Dict]: Extraction results for each email
    """
    results = []

    for email in emails:
        result = extract_amounts_from_email(email, min_amount, max_amount)
        results.append(result)

    return results


def filter_emails_by_amount(
    emails: List[Dict[str, Any]],
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Filter emails that contain amounts within specified range.

    Args:
        emails: List of email dicts
        min_amount: Minimum amount to include
        max_amount: Maximum amount to include

    Returns:
        List[Dict]: Emails that match the amount criteria
    """
    matching_emails = []

    for email in emails:
        result = extract_amounts_from_email(email, min_amount, max_amount)

        if result['matches_filter']:
            # Add amount info to email
            email_with_amounts = email.copy()
            email_with_amounts['detected_amounts'] = result['filtered_amounts']
            email_with_amounts['all_amounts'] = result['all_amounts']
            matching_emails.append(email_with_amounts)

    return matching_emails
