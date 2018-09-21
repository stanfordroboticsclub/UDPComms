#!/usr/bin/env python

import gps
from UDPComms import Publisher

# GPS example code from 
# https://learn.adafruit.com/adafruit-ultimate-gps-on-the-raspberry-pi/using-your-gps
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

fields = "time lat lon alt error_lat error_lon error_alt"
format_ = "i3f3f"
port = 8851
pub = Publisher(fields, format_, port)

while True:
    try:
    	report = session.next()
		# Wait for a 'TPV' report
        if report['class'] == 'TPV':
            # TODO: get time
            pub.send(0 ,report.lat,report.lon,report.alt,
                         report.epx, report.epy, report.epv)

    except AttributeError:
		pass
    except KeyError:
		pass
    except KeyboardInterrupt:
		quit()
    except StopIteration:
		session = None
		print "GPSD has terminated"

