#! /usr/bin/env python3

# Very basic utilities for observing colors in a (s)css file
# TODO
# make this instalable as a separate module usable from anywhere
# improve color similarity calculations

import os.path as osp
import colorsys
import re

from jinja2 import Environment

def rgb_to_hsv(r, g, b):
    """ this pretty much returns the data I want, 
        but I think there might be some floating point rounding issues

        returns h,s,v as ints

    """
    maxc = max(r, g, b)
    minc = min(r, g, b)
    v = maxc
    if minc == maxc:
        return 0, 0, int(round(v*100, 2))
    s = (maxc-minc) / maxc
    rc = (maxc-r) / (maxc-minc)
    gc = (maxc-g) / (maxc-minc)
    bc = (maxc-b) / (maxc-minc)
    if r == maxc:
        h = bc-gc
    elif g == maxc:
        h = 2.0+rc-bc
    else:
        h = 4.0+gc-rc
    # h = (h/6.0) % 1.0
    h = int(h*60)
    return h, int(round(s, 2)*100), int(round(v, 2)*100)

def hex2rgb(color_data):
    """ hex color as str > rgb tuple """
    hex_val = color_data['hex'].strip('#')
    rgb = [int(i, base=16) for i in (hex_val[0:2], hex_val[2:4], hex_val[4:6])]
    return rgb

def get_distance(a, b):
    """ distance/difference between 2 rgb colors"""
    # print(a, b)
    # print(*zip(a,b))
    dis = [max(i)-min(i) for i in zip(a,b)]
    return tuple(dis)

def find_similar_colors():
    color_names = []

    with open('main.scss') as fd:
        color_def_re = re.compile('(?P<name>\$[-_a-z0-9]*?):\s?(?P<hex>#[A-Za-z0-9]{6});')
        lines = fd.readlines()
        for no, line in enumerate(lines, start=1):
            color_name = re.search(color_def_re, line)
            if color_name:
                cd = color_name.groupdict()
                cd.update({'line':no})
                color_names.append(cd)

    color_names.sort(key=lambda i : i['name'])
    color_data = [i.update({'rgb': hex2rgb(i)}) for i in color_names]
    color_data = [i.update({'hsv': rgb_to_hsv(*[j/255 or 0 for j in i['rgb']])}) for i in color_names]

    for ind, i in enumerate(color_names):
        print('{} hsv:{}'.format(i['name'], i['hsv']))
        # get distances for all the color coords, set a threshold, show similar colors
        threshold = 12
        hsv = i['hsv']
        for j in color_names[ind+1:]:
            hsvab = zip(hsv, j['hsv'])
            distance = [max(k)-min(k) for k in hsvab]
            # Saturation is very similar for dark-gray and light-gray
            if all([n<threshold for n in distance]):
                print('\t{} {} distance: {}'.format(j['name'], j['hsv'], distance))

def generate_color_map(cssfn):
    """ this saves some HTML with a color chart of the colors used in the specified (S)CSS file """
    with open(cssfn) as fd:
        css = fd.read()
    
    # use finditer in case someday I want to get line numbers 
    all_colors_re = re.finditer('(rgba\(\d+,\s*?\d+,\s*?\d+, \d.\d\);|#[A-Za-z0-9]{6};)', css)
    all_colors = [i.groups(1)[0] for i in all_colors_re]
    # get colors defined as scss variables 
    scss_vars_re = re.finditer('(\$[-a-zA-Z0-9_]+):\s*?(#[A-Za-z0-9]{6};|rgba\(\d+,\s*?\d+,\s*?\d+, \d.\d\);)', css)
    scss_vars = {}
    for i in scss_vars_re:
        grp = i.groups(1)
        scss_vars[grp[1]] = grp[0]

    color_values = set()
    for col in all_colors:
        # gets computed values for colors (h,s,v)
        if not 'rgb' in col:
            rgb_floats = [ int(i, base=16)/255 for i in (col[1:3], col[3:5], col[5:7])]
        else:
            col_vals = col[5:-1].split(',')
            rgb_floats = [int(i)/255 for i in col_vals[0:3]]

        col_data = (col, rgb_to_hsv(*rgb_floats), scss_vars.get(col), tuple(rgb_floats))
        color_values.add(col_data)

    # incremental sort colors by rgb values
    color_values = list(color_values)
    color_values.sort(key=lambda i: i[3][0])
    color_values.sort(key=lambda i: i[3][1])
    color_values.sort(key=lambda i: i[3][2], reverse=True)

    for i in color_values:
        print(i[0:3])

    # jinja2 Environment
    env = Environment()

    with open('colormap_template.html', mode='r') as fd:
        tmpl = env.from_string(fd.read())
        rendered = tmpl.render(all_colors=color_values)
        with open('colormap.html', mode='w') as fd2:
            fd2.write(rendered)

# find_similar_colors()
generate_color_map('main.scss')
