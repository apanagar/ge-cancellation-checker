#!/usr/bin/python

# Note: for setting up email with sendmail, see: http://linuxconfig.org/configuring-gmail-as-sendmail-email-relay

from subprocess import check_output
from datetime import datetime
from os import path
import sys, smtplib, json, os
from twilio.rest import TwilioRestClient

PWD = os.path.abspath(os.path.dirname(__file__))
PHANTOMJS_PATH = '/home/ajay/node_modules/phantomjs/lib/phantom/bin' 
if not os.path.isfile(PHANTOMJS_PATH + '/phantomjs'):
    print 'Path to phantomjs is incorrect'
    sys.exit()

import urllib2
# Get settings
try:
    with open('%s/config.json' % PWD) as json_file:    
        settings = json.load(json_file)
except Exception as e:
    print 'Error extracting config file: %s' % e
    sys.exit()

# Make sure we have all our settings
if not 'current_interview_date_str' in settings or not settings['current_interview_date_str']:
    print 'Missing current_interview_date_str in config'
    sys.exit()
if not 'email_from' in settings or not settings['email_from']:
    print 'Missing from address in config'
    sys.exit()
if not 'email_to' in settings or not settings['email_to']:
    print 'Missing to address in config'
    sys.exit()
if not 'init_url' in settings or not settings['init_url']:
    print 'Missing initial URL in config'
    sys.exit()
if not 'enrollment_location_id' in settings or not settings['enrollment_location_id']:
    print 'Missing enrollment_location_id in config'
    sys.exit()
if not 'username' in settings or not settings['username']:
    print 'Missing username in config'
    sys.exit()
if not 'password' in settings or not settings['password']:
    print 'Missing password in config'
    sys.exit()

CURRENT_INTERVIEW_DATE = datetime.strptime(settings['current_interview_date_str'], '%b %d, %Y')

def log(msg):
    print msg

    if not 'logfile' in settings or not settings['logfile']: return
    with open(settings['logfile'], 'a') as logfile:
        logfile.write('%s: %s\n' % (datetime.now(), msg))

def send_sms(current_apt, avail_apt):
    account = "AC00aff63b55e765a3929552f185210e99"
    token = "a2f0aa4af99682a3e9c775cfa439803e"
    client = TwilioRestClient(account, token)
    from_phone = "+15713162774"
    to_phone = settings['sms_to']

    msg_str = 'Appt available on ' + avail_apt

    message = client.messages.create(to = to_phone,
                                    from_ = from_phone,
                                    body = msg_str)

#sys.exit(0)

new_apt_str = check_output(['%s/phantomjs' % PHANTOMJS_PATH, '%s/ge-cancellation-checker.phantom.js' % PWD]); # get string from PhantomJS script - formatted like 'July 20, 2015'
new_apt_str = new_apt_str.strip()

try: 
    new_apt = datetime.strptime(new_apt_str, '%B %d, %Y')
except ValueError as e:
    print new_apt_str
    log('Error - %s' % new_apt_str)
    sys.exit()

#send_sms(CURRENT_INTERVIEW_DATE, new_apt_str)
if new_apt < CURRENT_INTERVIEW_DATE: # new appointment is newer than existing!
    send_sms(CURRENT_INTERVIEW_DATE, new_apt_str)
    log('Found: %s (current is on %s)!' % (new_apt_str, settings['current_interview_date_str']))
else:
    log('None. Next on %s (current %s)' % (new_apt_str, settings['current_interview_date_str']))
