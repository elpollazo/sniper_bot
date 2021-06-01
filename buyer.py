import argparse
import bs4
import time
from objects.sniper_objects import Card, Page
from objects.common import config
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options 
import numpy as np
from datetime import datetime
import logging

FORMAT = '%(asctime)-8s %(message)s'
logging.basicConfig(format=FORMAT)

def check_stock(card, page) -> bool:
    logging.warning('Checking stock...')
    options = Options()
    if args.headless == 1:
        options.headless = True

    else:
        pass

    driver = webdriver.Firefox(options=options, executable_path=r'./geckodriver')
    
    try:
        driver.get(card.url)

    except:
        logging.warning('Captched')
        card.captched = True
        driver.quit()

        return True, None

    if not bs4.BeautifulSoup(driver.page_source, 'html.parser').select('.a-button-input'):
        logging.warning('No stock, sleep time')
        driver.quit()
        
        return False, None

    elif bs4.BeautifulSoup(driver.page_source, 'html.parser').select('.a-button-input'):
        logging.warning('There is stock')

        return True, driver

    else:
        logging.warning('Connectivity-Captcha problem')
        card.captched = True
        driver.quit()

        return True, None
    
def buy_card(page, card, args, driver) -> None:
    print('buying card')
    for step in page.buy_steps:
        done = False
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

    exit()

def main(args) -> None:
    card = Card(args.card, args.page)
    card.url = args.url
    page = Page(args.page)
    print('Starting bot')
    print(f'Max price: {args.maxprice} USD')
    print(f'Dry mode: {args.drymode}')
    print(f'Headless: {args.headless}')

    while True:
        while True:
            stock = False
            init = time.time()
            while not stock:
                stock, driver = check_stock(card, page)
                if not card.captched:
                    time.sleep(abs(int(np.random.normal(10, 5, 1))))

                if time.time() - init > 60*15:
                    print('Buy timedout')
                    exit()
                    
            if not card.captched:
                args = buy_card(page, card, args, driver)
                if args.timedout:
                    break

            else: 
                card.captched = False


    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Buyer bot')
    parser.add_argument("-c", "--card", help='Type of card')
    parser.add_argument("-p", "--page", help='Buying page')
    parser.add_argument("-m", "--maxprice", help='Max price', type=float)
    parser.add_argument("-d", "--drymode", help='Dry mode bot', type=int)
    parser.add_argument("-H", "--headless", help='Headless browser', type=int)
    parser.add_argument("-t", "--timedout_time", help='Timedout time', type=int)
    parser.add_argument("-u", "--url", help='ATC url')
    args = parser.parse_args()
    main(args)