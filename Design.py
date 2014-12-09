#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import wx.lib.agw.floatspin as FS
import itertools

from bitMapGrid import BitMapGrid
from cubes import SC, FCC, BCC
from atomsCanvas import AtomsCanvas

from pprint import pprint


class Design(wx.Frame):
    title = "Design"

    configs = {}

    def __init__(self, parent):
        wx.Frame.__init__(self, None, -1, self.title)
        self.SetSize((800,800))

        self.Show()

        self.drawSidebar()

    def drawSidebar(self):
        layout = wx.BoxSizer(wx.HORIZONTAL)
        
        sidebar = wx.BoxSizer(wx.VERTICAL)
        self.content = content = wx.BoxSizer(wx.VERTICAL)

        self.grid = BitMapGrid(self)
        self.canvas = AtomsCanvas(self)

        #Grid size
        self.sizeBox = wx.StaticBox(self, label='Grid size', size=(190, 200))
        self.sizeBoxSizer = wx.StaticBoxSizer(self.sizeBox, wx.VERTICAL)

        self.sizeBoxGrid = wx.GridSizer(1, 4, 10, 10)

        self.sizeBoxWidthLabel = wx.StaticText(self, label="Width")
        self.sizeBoxWidthCtrl = wx.SpinCtrl(self, value=str(self.grid.cols), initial=self.grid.cols, min=0, size=(50, 20))
        self.sizeBoxHeightLabel = wx.StaticText(self, label="Height")
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

        self.configBoxGrid = wx.GridSizer(10, 2, 10, 10)

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
        self.configBoxNetConstantCtrl = FS.FloatSpin(self, -1, min_val=0, increment=0.1, value=0.28, agwStyle=FS.FS_LEFT)
        self.configBoxNetConstantCtrl.SetFormat("%f")
        self.configBoxNetConstantCtrl.SetDigits(5)

        self.configBoxNetConstantCtrl.Bind(FS.EVT_FLOATSPIN, self.updateParametersProxy)

        # Size
        self.configBoxHeightLabel = wx.StaticText(self, label="Height (nm)", size=(70, 20))
        self.configBoxHeightCtrl = FS.FloatSpin(self, -1, min_val=0.1, increment=0.1, value=10, agwStyle=FS.FS_LEFT)
        self.configBoxHeightCtrl.SetFormat("%f")
        self.configBoxHeightCtrl.SetDigits(2)

        self.configBoxHeightCtrl.Bind(FS.EVT_FLOATSPIN, self.updateParametersProxy)

        # Sizes
        self.configBoxWidthLabel = wx.StaticText(self, label="Width (nm)", size=(70, 20))
        self.configBoxWidthValue = wx.StaticText(self, label="--", size=(70, 20))
        self.configBoxLengthLabel = wx.StaticText(self, label="Length (nm)", size=(70, 20))
        self.configBoxLengthValue = wx.StaticText(self, label="--", size=(70, 20))


        # Scaling
        self.configBoxEtaLabel = wx.StaticText(self, label="Eta", size=(70, 20))
        self.configBoxEtaCtrl = FS.FloatSpin(self, -1, min_val=0, increment=0.1, value=0.55, agwStyle=FS.FS_LEFT)
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
                (self.configBoxHeightLabel, 0, wx.EXPAND),
                (self.configBoxHeightCtrl, 0, wx.EXPAND),
                (self.configBoxWidthLabel, 0, wx.EXPAND),
                (self.configBoxWidthValue, 0, wx.EXPAND),
                (self.configBoxLengthLabel, 0, wx.EXPAND),
                (self.configBoxLengthValue, 0, wx.EXPAND),
                (self.configBoxEtaLabel, 0, wx.EXPAND),
                (self.configBoxEtaCtrl, 0, wx.EXPAND),
                (self.configBoxXLabel, 0, wx.EXPAND),
                (self.configBoxXValue, 0, wx.EXPAND)

            ])
        self.configBoxSizer.Add(self.configBoxGrid)

        # Figures
        self.figuresBox = wx.StaticBox(self, label='Figures', size=(190,200))
        self.figuresBoxSizer = wx.StaticBoxSizer(self.figuresBox, wx.VERTICAL)

        self.figuresBoxGrid = wx.GridSizer(2, 1, 10, 10)

        # Quadrilateral
        self.figuresQuadPane = wx.CollapsiblePane(self, label="Quadrilateral", style=wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE)
        self.figuresQuadPane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.quadToggled)

        self.figuresQuadSizer = wx.GridSizer(1, 4, 10, 10)
        self.figuresQuadPaneWin = self.figuresQuadPane.GetPane()

        self.figuresQuadWidthLabel = wx.StaticText(self.figuresQuadPaneWin, label="Width")
        self.figuresQuadWidthCtrl = wx.SpinCtrl(self.figuresQuadPaneWin, value="1", initial=1, min=1, size=(50,20))
        self.figuresQuadHeightLabel = wx.StaticText(self.figuresQuadPaneWin, label="Height")
        self.figuresQuadHeightCtrl = wx.SpinCtrl(self.figuresQuadPaneWin, value="1", initial=1, min=1, size=(50,20))

        self.figuresQuadSizer.AddMany([
                (self.figuresQuadWidthLabel, 0, wx.EXPAND),
                (self.figuresQuadWidthCtrl, 0, wx.EXPAND),
                (self.figuresQuadHeightLabel, 0, wx.EXPAND),
                (self.figuresQuadHeightCtrl, 0, wx.EXPAND)
            ])

        self.figuresQuadPaneWin.SetSizer(self.figuresQuadSizer)

        # Circle
        self.figuresCirclePane = wx.CollapsiblePane(self, label="Circle", style=wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE)
        self.figuresCirclePane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.circleToggled)

        self.figuresCircleSizer = wx.GridSizer(2, 2, 10, 10)
        self.figuresCirclePaneWin = self.figuresCirclePane.GetPane()

        self.figuresCircleRadiusLabel = wx.StaticText(self.figuresCirclePaneWin, label="Radius")
        self.figuresCircleRadiusCtrl = wx.SpinCtrl(self.figuresCirclePaneWin, value="1", initial=1, min=1, size=(50,20))

        self.figuresCircleRadiusCtrl.Bind(wx.EVT_SPINCTRL, self.updateCircleWidth)

        self.figuresCircleWidthLabel = wx.StaticText(self.figuresCirclePaneWin, label="Width (nm)")
        self.figuresCircleWidthValue = wx.StaticText(self.figuresCirclePaneWin, label="--")

        self.figuresCircleSizer.AddMany([
                (self.figuresCircleRadiusLabel, 0, wx.EXPAND),
                (self.figuresCircleRadiusCtrl, 0, wx.EXPAND),
                (self.figuresCircleWidthLabel, 0, wx.EXPAND),
                (self.figuresCircleWidthValue, 0, wx.EXPAND)
            ])

        self.figuresCirclePaneWin.SetSizer(self.figuresCircleSizer)

        self.figuresBoxGrid.AddMany([
            (self.figuresQuadPane, 0, wx.EXPAND),
            (self.figuresCirclePane, 0, wx.EXPAND)
            ])


        self.figuresBoxSizer.Add(self.figuresBoxGrid)

        exportButton = wx.Button(self, label="Export")
        exportButton.Bind(wx.EVT_BUTTON, self.checkParametersTrigger)

        previewButton = wx.Button(self, label="Show/hide preview")
        previewButton.Bind(wx.EVT_BUTTON, self.togglePreview)

        sidebar.Add(self.sizeBoxSizer, 0, wx.EXPAND | wx.ALL, 5)
        sidebar.Add(self.configBoxSizer, 0, wx.EXPAND | wx.ALL, 5)
        sidebar.Add(self.figuresBoxSizer, 0, wx.EXPAND | wx.ALL, 5)
        sidebar.Add(exportButton, 0, wx.EXPAND | wx.ALL, 5)
        sidebar.Add(previewButton, 0, wx.EXPAND | wx.ALL, 5)

        content.Add(self.grid, 1, wx.EXPAND)
        content.Add(self.canvas, 1, wx.EXPAND)

        self.grid.Show()
        self.canvas.Hide()
        self.Layout()
        self.togglePreviewStatus = 0

        layout.Add(sidebar, 0, wx.EXPAND)
        layout.Add(content, 1, wx.EXPAND)

        self.SetSizer(layout)
        self.Layout()

        self.grid.updateSize()

        self.updateParameters()

    def quadToggled(self, evt):
        self.Layout()
        if not evt.GetCollapsed():
            self.grid.figure = 'quad'
            self.setFigure(self.figuresQuadPane)
        else:
            self.grid.figure = False


    def circleToggled(self, evt):
        self.Layout()
        if not evt.GetCollapsed():
            self.grid.figure = 'circle'
            self.setFigure(self.figuresCirclePane)
        else:
            self.grid.figure = False

    def setFigure(self, openedPane):
        panes = [self.figuresQuadPane, self.figuresCirclePane]
        
        for pane in panes:
            if not pane == openedPane:
                pane.Collapse()

    def updateCircleWidth(self, evt):
        radius = self.figuresCircleRadiusCtrl.GetValue()
        
        width = radius * self.a / (self.x ** self.eta)

        self.figuresCircleWidthValue.SetLabel(str(width))

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

        layers = self.configBoxLayersCtrl.GetValue()
        heightReal = self.configBoxHeightCtrl.GetValue()

        widthPixels = self.grid.getWidth()
        lengthPixels = self.grid.getLength()

        widthReal = heightReal * widthPixels / layers
        lengthReal = heightReal * lengthPixels / layers

        self.configBoxWidthValue.SetLabel(str(widthReal))
        self.configBoxLengthValue.SetLabel(str(lengthReal))

        self.a = a = self.configBoxNetConstantCtrl.GetValue()
        self.eta = eta = self.configBoxEtaCtrl.GetValue()

        factor = 1
        if self.type == "BCC" or self.type == "FCC":
            factor = 1/2

        self.x = (layers * a * factor / heightReal) ** (1/eta)

        self.configBoxXValue.SetLabel('{0:.10f}'.format(self.x))


    def checkParametersTrigger(self, evt):
        self.checkParameters()

    def checkParameters(self):
        valid = True

        if not is_number(self.configBoxLayersCtrl.GetValue()):
            valid = False
        if not (self.configBoxCellTypeSCRadio.GetValue() or self.configBoxCellTypeBCCRadio.GetValue() or self.configBoxCellTypeFCCRadio.GetValue()):
            valid = False
        if not is_number(self.configBoxNetConstantCtrl.GetValue()):
            valid = False
        if not is_number(self.configBoxHeightCtrl.GetValue()):
            valid = False

        if not valid:
            wx.MessageBox('You must have valid values for each parameter.', 'Info', wx.OK | wx.ICON_WARNING)
        else:
            self.configs['layers'] = self.configBoxLayersCtrl.GetValue()
            self.configs['cells'] = self.grid.cells

            if self.type == 'SC':
                self.cube = SC(self.configs)
            if self.type == 'BCC':
                self.cube = BCC(self.configs)
            if self.type == 'FCC':
                self.cube = FCC(self.configs)

            self.cube.calculate()

            self.exportFile()

            wx.MessageBox('Data exported to export.dat file.', 'Info', wx.OK | wx.ICON_INFORMATION)

    def exportFile(self):
        f = open("export.dat", "w")

        number_of_neighbors = 6
        if self.type == 'BCC':
            number_of_neighbors = 8
        if self.type == 'FCC':
            number_of_neighbors = 12

        line = [len(self.cube.atoms), 1, number_of_neighbors, '{0:.10f}'.format(self.x)]
        
        f.write("\t".join(str(x) for x in line) + "\n")

        for atom_id, atom in self.cube.atoms.iteritems():
            neighbors = self.cube.neighborhood[atom_id]
            
            line = [atom_id] + ['{0:.10f}'.format(x * self.x) for x in atom] + [len(neighbors)] + neighbors + ([0] * (number_of_neighbors - len(neighbors)))
            #line = [atom_id] + ['{0:.10f}'.format(x) for x in atom] + [len(neighbors)] + neighbors + ([0] * (number_of_neighbors - len(neighbors)))
            
            f.write("\t".join(str(x) for x in line) + "\n")

        f.close()

    def togglePreview(self, evt):
        self.checkParameters()
        self.canvas.setAtoms(self.cube.atoms)
        if self.togglePreviewStatus:
            self.canvas.Hide()
            self.grid.Show()
            self.togglePreviewStatus = 0
        else:
            self.canvas.Show()
            self.grid.Hide()
            self.togglePreviewStatus = 1
        self.Layout()


    
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