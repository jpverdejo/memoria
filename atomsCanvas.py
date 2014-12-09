import wx
from wx import glcanvas
from OpenGL.GL import *

#from OpenGL import GLU
#from OpenGL import GL
#from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class AtomsCanvas(glcanvas.GLCanvas):
  def __init__(self, parent):
    self.parent = parent


    self.width = 560
    self.height = 575

    glcanvas.GLCanvas.__init__(self, parent, -1, size=(self.width,self.height))

    self.init = False
    self.context = glcanvas.GLContext(self)
    
    # initial mouse position
    self.lastx = self.x = 30
    self.lasty = self.y = 30
    self.size = None
    self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
    self.Bind(wx.EVT_SIZE, self.OnSize)
    self.Bind(wx.EVT_PAINT, self.OnPaint)
    self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
    self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
    self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
    self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

    self.atoms = []

  def OnMouseWheel(self, evt):
    # position viewer
    print evt.GetWheelRotation()
    glScalef(evt.GetWheelRotation(), evt.GetWheelRotation(), 1.0);
    
  def setAtoms(self, atoms):
    self.atoms = atoms
    print atoms

  def OnEraseBackground(self, event):
    pass # Do nothing, to avoid flashing on MSW.

  def OnSize(self, event):
    wx.CallAfter(self.DoSetViewport)
    event.Skip()

  def DoSetViewport(self):
    self.SetCurrent(self.context)
    glViewport(0, 0, self.width, self.height)

  def OnPaint(self, event):
    dc = wx.PaintDC(self)
    self.SetCurrent(self.context)
    if not self.init:
      self.InitGL()
      self.init = True
    self.OnDraw()

  def OnMouseDown(self, evt):
    self.CaptureMouse()
    self.x, self.y = self.lastx, self.lasty = evt.GetPosition()

  def OnMouseUp(self, evt):
    self.ReleaseMouse()

  def OnMouseMotion(self, evt):
    if evt.Dragging() and evt.LeftIsDown():
      self.lastx, self.lasty = self.x, self.y
      self.x, self.y = evt.GetPosition()
      self.Refresh(False)

  def InitGL(self):
    # set viewing projection

    glMatrixMode(GL_PROJECTION)
    glFrustum(-0.5, 0.5, -0.5, 0.5, 1.0, 3.0)

    # position viewer
    glMatrixMode(GL_MODELVIEW)
    glTranslatef(0.0, 0.0, -3.0)

    # position object
    glRotatef(self.y, 1.0, 0.0, 0.0)
    glRotatef(self.x, 0.0, 1.0, 0.0)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)


  def OnDraw(self):
    # clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # use a fresh transformation matrix
    glPushMatrix()
    #glTranslate(1, 1, 0)
    glutSolidSphere(1, 30, 30)

    # glutSolidCone(0.5, 1, 30, 5)
    glPopMatrix()

    glRotatef((self.y - self.lasty), 0.0, 0.0, 1.0);
    glRotatef((self.x - self.lastx), 1.0, 0.0, 0.0);
    # push into visible buffer
    self.SwapBuffers()