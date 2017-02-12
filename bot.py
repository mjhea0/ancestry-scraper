import os
import sys
import csv
from time import sleep

from selenium import webdriver


# globals

try:
    USERNAME = os.environ['ANCESTRY_USERNAME']
    PASSWORD = os.environ['ANCESTRY_PASSWORD']
except KeyError:
    print('Please set the correct environment variables')
    sys.exit(1)

NAMES = ['gates']
BASE = 'http://search.ancestry.com/cgi-bin/sse.dll?db=nypl&gss=sfs28_ms_db&new=1&rank=1&msT=1&MS_AdvCB=1&gsln={0}&gsln_x=1&MSAV=2&uidh=quk'.format(NAMES[0])


def authenticate():
    print('logging in...')
    driver = webdriver.Firefox()
    # driver = webdriver.Chrome()
    # driver = webdriver.PhantomJS()
    driver.get('https://www.ancestry.com/secure/login')
    sleep(5)
    username = driver.find_element_by_id('Username')
    password = driver.find_element_by_id('Password')
    username.send_keys(USERNAME)
    password.send_keys(PASSWORD)
    login_attempt = driver.find_element_by_xpath('//*[@type="submit"]')
    login_attempt.submit()
    sleep(5)
    welcome = driver.find_element_by_xpath('//h1[@class="pageTitle"]').text
    if 'Welcome,' in welcome:
        print('Successfully logged in!')
        sleep(5)
        return driver
    else:
        print('Something went wrong!')
        driver.quit()
        return False


def get_search_results(driver):
    print('getting records...')
    driver.get(BASE)
    records = driver.find_elements_by_css_selector("tr.record")
    if not len(records):
        print('No records!')
        driver.quit()
        return False
    else:
        for row in records:
            cell = row.find_elements_by_tag_name('td')[5].text
            if len(cell) > 1:
                row.find_elements_by_tag_name('td')[0].click()
                sleep(5)
                data = []
                for value in driver.find_elements_by_tag_name('td'):
                    data.append(value.text)
                with open('data.csv', 'a') as f:
                    w = csv.writer(f)
                    w.writerow(data)
            # sleep(5)
            # driver.quit()


if __name__ == '__main__':
    browser = authenticate()
    if browser:
        get_search_results(browser)
