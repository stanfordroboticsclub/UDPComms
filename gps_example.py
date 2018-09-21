import gps
from UDPComms import Publisher


## Totaly untested as of yet

# GPS example code from 
# https://learn.adafruit.com/adafruit-ultimate-gps-on-the-raspberry-pi/using-your-gps
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

fields = "time lat lon alt sats"
format_ = "ifffi"
port = 8851
pub = Publisher(fields, format_, port)

while True:
    try:
    	report = session.next()
		# Wait for a 'TPV' report and display the current time
		# To see all report data, uncomment the line below
		# print report
        if report['class'] == 'TPV':

            time = 0
            if hasattr(report, 'time'):
                time = int(report.time)

            latitude = 0
            if hasattr(report, 'latitude'):
                latitude = report.latitude

            longitude = 0
            if hasattr(report, 'longitude'):
                longitude = report.longitude

            altitude = 0
            if hasattr(report, 'altitude'):
                altitude = report.altitude

            # if hasattr(report, 'number_of_sats'):
            #     number_of_sats = int(report.number_of_sats)

            pub.send(time,latitude,longitude,altitude,0)

    except KeyError:
		pass
    except KeyboardInterrupt:
		quit()
    except StopIteration:
		session = None
		print "GPSD has terminated"

