#!/usr/bin/env python3
"""
Gmail Filter Agent - Main Application

An intelligent agent built with Google's Agent Development Kit (ADK) that helps
users filter and analyze their Gmail emails using natural language queries.

Features:
- Natural language email filtering
- Currency amount extraction
- CSV export of filtered emails
- OAuth 2.0 Gmail integration

Usage:
    python agent.py

    Or build as executable:
    python build.py
    ./dist/gmail-filter-agent
"""

import os
import sys
from typing import Dict, Any

# Add tools directory to path
if getattr(sys, 'frozen', False):
    PROJECT_DIR = os.path.dirname(sys.executable)
else:
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, PROJECT_DIR)

# Import ADK components
try:
    from google import genai
    from google.genai import types
except ImportError as e:
    print(f"ERROR: Failed to import Google ADK. Please install dependencies:")
    print(f"  pip install -r requirements.txt")
    print(f"\nError details: {e}")
    sys.exit(1)

# Import tools
try:
    from tools.gmail_tools import (
        gmail_search,
        email_fetcher,
        gmail_search_impl,
        email_fetcher_impl
    )
    from tools.parser_tools import (
        amount_extractor,
        amount_extractor_impl,
        filter_emails_by_amount
    )
    from tools.export_tools import (
        csv_export,
        csv_export_impl
    )
except ImportError as e:
    print(f"ERROR: Failed to import tools. Ensure tools/ directory exists.")
    print(f"Error details: {e}")
    sys.exit(1)


# Agent configuration
AGENT_MODEL = "gemini-2.0-flash-001"

AGENT_INSTRUCTION = """You are an intelligent Gmail Filter Agent that helps users find, analyze, and export emails from their Gmail account.

Your capabilities:
1. **Email Search**: Use gmail_search to find emails based on natural language queries. You can filter by:
   - Keywords (search in subject, body, from, to)
   - Sender email address
   - Date ranges (absolute dates like "2024-01-01" or relative like "last 30 days")
   - Attachments (has_attachment: true/false)
   - Labels (inbox, sent, important, etc.)

2. **Email Details**: Use email_fetcher to get full details of specific emails including:
   - Complete headers (From, To, Subject, Date)
   - Full body content
   - Labels and attachments info

3. **Amount Extraction**: Use amount_extractor to find and filter emails containing currency amounts:
   - Supports multiple currencies ($, €, £, ¥, USD, EUR, GBP, JPY)
   - Can filter by min/max amount
   - Extracts from subject, body, and snippet

4. **CSV Export**: Use csv_export to export filtered emails to CSV format:
   - Auto-generates timestamped filename
   - Saves to csv_files/ directory
   - Includes all email metadata and detected amounts

**Workflow for user requests:**

When a user asks to filter emails:
1. Parse their request to identify:
   - Keywords or search terms
   - Sender filters
   - Date range requirements
   - Attachment requirements
   - Amount filters (if they mention money/payments)

2. Use gmail_search with appropriate parameters to find matching emails

3. If they mentioned amounts or payments:
   - Use email_fetcher to get full details of found emails
   - Use amount_extractor to extract amounts
   - Filter emails by amount range if specified

4. **ALWAYS export results to CSV by default** using csv_export unless user explicitly says not to

5. Provide a summary to the user:
   - How many emails found
   - Date range of results
   - CSV file location
   - Key insights (top senders, amount ranges, etc.)

**Examples:**

User: "Find emails from john@example.com from last month"
You should:
- Use gmail_search with sender="john@example.com", after_date="last month"
- Export results to CSV
- Tell user how many emails found and CSV location

User: "Show me payment receipts over $100 from last week"
You should:
- Use gmail_search with user_query="payment receipt", after_date="last week"
- Use email_fetcher to get full email details
- Use amount_extractor with min_amount=100 to filter by amount
- Export filtered results to CSV
- Tell user how many emails matched and CSV location

User: "Find emails with attachments about project proposal"
You should:
- Use gmail_search with user_query="project proposal", has_attachment=true
- Export results to CSV
- Tell user how many emails found and CSV location

**Important guidelines:**
- Always be helpful and explain what you're doing
- Handle errors gracefully and provide clear error messages
- Default to exporting results to CSV (users want to see the data)
- Provide actionable summaries with specific numbers
- If no emails match, explain why and suggest alternatives
- Be conversational but concise

Remember: Your goal is to make email filtering effortless for users. Be proactive, export results by default, and provide clear summaries."""


