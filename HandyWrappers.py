from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import logging

class HandyWrappers:
    # Check if an element exists
    def element_exists(self, driver, timeout, xpath):
        try:
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except TimeoutException:
            return False

    # Click an element safely
    def click_element(self, driver, timeout, xpath):
        try:
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
        except TimeoutException:
            logging.warning(f"Element not clickable: {xpath}")
        
    # Input text into a field safely
    def input_text(self, driver, timeout, xpath, text, enter=False):
        try:
            element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            element.clear()
            element.send_keys(text + (Keys.RETURN if enter else ""))
        except TimeoutException:
            logging.warning(f"Failed to input text in: {xpath}")
    
    # Retrieve text from an element safely
    def get_text(self, driver, timeout, xpath):
        try:
            return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath))).text
        except TimeoutException:
            logging.warning(f"Failed to retrieve text from: {xpath}")
            return None

    # Get a proper date format
    def convert_proper_filename(self, date_str, account_number, LenderName='shellpoint'):
        date_obj = datetime.strptime(date_str, "%B %Y")  # Parse the string
        formatted_date = f"{date_obj.month}-{date_obj.year}"  # Convert to desired format
        return f'{formatted_date} - {LenderName} - {account_number}.pdf'