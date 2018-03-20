import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime

def get_app_list(listing):
	Appliances = listing.find('Appliances')
	app_list = []
	if Appliances != None:
	    for appliance in Appliances:
	        if appliance == '\n':
	            continue
	        app_list.append(appliance.string)
	return app_list

def get_room_list(listing):
	Rooms = listing.find('Rooms')
	room_list = []
	if Rooms != None:
	    for room in Rooms:
	        if room == '\n':
	            continue
	        room_list.append(room.string)
	return room_list

def get_bathrooms(listing):
	FullBathrooms = listing.find('FullBathrooms')
	HalfBathrooms = listing.find('HalfBathrooms')
	ThreeQuarterBathrooms = listing.find('ThreeQuarterBathrooms')

	bath_dic = {1: FullBathrooms, 0.5: HalfBathrooms, 0.75: ThreeQuarterBathrooms}
	Bathrooms = 0 
	for mult, bath in bath_dic.iteritems():
	    try:
	        Bathrooms += mult * int(bath.string)
	    except:
	        continue
	return Bathrooms

if __name__ == '__main__':
	raw = requests.get('http://syndication.enterprise.websiteidx.com/feeds/BoojCodeTest.xml')
	soup = bs(raw.content, features='xml')
	df = pd.DataFrame(columns=['MlsId', 'MlsName', 'DateListed', 'StreetAddress', 'Price', 'Bedrooms', 
	                       'Bathrooms', 'Appliances', 'Rooms', 'Description'])
	i = 0
	for listing in soup.find('Listings'):
		i += 1
		# skip every other listing since it is blank (due to structure of xml in combo with soup)
		if i % 2 == 1:
		    continue

		DateListed = datetime.strptime( listing.find('DateListed').string , '%Y-%m-%d %H:%M:%S')
		# filter only listings from 2016
		if DateListed.year != 2016:
		    continue
		    
		Description = listing.find('Description').string
		# filter out listings not containing 'and' (assumes words like 'candid' that technically \
		# contain 'and' are supposed to be included)
		if 'and' not in Description.lower():
		    continue

		# get reamaining info
		MlsId = listing.find('MlsId').string
		MlsName = listing.find('MlsName').string
		StreetAddress = listing.find('StreetAddress').string
		Price = listing.find('Price').string
		Bedrooms = listing.find('Bedrooms').string
		app_list = get_app_list(listing)
		room_list = get_room_list(listing)
		Bathrooms = get_bathrooms(listing)

		# add to dataframe
		df = df.append({'MlsId': MlsId, 'MlsName': MlsName, 'DateListed': DateListed, 
		                'StreetAddress': StreetAddress, 'Price': Price, 'Bedrooms': Bedrooms, 
		                'Bathrooms': Bathrooms, 'Appliances': ', '.join(app_list), 'Rooms': ', '.join(room_list), 
		                'Description': Description[:200]}, ignore_index=True)
	    
	# sort by DateListed
	df.sort_values('DateListed')
	df.to_csv('output.csv', index=False)