def create_agent():
    """
    Create and configure the Gmail Filter Agent.

    Returns:
        LlmAgent: Configured ADK agent instance
    """
    # Configure API client
    client = genai.Client()

    # Create agent with tools
    agent = client.agentic.create_agent(
        model=AGENT_MODEL,
        tools=[gmail_search, email_fetcher, amount_extractor, csv_export],
        system_instruction=AGENT_INSTRUCTION
    )

    return agent


def handle_tool_call(tool_name: str, tool_args: Dict[str, Any]) -> Any:
    """
    Handle tool function calls and return results.

    Maps FunctionDeclarations to their Python implementations.

    Args:
        tool_name: Name of the tool to call
        tool_args: Arguments for the tool

    Returns:
        Tool execution result
    """
    tool_implementations = {
        'gmail_search': gmail_search_impl,
        'email_fetcher': email_fetcher_impl,
        'amount_extractor': amount_extractor_impl,
        'csv_export': csv_export_impl
    }

    if tool_name in tool_implementations:
        try:
            result = tool_implementations[tool_name](**tool_args)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': f"Tool execution failed: {str(e)}"
            }
    else:
        return {
            'success': False,
            'error': f"Unknown tool: {tool_name}"
        }


def run_agent_interactive():
    """
    Run the agent in interactive mode (command-line chat).
    """
    print("=" * 70)
    print("Gmail Filter Agent")
    print("=" * 70)
    print("\nWelcome! I can help you filter and analyze your Gmail emails.")
    print("\nExamples:")
    print("  - Find emails from sender@example.com from last month")
    print("  - Show me payment receipts over $100")
    print("  - Find emails with attachments about project proposal")
    print("\nType 'quit' or 'exit' to stop.\n")

    try:
        agent = create_agent()
    except Exception as e:
        print(f"\nERROR: Failed to create agent: {e}")
        return

    # Chat loop
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\nGoodbye!")
                break

            # Send message to agent
            print("\nAgent: ", end="", flush=True)

            # Generate response
            response = agent.generate_content(user_input)

            # Handle tool calls if needed
            if hasattr(response, 'function_calls') and response.function_calls:
                for function_call in response.function_calls:
                    tool_name = function_call.name
                    tool_args = function_call.args

                    print(f"[Calling {tool_name}...]", end=" ", flush=True)

                    # Execute tool
                    result = handle_tool_call(tool_name, tool_args)

                    # Send result back to agent
                    response = agent.generate_content(
                        types.Content(
                            parts=[types.Part.from_function_response(
                                name=tool_name,
                                response=result
                            )]
                        )
                    )

            # Display response
            print(response.text)

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.")


def main():
    """
    Main entry point for the application.
    """
    # Check for credentials
    credentials_path = os.path.join(PROJECT_DIR, 'credentials.json')

    if not os.path.exists(credentials_path):
        print("\n" + "=" * 70)
        print("SETUP REQUIRED: Gmail API Credentials Missing")
        print("=" * 70)
        print("\nBefore using the Gmail Filter Agent, you need to set up Gmail API credentials.")
        print("\nSteps:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Gmail API for your project")
        print("4. Create OAuth 2.0 credentials (Application type: Desktop app)")
        print("5. Download the credentials file")
        print(f"6. Save it as: {credentials_path}")
        print("\nFor detailed instructions, see USER_INSTRUCTIONS.txt")
        print("\nOnce you have credentials.json in place, run this program again.")
        print("=" * 70 + "\n")
        return

    # Run interactive agent
    run_agent_interactive()


if __name__ == '__main__':
    main()
