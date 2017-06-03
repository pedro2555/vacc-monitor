#!/usr/bin/env python
"""
vAcc Monitor
Copyright (C) 2017  Pedro Rodrigues <prodrigues1990@gmail.com>

This file is part of vAcc Monitor.

ACARS API is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 2 of the License.

ACARS API is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with vAcc Monitor.  If not, see <http://www.gnu.org/licenses/>.
"""

from bs4 import BeautifulSoup
import requests
import re
import os
import datetime

data = requests.get('http://www.portugal-vacc.org').text
soup_document = BeautifulSoup(data, 'html.parser')

# for soup_tables in soup_document.find('table'):
# 	soup_table = soup_tables
# 	print(soup_table.find_all(text = 'Forecasted ATC'))

data = ""
for tr in soup_document.find_all('font', attrs = { 'face': 'Tahoma', 'size': '1', 'color': 'black' }):
	data = data + tr.text.strip('<font color="black" face="Tahoma" size="1"><b>')

#print data

p1 = re.compile('(?P<booking>LP[A-Z0-9]{2}\_[A-Z]{3}.+?[\d]{4}-[\d]{2}-[\d]{2})')
p2 = re.compile('(?P<facility>LP[A-Z0-9]{2}\_[A-Z]{3})(?P<operator>.+?)(?P<year>[\d]{4})-(?P<month>[\d]{2})-(?P<day>[\d]{2})\s(?P<starts_H>[\d]{2})(?P<starts_M>[\d]{2})z-(?P<ends_H>[\d]{2})(?P<ends_M>[\d]{2})')

for m1 in re.finditer(p2, data):
	starts = datetime.datetime(int(m1.groups()[2]), int(m1.groups()[3]), int(m1.groups()[4]), int(m1.groups()[5]), int(m1.groups()[6]))
	ends = datetime.datetime(int(m1.groups()[2]), int(m1.groups()[3]), int(m1.groups()[4]), int(m1.groups()[7]), int(m1.groups()[8]))
	if starts > ends:
		ends + timedelta(days=1)

	print m1.groups()[0] + " starts: " + starts.strftime("%A, %d. %B %Y %I:%M%p") + " ends: " + ends.strftime("%A, %d. %B %Y %I:%M%p")
	break
	# m2 = re.search(p2, match)

	# d = datetime.datetime(int(match.groups('year')), int(match.groups('month')), int(match.groups('day')))
	# print d.strftime("%A %d. %B %Y")

print "ok"