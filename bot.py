import os
import sys
import csv
from time import sleep

from selenium import webdriver


# globals

USERNAME = os.getenv('ANCESTRY_USERNAME', None)
PASSWORD = os.getenv('ANCESTRY_PASSWORD', None)
INPUT_FILE = os.path.join('data', 'surnames.txt')
OUTPUT_FILE = os.path.join('data', 'data.csv')
BASE = 'http://search.ancestry.com/cgi-bin/sse.dll?db=nypl&gss=sfs28_ms_db&new=1&rank=1&msT=1&MS_AdvCB=1&gsln={0}&gsln_x=1&MSAV=2&uidh=quk'


# functions

def get_surnames():
    data = []
    with open(INPUT_FILE) as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row[0])
        return data


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
        print('successfully logged in')
        sleep(5)
        return driver
    else:
        print('something went wrong')
        driver.quit()
        return False


def get_search_results(driver, array):
    driver.get(BASE)
    for surname in array:
        print('searching passenger list for {0}...'.format(surname))
        driver.get(BASE.format(surname))
        sleep(5)
        records = driver.find_elements_by_css_selector('tr.record')
        if not len(records):
            print('no records found for {0}'.format(surname))
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
                    with open(OUTPUT_FILE, 'a') as f:
                        w = csv.writer(f)
                        w.writerow(data)
                        print('...done')
                        break
    driver.quit()


if __name__ == '__main__':
    surnames = get_surnames()
    browser = authenticate()
    if browser:
        get_search_results(browser, surnames)
