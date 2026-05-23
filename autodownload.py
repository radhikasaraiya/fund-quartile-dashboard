import os
import subprocess
import sys
import datetime
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
        context.set_default_timeout(90000)
        context.set_default_navigation_timeout(90000)
        page = context.new_page()

        # ---------------- LOGIN ----------------
        page.goto(URL)
        page.wait_for_selector("input[type='text']")

        page.get_by_role("textbox", name="Email").fill(EMAIL)
        page.get_by_role("textbox", name="Username").fill(USERNAME)
        page.get_by_role("textbox", name="Password").fill(PASSWORD)
        page.get_by_role("button", name="Login").click()

        # Go to AUM page
        page.goto("https://www.money2management.com/MF_AUM.aspx")
        page.wait_for_selector("#ctl00_ContentPlaceHolder1_rbtnsort")

        # Select Individual Wise
        page.select_option(
            "#ctl00_ContentPlaceHolder1_rbtnsort",
            value="AUMClientWise"
        )
        page.wait_for_selector("#ctl00_ContentPlaceHolder1_chkinvamt")

        # Tick With Investment Amount
        page.check("#ctl00_ContentPlaceHolder1_chkinvamt")

        # Download Excel
        with page.expect_download(timeout=90000) as download_info:
            page.get_by_role("button", name="Excel").click()

        download = download_info.value
        
        # Ensure the directory exists
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        file_path = os.path.join(DOWNLOAD_DIR, "AUM_IndividualWise.xlsx")
        
        download.save_as(file_path)

        print(f"Download completed successfully [Success]. Saved to {file_path}")

        browser.close()


def MyFundList():
    _ensure_playwright_browsers()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        context.set_default_timeout(90000)
        context.set_default_navigation_timeout(90000)
        page = context.new_page()

        # ---------------- LOGIN ----------------
        page.goto(URL)
        page.wait_for_selector("input[type='text']")

        page.get_by_role("textbox", name="Email").fill(EMAIL)
        page.get_by_role("textbox", name="Username").fill(USERNAME)
        page.get_by_role("textbox", name="Password").fill(PASSWORD)
        page.get_by_role("button", name="Login").click()

        # Go to AUM page
        page.goto("https://www.money2management.com/MF_AUM.aspx")
        page.wait_for_selector("#ctl00_ContentPlaceHolder1_rbtnsort")

        # Select Scheme Wise
        page.select_option(
            "#ctl00_ContentPlaceHolder1_rbtnsort",
            value="AUMSchemeWise"
        )
        page.wait_for_selector("#ctl00_ContentPlaceHolder1_chkinvamt")

        # Tick With Investment Amount
        page.check("#ctl00_ContentPlaceHolder1_chkinvamt")

        # Download Excel
        with page.expect_download(timeout=90000) as download_info:
            page.get_by_role("button", name="Excel").click()

        download = download_info.value
        
        # Ensure the directory exists
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(DOWNLOAD_DIR, f"SchemeWise_Fund_{today_str}.xls")
        
        download.save_as(file_path)

        print(f"Download completed successfully [Success]. Saved to {file_path}")

        browser.close()


