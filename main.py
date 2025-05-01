from ShellpointAut import ShellpointAut
import logging
# Set up logging configuration for better debugging and monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Main():
    ShellpointAut = ShellpointAut()

    def main(self, headless):
        # Credentials
        shellpoint_url = 'https://www.shellpointmortgageservicing.com'
        shellpoint_username = '' # Add Shellpoint Username
        shellpoint_password = '' # Add Shellpoint User Password
        shellpoint_account_no = '' # Add Shellpoint Account no (in int datatype)
        phonecom_url = 'https://accounts.phone.com/?client_id=e53f4ba1-3af0-410d-8861-83759c0b37b0&redirect_uri=https://my.phone.com'
        phonecom_username = '' # Add Phonecom Username
        phonecom_password = '' # Add Phonecom User Password
        download_folder = r"C:\Users\Noor\Downloads" 
        SERVICE_ACCOUNT_FILE = ''  # Path to your service account file
        FOLDER_ID = ''  # Extracted from shared drive link
        
        # Perform login and download statement
        try:
            logging.info(f"Starting browser instance for {shellpoint_url}")
            driver = self.ShellpointAut.create_headless_browser()
            self.ShellpointAut.login_shellpoint(driver, shellpoint_url, shellpoint_username, shellpoint_password, 
                                                phonecom_url, phonecom_username, phonecom_password, headless)
            logging.info(f"Trying to download the **Monthly Statement** file")
            new_filename = self.ShellpointAut.download_statement(driver, shellpoint_account_no, 
                                                                 LenderName='shellpoint')
        except Exception as e:
            logging.error(f"Error during Shellpoint automation: {e}")
            new_filename = None
        finally:
            driver.quit()
            logging.info(f"Ending browser instance for {shellpoint_url}")


        # Rename the downloaded file
        try:
            logging.info("Renaming the downloaded file")
            new_file_path, new_filename = self.ShellpointAut.filename_renaming(download_folder, new_filename, 
                                                                               old_filename="Monthly Statement.pdf")
        except Exception as e:
            logging.error(f"Error during renaming the file: {e}")

      
        # Upload downloaded statement to Google Drive
        logging.info("Starting Google Drive upload process")
        try:
            self.ShellpointAut.upload_to_drive(SERVICE_ACCOUNT_FILE=SERVICE_ACCOUNT_FILE, FOLDER_ID=FOLDER_ID, 
                                               FILE_PATH= new_file_path, FILE_NAME=new_filename)
        except Exception as e:
            logging.error(f"Error during Google Drive upload: {e}")

test=Main()
test.main(headless=True)
