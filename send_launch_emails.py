"""
JobSnap Launch Email Dispatcher
Supports dry-run preview, test-send to founder, and full batch delivery via Gmail API.
"""

import os
import csv
import sys
import html
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

def get_csv_file():
    if os.path.exists(CSV_PATH):
        return CSV_PATH
    raise FileNotFoundError(f"Could not find waitlist CSV at {CSV_PATH}")

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
                    Spending 45 minutes re-typing your resume into yet another Workday portal - only to get left on "seen" like an unreplied Instagram DM - has to stop.
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
                    Have target roles in mind or specific features you’d love to see at launch? Simply reply to this email - I read every note personally.
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
    },
    "3": {
        "subject": "We're live! Your early access to AI JobSnap is open, {name}",
        "body_text": """\
Hey {name},

Thanks for joining the early-access waitlist - AI JobSnap is officially LIVE and your spot is open!

Jump straight in here:
https://app.jobsnap.me

What's ready for you right now (tailored for {role}):
- Multi-Source Job Discovery: Pull live opportunities from LinkedIn, Naukri, Internshala & direct recruiters in seconds.
- Resume-Aware AI Fit Score: Upload your resume once to see instant match scores and exact skill gaps on every role.
- Interactive Skill Gap & Roadmaps: Turn missing skills into weekly action plans with hands-on projects and verified certificates.
- Outreach Studio & Smart Reminders: Find hiring teams, set follow-up reminders, and sync deadlines straight to Google Calendar.

You can sign in with Google in one click (or create an email account) and start for free right away:
https://app.jobsnap.me

If you run into anything or want a specific feature for {role}, just hit reply - I read every single email personally.

Rooting for your career,
Musab
Founder, AI JobSnap
""",
        "body_html": """\
<html>
<body style="margin: 0; padding: 24px 12px; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #0f172a; line-height: 1.6;">
    <span style="display: none; font-size: 1px; color: #f8fafc; line-height: 1px; max-height: 0; max-width: 0; opacity: 0; overflow: hidden;">
        AI JobSnap is live! Sign in at app.jobsnap.me and start matching with live roles today.
    </span>
    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 540px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);">
        <!-- Header -->
        <tr>
            <td style="padding: 24px 32px; border-bottom: 1px solid #f1f5f9;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                        <td style="font-size: 18px; font-weight: 800; letter-spacing: -0.02em; color: #0f172a;">
                            AI JobSnap
                        </td>
                        <td align="right">
                            <span style="display: inline-block; font-size: 11px; font-weight: 700; color: #059669; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 4px 10px; border-radius: 999px; letter-spacing: 0.04em; text-transform: uppercase;">
                                WE'RE LIVE
                            </span>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>

        <!-- Body -->
        <tr>
            <td style="padding: 28px 32px 32px 32px;">
                <p style="margin: 0 0 14px 0; font-size: 15px;">Hey <strong>{name}</strong>,</p>

                <p style="margin: 0 0 16px 0; font-size: 14.5px; color: #334155;">
                    Thank you for signing up for early access - <strong>AI JobSnap is officially live</strong>, and your early-access invite is ready!
                </p>

                <p style="margin: 0 0 20px 0; font-size: 14px; color: #475569;">
                    No more juggling ten job boards or guessing which skills you're missing. Everything is built to save you hours every week in <strong>{role}</strong>:
                </p>

                <!-- Feature Highlights Card -->
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 3px solid #10b981; padding: 16px 18px; margin: 0 0 24px 0; border-radius: 0 10px 10px 0;">
                    <ul style="margin: 0; padding-left: 18px; font-size: 13.5px; color: #334155; line-height: 1.65;">
                        <li style="margin-bottom: 6px;"><strong>Multi-Source Job Discovery:</strong> Pull live roles across LinkedIn, Naukri, Internshala &amp; direct recruiters in seconds.</li>
                        <li style="margin-bottom: 6px;"><strong>Resume-Aware AI Fit Score:</strong> Upload your resume once to see instant match % and exact skill gaps on every role.</li>
                        <li style="margin-bottom: 6px;"><strong>Custom Skill Gap &amp; Roadmaps:</strong> Turn missing skills into weekly plans with hands-on projects &amp; verified certificates.</li>
                        <li><strong>Outreach Studio &amp; Calendar Sync:</strong> Track recruiters, set follow-up reminders, and sync directly with Google Calendar.</li>
                    </ul>
                </div>

                <!-- Primary Launch CTA Button -->
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 26px 0 18px 0;">
                    <tr>
                        <td align="center">
                            <a href="https://app.jobsnap.me" target="_blank" style="display: inline-block; background-color: #10b981; color: #ffffff; font-size: 14.5px; font-weight: 700; text-decoration: none; padding: 13px 28px; border-radius: 10px; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);">
                                Open AI JobSnap &rarr;
                            </a>
                        </td>
                    </tr>
                </table>

                <p style="margin: 0 0 20px 0; font-size: 12px; color: #64748b; text-align: center;">
                    Or copy &amp; paste this link: <a href="https://app.jobsnap.me" style="color: #059669; text-decoration: underline;">https://app.jobsnap.me</a>
                </p>

                <p style="margin: 0 0 16px 0; font-size: 13.5px; color: #475569;">
                    You can sign in with Google in one click and start right away. Hit reply anytime with feedback or feature ideas - I read every message personally!
                </p>

                <p style="margin: 24px 0 0 0; font-size: 13.5px; color: #64748b;">
                    Rooting for your career,<br>
                    <strong style="color: #0f172a;">Musab</strong><br>
                    Founder, AI JobSnap
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

def send_message(service, sender, to, subject, body_html, body_text=None):
    message = MIMEMultipart("alternative")
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject

    if body_text:
        message.attach(MIMEText(body_text, "plain", "utf-8"))
    message.attach(MIMEText(body_html, "html", "utf-8"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return service.users().messages().send(userId="me", body={"raw": raw}).execute()

def main():
    parser = argparse.ArgumentParser(description="JobSnap Launch Email Tool")
    parser.add_argument("--type", choices=["1", "2", "3"], default="3", help="1 = Heads-up, 2 = VIP Pass, 3 = We're Live (app.jobsnap.me)")
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
            subject = tmpl["subject"].format(name="Test User", role="Technology and IT")
            body = tmpl["body_html"].format(name="Test User", role="Technology and IT", ticketId="PREVIEW-001")
            body_text = tmpl.get("body_text", "").format(name="Test User", role="Technology and IT", ticketId="PREVIEW-001") or None
            send_message(service, "me", args.test_to, subject, body, body_text=body_text)
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
        name = (sample.get("Name") or "there").strip()
        role = (sample.get("Role_Category") or "your field").strip()
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
        raw_name = (c.get("Name") or "").strip() or "there"
        raw_role = (c.get("Role_Category") or "").strip() or "your field"
        ticket_id = c.get("TicketId") or c.get("PassCode") or f"JS-{random.randint(1000, 9999)}"
        subject = tmpl["subject"].format(name=raw_name, role=raw_role)
        body = tmpl["body_html"].format(
            name=html.escape(raw_name),
            role=html.escape(raw_role),
            ticketId=html.escape(ticket_id),
        )
        body_text = (
            tmpl.get("body_text", "").format(name=raw_name, role=raw_role, ticketId=ticket_id)
            if tmpl.get("body_text")
            else None
        )

        try:
            send_message(service, "me", email, subject, body, body_text=body_text)
            print(f"[{idx}/{len(contacts)}] Sent to {email} ({raw_name})")
            success_count += 1
            time.sleep(1.5)  # Safe rate limit
        except Exception as e:
            print(f"[-] Failed for {email}: {e}")

    print(f"\n[+] Finished! Successfully sent {success_count}/{len(contacts)} emails.")

if __name__ == "__main__":
    main()
