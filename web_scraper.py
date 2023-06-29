from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException


class CaseLawDownloader:
    def __init__(self, base_url, num_pages, download_directory):
        self.base_url = base_url
        self.num_pages = num_pages
        self.download_directory = download_directory
        self.driver = None

    def setup_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('prefs', {'download.default_directory': self.download_directory})
        self.driver = webdriver.Chrome(options=chrome_options)

    def teardown_driver(self):
        self.driver.quit()

    def download_cases(self):
        if not self.driver:
            self.setup_driver()

        for page_num in range(1, self.num_pages + 1):
            url = self.base_url + str(page_num) + "/"
            self.driver.get(url)

            read_more_buttons = self.driver.find_elements(By.XPATH, "//a[@class='show-more pull-right']")

            for button in read_more_buttons:
                try:
                    self.driver.execute_script("arguments[0].click();", button)

                    download_button = WebDriverWait(self.driver, 40).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[@title='Download Original Document']"))
                    )

                    self.driver.execute_script("arguments[0].click();", download_button)
                    self.driver.back()
                except StaleElementReferenceException:
                    continue

        self.teardown_driver()


# the base url which is the page 1 of the case repositories
base_url = "http://kenyalaw.org/caselaw/cases/advanced_search/page/"

# define how many web pages you want to scrape.(int) 
num_pages = 0

# directory where the downloaded files are to be stored
download_directory = ' '

downloader = CaseLawDownloader(base_url, num_pages, download_directory)
downloader.download_cases()
