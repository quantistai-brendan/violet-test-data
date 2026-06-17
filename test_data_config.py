"""
Violet Test Data Configuration
================================
All test data defined here. Edit this file to change clients, accounts, emails,
or calendar events. The automation scripts read from this config.

To add a new test run: duplicate and modify this file, then pass it to the scripts.
"""

from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# M365 Test Accounts
# ---------------------------------------------------------------------------
M365_ACCOUNTS = [
    {
        "first_name": "Sarah",
        "last_name": "Chen",
        "username": "sarah.chen",        # @domain appended automatically
        "display_name": "Sarah Chen",
        "job_title": "Account Manager",
        "license_sku": "O365_BUSINESS_ESSENTIALS",  # M365 Business Basic SKU
    },
    {
        "first_name": "James",
        "last_name": "Walker",
        "username": "james.walker",
        "display_name": "James Walker",
        "job_title": "Account Manager",
        "license_sku": "O365_BUSINESS_ESSENTIALS",
    },
]

# ---------------------------------------------------------------------------
# Clients (shared across Xero, Monday, Outlook)
# ---------------------------------------------------------------------------
CLIENTS = [
    {
        "name": "Hargreaves & Partners Ltd",
        "status": "Healthy",
        "gmail": "hargreaves.partners.test@quantistai.com",
        "assigned_to": "sarah.chen",   # internal M365 username prefix
    },
    {
        "name": "Meridian Consulting Solutions",
        "status": "Healthy",
        "gmail": "hargreaves.partners.test@quantistai.com",   # shared Gmail (2 clients per account)
        "assigned_to": "james.walker",
    },
    {
        "name": "Wentworth Solutions Ltd",
        "status": "Critical",
        "gmail": "wentworth.solutions.test@quantistai.com",
        "assigned_to": "james.walker",
    },
    {
        "name": "Thornbury Creative Agency",
        "status": "At Risk",
        "gmail": "thornbury.creative.test@quantistai.com",
        "assigned_to": "sarah.chen",
    },
    {
        "name": "Pinnacle Property Management",
        "status": "At Risk",
        "gmail": "wentworth.solutions.test@quantistai.com",
        "assigned_to": "james.walker",
    },
    {
        "name": "Blackwood Digital Ltd",
        "status": "Dormant",
        "gmail": "thornbury.creative.test@quantistai.com",
        "assigned_to": "sarah.chen",
    },
]

