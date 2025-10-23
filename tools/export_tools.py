"""
Export Tools for Gmail Filter Agent

This module provides FunctionTools for exporting email data:
- csv_export: Export filtered emails to CSV file

Features:
- Pandas DataFrame generation for robust CSV handling
- Proper UTF-8 encoding
- Special character escaping
- Timestamp-based filenames
- Configurable output directory
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

from google.genai.types import FunctionDeclaration

# Determine project directory for portable paths
if getattr(sys, 'frozen', False):
    PROJECT_DIR = os.path.dirname(sys.executable)
else:
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# CSV output directory
CSV_OUTPUT_DIR = os.path.join(PROJECT_DIR, 'csv_files')


def ensure_csv_directory():
    """
    Ensure CSV output directory exists.

    Creates the directory if it doesn't exist.
    """
    if not os.path.exists(CSV_OUTPUT_DIR):
        try:
            os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create CSV directory: {e}")


def format_email_for_csv(email: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format email data for CSV export.

    Handles:
    - None/null values
    - List formatting (labels, amounts)
    - Date formatting
    - Text escaping

    Args:
        email: Email dict with various fields

    Returns:
        Dict: Formatted email data ready for CSV
    """
    # Extract detected amounts if available
    amounts = email.get('detected_amounts', [])
    if not amounts:
        amounts = email.get('all_amounts', [])

    # Format amounts as comma-separated string
    amounts_str = ', '.join([f'${amt:.2f}' for amt in amounts]) if amounts else ''

    # Extract labels
    labels = email.get('labels', [])
    labels_str = ', '.join(labels) if labels else ''

    # Handle date formatting
    date = email.get('date', '')
    if not date:
        # Try internal_date (timestamp in milliseconds)
        internal_date = email.get('internal_date', '')
        if internal_date:
            try:
                timestamp = int(internal_date) / 1000
                date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                date = ''

    return {
        'ID': email.get('id', ''),
        'Date': date,
        'From': email.get('from', ''),
        'To': email.get('to', ''),
        'Subject': email.get('subject', ''),
        'Snippet': email.get('snippet', ''),
        'Labels': labels_str,
        'Has_Attachments': 'Yes' if email.get('has_attachments', False) else 'No',
        'Detected_Amounts': amounts_str
    }


