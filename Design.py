#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import wx.grid
import wx.lib.agw.floatspin as FS
import math
import itertools
import operator

from pprint import pprint

class BitMapGrid(wx.grid.Grid):
    def __init__(self, parent):
        
        self.parent = parent

        self.rows = 10
        self.cols = 10

        self.width = 560
        self.height = 575

        wx.grid.Grid.__init__(self, parent, -1, size=(self.width,self.height))
        
        self.cells = [[0 for x in xrange(self.cols)] for x in xrange(self.rows)]

        self.calcCellSize()

        self.SetWindowStyleFlag( self.GetWindowStyle() & ~ wx.HSCROLL );
        self.SetCellHighlightPenWidth(0)
        self.SetRowLabelSize(0)
        self.SetColLabelSize(0)
        self.EnableEditing(False)
        self.DisableDragGridSize()

        self.CreateGrid(self.rows, self.cols)

        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onSelectCell)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.onClickCell)
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.onSelectRange)
        self.Bind(wx.EVT_CHAR_HOOK, self.disableKeyboard)

    def calcCellSize(self):
        self.rowSize = math.ceil(self.height/self.rows)
        self.colSize = math.ceil(self.width/self.cols)

        self.cellSize = min(self.rowSize, self.colSize)
        
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

    def first_point(self):
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                if self.cells[i][j] == 1:
                    return [i, j]

        return None

    def find_group(self, point):
        key = "_".join(str(x) for x in point)
        
        if not key in self.group:
            self.group.append(key)

            deltas = itertools.permutations([-1,0,1], 2)
            
            for delta in deltas:
                next_point = map(operator.add, point, delta)
                next_key = "_".join(str(x) for x in next_point)

                if next_point[0] < 0 or next_point[1] < 0:
                    continue
                if next_key in self.group:
                    continue
                if self.cells[next_point[0]][next_point[1]]:
                    self.find_group(next_point)

    def valid(self):

        point = self.first_point()

        if point == None:
            return False #Empty array

        self.group = []
        self.find_group(point)

        for i in xrange(self.rows):
            for j in xrange(self.cols):
                if self.cells[i][j] == 1:
                    key = "%s_%s" % (i,j)
                    if not key in self.group:
                        return False


        return True
    
    def disableKeyboard(self, evt):
        pass

class SC:

    def __init__(self, configs):
        self.configs = configs

        self.top_layer = []

        self.atoms = {}
        self.atom_per_position = {}

        self.neighborhood = {}

    def calculate(self):
        i = j = -1
        deltas = [[0, 0], [0, 1], [1, 0], [1, 1]]
        
        for row in self.configs['cells']:
            j = -1
            i += 1

            for cell in row:
                j += 1 #Cell i,j
                point = [i, j]

                if cell == 1:
                    for delta in deltas:
                        atom = tuple(map(operator.add, point, delta))
                        self.top_layer.append(atom)


        # Remove duplicates
        self.top_layer = sorted(set(self.top_layer))

        # Add Z position to atoms
        atom_id = -1

        for z in xrange(self.configs['layers'] + 1):
            for atom in self.top_layer:
                atom += z, # add Z position
                
                atom_id += 1 #increment atom_id
                atom_key = "_".join(str(x) for x in atom)

                self.atoms[str(atom_id)] = atom
                self.atom_per_position[atom_key] = atom_id

        self.find_neighborhood()

    def find_neighborhood(self):
        deltas = [[-1,0,0], [1,0,0], [0,-1,0], [0,1,0],[0,0,-1],[0,0,1]]

        for atom_id, atom in self.atoms.iteritems():
            neighbors = []
            for delta in deltas:
                neighbor = tuple(map(operator.add, atom, delta))
                neighbor_key = "_".join(str(x) for x in neighbor)

                if neighbor_key in self.atom_per_position.keys():
                    neighbors.append(self.atom_per_position[neighbor_key])

            self.neighborhood[atom_id] = neighbors


