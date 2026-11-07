import os
import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = r"c:\Users\musab\Desktop\demo_screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Standard Full HD 1920x1080 for demo video editing
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2 # Retina 2x clarity for ultra-crisp video assets
        )
        page = context.new_page()

        print("=== 1. Capturing Guide & Showcase (localhost:3000) ===")
        try:
            page.goto("http://localhost:3000", wait_until="networkidle", timeout=15000)
            time.sleep(2)

            # 01 Hero Section
            hero = page.locator("#hero")
            if hero.count() > 0:
                hero.screenshot(path=os.path.join(OUTPUT_DIR, "01_hero_early_access.png"))
                print("Captured 01_hero_early_access.png")
            else:
                page.screenshot(path=os.path.join(OUTPUT_DIR, "01_hero_early_access.png"))
                print("Captured 01_hero_early_access.png (full viewport)")

            # 02 Dashboard Console Preview
            dash_preview = page.locator("#dashboard-preview")
            if dash_preview.count() > 0:
                dash_preview.scroll_into_view_if_needed()
                time.sleep(1)
                dash_preview.screenshot(path=os.path.join(OUTPUT_DIR, "02_interactive_console_dashboard.png"))
                print("Captured 02_interactive_console_dashboard.png")

            # 03 Workflow Section
            workflow = page.locator("#workflow")
            if workflow.count() > 0:
                workflow.scroll_into_view_if_needed()
                time.sleep(1)
                workflow.screenshot(path=os.path.join(OUTPUT_DIR, "03_workflow_pipeline.png"))
                print("Captured 03_workflow_pipeline.png")

            # 04 Specialized Studios Section
            studios = page.locator("#studios")
            if studios.count() > 0:
                studios.scroll_into_view_if_needed()
                time.sleep(1)
                studios.screenshot(path=os.path.join(OUTPUT_DIR, "04_specialized_studios_overview.png"))
                print("Captured 04_specialized_studios_overview.png")

                # Individual Studio Cards
                studio_cards = studios.locator(".studio-card")
                if studio_cards.count() >= 2:
                    studio_cards.nth(0).screenshot(path=os.path.join(OUTPUT_DIR, "05_outreach_studio_feature_card.png"))
                    print("Captured 05_outreach_studio_feature_card.png")
                    studio_cards.nth(1).screenshot(path=os.path.join(OUTPUT_DIR, "06_skill_gap_roadmap_feature_card.png"))
                    print("Captured 06_skill_gap_roadmap_feature_card.png")

            # 07 Founding VIP Pass Modal
            # Trigger modal via JS or claim button
            page.evaluate("""() => {
                const modal = document.getElementById('spotReservedModal');
                if (modal) {
                    modal.removeAttribute('hidden');
                    modal.setAttribute('aria-hidden', 'false');
                    modal.style.display = 'flex';
                }
            }""")
            time.sleep(1.5)
            vip_modal = page.locator("#spotReservedModal")
            if vip_modal.is_visible():
                page.screenshot(path=os.path.join(OUTPUT_DIR, "07_founding_vip_pass_modal.png"))
                print("Captured 07_founding_vip_pass_modal.png")
                # Close modal
                page.evaluate("""() => {
                    const modal = document.getElementById('spotReservedModal');
                    if (modal) {
                        modal.setAttribute('hidden', '');
                        modal.setAttribute('aria-hidden', 'true');
                        modal.style.display = 'none';
                    }
                }""")
                time.sleep(0.5)

            # 08 Early Access & FAQ
            faq = page.locator("#faq")
            if faq.count() > 0:
                faq.scroll_into_view_if_needed()
                time.sleep(1)
                faq.screenshot(path=os.path.join(OUTPUT_DIR, "08_faq_and_answers.png"))
                print("Captured 08_faq_and_answers.png")

            early_access = page.locator("#early-access")
            if early_access.count() > 0:
                early_access.scroll_into_view_if_needed()
                time.sleep(1)
                early_access.screenshot(path=os.path.join(OUTPUT_DIR, "09_early_access_reservation.png"))
                print("Captured 09_early_access_reservation.png")

        except Exception as e:
            print(f"Error capturing localhost:3000: {e}")

        print("\n=== 2. Capturing Core Flask App (127.0.0.1:5000) ===")
        try:
            # Login screen
            page.goto("http://127.0.0.1:5000/login", wait_until="networkidle", timeout=15000)
            time.sleep(1)
            page.screenshot(path=os.path.join(OUTPUT_DIR, "10_platform_login_screen.png"))
            print("Captured 10_platform_login_screen.png")

            # Perform login with demo_seeker
            page.fill('.sign-in-container input[name="username"]', 'demo_seeker')
            page.fill('.sign-in-container input[name="password"]', 'demo123')
            page.click('#submitSignInBtn')
            page.wait_for_load_state("networkidle")
            time.sleep(2)

            # 11 Dashboard
            page.screenshot(path=os.path.join(OUTPUT_DIR, "11_main_job_dashboard.png"))
            print("Captured 11_main_job_dashboard.png")

            # 12 Outreach Studio (Full)
            page.goto("http://127.0.0.1:5000/outreach_studio", wait_until="networkidle")
            time.sleep(1.5)
            page.screenshot(path=os.path.join(OUTPUT_DIR, "12_outreach_studio_full_view.png"))
            print("Captured 12_outreach_studio_full_view.png")

            # 13 Outreach Studio - AI Discovery Panel Open
            find_btn = page.locator("button:has-text('Find Recruiters')")
            if find_btn.count() > 0:
                find_btn.first.click()
                time.sleep(1)
                page.screenshot(path=os.path.join(OUTPUT_DIR, "13_outreach_studio_ai_discovery.png"))
                print("Captured 13_outreach_studio_ai_discovery.png")

            # 14 Outreach Studio - Manual Contact Panel Open
            add_btn = page.locator("button:has-text('Add Contact')")
            if add_btn.count() > 0:
                add_btn.first.click()
                time.sleep(1)
                page.screenshot(path=os.path.join(OUTPUT_DIR, "14_outreach_studio_manual_contact.png"))
                print("Captured 14_outreach_studio_manual_contact.png")

            # 15 Direct Message Modal Open
            msg_btn = page.locator("button:has-text('Message')")
            if msg_btn.count() > 0:
                msg_btn.first.click()
                time.sleep(1)
                page.screenshot(path=os.path.join(OUTPUT_DIR, "15_outreach_studio_send_message_modal.png"))
                print("Captured 15_outreach_studio_send_message_modal.png")
                # close modal if cancel exists
                cancel_btn = page.locator("#send-message-modal button:has-text('Cancel')")
                if cancel_btn.count() > 0:
                    cancel_btn.click()
                time.sleep(0.5)

            # 16 Message Vault
            page.goto("http://127.0.0.1:5000/message_vault", wait_until="networkidle")
            time.sleep(1.5)
            page.screenshot(path=os.path.join(OUTPUT_DIR, "16_message_vault_templates.png"))
            print("Captured 16_message_vault_templates.png")

            # 17 Signal Board
            page.goto("http://127.0.0.1:5000/signal_board", wait_until="networkidle")
            time.sleep(1.5)
            page.screenshot(path=os.path.join(OUTPUT_DIR, "17_signal_board_live_telemetry.png"))
            print("Captured 17_signal_board_live_telemetry.png")

            # 18 Skill Gap / People Radar / Roadmap
            try:
                page.goto("http://127.0.0.1:5000/people_radar", wait_until="networkidle")
                time.sleep(1.5)
                page.screenshot(path=os.path.join(OUTPUT_DIR, "18_people_radar_directory.png"))
                print("Captured 18_people_radar_directory.png")
            except Exception as e:
                print(f"Note on people radar: {e}")

        except Exception as e:
            print(f"Error capturing 127.0.0.1:5000: {e}")

        browser.close()
        print(f"\nAll screenshots successfully saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    run()
