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
from python_calendar_invite.eventInvitation import send_invite
import pickle

data = requests.get('http://www.portugal-vacc.org').text
soup_document = BeautifulSoup(data, 'html.parser')

data = ""
for tr in soup_document.find_all('font', attrs = { 'face': 'Tahoma', 'size': '1', 'color': 'black' }):
	data = data + tr.text.strip('<font color="black" face="Tahoma" size="1"><b>')

#print data

p1 = re.compile('(?P<booking>LP[A-Z0-9]{2}\_[A-Z]{3}.+?[\d]{4}-[\d]{2}-[\d]{2})')
p2 = re.compile('(?P<facility>LP[A-Z0-9]{2}\_[A-Z]{3})(?P<operator>.+?)(?P<year>[\d]{4})-(?P<month>[\d]{2})-(?P<day>[\d]{2})\s(?P<starts_H>[\d]{2})(?P<starts_M>[\d]{2})z-(?P<ends_H>[\d]{2})(?P<ends_M>[\d]{2})')
p3 = re.compile('^(?P<operator>.*?)\s\[Training\]Mentor\:\s(?P<mentor>.*?)$')

# load known bookings
firstRun = True
bookings = {}
if os.path.isfile('LP.dat'):
	bookings = pickle.load(open('LP.dat', 'rb'))
	firstRun = False
else:
	bookings = {}

# collect new bookings
new_bookings = {}

# identify removed bookings
received_bookings = {}

for m1 in re.finditer(p2, data):

	# parse start and end times
	starts = datetime.datetime(int(m1.groups()[2]), int(m1.groups()[3]), int(m1.groups()[4]), int(m1.groups()[5]), int(m1.groups()[6]))
	ends = datetime.datetime(int(m1.groups()[2]), int(m1.groups()[3]), int(m1.groups()[4]), int(m1.groups()[7]), int(m1.groups()[8]))
	if starts > ends:
		ends + timedelta(days = 1)

	# generate an id
	booking_id = m1.groups()[0] + starts.strftime("%Y%m%dT%H%M%SZ")

	# check operator and mentor
	operator = ""
	mentor = ""
	training = re.search(p3, m1.groups()[1])
	if training:
		operator = training.groups()[0]
		mentor = training.groups()[1]
	else:
		operator = m1.groups()[0]

	received_bookings[booking_id] = {}

	if booking_id not in bookings:
		bookings[booking_id] = {
			'facility': m1.groups()[0],
			'operator': operator,
			'mentor': mentor,
			'starts': starts,
			'ends': ends
		}
		new_bookings[booking_id] = bookings[booking_id]

for booking in bookings.copy():
	# remove canceled bookings
	if booking not in received_bookings:
		del bookings[booking]
		continue
	# clear expired bookings
	if bookings[booking]['ends'] < datetime.datetime.now():
		del bookings[booking]

# write down the new bookings state
pickle.dump(bookings, open('LP.dat', 'wb'))

# notify of new bookings
#if not firstRun:
#	for booking in new_bookings:
if True:
	for booking in bookings:
		# generate subject and body text
		subject = ""
		body_text = ""
		if bookings[booking]['mentor'] == "":
			subject = bookings[booking]['facility'] + ' Just booked'
			body_text = bookings[booking]['operator'] + ' will be staffing ' + bookings[booking]['facility']
		else:
			subject = bookings[booking]['facility'] + ' Training session'
			body_text = bookings[booking]['operator'] + ', and it\'s mentor ' + bookings[booking]['mentor'] + ', will be in a training session at ' + bookings[booking]['facility'] 
		# complete body text
		body_text = body_text + '. Starting ' + bookings[booking]['starts'].strftime("%A, %-d %B %H%MZ") + ' untill '
		if bookings[booking]['starts'].date() == bookings[booking]['ends'].date():
			body_text = body_text + bookings[booking]['ends'].strftime("%H%MZ")
		else:
			body_text = body_text + bookings[booking]['ends'].strftime("%A, %-d %B %H%MZ")
		body_text = body_text + '.'
		
		# create email
		body = open(os.path.join('mail.html')).read()
		body = body.replace('subject', subject)
		body = body.replace('body_text', body_text)

		# create ics attachment
		ics = open(os.path.join('calendar.ics')).read()

		send_invite({
			'from': 'vAcc Monitor Monkey',
			'to': [ 'prodrigues1990@gmail.com' ],
			"subject": subject,
			"body_html": body,
			"startDate": bookings[booking]['starts'], 
			"endDate": bookings[booking]['ends'],
			"ics_file": ics})

		break