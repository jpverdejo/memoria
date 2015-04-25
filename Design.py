#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import wx.lib.agw.floatspin as FS
import  wx.lib.scrolledpanel as scrolled
import itertools
import glob
import os
import re
import wx.lib.plot as plot

from bitMapGrid import BitMapGrid
from cubes import SC, FCC, BCC
from atomsCanvas import AtomsCanvas
from axes import Axes

from pprint import pprint

class Design(wx.Frame):
    title = "Design"

    configs = {}

    def __init__(self, parent):
        wx.Frame.__init__(self, None, -1, self.title)
        # self.SetSize((800,700))

        # Allow OS X users to close the window with Cmd+Q
        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        self.Show()
        self.Maximize(True)

        self.drawSidebar()

    def drawSidebar(self):
        layout = wx.BoxSizer(wx.HORIZONTAL)

        tabs = wx.Notebook(self)

        self.designSidebarPanel = scrolled.ScrolledPanel(tabs)
        self.designSidebar = wx.BoxSizer(wx.VERTICAL)
        self.content = content = wx.BoxSizer(wx.VERTICAL)

        self.grid = BitMapGrid(self)
        self.canvas = AtomsCanvas(self)

        #Grid size
        self.sizeBox = wx.StaticBox(self.designSidebarPanel, label='Grid size', size=(190, 200))
        self.sizeBoxSizer = wx.StaticBoxSizer(self.sizeBox, wx.VERTICAL)

        self.sizeBoxGrid = wx.GridSizer(1, 4, 10, 10)

        self.sizeBoxWidthLabel = wx.StaticText(self.designSidebarPanel, label="Width")
        self.sizeBoxWidthCtrl = wx.SpinCtrl(self.designSidebarPanel, value=str(self.grid.cols), initial=self.grid.cols, min=0, size=(50, 20))
        self.sizeBoxHeightLabel = wx.StaticText(self.designSidebarPanel, label="Height")
        self.sizeBoxHeightCtrl = wx.SpinCtrl(self.designSidebarPanel, value=str(self.grid.rows), initial=self.grid.rows, min=0, size=(50, 20))

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
        self.configBox = wx.StaticBox(self.designSidebarPanel, label='Object parameters', size=(190,200))
        self.configBoxSizer = wx.StaticBoxSizer(self.configBox, wx.VERTICAL)

        self.configBoxGrid = wx.GridSizer(10, 2, 5, 5)

        # Number of layers
        self.configBoxLayersLabel = wx.StaticText(self.designSidebarPanel, label="Layers", size=(70,20))
        self.configBoxLayersCtrl = wx.SpinCtrl(self.designSidebarPanel, value="3", initial=3, min=1, size=(50, 20))

        # Avoid bug on OS X that auto-focus on first field and hides the default value
        wx.CallAfter(self.configBoxLayersCtrl.SetFocus)

        self.configBoxLayersCtrl.Bind(wx.EVT_SPINCTRL, self.updateParametersProxy)

        # Type of structure
        self.configBoxCellTypeLabel = wx.StaticText(self.designSidebarPanel, label="Structure")
        self.configBoxCellTypeSCRadio = wx.RadioButton(self.designSidebarPanel, label='SC', style=wx.RB_GROUP)
        self.configBoxCellTypeBCCRadio = wx.RadioButton(self.designSidebarPanel, label='BCC')
        self.configBoxCellTypeFCCRadio = wx.RadioButton(self.designSidebarPanel, label='FCC')

        self.configBoxCellTypeSCRadio.SetValue(True)
        self.type = "SC"
        self.configs['type'] = self.type

        self.configBoxCellTypeSCRadio.Bind(wx.EVT_RADIOBUTTON, self.updateType)
        self.configBoxCellTypeBCCRadio.Bind(wx.EVT_RADIOBUTTON, self.updateType)
        self.configBoxCellTypeFCCRadio.Bind(wx.EVT_RADIOBUTTON, self.updateType)

        # Net constant
        self.configBoxNetConstantLabel = wx.StaticText(self.designSidebarPanel, label="Lattice constant")
        self.configBoxNetConstantCtrl = FS.FloatSpin(self.designSidebarPanel, -1, min_val=0, increment=0.1, value=0.28, agwStyle=FS.FS_LEFT)
        self.configBoxNetConstantCtrl.SetFormat("%f")
        self.configBoxNetConstantCtrl.SetDigits(5)

        self.configBoxNetConstantCtrl.Bind(FS.EVT_FLOATSPIN, self.updateParametersProxy)

        # Size
        self.configBoxHeightLabel = wx.StaticText(self.designSidebarPanel, label="Height (nm)", size=(70, 20))
        self.configBoxHeightCtrl = FS.FloatSpin(self.designSidebarPanel, -1, min_val=0.1, increment=0.1, value=10, agwStyle=FS.FS_LEFT)
        self.configBoxHeightCtrl.SetFormat("%f")
        self.configBoxHeightCtrl.SetDigits(2)

        self.configBoxHeightCtrl.Bind(FS.EVT_FLOATSPIN, self.updateParametersProxy)

        # Sizes
        self.configBoxWidthLabel = wx.StaticText(self.designSidebarPanel, label="Width (nm)", size=(70, 20))
        self.configBoxWidthValue = wx.StaticText(self.designSidebarPanel, label="--", size=(70, 20))
        self.configBoxLengthLabel = wx.StaticText(self.designSidebarPanel, label="Length (nm)", size=(70, 20))
        self.configBoxLengthValue = wx.StaticText(self.designSidebarPanel, label="--", size=(70, 20))


        # Scaling
        self.configBoxEtaLabel = wx.StaticText(self.designSidebarPanel, label="Eta", size=(70, 20))
        self.configBoxEtaCtrl = FS.FloatSpin(self.designSidebarPanel, -1, min_val=0, increment=0.1, value=0.55, agwStyle=FS.FS_LEFT)
        self.configBoxEtaCtrl.SetFormat("%f")
        self.configBoxEtaCtrl.SetDigits(5)

        self.configBoxEtaCtrl.Bind(FS.EVT_FLOATSPIN, self.updateParametersProxy)

        self.configBoxXLabel = wx.StaticText(self.designSidebarPanel, label="X", size=(70, 20))
        self.configBoxXValue = wx.StaticText(self.designSidebarPanel, label="--", size=(50, 20))

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
        self.figuresBox = wx.StaticBox(self.designSidebarPanel, label='Figures', size=(190,200))
        self.figuresBoxSizer = wx.StaticBoxSizer(self.figuresBox, wx.VERTICAL)

        self.figuresBoxGrid = wx.FlexGridSizer(2, 1, 10, 10)

        # Quadrilateral
        self.figuresQuadPane = wx.CollapsiblePane(self.designSidebarPanel, label="Quadrilateral", style=wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE)
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
        self.figuresCirclePane = wx.CollapsiblePane(self.designSidebarPanel, label="Circle", style=wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE)
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

        self.clearButton = wx.Button(self.designSidebarPanel, label="Clear grid")
        self.clearButton.Bind(wx.EVT_BUTTON, self.clearGrid)

        self.exportButton = wx.Button(self.designSidebarPanel, label="Export")
        self.exportButton.Bind(wx.EVT_BUTTON, self.checkParametersTrigger)

        self.previewButton = wx.Button(self.designSidebarPanel, label="Show/hide preview")
        self.previewButton.Bind(wx.EVT_BUTTON, self.togglePreview)

        axesBoxD = wx.StaticBox(self.designSidebarPanel, label='Axes')
        self.axesBoxSizerD = wx.StaticBoxSizer(axesBoxD, wx.VERTICAL)
        self.axesD = Axes(self.designSidebarPanel)
        self.axesBoxSizerD.Add(self.axesD)

        self.designSidebar.Add(self.sizeBoxSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.designSidebar.Add(self.configBoxSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.designSidebar.Add(self.figuresBoxSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.designSidebar.Add(self.clearButton, 0, wx.EXPAND | wx.ALL, 5)
        self.designSidebar.Add(self.exportButton, 0, wx.EXPAND | wx.ALL, 5)
        self.designSidebar.Add(self.previewButton, 0, wx.EXPAND | wx.ALL, 5)
        self.designSidebar.Add(self.axesBoxSizerD, 0, wx.EXPAND | wx.ALL, 5)

        self.designSidebarPanel.SetSizer(self.designSidebar)

        self.axesBoxSizerD.ShowItems(False)

        self.visualizationSidebarPanel = scrolled.ScrolledPanel(tabs)
        visualizationSidebar = wx.BoxSizer(wx.VERTICAL)

        inputDirBtn = wx.Button(self.visualizationSidebarPanel, -1, "Select Atoms file")

        self.Bind(wx.EVT_BUTTON, self.openFileDialog, inputDirBtn)

        self.statsBox = wx.StaticBox(self.visualizationSidebarPanel, label='Input Stats', size=(190, 200))
        self.statsSizer = wx.StaticBoxSizer(self.statsBox, wx.VERTICAL)

        self.statsGrid = wx.GridSizer(2, 2, 5, 5)

        statsValidPathLabel = wx.StaticText(self.statsBox, label="Valid Atom file")
        self.statsValidPathValue = wx.StaticText(self.statsBox, label="--")

        statsNumberDataFilesLabel = wx.StaticText(self.statsBox, label="# of Data files")
        self.statsNumberDataFilesValue = wx.StaticText(self.statsBox, label="--")

        self.statsGrid.AddMany([
            (statsValidPathLabel, 0, wx.EXPAND),
            (self.statsValidPathValue, 0, wx.EXPAND),
            (statsNumberDataFilesLabel, 0, wx.EXPAND),
            (self.statsNumberDataFilesValue, 0, wx.EXPAND)
        ])

        self.statsSizer.Add(self.statsGrid)

        self.readInputBtn = wx.Button(self.visualizationSidebarPanel, label="Read Input files")

        # Enable only if we have a valid directory
        self.readInputBtn.Enable(False)

        self.readInputBtn.Bind(wx.EVT_BUTTON, self.readInputFiles)

        viewModeBox = wx.StaticBox(self.visualizationSidebarPanel, label='View layer', size=(190, 200))
        self.viewModeSizer = wx.StaticBoxSizer(viewModeBox, wx.VERTICAL)

        viewModeGrid = wx.FlexGridSizer(2, 4, 5, 5)

        self.viewModeAllLayers = wx.RadioButton(viewModeBox, label='All', style=wx.RB_GROUP)

        self.viewModeLayerX = wx.RadioButton(viewModeBox, label='X')
        self.viewLayerX = wx.ComboBox(viewModeBox, choices=["0.000"], style=wx.CB_DROPDOWN|wx.CB_READONLY, size=(60, 27))

        self.viewModeLayerY = wx.RadioButton(viewModeBox, label='Y')
        self.viewLayerY = wx.ComboBox(viewModeBox, choices=["0.000"], style=wx.CB_DROPDOWN|wx.CB_READONLY, size=(60, 27))

        self.viewModeLayerZ = wx.RadioButton(viewModeBox, label='Z')
        self.viewLayerZ = wx.ComboBox(viewModeBox, choices=["0.000"], style=wx.CB_DROPDOWN|wx.CB_READONLY, size=(60, 27))

        self.viewModeAllLayers.SetValue(True)
        self.viewModeAllLayers.Enable(False)
        self.viewModeLayerX.Enable(False)
        self.viewModeLayerY.Enable(False)
        self.viewModeLayerZ.Enable(False)
        self.viewLayerX.Enable(False)
        self.viewLayerY.Enable(False)
        self.viewLayerZ.Enable(False)

        self.viewModeAllLayers.Bind(wx.EVT_RADIOBUTTON, self.updateViewMode)
        self.viewModeLayerX.Bind(wx.EVT_RADIOBUTTON, self.updateViewMode)
        self.viewModeLayerY.Bind(wx.EVT_RADIOBUTTON, self.updateViewMode)
        self.viewModeLayerZ.Bind(wx.EVT_RADIOBUTTON, self.updateViewMode)

        self.viewLayerX.Bind(wx.EVT_COMBOBOX, self.updateViewMode)
        self.viewLayerY.Bind(wx.EVT_COMBOBOX, self.updateViewMode)
        self.viewLayerZ.Bind(wx.EVT_COMBOBOX, self.updateViewMode)

        viewModeGrid.AddMany([
            (self.viewModeAllLayers, 0, wx.EXPAND),
            (self.viewModeLayerX, 0, wx.EXPAND),
            (self.viewModeLayerY, 0, wx.EXPAND),
            (self.viewModeLayerZ, 0, wx.EXPAND),
            ((1,1)), #Blank space
            (self.viewLayerX, 0, wx.EXPAND),
            (self.viewLayerY, 0, wx.EXPAND),
            (self.viewLayerZ, 0, wx.EXPAND)
        ])

        self.viewModeSizer.Add(viewModeGrid, flag=wx.ALL, border=1)

        controlsBox = wx.StaticBox(self.visualizationSidebarPanel, label='Controls', size=(190, 200))
        self.controlsSizer = wx.StaticBoxSizer(controlsBox, wx.VERTICAL)

        controlsGrid = wx.FlexGridSizer(1, 6, 5, 5)

        self.playBitmap = wx.Bitmap("images/play.png", wx.BITMAP_TYPE_ANY)
        self.stopBitmap = wx.Bitmap("images/pause.png", wx.BITMAP_TYPE_ANY)
        self.backBitmap = wx.Bitmap("images/back.png", wx.BITMAP_TYPE_ANY)
        self.forwardBitmap = wx.Bitmap("images/forward.png", wx.BITMAP_TYPE_ANY)
        self.previousBitmap = wx.Bitmap("images/previous.png", wx.BITMAP_TYPE_ANY)
        self.nextBitmap = wx.Bitmap("images/next.png", wx.BITMAP_TYPE_ANY)

        self.backBtn = wx.BitmapButton(controlsBox, -1, self.backBitmap, (0,0), ((30,30)))
        self.previousBtn = wx.BitmapButton(controlsBox, -1, self.previousBitmap, (0,0), ((30,30)))
        self.playStopBtn = wx.BitmapButton(controlsBox, -1, self.playBitmap, (0,0), ((30,30)))
        self.nextBtn = wx.BitmapButton(controlsBox, -1, self.nextBitmap, (0,0), ((30,30)))
        self.forwardBtn = wx.BitmapButton(controlsBox, -1, self.forwardBitmap, (0,0), ((30,30)))

        self.previousBtn.Bind(wx.EVT_BUTTON, self.previousT)
        self.backBtn.Bind(wx.EVT_BUTTON, self.backT)
        self.playStopBtn.Bind(wx.EVT_BUTTON, self.playStop)
        self.forwardBtn.Bind(wx.EVT_BUTTON, self.forwardT)
        self.nextBtn.Bind(wx.EVT_BUTTON, self.nextT)

        self.backBtn.Enable(False)
        self.previousBtn.Enable(False)
        self.playStopBtn.Enable(False)
        self.forwardBtn.Enable(False)
        self.nextBtn.Enable(False)

        self.currentTCtrl = wx.TextCtrl(controlsBox, value="0", style=wx.TE_CENTRE, size=(70, 10))
        font = wx.Font(18, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.currentTCtrl.SetFont(font)
        self.currentTCtrl.Enable(False)
        self.currentTCtrl.Bind(wx.EVT_TEXT, self.startCurrentTTimer)
        self.currentTTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.setCurrentT, self.currentTTimer)

        controlsGrid.AddMany([
            (self.backBtn, 0, wx.EXPAND),
            (self.previousBtn, 0, wx.EXPAND),
            (self.playStopBtn, 0, wx.EXPAND),
            (self.nextBtn, 0, wx.EXPAND),
            (self.forwardBtn, 0, wx.EXPAND),
            (self.currentTCtrl, 0, wx.EXPAND)
        ])

        self.controlsSizer.Add(controlsGrid)

        axesBoxV = wx.StaticBox(self.visualizationSidebarPanel, label='Axes')
        axesBoxSizerV = wx.StaticBoxSizer(axesBoxV, wx.VERTICAL)
        self.axesV = Axes(self.visualizationSidebarPanel)
        axesBoxSizerV.Add(self.axesV)

        self.plotBox = wx.StaticBox(self.visualizationSidebarPanel, label='Plot', size=(190, 200))
        plotSizer = wx.StaticBoxSizer(self.plotBox, wx.VERTICAL)

        self.plotter = plot.PlotCanvas(self.plotBox, size=(220, 220))
        plotSizer.Add(self.plotter)

        self.plotBox.Show(False)

        visualizationSidebar.AddMany([
            (inputDirBtn, 0, wx.EXPAND | wx.ALL, 5),
            (self.statsSizer, 0, wx.EXPAND | wx.ALL, 5),
            (self.readInputBtn, 0, wx.EXPAND | wx.ALL, 5),
            (self.controlsSizer, 0, wx.EXPAND | wx.ALL, 5),
            (self.viewModeSizer, 0, wx.EXPAND | wx.ALL, 5),
            (axesBoxSizerV, 0, wx.EXPAND | wx.ALL, 5),
            (plotSizer, 0, wx.EXPAND | wx.ALL, 5)
        ])

        self.visualizationSidebarPanel.SetSizer(visualizationSidebar)

        self.viewModeSizer.ShowItems(False)
        self.controlsSizer.ShowItems(False)

        tabs.AddPage(self.designSidebarPanel, "Design")
        tabs.AddPage(self.visualizationSidebarPanel, "Visualization")

        tabs.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

        content.Add(self.grid, 1, wx.EXPAND)
        content.Add(self.canvas, 1, wx.EXPAND)

        self.grid.Show()
        self.canvas.Hide()

        self.togglePreviewStatus = 0

        layout.Add(tabs, 0, wx.EXPAND)
        layout.Add(content, 1, wx.EXPAND)

        self.designSidebarPanel.SetupScrolling(scroll_x=False)
        self.visualizationSidebarPanel.SetupScrolling(scroll_x=False)

        self.SetSizer(layout)
        self.Layout()
        self.Refresh()

        self.grid.updateSize()

        self.updateParameters()

    def validateAtomsFile(self):
        line_number = 0

        valid_first_line = re.compile("[0-9]+\t[0-9]+\t[0-9]+\t[0-9]+(\.[0-9+])*")
        valid_n_line = re.compile("[0-9]+(\t\-?[0-9]+(\.[0-9]+)*){3}(\t[0-9]+){2,}")

        valid = False

        f = open(self.atoms_file, "r")

        for line in f:
            # Verify we have at least 1 line
            if line_number == 0:
                valid = True
            if line_number == 0 and valid_first_line.match(line) == None:
                valid = False
                break
            if line_number > 0 and valid_n_line.match(line) == None:
                valid = False
                break
            line_number += 1
        f.close()

        if valid:
            error = False
            self.statsValidPathValue.SetLabel("Yes")

            os.chdir(os.path.dirname(self.atoms_file))
            data_files = glob.glob("*_*_*.dat")

            if(len(data_files)):
                self.data_files = data_files

                self.statsNumberDataFilesValue.SetLabel(str(len(data_files)))

                self.readInputBtn.Enable(True)
            else:
                error = 'No data files'
        else:
            error = 'Path does not exist'
            self.statsValidPathValue.SetLabel("No")

        if error:
            self.atoms_file = self.data_files = False
            # print "Invalid directory: %s" % error

    def readInputFiles(self, evt):

        atoms = {}
        dataset = {}

        x_param = 0

        f = open(self.atoms_file, "r")
        first_line = True
        for line in f:
            line = line.replace("\n", "").split("\t")

            if first_line:
                x_param = float(line[3])
            else:
                # We get the first 4 elements from the line
                atom_id = int(line.pop(0))
                atom_x = float(line.pop(0))
                atom_y = float(line.pop(0))
                atom_z = float(line.pop(0))

                atoms[atom_id] = (atom_x, atom_y, atom_z)

            first_line = False
        f.close()

        regex = re.compile(".*_([0-9]*)_.*.dat")

        self.max_Mx = 0
        self.max_My = 0
        self.max_Mz = 0

        for data_file in self.data_files:
            data_at_t = { 'intensity': 0, 'Mx': 0, 'My': 0, 'Mz': 0, 'atoms': {} }

            direction = 'x'

            find_t = regex.search(data_file)

            if find_t:
                t = find_t.group(1)
                f = open(data_file)
                first_line = True

                for line in f:
                    line = line.replace("\n", "").split("\t")
                    try:
                        atom_id = int(line.pop(0))
                        vector_x = float(line.pop(0))
                        vector_y = float(line.pop(0))
                        vector_z = float(line.pop(0))

                        data_at_t['Mx'] += vector_x
                        data_at_t['My'] += vector_y
                        data_at_t['Mz'] += vector_z

                        data_at_t['atoms'][atom_id] = (vector_x, vector_y, vector_z)

                        if first_line:
                            data_at_t['intensity'] = float(line.pop(0))
                    except:
                        pass

                    first_line = False

                if data_at_t['Mx'] > self.max_Mx:
                    self.max_Mx = data_at_t['Mx']
                if data_at_t['My'] > self.max_My:
                    self.max_My = data_at_t['My']
                if data_at_t['Mz'] > self.max_Mz:
                    self.max_Mz = data_at_t['Mz']

                dataset[int(t)] = data_at_t

                f.close()

        first_t = None
        for t, data in dataset.iteritems():
            if first_t == None or t < first_t:
                first_t = t
            if self.max_Mx:
                dataset[t]['Mx'] = (dataset[t]['Mx'] + 0.0) / self.max_Mx
            if self.max_My:
                dataset[t]['My'] = (dataset[t]['My'] + 0.0) / self.max_My
            if self.max_Mz:
                dataset[t]['Mz'] = (dataset[t]['Mz'] + 0.0) / self.max_Mz


        self.canvas.setDataset(atoms, dataset)
        self.setT(first_t)

        self.backBtn.Enable(True)
        self.previousBtn.Enable(True)
        self.playStopBtn.Enable(True)
        self.nextBtn.Enable(True)
        self.forwardBtn.Enable(True)
        self.viewModeAllLayers.Enable(True)
        self.viewModeLayerX.Enable(True)
        self.viewModeLayerY.Enable(True)
        self.viewModeLayerZ.Enable(True)
        self.currentTCtrl.Enable(True)

        self.readInputBtn.Show(False)
        self.statsBox.Show(False)
        self.viewModeSizer.ShowItems(True)
        self.controlsSizer.ShowItems(True)
        self.plotBox.Show(True)
        self.designSidebarPanel.SetupScrolling(scroll_x=False)
        self.visualizationSidebarPanel.SetupScrolling(scroll_x=False)
        self.Layout()

        layersX = self.canvas.layersX.keys()
        layersX.sort()
        layersX = [str(x) for x in layersX]

        layersY = self.canvas.layersY.keys()
        layersY.sort()
        layersY = [str(x) for x in layersY]

        layersZ = self.canvas.layersZ.keys()
        layersZ.sort()
        layersZ = [str(x) for x in layersZ]

        self.viewLayerX.Clear()
        self.viewLayerX.AppendItems(layersX)
        self.viewLayerX.SetSelection(0)

        self.viewLayerY.Clear()
        self.viewLayerY.AppendItems(layersY)
        self.viewLayerY.SetSelection(0)

        self.viewLayerZ.Clear()
        self.viewLayerZ.AppendItems(layersZ)
        self.viewLayerZ.SetSelection(0)

    def plot(self, data, markerPoint, axis, max_y):
        line = plot.PolyLine(data, colour='red', width=1)
        marker = plot.PolyMarker([markerPoint])
        # set up text, axis and draw
        gc = plot.PlotGraphics([line, marker], '', '', '')

        max_y += 0.5

        self.plotter.Draw(gc, xAxis=(-1.5,1.5), yAxis=(-max_y,max_y))

    def startCurrentTTimer(self, evt):
        self.currentTTimer.Start(500, wx.TIMER_ONE_SHOT)

    def validateNewT(self, t):
        t = int(t)
        if t not in self.canvas.dataset.keys():
            t = self.canvas.currentT

            Ts = self.canvas.dataset.keys()
            Ts.sort()
            min_t = Ts[0]

            Ts.sort(reverse=True)
            max_t = Ts[0]

            if t > max_t:
                t = max_t

            if t < min_t:
                t = min_t

        self.setT(t)
        self.canvas.currentT = t
        self.canvas.OnDraw()

    def setCurrentT(self, evt):
        t = int(self.currentTCtrl.GetValue())
        self.validateNewT(t)

    def previousT(self, evt):
        t = self.canvas.currentT - 1

        Ts = self.canvas.dataset.keys()
        Ts.sort()
        min_t = Ts[0]

        if t < min_t:
            t = min_t

        if t > min_t:
            self.backBtn.Enable(True)
            self.previousBtn.Enable(True)

        self.validateNewT(t)

    def backT(self, evt):
        t = self.canvas.currentT - 50

        Ts = self.canvas.dataset.keys()
        Ts.sort()
        min_t = Ts[0]

        if t < min_t:
            t = min_t

        if t > min_t:
            self.backBtn.Enable(True)
            self.previousBtn.Enable(True)

        self.validateNewT(t)

    def forwardT(self, evt):
        t = self.canvas.currentT + 50

        Ts = self.canvas.dataset.keys()
        Ts.sort(reverse=True)
        max_t = Ts[0]

        if t > max_t:
            t = max_t

        if t < max_t:
            self.forwardBtn.Enable(True)
            self.nextBtn.Enable(True)

        self.validateNewT(t)

    def nextT(self, evt):
        t = self.canvas.currentT + 1

        Ts = self.canvas.dataset.keys()
        Ts.sort(reverse=True)
        max_t = Ts[0]

        if t > max_t:
            t = max_t

        if t < max_t:
            self.forwardBtn.Enable(True)
            self.nextBtn.Enable(True)

        self.validateNewT(t)

    def setT(self, t):
        self.currentTCtrl.ChangeValue(str(t))

        Ts = self.canvas.dataset.keys()
        Ts.sort()
        min_t = Ts[0]

        Ts.sort(reverse=True)
        max_t = Ts[0]

        if t == max_t:
            self.forwardBtn.Enable(False)
            self.nextBtn.Enable(False)

        if t == min_t:
            self.backBtn.Enable(False)
            self.previousBtn.Enable(False)

        plotData = self.canvas.plotData
        axis = self.canvas.colorDirection
        max_y = self.canvas.dataset[min_t]['intensity']
        markerPoint = (self.canvas.dataset[t]['Mx'], self.canvas.dataset[t]['intensity'])

        if axis == 'y':
            markerPoint = (self.canvas.dataset[t]['My'], self.canvas.dataset[t]['intensity'])
        if axis == 'z':
            markerPoint = (self.canvas.dataset[t]['Mz'], self.canvas.dataset[t]['intensity'])

        self.plot(plotData, markerPoint, axis, max_y)

    def playStop(self, evt):
        if self.canvas.playStatus == 'stop':
            self.canvas.playStatus = 'play'
            self.playStopBtn.SetBitmapLabel(self.stopBitmap)
            self.currentTCtrl.Enable(False)
            self.backBtn.Enable(False)
            self.previousBtn.Enable(False)
            self.forwardBtn.Enable(False)
            self.nextBtn.Enable(False)
            self.canvas.play(True)
        else:
            self.canvas.playStatus = 'stop'
            self.currentTCtrl.Enable(True)
            self.backBtn.Enable(True)
            self.previousBtn.Enable(True)
            self.forwardBtn.Enable(True)
            self.nextBtn.Enable(True)
            self.playStopBtn.SetBitmapLabel(self.playBitmap)
        self.Layout()

    def openFileDialog(self, evt):
        self.statsValidPathValue.SetLabel("--")
        self.statsNumberDataFilesValue.SetLabel("--")
        self.statsGrid.ShowItems(True)

        self.readInputBtn.Enable(False)
        self.backBtn.Enable(False)
        self.previousBtn.Enable(False)
        self.playStopBtn.Enable(False)
        self.forwardBtn.Enable(False)
        self.nextBtn.Enable(False)

        self.viewModeAllLayers.Enable(False)
        self.viewModeLayerX.Enable(False)
        self.viewModeLayerY.Enable(False)
        self.viewModeLayerZ.Enable(False)

        self.readInputBtn.Show(True)
        self.statsBox.Show(True)
        self.viewModeSizer.ShowItems(False)
        self.controlsSizer.ShowItems(False)
        self.plotBox.Show(False)
        self.Layout()

        self.canvas.playStatus = 'stop'
        self.playStopBtn.SetBitmapLabel(self.playBitmap)

        self.canvas.setDataset({}, {})

        dlg = wx.FileDialog(self, message="Choose a file",
            style=wx.OPEN | wx.CHANGE_DIR
        )

        if dlg.ShowModal() == wx.ID_OK:
            self.atoms_file = dlg.GetPath()
            wx.CallAfter(self.validateAtomsFile)

        dlg.Destroy()

    def OnPageChanged(self, evt):
        # 0 = Design
        # 1 = Visualization

        selection = evt.GetSelection()

        if selection == 0:
            self.canvas.Hide()
            self.grid.Show()
            self.togglePreviewStatus = 0
            self.designSidebar.ShowItems(True)
            self.axesBoxSizerD.ShowItems(False)
            self.sizeBoxSizer.ShowItems(True)
            self.figuresBoxSizer.ShowItems(True)
            self.allowParameterInput(True)
        else:
            self.canvas.setAtoms({}, {})
            self.canvas.restartPosition()
            wx.CallAfter(self.canvas.OnDraw)
            self.canvas.Show()
            self.grid.Hide()
            self.designSidebar.ShowItems(False)
            self.readInputBtn.Show(True)
            self.statsBox.Show(True)
            self.viewModeSizer.ShowItems(False)
            self.controlsSizer.ShowItems(False)
            self.plotBox.Show(False)
            self.axesBoxSizerD.ShowItems(True)
            self.togglePreviewStatus = 1
            self.allowParameterInput(False)
        self.Layout()
        evt.Skip()

    def allowParameterInput(self, allow):
        inputs = [
            self.sizeBoxWidthCtrl,
            self.sizeBoxHeightCtrl,
            self.configBoxLayersCtrl,
            self.configBoxCellTypeSCRadio,
            self.configBoxCellTypeBCCRadio,
            self.configBoxCellTypeFCCRadio,
            self.configBoxNetConstantCtrl,
            self.configBoxHeightCtrl,
            self.configBoxEtaCtrl,
            self.figuresQuadPane,
            self.figuresCirclePane,
            self.clearButton,
        ]

        for input in inputs:
            input.Enable(allow)

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

    def clearGrid(self, evt):
        self.grid.clearGrid()

    def setFigure(self, openedPane):
        panes = [self.figuresQuadPane, self.figuresCirclePane]

        for pane in panes:
            if not pane == openedPane:
                pane.Collapse()

        self.Layout()

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

    def updateViewMode(self, evt):
        self.viewLayerX.Enable(False)
        self.viewLayerY.Enable(False)
        self.viewLayerZ.Enable(False)

        if self.viewModeAllLayers.GetValue():
            self.canvas.viewMode = 'all'
        if self.viewModeLayerX.GetValue():
            self.canvas.viewMode = 'x'
            self.viewLayerX.Enable(True)
            self.canvas.viewLayer = float(self.viewLayerX.GetStringSelection())
        if self.viewModeLayerY.GetValue():
            self.canvas.viewMode = 'y'
            self.viewLayerY.Enable(True)
            self.canvas.viewLayer = float(self.viewLayerY.GetStringSelection())
        if self.viewModeLayerZ.GetValue():
            self.canvas.viewMode = 'z'
            self.viewLayerZ.Enable(True)
            self.canvas.viewLayer = float(self.viewLayerZ.GetStringSelection())

        self.canvas.OnDraw()

    def updateParametersProxy(self, evt):
        self.updateParameters()

    def updateParameters(self):

        layers = self.configBoxLayersCtrl.GetValue()
        heightReal = self.configBoxHeightCtrl.GetValue()

        widthPixels = self.grid.getWidth()
        lengthPixels = self.grid.getLength()

        widthReal = heightReal * widthPixels / layers
        lengthReal = heightReal * lengthPixels / layers

        self.configBoxWidthValue.SetLabel(str('{0:.5f}'.format(widthReal)))
        self.configBoxLengthValue.SetLabel(str('{0:.5f}'.format(lengthReal)))

        self.a = a = self.configBoxNetConstantCtrl.GetValue()
        self.eta = eta = self.configBoxEtaCtrl.GetValue()

        factor = 1.0
        if self.type == "BCC" or self.type == "FCC":
            factor = 0.5

        self.x = (layers * a * factor / heightReal) ** (1/eta)

        self.configBoxXValue.SetLabel('{0:.5f}'.format(self.x))
        # self.configBoxXValue.SetLabel(str(self.x))


    def checkParametersTrigger(self, evt):
        self.checkParameters()
        self.exportFile()

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

            #self.exportFile()

            # wx.MessageBox('Data exported to export.dat file.', 'Info', wx.OK | wx.ICON_INFORMATION)

    def exportFile(self):
        f = open("export.dat", "w")

        number_of_neighbors = 6
        if self.type == 'BCC':
            number_of_neighbors = 8
        if self.type == 'FCC':
            number_of_neighbors = 12

        line = [len(self.cube.atoms), 1, number_of_neighbors, '{0:.5f}'.format(self.x)]

        f.write("\t".join(str(x) for x in line) + "\n")

        atom_keys = [int(x) for x in self.cube.atoms.keys()]
        atom_keys.sort()

        for atom_id in atom_keys:
            atom = self.cube.atoms[atom_id]
            neighbors = self.cube.neighborhood[atom_id]

            line = [atom_id] + ['{0:.5f}'.format(x * self.x) for x in atom] + [len(neighbors)] + neighbors + ([0] * (number_of_neighbors - len(neighbors)))

            f.write("\t".join(str(x) for x in line) + "\n")

        f.close()

    def togglePreview(self, evt):
        self.checkParameters()
        self.canvas.setAtoms(self.cube.atoms, self.cube.atom_type)
        self.canvas.restartPosition()
        if self.togglePreviewStatus:
            self.canvas.Hide()
            self.grid.Show()
            self.togglePreviewStatus = 0
            self.axesBoxSizerD.ShowItems(False)
            self.sizeBoxSizer.ShowItems(True)
            self.figuresBoxSizer.ShowItems(True)
            self.allowParameterInput(True)
        else:
            self.canvas.Show()
            self.grid.Hide()
            self.togglePreviewStatus = 1
            self.axesBoxSizerD.ShowItems(True)
            self.sizeBoxSizer.ShowItems(False)
            self.figuresBoxSizer.ShowItems(False)
            self.allowParameterInput(False)
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