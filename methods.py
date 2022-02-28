import os
from scipy import interpolate
import math as m
import numpy as np
import random
import gdal
import datetime as dt
import langs as ln


gdal.UseExceptions()

SAMPLES = 3600  #number of longitudinal samples in AW3D30 DSM files
DATA = 'data'   #name of the folder containing misc files

def do_comment(trk_cmt):
    #print(trk_cmt)
    if isinstance(trk_cmt, str):
        trk_cmt = trk_cmt.split(' ')
    else:
        trk_cmt = ['1', '1']
    
    tdate = trk_cmt[0].split('-')
    
    if len(tdate)!=3:
        tdate = trk_cmt[0].split('.')
    if len(tdate)!=3:
        tdate = trk_cmt[0].split('/')
    if len(tdate)!=3:
        tdate = str(dt.datetime.now())
        tdate = [tdate[8:10], tdate[5:7], tdate[0:4]]
   
    if len(trk_cmt) > 1:
        ttime = trk_cmt[1].split(':')
    else:
        ttime = ' '
   
    if len(ttime)!=3:
        ttime = str(dt.datetime.now())
        
        ttime = [ttime[11:13], ttime[14:16], ttime[17:19]]
    
    year = tdate[2]
    month = tdate[1]
    day = tdate[0]
    hour = ttime[0]
    minute = ttime[1]
    second = ttime[2]
    
    if year.isdecimal():
        if len(year) == 2:
            year = int(year)
            year = year + 2000
        year = int(year)
    else:
        year = 0
        
    if month.isdecimal():
        month = int(month)
        if month > 12 or month <1:
            month = 1
    else:
        month = ln.months.get(month, 1)
    
    if day.isdecimal():
        day = int(day)
        if (year%4 == 0 and not year%100 == 0) or (year%400 == 0):
            if not 0 <= day <= ln.daycounts_leap.get(month):
                day = 1
        else:
            if not 0 <= day <= ln.daycounts_normal.get(month):
                day = 1
    else:
        day = 1
        
    if hour.isdecimal():
        hour = int(hour)
        if not 0 <= hour <= 24:
            hour = 0
    else:
        hour = 0
        
    if minute.isdecimal():
        minute = int(minute)
        if not 0 <= minute <= 59:
            minute = 0
    else:
        minute = 0
        
    if second.isdecimal():
        second = int(second)
        if not 0 <= second <= 59:
            second = 0
    else:
        second = 0

    speed = None
    if len(trk_cmt) == 3:
        if trk_cmt[2].isdecimal():
            speed = int(trk_cmt[2])
    
    return [dt.datetime(year, month, day, hour, minute, second), speed]

def core(creator, q, name, path):#creating an empty GPX track file using a template
    #print(path)
    output = open(path,"wb")
    tmplt = open(DATA + "/trk_tmplt.gpx","rb") #template of a GPX track file from Soviet Military Maps Android App(should be included with this script)
                                           #every filling function in this script is designed for a specific GPX template
    output.write(tmplt.read(126))
    output.write(creator.encode(encoding='utf-8', errors='strict'))
    output.write(tmplt.read(160))
    output.write(name.encode(encoding='utf-8', errors='strict'))
    output.write(tmplt.read(20))
    output.write(name.encode(encoding='utf-8', errors='strict'))
    output.write(tmplt.read(17))
    for i in range(q):
        output.write(tmplt.read(60))
        tmplt.seek(0)
        for j in range(6):
            tmplt.readline()
    for j in range(5):
        tmplt.readline()
    output.write(tmplt.read(24))
    output.seek(0)
    output.close()
    tmplt.close()

def coordin(coord, path):#filling in the coordinates into an empty GPX track file
    output = open(path,"r+b")
    temp = open(DATA + "/temp.gpx", "w+b")
    temp.write(output.read())
    output.seek(0)
    temp.seek(0)
    for i in range(6):
        output.readline()
        temp.readline()
    output.read(7)
    temp.read(7)
    f1 = 'lat="'
    f2 = '" lon="'
    f3 = '"'
    for i in range(coord[0]):
        tlat = round(coord[2*i+1], 8)
        tlat = str(tlat)
        tlat = tlat[0:11]
        tlon = round(coord[2*(i+1)], 8)
        tlon = str(tlon)
        tlon = tlon[0:11]
        output.write(f1.encode(encoding='utf-8', errors='strict'))
        output.write(tlat.encode(encoding='utf-8', errors='strict'))
        output.write(f2.encode(encoding='utf-8', errors='strict'))
        output.write(tlon.encode(encoding='utf-8', errors='strict'))
        output.write(f3.encode(encoding='utf-8', errors='strict'))
        output.write(temp.read(60))
    output.write(temp.read(55))
    temp.close()
    os.remove(DATA + "/temp.gpx")
    output.close()

