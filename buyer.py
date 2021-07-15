import argparse
import bs4
import time
from objects.sniper_objects import Card, Page
from objects.common import config
from selenium import webdriver
from selenium.webdriver.firefox.options import Options 
import numpy as np
import logging
import os
from main import set_stock, get_stock, get_captcha

FORMAT = '%(asctime)-8s %(message)s'
logging.basicConfig(format=FORMAT)

def check_stock(card, page, args) -> bool:
    """This function checks the availability of stock. If stock is available it will return the driver and bool True value."""
    logging.warning('Checking stock...')
    options = Options()
    if args.headless == 1:
        options.headless = True

    driver = webdriver.Firefox(options=options, executable_path=r'./geckodriver')    
    try:
        driver.get(card.url)
        with open('captcha.html', 'w') as f:
            f.write(driver.page_source)

    except:
        logging.warning('Failed to get request')
        card.captched = True
        driver.quit()

        return True, None

    if bs4.BeautifulSoup(driver.page_source, 'html.parser').select('.a-last'):
        if bs4.BeautifulSoup(driver.page_source, 'html.parser').select('.a-last')[0].text == config()[page.name]['captcha']['text']:
            logging.warning("Captched")
            card.captched = True
            driver.quit()
            if not get_captcha():
                send_captcha("True")

            return True, None

    elif not bs4.BeautifulSoup(driver.page_source, 'html.parser').select('.a-button-input'):
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
    """This function will do the buying process when the bot finds stock."""
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

def send_pid():
    """This funcion modifies the file ./data/pid_process to the current pid of the bot when it finds stock."""
    with open("./data/pid_process", "w") as f:
        f.write(str(os.getpid()))

def send_captcha(value):
    """If the bot is captched this function will modify the value of ./data/captcha to 'True'."""
    with open("./data/captcha", "w") as f:
        f.write(value)

def main(args) -> None:
    """Main function of buyer bot. It will start a loop to continously search stock and when it is available will start the buying process."""
    os.system(f'mv ./outputs/output{args.output} ./outputs/{os.getpid()}') #Renaming the output file to the current process ID
    card = Card(args.card, args.page)
    card.url = args.url
    page = Page(args.page)
    print(f'Checking Stock for {card.url}')
    args.headless = 1
    args.maxprice = float(config()[args.page]['maxprice'])
    args.drymode = config()[args.page]['drymode']
    args.timedout_time = int(config()[args.page]['timedout_time'])
    while True:
        while True:
            stock = False
            init = time.time()
            while not stock:
                stock, driver = check_stock(card, page, args)
                if not card.captched and not stock:
                    time.sleep(abs(int(np.random.normal(10, 5, 1))))

                if time.time() - init > 60*5:
                    print('Buy timedout')
                    set_stock("False")
                    args.headless = 1
                    
            if not card.captched:
                if args.headless != int(config()[args.page]['headless']):
                    args.headless = int(config()[args.page]['headless'])

                if not get_stock():
                    send_pid()
                    set_stock("True")

                args = buy_card(page, card, args, driver)
                if args.timedout:
                    break

            else: 
                card.captched = False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Buyer bot')
    parser.add_argument("-c", "--card", help='Type of card')
    parser.add_argument("-p", "--page", help='Buying page')
    parser.add_argument("-u", "--url", help='ATC url')
    parser.add_argument("-o", "--output", help='Number of output file')
    args = parser.parse_args()
    main(args)
