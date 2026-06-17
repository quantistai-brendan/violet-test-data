# Violet Test Data Automation

Automates provisioning of Outlook test data for Violet integration development.
Replaces the manual steps in `Brendan_Outlook_Setup.docx`.

---

## What This Automates

| Manual Step | Script | Status |
|---|---|---|
| Create M365 test accounts (Sarah Chen, James Walker) | `provision_m365.py` | ✅ Automated |
| Send outbound emails (Outlook → Gmail) | `provision_m365.py` | ✅ Automated |
| Inject inbound emails (Gmail → Outlook) | `provision_m365.py` | ✅ Automated |
| Create calendar events | `provision_m365.py` | ✅ Automated |
| Update Xero contact emails | `xero_update.py` | ✅ Automated |
| Create Gmail client accounts | *(manual — Google API restriction)* | ❌ Manual (one-time) |
| Licence assignment | `provision_m365.py` (stub) | ⚠️ Needs SKU ID |

---

## One-Time Manual Step: Create Gmail Accounts

Google does not allow programmatic Gmail account creation. Do this once:

1. Go to [accounts.google.com](https://accounts.google.com) and create:
   - `hargreaves.partners.test@gmail.com`
   - `wentworth.solutions.test@gmail.com`
   - `thornbury.creative.test@gmail.com`
2. Use a desktop browser — no phone verification required.
3. Store the passwords in Bitwarden (not Slack/email).

These accounts persist between test runs. You only create them once.

---

## Prerequisites

```bash
pip install msal requests
```

---

## Azure App Registration (one-time)

1. Go to [portal.azure.com](https://portal.azure.com) → Azure Active Directory → App registrations → New registration
2. Name: `Violet Test Data Provisioner`
3. Supported account types: Single tenant
4. No redirect URI needed (client credentials flow)
5. Go to **API permissions** → Add a permission → Microsoft Graph → Application permissions:
   - `User.ReadWrite.All`
   - `Mail.Send`
   - `Mail.ReadWrite`
   - `Calendars.ReadWrite`
   - `Directory.ReadWrite.All`
6. Click **Grant admin consent**
7. Go to **Certificates & secrets** → New client secret → Copy the value

Fill in `provision_m365.py`:
```python
TENANT_ID     = "your-tenant-id"
CLIENT_ID     = "your-client-id"
CLIENT_SECRET = "your-client-secret"
DOMAIN        = "quantistai.com"
```

---

## Xero App Registration (one-time)

1. Go to [developer.xero.com](https://developer.xero.com) → New app
2. Integration type: Web app
3. Redirect URI: `http://localhost:8080/callback`
4. Scope: `accounting.contacts`
5. Copy client ID and secret

Fill in `xero_update.py`:
```python
XERO_CLIENT_ID     = "your-client-id"
XERO_CLIENT_SECRET = "your-client-secret"
```

Authenticate once:
```bash
python xero_update.py --auth
```

---

## Usage

### Full provision (new test environment)

```bash
# Step 1: Create accounts, send all emails, create calendar events
python provision_m365.py

# Step 2: Update Xero contact emails
python xero_update.py
```

### Re-run emails and calendar only (accounts already exist)

```bash
python provision_m365.py --skip-accounts
```

### Dry run (see what would happen, no API calls)

```bash
python provision_m365.py --dry-run
python xero_update.py --dry-run
```

### Teardown (reset between test runs)

```bash
python provision_m365.py --teardown
```

This deletes the M365 accounts. Gmail accounts and Xero contacts persist and do not need to be recreated.

---

## Licence Assignment

M365 Business Basic licence assignment requires your tenant's SKU ID. To find it:

```
GET https://graph.microsoft.com/v1.0/subscribedSkus
```

Look for `skuPartNumber: O365_BUSINESS_ESSENTIALS`. Copy the `skuId` GUID, then uncomment and populate the `assign_licence()` call in `provision_m365.py`.

Cost: ~£4.50/user/month × 2 = ~£9/month. Cancel accounts when MIS completes integration development.

---

## Modifying Test Data

All test data (clients, emails, calendar events) is defined in `test_data_config.py`.

- To add a new client: add to `CLIENTS` and add their emails to `OUTBOUND_EMAILS` / `INBOUND_EMAILS`
- To add a new test account: add to `M365_ACCOUNTS`
- To change email subjects/bodies: edit `OUTBOUND_EMAILS` or `INBOUND_EMAILS`
- To change calendar events: edit `CALENDAR_EVENTS`

The scripts automatically use whatever is in the config — no changes to the scripts needed.

---

## Security Notes

- Never share test account passwords in Slack, Teams, or email
- Use Bitwarden Send for an encrypted, expiring link
- The `.xero_token.json` file contains OAuth tokens — do not commit to Git
- Add `.xero_token.json` to `.gitignore`

---

## Files

| File | Purpose |
|---|---|
| `test_data_config.py` | All test data: clients, accounts, emails, calendar events |
| `provision_m365.py` | M365 account creation, email injection, calendar events |
| `xero_update.py` | Xero contact email updates |
| `README.md` | This file |
