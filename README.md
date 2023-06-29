## Description
This is a Python script that automates the process of downloading case documents from the [Kenyan Law](http://kenyalaw.org/caselaw/cases/advanced_search/page/) website. I have used the Selenium library to download the case documents and the script can be modified to download as many as the executor of the code would like. 

## Usage

- Clone the repository to your local machine.
- Install the required dependencies by running the following command: `pip install -r requirements.txt`
- Download Chrome Webdriver by running `python webdriver_download.py`
- Open `main.py` and update the `base_url`, `num_pages`, and `download_directory` variables according to your requirements.
- The script will start downloading the case documents from the specified number of pages.
