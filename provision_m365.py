"""
Violet Test Data Automation — Microsoft 365 Provisioning
=========================================================
Automates Steps 1, 3, 4, and 5 from the Outlook Setup document:
  - Creates M365 test user accounts
  - Sends outbound emails (Outlook → Gmail) via Graph API
  - Creates calendar events for both test users
  - Sends inbound emails (Gmail → Outlook) via SMTP

NOT automated (requires manual steps):
  - Gmail account creation (Google does not allow programmatic account creation)
  - Xero contact updates (run xero_update.py separately)

Prerequisites:
  pip install msal requests

Azure App Registration required:
  - Register an app in Azure AD (https://portal.azure.com)
  - Grant these Application (not Delegated) permissions:
      User.ReadWrite.All
      Mail.Send
      Mail.ReadWrite
      Calendars.ReadWrite
      Directory.ReadWrite.All
  - Grant admin consent for your tenant
  - Create a client secret and copy the value below

Usage:
  python provision_m365.py

  With flags:
  python provision_m365.py --skip-accounts   (skip user creation, accounts exist)
  python provision_m365.py --skip-emails     (skip email creation)
  python provision_m365.py --skip-calendar   (skip calendar event creation)
  python provision_m365.py --dry-run         (print what would happen, no API calls)
"""

import argparse
import json
import logging
import secrets
import string
import sys
import time
from typing import Optional

import requests

# ---------------------------------------------------------------------------
# Configuration — fill these in before running
# ---------------------------------------------------------------------------
TENANT_ID     = "YOUR_TENANT_ID"          # Azure AD tenant ID (GUID)
CLIENT_ID     = "YOUR_CLIENT_ID"          # App registration client ID
CLIENT_SECRET = "YOUR_CLIENT_SECRET"      # App registration client secret
DOMAIN        = "quantistai.com"          # M365 domain (must match your tenant)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Import test data config
# ---------------------------------------------------------------------------
sys.path.insert(0, ".")
from test_data_config import (
    M365_ACCOUNTS,
    OUTBOUND_EMAILS,
    INBOUND_EMAILS,
    CALENDAR_EVENTS,
)

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
_token_cache: dict = {}

def get_access_token() -> str:
    """Fetch OAuth2 token using client credentials flow."""
    if _token_cache.get("token") and time.time() < _token_cache.get("expires_at", 0) - 60:
        return _token_cache["token"]

    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "grant_type":    "client_credentials",
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope":         "https://graph.microsoft.com/.default",
    }
    resp = requests.post(url, data=data, timeout=30)
    resp.raise_for_status()
    result = resp.json()
    _token_cache["token"] = result["access_token"]
    _token_cache["expires_at"] = time.time() + result["expires_in"]
    return _token_cache["token"]


def graph(method: str, path: str, payload: Optional[dict] = None, dry_run: bool = False):
    """Make a Microsoft Graph API call. Returns parsed JSON or None on dry run."""
    url = f"https://graph.microsoft.com/v1.0{path}"
    if dry_run:
        log.info("[DRY RUN] %s %s %s", method.upper(), url,
                 json.dumps(payload, indent=2) if payload else "")
        return {"id": "dry-run-id", "userPrincipalName": "dry-run@example.com"}

    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
    }
    resp = requests.request(method, url, headers=headers,
                            json=payload, timeout=30)
    if not resp.ok:
        log.error("Graph API error: %s %s", resp.status_code, resp.text)
        resp.raise_for_status()
    return resp.json() if resp.text else {}


