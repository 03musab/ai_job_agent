"""
JobSnap Launch Email Dispatcher
Supports dry-run preview, test-send to founder, and full batch delivery via Gmail API.
"""

import os
import csv
import sys
import time
import random
import base64
import pickle
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CSV_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "jobsnap_waitlist_contacts.csv"
)

# Brain artifact fallback if not in root
BRAIN_CSV = r"C:\Users\musab\.gemini\antigravity-ide\brain\32f0db5e-5c44-4e45-92bb-fa19d9ec546e\jobsnap_waitlist_contacts.csv"

def get_csv_file():
    if os.path.exists(CSV_PATH):
        return CSV_PATH
    if os.path.exists(BRAIN_CSV):
        return BRAIN_CSV
    raise FileNotFoundError("Could not find jobsnap_waitlist_contacts.csv")

EMAIL_TEMPLATES = {
    "1": {
        "subject": "The job market is not for beginners, {name} (Good news inside)",
        "body_html": """\
<html>
<body style="margin: 0; padding: 24px 12px; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #0f172a; line-height: 1.55;">
    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 520px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <!-- Header -->
        <tr>
            <td style="padding: 28px 32px 20px 32px; border-bottom: 1px solid #f1f5f9;">
                <div style="font-size: 18px; font-weight: 700; letter-spacing: -0.02em; color: #0f172a;">
                    JobSnap <span style="font-size: 11px; font-weight: 600; color: #475569; background: #f1f5f9; padding: 3px 8px; border-radius: 12px; margin-left: 6px; letter-spacing: 0;">EARLY ACCESS</span>
                </div>
            </td>
        </tr>

        <!-- Content -->
        <tr>
            <td style="padding: 28px 32px 32px 32px;">
                <p style="margin: 0 0 16px 0; font-size: 15px;">Hey <strong>{name}</strong>,</p>

                <p style="margin: 0 0 16px 0; font-size: 15px; color: #334155;">
                    The modern job market is genuinely not for beginners.
                </p>

                <p style="margin: 0 0 18px 0; font-size: 14px; color: #475569;">
                    Spending 45 minutes re-typing your resume into yet another Workday portal — only to get left on "seen" like an unreplied Instagram DM — has to stop.
                </p>

                <div style="background-color: #f8fafc; border-left: 3px solid #0f172a; padding: 14px 16px; margin: 0 0 20px 0; border-radius: 0 6px 6px 0;">
                    <p style="margin: 0; font-size: 14px; font-weight: 600; color: #0f172a;">
                        We built JobSnap to do the heavy lifting:
                    </p>
                    <ul style="margin: 8px 0 0 0; padding-left: 18px; font-size: 13.5px; color: #475569;">
                        <li style="margin-bottom: 5px;">Aggregates live roles across LinkedIn, Naukri & Internshala</li>
                        <li style="margin-bottom: 5px;">AI scans your resume & gives you an instant match %</li>
                        <li>Autofills tedious application forms with 1 click</li>
                    </ul>
                </div>

                <p style="margin: 0 0 16px 0; font-size: 14px; color: #334155;">
                    We originally planned to charge for Pro access, but knowing how tough the hiring scene is right now, we decided to make it <strong>100% FREE for early members</strong> until our server compute runs out. No cards, no catches.
                </p>

                <!-- Clean No-Link CTA Box -->
                <div style="background-color: #0f172a; color: #ffffff; padding: 16px 20px; border-radius: 8px; text-align: center; margin: 24px 0;">
                    <p style="margin: 0; font-size: 14px; font-weight: 600; color: #ffffff;">
                        Want your private access pass?
                    </p>
                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #94a3b8;">
                        Simply reply <strong>"ACCESS"</strong> to this email, and I’ll send your private key directly.
                    </p>
                </div>

                <p style="margin: 24px 0 0 0; font-size: 13.5px; color: #64748b;">
                    Rooting for your career,<br>
                    <strong style="color: #0f172a;">Musab</strong><br>
                    Founder, JobSnap
                </p>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    },
    "2": {
        "subject": "Your JobSnap founding pass is confirmed",
        "body_html": """\
<html>
<body style="margin: 0; padding: 24px 12px; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #0f172a; line-height: 1.55;">
    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 520px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <tr>
            <td style="padding: 28px 32px 20px 32px; border-bottom: 1px solid #f1f5f9;">
                <div style="font-size: 18px; font-weight: 700; letter-spacing: -0.02em; color: #0f172a;">
                    JobSnap <span style="font-size: 11px; font-weight: 600; color: #059669; background: #ecfdf5; padding: 3px 8px; border-radius: 12px; margin-left: 6px; letter-spacing: 0;">VIP PASS CONFIRMED</span>
                </div>
            </td>
        </tr>
        <tr>
            <td style="padding: 28px 32px 32px 32px;">
                <p style="margin: 0 0 16px 0; font-size: 15px;">Hey <strong>{name}</strong>,</p>

                <p style="margin: 0 0 16px 0; font-size: 14px; color: #334155;">
                    As promised, your private founding member pass is officially reserved:
                </p>

                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 14px 16px; margin: 0 0 20px 0; border-radius: 8px;">
                    <p style="margin: 0 0 4px 0; font-size: 13px; color: #64748b;">Member Tier: <strong style="color: #0f172a;">Early Founding VIP (100% Free)</strong></p>
                    <p style="margin: 0 0 4px 0; font-size: 13px; color: #64748b;">Role Focus: <strong style="color: #0f172a;">{role}</strong></p>
                    <p style="margin: 0; font-size: 13px; color: #64748b;">Invite Pass Code: <strong style="color: #0284c7; font-family: monospace; font-size: 14px;">{ticketId}</strong></p>
                </div>

                <p style="margin: 0 0 10px 0; font-size: 14px; font-weight: 600; color: #0f172a;">
                    What happens next:
                </p>
                <ol style="margin: 0 0 20px 0; padding-left: 20px; font-size: 13.5px; color: #475569; line-height: 1.6;">
                    <li style="margin-bottom: 6px;"><strong>VIP Spot Secured:</strong> Your free founding access and priority compute allocation are locked in under pass <strong>{ticketId}</strong>.</li>
                    <li style="margin-bottom: 6px;"><strong>Private Beta Rollout:</strong> We’re wrapping up the final touches and onboarding founding members in small, private batches.</li>
                    <li><strong>Direct Access Link:</strong> The moment your batch opens, you’ll receive an email with your private access link to jump straight in.</li>
                </ol>

                <p style="margin: 0 0 16px 0; font-size: 13.5px; color: #475569;">
                    Have target roles in mind or specific features you’d love to see at launch? Simply reply to this email — I read every note personally.
                </p>

                <p style="margin: 24px 0 0 0; font-size: 13.5px; color: #64748b;">
                    Rooting for your career,<br>
                    <strong style="color: #0f172a;">Musab</strong><br>
                    Founder, JobSnap
                </p>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    }
}