class BCC:

    def __init__(self, configs):
        self.configs = configs

        self.top_layer = []
        self.intermediate_layer = []

        self.atoms = {}
        self.atom_per_position = {}

        self.neighborhood = {}

    def calculate(self):
        i = j = -1
        deltas = [[0, 0], [0, 1], [1, 0], [1, 1]]
        
        for row in self.configs['cells']:
            j = -1
            i += 1

            for cell in row:
                j += 1 #Cell i,j
                point = [i, j]

                if cell == 1:
                    self.intermediate_layer.append((i+0.5, j+0.5))

                    for delta in deltas:
                        atom = tuple(map(operator.add, point, delta))
                        self.top_layer.append(atom)


        # Remove duplicates
        self.top_layer = sorted(set(self.top_layer))

        # Add Z position to atoms
        atom_id = -1

        for z in xrange(int(math.ceil(float(self.configs['layers']) / 2))):
            for atom in self.top_layer:
                atom += z, # add Z position
                
                atom_id += 1 #increment atom_id
                atom_key = "_".join(str(x) for x in atom)

                self.atoms[atom_id] = atom
                self.atom_per_position[atom_key] = atom_id

        for z in xrange(int(math.floor(float(self.configs['layers']) / 2))):
            for atom in self.intermediate_layer:
                atom += (z + 0.5), # add Z position
                
                atom_id += 1 #increment atom_id
                atom_key = "_".join(str(x) for x in atom)

                self.atoms[atom_id] = atom
                self.atom_per_position[atom_key] = atom_id

    def find_neighborhood(self):
        deltas = [
        [0.5, 0.5, 0.5], [0.5, -0.5, 0.5], [-0.5, 0.5, 0.5], [-0.5, -0.5, 0.5],
        [0.5, 0.5, -0.5], [0.5, -0.5, -0.5], [-0.5, 0.5, -0.5], [-0.5, -0.5, -0.5]]

        for atom_id, atom in self.atoms.iteritems():
            neighbors = []
            for delta in deltas:
                neighbor = tuple(map(operator.add, atom, delta))
                neighbor_key = "_".join(str(x) for x in neighbor)

                if neighbor_key in self.atom_per_position.keys():
                    neighbors.append(self.atom_per_position[neighbor_key])

            self.neighborhood[atom_id] = neighbors
                
class FCC:

    def __init__(self, configs):
        self.configs = configs

        self.top_layer = []
        self.intermediate_layer = []

        self.atoms = {}
        self.atom_per_position = {}

        self.neighborhood = {}

    def calculate(self):
        i = j = -1
        top_deltas = [[0, 0], [0, 1], [1, 0], [1, 1], [0.5, 0.5]]
        intermediate_deltas = [[0, 0.5], [0.5, 1], [1, 0.5], [0.5, 0]]
        
        for row in self.configs['cells']:
            j = -1
            i += 1

            for cell in row:
                j += 1 #Cell i,j
                point = [i, j]

                if cell == 1:
                    for delta in top_deltas:
                        atom = tuple(map(operator.add, point, delta))
                        self.top_layer.append(atom)

                    for delta in intermediate_deltas:
                        atom = tuple(map(operator.add, point, delta))
                        self.intermediate_layer.append(atom)


        # Remove duplicates
        self.top_layer = sorted(set(self.top_layer))
        self.intermediate_layer = sorted(set(self.intermediate_layer))

        # Add Z position to atoms
        atom_id = -1

        for z in xrange(int(math.ceil(float(self.configs['layers']) / 2))):
            for atom in self.top_layer:
                atom += z, # add Z position
                
                atom_id += 1 #increment atom_id
                atom_key = "_".join(str(x) for x in atom)

                self.atoms[atom_id] = atom
                self.atom_per_position[atom_key] = atom_id

        for z in xrange(int(math.floor(float(self.configs['layers']) / 2))):
            for atom in self.intermediate_layer:
                atom += (z + 0.5), # add Z position
                
                atom_id += 1 #increment atom_id
                atom_key = "_".join(str(x) for x in atom)

                self.atoms[atom_id] = atom
                self.atom_per_position[atom_key] = atom_id

    def find_neighborhood(self):
        deltas = [
        [0, 0.5, 0.5], [0, 0.5, -0.5], [0, -0.5, 0.5], [0, -0.5, -0.5],
        [0.5, 0, 0.5], [0.5, 0, -0.5], [-0.5, 0, 0.5], [-0.5, 0, -0.5],
        [0.5, 0.5, 0], [0.5, -0.5, 0], [-0.5, 0.5, 0], [-0.5, -0.5, 0]]

        for atom_id, atom in self.atoms.iteritems():
            neighbors = []
            for delta in deltas:
                neighbor = tuple(map(operator.add, atom, delta))
                neighbor_key = "_".join(str(x) for x in neighbor)

                if neighbor_key in self.atom_per_position.keys():
                    neighbors.append(self.atom_per_position[neighbor_key])

            self.neighborhood[atom_id] = neighbors

