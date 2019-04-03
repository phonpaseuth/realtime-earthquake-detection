# https://stackoverflow.com/questions/5419888/reading-from-a-frequently-updated-file

import time
import numpy
from obspy import read, UTCDateTime
from datetime import datetime, timedelta
from display_time import display_time
import itertools # https://stackoverflow.com/questions/8671280/pythonic-way-to-iterate-over-part-of-a-list


def follow(thefile):
    thefile.seek(0,2)

    # a model
    duration = 0    # use to trigger model creation
    modelExist = False
    dataMean = 0
    dataStd = 0
    sensitivity = 5
    cut_off = 0
    lower = 0
    upper = 0

    currentIndex = 0

    outliers = []
    timestamp = []
    events=[]
    outlierIndex = 0

    while True:
        # Use to trigger changes
        if not thefile.read():
            time.sleep(0.1)
            continue

        st = read('2019/CI/HEC/BHE.D/CI.HEC..BHE.D.2019.093')
        tr = st[1]

        # Get the model for the first 5 minute
        startTime = tr.stats.starttime
        endTime = tr.stats.starttime + tr.times()[-1]
        duration = endTime - startTime
        print '\n>>> ' + str(display_time(duration)) + ' of data collected.'
        print tr.data
        if modelExist == False:
            if duration < 1800:
                continue
            else:
                print "\n*** Creating a model ***"
                data_mean = numpy.mean(tr.data)
                print "Mean: " + str(data_mean)
                data_std = numpy.std(tr.data)
                print "Standard Deviation: " + str(data_std)

                cut_off = data_std * sensitivity  # change the multiplier to affect data sensitivity
                lower = data_mean - cut_off
                upper = data_mean + cut_off
                print "Sensitivity: " + str(sensitivity)
                print "Lower: " + str(lower)
                print "Upper: " + str(upper)

                currentIndex = len(tr.data)
                modelExist = True
                continue
   
        print "*** Finding outliers ***"
        for data in tr.data[currentIndex:]:
            if data < lower or data > upper:
                outliers.append(data)
                t = datetime.utcfromtimestamp(tr.times()[currentIndex]+float(tr.stats.starttime))
                timestamp.append(t)
                events.append({"time": UTCDateTime(t)})
            currentIndex = currentIndex + 1
        print "Total number of samples: " + str(len(tr.data))
        print "Total number of outliers: " + str(len(outliers))

        if outliers[outlierIndex:]:
            sTime = timestamp[outlierIndex] - timedelta(seconds=15) 
            eTime = timestamp[len(outliers)-1] + timedelta(seconds=15)
            fileName = sTime.strftime("%c")
            st.plot(method='full', starttime=UTCDateTime(sTime), endtime=UTCDateTime(eTime), outfile=fileName)
            outlierIndex = len(outliers)

if __name__ == '__main__':
    time.sleep(45)
    logfile = open('2019/CI/HEC/BHE.D/CI.HEC..BHE.D.2019.093','r')
    follow(logfile)