def merc(input):#lat/lon coordinates to Mercator projection conversion
    l = input[0]
    output = []
    output.append(l)
    for i in range(l):
        lat = input[2*i+1]
        lon = input[2*(i+1)]
        x = m.radians(lon)  #conversion
        y = m.log((1+m.sin(m.radians(lat)))/(1-m.sin(m.radians(lat))))/2    #conversion
        output.append(x)
        output.append(y)
    return output

def frommerc(input):#Mercator projection to lat/lon coordinates conversion
    l = input[0]
    output = []
    output.append(l)
    for i in range(l):
        x = input[2*i+1]
        y = input[2*(i+1)]
        lon = m.degrees(x)  #conversion
        lat = m.degrees(2*m.atan(m.pow(m.e, y))) - 90   #conversion
        output.append(lat)
        output.append(lon)
    return output

def spline(length, array):#cubic spline for a track(should convert track to Mercator first)
    #print('making a spline')
    x_points = []
    y_points = []
    out = []
    out.append(length)
    
    deg = 1
    if array[0]==3:
        deg = 2
    if array[0]>3:
        deg = 3
    x_points.append(array[1])
    y_points.append(array[2])
    d = 0
    for i in range(1, array[0]):
        if array[2*i+1]!=x_points[i-1-d] and array[2*(i+1)]!=y_points[i-1-d]:
            x_points.append(array[2*i+1])
            y_points.append(array[2*(i+1)])
        else:
            #print('a consecutive duplicate: ')
            #print(array[2*i+1],'=', x_points[i-1-d])
            #print(array[2*(i+1)], '=', y_points[i-1-d])
            d += 1
    mytck,myu=interpolate.splprep([x_points,y_points], s = 0.0, k = deg)
    xnew,ynew= interpolate.splev(np.linspace(0,1,length),mytck)
    out[0] = len(xnew)
    for i in range(length):
        out.append(xnew[i] + xnew[i] * 0.00000005 * (random.random() - 0.5))     #resulting x/y coordinates are slightly randomized scaling with overall track length
        out.append(ynew[i] + ynew[i] * 0.00000005 * (random.random() - 0.5))
    #print('spline is done')
    return out

def haversine(lat1, lon1, lat2, lon2):#distance between two geographical points in kilometers(lat/lon coordinates)
    dlon = m.radians(lon2 - lon1)
    dlat = m.radians(lat2 - lat1)
    a = m.pow(m.sin(dlat/2), 2) + m.cos(m.radians(lat1))*m.cos(m.radians(lat2))*m.pow(m.sin(dlon/2), 2)     #haversine formula
    c = 2 * m.atan2(m.sqrt(a), m.sqrt(1-a))#haversine formula
    return 6371 * c

def dist(array):#roughly calculating track length in kilometers
    out = []
    out.append(array[0]-1)
    for i in range(out[0]):
        d = haversine(array[2*i+1], array[2*(i+1)], array[2*i+3], array[2*(i+2)])
        out.append(d)
    return out