# ---------------------------------------------------------------------------
# Outbound emails: internal Outlook → Gmail (simulates team contacting clients)
# from_username: M365 username prefix (no @domain)
# to_gmail: destination Gmail address
# subject: email subject
# body: plain text body (keep brief — this is test data)
# ---------------------------------------------------------------------------
OUTBOUND_EMAILS = [
    # --- Sarah Chen: Hargreaves & Partners (healthy, frequent contact) ---
    {
        "from_username": "sarah.chen",
        "to_gmail": "hargreaves.partners.test@quantistai.com",
        "subject": "Hargreaves & Partners Ltd — Website Redesign proposal",
        "body": "Hi, please find attached our proposal for the website redesign project. Looking forward to your feedback.",
    },
    {
        "from_username": "sarah.chen",
        "to_gmail": "hargreaves.partners.test@quantistai.com",
        "subject": "Re: Hargreaves & Partners Ltd — Homepage wireframe feedback",
        "body": "Thanks for the feedback — we'll incorporate the amendments in the next revision.",
    },
    {
        "from_username": "sarah.chen",
        "to_gmail": "hargreaves.partners.test@quantistai.com",
        "subject": "Re: Hargreaves & Partners Ltd — Brand colour refinements",
        "body": "Great — confirmed. We'll proceed with the approved colour palette.",
    },
    {
        "from_username": "sarah.chen",
        "to_gmail": "hargreaves.partners.test@quantistai.com",
        "subject": "Re: Hargreaves & Partners Ltd — Project kickoff notes",
        "body": "Notes from today's kickoff attached. Next steps as discussed.",
    },
    # --- Sarah Chen: Thornbury Creative Agency (at risk, scope creep) ---
    {
        "from_username": "sarah.chen",
        "to_gmail": "thornbury.creative.test@quantistai.com",
        "subject": "Thornbury Creative Agency — Brand Refresh kickoff",
        "body": "Welcome to the project. Please find the kickoff notes and initial timeline attached.",
    },
    {
        "from_username": "sarah.chen",
        "to_gmail": "thornbury.creative.test@quantistai.com",
        "subject": "Re: Thornbury Creative Agency — Logo concepts round 2",
        "body": "Round 2 concepts attached — let us know which direction you'd like to take forward.",
    },
    {
        "from_username": "sarah.chen",
        "to_gmail": "thornbury.creative.test@quantistai.com",
        "subject": "Re: Thornbury Creative Agency — Brand guidelines update",
        "body": "Brand guidelines updated with your feedback. Please review and confirm.",
    },
    {
        "from_username": "sarah.chen",
        "to_gmail": "thornbury.creative.test@quantistai.com",
        "subject": "Thornbury Creative Agency — Scope change request: social media templates",
        "body": "I wanted to flag that the social media template request is outside the original scope. Happy to discuss options.",
    },
    # --- Sarah Chen: Blackwood Digital (dormant, project complete) ---
    {
        "from_username": "sarah.chen",
        "to_gmail": "thornbury.creative.test@quantistai.com",
        "subject": "Blackwood Digital Ltd — Annual Report first draft",
        "body": "Please find the first draft of the annual report attached for your review.",
    },
    {
        "from_username": "sarah.chen",
        "to_gmail": "thornbury.creative.test@quantistai.com",
        "subject": "Re: Blackwood Digital Ltd — Print proofs approved",
        "body": "Confirmed — sending to print today. Great working with you on this.",
    },
    {
        "from_username": "sarah.chen",
        "to_gmail": "thornbury.creative.test@quantistai.com",
        "subject": "Re: Blackwood Digital Ltd — Final sign-off confirmed",
        "body": "Wonderful — project now complete. It's been a pleasure. We'll be in touch for future projects.",
    },
    # --- James Walker: Meridian Consulting (healthy) ---
    {
        "from_username": "james.walker",
        "to_gmail": "hargreaves.partners.test@quantistai.com",
        "subject": "Meridian Consulting Solutions — Audit engagement letter",
        "body": "Please find the audit engagement letter attached. Kindly sign and return at your earliest convenience.",
    },
    {
        "from_username": "james.walker",
        "to_gmail": "hargreaves.partners.test@quantistai.com",
        "subject": "Re: Meridian Consulting Solutions — Q3 audit document checklist",
        "body": "Checklist received — we're working through the items. Will revert by end of week.",
    },
    {
        "from_username": "james.walker",
        "to_gmail": "hargreaves.partners.test@quantistai.com",
        "subject": "Re: Meridian Consulting Solutions — Revenue recognition queries",
        "body": "Happy to schedule a call — availability sent separately.",
    },
    # --- James Walker: Wentworth Solutions (critical — gap required) ---
    {
        "from_username": "james.walker",
        "to_gmail": "wentworth.solutions.test@quantistai.com",
        "subject": "Wentworth Solutions Ltd — Project Nexus kickoff",
        "body": "Kickoff notes from today attached. Timeline and milestones as discussed.",
    },
    {
        "from_username": "james.walker",
        "to_gmail": "wentworth.solutions.test@quantistai.com",
        "subject": "Re: Wentworth Solutions Ltd — Migration timeline concerns",
        "body": "Understood — we're reviewing the timeline and will come back with a revised plan.",
    },
    {
        "from_username": "james.walker",
        "to_gmail": "wentworth.solutions.test@quantistai.com",
        "subject": "Re: Wentworth Solutions Ltd — UAT delay notification",
        "body": "Noted. We'll adjust the UAT schedule accordingly and communicate to the wider team.",
    },
    {
        "from_username": "james.walker",
        "to_gmail": "wentworth.solutions.test@quantistai.com",
        "subject": "Re: Wentworth Solutions Ltd — Project Nexus API access still pending",
        "body": "Chasing IT for the API access — will escalate if no response by end of day.",
        # NOTE: This is the LAST email for Wentworth. No further contact = 3-week gap.
    },
    # --- James Walker: Pinnacle Property Management (at risk — gap required) ---
    {
        "from_username": "james.walker",
        "to_gmail": "wentworth.solutions.test@quantistai.com",
        "subject": "Pinnacle Property Management — Portfolio Review proposal",
        "body": "Please find our portfolio review proposal attached. Happy to discuss further.",
    },
    {
        "from_username": "james.walker",
        "to_gmail": "wentworth.solutions.test@quantistai.com",
        "subject": "Re: Pinnacle Property Management — Additional site visit required",
        "body": "Understood — we'll arrange the additional site visit. Dates to follow.",
    },
    {
        "from_username": "james.walker",
        "to_gmail": "wentworth.solutions.test@quantistai.com",
        "subject": "Re: Pinnacle Property Management — Valuation report timeline",
        "body": "We're on track for the agreed timeline. Will share a draft by end of month.",
        # NOTE: This is the LAST email for Pinnacle. No further contact = 4-week gap.
    },
]

