#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
import json
import urllib.request as rq
import numpy as np
import k3d

#baseurl = 'https://www.edsm.net/api-v1/sphere-systems?showCoordinates=1&radius=100&systemName='
baseurl = 'https://www.edsm.net/api-v1/cube-systems?showCoordinates=1&size=200&systemName='

guardians=["Graea Hypue QL-V b19-15", "Graea Hypue LS-S d4-83", "Graea Hypue LS-S d4-3", "Graea Hypue HX-S d4-2"]

sys_coords = []
colors = []
num_coords = []
max_bodies = 1

for count, g in enumerate(guardians):
    url = baseurl + urllib.parse.quote(format(g.strip()))
    response = rq.urlopen(url)
    r = response.read()
    systems = json.loads(r.decode('utf-8'))
    num_coords.append(len(systems))
    print (len(systems))
    #print (systems)

    for s in systems:
        bc = s['bodyCount']
        if s['bodyCount']:
            bc = s['bodyCount']
        else:
            bc = 1
        if bc > max_bodies:
            max_bodies = bc
        colors.append(bc)
        
        coords = s['coords']
        point = [coords['x'], coords['y'], coords['z']]
        sys_coords.append(point)

#print (num_coords)
#print (sys_coords)
#print (max_bodies)

for k in range(len(colors)):
    color = 255 - int(colors[k]*255/max_bodies)
    colors[k] = (255 << 16) + (color << 8)


plot = k3d.plot()
start = 0
for n in num_coords:
    np_points = np.array(sys_coords[start:(start + n)])
    sys_colors = np.array(colors[start:(start + n)])
    points = k3d.points(np_points.astype(np.float32), sys_colors.astype(np.uint32), point_size=2.0, shader='flat')
    plot += points
    start = start + n
    
#np_points = np.array(sys_coords[:num_coords[0]])
#sys_colors = np.array(colors[:num_coords[0]])
#points = k3d.points(np_points.astype(np.float32), sys_colors.astype(np.uint32), point_size=2.0, shader='flat')
#plot += points
#sys_colors = np.array(colors[num_coords[0]:(num_coords[0] + num_coords[1])])
#np_points = np.array(sys_coords[num_coords[0]:(num_coords[0] + num_coords[1])])
#points = k3d.points(np_points.astype(np.float32), sys_colors.astype(np.uint32), point_size=2.0, shader='flat')
#plot += points
#sys_colors = np.array(colors[(num_coords[0] + num_coords[1]):(num_coords[0] + num_coords[1] + num_coords[2])])
#np_points = np.array(sys_coords[(num_coords[0] + num_coords[1]):(num_coords[0] + num_coords[1] + num_coords[2])])
#points = k3d.points(np_points.astype(np.float32), sys_colors.astype(np.uint32), point_size=2.0, shader='flat')
#plot += points

plot.display()
