import wx.grid
import math

class BitMapGrid(wx.grid.Grid):
  def __init__(self, parent):

    self.parent = parent

    self.rows = 10
    self.cols = 10

    self.figure = False

    self.width = self.height = 0

    wx.grid.Grid.__init__(self, parent, -1)

    self.cells = [[0 for x in xrange(self.cols)] for x in xrange(self.rows)]

    self.lastSelected = self.lastClicked = [0,0]

    self.calcCellSize()

    self.SetWindowStyleFlag( self.GetWindowStyle() & ~ wx.HSCROLL );
    self.SetCellHighlightPenWidth(0)
    # self.SetRowLabelSize(0)
    # self.SetColLabelSize(0)
    self.EnableEditing(False)
    self.DisableDragGridSize()

    self.CreateGrid(self.rows, self.cols)

    self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onSelectCell)
    self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.onClickCell)
    self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.onSelectRange)
    self.Bind(wx.EVT_CHAR_HOOK, self.disableKeyboard)

    self.Bind(wx.EVT_SIZE, self.updateSizeEvt)

  def updateSizeEvt(self, evt):
    self.updateSize()

  def calcCellSize(self):
    (self.width, self.height) = self.parent.content.GetSize()

    self.rowSize = math.ceil(self.height/(self.rows + 1))
    self.colSize = math.ceil(self.width/(self.cols + 1))

    self.cellSize = max(min(self.rowSize, self.colSize), 20)

    self.SetRowLabelSize(self.cellSize)
    self.SetColLabelSize(self.cellSize)

    self.SetDefaultColSize(self.cellSize)
    self.SetDefaultRowSize(self.cellSize)

  def updateSize(self):
    self.calcCellSize()
    newCells = [[0 for x in xrange(self.cols)] for x in xrange(self.rows)]


    colsDiff = self.cols - self.GetNumberCols()
    rowsDiff = self.rows - self.GetNumberRows()

    if colsDiff > 0:
      self.AppendCols(colsDiff)
    if colsDiff < 0:
      self.DeleteCols(0, (-1 * colsDiff))
    if rowsDiff > 0:
      self.AppendRows(rowsDiff)
    if rowsDiff < 0:
      self.DeleteRows(0, (-1 * rowsDiff))

    for j in xrange(self.cols):
      # j starts from 0, the label should start from 1
      self.SetColLabelValue(j, str(j + 1))

    for i in xrange(self.rows):
      for j in xrange(self.cols):
        value = 0

        try:
          value = self.cells[i][j]
        except IndexError:
          pass

        newCells[i][j] = value

        if value == 1:
          self.SetCellBackgroundColour(i, j, "BLACK")
        else:
          self.SetCellBackgroundColour(i, j, "WHITE")

    self.cells = newCells


  def onSelectCell(self, evt):
    x = evt.GetRow()
    y = evt.GetCol()

    self.lastSelected = [x, y]

    self.toggleCell(x, y)
    evt.Skip()

  def onClickCell(self, evt):
    x = evt.GetRow()
    y = evt.GetCol()

    self.lastClicked = [x, y]

    if self.figure:
      if self.figure == 'quad':
        quadWidth = self.parent.figuresQuadWidthCtrl.GetValue()
        quadHeight = self.parent.figuresQuadHeightCtrl.GetValue()

        for i in xrange(x, min(x + quadHeight, self.rows)):
          for j in xrange(y, min(y + quadWidth, self.cols)):
            self.cells[i][j] = 1

        self.toggleCell(x,y)

        self.parent.figuresQuadPane.Collapse()
        self.figure = False

      if self.figure == 'circle':
        CircleRadius = self.parent.figuresCircleRadiusCtrl.GetValue()

        for i in xrange(max(0, x - CircleRadius), min(x + CircleRadius +1, self.rows)):
          for j in xrange(max(0, y - CircleRadius), min(y + CircleRadius +1, self.cols)):
            if in_circle(x, y, CircleRadius, i, j):
              self.cells[i][j] = 1

        self.toggleCell(x,y)

        self.parent.figuresCirclePane.Collapse()
        self.figure = False

      self.updateSize()

    evt.Skip()

  def onSelectRange(self, evt):
    if evt.Selecting():
      topLeft = evt.GetTopLeftCoords()
      bottomRight = evt.GetBottomRightCoords()

      rowStart = topLeft.GetRow()
      colStart = topLeft.GetCol()

      rowEnd = bottomRight.GetRow()
      colEnd = bottomRight.GetCol()

      for i in xrange(rowStart, rowEnd+1):
        for j in xrange(colStart, colEnd+1):
          if not (i == self.GetGridCursorRow() and j==self.GetGridCursorCol() and self.lastClicked == self.lastSelected):
            self.toggleCell(i, j)

      evt.Skip()

  def toggleCell(self, x, y):
    if self.cells[x][y] == 0:
      self.cells[x][y] = 1
      self.SetCellBackgroundColour(x, y, "BLACK")
    else:
      self.cells[x][y] = 0
      self.SetCellBackgroundColour(x, y, "WHITE")

    self.ClearSelection()
    self.ForceRefresh()
    self.parent.updateParameters()

  def clearGrid(self):
    self.cells = [[0 for x in xrange(self.cols)] for x in xrange(self.rows)]
    for i in xrange(self.rows):
      for j in xrange(self.cols):
        self.SetCellBackgroundColour(i, j, "WHITE")
    self.ForceRefresh()

  def getWidth(self):
    left = right = None
    for i in xrange(self.rows):
      for j in xrange(self.cols):
        if self.cells[i][j] == 1:
          if left == None or j < left:
            left = j
          if right == None or j > right:
            right = j

    if left != None and right != None:
      return right - left + 1
    return 0

  def getLength(self):
    top = bottom = None
    for i in xrange(self.rows):
      for j in xrange(self.cols):
        if self.cells[i][j] == 1:
          if top == None or i < top:
            top = i
          if bottom == None or i > bottom:
            bottom = i

    if top != None and bottom != None:
      return bottom - top + 1
    return 0

  def disableKeyboard(self, evt):
    pass

# From: http://stackoverflow.com/questions/481144/equation-for-testing-if-a-point-is-inside-a-circle
def in_circle(center_x, center_y, radius, x, y):
  square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
  return square_dist <= radius ** 2

