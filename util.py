
import re
from BeautifulSoup import BeautifulSoup, NavigableString

def textOf(soup):
	if soup == None:
		return str(None)
	elif isinstance(soup, NavigableString):
		return str(soup)
	return str(' '.join(soup.findAll(text=True)))

def stripSpaces(input):
	return re.sub('\s{2,}', ' ', input).strip()

def stripCurrency(input):
	try:
		return float(re.search('([0-9.,]+)', input).groups(1)[0].replace(",", ""))
	except:
		return 0

def fieldText(soup, descend = True):
	if soup == None:
		return None
	target = soup.parent.nextSibling.find("span") if descend else soup
	return stripSpaces(textOf(target))

