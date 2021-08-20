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

    min_beta = (rel_range[0]-abs_range[0])/np.abs(abs_range[1]-abs_range[0])*alpha
    max_beta = (1 - (abs_range[1]-rel_range[1])/np.abs(abs_range[1]-abs_range[0])) *alpha

    """ Icon """
    size = radius
    draw_image(ctx, parameter['icon'],
               top+radius-size/2,
               left+radius-size/2,
               size,
               size)

    """ Minimum """
    ctx.set_line_width(thick)
    ctx.set_source_rgb(1, 0, 0)
    ctx.move_to(left+radius+(radius-thick/2)*math.cos(math.pi/2+beta/2), top+radius+(radius-thick/2)*math.sin(math.pi/2+beta/2))
    ctx.arc(left+radius, top+radius, radius-thick/2, math.pi/2+beta/2, math.pi/2+beta/2+min_beta)
    ctx.stroke()

    """ Maximum """
    ctx.move_to(left+radius+(radius-thick/2)*math.cos(math.pi/2+beta/2+max_beta), top+radius+(radius-thick/2)*math.sin(math.pi/2+beta/2+max_beta))
    ctx.arc(left+radius, top+radius, radius-thick/2, math.pi/2+beta/2+max_beta, math.pi/2-beta/2)
    ctx.stroke()

    """ Contour """
    ctx.set_line_width(1)
    ctx.set_source_rgb(0, 0, 0)
    ctx.move_to(left+radius+(radius-thick)*math.cos(math.pi/2+beta/2), top+radius+(radius-thick)*math.sin(math.pi/2+beta/2))
    ctx.arc(left+radius, top+radius, radius, math.pi/2+beta/2, math.pi/2-beta/2)
    ctx.move_to(left+radius+(radius-thick)*math.cos(math.pi/2+beta/2), top+radius+(radius-thick)*math.sin(math.pi/2+beta/2))
    ctx.arc(left+radius, top+radius, radius-thick, math.pi/2+beta/2, math.pi/2-beta/2)
    ctx.line_to(left+radius+radius*math.cos(math.pi/2-beta/2), top+radius+radius*math.sin(math.pi/2-beta/2))
    ctx.stroke()

    """ Value indicator """
    if value:
        val = (value - abs_range[0]) / np.abs(abs_range[1] - abs_range[0]) * alpha

        ctx.move_to(left + radius + radius * math.cos(math.pi / 2 + beta / 2 + val),
                    top + radius + radius * math.sin(math.pi / 2 + beta / 2 + val))
        ctx.line_to(left + radius + (radius+thick) * math.cos(math.pi / 2 + beta / 2 + val + 0.1),
                top + radius + (radius+thick) * math.sin(math.pi / 2 + beta / 2 + val + 0.1))
        ctx.line_to(left + radius + (radius+thick) * math.cos(math.pi / 2 + beta / 2 + val - 0.1),
                top + radius + (radius+thick) * math.sin(math.pi / 2 + beta / 2 + val - 0.1))
        ctx.line_to(left + radius + (radius) * math.cos(math.pi / 2 + beta / 2 + val),
                top + radius + (radius) * math.sin(math.pi / 2 + beta / 2 + val))
        ctx.fill_preserve()
        ctx.stroke()

        label = str(value) + ' ' + parameter['unit']
        xbearing, ybearing, width, height, dx, dy = ctx.text_extents(label)
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_font_size(parameter['font_size'])
        ctx.select_font_face(parameter['font_type'],
                             cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_NORMAL)
        ctx.move_to(left + radius + parameter['font_xoff']- width/2, top +2.7*radius)
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
    ctx.set_source_rgb(config['general']['background'][0], config['general']['background'][1], config['general']['background'][2])
    ctx.fill()

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

    """ Image """
    draw_image(ctx, config['image']['path'],
               config['image']['position'][1],
               config['image']['position'][0],
               config['image']['size'][0],
               config['image']['size'][1])


    """ Parameters """
    sim = 1
    if not simulation:
        sim = 0
    plot_parameter(ctx, config['parameters']['moisture'], sim*50)
    plot_parameter(ctx, config['parameters']['temperature'], sim*18)
    plot_parameter(ctx, config['parameters']['light'], sim*200)
    plot_parameter(ctx, config['parameters']['fertility'], sim*440)

    """ Simulated data """
    if simulation:
        """ Date """

        today = datetime.date.today()
        date = today.strftime("%d/%m")
        xbearing, ybearing, width, height, dx, dy = ctx.text_extents(date)
        ctx.set_font_size(config['subtitle']['font_size'])
        ctx.select_font_face(config['subtitle']['font_type'],
                             cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_NORMAL)
        ctx.move_to(config['general']['size'][0] - (1.1*width), config['subtitle']['position'][1])
        ctx.show_text(date)
        draw_image(ctx, 'src/sync.png',
                   config['subtitle']['position'][1]-15,
                   config['general']['size'][0] - 1.5*width,
                   20, 20)

        """ Battery status"""
        bat = str(85) + "%"
        draw_image(ctx, 'src/Battery/battery-90.png',
                   5-config['general']['size'][0],
                   5, 20, 20, 90)
        xbearing, ybearing, width, height, dx, dy = ctx.text_extents(bat)
        ctx.set_font_size(config['subtitle']['font_size'])
        ctx.select_font_face(config['subtitle']['font_type'],
                             cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_NORMAL)
        ctx.move_to(config['general']['size'][0] - width - 25, config['title']['position'][1])
        ctx.show_text(bat)

    output = path.split('.')[0] + '_label_1.png'
    surface.write_to_png(output)

if __name__ == "__main__":

    paths = ['examples/Basil/Basil.json',
             'examples/Coriander/Coriander.json'
    ]

    for path in paths:
        main(path, simulation=True)

