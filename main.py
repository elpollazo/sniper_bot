from selenium import webdriver
import bs4
import re
import requests
import json
import time
from selenium.webdriver.firefox.options import Options
from objects.common import config 
import argparse
import os
import logging

FORMAT = '%(asctime)-8s %(message)s'
logging.basicConfig(format=FORMAT)

stock_pattern = re.compile(r'https://twitter.*?')
atc_pattern = re.compile(r'https://.*Quantity.*OfferListingId.*?')

def retreive_messages(channel_id, auth):
	headers = {
	'authorization': auth
	}
	done = False
	while not done:
		try:
			r = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages?limit=1', headers=headers)
			response = json.loads(r.text)
			done = True

		except:
			print('Resting')
			time.sleep(10)

	return response[0]['content']

def check_stock(args):
	channel_id = config()[args.page]['cards'][args.card]['channel_id']
	auth = config()[args.page]['discord_auth']
	latest_message = retreive_messages(channel_id, auth)
	new_message = retreive_messages(channel_id, auth)
	while latest_message == new_message or not stock_pattern.match(new_message):
		logging.warning('No stock')
		time.sleep(10)
		new_message = retreive_messages(channel_id, auth)

	url = new_message.split()[0]
	print(f'New url found: {url}')

	return url

def get_atc_url(twitter_url, args):
	print('Getting ATC url')
	options = Options()
	options.headless = True
	driver = webdriver.Firefox(executable_path = r'./geckodriver', options=options)
	driver.get(twitter_url)
	done = False
	while not bs4.BeautifulSoup(driver.page_source, 'html.parser').select(config()[args.page]['atc_class']):
		pass

	soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
	driver.quit()
	for element in soup.select(config()[args.page]['atc_class']):
		if atc_pattern.match(element.text):

			return element.text

		else:
			continue

def buy_card(atc_url):
	print('Buying card')
	os.system(f'python3 buyer.py --card {args.card} --page {args.page} --drymode {config()[args.page]["drymode"]} --headless {config()[args.page]["headless"]} --maxprice {config()[args.page]["maxprice"]} --timedout_time {config()[args.page]["timedout_time"]} --url "{atc_url}"')

def main(args):
	atc_urls = []
	logging.warning('Starting bot')
	while True:
		twitter_url = check_stock(args)
		atc_url = get_atc_url(twitter_url, args)
		if atc_url not in atc_urls:
			print(f'New ATC url found: {atc_url}')
			atc_urls.append(atc_url)
			buy_card(atc_url)

		else:
			print('not new ATC')			

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Main script')
	parser.add_argument("-c", "--card", help='Type of card')
	parser.add_argument("-p", "--page", help='Type of card')
	args = parser.parse_args()
	main(args)