class Design(wx.Frame):
    title = "Design"

    configs = {}

    def __init__(self, parent):
        wx.Frame.__init__(self, None, -1, self.title)
        self.SetSize((800,600))
        self.Show()

        self.drawSidebar()

    def drawSidebar(self):
        layout = wx.BoxSizer(wx.HORIZONTAL)
        
        sidebar = wx.BoxSizer(wx.VERTICAL)
        content = wx.BoxSizer(wx.VERTICAL)

        self.grid = BitMapGrid(self)


        #Grid size
        self.sizeBox = wx.StaticBox(self, label='Grid size', size=(190, 200))
        self.sizeBoxSizer = wx.StaticBoxSizer(self.sizeBox, wx.VERTICAL)

        self.sizeBoxGrid = wx.GridSizer(2, 2, 10, 10)

        self.sizeBoxWidthLabel = wx.StaticText(self, label="Width", size=(70, 20))
        self.sizeBoxWidthCtrl = wx.SpinCtrl(self, value=str(self.grid.cols), initial=self.grid.cols, min=0, size=(50, 20))
        self.sizeBoxHeightLabel = wx.StaticText(self, label="Height", size=(70, 20))
        self.sizeBoxHeightCtrl = wx.SpinCtrl(self, value=str(self.grid.rows), initial=self.grid.rows, min=0, size=(50, 20))

        self.sizeBoxGrid.AddMany([
                (self.sizeBoxWidthLabel, 0, wx.EXPAND),
                (self.sizeBoxWidthCtrl, 0, wx.EXPAND),
                (self.sizeBoxHeightLabel, 0, wx.EXPAND),
                (self.sizeBoxHeightCtrl, 0, wx.EXPAND)
            ])

        self.sizeBoxWidthCtrl.Bind(wx.EVT_SPINCTRL, self.updateGridSize)
        self.sizeBoxHeightCtrl.Bind(wx.EVT_SPINCTRL, self.updateGridSize)

        self.sizeBoxSizer.Add(self.sizeBoxGrid)

        #Object parameters
        self.configBox = wx.StaticBox(self, label='Object parameters', size=(190,200))
        self.configBoxSizer = wx.StaticBoxSizer(self.configBox, wx.VERTICAL)

        self.configBoxGrid = wx.GridSizer(8, 2, 10, 10)

        # Number of layers
        self.configBoxLayersLabel = wx.StaticText(self, label="Layers", size=(70,20))
        self.configBoxLayersCtrl = wx.SpinCtrl(self, value="3", initial=3, min=1, size=(50, 20))

        self.configBoxLayersCtrl.Bind(wx.EVT_SPINCTRL, self.updateParametersProxy)

        # Type of structure
        self.configBoxCellTypeLabel = wx.StaticText(self, label="Structure")
        self.configBoxCellTypeSCRadio = wx.RadioButton(self, label='SC', style=wx.RB_GROUP)
        self.configBoxCellTypeBCCRadio = wx.RadioButton(self, label='BCC')
        self.configBoxCellTypeFCCRadio = wx.RadioButton(self, label='FCC')
        
        self.configBoxCellTypeSCRadio.SetValue(True)
        self.type = "SC"
        self.configs['type'] = self.type

        self.configBoxCellTypeSCRadio.Bind(wx.EVT_RADIOBUTTON, self.updateType)
        self.configBoxCellTypeBCCRadio.Bind(wx.EVT_RADIOBUTTON, self.updateType)
        self.configBoxCellTypeFCCRadio.Bind(wx.EVT_RADIOBUTTON, self.updateType)

        # Net constant
        self.configBoxNetConstantLabel = wx.StaticText(self, label="Net constant")
        self.configBoxNetConstantCtrl = FS.FloatSpin(self, -1, min_val=0, increment=0.1, value=0.1, agwStyle=FS.FS_LEFT)
        self.configBoxNetConstantCtrl.SetFormat("%f")
        self.configBoxNetConstantCtrl.SetDigits(5)

        self.configBoxNetConstantCtrl.Bind(FS.EVT_FLOATSPIN, self.updateParametersProxy)

        # Size
        self.configBoxWidthLabel = wx.StaticText(self, label="Width (nm)", size=(70, 20))
        self.configBoxWidthCtrl = FS.FloatSpin(self, -1, min_val=0.1, increment=0.1, value=10, agwStyle=FS.FS_LEFT)
        self.configBoxWidthCtrl.SetFormat("%f")
        self.configBoxWidthCtrl.SetDigits(2)

        self.configBoxWidthCtrl.Bind(FS.EVT_FLOATSPIN, self.updateParametersProxy)

        # Scaling
        self.configBoxEtaLabel = wx.StaticText(self, label="Eta", size=(70, 20))
        self.configBoxEtaCtrl = FS.FloatSpin(self, -1, min_val=0, increment=0.1, value=0.1, agwStyle=FS.FS_LEFT)
        self.configBoxEtaCtrl.SetFormat("%f")
        self.configBoxEtaCtrl.SetDigits(5)

        self.configBoxEtaCtrl.Bind(FS.EVT_FLOATSPIN, self.updateParametersProxy)

        self.configBoxXLabel = wx.StaticText(self, label="X", size=(70, 20))
        self.configBoxXValue = wx.StaticText(self, label="--", size=(50, 20))

        self.configBoxGrid.AddMany([
                (self.configBoxLayersLabel, 0, wx.EXPAND),
                (self.configBoxLayersCtrl, 0, wx.EXPAND),
                (self.configBoxCellTypeLabel, 0, wx.EXPAND),
                (self.configBoxCellTypeSCRadio, 0, wx.EXPAND),
                (wx.StaticText(self, -1, ''), 0, wx.EXPAND), #Blank space
                (self.configBoxCellTypeBCCRadio, 0, wx.EXPAND),
                (wx.StaticText(self, -1, ''), 0, wx.EXPAND), #Blank space
                (self.configBoxCellTypeFCCRadio, 0, wx.EXPAND),
                (self.configBoxNetConstantLabel, 0, wx.EXPAND),
                (self.configBoxNetConstantCtrl, 0, wx.EXPAND),
                (self.configBoxWidthLabel, 0, wx.EXPAND),
                (self.configBoxWidthCtrl, 0, wx.EXPAND),
                (self.configBoxEtaLabel, 0, wx.EXPAND),
                (self.configBoxEtaCtrl, 0, wx.EXPAND),
                (self.configBoxXLabel, 0, wx.EXPAND),
                (self.configBoxXValue, 0, wx.EXPAND)

            ])
        self.configBoxSizer.Add(self.configBoxGrid)

        exportButton = wx.Button(self, label="Export")
        exportButton.Bind(wx.EVT_BUTTON, self.checkParameters)

        
        sidebar.Add(self.sizeBoxSizer, 0, wx.EXPAND | wx.ALL, 5)
        sidebar.Add(self.configBoxSizer, 0, wx.EXPAND | wx.ALL, 5)
        sidebar.Add(exportButton, 0, wx.EXPAND | wx.ALL, 5)

        content.Add(self.grid, 0, wx.EXPAND)

        layout.Add(sidebar, 0, wx.EXPAND)
        layout.Add(content, 0, wx.EXPAND)

        self.SetSizer(layout)
        self.Layout()

        self.updateParameters()

    def updateGridSize(self, evt):
        self.grid.cols = self.sizeBoxWidthCtrl.GetValue()
        self.grid.rows = self.sizeBoxHeightCtrl.GetValue()
        self.grid.updateSize()

    def updateType(self, evt):
        if self.configBoxCellTypeSCRadio.GetValue():
            self.type = "SC"
        if self.configBoxCellTypeBCCRadio.GetValue():
            self.type = "BCC"
        if self.configBoxCellTypeFCCRadio.GetValue():
            self.type = "FCC"

        self.configs['type'] = self.type

        self.updateParameters()

    def updateParametersProxy(self, evt):
        self.updateParameters()

    def updateParameters(self):

        widthPixels = self.grid.getWidth()
        
        layers = self.configBoxLayersCtrl.GetValue()
        widthReal = self.configBoxWidthCtrl.GetValue()

        a = self.configBoxNetConstantCtrl.GetValue()
        eta = self.configBoxEtaCtrl.GetValue()

        if widthPixels > 0:
            factor = layers * a
            if self.type == "BCC" or self.type == "FCC":
                factor = factor/2

            x = factor / heightReal ** (1/eta)

            self.configBoxXValue.SetLabel(str(x))
        else:
            self.configBoxXValue.SetLabel("--")


    def checkParameters(self, evt):
        valid = True

        if not is_number(self.configBoxLayersCtrl.GetValue()):
            valid = False
        if not (self.configBoxCellTypeSCRadio.GetValue() or self.configBoxCellTypeBCCRadio.GetValue() or self.configBoxCellTypeFCCRadio.GetValue()):
            valid = False
        if not is_number(self.configBoxNetConstantCtrl.GetValue()):
            valid = False
        if not is_number(self.configBoxWidthCtrl.GetValue()):
            valid = False
        if not self.grid.valid():
            valid = False

        if not valid:
            wx.MessageBox('You must have valid values for each parameter.', 'Info', wx.OK | wx.ICON_WARNING)
        else:
            self.configs['layers'] = self.configBoxLayersCtrl.GetValue()
            self.configs['cells'] = self.grid.cells

            if self.type == 'SC':
                cube = SC(self.configs)
            if self.type == 'BCC':
                cube = BCC(self.configs)
            if self.type == 'FCC':
                cube = FCC(self.configs)

            cube.calculate()

            pprint(cube.atoms)
            pprint(cube.neighborhood)

            #wx.MessageBox('Valid! Calculating atoms.', 'Info', wx.OK | wx.ICON_INFORMATION)


    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

app = wx.App(False)
frame = Design(None)

app.MainLoop()