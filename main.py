import csv
import os
import time
from glob import glob
import requests
from lxml.html import fromstring
# import seleniumwire.undetected_chromedriver as uc_wire
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options

working_dir = os.getcwd()
download_dir_path = os.path.join(working_dir, 'downloaded_pdfs')
firefox_driver_path = os.path.join(working_dir, 'geckodriver.exe')
done_urls_csv_path = os.path.join(working_dir, 'done_url.csv')
if not os.path.exists(download_dir_path):
    os.mkdir(download_dir_path)


def create_firefox_driver(healdess=False):
    try:
        firefox_options = Options()
        firefox_options.set_preference("browser.download.folderList", 2)
        firefox_options.set_preference("browser.download.dir", download_dir_path)
        firefox_options.set_preference("browser.helperApps.alwaysAsk.force", False)
        firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
        firefox_options.set_preference("services.sync.prefs.sync.browser.download.manager.showWhenStarting", False)
        firefox_options.set_preference("browser.download.useDownloadDir", True)
        firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
        firefox_options.set_preference("pdfjs.disabled", True)

        driver = webdriver.Firefox(service=Service(executable_path=firefox_driver_path), options=firefox_options)

        driver.maximize_window()
        time.sleep(3)
        driver.get("https://crop.rld.nm.gov/dispensaries.html")
        return driver
    except Exception as e:
        print(e)
        print("----Got Exception----")

def write_data_in_csv_file(data_list, file_name):
    csv_file_name = os.path.join(working_dir, f'{file_name}.csv')
    exist = False
    if os.path.exists(csv_file_name):
        exist = True
    with open(csv_file_name, 'a+', newline='', encoding='utf-16') as file:
        writer = csv.writer(file, delimiter=';')
        for d in data_list:
            if not exist:
                writer.writerow(d.keys())
            writer.writerow(d.values())


def scraping():
    driver = create_firefox_driver()
    got_to_next_page = driver.find_elements(By.XPATH, "(//a[@aria-label='Go to the next page'])[1]")
    time.sleep(2)
    while got_to_next_page:
        page_source = driver.page_source
        data = fromstring(html=page_source)
        data_list = data.xpath("//div[@class='k-listview-content']/div")
        for d in data_list:
            companyName = d.xpath("./h3/text()")[0].strip()
            address = d.xpath("./div/text()")[0].replace('Address:', '').strip().replace('"', '')
            write_data_in_csv_file([{'companyName': companyName, 'Address': address}], 'scraped_data')
        time.sleep(2)
        got_to_next_page = driver.find_elements(By.XPATH, "(//a[@aria-label='Go to the next page'])[1]")
        if got_to_next_page:
            got_to_next_page[0].click()
            time.sleep(2)
    driver.quit()
if __name__ == '__main__':
    scraping()
