'''
Created on 14.11.2019

@author: sven.fabricius
'''

import requests
import config
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from pyzbar.pyzbar import decode
from PIL import Image
import time
import datetime
import re
from datetime import timedelta

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

codec_username = config.codec_username
codec_password = config.codec_password

sess = requests.session()

if __name__ == '__main__':
    
    while True:
        sess.post("https://192.168.1.8/web/signin/open", verify=False, data={"username": codec_username, "password": codec_password})
        response = sess.get('https://192.168.1.8/web/api/snapshot/get', verify=False) 
        #output will be binary. the encode function down below understands binary. next higher output would be encoding it in base64
        with open("tmp.jpg", "wb") as outfile:
            outfile.write(response.content)
            outfile.close()
            
        data = decode(Image.open("tmp.jpg"))
        for code in data:
            meeting = dict(item.split(":", 1) for item in code.data.decode("utf-8").splitlines())
            
            match = re.search('(?P<hours>\d)(?P<minutes>\d{2})', meeting['d'])
            minutes = int(match.group('hours')) * 60 + int(match.group('minutes'))

            start = datetime.datetime.strptime(meeting['s'], '%Y-%m-%d %H:%M:%S')
            
            # debug override
            start = datetime.datetime.utcnow()
            meeting['m'] = "linorton@cisco.com"
            minutes = 10
            
        
            
            end = start + timedelta(minutes=minutes) 
            
            xml = f'''<?xml version="1.0"?>
<Bookings item="1" status="OK">
  <Booking item="1">
    <Id item="1">1</Id>
    <Title item="1">{meeting['t']}</Title>
    <Agenda item="1"></Agenda>
    <Privacy item="1">Public</Privacy>
    <Organizer item="1">
      <FirstName item="1">Demo</FirstName>
      <LastName item="1"></LastName>
      <Email item="1"></Email>
    </Organizer>
    <Time item="1">
      <StartTime item="1">{start.strftime("%Y-%m-%dT%H:%M:%SZ")}</StartTime>
      <StartTimeBuffer item="1">300</StartTimeBuffer>
      <EndTime item="1">{end.strftime("%Y-%m-%dT%H:%M:%SZ")}</EndTime>
      <EndTimeBuffer item="1">0</EndTimeBuffer>
    </Time>
    <MaximumMeetingExtension item="1">5</MaximumMeetingExtension>
    <BookingStatus item="1">OK</BookingStatus>
    <BookingStatusMessage item="1"></BookingStatusMessage>
    <Webex item="1">
      <Enabled item="1">False</Enabled>
      <MeetingNumber item="1"></MeetingNumber>
      <Password item="1"></Password>
    </Webex>
    <Encryption item="1">BestEffort</Encryption>
    <Role item="1">Master</Role>
    <Recording item="1">Disabled</Recording>
    <DialInfo item="1">
      <Calls item="1">
        <Call item="1">
          <Number item="1">{meeting['m']}</Number>
          <Protocol item="1">SIP</Protocol>
          <CallRate item="1">6000</CallRate>
          <CallType item="1">Video</CallType>
        </Call>
      </Calls>
      <ConnectMode item="1">OBTP</ConnectMode>
    </DialInfo>
  </Booking>
</Bookings>'''
            res = sess.post("https://192.168.1.8/bookingsputxml", verify=False, data=xml, headers={'Content-Type': 'text/xml'})
            
        sess.get("https://192.168.1.8/web/signin/signout", verify=False)
        time.sleep(5)
        

        