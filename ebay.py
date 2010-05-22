import re
import mechanize
import sys, os
import pytz
from BeautifulSoup import BeautifulSoup
from dateutil.parser import *
from dateutil.tz import *
from datetime import *
from util import *

class LoginException(Exception): pass
class NotLoggedInException(Exception): pass
class ItemNotFoundException(Exception): pass
class IncorrectValueException(Exception): pass
class OutbidException(Exception): pass
class ParseException(Exception): pass

class EBayClient:
	TZINFOS = {
		'PDT': -25200,	# UTC-7
		'PST': -28800	# UTC-8
	}

	item_page = "http://cgi.ebay.com/ws/eBayISAPI.dll?ViewItem&item=%s"
	bid_page = "http://offer.ebay.com/ws/eBayISAPI.dll?MakeBid&item=%s"

	def __init__(self):
		self.br = mechanize.Browser(factory=mechanize.RobustFactory())

	def login(self, login, password):
		self.br.open('http://www.ebay.com/')
		self.br.set_handle_refresh(None, True)
		self.br.set_debug_redirects(True)
		self.br.set_handle_robots(False)

		try:
			response = self.br.follow_link(text_regex=re.compile(r'Sign in'), nr=0)
			assert self.br.viewing_html()
			response.close();
		except mechanize._mechanize.LinkNotFoundError:
			print "Already logged in, skipping"
			return

		self.br.select_form(name='SignInForm')
		self.br['userid'] = login
		self.br['pass'] = password
		response = self.br.submit()

		try:
			response = self.br.follow_link(text_regex=re.compile(r'Continue'))
		except mechanize._mechanize.LinkNotFoundError:
			raise LoginException("Login failed for user %s" % login)

	def getBidURL(self, item):
		return self.bid_page % item

	def getItemURL(self, item):
		return self.item_page % item

	def getItemInfo(self, item):
		try:
			self.br.open(self.getItemURL(item))
		except:
			raise ItemNotFoundException("Unable to open item page")

		page = self.br.response().read()
		m = re.match('^(.+) - eBay \(item ([0-9]+) end time (.+)\)$', self.br.title())
		(description, id, end_strtime) = m.group(1, 2, 3)
		end_time = parse(end_strtime, tzinfos=self.TZINFOS)
		now_time = datetime.now(tzlocal())

		result = dict()
		soup = BeautifulSoup(page)
		info = soup.find("form", "vi-is1-s4").find("table")
		minbid_re = "\(Enter (.+) or more\)"

		result['id']		 = item
		result['name']		 = description
		result['condition']  = fieldText(info.find(text=re.compile("Item condition")));
		result['timeleft']   = fieldText(info.find(text=re.compile("Time left")));
		result['ended']		 = fieldText(info.find(text=re.compile("Ended")));
		result['bidhistory'] = fieldText(info.find(text=re.compile("Bid history")));
		result['bid']		 = stripCurrency(fieldText(info.find(text=re.compile("(Current|Starting|Winning) bid"))))
		result['minbid']	 = stripCurrency(fieldText(info.find(text=re.compile(minbid_re)), False))
		result['shipping']	 = stripCurrency(fieldText(info.find(text=re.compile("Shipping"))))
		result['returns']	 = fieldText(info.find(text=re.compile("Returns")));
		result['timedelta']  = end_time - now_time
		result['endtime']	 = end_time.astimezone(tzlocal())
		result['isoendtime'] = end_time.isoformat()
		result['bidurl']	 = self.getBidURL(item)
		result['itemurl']	 = self.getItemURL(item)

		return result

	def bid(self, item, maxbid):
		try:
			self.br.open(self.getBidURL(item))
		except:
			raise ItemNotFoundException("Unable to open bid page")

		try:
			self.br.select_form(name='SignInForm')
			raise NotLoggedInException("Not logged in")
		except mechanize._mechanize.FormNotFoundError:
			pass

		if 'MakeBidErrorInvalidItem' in self.br.response().read():
			raise ItemNotFoundException("Item with ID %s not found" % item)

		try:
			self.br.select_form(name='PlaceBid')
		except mechanize._mechanize.FormNotFoundError, e:
			raise ParseException("Bidding form not found")

		self.br['maxbid'] = str(maxbid).replace('.', ',')
		response = self.br.submit()

		r = response.read()
		if 'must be corrected' in r:
			raise IncorrectValueException("Invalid value. Perhaps lower than the minimal bid?")

		self.br.select_form(name='PlaceBid')
		response = self.br.submit()
		r = response.read()

		if 'just been outbid' in r:
			raise OutbidException("You've just been outbid. Try to bid again")