# ---------------------------------------------------------------------------
# Inbound emails: Gmail → Outlook (simulates clients contacting the team)
# These are sent FROM the Gmail test accounts TO the M365 test accounts.
# The script will use SMTP with Gmail app passwords to send these.
# ---------------------------------------------------------------------------
INBOUND_EMAILS = [
    # Hargreaves → Sarah
    {
        "from_gmail": "hargreaves.partners.test@quantistai.com",
        "to_username": "sarah.chen",
        "subject": "Re: Homepage wireframe — looks great, a few amends attached",
        "body": "Hi Sarah, thanks for the wireframe — it looks great. A few minor amends attached.",
    },
    {
        "from_gmail": "hargreaves.partners.test@quantistai.com",
        "to_username": "sarah.chen",
        "subject": "Re: Brand colour refinements — approved, go ahead",
        "body": "Hi Sarah, approved — please go ahead with the colour palette as discussed.",
    },
    # Meridian → James
    {
        "from_gmail": "hargreaves.partners.test@quantistai.com",
        "to_username": "james.walker",
        "subject": "Re: Q3 audit — documents uploaded to shared folder",
        "body": "Hi James, documents uploaded to the shared folder as requested.",
    },
    {
        "from_gmail": "hargreaves.partners.test@quantistai.com",
        "to_username": "james.walker",
        "subject": "Re: Revenue recognition — can we schedule a call?",
        "body": "Hi James, happy to schedule a call — what works for you this week?",
    },
    # Wentworth → James (ONLY ONE — creates the gap)
    {
        "from_gmail": "wentworth.solutions.test@quantistai.com",
        "to_username": "james.walker",
        "subject": "Re: Project Nexus — API access request submitted to IT",
        "body": "Hi James, just to confirm the API access request has been submitted to our IT team.",
    },
    # Thornbury → Sarah
    {
        "from_gmail": "thornbury.creative.test@quantistai.com",
        "to_username": "sarah.chen",
        "subject": "Re: Brand refresh — can we add social media templates to the scope?",
        "body": "Hi Sarah, we'd love to add social media templates — can we discuss the cost?",
    },
    {
        "from_gmail": "thornbury.creative.test@quantistai.com",
        "to_username": "sarah.chen",
        "subject": "Re: Logo concepts — love option 3, let's proceed",
        "body": "Hi Sarah, option 3 is the one — please proceed.",
    },
    # Blackwood → Sarah (ONLY ONE, old — 2-month gap)
    {
        "from_gmail": "thornbury.creative.test@quantistai.com",
        "to_username": "sarah.chen",
        "subject": "Re: Annual report — sign-off confirmed, great work",
        "body": "Hi Sarah, happy to confirm sign-off. Great work on the report — we're very pleased.",
    },
    # No inbound from Pinnacle at all — complete silence
]

