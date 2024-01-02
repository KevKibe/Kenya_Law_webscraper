import os
import boto3
from botocore.exceptions import NoCredentialsError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException


class CaseLawScraper:

    def __init__(self, base_url, num_pages, tmp_directory):

        """
        Initializes the CaseLawDownloader.

        Args:
            base_url (str): The base URL for the kenyalaw website caselaws repository.
            num_pages (int): The number of pages to download.
            tmp_directory (str): The temporary directory for storing downloaded files default('/temp').
        """

        print("Initializing CaseLawDownloader...")
        self.base_url = base_url
        self.num_pages = num_pages
        self.tmp_directory = tmp_directory
        self.driver = None
        self.downloaded_files = set()  



    def setup_driver(self):

        """
        Sets up the WebDriver for interacting with the web page.

        Uses Chrome WebDriver with specific options for downloading files to the specified directory.
        """

        print("Setting up driver...")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('prefs', {'download.default_directory': self.tmp_directory})
        self.driver = webdriver.Chrome(options=chrome_options)



    def teardown_driver(self):

        """
        Tears down the WebDriver, closing the browser window.
        """

        print("Tearing down driver...")
        self.driver.quit()



    def read_file_content(self, file_path):

        """
        Reads and returns the content of a file.

        Args:
            file_path (str): The path to the file.

        Returns:
            str: The content of the file.
        """

        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return file.read()
        else:
            print(f"File {file_path} does not exist.")
            return None
        


    def download_cases(self):

        """
        Downloads casefiels from the base_url.
        
        """

        print("Downloading cases...")
        if not self.driver:
            self.setup_driver()

        for page_num in range(1, self.num_pages + 1):
            url = self.base_url + str(page_num) + "/"
            print(f"Accessing URL: {url}")
            self.driver.get(url)

            read_more_buttons = self.driver.find_elements(By.XPATH, "//a[@class='show-more pull-right']")

            for button in read_more_buttons:
                try:
                    print("Clicking 'read more' button...")
                    self.driver.execute_script("arguments[0].click();", button)

                    print("Waiting for download button to appear...")
                    download_button = WebDriverWait(self.driver, 40).until(
                        EC.presence_of_element_located((By.XPATH, "//a[@title='Download Original Document']"))
                    )

                    print("Downloading file...")
                    self.driver.execute_script("arguments[0].click();", download_button)
                    self.driver.back()

                except StaleElementReferenceException:
                    print("Caught StaleElementReferenceException, continuing...")
                    continue
        self.teardown_driver()



    def note_downloaded_files_s3(self,bucket):

        """
        Lists all downloaded files in an S3 bucket and writes the filenames to 'casefile_names.txt'.

        Args:
            bucket (str): The name of the S3 bucket.
        """
        try:
            s3 = boto3.client('s3')
            objects = s3.list_objects(Bucket=bucket)
            filenames = [obj['Key'] for obj in objects.get('Contents', [])]

            with open('casefile_names.txt', 'w') as f:
                for filename in filenames:
                    f.write(filename + '\n')
            print("Successfully written filenames to 'casefile_names.txt'")
        except Exception as e:
            print(f"An error occurred: {e}")




    def upload_object_to_s3(self, local_file, bucket, s3_file):

        """
        Uploads downloaded files to an S3 bucket.

        Args:
            local_file (str): The path to the local file to upload.
            bucket (str): The name of the S3 bucket.
            s3_file (str): The destination filename in the S3 bucket.

        Returns:
           bool: True if the upload is successful, False otherwise.

        """

        try:
            s3 = boto3.client('s3')
            s3.upload_file(local_file, bucket, s3_file)
            print("Upload Successful")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False



    def upload_cases_to_s3(self, bucket):
        """
        Uploads downloaded cases to an S3 bucket.

        Args:
            bucket (str): The name of the S3 bucket.
        """
        s3 = boto3.client('s3')
        
        with open('casefile_names.txt', 'r') as f:
            casefile_names = f.read().splitlines()

        for filename in os.listdir(self.tmp_directory):
            if filename.endswith(".docx") and filename not in casefile_names:  
                local_file = os.path.join(self.tmp_directory, filename)
                s3_file = filename

                # Check if the file already exists in S3 before uploading
                try:
                    s3.head_object(Bucket=bucket, Key=s3_file)
                    print(f"File {s3_file} already exists in S3. Skipping upload.")
                except s3.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        # File does not exist in S3, proceed with the upload
                        self.upload_object_to_s3(local_file, bucket, s3_file)
                        casefile_names.append(filename)
                        os.remove(local_file)
                    else:
                        print(f"An error occurred checking S3: {e}")

        # Update the list of casefile names
        with open('casefile_names.txt', 'w') as f:
            for filename in casefile_names:
                f.write(filename + '\n')