def ScriptWiseClient(scriptname):
    """Download scheme-wise client details Excel for a given script/scheme name."""
    _ensure_playwright_browsers()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        context.set_default_timeout(90000)
        context.set_default_navigation_timeout(90000)
        page = context.new_page()

        # ---------------- LOGIN ----------------
        page.goto(URL)
        page.wait_for_selector("input[type='text']")

        page.get_by_role("textbox", name="Email").fill(EMAIL)
        page.get_by_role("textbox", name="Username").fill(USERNAME)
        page.get_by_role("textbox", name="Password").fill(PASSWORD)
        page.get_by_role("button", name="Login").click()

        # Go to Scheme Wise Report page
        page.goto("https://www.money2management.com/MF_SchemewiseReport.aspx")
        page.wait_for_selector("#ctl00_ContentPlaceHolder1_drp_scheme", state="attached")

        # Find the matching option value for the given scriptname
        options = page.locator("#ctl00_ContentPlaceHolder1_drp_scheme option").element_handles()
        selected_value = None
        print(f"Found {len(options)} scheme options.")

        # Try exact match first, then partial match
        for opt in options:
            text = opt.text_content()
            if text and scriptname.strip().lower() == text.strip().lower():
                selected_value = opt.get_attribute("value")
                break

        if not selected_value:
            # Fallback to partial match
            for opt in options:
                text = opt.text_content()
                if text and scriptname.strip().lower() in text.strip().lower():
                    selected_value = opt.get_attribute("value")
                    print(f"Partial match found: {text.strip()}")
                    break

        if not selected_value:
            print(f"Could not find scheme: {scriptname}")
            browser.close()
            return None

        # Chosen.js hides the select tag, so use JS to set value and trigger postback
        page.evaluate(f"""
            const el = document.getElementById('ctl00_ContentPlaceHolder1_drp_scheme');
            el.value = '{selected_value}';
            el.dispatchEvent(new Event('change'));
            __doPostBack('ctl00$ContentPlaceHolder1$drp_scheme', '');
        """)
        # Wait for Export to Excel button to be attached/visible
        page.wait_for_selector("#ctl00_ContentPlaceHolder1_Btn_Export_Excel")

        # Click Export to Excel
        with page.expect_download(timeout=90000) as download_info:
            page.locator("#ctl00_ContentPlaceHolder1_Btn_Export_Excel").click()

        download = download_info.value

        # Save file
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(DOWNLOAD_DIR, f"ScriptWise_ClientDetails_{today_str}.xls")

        download.save_as(file_path)
        print(f"ScriptWise download completed [Success]. Saved to {file_path}")

        browser.close()
        return file_path


def download_client_portfolio(client_name):
    # Ensure the directory exists
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    safe_name = "".join([c if c.isalnum() else "_" for c in client_name])
    file_path = os.path.join(DOWNLOAD_DIR, f"Portfolio_{safe_name}_{today_str}.xls")
    
    if os.path.exists(file_path):
        print(f"Portfolio file for today already exists at {file_path}. Skipping download.")
        return file_path

    _ensure_playwright_browsers()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        # Increase timeouts significantly for cloud deployment (e.g. 120 seconds)
        context.set_default_timeout(120000)
        context.set_default_navigation_timeout(120000)
        page = context.new_page()

        # ---------------- LOGIN ----------------
        page.goto(URL)
        page.wait_for_selector("input[type='text']")

        page.get_by_role("textbox", name="Email").fill(EMAIL)
        page.get_by_role("textbox", name="Username").fill(USERNAME)
        page.get_by_role("textbox", name="Password").fill(PASSWORD)
        page.get_by_role("button", name="Login").click()

        # Go to Portfolio page
        page.goto("https://www.money2management.com/MF_MutualFundPortFoilo.aspx")
        page.wait_for_selector("#ctl00_ContentPlaceHolder1_rbtn_clienttype_1")

        # Select Individual Radio Button
        page.check("#ctl00_ContentPlaceHolder1_rbtn_clienttype_1")
        
        # Wait for the Client Name dropdown to contain options (it is populated via AJAX)
        page.wait_for_selector("#ctl00_ContentPlaceHolder1_drp_ClientName option[value]", state="attached")
        page.wait_for_timeout(3000)  # Wait for AJAX population to complete

        # Select Client
        options = page.locator("#ctl00_ContentPlaceHolder1_drp_ClientName option").element_handles()
        selected_value = None
        print(f"Found {len(options)} options.")

        for opt in options:
            text = opt.text_content()
            if text:
                norm_text = " ".join(text.lower().split())
                norm_client = " ".join(client_name.lower().split())
                if norm_client in norm_text:
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
        
        # Wait for the export button to be visible/enabled
        page.wait_for_selector("#ctl00_ContentPlaceHolder1_btn_export_excel")

        # Download Excel
        with page.expect_download(timeout=120000) as download_info:
            page.locator("#ctl00_ContentPlaceHolder1_btn_export_excel").click()

        download = download_info.value
        
        download.save_as(file_path)
        print(f"Portfolio download completed [Success]. Saved to {file_path}")

        browser.close()
        return file_path



if __name__ == "__main__":
   # download_client_portfolio("RADHIKA PRAGNESH SARAIYA")   
    #download_client_portfolio("AAFRIN WASIM QURESHI")
    #MyFundList()
    ScriptWiseClient("EDELWEISS LARGE & MID CAP FUND-REG(G)")