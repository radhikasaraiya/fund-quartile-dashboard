import os
from playwright.sync_api import sync_playwright

# ====== CONFIG ======
URL = "https://www.money2management.com/"
DOWNLOAD_DIR = os.path.join(os.getcwd(), "Data")

# Use environment variables for safety
USERNAME ="admin"
PASSWORD = "anand"
EMAIL = "pragneshsaraiya@hotmail.com"


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        # ---------------- LOGIN ----------------
        page.goto(URL)
        page.wait_for_load_state("networkidle")

        page.get_by_role("textbox", name="Email").fill(EMAIL)
        page.get_by_role("textbox", name="Username").fill(USERNAME)
        page.get_by_role("textbox", name="Password").fill(PASSWORD)
        page.get_by_role("button", name="Login").click()

       
        # ---------------- NAVIGATION ----------------
        # Wait properly after login
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(4000)

        # # 1️⃣ Click Mutual Fund (NOT hover)
        # page.get_by_text("Mutual Fund", exact=True).click()
        # page.wait_for_timeout(2000)

        # # 2️⃣ Click Distributor Report
        # page.get_by_text("Distributor Report", exact=True).click()
        # page.wait_for_timeout(2000)

        # # 3️⃣ Click AUM Report
        # page.get_by_text("AUM Report", exact=True).click()
        # Wait after login
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        # Go to AUM page
        page.goto("https://www.money2management.com/MF_AUM.aspx")
        page.wait_for_load_state("networkidle")

        # Select Individual Wise
        page.select_option(
            "#ctl00_ContentPlaceHolder1_rbtnsort",
            value="AUMClientWise"
        )
        page.wait_for_load_state("networkidle")

        # Tick With Investment Amount
        page.check("#ctl00_ContentPlaceHolder1_chkinvamt")

        # Download Excel
        with page.expect_download() as download_info:
            page.get_by_role("button", name="Excel").click()

        download = download_info.value
        
        # Ensure the directory exists
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        file_path = os.path.join(DOWNLOAD_DIR, "AUM_IndividualWise.xlsx")
        
        download.save_as(file_path)

        print(f"Download completed successfully ✅. Saved to {file_path}")

        browser.close()


if __name__ == "__main__":
    run()