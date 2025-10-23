"""
Gmail Tools for Gmail Filter Agent

This module provides FunctionTools for Gmail API integration:
- gmail_search: Convert natural language to Gmail query and search
- email_fetcher: Fetch full email details by ID

Features:
- OAuth 2.0 authentication with token caching
- Natural language to Gmail query syntax conversion
- Read-only access (gmail.readonly scope)
- Comprehensive error handling
"""

import os
import sys
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dateutil import parser as date_parser

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.genai.types import FunctionDeclaration, Tool

# Determine project directory for portable paths
if getattr(sys, 'frozen', False):
    PROJECT_DIR = os.path.dirname(sys.executable)
else:
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Gmail API scope (read-only for security)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# File paths relative to project directory
CREDENTIALS_FILE = os.path.join(PROJECT_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(PROJECT_DIR, 'token.json')


def get_gmail_service():
    """
    Authenticate and return Gmail API service instance.

    Uses OAuth 2.0 flow with token caching:
    1. Check for existing valid token
    2. Refresh token if expired
    3. Run OAuth flow if no valid token exists

    Returns:
        googleapiclient.discovery.Resource: Gmail API service instance

    Raises:
        FileNotFoundError: If credentials.json is missing
        Exception: If authentication fails
    """
    creds = None

    # Check if credentials.json exists
    if not os.path.exists(CREDENTIALS_FILE):
        error_msg = (
            f"ERROR: credentials.json not found at {CREDENTIALS_FILE}\n\n"
            "To set up Gmail API credentials:\n"
            "1. Go to https://console.cloud.google.com/\n"
            "2. Create a new project or select existing one\n"
            "3. Enable Gmail API\n"
            "4. Create OAuth 2.0 credentials (Desktop app)\n"
            "5. Download credentials.json to the project directory\n"
        )
        raise FileNotFoundError(error_msg)

    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"Warning: Could not load token file: {e}")
            creds = None

    # Refresh or obtain new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed: {e}")
                creds = None

        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                raise Exception(f"OAuth authentication failed: {e}")

        # Save credentials for future use
        try:
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"Warning: Could not save token: {e}")

    # Build and return Gmail service
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        raise Exception(f"Failed to build Gmail service: {e}")


def convert_natural_language_to_gmail_query(
    user_query: str,
    sender: Optional[str] = None,
    after_date: Optional[str] = None,
    before_date: Optional[str] = None,
    has_attachment: Optional[bool] = None,
    label: Optional[str] = None
) -> str:
    """
    Convert natural language query and filters to Gmail search syntax.

    Gmail Query Operators:
    - from:sender@example.com
    - after:YYYY/MM/DD
    - before:YYYY/MM/DD
    - has:attachment
    - filename:pdf
    - label:inbox
    - subject:keyword
    - Keywords without operator search everywhere

    Args:
        user_query: Natural language search query
        sender: Email address to filter by sender
        after_date: Date string (YYYY-MM-DD or relative like "30 days ago")
        before_date: Date string (YYYY-MM-DD or relative)
        has_attachment: Filter for emails with attachments
        label: Gmail label to filter (inbox, sent, etc.)

    Returns:
        str: Gmail query syntax string
    """
    query_parts = []

    # Add sender filter
    if sender:
        query_parts.append(f"from:{sender}")

    # Parse and add date filters
    if after_date:
        try:
            parsed_date = parse_relative_date(after_date)
            query_parts.append(f"after:{parsed_date.strftime('%Y/%m/%d')}")
        except Exception as e:
            print(f"Warning: Could not parse after_date '{after_date}': {e}")

    if before_date:
        try:
            parsed_date = parse_relative_date(before_date)
            query_parts.append(f"before:{parsed_date.strftime('%Y/%m/%d')}")
        except Exception as e:
            print(f"Warning: Could not parse before_date '{before_date}': {e}")

    # Add attachment filter
    if has_attachment:
        query_parts.append("has:attachment")

    # Add label filter
    if label:
        query_parts.append(f"label:{label}")

    # Add user query (keywords)
    if user_query and user_query.strip():
        query_parts.append(user_query.strip())

    # Combine all parts with space (implicit AND)
    gmail_query = " ".join(query_parts)

    return gmail_query if gmail_query else "*"


