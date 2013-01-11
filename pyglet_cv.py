#!/usr/bin/python

import math
import cv
import pyglet
from pyglet.gl import *
import pyglet.image
import Image
import random
import sys

class Video(object):
    def __init__(self):
        super(Video, self).__init__()
        cameraid = 0
        self.capture = cv.CaptureFromCAM(cameraid)
        if not self.capture:
            print "Error opening capture device"
            sys.exit (1)

        self.frame = cv.QueryFrame (self.capture)
        self.raw_video_image = cv.CreateImage(cv.GetSize(self.frame), 8, 3)
        (self.width, self.height) = cv.GetSize(self.frame)
        
    def get_video(self):
        self.raw_video_image = cv.QueryFrame (self.capture)
        cv.Flip(self.raw_video_image,None,-1)
        video_image = pyglet.image.ImageData(self.width, self.height, 
                                             "BGR", 
                                             self.raw_video_image.tostring()) 
        return video_image
    
if __name__ == '__main__':
    cv.NamedWindow("Depth")

    v_in = Video()
    
    window = pyglet.window.Window()
    window.width = 1280
    window.height = 960

    def update_images(dt):
        global v_in, video
        video = v_in.get_video()

    pyglet.clock.schedule_interval(update_images, 1/30.0)
        
    update_images(0.0)
    
    if video is not None:
        video_sprite = pyglet.sprite.Sprite(video)
        video_sprite.x = 0
        video_sprite.y = 0
        scale = window.width / v_in.width
        video_sprite.scale = scale

    eye = pyglet.image.load("eye.jpg")
    eye_sprite = pyglet.sprite.Sprite(eye)

    vertices = [
        200, 200,
        400, 400,
        0, 200]
    vertices_gl = (GLfloat * len(vertices))(*vertices)

    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, vertices_gl)

    @window.event
    def on_draw():

        window.clear()

        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        video_sprite.image = video
        video_sprite.draw()

        glDrawArrays(GL_TRIANGLES, 0, len(vertices) // 2)

        eye_sprite.x = random.randint(1,window.width)
        eye_sprite.y = random.randint(1,window.height)
        eye_sprite.scale = .2
        eye_sprite.draw()

    pyglet.app.run()