def export_emails_to_csv(
    emails: List[Dict[str, Any]],
    filename: Optional[str] = None,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Export list of emails to CSV file.

    Creates a CSV file with columns:
    - ID: Gmail message ID
    - Date: Email date
    - From: Sender
    - To: Recipient(s)
    - Subject: Email subject
    - Snippet: Email preview
    - Labels: Gmail labels
    - Has_Attachments: Yes/No
    - Detected_Amounts: Extracted currency amounts

    Args:
        emails: List of email dicts to export
        filename: Output filename (auto-generated if None)
        output_dir: Output directory (uses CSV_OUTPUT_DIR if None)

    Returns:
        Dict with export results (success, filepath, count)
    """
    try:
        # Ensure output directory exists
        ensure_csv_directory()

        # Determine output directory
        if output_dir is None:
            output_dir = CSV_OUTPUT_DIR

        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'filtered_emails_{timestamp}.csv'

        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'

        # Full output path
        filepath = os.path.join(output_dir, filename)

        # Format emails for CSV
        formatted_emails = [format_email_for_csv(email) for email in emails]

        # Create DataFrame
        df = pd.DataFrame(formatted_emails)

        # Define column order
        column_order = [
            'ID', 'Date', 'From', 'To', 'Subject', 'Snippet',
            'Labels', 'Has_Attachments', 'Detected_Amounts'
        ]

        # Ensure all columns exist
        for col in column_order:
            if col not in df.columns:
                df[col] = ''

        # Reorder columns
        df = df[column_order]

        # Export to CSV
        df.to_csv(filepath, index=False, encoding='utf-8', escapechar='\\')

        return {
            'success': True,
            'filepath': filepath,
            'filename': filename,
            'count': len(emails),
            'message': f'Successfully exported {len(emails)} emails to {filepath}'
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'filepath': '',
            'filename': '',
            'count': 0,
            'message': f'Export failed: {e}'
        }


def generate_csv_summary(filepath: str) -> Dict[str, Any]:
    """
    Generate summary statistics for exported CSV file.

    Args:
        filepath: Path to CSV file

    Returns:
        Dict with summary statistics
    """
    try:
        df = pd.read_csv(filepath, encoding='utf-8')

        summary = {
            'total_emails': len(df),
            'date_range': {
                'earliest': df['Date'].min() if 'Date' in df.columns else None,
                'latest': df['Date'].max() if 'Date' in df.columns else None
            },
            'unique_senders': df['From'].nunique() if 'From' in df.columns else 0,
            'with_attachments': len(df[df['Has_Attachments'] == 'Yes']) if 'Has_Attachments' in df.columns else 0,
            'with_amounts': len(df[df['Detected_Amounts'] != '']) if 'Detected_Amounts' in df.columns else 0
        }

        return summary

    except Exception as e:
        return {
            'error': str(e)
        }


# FunctionDeclaration for csv_export
csv_export = FunctionDeclaration(
    name="csv_export",
    description=(
        "Export filtered emails to CSV file for easy analysis in Excel or other tools. "
        "Creates a CSV with columns: ID, Date, From, To, Subject, Snippet, Labels, Has_Attachments, Detected_Amounts. "
        "Auto-generates timestamp-based filename if not specified. "
        "Saves to csv_files/ directory in project root. "
        "Use this tool to export search results for the user."
    ),
    parameters={
        "type": "object",
        "properties": {
            "emails": {
                "type": "array",
                "description": "List of email objects to export (should include id, date, from, to, subject, snippet, labels, has_attachments, detected_amounts)",
                "items": {"type": "object"}
            },
            "filename": {
                "type": "string",
                "description": "Output filename (optional, auto-generated with timestamp if not provided)"
            }
        },
        "required": ["emails"]
    }
)


# Python function implementation for csv_export
def csv_export_impl(
    emails: List[Dict[str, Any]],
    filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    Implementation of csv_export FunctionTool.

    Args:
        emails: List of email dicts to export
        filename: Optional output filename

    Returns:
        Dict with export results
    """
    return export_emails_to_csv(emails, filename)


# Utility function for appending to existing CSV
def append_to_csv(
    emails: List[Dict[str, Any]],
    filepath: str
) -> Dict[str, Any]:
    """
    Append emails to existing CSV file.

    Args:
        emails: List of email dicts to append
        filepath: Path to existing CSV file

    Returns:
        Dict with append results
    """
    try:
        # Format emails for CSV
        formatted_emails = [format_email_for_csv(email) for email in emails]

        # Create DataFrame
        new_df = pd.DataFrame(formatted_emails)

        # Check if file exists
        if os.path.exists(filepath):
            # Read existing CSV
            existing_df = pd.read_csv(filepath, encoding='utf-8')

            # Append new data
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)

            # Remove duplicates based on ID
            combined_df = combined_df.drop_duplicates(subset=['ID'], keep='first')

            # Export
            combined_df.to_csv(filepath, index=False, encoding='utf-8', escapechar='\\')

            return {
                'success': True,
                'filepath': filepath,
                'added': len(new_df),
                'total': len(combined_df),
                'message': f'Appended {len(new_df)} emails to {filepath}'
            }
        else:
            # File doesn't exist, create new
            return export_emails_to_csv(emails, os.path.basename(filepath), os.path.dirname(filepath))

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'Append failed: {e}'
        }


# Utility function for reading CSV
def read_csv_file(filepath: str) -> Dict[str, Any]:
    """
    Read CSV file and return as list of email dicts.

    Args:
        filepath: Path to CSV file

    Returns:
        Dict with emails list or error
    """
    try:
        df = pd.read_csv(filepath, encoding='utf-8')

        # Convert to list of dicts
        emails = df.to_dict('records')

        return {
            'success': True,
            'emails': emails,
            'count': len(emails)
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'emails': [],
            'count': 0
        }
