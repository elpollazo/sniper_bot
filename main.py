import argparse
import bs4
import time
from objects.sniper_objects import Card, Page, Proxy
from objects.common import config
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options 
import numpy as np
from datetime import datetime


def check_stock(card, page, proxy) -> bool:
    print('Checking stock...')
    options = Options()
    options.headless = True
    capabilities = set_capabilities(proxy.address)
    if capabilities:
        driver = webdriver.Firefox(capabilities=set_capabilities(proxy.address), options=options, executable_path=r'./geckodriver')
    
    else:
        driver = webdriver.Firefox(options=options, executable_path=r'./geckodriver')
    
    try:
        driver.get(card.url)

    except:
        print('Captched')
        card.captched = True
        driver.quit()

        return True

    if not bs4.BeautifulSoup(driver.page_source, 'html.parser').select('.a-button-input'):
        print('No stock, sleep time')
        driver.quit()
        
        return False

    elif bs4.BeautifulSoup(driver.page_source, 'html.parser').select('.a-button-input'):
        print('There is stock')
        driver.quit()

        return True

    else:
        print('Connectivity-Captcha problem')
        card.captched = True
        driver.quit()

        return True

def set_capabilities(proxy_address) -> object:
    if proxy_address[0] != '127.0.0.1':
        return None

    else:
        firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = True

        firefox_capabilities['proxy'] = {
            "proxyType": "MANUAL",
            "httpProxy": proxy_address,
            "ftpProxy": proxy_address,
            "sslProxy": proxy_address
        }

        return firefox_capabilities
    
def buy_card(page, card, args) -> None:
    print('buying card')
    args.timedout = False
    options = Options()
    if args.headless == 1:
        options.headless = True

    else:
        pass

    driver = webdriver.Firefox(options=options, executable_path=r'./geckodriver')
    driver.get(card.url)
    for step in page.buy_steps:
        done = False
        count = 0
        init = time.time()
        while not done:
            try:
                if step['type'] == 'button':
                    driver.find_element_by_class_name(step['class']).click()

                elif step['type'] == 'text':
                    driver.find_element_by_name(step['class']).send_keys(step['key'])

                elif step['type'] == 'xpath':
                    driver.find_element_by_xpath(step['class']).click()

                if step['comment']:
                    print(step['comment'])
                
                done = True

            except:
                if time.time() - init > args.timedout_time:
                    print('Timedout')
                    args.timedout = True

                    return args

                else:
                    print('NoSuchElementException, retrying')
                    time.sleep(1)

    done = False
    init = time.time()
    print('Getting price')
    while not done:
        try:
            price_label = bs4.BeautifulSoup(driver.page_source, 'html.parser').select('.a-text-right.a-text-bold')[1].text
            done = True

        except:
            if time.time() - init > args.timedout_time:
                print('Timedout')
                args.timedout = True

                return args

    price = float(price_label.replace('\n', '').replace('USD', '').replace(' ','').replace(',', ''))
    if price > args.maxprice:
        print(f'Current price is USD {price}, max price addmited is {args.maxprice}')
        print('Shutting down')

        return args
    
    else:
        if args.drymode == 0:
            driver.find_element_by_class_name('a-button-text.place-your-order-button').click()

        else:
            pass

    print('buying process done')
    time.sleep(5)
    driver.quit()

    return args

def parse_proxies():
    with open('./proxy/proxies.txt', 'r') as f:
        lines = [line.split()[0] for line in f]

    return lines


def main(args) -> None:
    card = Card(args.card, args.page)
    page = Page(args.page)
    print('Starting bot')
    print(f'Max price: {args.maxprice} USD')
    print(f'Dry mode: {args.drymode}')
    print(f'Headless: {args.headless}')
    print('Loading proxies')
    proxy_address = parse_proxies()
    if not proxy_address:
        proxy_address = ['127.0.0.1']

    while True:
        for address in proxy_address:
            proxy = Proxy(address)
            print(f'Setting proxy to {proxy.address}')
            stock = False
            while not proxy.captched:
                while not stock:
                    stock = check_stock(card, page, proxy)
                    if not card.captched:
                        time.sleep(abs(int(np.random.normal(10, 5, 1))))
                
                if not card.captched:
                    args = buy_card(page, card, args)
                    if args.timedout:
                        break

                else: 
                    proxy.captched = True
                    card.captched = False


    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Buyer bot')
    parser.add_argument("-c", "--card", help='Type of card')
    parser.add_argument("-p", "--page", help='Buying page')
    parser.add_argument("-m", "--maxprice", help='Max price', type=float)
    parser.add_argument("-d", "--drymode", help='Dry mode bot', type=int)
    parser.add_argument("-H", "--headless", help='Headless browser', type=int)
    parser.add_argument("-t", "--timedout_time", help='Timedout time', type=int)
    args = parser.parse_args()
    main(args)