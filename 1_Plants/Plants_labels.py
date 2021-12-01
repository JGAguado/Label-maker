#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
------------------------------------------------------------
%   File: template_2_printable.py
%   Description: 
%   Author: J.G.Aguado
%   Email: jon-garcia@hotmail.com
%   Date of creation: 8/19/2021
------------------------------------------------------------
"""
import datetime
import numpy as np
import math
import cairo
import json

def draw_image(ctx, image, top, left, height, width, rot=0):
    """Draw a scaled image on a given context."""
    image_surface = cairo.ImageSurface.create_from_png(image)
    # calculate proportional scaling
    img_height = image_surface.get_height()
    img_width = image_surface.get_width()
    width_ratio = float(width) / float(img_width)
    height_ratio = float(height) / float(img_height)
    scale_xy = min(height_ratio, width_ratio)
    # scale image and add it
    ctx.save()
    ctx.rotate(rot*math.pi/180)
    ctx.translate(left, top)
    ctx.scale(scale_xy, scale_xy)
    ctx.set_source_surface(image_surface)

    ctx.paint()
    ctx.restore()

def plot_parameter(ctx, parameter, value=False, thick=5, angle=270):
    alpha = np.deg2rad(angle)
    beta = 2*math.pi - alpha

    rel_range = parameter['rel_range']
    abs_range = parameter['abs_range']
    left = parameter['position'][0]
    top = parameter['position'][1]
    radius = parameter['radius']

    if rel_range[0] < abs_range[0] or rel_range[1] > abs_range[1]:
        print('Error: rel_range values are not in abs_range')
        return

    value = (np.mean(rel_range)-abs_range[0])/np.abs(abs_range[1]-abs_range[0])*alpha

    """ Icon """
    size = radius
    draw_image(ctx, parameter['icon'],
               top+radius-size/2,
               left+radius-size/2,
               size,
               size)

    """ Value """
    ctx.set_line_width(1)
    if 'water' in parameter['icon']:
        ctx.set_source_rgb(0,191/255,255/255)
    elif 'sunny' in parameter['icon']:
        ctx.set_source_rgb(255/255,215/255,0)
    elif 'thermometer' in parameter['icon']:
        ctx.set_source_rgb(255/255,69/255,0)
    elif 'leaf' in parameter['icon']:
        ctx.set_source_rgb(50/255,205/255,50/255)
    #
    ctx.move_to(left+radius+(radius-thick)*math.cos(math.pi/2+beta/2), top+radius+(radius-thick)*math.sin(math.pi/2+beta/2))
    ctx.arc(left+radius, top+radius, radius, math.pi/2+beta/2, math.pi/2+value)
    ctx.line_to(left+radius+radius*math.cos(math.pi/2+value), top+radius+radius*math.sin(math.pi/2+value))
    ctx.arc_negative(left+radius, top+radius, radius-thick, math.pi/2+value, math.pi/2+beta/2)
    ctx.fill()
    ctx.stroke()


    """ Contour """
    ctx.set_source_rgb(0, 0, 0)
    ctx.move_to(left+radius+(radius-thick)*math.cos(math.pi/2+beta/2), top+radius+(radius-thick)*math.sin(math.pi/2+beta/2))
    ctx.arc(left+radius, top+radius, radius, math.pi/2+beta/2, math.pi/2-beta/2)
    ctx.line_to(left+radius+radius*math.cos(math.pi/2-beta/2), top+radius+radius*math.sin(math.pi/2-beta/2))
    ctx.arc_negative(left+radius, top+radius, radius-thick, math.pi/2-beta/2, math.pi/2+beta/2)
    ctx.stroke()

    """ Recomendation"""
    if 'recomended' in parameter:
        label = parameter['recomended']
        xbearing, ybearing, width, height, dx, dy = ctx.text_extents(label)
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_font_size(parameter['font_size']-2)
        ctx.select_font_face(parameter['font_type'],
                             cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_NORMAL)
        ctx.move_to(left + radius + parameter['font_xoff'] - width / 2, top + 2.7 * radius)
        ctx.show_text(label)

def main(path, simulation=True):
    with open(path) as json_file:
        config = json.load(json_file)

    surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
                                 config['general']['size'][0],
                                 config['general']['size'][1])
    ctx = cairo.Context(surface)
    ctx.scale(1, 1)

    ctx.rectangle(0, 0, config['general']['size'][0], config['general']['size'][1])
    # ctx.set_source_rgb(config['general']['background'][0], config['general']['background'][1], config['general']['background'][2])
    pattern = cairo.LinearGradient(0, 0, 0, config['general']['size'][1])
    pattern.add_color_stop_rgb(0, 50/255, 205/255, 50/255)
    pattern.add_color_stop_rgb(1, 0.5, 0.5, 1)
    ctx.set_source(pattern)
    ctx.fill()

    ctx.set_line_width(10)
    r = config['general']['radius']
    ctx.set_source_rgb(0, 0, 0)
    ctx.arc(r, r, r, math.pi, 3*math.pi/2)
    ctx.arc(config['general']['size'][0]-r, r, r, 3*math.pi/2, 0)
    ctx.arc(config['general']['size'][0]-r, config['general']['size'][1]-r, r, 0, math.pi/2)
    ctx.arc(r, config['general']['size'][1]-r, r, math.pi/2, math.pi)
    ctx.close_path()
    ctx.stroke()

    """ Title """
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_font_size(config['title']['font_size'])
    ctx.select_font_face(config['title']['font_type'],
                         cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_NORMAL)
    ctx.move_to(config['title']['position'][0], config['title']['position'][1])
    ctx.show_text(config['title']['value'])

    """ Subtitle """
    ctx.set_font_size(config['subtitle']['font_size'])
    ctx.select_font_face(config['subtitle']['font_type'],
                         cairo.FONT_SLANT_ITALIC,
                         cairo.FONT_WEIGHT_NORMAL)
    ctx.move_to(config['subtitle']['position'][0], config['subtitle']['position'][1])
    ctx.show_text(config['subtitle']['value'])

    """ Life-cycle"""
    lifespan = config['life-cycle']['span']
    xbearing, ybearing, width, height, dx, dy = ctx.text_extents(lifespan)

    ctx.set_font_size(config['subtitle']['font_size'])
    ctx.select_font_face(config['subtitle']['font_type'],
                         cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_NORMAL)
    ctx.move_to(config['general']['size'][0] - 1.1*width, config['title']['position'][1])
    ctx.show_text(lifespan)

    draw_image(ctx, config['life-cycle']['icon'],
               config['title']['position'][0],
               config['general']['size'][0] - 1.2*width - height,
               1.2*height,
               1.2*height)

    """ Image """
    draw_image(ctx, config['image']['path'],
               config['image']['position'][1],
               config['image']['position'][0],
               config['image']['size'][0],
               config['image']['size'][1])


    """ Parameters """

    plot_parameter(ctx, config['parameters']['moisture'])
    plot_parameter(ctx, config['parameters']['temperature'])
    plot_parameter(ctx, config['parameters']['light'])
    plot_parameter(ctx, config['parameters']['fertility'])


    output = path.split('.')[0] + '_label_2.png'
    surface.write_to_png(output)

if __name__ == "__main__":

    paths = ['examples/Basil/Basil.json',
             'examples/Coriander/Coriander.json'
    ]

    for path in paths:
        main(path, simulation=True)

