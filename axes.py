import wx
from wx import glcanvas
from OpenGL.GL import *

#from OpenGL import GLU
#from OpenGL import GL
#from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy as np
import math
import operator

from PIL import Image

from pprint import pprint

class Axes(glcanvas.GLCanvas):
  def __init__(self, parent):
    self.parent = parent

    self.width = 200
    self.height = 200

    glcanvas.GLCanvas.__init__(self, parent, -1, size=(230, 200))

    self.init = False
    self.context = glcanvas.GLContext(self)

    self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
    self.Bind(wx.EVT_PAINT, self.OnPaint)


  def OnEraseBackground(self, event):
    pass # Do nothing, to avoid flashing on screen.

  def OnSize(self, event):
    self.DoSetViewport()
    event.Skip()

  def DoSetViewport(self):
    if self.IsShown():
      self.SetCurrent(self.context)
      glViewport(0, 0, 200, 200)

  def OnPaint(self, event):
    if self.IsShown():
      dc = wx.PaintDC(self)
      self.SetCurrent(self.context)
      if not self.init:
        self.InitGL()
        self.init = True
      self.OnDraw()

  def InitGL(self):
    glMatrixMode(GL_PROJECTION)
    glFrustum(-0.5, 0.5, -0.5, 0.5, 1.0, 100.0)

    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

  def update(self):
    wx.CallAfter(self.DoSetViewport)
    wx.CallAfter(self.OnDraw)

  def OnDraw(self):
    self.SetCurrent(self.context)
    if glCheckFramebufferStatus(GL_DRAW_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE:
      # clear color and depth buffers
      glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

      glLoadIdentity();
      glRotate(180, 1, 0, 0)

      # Translate and rotate the image (or 'moving the camera')
      # glTranslatef(self.parent.GetParent().GetParent().canvas.translationX, self.parent.GetParent().GetParent().canvas.translationY, self.parent.GetParent().GetParent().canvas.translationZ)
      glTranslatef(0, 0, 3)

      glRotate(self.parent.GetParent().GetParent().canvas.rotationVectorY, 1, 0, 0)
      glRotate(self.parent.GetParent().GetParent().canvas.rotationVectorX, 0, 1, 0)
      glRotate(self.parent.GetParent().GetParent().canvas.rotationVectorZ, 0, 0, 1)

      glPushMatrix()

      length = 1

      glMaterialfv(GL_FRONT,GL_DIFFUSE,[1, 0, 0, 1])
      z = gluNewQuadric()
      gluCylinder( z , 0.05 , 0.05 , length , 30 , 30 )
      glTranslate(0,0,length)
      glutSolidCone(0.1, 0.2, 30, 30)
      glTranslate(0,0,-length)

      glMaterialfv(GL_FRONT,GL_DIFFUSE,[0, 0, 1, 1])
      glRotate(90, 0, 1, 0)
      x = gluNewQuadric()
      gluCylinder( x , 0.05 , 0.05 , length , 30 , 30 )
      glTranslate(0,0,length)
      glutSolidCone(0.1, 0.2, 30, 30)
      glTranslate(0,0,-length)
      glRotate(-90, 0, 1, 0)

      glMaterialfv(GL_FRONT,GL_DIFFUSE,[0, 1, 0, 1])
      glRotate(-90, 1, 0, 0)
      y = gluNewQuadric()
      gluCylinder( y , 0.05 , 0.05 , length , 30 , 30 )
      glTranslate(0,0,length)
      glutSolidCone(0.1, 0.2, 30, 30)
      glTranslate(0,0,-length)

      glPopMatrix()

      # push into visible buffer
      self.SwapBuffers()
      self.Refresh(False)