def ele(array, folder):#reading elevations above sea level of each point in a track
    out = []
    temp_out = []
    out.append(array[0])
    temp_out.append(array[0])
    tiles = []
    t = 1
    tiles.append(t)
    tiles.append(m.floor(array[1]))
    tiles.append(m.floor(array[2]))
    flag = 1
    
    for i in range(array[0] - 1):
        tlat = m.floor(array[2*i+3])
        tlon = m.floor(array[2*(i+2)])
        for j in range(tiles[0]):
            if (tlat==tiles[2*j+1])and(tlon==tiles[2*(j+1)]):
                flag = 0
        if flag == 1:
            t = t + 1
            tiles[0] = t
            tiles.append(tlat)
            tiles.append(tlon)        
        else:
            flag = 1
    count = []  #array to keep the order of points in a track
    count.append(array[0])
    
    for i in range(tiles[0]):
        hgt_file = filename(tiles[2*i+1], tiles[2*(i+1)], folder)
        if os.path.isfile(hgt_file):
            flag = True
            ds = gdal.Open(hgt_file)
            band = ds.GetRasterBand(1)
            elevation = band.ReadAsArray()  #reading elevation values in a tile
        else:
            flag = False
        
        for j in range(array[0]):
            lat = array[2*j+1]
            lon = array[2*(j+1)]
            
            lon_samples = SAMPLES   #number of latitudinal samples in AW3D30 DSM files is 3600 until 60 degrees N and S
            if abs(lat) > 60:
                lon_samples = 1800  #1800 from 60 to 80 degrees N and S
            if abs(lat) > 70:
                lon_samples = 1200  #1200 from 70 to 80 degrees N and S
            if abs(lat) > 80:
                lon_samples = 600   #600 from 80 degrees N and S
                
            if (m.floor(lat) ==  tiles[2*i+1])and(m.floor(lon) == tiles[2*(i+1)]):
                if flag:
                    lat_row = int(round((lat - int(lat)) * (SAMPLES - 1), 0))       #since data read from a tile is a 1-d array
                    lon_row = int(round((lon - int(lon)) * (lon_samples - 1), 0))   #converting x/y pointer to a single position
                    e = elevation[SAMPLES - 1 - lat_row, lon_row].astype(int)   
                    temp_out.append(e + round(random.random() + random.random() - random.random() - random.random(), 1))
                else:
                    temp_out.append(0.0)
                count.append(j+1)   #remembering position of track point we just read an elevation value for
        if flag:
            ds = None
            band = None
            elevation = None
    
    
    #sorting aquired elevation values according to order of points in a track
    count_sorted = []
    count_sorted.append(array[0])
    pointer = 1
    
    while len(count_sorted)<len(count):             #reading through count array and adding next elevation value only if
        for i in range(array[0]):                   #its position corresponds to a track point
            if count[i+1] == pointer:               #if count_sorted has the same number of values as count
                pointer = pointer + 1               #that means we sorted all of the values and placed them in out array
                count_sorted.append(count[i])
                out.append(temp_out[i+1])
                
    return out

def filename(lon, lat, folder):#generating file name of a AW3D30 DSM file containing elevation value of a point with lon/lat coordinates
    if lat >= 0:
        ns = 'N'
    elif lat < 0:
        ns = 'S'

    if lon >= 0:
        ew = 'E'
    elif lon < 0:
        ew = 'W'

    hgt_file_path = folder + "/ALPSMLC30_"+str(ns)+str("{:03d}".format(m.floor(lon)))+str(ew)+str(m.floor(lat))+"_DSM.tif"
    
    return hgt_file_path
    
def elein(array, path):#filling in the elevation values into an resulting GPX track file
    output = open(path,"r+b")
    temp = open(DATA + "/temp.gpx", "w+b")
    temp.write(output.read())
    output.seek(0)
    temp.seek(0)
    for i in range(7):
        output.readline()
        temp.readline()
    for i in range(array[0]):
        output.write(temp.read(5))
        output.write(str(array[i+1]).encode(encoding='utf-8', errors='strict'))
        output.write(temp.read(7))
        for j in range(4):
            output.write(temp.readline())
    output.write(temp.read(52))
    temp.close()
    os.remove(DATA + "/temp.gpx")
    output.close()
    
def timein(array, path):#filling in the date/time values into an resulting GPX track file
    output = open(path,"r+b")
    temp = open(DATA + "/temp.gpx", "w+b")
    temp.write(output.read())
    output.seek(0)
    temp.seek(0)
    t = "T"
    for i in range(8):
        output.readline()
        temp.readline()
    for i in range(array[0]):
        output.write(temp.read(6))
        output.write(str(array[i+1].date()).encode(encoding='utf-8', errors='strict'))
        output.write(t.encode(encoding='utf-8', errors='strict'))
        output.write(str(array[i+1].time())[:8].encode(encoding='utf-8', errors='strict'))
        output.write(temp.read(8))
        for j in range(4):
            output.write(temp.readline())
    output.write(temp.read(41))
    temp.close()
    os.remove(DATA + "/temp.gpx")
    output.close()

