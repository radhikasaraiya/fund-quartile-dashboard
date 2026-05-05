import os
import subprocess
import sys
from playwright.sync_api import sync_playwright

# ====== CONFIG ======
URL = "https://www.money2management.com/"
DOWNLOAD_DIR = os.path.join(os.getcwd(), "Data")

# Use environment variables for safety
USERNAME ="admin"
PASSWORD = "anand"
EMAIL = "pragneshsaraiya@hotmail.com"


def _ensure_playwright_browsers():
    """Install Playwright Chromium browser if not already present (needed on Streamlit Cloud)."""
    # Check if chromium is already installed by looking for the executable
    try:
        from playwright._impl._driver import compute_driver_executable
        driver_exec = compute_driver_executable()
        result = subprocess.run(
            [str(driver_exec), "install", "--dry-run", "chromium"],
            capture_output=True, text=True
        )
        if "already installed" in (result.stdout + result.stderr).lower():
            return
    except Exception:
        pass
    # Download chromium browser binary (system deps come from packages.txt)
    print("Installing Playwright Chromium browser …")
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        check=True
    )


def run():
    _ensure_playwright_browsers()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
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

def download_client_portfolio(client_name):
    _ensure_playwright_browsers()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        # ---------------- LOGIN ----------------
        page.goto(URL)
        page.wait_for_load_state("networkidle")

        page.get_by_role("textbox", name="Email").fill(EMAIL)
        page.get_by_role("textbox", name="Username").fill(USERNAME)
        page.get_by_role("textbox", name="Password").fill(PASSWORD)
        page.get_by_role("button", name="Login").click()

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        # ---------------- NAVIGATION ----------------
        page.goto("https://www.money2management.com/MF_MutualFundPortFoilo.aspx")
        page.wait_for_load_state("networkidle")

        # Select Client
        page.wait_for_selector("#ctl00_ContentPlaceHolder1_drp_ClientName", state="attached")
        options = page.locator("#ctl00_ContentPlaceHolder1_drp_ClientName option").element_handles()
        selected_value = None
        for opt in options:
            text = opt.inner_text()
            if client_name.lower() in text.lower():
                selected_value = opt.get_attribute("value")
                break
                
        if not selected_value:
            print(f"Could not find client: {client_name}")
            browser.close()
            return None
            
        # Chosen.js hides the select tag, so we use JS to set value and trigger onchange
        page.evaluate(f"""
            const el = document.getElementById('ctl00_ContentPlaceHolder1_drp_ClientName');
            el.value = '{selected_value}';
            el.dispatchEvent(new Event('change'));
        """)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        # Download Excel
        with page.expect_download() as download_info:
            page.locator("#ctl00_ContentPlaceHolder1_btn_export_excel").click()

        download = download_info.value
        
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        safe_name = "".join([c if c.isalnum() else "_" for c in client_name])
        file_path = os.path.join(DOWNLOAD_DIR, f"Portfolio_{safe_name}.xls")
        
        download.save_as(file_path)
        print(f"Portfolio download completed ✅. Saved to {file_path}")

        browser.close()
        return file_path



if __name__ == "__main__":
    download_client_portfolio("AAKASH ISHVARLAL SHAH")