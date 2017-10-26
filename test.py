import urllib2
import re
from bs4 import BeautifulSoup as Soup

site= "https://www.nespresso.com/pro/fr/fr/product/ristretto-intenso-boite-capsule-cafe"
hdr = {'User-Agent': 'Mozilla/5.0'}
req = urllib2.Request(site,headers=hdr)
page = urllib2.urlopen(req)
soup = Soup(page, 'html.parser')

#for ultag_family in  soup.find_all('ul', class_="coffee-family-tile"):
#   for litag_family in ultag_family.find_all('li'):
#       print litag_family.text

for span in  soup.find_all('span', class_="nes_list-price"):
       for coffee_price in span.find_all('span'):
	   coffee_price_modified = re.sub(r'[^0-9,]*', '',coffee_price.text)
           coffee_price_modified_decimal = re.sub(r',', '.',coffee_price_modified)
           print float(coffee_price_modified_decimal)

#print family_ul
#print grid_ul