# ---------------------------------------------------------------------------
# Calendar events
# All times are in ISO 8601 format. Use helper below for relative dates.
# ---------------------------------------------------------------------------
def _future(days: int, hour: int, minute: int = 0) -> dict:
    """Returns start/end dict for an event N days from today."""
    now = datetime.utcnow()
    start = (now + timedelta(days=days)).replace(hour=hour, minute=minute, second=0, microsecond=0)
    end = start + timedelta(hours=1)
    return {
        "start": start.isoformat() + "Z",
        "end": end.isoformat() + "Z",
    }

def _past(days: int, hour: int, minute: int = 0) -> dict:
    """Returns start/end dict for an event N days in the past."""
    now = datetime.utcnow()
    start = (now - timedelta(days=days)).replace(hour=hour, minute=minute, second=0, microsecond=0)
    end = start + timedelta(hours=1)
    return {
        "start": start.isoformat() + "Z",
        "end": end.isoformat() + "Z",
    }

CALENDAR_EVENTS = [
    # --- Sarah Chen ---
    {
        "username": "sarah.chen",
        "subject": "Hargreaves & Partners Ltd — Design review",
        "body": "Monthly design review with Hargreaves & Partners.",
        **_future(days=7, hour=10),
    },
    {
        "username": "sarah.chen",
        "subject": "Thornbury Creative Agency — Brand guidelines sign-off",
        "body": "Final brand guidelines sign-off meeting.",
        **_future(days=9, hour=14),
    },
    {
        "username": "sarah.chen",
        "subject": "Thornbury Creative Agency — Scope change discussion",
        "body": "Discussion re: social media templates scope addition.",
        **_future(days=10, hour=11),
    },
    {
        "username": "sarah.chen",
        "subject": "Team standup",
        "body": "Daily team standup.",
        **_future(days=1, hour=9, minute=15),
    },
    {
        "username": "sarah.chen",
        "subject": "Quarterly portfolio review — all clients",
        "body": "Quarterly review of all active client portfolios.",
        **_future(days=21, hour=14),
    },
    # --- James Walker ---
    {
        "username": "james.walker",
        "subject": "Meridian Consulting Solutions — Audit progress call",
        "body": "Q3 audit progress review call with Meridian.",
        **_future(days=8, hour=11),
    },
    {
        "username": "james.walker",
        "subject": "Wentworth Solutions Ltd — Project Nexus escalation",
        "body": "Escalation call re: Project Nexus delays. NOTE: No follow-up email sent after this.",
        **_past(days=7, hour=15),   # Last week — no follow-up = Violet alert
    },
    {
        "username": "james.walker",
        "subject": "Pinnacle Property Management — Portfolio review catch-up",
        "body": "Catch-up on portfolio review progress. NOTE: No follow-up email sent after this.",
        **_past(days=14, hour=10),  # 2 weeks ago — no follow-up = Violet alert
    },
    {
        "username": "james.walker",
        "subject": "Team standup",
        "body": "Daily team standup.",
        **_future(days=1, hour=9, minute=15),
    },
    {
        "username": "james.walker",
        "subject": "New business — pipeline review",
        "body": "Weekly pipeline review.",
        **_future(days=6, hour=16),
    },
]

# ---------------------------------------------------------------------------
# Xero contact → Gmail mapping (for updating Xero contact emails)
# ---------------------------------------------------------------------------
XERO_CONTACT_EMAIL_MAP = {
    "Hargreaves & Partners Ltd":       "hargreaves.partners.test@quantistai.com",
    "Meridian Consulting Solutions":   "hargreaves.partners.test@quantistai.com",
    "Wentworth Solutions Ltd":         "wentworth.solutions.test@quantistai.com",
    "Pinnacle Property Management":    "wentworth.solutions.test@quantistai.com",
    "Thornbury Creative Agency":       "thornbury.creative.test@quantistai.com",
    "Blackwood Digital Ltd":           "thornbury.creative.test@quantistai.com",
}
