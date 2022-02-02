import methods as mt
import gpxpy
import gpxpy.gpx
import os
import datetime as dt
import langs as ln

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
        
        for waypoint in gpx.waypoints:
            #print('waypoint {0} -> ({1},{2})'.format(waypoint.name, waypoint.latitude, waypoint.longitude))
            
            pnt_name.append(waypoint.name)
            pnt_cmt.append(waypoint.comment)
            pnt_lat.append(waypoint.latitude)
            pnt_lon.append(waypoint.longitude)
            pnt_done.append(False)
            output_point_path.append(output_path + "/" + waypoint.name + ".gpx")
           
    total_length = 0    #combined length of all found tracks and routes in km
    pnt_counter = 0     #well, duh
    
    for i, route in enumerate(gpx.routes):
        #print('Route:')
        trk_name = route.name
        trk_cmt = route.comment
        output_track_path = output_path + "/" + trk_name + ".gpx"
        
        if trk_cmt is None:
            trk_cmt = "01-01-0001 00:00:00"
        if len(trk_cmt) > 18:
            trk_cmt = trk_cmt.split(' ')
        else:
            trk_cmt = ["01-01-0001", "00:00:00"]
        tdate = trk_cmt[0].split('-')
        if len(tdate)!=3:
            tdate = trk_cmt[0].split('.')
        if len(tdate)!=3:
            tdate = trk_cmt[0].split('/')
        if len(tdate)!=3:
            tdate = ["01", "01", "01"]
        ttime = trk_cmt[1].split(':')
        if len(ttime)!=3:
            ttime = ["00", "00", "00"]
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
        
        start = dt.datetime(year, month, day, hour, minute, second)
        speed = 30
        
        if len(trk_cmt) == 3:
            if trk_cmt[2].isdecimal():
                speed = int(trk_cmt[2])
        
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
            
        if 2 <= (i+1)%10 <= 4 and not(12 <= (i+1)%100 <= 14):
            tmp = str(i+1) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_2', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if (12 <= (i+1)%100 <= 14) or 5 <= (i+1)%10 <= 9 or (i+1)%10 == 0:
            tmp = str(i+1) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_3', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if (i+1)%10 == 1 and ((i+1)%100 != 11):
            tmp = str(i+1) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_1', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if ((i+1)%100 == 11):
            tmp = str(i+1) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_3', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if i == 0:
            tmp = "1 " + ln.langs.get(window.lang, ln.eng).get('trk_count_1', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        window.label3.setText(tmp)
        window.update()
    
        if window.point:
            for i, name in enumerate(pnt_name):
                if not pnt_done[i]:
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
        #print('Route:')
        trk_name = track.name
        trk_cmt = track.comment
        output_track_path = output_path + "/" + trk_name + ".gpx"
        
        if trk_cmt is None:
            trk_cmt = "01-01-0001 00:00:00"
        if len(trk_cmt) > 18:
            trk_cmt = trk_cmt.split(' ')
        else:
            trk_cmt = ["01-01-0001", "00:00:00"]
        tdate = trk_cmt[0].split('-')
        if len(tdate)!=3:
            tdate = trk_cmt[0].split('.')
        if len(tdate)!=3:
            tdate = trk_cmt[0].split('/')
        if len(tdate)!=3:
            tdate = ["01", "01", "01"]
        ttime = trk_cmt[1].split(':')
        if len(ttime)!=3:
            ttime = ["00", "00", "00"]
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
        
        start = dt.datetime(year, month, day, hour, minute, second)
        speed = 30
        
        if len(trk_cmt) == 3:
            if trk_cmt[2].isdecimal():
                speed = int(trk_cmt[2])
        
        coords = []
        for segment in track.segments:
            for point in segment.points:
                print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))
                coords.append(float(point.latitude))
                coords.append(float(point.longitude))
        coords.insert(0, int(len(coords)/2))
        
        dst = mt.dist(coords)
        
        times = mt.time(start, sum(dst[1:]), speed)
        
        result_coords = mt.frommerc(mt.spline(times[0], mt.merc(coords)))
        
        total_length += sum(mt.dist(result_coords)[1:])
        
        elevations = mt.ele(result_coords, window.hgt)
        
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
            
        if 2 <= (i+1)%10 <= 4 and not(12 <= (i+1)%100 <= 14):
            tmp = str(i+1) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_2', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if (12 <= (i+1)%100 <= 14) or 5 <= (i+1)%10 <= 9 or (i+1)%10 == 0:
            tmp = str(i+1) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_3', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if (i+1)%10 == 1 and ((i+1)%100 != 11):
            tmp = str(i+1) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_1', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if ((i+1)%100 == 11):
            tmp = str(i+1) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_3', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if i == 0:
            tmp = "1 " + ln.langs.get(window.lang, ln.eng).get('trk_count_1', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        window.label3.setText(tmp)
        window.update()
    
        if window.point:
            for i, name in enumerate(pnt_name):
                if not pnt_done[i]:
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
    window.b2.setEnabled(False)