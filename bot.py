import os
import csv
import math
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
    # driver = webdriver.Firefox()
    driver = webdriver.Chrome()
    # driver = webdriver.PhantomJS()
    driver.get('https://www.ancestry.com/secure/login')
    sleep(5)
    username = driver.find_element_by_id('username')
    password = driver.find_element_by_id('password')
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


def get_search_results(driver, name):
    print('\nsearching passenger list for {0}...'.format(name))
    driver.get(BASE.format(name))
    sleep(5)
    try:
        total_records = str(driver.find_element_by_class_name(
            'w50').text).split(' ')[-1]
        total_pages = math.ceil(int(int(total_records.replace(',', ''))) / 20)
        print('...found {0} records'.format(total_records))
        return {
            'total_records': total_records,
            'total_pages': total_pages
        }
    except:
        print('...no records found for {0}'.format(name))
        return False


def get_page(driver, results, name):
    page = 1
    print('   ...getting page {0}'.format(page))
    records = driver.find_elements_by_css_selector('tr.record')
    # get first page
    get_links(driver, records, name, page, results['total_records'])
    driver.find_element_by_class_name('iconArrowBack').click()
    # get subsequent pages
    while page != results['total_pages']:
        driver.find_element_by_class_name('iconArrowRight').click()
        page += 1
        print('   ...getting page {0}'.format(page))
        records = driver.find_elements_by_css_selector('tr.record')
        get_links(driver, records, name, page, results['total_records'])
        driver.find_element_by_class_name('iconArrowBack').click()
    print('...done')
    return True


def get_links(driver, records, name, page, total):
    end = int(page) * 20
    start = (int(end) - 20) + 1
    print('      ...getting links {0} to {1} of {2}'.format(start, end, total))
    links = []
    for row in records:
        cell = row.find_elements_by_tag_name('td')[5].text
        if len(cell) > 1:
            link = row.find_element_by_tag_name('a')
            links.append(link.get_attribute('href'))
    print('      ...found {0} appropriate links'.format(len(links)))
    for link in links:
        print('         ...getting link')
        driver.get(link)
        sleep(5)
        data = []
        data.append(name)
        for value in driver.find_elements_by_tag_name('td'):
            data.append(value.text)
        with open(OUTPUT_FILE, 'a') as f:
            w = csv.writer(f)
            w.writerow(data)


if __name__ == '__main__':
    surnames = get_surnames()
    browser = authenticate()
    if browser:
        for surname in surnames:
            totals = get_search_results(browser, surname)
            if totals:
                get_page(browser, totals, surname)
        browser.quit()