def get_gmail_service():
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.pickle")
    if not os.path.exists(token_path):
        raise FileNotFoundError(f"token.pickle not found at {token_path}")
    
    with open(token_path, "rb") as token:
        creds = pickle.load(token)
    
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)
    
    service = build("gmail", "v1", credentials=creds)
    return service

def send_message(service, sender, to, subject, body_html):
    message = MIMEMultipart("alternative")
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject

    part = MIMEText(body_html, "html")
    message.attach(part)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return service.users().messages().send(userId="me", body={"raw": raw}).execute()

def main():
    parser = argparse.ArgumentParser(description="JobSnap Launch Email Tool")
    parser.add_argument("--type", choices=["1", "2"], default="1", help="1 = Heads-up, 2 = Live launch")
    parser.add_argument("--test-to", type=str, default=None, help="Send a single test email to this address")
    parser.add_argument("--send-all", action="store_true", help="Actually send emails to all waitlist contacts")
    parser.add_argument("--yes", action="store_true", help="Confirm execution without interactive prompt")
    parser.add_argument("--filter-names", nargs="+", help="Filter recipients by name (case-insensitive substring)")
    parser.add_argument("--filter-emails", nargs="+", help="Filter recipients by email (case-insensitive substring)")
    args = parser.parse_args()

    csv_file = get_csv_file()
    contacts = []
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append(row)

    if args.filter_names or args.filter_emails:
        filtered = []
        for c in contacts:
            c_name = c.get("Name", "").lower()
            c_email = c.get("Email", "").lower()
            match = False
            if args.filter_names and any(fn.lower() in c_name for fn in args.filter_names):
                match = True
            if args.filter_emails and any(fe.lower() in c_email for fe in args.filter_emails):
                match = True
            if match:
                filtered.append(c)
        contacts = filtered

    tmpl = EMAIL_TEMPLATES[args.type]

    if args.test_to:
        print(f"[*] Sending test Email Type {args.type} to: {args.test_to}")
        try:
            service = get_gmail_service()
            subject = tmpl["subject"].format(name="Founder Test", role="Tech / Product")
            body = tmpl["body_html"].format(name="Musab", role="Tech / Product", ticketId="FOUNDER-VIP")
            send_message(service, "me", args.test_to, subject, body)
            print("[+] Test email sent successfully via Gmail API!")
        except Exception as e:
            print(f"[-] Error sending test email: {e}")
        return

    if not args.send_all:
        print("="*60)
        print(f"[DRY RUN PREVIEW] (Email Type {args.type}) - No emails sent.")
        print(f"Found {len(contacts)} waitlist contacts in CSV.")
        print("="*60)
        sample = contacts[0]
        name = sample.get("Name", "there")
        role = sample.get("Role_Category", "your domain")
        print(f"Sample Recipient: {sample['Email']} ({name})")
        print(f"Subject: {tmpl['subject'].format(name=name, role=role)}")
        print("\nPass '--send-all' to send to all contacts, or '--test-to you@example.com' to test.\n")
        for i, c in enumerate(contacts, 1):
            print(f"{i:02d}. {c['Email']} | {c['Name']} | {c['Role_Category']}")
        return

    # Real send
    print(f"[!] REAL SEND: Broadcasting Email Type {args.type} to {len(contacts)} recipients...")
    if not args.yes:
        confirm = input("Are you absolutely sure you want to send? (type 'yes' to proceed): ")
        if confirm.strip().lower() != "yes":
            print("Aborted.")
            return

    service = get_gmail_service()
    success_count = 0
    for idx, c in enumerate(contacts, 1):
        email = c["Email"].strip()
        name = c["Name"].strip() or "there"
        role = c.get("Role_Category", "your domain")
        ticket_id = c.get("TicketId") or c.get("PassCode") or f"JS-{random.randint(1000, 9999)}"
        subject = tmpl["subject"].format(name=name, role=role)
        body = tmpl["body_html"].format(name=name, role=role, ticketId=ticket_id)

        try:
            send_message(service, "me", email, subject, body)
            print(f"[{idx}/{len(contacts)}] Sent to {email} ({name})")
            success_count += 1
            time.sleep(1.5)  # Safe rate limit
        except Exception as e:
            print(f"[-] Failed for {email}: {e}")

    print(f"\n[+] Finished! Successfully sent {success_count}/{len(contacts)} emails.")

if __name__ == "__main__":
    main()
