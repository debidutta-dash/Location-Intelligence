
from fileinput import filename
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
import pandas as pd

import sys

category = sys.argv[1]
region = sys.argv[2]

query = category + " in " + region


# query = 'Apartment in Whitefield, Bengaluru'

# category = 'Apartment'
# region = 'Whitefield, Bengaluru'


def scroll_down(driver):
    # scrolling_element_xpath = '/html/body/div[3]/div[9]/div[8]/div/div[1]/div/div/div[2]/div[1]'
    scrolling_element = driver.find_element_by_xpath(
        "//div[@aria-label='%s']" % (scrollbar_str))

    last_height = driver.execute_script(
        "return arguments[0].scrollHeight", scrolling_element)
    # print(last_height)

    SCROLL_PAUSE_TIME = 2.0  # pause before next scroll, to let page load
    t = 0  # number of times we have scrolled

    # Loop the scrolling until cannot scroll anymore
    while True:
        print("Scrolling down")

        # Scroll down to bottom of whatever is currently loaded

        driver.execute_script(
            'arguments[0].scrollTo(0, arguments[0].scrollHeight)', scrolling_element)
        t = t+1

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Check if more scrolling required
        new_height = driver.execute_script(
            "return arguments[0].scrollHeight", scrolling_element)
        # print(new_height)
        if new_height == last_height:
            print("Reached the end of this page")
            break
        last_height = new_height

# driver = webdriver.Chrome('chromedriver.exe')


chrome_options = Options()
# chrome_options.add_argument("--disable-extensions")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox") # linux only
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
# driver.maximize_window()


driver.get("https://www.google.com/maps")


store_location = driver.find_element_by_xpath(
    "//input[@aria-label= 'Search Google Maps']")


print("Searching for ", query)

scrollbar_str = "Results for "+query


results = []

store_location.send_keys(query)
time.sleep(2)
store_location.send_keys(Keys.RETURN)

time.sleep(20)


c = 1
while True:
    elm = driver.find_element_by_xpath("//button[@aria-label=' Next page ']")
    if elm.get_attribute("disabled") == None:
        print("On page ", c)

        scroll_down(driver)

        time.sleep(10)

        page = BeautifulSoup(driver.page_source, 'html.parser')
        time.sleep(5)
        all_urls = (page.find_all("a", {"class": "hfpxzc"}))

        print("Fetched ", len(all_urls), " rows from this page")
        for i in range(len(all_urls)):
            t = all_urls[i]['href']
            results.append(t)

        elm.click()
        time.sleep(12)

        c += 1
    else:

        scroll_down(driver)

        time.sleep(3)

        page = BeautifulSoup(driver.page_source, 'html.parser')
        time.sleep(5)
        all_urls = (page.find_all("a", {"class": "hfpxzc"}))

        print("Fetched ", len(all_urls), " rows from this page")
        for i in range(len(all_urls)):
            t = all_urls[i]['href']
            results.append(t)

        break


print("Fetched ", len(results), " rows in total")
time.sleep(2)
driver.close()


scraped_data = []
for k in range(len(results)):
    # print(k)
    str_url = results[k]
    name = str_url.split("place")[1].split(
        "data")[0].replace('/', '').replace('+', ' ')
    lat_regex = re.compile('3d\d\d\.[0-9]+')
    lat = float(re.findall(lat_regex, str_url)[0][2:])
    lon_regex = re.compile('4d\d\d\.[0-9]+')
    lon = float(re.findall(lon_regex, str_url)[0][2:])
    row = {
        'Place_name': name,
        'Latitude': lat,
        'Longitude': lon,
        'Category': category,
        'Region': region
    }
    scraped_data.append(row)

df = pd.DataFrame(scraped_data)

filename = query+".csv"
df.to_csv(filename, index=False)
