from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from HandyWrappers import HandyWrappers
from pathlib import Path
import logging
import time
import re
import os

class ShellpointAut:
    HW = HandyWrappers()

    def create_headless_browser(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Remove "Chrome is being controlled" message
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # Prevent Selenium from being detected
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # Automatically download & use the correct ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def open_url(self, driver, url, timeout=100):
        """Open a URL with error handling."""
        try:
            logging.info(f"Opening URL: {url}")
            driver.get(url)
            driver.implicitly_wait(timeout)
        except TimeoutException:
            logging.error("Page load timed out.")
            print("The page took too long to load. Please try again.")

    def login_shellpoint(self, driver, shellpoint_url, shellpoint_username, shellpoint_password, phonecom_url, phonecom_username, phonecom_password, headless):
        """Log into Shellpoint, handling potential 2FA."""
        self.open_url(driver, shellpoint_url, timeout=100)

        logging.info(f"Working on login.")
        # Click the sign-in button
        self.HW.click_element(driver, 20, "//myaccount-dashboard-root//myaccount-servicing-welcome-home//a[contains(.,'Sign In')]")
        # Enter username and password
        self.HW.input_text(driver, 20, "//input[@autocomplete or @name='username']", shellpoint_username, enter=True)
        self.HW.input_text(driver, 20, "//input[@type ='password']", shellpoint_password, enter=True)
        time.sleep(5)

        # Handle 2FA if prompted
        try:
            if self.HW.element_exists(driver, 10, "//a[.='Send code']"):
                self.HW.click_element(driver, 10, "//a[.='Send code']")
                code = self.retrieve_2fa_code(driver, phonecom_url, phonecom_username, phonecom_password, headless)
                self.HW.input_text(driver, 20, "//input[@name='answer']", code, enter=True)
        except TimeoutException as e:
            logging.error(f"Timeout while trying to access the page: {e}")
        except NoSuchElementException as e:
            logging.error(f"Code not found: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
    
    def retrieve_2fa_code(self, driver, phonecom_url, phonecom_username, phonecom_password, headless):
        """Retrieve 2FA code from Phone.com."""
        logging.info(f"Retrieving 2FA code from {phonecom_url}")
        phonecom_driver = Driver(uc=True, headless=headless)
        self.open_url(phonecom_driver, phonecom_url, timeout=100)

        # Log into Phone.com account
        self.HW.input_text(phonecom_driver, 20, "//input[@name='username']", phonecom_username)
        self.HW.input_text(phonecom_driver, 20, "//input[@type ='password']", phonecom_password, enter=True)        
        time.sleep(60)
        #self.HW.click_element(phonecom_driver, 30, "//span[.='Messages']")
        self.HW.click_element(phonecom_driver, 30, '//div[contains(@data-test-id,"messages")]')
        time.sleep(15)

        # Extract 2FA code
        try:
            latest_message = self.HW.get_text(phonecom_driver, 30, '(//span[contains(., "Your verification code is")])[1]')
            code = re.search(r'(\d{6})', latest_message).group(1) if latest_message else None
        except (TimeoutException, AttributeError):
            logging.warning("2FA code not found, attempting re-fetch.")
            self.HW.click_element(driver, 30, "//a[.='Re-send code']")
            time.sleep(5)
            phonecom_driver.refresh()
            phonecom_driver.implicitly_wait(100)
            time.sleep(2)
            self.HW.click_element(phonecom_driver, 30, "//span[.='Messages']")
            latest_message = self.HW.get_text(phonecom_driver, 30, '(//span[contains(., "Your verification code is")])[1]')
            code = re.search(r'(\d{6})', latest_message).group(1) if latest_message else None

        phonecom_driver.quit()
        logging.info(f"Retrieved 2FA code: {code}")
        return code
        
    def download_statement(self, driver, account_number, LenderName='shellpoint'):
        """Download the latest statement for the given account."""
        js_code = "arguments[0].scrollIntoView();"
        element = driver.find_element(By.XPATH, f'(//span[normalize-space(.)="Loan #: {account_number}"])[1]')
        driver.execute_script(js_code, element)
        time.sleep(2)
        # Navigate through the UI to download the statement
        self.HW.click_element(driver, 10, f'(//span[normalize-space(.)="Loan #: {account_number}"])[1]//ancestor::div[contains(@class, "loan-card")]//button[normalize-space(.)="Account Details"]')
        self.HW.click_element(driver, 10, '//div[@class="container-fluid"]//li//a[normalize-space(.)="Statements"]')
        self.HW.click_element(driver, 10, '//div[@class="container-fluid"]//li//a[normalize-space(.)="Monthly"]')
        self.HW.click_element(driver, 10, '(//div[contains(@class,"card")]//span[.="Download"])[1]')
        logging.info(f"Trying to Get the date and creating desired file name")
        date_text = self.HW.get_text(driver, 10, '(//div[contains(@class,"card")]//h6)[1]')
        filename = self.HW.convert_proper_filename(date_text, account_number, LenderName)
        time.sleep(10)  # Allow time for download
        return filename

    def filename_renaming(self, download_folder, new_filename, old_filename="Monthly Statement.pdf"):
        # Construct full file paths
        old_file_path = os.path.join(download_folder, old_filename)
        # new_file_path = os.path.join(download_folder, new_filename)
        
        # Ensure paths are properly formatted
        new_file_path = Path(download_folder) / new_filename
        # Convert to string if needed for external functions
        new_file_path_str = str(new_file_path)

        # Check if the file exists before renaming
        if os.path.exists(old_file_path):
            os.rename(old_file_path, new_file_path_str)
            print(f"✅ File successfully renamed to: {new_filename} and saved in: {new_file_path_str}")
        else:
            print(f"⚠ File not found: {old_file_path}")
        return new_file_path_str, new_filename
  
    def upload_to_drive(self, SERVICE_ACCOUNT_FILE, FOLDER_ID, FILE_PATH, FILE_NAME):
        # Define the scope
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        # Authenticate the service account
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)

        try:
            # Set metadata for the file
            file_metadata = {'name': FILE_NAME, 'parents': [FOLDER_ID], 'driveId': FOLDER_ID, 'mimeType': 'pdf'}

            # Upload the file
            media = MediaFileUpload(FILE_PATH, mimetype='application/pdf')
            file = service.files().create(body=file_metadata, media_body=media, 
                                          supportsAllDrives=True, fields='id').execute()
            print(f"File uploaded successfully! File ID: {file.get('id')}")

        except Exception as e:
            print(f"Error during Google Drive upload: {e}")
