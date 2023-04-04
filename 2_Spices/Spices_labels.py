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
import yaml

def frame(config, spice):
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
                                 config['general']['size'][0],
                                 config['general']['size'][1])
    pad = 2
    grad = config['general']['color grad']
    r, g, b = spice['color']
    r0, g0, b0 = r + grad, g + grad, b + grad
    r1, g1, b1 = r - grad, g - grad, b - grad

    ctx = cairo.Context(surface)
    ctx.scale(1, 1)
    ctx.set_source_rgb(0, 0, 0)
    ctx.rectangle(0, 0, config['general']['size'][0], config['general']['size'][1])
    ctx.fill()

    ctx.rectangle(pad, pad, config['general']['size'][0]-2*pad, config['general']['size'][1]-2*pad)
    pattern = cairo.LinearGradient(0, 0, 0, config['general']['size'][1])
    pattern.add_color_stop_rgb(0, r0 / 255, g0 / 255, b0 / 255)
    pattern.add_color_stop_rgb(1, r1 / 255, g1 / 255, b1 / 255)
    ctx.set_source(pattern)
    ctx.fill()

    roundrect(ctx, config['general']['pad'], config['general']['pad'],
              config['general']['size'][0] - 2 * config['general']['pad'],
              config['general']['size'][1] - 2 * config['general']['pad'],
              config['general']['radius'])
    return ctx, surface

def roundrect(ctx, x, y, width, height, rad=10, thickness=2, color=[255,255,255]):
    r,g,b = [x/255 for x in color]
    ctx.arc(x + rad, y + rad, rad,
                math.pi, 3 * math.pi / 2)

    ctx.arc(x + width - rad, y + rad, rad,
                3 * math.pi / 2, 0)

    ctx.arc(x + width - rad, y + height - rad,
                rad, 0, math.pi / 2)

    ctx.arc(x + rad, y + height - rad, rad,
                math.pi / 2, math.pi)

    ctx.close_path()
    ctx.set_source_rgb(r, g, b);
    ctx.fill_preserve();
    ctx.set_source_rgba(r, g, b);
    ctx.set_line_width(thickness);
    ctx.stroke();

def draw_image(ctx, image, xc, yc, width, height, angle=None):
    ctx.save()
    image_surface = cairo.ImageSurface.create_from_png(image)

    w = image_surface.get_width()
    h = image_surface.get_height()
    scale_xy = min(width/w, height/h)
    w = scale_xy * w
    h = scale_xy * h

    """ Best rotation """
    width_rot = []
    height_rot = []
    comb = []
    for theta in np.arange(0,91):
        theta = theta*math.pi/180
        width = w * abs(np.cos(theta)) + h * abs(np.sin(theta))
        height = w * abs(np.sin(theta)) + h * abs(np.cos(theta))

        width_rot.append(width)
        height_rot.append(height)
        comb.append(abs(1-abs(width/ height)))
    comb = np.array(comb)
    if angle is None:
        angle = np.argmin(comb)
    print(angle)

    """ Computations """
    angle = angle * math.pi / 180

    alpha = math.atan((h/2)/ (w/2))
    r = math.hypot(w/2, h/2)
    x, y = xc - r*np.cos(alpha), yc - r*np.sin(alpha)

    beta = alpha + angle
    xc1 = x + r * np.cos(beta)
    yc1 = y + r * np.sin(beta)

    x1, y1 = x + xc -xc1, y + yc - yc1

    # ****** Aux plotting lines  ******
    # ctx.move_to(0, 0)
    # ctx.line_to(xc, yc)
    # ctx.set_source_rgb(1, 0, 0)
    # ctx.stroke()
    #
    # ctx.move_to(0, 0)
    # ctx.line_to(x, y)
    # ctx.set_source_rgb(0, 1, 0)
    # ctx.stroke()
    #
    # ctx.move_to(x, y)
    # ctx.line_to(xc1, yc1)
    # ctx.set_source_rgb(0, 0, 1)
    # ctx.stroke()
    #
    # ctx.move_to(xc1, yc1)
    # ctx.line_to(x1, y1)
    # ctx.set_source_rgb(1, 0, 1)
    # ctx.stroke()

    """ Translate """
    ctx.translate(x1,y1)

    """ Rotate """
    ctx.rotate(angle)

    """ Scale & write """
    ctx.scale(scale_xy, scale_xy)
    ctx.set_source_surface(image_surface, 0, 0)
    ctx.paint()
    ctx.restore()
    return

def names(ctx, config, spice):
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_font_size(config['text']['size'])
    ctx.select_font_face(config['text']['type'],
                         cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_NORMAL)
    xc, yc, w, h = config['text']['x'], config['text']['y'],\
                   config['text']['width'], config['text']['height']

    for string, ii in zip([spice['es'], spice['en'], spice['de']], [-1, 0, 1]):
        text_props = ctx.text_extents(string)
        ts = w/text_props.width
        if ts < 1:
            size = config['text']['size'] - ((1-ts)*config['text']['scale'])

        elif ts > 1:
            size = config['text']['size'] + 2

        ctx.set_font_size(size)
        text_props = ctx.text_extents(string)

        nx = -text_props.width/2
        ny = text_props.height/2
        x = xc + nx
        y = yc + ii* h/3 + ny
        ctx.move_to(x, y)
        ctx.show_text(string)

def main(path, simulation=True):
    with open(path, 'rt', encoding='utf8') as yaml_file:
        config = yaml.load(yaml_file)

    """ Individual labels generator """
    labels = []
    for spice_type in config['spices']:
        for spice in config['spices'][spice_type]['items']:
            ctx, surface = frame(config, config['spices'][spice_type])

            draw_image(ctx, spice['img'],
                       config['image']['x'],
                       config['image']['y'],
                       config['image']['width'],
                       config['image']['height'])
            names(ctx, config, spice)

            output = '.\labels\\' + spice['es'] + '_label.png'
            surface.write_to_png(output)
            labels.append(output)
    """ Gropu by 24 labels """
    pad = 25
    w, h =  2480, 3508
    width, height = w-2*pad, h-2*pad
    a4 = cairo.ImageSurface(cairo.FORMAT_RGB24,w, h)
    ctx = cairo.Context(a4)
    ctx.scale(1, 1)
    ctx.set_source_rgb(1, 1, 1)
    ctx.rectangle(0, 0, w, h)
    ctx.fill()
    idx = 0
    for column in np.arange(pad, width, width/3):
        for row in np.arange(pad, height, height/8):
            ctx.save()
            image_surface = cairo.ImageSurface.create_from_png(labels[idx])
            w = image_surface.get_width()
            h = image_surface.get_height()
            scale_xy = min((width/3)/ w, (height/8) / h)
            w = scale_xy * w
            h = scale_xy * h
            ctx.translate(column, row)

            ctx.scale(scale_xy, scale_xy)
            ctx.set_source_surface(image_surface, 0, 0)
            ctx.paint()
            ctx.restore()

            idx = idx + 1

    output = '.\labels\Labels.png'
    a4.write_to_png(output)

if __name__ == "__main__":

    paths = ['config.yaml'
    ]

    for path in paths:
        main(path, simulation=True)

