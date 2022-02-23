import methods as mt
import gpxpy
import gpxpy.gpx
import os
import langs as ln
import platform
if platform.system() == 'Windows':
    import pywintypes, win32file, win32con

def changeFileCreationTime(fname, newtime):
    wintime = pywintypes.Time(newtime)
    winfile = win32file.CreateFile(
        fname, win32con.GENERIC_WRITE,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None, win32con.OPEN_EXISTING,
        win32con.FILE_ATTRIBUTE_NORMAL, None)

    win32file.SetFileTime(winfile, wintime, None, None)

    winfile.close()

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
    window.label2.setText(ln.langs.get(window.lang, ln.eng).get('reading', '***'))
    gpx = gpxpy.parse(main)
    
    track_count = 0
    waypoint_count = 0
    
    for route in gpx.routes:
        track_count += 1
    for track in gpx.tracks:
        track_count += 1
    for waypoint in gpx.waypoints:
        waypoint_count += 1
        
    #searching for waypoints
    if window.point:
        
        #waypoint attributes cause fuck OOP
        pnt_name = []
        pnt_cmt = []
        pnt_lat = []
        pnt_lon = []
        pnt_ele = []
        pnt_done = []
        
        for i, waypoint in enumerate(gpx.waypoints):
            #print('waypoint {0} -> ({1},{2})'.format(waypoint.name, waypoint.latitude, waypoint.longitude))
            
            if waypoint.name is not None:
                pnt_name.append(waypoint.name)
            else:
                pnt_name.append('Point ' + str(i))
            
            if waypoint.comment is not None:
                pnt_cmt.append(waypoint.comment)
            elif waypoint.name is not None:
                pnt_cmt.append(waypoint.name)
            else:
                pnt_cmt.append(str(waypoint.latitude) + ', ' + str(waypoint.longitude))
            
            if waypoint.latitude is not None:
                pnt_lat.append(waypoint.latitude)
            else:
                pnt_lat.append(0.0)
            
            if waypoint.longitude is not None:
                pnt_lon.append(waypoint.longitude)
            else:
                pnt_lon.append(0.0)
                
            pnt_ele.append(mt.ele([1, waypoint.latitude, waypoint.longitude], window.hgtdir)[1])
            
            pnt_done.append(False)
            pnt_name[i] = pnt_name[i].translate({ord(c): None for c in '<>:"|?*'})
           
    total_length = 0    #combined length of all found tracks and routes in km
    pnt_counter = 0     #well, duh
    trk_count = 0
    
    for i, route in enumerate(gpx.routes):
        trk_point_counter = 0
        window.label2.setText(ln.langs.get(window.lang, ln.eng).get('trk_proc', '***') + ', ' + ln.langs.get(window.lang, ln.eng).get('wait', '***'))
        trk_count += 1
        #print('Route: ', route.name)
        trk_name = route.name
        trk_cmt = route.comment
        trk_name = trk_name.translate({ord(c): None for c in '<>:"|?*'})
        output_track_path = output_path + "/" + trk_name + ".gpx"
        output_track_points_path = output_track_path[:len(output_track_path)-4] + ' + p.gpx'
        #print('comment is ', trk_cmt)
        comment = mt.do_comment(trk_cmt)
        #print('comment read as ', comment)
        start = comment[0]
        speed = 30
        
        if comment[1] is not None:
            speed = comment[1]
        #print('speed is set to ', speed)
        coords = []
        for point in route.points:
            #print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))
            
            coords.append(float(point.latitude))
            coords.append(float(point.longitude))
        coords.insert(0, int(len(coords)/2))
        
        if coords[0] > 1:
            dst = mt.dist(coords)
            
            n = int(1800*sum(dst[1:])/speed)
            
            result_coords = mt.frommerc(mt.spline(n, mt.merc(coords)))
            
            dst = mt.dist(result_coords)
            
            times = mt.time(start, dst, speed, n)
            
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
            
            mt.core(window.creator, n, trk_name, output_track_path)
            
            mt.coordin(result_coords, output_track_path)
            
            mt.elein(elevations, output_track_path)
            
            mt.timein(times, output_track_path)
            
            mt.speedin(spd, output_track_path)
        else:
            mt.core(window.creator, 1, trk_name, output_track_path)
            
            mt.coordin(coords, output_track_path)
            
            mt.elein(mt.ele(coords, window.hgtdir), output_track_path)
            
            mt.timein([1, start], output_track_path)
            
            mt.speedin([1, 0], output_track_path)
            
        if 2 <= (trk_count)%10 <= 4 and not(12 <= (trk_count)%100 <= 14):
            tmp = str(trk_count) + "/" + str(track_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_2', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if (12 <= (trk_count)%100 <= 14) or 5 <= (trk_count)%10 <= 9 or (trk_count)%10 == 0:
            tmp = str(trk_count) + "/" + str(track_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_3', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if (trk_count)%10 == 1 and ((trk_count)%100 != 11):
            tmp = str(trk_count) + "/" + str(track_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_1', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if ((trk_count)%100 == 11):
            tmp = str(trk_count) + "/" + str(track_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_3', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if i == 0:
            tmp = "1" + "/" + str(track_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_1', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        window.label3.setText(tmp)
        window.update()
    
        if window.point:
            for i, name in enumerate(pnt_name):
                if not pnt_done[i]:
                    window.label2.setText(ln.langs.get(window.lang, ln.eng).get('pnt_proc', '***') + ', ' + ln.langs.get(window.lang, ln.eng).get('wait', '***'))
                    min_dist = mt.haversine(pnt_lat[i], pnt_lon[i], result_coords[1], result_coords[2])
                    timestamp_index = 1
                    for j in range(1, times[0]):
                        point_dist = mt.haversine(pnt_lat[i], pnt_lon[i], result_coords[2*j+1], result_coords[2*(j+1)])
                        if point_dist < min_dist:
                            min_dist = point_dist
                            timestamp_index = j
                       
                    if min_dist < 0.01:
                        pnt_done[i] = True
                        if trk_point_counter == 0:
                            trk_point_counter += 1
                            track = open(output_track_path, mode='rb')
                            track_with_points = open(output_track_points_path, mode='wb')
                            track_with_points.write(track.read())
                            track.close()
                            track_with_points.close()
                            
                        mt.pointin(window.creator, name, pnt_cmt[i], result_coords[2*timestamp_index+1], result_coords[2*(timestamp_index+1)], output_track_points_path, times[timestamp_index], pnt_ele[i])
                        pnt_counter += 1
                        if 2 <= (pnt_counter)%10 <= 4 and not(12 <= (pnt_counter+1)%100 <= 14):
                            strng = str(pnt_counter) + "/" + str(waypoint_count) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_2', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_2', '***')
                            
                        if (12 <= (pnt_counter)%100 <= 14) or 5 <= (pnt_counter)%10 <= 9 or (pnt_counter)%10 == 0:
                            strng = str(pnt_counter) + "/" + str(waypoint_count) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_3', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_2', '***')
                            
                        if (pnt_counter)%10 == 1 and ((pnt_counter)%100 != 11):
                            strng = str(pnt_counter) + "/" + str(waypoint_count) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_1', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_1', '***')
                            
                        if ((pnt_counter)%100 == 11):
                            strng = str(pnt_counter) + "/" + str(waypoint_count) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_3', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_2', '***')
                            
                        if pnt_counter == 1:
                            strng = "1" + "/" + str(waypoint_count) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_1', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_1', '***')
                        window.label4.setText(strng)
                        window.update()
                        
        
            
        
    for track in gpx.tracks:
        trk_point_counter = 0
        window.label2.setText(ln.langs.get(window.lang, ln.eng).get('trk_proc', '***') + ', ' + ln.langs.get(window.lang, ln.eng).get('wait', '***'))
        trk_count += 1
        #print('Track: ', track.name)
        trk_name = track.name
        trk_cmt = track.comment
        trk_name = trk_name.translate({ord(c): None for c in '<>:"|?*'})
        output_track_path = output_path + "/" + trk_name + ".gpx"
        output_track_points_path = output_track_path[:len(output_track_path)-4] + ' + p.gpx'
        #print('comment is ', trk_cmt)
        comment = mt.do_comment(trk_cmt)
        #print('comment read as ', comment)
        start = comment[0]
        speed = 30
        
        if comment[1] is not None:
            speed = comment[1]
        #print('speed is set to ', speed)
        coords = []
        for segment in track.segments:
            for point in segment.points:
                #print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))
                coords.append(float(point.latitude))
                coords.append(float(point.longitude))
        coords.insert(0, int(len(coords)/2))
            
        if coords[0] > 1:
            dst = mt.dist(coords)
            
            n = int(1800*sum(dst[1:])/speed)
            
            result_coords = mt.frommerc(mt.spline(n, mt.merc(coords)))
            
            dst = mt.dist(result_coords)
            
            times = mt.time(start, dst, speed, n)
            
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
            
            mt.core(window.creator, n, trk_name, output_track_path)
            
            mt.coordin(result_coords, output_track_path)
            
            mt.elein(elevations, output_track_path)
            
            mt.timein(times, output_track_path)
            
            mt.speedin(spd, output_track_path)
        else:
            mt.core(window.creator, 1, trk_name, output_track_path)
            
            mt.coordin(coords, output_track_path)
            
            mt.elein(mt.ele(coords, window.hgtdir), output_track_path)
            
            mt.timein([1, start], output_track_path)
            
            mt.speedin([1, 0], output_track_path)
            
        if 2 <= (trk_count)%10 <= 4 and not(12 <= (trk_count)%100 <= 14):
            tmp = str(trk_count) + "/" + str(track_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_2', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if (12 <= (trk_count)%100 <= 14) or 5 <= (trk_count)%10 <= 9 or (trk_count)%10 == 0:
            tmp = str(trk_count) + "/" + str(track_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_3', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if (trk_count)%10 == 1 and ((trk_count)%100 != 11):
            tmp = str(trk_count) + "/" + str(track_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_1', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if ((trk_count)%100 == 11):
            tmp = str(trk_count) + "/" + str(track_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_3', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        if i == 0:
            tmp = "1" + "/" + str(track_count) + " " + ln.langs.get(window.lang, ln.eng).get('trk_count_1', '***') + ", " + str(round(total_length, 3)) + " " + ln.langs.get(window.lang, ln.eng).get('length', '***')
            
        window.label3.setText(tmp)
        window.update()
    
        if window.point:
            for i, name in enumerate(pnt_name):
                if not pnt_done[i]:
                    window.label2.setText(ln.langs.get(window.lang, ln.eng).get('pnt_proc', '***') + ', ' + ln.langs.get(window.lang, ln.eng).get('wait', '***'))
                    min_dist = mt.haversine(pnt_lat[i], pnt_lon[i], result_coords[1], result_coords[2])
                    timestamp_index = 1
                    for j in range(1, times[0]):
                        point_dist = mt.haversine(pnt_lat[i], pnt_lon[i], result_coords[2*j+1], result_coords[2*(j+1)])
                        if point_dist < min_dist:
                            min_dist = point_dist
                            timestamp_index = j
                    if min_dist < 0.01:
                        pnt_done[i] = True
                        if trk_point_counter == 0:
                            trk_point_counter += 1
                            track = open(output_track_path, mode='rb')
                            track_with_points = open(output_track_points_path, mode='wb')
                            track_with_points.write(track.read())
                            track.close()
                            track_with_points.close()
                        
                        mt.pointin(window.creator, name, pnt_cmt[i], result_coords[2*timestamp_index+1], result_coords[2*(timestamp_index+1)], output_track_points_path, times[timestamp_index], pnt_ele[i])
                        pnt_counter += 1
                        if 2 <= (pnt_counter)%10 <= 4 and not(12 <= (pnt_counter+1)%100 <= 14):
                            strng = str(pnt_counter) + "/" + str(waypoint_count) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_2', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_2', '***')
                            
                        if (12 <= (pnt_counter)%100 <= 14) or 5 <= (pnt_counter)%10 <= 9 or (pnt_counter)%10 == 0:
                            strng = str(pnt_counter) + "/" + str(waypoint_count) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_3', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_2', '***')
                            
                        if (pnt_counter)%10 == 1 and ((pnt_counter)%100 != 11):
                            strng = str(pnt_counter) + "/" + str(waypoint_count) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_1', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_1', '***')
                            
                        if ((pnt_counter)%100 == 11):
                            strng = str(pnt_counter) + "/" + str(waypoint_count) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_3', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_2', '***')
                            
                        if pnt_counter == 1:
                            strng = "1" + "/" + str(waypoint_count) + " " + ln.langs.get(window.lang, ln.eng).get('pnt_count_1', '***') + " " + ln.langs.get(window.lang, ln.eng).get('snapped_1', '***')
                        window.label4.setText(strng)
                        window.update()  
        
    
    window.label2.setText(ln.langs.get(window.lang, ln.eng).get('done_stat', '***'))
    window.sign.setPixmap(window.checkmark)
    window.label1.setText("...")
    window.b1.setEnabled(True)
    window.set.setEnabled(True)