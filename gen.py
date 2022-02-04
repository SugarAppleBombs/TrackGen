import methods as mt
import gpxpy
import gpxpy.gpx
import os
import datetime as dt
import langs as ln
import time

def do_comment(trk_cmt):
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
        tdate = str(dt.date.fromtimestamp(time.time()))
        tdate = [tdate[8:10], tdate[5:7], tdate[0:4]]
   
    ttime = trk_cmt[1].split(':')
   
    if len(ttime)!=3:
        ttime = str(dt.datetime.fromtimestamp(time.time()))
        
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
    else:
        day = 1
        
    if hour.isdecimal():
        hour = int(hour)
    else:
        hour = 0
        
    if minute.isdecimal():
        minute = int(minute)
    else:
        minute = 0
        
    if second.isdecimal():
        second = int(second)
    else:
        second = 0

    speed = None
    if len(trk_cmt) == 3:
        if trk_cmt[2].isdecimal():
            speed = int(trk_cmt[2])
    
    return [dt.datetime(year, month, day, hour, minute, second), speed]

def generate(main_path, window):#main function
    
    main = open(main_path, encoding='utf-8', mode='r')
    
    #generating path and folder for output GPX file
    pth_holder = main_path.split('/')
    output_path = ""
    for i in range(len(pth_holder)-1):
        output_path = output_path + pth_holder[i]
        output_path = output_path + "/"
    smth = pth_holder[len(pth_holder) - 1].split('.')
    output_path = output_path + smth[0] + "_output"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    #parse GPX file
    gpx = gpxpy.parse(main)
    
    #searching for waypoints
    if window.point:
        
        #waypoint attributes cause fuck OOP
        pnt_name = []
        pnt_cmt = []
        pnt_lat = []
        pnt_lon = []
        output_point_path = []
        pnt_done = []
        
        for i, waypoint in enumerate(gpx.waypoints):
            #print('waypoint {0} -> ({1},{2})'.format(waypoint.name, waypoint.latitude, waypoint.longitude))
            
            pnt_name.append(waypoint.name)
            pnt_cmt.append(waypoint.comment)
            pnt_lat.append(waypoint.latitude)
            pnt_lon.append(waypoint.longitude)
            pnt_done.append(False)
            pnt_name[i] = pnt_name[i].translate({ord(c): None for c in '<>:"|?*'})
            output_point_path.append(output_path + "/" + pnt_name[i] + ".gpx")
           
    total_length = 0    #combined length of all found tracks and routes in km
    pnt_counter = 0     #well, duh
    trk_count = 0
    
    for i, route in enumerate(gpx.routes):
        window.label2.setText(ln.langs.get(window.lang, ln.eng).get('trk_proc', '***') + ', ' + ln.langs.get(window.lang, ln.eng).get('wait', '***'))
        trk_count += 1
        #print('Route: ', route.name)
        trk_name = route.name
        trk_cmt = route.comment
        trk_name = trk_name.translate({ord(c): None for c in '<>:"|?*'})
        output_track_path = output_path + "/" + trk_name + ".gpx"
        
        comment = do_comment(trk_cmt)
        start = comment[0]
        speed = 30
        
        if comment[1] is not None:
            speed = comment[1]
        
        coords = []
        for point in route.points:
            #print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))
            
            coords.append(float(point.latitude))
            coords.append(float(point.longitude))
        coords.insert(0, int(len(coords)/2))
        
        dst = mt.dist(coords)
        
        times = mt.time(start, sum(dst[1:]), speed)
        
        result_coords = mt.frommerc(mt.spline(times[0], mt.merc(coords)))
        
        total_length += sum(mt.dist(result_coords)[1:])
        
        elevations = mt.ele(result_coords, window.hgtdir)
        
        spd = mt.speeds(times, mt.dist(result_coords))
        
        #next 5 functions create an empty GPX track file and fill it with data
        #they should be executed exactly in this order:
        #core()
        #coordin()
        #elein()
        #timein()
        #speedin()
        
        mt.core(window.creator, times[0], trk_name, output_track_path)
        
        mt.coordin(result_coords, output_track_path)
        
        mt.elein(elevations, output_track_path)
        
        mt.timein(times, output_track_path)
        
        mt.speedin(spd, output_track_path)
            
        if 2 <= (trk_count)%10 <= 4 and not(12 <= (trk_count)%100 <= 14):
            tmp = str(trk_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_2', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if (12 <= (trk_count)%100 <= 14) or 5 <= (trk_count)%10 <= 9 or (trk_count)%10 == 0:
            tmp = str(trk_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_3', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if (trk_count)%10 == 1 and ((trk_count)%100 != 11):
            tmp = str(trk_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_1', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if ((trk_count)%100 == 11):
            tmp = str(trk_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_3', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if i == 0:
            tmp = "1 " + ln.langs.get(window.lang, ln.eng).get('trk_count_1', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        window.label3.setText(tmp)
        window.update()
    
        if window.point:
            for i, name in enumerate(pnt_name):
                if not pnt_done[i]:
                    window.label2.setText(ln.langs.get(window.lang, ln.eng).get('pnt_proc', '***') + ', ' + ln.langs.get(window.lang, ln.eng).get('wait', '***'))
                    min_dist = mt.haversine(pnt_lat[i], pnt_lon[i], result_coords[1], result_coords[2])
                    for j in range(1, times[0]):
                        point_dist = mt.haversine(pnt_lat[i], pnt_lon[i], result_coords[2*j+1], result_coords[2*(j+1)])
                        min_dist = min([min_dist, point_dist])
                    if min_dist < 0.01:
                        pnt_done[i] = True
                        mt.pointin(window.creator, name, pnt_cmt[i], pnt_lat[i], pnt_lon[i], output_point_path[i], times[j])
                        pnt_counter += 1
                        if 2 <= (pnt_counter)%10 <= 4 and not(12 <= (pnt_counter+1)%100 <= 14):
                            strng = str(pnt_counter) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_2', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_2', '***')
                            
                        if (12 <= (pnt_counter)%100 <= 14) or 5 <= (pnt_counter)%10 <= 9 or (pnt_counter)%10 == 0:
                            strng = str(pnt_counter) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_3', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_2', '***')
                            
                        if (pnt_counter)%10 == 1 and ((pnt_counter)%100 != 11):
                            strng = str(pnt_counter) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_1', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_1', '***')
                            
                        if ((pnt_counter)%100 == 11):
                            strng = str(pnt_counter) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_3', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_2', '***')
                            
                        if pnt_counter == 1:
                            strng = "1 " + ln.langs.get(window.lang, ln.eng).get('pnt_count_1', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_1', '***')
                        window.label4.setText(strng)
                        window.update()
    
    for track in gpx.tracks:
        window.label2.setText(ln.langs.get(window.lang, ln.eng).get('trk_proc', '***') + ', ' + ln.langs.get(window.lang, ln.eng).get('wait', '***'))
        trk_count += 1
        #print('Track: ', track.name)
        trk_name = track.name
        trk_cmt = track.comment
        trk_name = trk_name.translate({ord(c): None for c in '<>:"|?*'})
        output_track_path = output_path + "/" + trk_name + ".gpx"
        
        comment = do_comment(trk_cmt)
        start = comment[0]
        speed = 30
        
        if comment[1] is not None:
            speed = comment[1]
                
        coords = []
        for segment in track.segments:
            for point in segment.points:
                #print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))
                coords.append(float(point.latitude))
                coords.append(float(point.longitude))
        coords.insert(0, int(len(coords)/2))
        
        dst = mt.dist(coords)
        
        times = mt.time(start, sum(dst[1:]), speed)
        
        result_coords = mt.frommerc(mt.spline(times[0], mt.merc(coords)))
        
        total_length += sum(mt.dist(result_coords)[1:])
        
        elevations = mt.ele(result_coords, window.hgtdir)
        
        spd = mt.speeds(times, mt.dist(result_coords))
        
        #next 5 functions create an empty GPX track file and fill it with data
        #they should be executed exactly in this order:
        #core()
        #coordin()
        #elein()
        #timein()
        #speedin()
        
        mt.core(window.creator, times[0], trk_name, output_track_path)
        
        mt.coordin(result_coords, output_track_path)
        
        mt.elein(elevations, output_track_path)
        
        mt.timein(times, output_track_path)
        
        mt.speedin(spd, output_track_path)
            
        if 2 <= (trk_count)%10 <= 4 and not(12 <= (trk_count)%100 <= 14):
            tmp = str(trk_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_2', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if (12 <= (trk_count)%100 <= 14) or 5 <= (trk_count)%10 <= 9 or (trk_count)%10 == 0:
            tmp = str(trk_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_3', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if (trk_count)%10 == 1 and ((trk_count)%100 != 11):
            tmp = str(trk_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_1', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if ((trk_count)%100 == 11):
            tmp = str(trk_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_3', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if i == 0:
            tmp = "1 " + ln.langs.get(window.lang, ln.eng).get('trk_count_1', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        window.label3.setText(tmp)
        window.update()
    
        if window.point:
            for i, name in enumerate(pnt_name):
                if not pnt_done[i]:
                    window.label2.setText(ln.langs.get(window.lang, ln.eng).get('pnt_proc', '***') + ', ' + ln.langs.get(window.lang, ln.eng).get('wait', '***'))
                    min_dist = mt.haversine(pnt_lat[i], pnt_lon[i], result_coords[1], result_coords[2])
                    for j in range(1, times[0]):
                        point_dist = mt.haversine(pnt_lat[i], pnt_lon[i], result_coords[2*j+1], result_coords[2*(j+1)])
                        min_dist = min([min_dist, point_dist])
                    if min_dist < 0.01:
                        pnt_done[i] = True
                        mt.pointin(window.creator, name, pnt_cmt[i], pnt_lat[i], pnt_lon[i], output_point_path[i], times[j])
                        pnt_counter += 1
                        if 2 <= (pnt_counter)%10 <= 4 and not(12 <= (pnt_counter+1)%100 <= 14):
                            strng = str(pnt_counter) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_2', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_2', '***')
                            
                        if (12 <= (pnt_counter)%100 <= 14) or 5 <= (pnt_counter)%10 <= 9 or (pnt_counter)%10 == 0:
                            strng = str(pnt_counter) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_3', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_2', '***')
                            
                        if (pnt_counter)%10 == 1 and ((pnt_counter)%100 != 11):
                            strng = str(pnt_counter) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_1', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_1', '***')
                            
                        if ((pnt_counter)%100 == 11):
                            strng = str(pnt_counter) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_3', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_2', '***')
                            
                        if pnt_counter == 1:
                            strng = "1 " + ln.langs.get(window.lang, ln.eng).get('pnt_count_1', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_1', '***')
                        window.label4.setText(strng)
                        window.update()     
    
    window.label2.setText(ln.langs.get(window.lang, ln.eng).get('done_stat', '***'))
    window.sign.setPixmap(window.checkmark)
    window.label1.setText("...")
    window.b1.setEnabled(True)
    window.set.setEnabled(True)