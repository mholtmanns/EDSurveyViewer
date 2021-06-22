#!/usr/bin/env python
# coding: utf-8

# Copyright [2021] [Markus Hoff-Holtmanns]

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#************************************************************************#
# This script accesses the public API of EDSM (https://www.edsm.net)
# to retrieve a list of discovered systems in the Space simulation game
# Elite Dangerous (https://www.elitedangerous.com/) in order to visualize
# them in 3D.
# 
# Start this file in a Jupyter notebook with k3d installed, see
# https://github.com/K3D-tools/K3D-jupyter for more details.
#
# Given a set of systems as reference this will retrieve all EDSM listed
# systems either in a spherical or a cuboid region around these reference
# systems. The amount of systems is constrained by the radius or cube edge
# length specified, bounded by EDSM max values.
#
# The retrieved systems are then visualized in 3d where the coloring of
# systems depends on the number of bodies in the system. The more bodies,
# the more red will the system point appear.

from __future__ import print_function
import json
import urllib.parse as parse
import urllib.request as rq
import numpy as np
import k3d
import re

# Define this for spherical queries, EDSM max is 100
RADIUS = 100
# Define this for cube queries, EDSM max edge length is 200
SIZE = 200
# Spherical
s_baseurl = 'https://www.edsm.net/api-v1/sphere-systems?showCoordinates=1&radius={}&systemName='.format(RADIUS)
# Cube
c_baseurl = 'https://www.edsm.net/api-v1/cube-systems?showCoordinates=1&size={}&systemName='.format(SIZE)

baseurl = c_baseurl

# List all systems you want to see vicinity data about. They MUST exist in EDSM.
base_systems=[
    "Graea Hypue QL-V b19-15",
    "Graea Hypue LS-S d4-83",
    "Graea Hypue LS-S d4-3",
    "Graea Hypue HX-S d4-2",
    ]

# Try to infer the mass type from the system name
def mass_type(system):
    reg = re.split("\s[A-Z]{2}-[A-Z]\s", system)
    if len(reg) > 1:
        return reg[1]
    else:
        return 'd'

sys_coords = []
colors = []
num_coords = []
max_bodies = 1
names = {}

# Iterate over the reference systems and retrieve EDSM JSON data
for count, g in enumerate(base_systems):
    url = baseurl + parse.quote(format(g.strip()))
    response = rq.urlopen(url)
    r = response.read()
    systems = json.loads(r.decode('utf-8'))
    # num_coords.append(len(systems))
    print (len(systems))
    #print (systems)

    # Iterate over the systems found and store body count for
    # the color map and coordinates for spatial placement
    count_per_set = 0
    for s in systems:
        # Avoid duplication
        if s['name'] in names:
            continue
        else:
            names[s['name']] = mass_type(s['name'])
        count_per_set = count_per_set + 1
        bc = s['bodyCount']
        # Some systems don't seem to have a body count
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

    num_coords.append(count_per_set)

print (num_coords)
#print (sys_coords)
#print (max_bodies)

# Map colors depending on the body count
# Pretty naive, simply decrease the green and blue component
# the more bodies there are in a system
# [ToDo: think of an exponential curve or something to better
#        distinguish >30 from ~10 body systems]
for k in range(len(colors)):
    color = 300 - int(colors[k]*300/max_bodies)
    if color <= 255:
        g = color
        b = 0
    else:
        g = 255
        b = color - 255
    colors[k] = (255 << 16) + (g << 8) + b


plot = k3d.plot()
plot.background_color = 0x808080
start = 0
# Add seperate point objects for each reference system. This way
# they can be enabled/disabled seperately
for n in num_coords:
    np_points = np.array(sys_coords[start:(start + n)])
    sys_colors = np.array(colors[start:(start + n)])
    points = k3d.points(np_points.astype(np.float32), sys_colors.astype(np.uint32), point_size=2.0, shader='flat')
    plot += points
    start = start + n

plot.display()