def parse_relative_date(date_str: str) -> datetime:
    """
    Parse date string supporting both absolute and relative formats.

    Supported formats:
    - Absolute: YYYY-MM-DD, YYYY/MM/DD
    - Relative: "30 days ago", "last week", "yesterday"

    Args:
        date_str: Date string to parse

    Returns:
        datetime: Parsed date

    Raises:
        ValueError: If date format is not recognized
    """
    date_str = date_str.strip().lower()

    # Handle relative dates
    if "ago" in date_str or "last" in date_str:
        if "day" in date_str:
            # Extract number of days
            try:
                days = int(''.join(filter(str.isdigit, date_str)))
                return datetime.now() - timedelta(days=days)
            except ValueError:
                pass

        if "week" in date_str:
            try:
                weeks = int(''.join(filter(str.isdigit, date_str))) if any(c.isdigit() for c in date_str) else 1
                return datetime.now() - timedelta(weeks=weeks)
            except ValueError:
                pass

        if "month" in date_str:
            try:
                months = int(''.join(filter(str.isdigit, date_str))) if any(c.isdigit() for c in date_str) else 1
                return datetime.now() - timedelta(days=months * 30)
            except ValueError:
                pass

    # Handle "yesterday", "today"
    if date_str == "yesterday":
        return datetime.now() - timedelta(days=1)
    elif date_str == "today":
        return datetime.now()

    # Try parsing as absolute date
    try:
        return date_parser.parse(date_str)
    except Exception:
        raise ValueError(f"Could not parse date: {date_str}")


def search_gmail(
    query: str,
    max_results: int = 100
) -> List[Dict[str, Any]]:
    """
    Search Gmail using query syntax and return message IDs and snippets.

    Args:
        query: Gmail query syntax string
        max_results: Maximum number of results to return

    Returns:
        List[Dict]: List of email summaries with id, threadId, snippet

    Raises:
        Exception: If Gmail API call fails
    """
    try:
        service = get_gmail_service()

        results = []
        page_token = None

        while len(results) < max_results:
            # Calculate how many results to fetch in this iteration
            remaining = max_results - len(results)
            page_size = min(remaining, 100)  # Gmail API max is 500, but 100 is safer

            # Execute search
            response = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=page_size,
                pageToken=page_token
            ).execute()

            messages = response.get('messages', [])

            if not messages:
                break

            # Fetch snippets for each message
            for msg in messages:
                try:
                    msg_data = service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['From', 'To', 'Subject', 'Date']
                    ).execute()

                    results.append({
                        'id': msg_data['id'],
                        'threadId': msg_data['threadId'],
                        'snippet': msg_data.get('snippet', ''),
                        'internalDate': msg_data.get('internalDate', '')
                    })

                    if len(results) >= max_results:
                        break
                except Exception as e:
                    print(f"Warning: Could not fetch message {msg['id']}: {e}")

            # Check for more pages
            page_token = response.get('nextPageToken')
            if not page_token:
                break

        return results

    except HttpError as error:
        raise Exception(f"Gmail API error: {error}")
    except Exception as e:
        raise Exception(f"Search failed: {e}")


def fetch_email_details(email_id: str) -> Dict[str, Any]:
    """
    Fetch full details of an email by ID.

    Extracts:
    - Headers: From, To, Subject, Date
    - Body: Plain text and HTML content
    - Labels
    - Attachments info

    Args:
        email_id: Gmail message ID

    Returns:
        Dict: Complete email details

    Raises:
        Exception: If Gmail API call fails
    """
    try:
        service = get_gmail_service()

        message = service.users().messages().get(
            userId='me',
            id=email_id,
            format='full'
        ).execute()

        # Extract headers
        headers = {}
        for header in message['payload'].get('headers', []):
            name = header['name']
            if name in ['From', 'To', 'Subject', 'Date', 'Cc', 'Bcc']:
                headers[name] = header['value']

        # Extract body
        body = extract_body(message['payload'])

        # Extract labels
        labels = message.get('labelIds', [])

        # Check for attachments
        has_attachments = has_attachment_check(message['payload'])

        # Parse date
        date_str = headers.get('Date', '')
        try:
            parsed_date = date_parser.parse(date_str) if date_str else None
            formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S') if parsed_date else date_str
        except Exception:
            formatted_date = date_str

        return {
            'id': message['id'],
            'threadId': message['threadId'],
            'from': headers.get('From', ''),
            'to': headers.get('To', ''),
            'subject': headers.get('Subject', ''),
            'date': formatted_date,
            'snippet': message.get('snippet', ''),
            'body': body,
            'labels': labels,
            'has_attachments': has_attachments,
            'internal_date': message.get('internalDate', '')
        }

    except HttpError as error:
        raise Exception(f"Gmail API error: {error}")
    except Exception as e:
        raise Exception(f"Failed to fetch email details: {e}")


