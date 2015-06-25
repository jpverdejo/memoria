import wx
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy as np
import math

import sys

import time

from PIL import Image

class AtomsCanvas(glcanvas.GLCanvas):
  def __init__(self, parent):
    self.parent = parent

    self.width = 560
    self.height = 560

    glcanvas.GLCanvas.__init__(self, parent, -1)
    glutInit(sys.argv)

    self.init = False
    self.context = glcanvas.GLContext(self)

    # initial mouse position
    self.lastmousex = self.mousex = 30
    self.lastmousey = self.mousey = 30
    self.size = None
    self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
    self.Bind(wx.EVT_PAINT, self.OnPaint)
    self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
    self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
    self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
    self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
    self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    self.Bind(wx.EVT_SIZE, self.updateSize)

    self.atoms = []
    self.atoms_type = {}

    self.viewMode = 'all'
    self.viewLayer = 0
    self.layersX = {}
    self.layersY = {}
    self.layersZ = {}

    self.colorDirection = 'x'
    self.maxColor = 0

    self.playStatus = 'stop'

    self.currentT = 0

    self.playTimer = wx.Timer(self)
    self.Bind(wx.EVT_TIMER, self.play, self.playTimer)

    self.restartPosition()

    wx.CallAfter(self.updateSize, {})

  def updateSize(self, evt):
    size = self.GetSize()
    glViewport(0, 0, size.GetWidth(), size.GetHeight())
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, (size.GetWidth() + 0.0)/size.GetHeight(), 0.1, 100.0);
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    self.Refresh(False)

  def restartPosition(self):
    self.translationX = 0.0
    self.translationY = 0.0
    self.translationZ = 10.0

    self.rotationVectorX = self.rotationVectorY = self.rotationVectorZ = 0

  def OnMouseWheel(self, evt):
    # position viewer
    move = (evt.GetWheelRotation() + 0.0) / 10

    self.translationZ -= move
    self.Refresh(False)

  def OnKeyDown(self, evt):
    keycode = evt.GetKeyCode()

    delta = 0.1

    if keycode == wx.WXK_UP:
        self.translationY -= delta
    if keycode == wx.WXK_DOWN:
        self.translationY += delta
    if keycode == wx.WXK_LEFT:
        self.translationX -= delta
    if keycode == wx.WXK_RIGHT:
        self.translationX += delta

    self.Refresh(False)

  def play(self, evt):
    if self.playStatus == 'play':

      Ts = self.dataset.keys()
      Ts = [int(x) for x in Ts]
      Ts.sort()

      for t in Ts:
        if t > self.currentT:
          self.currentT = t
          self.parent.setT(self.currentT)
          self.playTimer.Start(100, wx.TIMER_ONE_SHOT)
          self.OnDraw()
          break

      Ts.sort(reverse=True)
      max_t = Ts[0]
      if t == max_t:
        self.parent.playStop({})

  def centerObject(self, atoms):
    firstx = lastx = firsty = lasty = firstz = lastz = False
    for atom_id, atom in atoms.iteritems():
      x, y, z = atom

      if firstx == False or x < firstx:
        firstx = x
      if lastx == False or x > lastx:
        lastx = x

      if firsty == False or y < firsty:
        firsty = y
      if lasty == False or y > lasty:
        lasty = y

      if firstz == False or z < firstz:
        firstz = z
      if lastz == False or z > lastz:
        lastz = z

    objectcenterx = float(firstx + lastx) / 2
    objectcentery = float(firsty + lasty) / 2
    objectcenterz = float(firstz + lastz) / 2

    tmp_atoms = {}
    for atom_id, atom in atoms.iteritems():
      x, y, z = atom

      # Center the cube to 0,0,0 in order to
      # rotate it on itself
      x -= objectcenterx
      y -= objectcentery
      z -= objectcenterz

      tmp_atoms[atom_id] = (x, y, z)

    return tmp_atoms

  def setAtoms(self, atoms, types):
    self.mode = 'design'
    self.atoms = atoms
    self.atoms_type = {}

    for atom_id, atom in self.atoms.iteritems():
      atom_key = "_".join(str(x) for x in atom)
      self.atoms_type[atom_id] = types[atom_key]

  def setDataset(self, atoms, dataset):
    self.mode = 'visualization'
    self.dataset = dataset
    self.layersX = {}
    self.layersY = {}
    self.layersZ = {}

    Ts = dataset.keys()
    if len(Ts):
      Ts.sort()
      self.currentT = Ts[0]
      self.parent.setT(self.currentT)

      atom_ids = dataset[self.currentT]['atoms'].keys()

      if len(atom_ids):
        atom_ids.sort()
        x,y,z = dataset[self.currentT]['atoms'][atom_ids[0]]

        if x > 0 and x > y and x > z:
          self.colorDirection = 'x'
          self.maxColor = abs(x)
        if y > 0 and y > x and y > z:
          self.colorDirection = 'y'
          self.maxColor = abs(y)
        if z > 0 and z > x and z > y:
          self.colorDirection = 'z'
          self.maxColor = abs(z)
    else:
      self.currentT = 0

    self.plotData = []
    for t, data in dataset.iteritems():
      if self.colorDirection == 'x':
        M = data['Mx']
      if self.colorDirection == 'y':
        M = data['My']
      if self.colorDirection == 'z':
        M = data['Mz']

      self.plotData.append((data['intensity'], M))

    self.atoms = {}

    factor = False

    # Normalize the values
    for atom_id, atom in atoms.iteritems():
      for value in atom:
        if value > 0 and ((not factor) or value < factor):
          factor = value

    for atom_id, atom in atoms.iteritems():
      x, y, z = atom

      if x not in self.layersX:
        self.layersX[x] = []
      if y not in self.layersY:
        self.layersY[y] = []
      if z not in self.layersZ:
        self.layersZ[z] = []

      self.layersX[x].append(atom_id)
      self.layersY[y].append(atom_id)
      self.layersZ[z].append(atom_id)

      if factor:
        x = x/factor
        y = y/factor
        z = z/factor

      self.atoms[atom_id] = (x, y, z)

    self.OnDraw()

  def OnEraseBackground(self, event):
    pass # Do nothing, to avoid flashing on screen.

  def DoSetViewport(self):
    size = self.size = self.GetClientSize()
    size = min(size.width, size.height)
    self.SetCurrent(self.context)
    glViewport(0, 0, size, size)

  def OnPaint(self, event):
    dc = wx.PaintDC(self)
    self.SetCurrent(self.context)
    if not self.init:
      self.InitGL()
      self.init = True
    self.OnDraw()

  def OnMouseDown(self, evt):
    self.CaptureMouse()
    self.mousex, self.mousey = self.lastmousex, self.lastmousey = evt.GetPosition()

  def OnMouseUp(self, evt):
    self.ReleaseMouse()

  def OnMouseMotion(self, evt):
    if evt.Dragging() and evt.LeftIsDown():
      self.lastmousex, self.lastmousey = self.mousex, self.mousey
      self.mousex, self.mousey = evt.GetPosition()

      self.rotationVectorX -= self.lastmousex - self.mousex
      self.rotationVectorY -= self.lastmousey - self.mousey

      wx.CallAfter(self.parent.axesD.update)
      wx.CallAfter(self.parent.axesV.update)

      self.Refresh(False)

  def InitGL(self):
    glMatrixMode(GL_PROJECTION)
    glFrustum(-0.5, 0.5, -0.5, 0.5, 1.0, 100.0)

    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    self.updateSize({})

  def getVectorColor(self, vector):
    x, y, z = vector

    value = x
    if self.colorDirection == 'y':
      value = y
    if self.colorDirection == 'z':
      value = z

    color_delta = 1 / self.maxColor
    color_base = [0, 1, 0]

    color_factor = [color_delta, -color_delta, 0]
    if value < 0:
      color_factor = [0, -color_delta, color_delta]

    color_diff = [diff * abs(value) for diff in color_factor]
    color = [color_base[0] + color_diff[0], color_base[1] + color_diff[1], color_base[2] + color_diff[2], 1];

    return color

  def drawVector(self, vector):
    length = 0.5
    color = self.getVectorColor(vector)

    # perpendicular_vector = self.perpendicular_vector(vector)
    perpendicular_vector = np.cross(vector, (0,0,1))
    angle_radians = self.angle_between(vector, (0,0,1))
    angle = math.degrees(angle_radians)

    vx, vy, vz = perpendicular_vector

    glMaterialfv(GL_FRONT,GL_DIFFUSE,color)
    glRotate(-angle, vx, vy, vz)
    q = gluNewQuadric()
    gluCylinder( q , 0.15 , 0.05 , length , 30 , 30 )
    glTranslate(0,0,length)
    glutSolidCone(0.2, 0.3, 30, 30)
    glTranslate(0,0,-length)
    glRotate(angle, vx, vy, vz)
    glMaterialfv(GL_FRONT,GL_DIFFUSE,[1, 1, 1, 1])

  # Next 2 function got from http://stackoverflow.com/a/13849249
  def unit_vector(self, vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

  def angle_between(self, v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

      >>> angle_between((1, 0, 0), (0, 1, 0))
      1.5707963267948966
      >>> angle_between((1, 0, 0), (1, 0, 0))
      0.0
      >>> angle_between((1, 0, 0), (-1, 0, 0))
      3.141592653589793
    """
    v1_u = self.unit_vector(v1)
    v2_u = self.unit_vector(v2)
    angle = np.arccos(np.dot(v1_u, v2_u))
    if np.isnan(angle):
      if (v1_u == v2_u).all():
        return 0.0
      else:
        return np.pi
    return angle

  def getCurrentImage(self):
    start = time.clock()
    self.SetCurrent(self.context)
    # Export to PNG
    size = self.GetClientSize()
    data = glReadPixels(0, 0, size.width, size.height, GL_RGBA, GL_UNSIGNED_BYTE)
    image = Image.fromstring("RGBA", (size.width, size.height), data)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    # print "get image: %f" % (time.clock() - start)

    return image

  def export(self, filename):
    image = self.getCurrentImage()
    image.save(filename, 'PNG')

  def OnDraw(self):
    self.SetCurrent(self.context)
    if (not bool(glCheckFramebufferStatus)) or glCheckFramebufferStatus(GL_DRAW_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE:
      # clear color and depth buffers
      glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

      glLoadIdentity();
      glRotate(180, 1, 0, 0)
      # Translate and rotate the image (or 'moving the camera')
      glTranslatef(self.translationX, self.translationY, self.translationZ)

      glRotate(self.rotationVectorY, 1, 0, 0)
      glRotate(self.rotationVectorX, 0, 1, 0)
      glRotate(self.rotationVectorZ, 0, 0, 1)

      # Default color
      color = [1, 1, 1, 1]
      glMaterialfv(GL_FRONT,GL_DIFFUSE,color)

      colors = {
        'vertex': [1, 1, 1, 1],
        'body': [1, 0, 0, 1],
        'face': [1, 1, 0, 1]
      }

      glPushMatrix()

      if self.mode == 'design' or self.viewMode == 'all':
        atoms = self.atoms
      else:
        layers = self.layersX

        atoms = {}

        if self.viewMode == 'y':
          layers = self.layersY
        if self.viewMode == 'z':
          layers = self.layersZ

        if self.viewLayer in layers:
          layer = layers[self.viewLayer]

          for atom_id in layer:
            atoms[atom_id] = self.atoms[atom_id]

      atoms = self.centerObject(atoms)

      for atom_id, atom in atoms.iteritems():
        x, y, z = atom

        glTranslate(x, y, z)

        if self.mode == 'design':
          atom_color = colors[self.atoms_type[atom_id]]
          if atom_color != color:
            color = atom_color
            glMaterialfv(GL_FRONT,GL_DIFFUSE,color)

          glutSolidSphere(0.2, 15, 15)
        else:
          dataset = self.dataset[self.currentT]['atoms']
          vector = dataset[atom_id]
          self.drawVector(vector)

        glTranslate(-x, -y, -z)

      glPopMatrix()

      # push into visible buffer
      self.SwapBuffers()

      self.Refresh(False)
