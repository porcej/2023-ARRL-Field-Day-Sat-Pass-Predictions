from skyfield.api import load, wgs84
from datetime import datetime, timedelta
from pytz import timezone
import os

eastern = timezone('US/Eastern')
ts = load.timescale()


###############################################################################
# Settings

# Position on Earth of the observer
# Fairfax City, VA - +38.8498876,-77.2780489
# Alexandria, VA - 38.8212785,-77.082475
# Location:       Alexandria VA USA
# Latitude:       38.766970°
# Longitude:      -77.151200°
 # Camp Snyder - 38.8287618,-77.666188
myPos = wgs84.latlon(38.8287618,-77.666188)

# Start Time for observations
# t0 = ts.now()
t0 = ts.utc(2023, 7, 21, 10)

# End Time for observations
t1 = t0 + timedelta(hours=14)
# t1 = ts.utc(2023, 7, 21, 22)

# Satellites to observe
theseSats = [
    # "AO-109",
    "AO-07",
    "AO-91",
    "CAS-4B",
    "EO-88",
    "IO-117",
    "IO-86",
    "ISS",
    "JO-97",
    "LILACSAT-2",
    "PO-101",
    "RS-44",
    "Tevel-1",
    "Tevel-2",
    "Tevel-3",
    "Tevel-4",
    "Tevel-5",
    "Tevel-6",
    "XW-2B",
    "XW-2C",
    "XW-2D",
    "XW-2E",
    "XW-2F"
]

# Minumum elevation of pass to include, in degrees
min_elevation = 1

# satUrl = 'http://celestrak.com/NORAD/elements/active.txt'
satUrl = 'https://www.amsat.org/tle/current/dailytle.txt'

# End Settings
###############################################################################


class SatPass:
    def __init__ (self, satName, startTime, inEclipse=False):
        self.satellite = satName
        self.startTime = startTime
        self.endTime = ""
        self.maxTime = ""
        self.maxEl = ""
        self.inEclipse = inEclipse

    def max(self, maxTime, elevation, inEclipse):
        self.maxTime = maxTime
        self.maxEl = elevation
        self.inEclipse = self.inEclipse or inEclipse

    def end(self, endTime, inEclipse):
        self.endTime = endTime
        self.inEclipse = self.inEclipse or inEclipse

    def duration(self):
        return self.endTime.utc_datetime() - self.startTime.utc_datetime()

    def durationStr(self):
        secs = self.duration().total_seconds()
        mins = secs / 60
        secs = (mins % 60)
        return "%0.0f Minutes %.0f Seconds" % (mins, secs)

    def toTab(self):
        duration = self.endTime - self.startTime
        state = "*Possible Eclipse*" if self.inEclipse else ""
        return "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
                self.startTime.astimezone(eastern).strftime('%Y %b %d %H:%M:%S'),
                self.maxTime.astimezone(eastern).strftime('%Y %b %d %H:%M:%S'),
                self.endTime.astimezone(eastern).strftime('%Y %b %d %H:%M:%S'),
                self.satellite,
                self.maxEl,
                self.durationStr(),
                state
            ) 
    def toCsv(self):
        duration = self.endTime - self.startTime
        state = "*Possible Eclipse*" if self.inEclipse else ""
        return "%s,%s,%s,%s,%s,%s,%s" % (
                self.startTime.astimezone(eastern).strftime('%Y %b %d %H:%M:%S'),
                self.maxTime.astimezone(eastern).strftime('%Y %b %d %H:%M:%S'),
                self.endTime.astimezone(eastern).strftime('%Y %b %d %H:%M:%S'),
                self.satellite,
                self.maxEl,
                self.durationStr(),
                state
            )

    def toTabUTC(self):
        duration = self.endTime - self.startTime
        state = "*Possible Eclipse*" if self.inEclipse else ""
        return "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
                self.startTime.utc_strftime('%Y %b %d %H:%M:%S'),
                self.maxTime.utc_strftime('%Y %b %d %H:%M:%S'),
                self.endTime.utc_strftime('%Y %b %d %H:%M:%S'),
                self.satellite,
                self.maxEl,
                self.durationStr(),
                state
            ) 
    def toCsvUTC(self):
        duration = self.endTime - self.startTime
        state = "*Possible Eclipse*" if self.inEclipse else ""
        return "%s,%s,%s,%s,%s,%s,%s" % (
                self.startTime.utc_strftime('%Y %b %d %H:%M:%S'),
                self.maxTime.utc_strftime('%Y %b %d %H:%M:%S'),
                self.endTime.utc_strftime('%Y %b %d %H:%M:%S'),
                self.satellite,
                self.maxEl,
                self.durationStr(),
                state
            )

event_start = 0
event_peak = 1
event_end = 2



sats = load.tle_file(satUrl)
print("Start of Pass\tMax Elevation Time\tEnd of Pass\tSatellite\tMax Elevation\tPass Duration\tNotes")



satNames = {sat.name: sat for sat in sats}
for thisSat in theseSats:
    sat = satNames[thisSat]
    t, events = sat.find_events(myPos, t0, t1, altitude_degrees = min_elevation)


    eph = load('de421.bsp')
    sunlit = sat.at(t).is_sunlit(eph)
    diff = sat - myPos
    topocentric = diff.at(t)
    satPos = topocentric.altaz()
    alt, az, distance = topocentric.altaz()


    satPasses = []

    for ti, event, sunlit_flag, alti in zip(t, events, sunlit, alt.degrees):
        if (event == event_start):
            satPass =  SatPass(thisSat, ti, not sunlit_flag)
        elif (event == event_end):
            satPass.end(ti, not sunlit_flag)
            satPasses.append(satPass)
        else:
            satPass.max(ti, "%.2f°" % alti, not sunlit_flag)


    for satPass in satPasses:
        print(satPass.toTab())

tleFile = "dailytle.txt"
if os.path.isfile(tleFile):
    os.remove(tleFile)