def extract_body(payload: Dict) -> str:
    """
    Extract email body from payload (handles multipart messages).

    Args:
        payload: Gmail message payload

    Returns:
        str: Email body text
    """
    body = ""

    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    import base64
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    break
            elif part['mimeType'] == 'text/html' and not body:
                if 'data' in part['body']:
                    import base64
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
            elif 'parts' in part:
                body = extract_body(part)
                if body:
                    break
    else:
        if 'body' in payload and 'data' in payload['body']:
            import base64
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')

    return body


def has_attachment_check(payload: Dict) -> bool:
    """
    Check if email has attachments.

    Args:
        payload: Gmail message payload

    Returns:
        bool: True if email has attachments
    """
    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('filename'):
                return True
            if 'parts' in part:
                if has_attachment_check(part):
                    return True
    return False


# FunctionDeclaration for gmail_search
gmail_search = FunctionDeclaration(
    name="gmail_search",
    description=(
        "Search Gmail using natural language query and filters. "
        "Converts natural language to Gmail query syntax and returns matching emails. "
        "Use this tool to find emails based on sender, date range, keywords, attachments, or labels. "
        "Returns basic email information (ID, snippet, date) for matching messages."
    ),
    parameters={
        "type": "object",
        "properties": {
            "user_query": {
                "type": "string",
                "description": "Natural language search query (keywords to search for in emails)"
            },
            "sender": {
                "type": "string",
                "description": "Filter by sender email address (optional)"
            },
            "after_date": {
                "type": "string",
                "description": "Filter emails after this date. Supports YYYY-MM-DD format or relative dates like '30 days ago', 'last week' (optional)"
            },
            "before_date": {
                "type": "string",
                "description": "Filter emails before this date. Supports YYYY-MM-DD format or relative dates (optional)"
            },
            "has_attachment": {
                "type": "boolean",
                "description": "Filter for emails with attachments (optional)"
            },
            "label": {
                "type": "string",
                "description": "Filter by Gmail label (inbox, sent, important, etc.) (optional)"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 100)"
            }
        },
        "required": ["user_query"]
    }
)


# Python function implementation for gmail_search
def gmail_search_impl(
    user_query: str,
    sender: Optional[str] = None,
    after_date: Optional[str] = None,
    before_date: Optional[str] = None,
    has_attachment: Optional[bool] = None,
    label: Optional[str] = None,
    max_results: int = 100
) -> Dict[str, Any]:
    """
    Implementation of gmail_search FunctionTool.

    Args:
        user_query: Natural language search query
        sender: Filter by sender email
        after_date: Filter emails after date
        before_date: Filter emails before date
        has_attachment: Filter for attachments
        label: Filter by label
        max_results: Max results to return

    Returns:
        Dict with search results and query used
    """
    try:
        # Convert to Gmail query syntax
        gmail_query = convert_natural_language_to_gmail_query(
            user_query=user_query,
            sender=sender,
            after_date=after_date,
            before_date=before_date,
            has_attachment=has_attachment,
            label=label
        )

        # Execute search
        results = search_gmail(gmail_query, max_results)

        return {
            'success': True,
            'query': gmail_query,
            'count': len(results),
            'results': results
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'query': '',
            'count': 0,
            'results': []
        }


# FunctionDeclaration for email_fetcher
email_fetcher = FunctionDeclaration(
    name="email_fetcher",
    description=(
        "Fetch complete details of a specific email by ID. "
        "Returns full email content including headers (From, To, Subject, Date), "
        "body text, labels, and attachment information. "
        "Use this after gmail_search to get full details of specific emails."
    ),
    parameters={
        "type": "object",
        "properties": {
            "email_id": {
                "type": "string",
                "description": "Gmail message ID to fetch (obtained from gmail_search results)"
            }
        },
        "required": ["email_id"]
    }
)


# Python function implementation for email_fetcher
def email_fetcher_impl(email_id: str) -> Dict[str, Any]:
    """
    Implementation of email_fetcher FunctionTool.

    Args:
        email_id: Gmail message ID

    Returns:
        Dict with email details or error
    """
    try:
        email_details = fetch_email_details(email_id)
        email_details['success'] = True
        return email_details
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'id': email_id
        }
