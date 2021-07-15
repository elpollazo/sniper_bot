import argparse
import logging
import time 
import re
import os
import subprocess
from objects.common import config

"""Main script of the bot. It manages the current processes launched (1 process/link)"""

twitter_pattern = re.compile(r'https://twitter.com/.*?')
atc_pattern = re.compile(r'https://.*Quantity.*OfferListingId.*?')

FORMAT = '%(asctime)-8s %(message)s'
logging.basicConfig(format=FORMAT)

def launch_processes(atc_links, args):
    """Launchs a buyer bot in second thread to monitoring an ATC link."""
    adder = 0
    for url in atc_links:
        os.system(f'python3 buyer.py --card {args.card} --page {args.page} --url "{url}" --output {adder} > ./outputs/output{adder} 2>&1 &')
        adder += 1 

def read_data():
    """Reads the ATC links stored."""
    with open('./data/data.txt', 'r') as f:
        data = [line.split() for line in f]
        
    return [link[0] for link in data]

def set_stock(value):
    """This set a binary value (True-False) on ./data/stock. If a buyer bot finds stock available it will change this value to 'True'."""
    with open('./data/stock', 'w') as f:
        f.write(value)

def get_stock():
    """Check the value of ./data/stock"""
    with open('./data/stock', 'r') as f:
        stock = f.read()

    return stock.split()[0] == 'True'

def get_current_process():
    """This function is used to check the number current buyer bots running at time."""
    proc = subprocess.Popen(["ps -aux | grep 'buyer.py' | wc -l"], stdout=subprocess.PIPE, shell=True)
    (out, _) = proc.communicate()
    
    return int(out.decode('utf-8').split()[0]) - 2

def get_pid():
    """If stock is available, this function will retreive the pid of the bot that found stock. The pid process is stored in ./data/pid_process."""
    with open('./data/pid_process', 'r') as f:
        pid_process = f.read()

    return pid_process

def get_captcha():
    """Reads the data from ./data/captcha. If some bot gets captched it will modify this file to 'True'."""
    with open("./data/captcha", "r") as f:
        captcha = f.read()

    return captcha.split()[0] == 'True'

def main(args):
    os.system('mkdir outputs 2>/dev/null')
    atc_links= read_data()
    launch_processes(atc_links, args)
    set_stock("False")
    while True:
        try:
            while True:
                try:
                    stock = get_stock()
                
                except:
                    break
                
                if stock:
                    """killer2.sh script is used to kill all process except for the bot that finds stock."""
                    os.system(f'./killer2.sh {get_pid()}')
                    while stock:
                        processes = get_current_process()
                        logging.warning(f'Bot heartbeat. Stock: {stock}. Current processes: {processes}. Captcha: {get_captcha()}')
                        time.sleep(10)
                        try:
                            stock = get_stock()

                        except:
                            break

                processes = get_current_process()
                if (processes != len(atc_links) and processes != 1) or (processes == 1 and not get_stock()):
                    """If the number of the current processes does not match with the number of ATC links, the processes will be restarted."""
                    logging.warning('Some process may died. Restarting.')
                    os.system('./killer1.sh')
                    launch_processes(atc_links, args)

                logging.warning(f'Bot heartbeat. Stock: {stock}. Current processes: {processes}. Captcha: {get_captcha()}')
                time.sleep(10)
                
        
        except KeyboardInterrupt:
            print("Bye")
            os.system('./killer1.sh')
            os.system('rm -r ./outputs/*')
            exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Buyer bot')
    parser.add_argument("-c", "--card", help='Type of card')
    parser.add_argument("-p", "--page", help='Buying page')
    args = parser.parse_args()
    main(args)
