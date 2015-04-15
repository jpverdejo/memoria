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

class AtomsCanvas(glcanvas.GLCanvas):
  def __init__(self, parent):
    self.parent = parent

    self.width = 560
    self.height = 560

    glcanvas.GLCanvas.__init__(self, parent, -1)

    self.init = False
    self.context = glcanvas.GLContext(self)

    # initial mouse position
    self.lastmousex = self.mousex = 30
    self.lastmousey = self.mousey = 30
    self.size = None
    self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
    self.Bind(wx.EVT_SIZE, self.OnSize)
    self.Bind(wx.EVT_PAINT, self.OnPaint)
    self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
    self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
    self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
    self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
    self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    self.Bind(wx.EVT_SIZE, self.OnSize)

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

  def updateSize(self, evt):
    size = self.GetSize()
    glViewport(0, 0, size.GetWidth(), size.GetHeight())
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
        self.translationY += delta
    if keycode == wx.WXK_DOWN:
        self.translationY -= delta
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

      # Invert x and y positions to make it look logical
      tmp_atoms[atom_id] = (y, x, z)

    return tmp_atoms

  def setAtoms(self, atoms, types):
    self.mode = 'design'
    self.atoms = atoms
    self.atoms_type = {}

    for atom_id, atom in self.atoms.iteritems():
      atom_key = "_".join(str(x) for x in atom)
      self.atoms_type[atom_id] = types[atom_key]

    self.atoms = self.centerObject(self.atoms)

  def setDataset(self, atoms, dataset):
    self.mode = 'visualization'
    self.dataset = dataset

    Ts = dataset.keys()
    if len(Ts):
      Ts.sort()
      self.currentT = Ts[0]
      self.parent.setT(self.currentT)

      atom_ids = dataset[self.currentT]['atoms'].keys()

      if len(atom_ids):
        atom_ids.sort()
        x,y,z = dataset[self.currentT]['atoms'][atom_ids[0]]

        if x > 0:
          self.colorDirection = 'x'
          self.maxColor = abs(x)
        if y > 0:
          self.colorDirection = 'y'
          self.maxColor = abs(y)
        if z > 0:
          self.colorDirection = 'z'
          self.maxColor = abs(z)
    else:
      self.currentT = 0

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

    self.atoms = self.centerObject(self.atoms)

    self.OnDraw()

  def OnEraseBackground(self, event):
    pass # Do nothing, to avoid flashing on screen.

  def OnSize(self, event):
    self.DoSetViewport()
    event.Skip()

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

      self.Refresh(False)

  def InitGL(self):
    glMatrixMode(GL_PROJECTION)
    glFrustum(-0.5, 0.5, -0.5, 0.5, 1.0, 100.0)

    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

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
    length = 0.3
    color = self.getVectorColor(vector)

    # perpendicular_vector = self.perpendicular_vector(vector)
    perpendicular_vector = np.cross(vector, (0,0,1))
    angle_radians = self.angle_between(vector, (0,0,1))
    angle = math.degrees(angle_radians)

    # print vector
    # print perpendicular_vector
    # print angle_radians
    # print angle

    vx, vy, vz = perpendicular_vector

    glMaterialfv(GL_FRONT,GL_DIFFUSE,color)
    glRotate(-angle, vx, vy, vz)
    q = gluNewQuadric()
    gluCylinder( q , 0.05 , 0.05 , length , 30 , 30 )
    glTranslate(0,0,length)
    glutSolidCone(0.1, 0.2, 30, 30)
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

  def OnDraw(self):
    # clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity();
    glRotate(180, 1, 0, 0)
    # Translate and rotate the image (or 'moving the camera')
    glTranslatef(self.translationX, self.translationY, self.translationZ)

    glRotate(self.rotationVectorY, 1, 0, 0)
    glRotate(self.rotationVectorX, 0, 1, 0)
    glRotate(self.rotationVectorZ, 0, 0, 1)

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

      atom_key = "_".join(str(x) for x in atom)

      glTranslate(x, y, z)

      if self.mode == 'design':
        color = colors[self.atoms_type[atom_id]]
        glMaterialfv(GL_FRONT,GL_DIFFUSE,color)

        glutSolidSphere(0.2, 30, 30)
      else:
        dataset = self.dataset[self.currentT]['atoms']
        vector = dataset[atom_id]
        self.drawVector(vector)

      glTranslate(-x, -y, -z)

    glPopMatrix()

    # Export to PNG
    # size = self.size = self.GetClientSize()
    # size = min(size.width, size.height)
    # data = glReadPixels(0, 0, size, size, GL_RGBA, GL_UNSIGNED_BYTE)
    # image = Image.fromstring("RGBA", (size, size), data)
    # image = image.transpose(Image.FLIP_TOP_BOTTOM)
    # image.save('out.png', 'PNG')

    # push into visible buffer
    self.SwapBuffers()

    wx.CallAfter(self.parent.axesD.update)
    wx.CallAfter(self.parent.axesV.update)
    self.Refresh(False)