# ---------------------------------------------------------------------------
# Step 1 — Create M365 Accounts
# ---------------------------------------------------------------------------
def generate_password(length: int = 16) -> str:
    """Generate a strong random temporary password."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return "".join(secrets.choice(chars) for _ in range(length))


def create_accounts(dry_run: bool = False) -> dict[str, str]:
    """
    Create M365 user accounts. Returns {username_prefix: temp_password} map.
    Skips accounts that already exist.
    """
    log.info("=== Step 1: Creating M365 accounts ===")
    created: dict[str, str] = {}

    # Get existing users to avoid duplicates
    existing_upns: set[str] = set()
    if not dry_run:
        result = graph("GET", "/users?$select=userPrincipalName")
        for user in result.get("value", []):
            existing_upns.add(user["userPrincipalName"].lower())

    for acct in M365_ACCOUNTS:
        upn = f"{acct['username']}@{DOMAIN}"
        if upn.lower() in existing_upns:
            log.info("  SKIP  %s (already exists)", upn)
            created[acct["username"]] = "(existing account — password unknown)"
            continue

        password = generate_password()
        payload = {
            "accountEnabled": True,
            "displayName":    acct["display_name"],
            "givenName":      acct["first_name"],
            "surname":        acct["last_name"],
            "jobTitle":       acct.get("job_title", ""),
            "userPrincipalName": upn,
            "mailNickname":   acct["username"].replace(".", ""),
            "passwordProfile": {
                "forceChangePasswordNextSignIn": True,
                "password": password,
            },
            "usageLocation": "GB",   # Required for licence assignment
        }
        result = graph("POST", "/users", payload, dry_run=dry_run)
        log.info("  CREATED  %s", upn)

        # Assign licence
        # Note: SKU IDs vary by tenant. Run get_sku_ids.py to find yours.
        # Common M365 Business Basic SKU: 3b555118-da6a-4418-894f-7df1e2096870
        # Uncomment and populate after confirming your SKU ID:
        # assign_licence(result["id"], acct["license_sku"], dry_run)

        created[acct["username"]] = password

    return created


def assign_licence(user_id: str, sku_friendly_name: str, dry_run: bool = False):
    """Assign an M365 licence to a user. SKU ID must be resolved first."""
    # This is left as a stub — SKU IDs are tenant-specific.
    # Run: GET /subscribedSkus to list available SKUs in your tenant.
    log.info("  (Licence assignment for %s — populate SKU ID to enable)", user_id)


# ---------------------------------------------------------------------------
# Step 3 & 4 — Send Emails (Outbound: Outlook → Gmail)
# ---------------------------------------------------------------------------
def send_outbound_emails(dry_run: bool = False):
    """
    Send outbound emails from M365 test accounts to Gmail addresses.
    Uses Graph API sendMail endpoint (no SMTP credentials needed).
    """
    log.info("=== Steps 3&4: Sending outbound emails ===")
    for i, email in enumerate(OUTBOUND_EMAILS, 1):
        upn = f"{email['from_username']}@{DOMAIN}"
        payload = {
            "message": {
                "subject": email["subject"],
                "body": {
                    "contentType": "Text",
                    "content":     email["body"],
                },
                "toRecipients": [
                    {"emailAddress": {"address": email["to_gmail"]}}
                ],
            },
            "saveToSentItems": True,
        }
        graph("POST", f"/users/{upn}/sendMail", payload, dry_run=dry_run)
        log.info("  [%d/%d] SENT  %s → %s | %s",
                 i, len(OUTBOUND_EMAILS), upn, email["to_gmail"], email["subject"][:60])
        if not dry_run:
            time.sleep(0.3)   # Polite rate limiting


# ---------------------------------------------------------------------------
# Step 3 — Send Inbound Emails (Gmail → Outlook) via Graph API injection
# ---------------------------------------------------------------------------
def inject_inbound_emails(dry_run: bool = False):
    """
    Inject inbound emails into M365 inboxes using Graph API message creation.
    This creates the email directly in the inbox (appearing as received),
    without needing Gmail SMTP credentials.

    The 'from' address is set to the Gmail address so Violet's domain-matching
    logic works correctly.
    """
    log.info("=== Step 3: Injecting inbound emails (Gmail → Outlook) ===")
    for i, email in enumerate(INBOUND_EMAILS, 1):
        upn = f"{email['to_username']}@{DOMAIN}"

        # Create message in inbox directly (received simulation)
        payload = {
            "subject": email["subject"],
            "body": {
                "contentType": "Text",
                "content":     email["body"],
            },
            "from": {
                "emailAddress": {
                    "address": email["from_gmail"],
                    "name":    email["from_gmail"].split("@")[0].replace(".", " ").title(),
                }
            },
            "toRecipients": [
                {"emailAddress": {"address": upn}}
            ],
            "isRead": True,
        }
        result = graph("POST", f"/users/{upn}/messages", payload, dry_run=dry_run)

        # Move to Inbox (messages created via API land in Drafts by default)
        if not dry_run and result.get("id"):
            graph("POST", f"/users/{upn}/messages/{result['id']}/move",
                  {"destinationId": "inbox"}, dry_run=False)

        log.info("  [%d/%d] INJECTED  %s → %s | %s",
                 i, len(INBOUND_EMAILS), email["from_gmail"], upn, email["subject"][:60])
        if not dry_run:
            time.sleep(0.3)


# ---------------------------------------------------------------------------
# Step 5 — Create Calendar Events
# ---------------------------------------------------------------------------
def create_calendar_events(dry_run: bool = False):
    """Create calendar events for each test user."""
    log.info("=== Step 5: Creating calendar events ===")
    for i, event in enumerate(CALENDAR_EVENTS, 1):
        upn = f"{event['username']}@{DOMAIN}"
        payload = {
            "subject": event["subject"],
            "body": {
                "contentType": "Text",
                "content":     event["body"],
            },
            "start": {
                "dateTime": event["start"],
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": event["end"],
                "timeZone": "UTC",
            },
            "isOnlineMeeting": False,
        }
        graph("POST", f"/users/{upn}/events", payload, dry_run=dry_run)
        log.info("  [%d/%d] CREATED  %s | %s | %s",
                 i, len(CALENDAR_EVENTS), upn, event["start"][:16], event["subject"][:60])
        if not dry_run:
            time.sleep(0.3)


# ---------------------------------------------------------------------------
# Teardown (optional — for resetting between test runs)
# ---------------------------------------------------------------------------
def delete_accounts(dry_run: bool = False):
    """
    Delete the test M365 accounts. Use with caution.
    Run with: python provision_m365.py --teardown
    """
    log.warning("=== TEARDOWN: Deleting M365 test accounts ===")
    for acct in M365_ACCOUNTS:
        upn = f"{acct['username']}@{DOMAIN}"
        if dry_run:
            log.info("[DRY RUN] Would delete %s", upn)
            continue
        try:
            graph("DELETE", f"/users/{upn}")
            log.info("  DELETED  %s", upn)
        except Exception as e:
            log.warning("  Could not delete %s: %s", upn, e)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Violet M365 test data provisioner")
    parser.add_argument("--skip-accounts",  action="store_true", help="Skip user account creation")
    parser.add_argument("--skip-emails",    action="store_true", help="Skip email creation")
    parser.add_argument("--skip-calendar",  action="store_true", help="Skip calendar event creation")
    parser.add_argument("--dry-run",        action="store_true", help="Print actions without making API calls")
    parser.add_argument("--teardown",       action="store_true", help="Delete test accounts (use with caution)")
    args = parser.parse_args()

    if args.teardown:
        confirm = input("Type DELETE to confirm teardown: ")
        if confirm != "DELETE":
            print("Aborted.")
            sys.exit(0)
        delete_accounts(dry_run=args.dry_run)
        return

    passwords = {}
    if not args.skip_accounts:
        passwords = create_accounts(dry_run=args.dry_run)

    # Brief pause to let accounts propagate in Azure AD
    if passwords and not args.dry_run:
        log.info("Waiting 15 seconds for account propagation...")
        time.sleep(15)

    if not args.skip_emails:
        send_outbound_emails(dry_run=args.dry_run)
        inject_inbound_emails(dry_run=args.dry_run)

    if not args.skip_calendar:
        create_calendar_events(dry_run=args.dry_run)

    # Print credentials summary
    if passwords:
        log.info("")
        log.info("=== Account Credentials (share via Bitwarden Send — NOT Slack) ===")
        for username, pwd in passwords.items():
            log.info("  %s@%s  →  %s", username, DOMAIN, pwd)
        log.info("")
        log.info("Done. Share credentials via Bitwarden Send before notifying MIS.")


if __name__ == "__main__":
    main()
