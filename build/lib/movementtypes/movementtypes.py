# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from pyproj import Proj, transform
import math
import sskernel
import requests
import xml.etree.ElementTree as ET

class mvtypes:
    """
    This package try to properly categorized the movement type of gps trace over a period of time.

    *CSV format*

        :header line:
            CSV file prefer header line to this order ["id", "lat", "lng", "alt", "time", ...],

            so the file looks like

            line1|id,lat,lng,alt,time,photoname

            line2|1,24.3899016667,120.760261667,462.1,2013-12-24 07:54:23,IMGP4388.JPG

            ...

        :lat, lng:
            if your position information is DMS format(Degrees, minutes and seconds),

            you need to convert to decimal degrees

        :time:
            this value can be YYYY-MM-DD hh:mm:ss or ISO 8601 date and time format


    """
    def __init__(self, path, threshold=15, inEPSG=4326, outEPSG=3857):
        """
        Constructor. Set up the class variables, cluster the trace and deal with the missing value.

        You can set threshold, EPSG code of trace data and EPSG code for output.

        If you want to try another projection, here is a reference you can search from it.

        http://epsg.io/

        :param path: path of csv file
        :param threshold: 15 minutes
        :param inEPSG: default is 4326, the EPSG code identifier of WGS84
        :param outEPSG: default is 3857, the EPSG code identifier of
        """

        # transform(Proj(init='epsg:4326'), Proj(init='epsg:3857'), -0.1285907, 51.50809)

        self.data = pd.read_csv(path)
        self.vecList = [0 for i in range(self.data.shape[0])]
        self.threshold = threshold
        self.velocity = 0
        self.inRef = Proj(init='epsg:{}'.format(inEPSG))
        self.outRef = Proj(init='epsg:{}'.format(outEPSG))
        self.cluster = []
        self.cls_number = 1
        self.classifyNum = 5
        self.opt = None
        self.result = []

        self.clusterBySetting()
        self.cleanMissingData()

    def export_csv(self, path):
        """
        Export the dataframe to csv.

        :param path: output path of file
        :return: None
        """
        self.data.to_csv(path, index=False)


    def clusterBySetting(self):
        """
        Choosing a constant threshold (default is 15 minutes) to partition the event sequence into different cluster.

        :return: None
        """
        init = pd.to_datetime(self.data.iloc[0, 4])
        for i, r in enumerate(self.data.itertuples()):
            if pd.Timedelta(pd.to_datetime(r.time)-init)/pd.Timedelta('1 minutes') > self.threshold:
                self.cls_number += 1

            self.cluster.append(self.cls_number)
            init = pd.to_datetime(r.time)

        self.data['cluster'] = self.cluster

    def cleanMissingData(self):
        """
        This process will deal with the position of an event is missing or erroneous.

        :return: None
        """
        clusterList = self.data['cluster'].unique()

        for c in clusterList:
            clusterDf = self.data[self.data['cluster'] == c]
            rmDf = []
            for i, r in enumerate(clusterDf.itertuples()):
                if (i == 0):
                    continue

                if (r.lat == clusterDf.iloc[i - 1].lat or r.lng == clusterDf.iloc[i - 1].lng):
                    rmDf.append(i)
                elif (r.lat == 0):
                    rmDf.append(i)

            clusterDf = clusterDf.drop(clusterDf.index[[rmDf]])
            for i, r in enumerate(clusterDf.itertuples()):
                if (i == 0 or i == clusterDf.shape[0] - 1):
                    continue

                velocity = self.calVelocity(clusterDf.iloc[i - 1], r, clusterDf.iloc[i + 1])
                self.vecList[r.Index] = velocity

        self.data['velocity'] = self.vecList

    def calVelocity(self, pre, init, nexti):
        """
        Usage: df.calVelocity(df.data.iloc[17], df.data.iloc[18][:-1], df.data.iloc[19])

        :param pre: index of mvtypes pre data
        :param init: index of mvtypes data
        :param nexti: index of mvtypes next data
        :return: point of velocity(unit: km/hr)
        """
        pinit = transform(self.inRef, self.outRef, init.lng, init.lat)
        pre_pinit = transform(self.inRef, self.outRef, pre.lng, pre.lat)
        next_pinit = transform(self.inRef, self.outRef, nexti.lng, nexti.lat)

        vector = [next_pinit[0] - pinit[0],
                  next_pinit[1] - pinit[1],
                  pinit[0] - pre_pinit[0],
                  pinit[1] - pre_pinit[1]]
        perhour = pd.Timedelta(pd.to_datetime(nexti.time) - pd.to_datetime(pre.time)) / \
                  pd.Timedelta('1 hours')
        vector_length = math.hypot(vector[0], vector[1]) + math.hypot(vector[2], vector[3])

        return vector_length/perhour/1000

    def optbwKDE(self):
        """
        This results is using the KDE module to choose an optimal bandwidth and help us to get some ideas of the distribution of speeds.

        :return: the number of the movement types
        """
        x = np.array(self.vecList)
        y = np.array(self.data['time'])
        t = np.linspace(0, math.floor(np.nanmax(x)), math.floor(np.nanmax(x))*2)

        self.opt = sskernel.sskernel(x, tin=t, bootstrap=True)
        # self.opt = sskernel(x, tin=t)

        localmin = []
        localtemp = 1
        for i in self.opt['y']:
            if len(localmin) == 0:
                localmin.append(0)
                localtemp = i
            else:
                e = 1 if i > localtemp else -1
                localmin.append(e)
                localtemp = i

        pre = 0
        localmin_all = []

        for index, i in enumerate(localmin):
            if i == -1:
                pre = -1
            else:
                if pre == -1 and i > pre:
                    localmin_all.append([self.opt['t'][index], self.opt['y'][index]])
                    pre = 0

        self.result = []
        for i, r in enumerate(localmin_all):
            if i < self.classifyNum:
                self.result.append(r[0])

        # return self.result
        return localmin_all

    def classifySpeed(self):
        """
        Add the column 'velocity'

        :return: None
        """
        self.data['mvtypes'] = pd.cut(self.data['velocity'],
                                      bins=[0]+self.result,
                                      labels=[i for i in range(len(self.result))],
                                      include_lowest=True)

class convert:
    @staticmethod
    def gpx2csv(path, output):
        """
        Convert gpx file to csv.

        :param path: your file path or url link
        :param output: the name of output file
        :return: None
        """
        fields = ["id", "lat", "lng", "alt", "time"]

        if (path.find('http') + 1):
            res = requests.get(path).text
        else:
            res = open(path, "r").read()

        root = ET.fromstring(str(res))

        f = open('{0}.csv'.format(output), 'w')
        f.write(','.join(fields) + '\n')
        index = 1
        ns = root.tag.split('gpx')[0].translate(None, '{}')

        for trkpt in root.findall('./{{{0}}}trk/{{{0}}}trkseg/{{{0}}}trkpt'.format(ns)):
            r = [];
            r.extend((index, trkpt.attrib['lat'], trkpt.attrib['lon']))
            for child in trkpt:
                if (child.tag == '{{{0}}}ele'.format(ns) or child.tag == '{{{0}}}time'.format(ns)):
                    r.append(child.text)

            f.write(','.join([str(x) for x in r]) + '\n')
            index += 1

        f.close()