def generate_spds(mean_spd, n):
    result = []
    result.append(n)
    for i in range(n+1):
        result.append(mean_spd)

    first_y = []
    first_x = []

    first_y.append((random.random() - 0.5)*mean_spd*0.15)
    first_x.append(1)
    for i in range(int(random.random()*15) + 15):
        dec = random.random()
        if dec>0.3:
            new = (random.random() - 0.5)*2*5
            first_y.append(new)
        else:
            first_y.append(first_y[i-1])
        first_x.append(i+2)

    mytck,myu=interpolate.splprep([first_x,first_y], s = 80.0, k = 1)
    xnew,ynew= interpolate.splev(np.linspace(0,1,len(result)),mytck)

    for i in range(n+1):
        ynew[i] = ynew[i] * (1 + (random.random() - 0.5)*0.7) * (1 + (random.random() - 0.5)*0.7) 

    for i in range(n+1):
        result[i] += ynew[i]
            
    return result

def time(t1, dist, speed, n):#calculating the timestamp of each track point knowing timestamp of the first point and average speed
    time = []
    current_time = t1
    
    time.append(n)
    time.append(current_time)
    
    speeds = generate_spds(speed, n)
    for i in range(1, n):
        delta = (dist[i]/speeds[i])*3600
        #print(dist[i], ' ' , speeds[i], ' ' ,delta)
        current_time = current_time + dt.timedelta(seconds=delta)
        time.append(current_time)
    
    return time

def speeds(times, dists):#calculating "instant" speed between two points using "real" distance beetween points and their time delta
    spd = []
    spd.append(dists[0]+1)
    
    t = times[2]-times[1]
    t = t.total_seconds()/3600
    v = dists[1]/t
    spd.append(v)
    
    for i in range(dists[0]):
        t = times[i+2]-times[i+1]
        t = t.total_seconds()/3600
        v = dists[i+1]/t
        #print(dists[i+1], ' ', t*3600, ' ', v)
        spd.append(v)
    
    return spd

def speedin(array, path):#filling in the "instant" speed values into an resulting GPX track file
    output = open(path,"r+b")
    temp = open(DATA + "/temp.gpx", "w+b")
    temp.write(output.read())
    output.seek(0)
    temp.seek(0)
    for i in range(9):
        output.readline()
        temp.readline()
    for i in range(array[0]):
        output.write(temp.read(7))
        output.write(str(round(array[i+1], 1)).encode(encoding='utf-8', errors='strict'))
        output.write(temp.read(9))
        for j in range(4):
            output.write(temp.readline())
    output.write(temp.read(49))
    temp.close()
    os.remove(DATA + "/temp.gpx")
    output.close()

def pointin(creator, name, cm, lat, lon, output_path, timestamp, ele):
    file = open(output_path, mode='rb')
    contents = file.read()
    file.close()
    file = open(output_path, mode='r+b')
    file.seek(len(contents)-7)
    
    file.write('<wpt lat="'.encode(encoding='utf-8', errors='strict'))
    file.write(str(round(lat, 8)).encode(encoding='utf-8', errors='strict'))
    file.write('" lon="'.encode(encoding='utf-8', errors='strict'))
    file.write(str(round(lon, 8)).encode(encoding='utf-8', errors='strict'))
    file.write('">\n<name>'.encode(encoding='utf-8', errors='strict'))
    file.write(name.encode(encoding='utf-8', errors='strict'))
    file.write('</name>\n<ele>'.encode(encoding='utf-8', errors='strict'))
    file.write(str(ele).encode(encoding='utf-8', errors='strict'))
    file.write('</ele>\n<desc>'.encode(encoding='utf-8', errors='strict'))
    file.write(cm.encode(encoding='utf-8', errors='strict'))
    file.write('</desc>\n<time>'.encode(encoding='utf-8', errors='strict'))
    file.write(str(timestamp.date()).encode(encoding='utf-8', errors='strict'))
    file.write("T".encode(encoding='utf-8', errors='strict'))
    file.write(str(timestamp.time())[:8].encode(encoding='utf-8', errors='strict'))
    file.write('</time>\n</wpt>\n</gpx>\n'.encode(encoding='utf-8', errors='strict'))
    
    file.close()
