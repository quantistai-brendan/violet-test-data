"""
Violet Test Data Automation — Xero Contact Email Updates
=========================================================
Updates Xero sandbox contacts to use the Gmail test addresses,
enabling Violet's cross-system domain matching.

This must be run AFTER Gmail accounts are created manually.

Prerequisites:
  pip install requests

Xero OAuth2 setup:
  1. Create a Xero app at developer.xero.com
  2. Select OAuth 2.0
  3. Add redirect URI: http://localhost:8080/callback
  4. Copy client ID and secret below
  5. Run: python xero_update.py --auth   (first time only, opens browser)
  6. Token is saved to .xero_token.json for subsequent runs

Usage:
  python xero_update.py          (update contacts)
  python xero_update.py --auth   (re-authenticate)
  python xero_update.py --dry-run
"""

import argparse
import json
import logging
import sys
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
XERO_CLIENT_ID     = "YOUR_XERO_CLIENT_ID"
XERO_CLIENT_SECRET = "YOUR_XERO_CLIENT_SECRET"
XERO_REDIRECT_URI  = "http://localhost:8080/callback"
XERO_SCOPE         = "accounting.contacts"
TOKEN_FILE         = Path(".xero_token.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

sys.path.insert(0, ".")
from test_data_config import XERO_CONTACT_EMAIL_MAP


# ---------------------------------------------------------------------------
# OAuth2 — Token Management
# ---------------------------------------------------------------------------
def save_token(token: dict):
    TOKEN_FILE.write_text(json.dumps(token, indent=2))


def load_token() -> dict:
    if TOKEN_FILE.exists():
        return json.loads(TOKEN_FILE.read_text())
    return {}


def refresh_token(token: dict) -> dict:
    resp = requests.post(
        "https://identity.xero.com/connect/token",
        data={
            "grant_type":    "refresh_token",
            "refresh_token": token["refresh_token"],
            "client_id":     XERO_CLIENT_ID,
            "client_secret": XERO_CLIENT_SECRET,
        },
        timeout=30,
    )
    resp.raise_for_status()
    new_token = resp.json()
    new_token["obtained_at"] = time.time()
    save_token(new_token)
    return new_token


def get_token() -> dict:
    token = load_token()
    if not token:
        log.error("No token found. Run: python xero_update.py --auth")
        sys.exit(1)
    if time.time() > token.get("obtained_at", 0) + token.get("expires_in", 0) - 60:
        log.info("Refreshing Xero token...")
        token = refresh_token(token)
    return token


def authenticate():
    """Open browser for OAuth2 authorisation and capture the callback."""
    params = {
        "response_type": "code",
        "client_id":     XERO_CLIENT_ID,
        "redirect_uri":  XERO_REDIRECT_URI,
        "scope":         XERO_SCOPE,
        "state":         "violet-setup",
    }
    auth_url = "https://login.xero.com/identity/connect/authorize?" + urlencode(params)
    log.info("Opening browser for Xero authorisation...")
    webbrowser.open(auth_url)

    # Capture the callback on a local server
    auth_code = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            auth_code["code"] = qs.get("code", [""])[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorised. You can close this tab.")
            log.info("Authorisation code received.")

        def log_message(self, *args):
            pass  # Suppress server log noise

    server = HTTPServer(("localhost", 8080), Handler)
    server.handle_request()

    # Exchange code for tokens
    resp = requests.post(
        "https://identity.xero.com/connect/token",
        data={
            "grant_type":   "authorization_code",
            "code":         auth_code["code"],
            "redirect_uri": XERO_REDIRECT_URI,
            "client_id":    XERO_CLIENT_ID,
            "client_secret": XERO_CLIENT_SECRET,
        },
        timeout=30,
    )
    resp.raise_for_status()
    token = resp.json()
    token["obtained_at"] = time.time()
    save_token(token)
    log.info("Token saved to %s", TOKEN_FILE)


# ---------------------------------------------------------------------------
# Xero API helpers
# ---------------------------------------------------------------------------
def get_tenant_id(token: dict) -> str:
    """Get the Xero tenant (organisation) ID."""
    resp = requests.get(
        "https://api.xero.com/connections",
        headers={"Authorization": f"Bearer {token['access_token']}"},
        timeout=30,
    )
    resp.raise_for_status()
    connections = resp.json()
    if not connections:
        log.error("No Xero tenants connected. Check your app has access to a Xero org.")
        sys.exit(1)
    tenant = connections[0]
    log.info("Connected to Xero org: %s (%s)", tenant["tenantName"], tenant["tenantId"])
    return tenant["tenantId"]


def get_contacts(token: dict, tenant_id: str) -> list[dict]:
    """Fetch all contacts from Xero."""
    resp = requests.get(
        "https://api.xero.com/api.xro/2.0/Contacts",
        headers={
            "Authorization": f"Bearer {token['access_token']}",
            "Xero-tenant-id": tenant_id,
            "Accept": "application/json",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("Contacts", [])


def update_contact_email(token: dict, tenant_id: str,
                          contact_id: str, contact_name: str,
                          new_email: str, dry_run: bool = False):
    """Update a single Xero contact's email address."""
    if dry_run:
        log.info("[DRY RUN] Would update '%s' → %s", contact_name, new_email)
        return

    payload = {
        "Contacts": [
            {
                "ContactID":    contact_id,
                "EmailAddress": new_email,
            }
        ]
    }
    resp = requests.post(
        "https://api.xero.com/api.xro/2.0/Contacts",
        headers={
            "Authorization":  f"Bearer {token['access_token']}",
            "Xero-tenant-id": tenant_id,
            "Content-Type":   "application/json",
            "Accept":         "application/json",
        },
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    log.info("  UPDATED  '%s'  →  %s", contact_name, new_email)


# ---------------------------------------------------------------------------
# Main update flow
# ---------------------------------------------------------------------------
def update_xero_contacts(dry_run: bool = False):
    token = get_token()
    tenant_id = get_tenant_id(token)

    log.info("=== Fetching Xero contacts ===")
    contacts = get_contacts(token, tenant_id)
    log.info("Found %d contacts in Xero", len(contacts))

    # Build lookup: name → contact_id
    name_to_id = {c["Name"]: c["ContactID"] for c in contacts}

    log.info("=== Updating contact emails ===")
    not_found = []
    for contact_name, gmail_address in XERO_CONTACT_EMAIL_MAP.items():
        if contact_name not in name_to_id:
            log.warning("  NOT FOUND in Xero: '%s'", contact_name)
            not_found.append(contact_name)
            continue
        update_contact_email(
            token, tenant_id,
            name_to_id[contact_name], contact_name,
            gmail_address, dry_run=dry_run,
        )

    if not_found:
        log.warning("")
        log.warning("These contacts were not found in Xero and must be created manually:")
        for name in not_found:
            log.warning("  - %s", name)

    log.info("")
    log.info("Done. Xero contacts updated — Violet domain matching is now configured.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Violet Xero contact email updater")
    parser.add_argument("--auth",    action="store_true", help="Authenticate with Xero (first time)")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without making API calls")
    args = parser.parse_args()

    if args.auth:
        authenticate()
        return

    update_xero_contacts(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
