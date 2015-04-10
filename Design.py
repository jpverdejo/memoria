#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import wx.lib.agw.floatspin as FS
import itertools
import glob
import os
import re

from bitMapGrid import BitMapGrid
from cubes import SC, FCC, BCC
from atomsCanvas import AtomsCanvas

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

        self.atoms_file_format = "bloque9x13_fccc.dat"
        self.data_files_format = "mcbloquen1P100_*_1.dat"

        self.drawSidebar()

    def drawSidebar(self):
        layout = wx.BoxSizer(wx.HORIZONTAL)

        tabs = wx.Notebook(self)

        designSidebarPanel = wx.Panel(tabs)
        designSidebar = wx.BoxSizer(wx.VERTICAL)
        self.content = content = wx.BoxSizer(wx.VERTICAL)

        self.grid = BitMapGrid(self)
        self.canvas = AtomsCanvas(self)

        #Grid size
        self.sizeBox = wx.StaticBox(designSidebarPanel, label='Grid size', size=(190, 200))
        self.sizeBoxSizer = wx.StaticBoxSizer(self.sizeBox, wx.VERTICAL)

        self.sizeBoxGrid = wx.GridSizer(1, 4, 10, 10)

        self.sizeBoxWidthLabel = wx.StaticText(designSidebarPanel, label="Width")
        self.sizeBoxWidthCtrl = wx.SpinCtrl(designSidebarPanel, value=str(self.grid.cols), initial=self.grid.cols, min=0, size=(50, 20))
        self.sizeBoxHeightLabel = wx.StaticText(designSidebarPanel, label="Height")
        self.sizeBoxHeightCtrl = wx.SpinCtrl(designSidebarPanel, value=str(self.grid.rows), initial=self.grid.rows, min=0, size=(50, 20))

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
        self.configBox = wx.StaticBox(designSidebarPanel, label='Object parameters', size=(190,200))
        self.configBoxSizer = wx.StaticBoxSizer(self.configBox, wx.VERTICAL)

        self.configBoxGrid = wx.GridSizer(10, 2, 10, 10)

        # Number of layers
        self.configBoxLayersLabel = wx.StaticText(designSidebarPanel, label="Layers", size=(70,20))
        self.configBoxLayersCtrl = wx.SpinCtrl(designSidebarPanel, value="3", initial=3, min=1, size=(50, 20))

        # Avoid bug on OS X that auto-focus on first field and hides the default value
        wx.CallAfter(self.configBoxLayersCtrl.SetFocus)

        self.configBoxLayersCtrl.Bind(wx.EVT_SPINCTRL, self.updateParametersProxy)

        # Type of structure
        self.configBoxCellTypeLabel = wx.StaticText(designSidebarPanel, label="Structure")
        self.configBoxCellTypeSCRadio = wx.RadioButton(designSidebarPanel, label='SC', style=wx.RB_GROUP)
        self.configBoxCellTypeBCCRadio = wx.RadioButton(designSidebarPanel, label='BCC')
        self.configBoxCellTypeFCCRadio = wx.RadioButton(designSidebarPanel, label='FCC')

        self.configBoxCellTypeSCRadio.SetValue(True)
        self.type = "SC"
        self.configs['type'] = self.type

        self.configBoxCellTypeSCRadio.Bind(wx.EVT_RADIOBUTTON, self.updateType)
        self.configBoxCellTypeBCCRadio.Bind(wx.EVT_RADIOBUTTON, self.updateType)
        self.configBoxCellTypeFCCRadio.Bind(wx.EVT_RADIOBUTTON, self.updateType)

        # Net constant
        self.configBoxNetConstantLabel = wx.StaticText(designSidebarPanel, label="Net constant")
        self.configBoxNetConstantCtrl = FS.FloatSpin(designSidebarPanel, -1, min_val=0, increment=0.1, value=0.28, agwStyle=FS.FS_LEFT)
        self.configBoxNetConstantCtrl.SetFormat("%f")
        self.configBoxNetConstantCtrl.SetDigits(5)

        self.configBoxNetConstantCtrl.Bind(FS.EVT_FLOATSPIN, self.updateParametersProxy)

        # Size
        self.configBoxHeightLabel = wx.StaticText(designSidebarPanel, label="Height (nm)", size=(70, 20))
        self.configBoxHeightCtrl = FS.FloatSpin(designSidebarPanel, -1, min_val=0.1, increment=0.1, value=10, agwStyle=FS.FS_LEFT)
        self.configBoxHeightCtrl.SetFormat("%f")
        self.configBoxHeightCtrl.SetDigits(2)

        self.configBoxHeightCtrl.Bind(FS.EVT_FLOATSPIN, self.updateParametersProxy)

        # Sizes
        self.configBoxWidthLabel = wx.StaticText(designSidebarPanel, label="Width (nm)", size=(70, 20))
        self.configBoxWidthValue = wx.StaticText(designSidebarPanel, label="--", size=(70, 20))
        self.configBoxLengthLabel = wx.StaticText(designSidebarPanel, label="Length (nm)", size=(70, 20))
        self.configBoxLengthValue = wx.StaticText(designSidebarPanel, label="--", size=(70, 20))


        # Scaling
        self.configBoxEtaLabel = wx.StaticText(designSidebarPanel, label="Eta", size=(70, 20))
        self.configBoxEtaCtrl = FS.FloatSpin(designSidebarPanel, -1, min_val=0, increment=0.1, value=0.55, agwStyle=FS.FS_LEFT)
        self.configBoxEtaCtrl.SetFormat("%f")
        self.configBoxEtaCtrl.SetDigits(5)

        self.configBoxEtaCtrl.Bind(FS.EVT_FLOATSPIN, self.updateParametersProxy)

        self.configBoxXLabel = wx.StaticText(designSidebarPanel, label="X", size=(70, 20))
        self.configBoxXValue = wx.StaticText(designSidebarPanel, label="--", size=(50, 20))

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
        self.figuresBox = wx.StaticBox(designSidebarPanel, label='Figures', size=(190,200))
        self.figuresBoxSizer = wx.StaticBoxSizer(self.figuresBox, wx.VERTICAL)

        self.figuresBoxGrid = wx.FlexGridSizer(2, 1, 10, 10)

        # Quadrilateral
        self.figuresQuadPane = wx.CollapsiblePane(designSidebarPanel, label="Quadrilateral", style=wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE)
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
        self.figuresCirclePane = wx.CollapsiblePane(designSidebarPanel, label="Circle", style=wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE)
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

        self.clearButton = wx.Button(designSidebarPanel, label="Clear grid")
        self.clearButton.Bind(wx.EVT_BUTTON, self.clearGrid)

        self.exportButton = wx.Button(designSidebarPanel, label="Export")
        self.exportButton.Bind(wx.EVT_BUTTON, self.checkParametersTrigger)

        self.previewButton = wx.Button(designSidebarPanel, label="Show/hide preview")
        self.previewButton.Bind(wx.EVT_BUTTON, self.togglePreview)

        designSidebar.Add(self.sizeBoxSizer, 0, wx.EXPAND | wx.ALL, 5)
        designSidebar.Add(self.configBoxSizer, 0, wx.EXPAND | wx.ALL, 5)
        designSidebar.Add(self.figuresBoxSizer, 0, wx.EXPAND | wx.ALL, 5)
        designSidebar.Add(self.clearButton, 0, wx.EXPAND | wx.ALL, 5)
        designSidebar.Add(self.exportButton, 0, wx.EXPAND | wx.ALL, 5)
        designSidebar.Add(self.previewButton, 0, wx.EXPAND | wx.ALL, 5)

        designSidebarPanel.SetSizer(designSidebar)

        visualizationSidebarPanel = wx.Panel(tabs)
        visualizationSidebar = wx.BoxSizer(wx.VERTICAL)

        inputDirBox = wx.StaticBox(visualizationSidebarPanel, label='Input Directory', size=(190, 200))
        inputDirSizer = wx.StaticBoxSizer(inputDirBox, wx.VERTICAL)

        inputDirGrid = wx.GridSizer(2, 1, 10, 10)

        self.inputDirCtrl = wx.TextCtrl(inputDirBox, value="", size=(220, 25))
        inputDirBtn = wx.Button(inputDirBox, -1, "Select input directory")

        self.inputDirCtrl.Bind(wx.EVT_TEXT, self.startValidDirectoryTimer)
        self.Bind(wx.EVT_BUTTON, self.openDirDialog, inputDirBtn)

        self.validDirectoryTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.validateInputDirectory, self.validDirectoryTimer)

        inputDirGrid.AddMany([
            (self.inputDirCtrl, 0, wx.EXPAND),
            (inputDirBtn, 0, wx.EXPAND)
        ])
        inputDirSizer.Add(inputDirGrid)

        statsBox = wx.StaticBox(visualizationSidebarPanel, label='Input Stats', size=(190, 200))
        statsSizer = wx.StaticBoxSizer(statsBox, wx.VERTICAL)

        statsGrid = wx.GridSizer(4, 2, 10, 10)

        statsValidPathLabel = wx.StaticText(visualizationSidebarPanel, label="Valid path")
        self.statsValidPathValue = wx.StaticText(visualizationSidebarPanel, label="--")

        statsAtomsFileLabel = wx.StaticText(visualizationSidebarPanel, label="Atoms file")
        self.statsAtomsFileValue = wx.StaticText(visualizationSidebarPanel, label="--")

        statsDataFilesLabel = wx.StaticText(visualizationSidebarPanel, label="Data files")
        self.statsDataFilesValue = wx.StaticText(visualizationSidebarPanel, label="--")

        statsNumberDataFilesLabel = wx.StaticText(visualizationSidebarPanel, label="# of Data files")
        self.statsNumberDataFilesValue = wx.StaticText(visualizationSidebarPanel, label="--")

        statsGrid.AddMany([
            (statsValidPathLabel, 0, wx.EXPAND),
            (self.statsValidPathValue, 0, wx.EXPAND),
            (statsAtomsFileLabel, 0, wx.EXPAND),
            (self.statsAtomsFileValue, 0, wx.EXPAND),
            (statsDataFilesLabel, 0, wx.EXPAND),
            (self.statsDataFilesValue, 0, wx.EXPAND),
            (statsNumberDataFilesLabel, 0, wx.EXPAND),
            (self.statsNumberDataFilesValue, 0, wx.EXPAND)
        ])

        statsSizer.Add(statsGrid)

        self.readInputBtn = wx.Button(visualizationSidebarPanel, label="Read Input files")

        # Enable only if we have a valid directory
        self.readInputBtn.Enable(False)

        self.readInputBtn.Bind(wx.EVT_BUTTON, self.readInputFiles)

        viewModeBox = wx.StaticBox(visualizationSidebarPanel, label='View mode', size=(190, 200))
        viewModeSizer = wx.StaticBoxSizer(viewModeBox, wx.VERTICAL)

        viewModeGrid = wx.FlexGridSizer(4, 2, 10, 10)

        self.viewModeAllLayers = wx.RadioButton(visualizationSidebarPanel, label='All layers', style=wx.RB_GROUP)

        self.viewModeLayerX = wx.RadioButton(visualizationSidebarPanel, label='Layer in X')
        self.viewLayerX = wx.ComboBox(visualizationSidebarPanel, choices=["0.000"], style=wx.CB_DROPDOWN|wx.CB_READONLY)

        self.viewModeLayerY = wx.RadioButton(visualizationSidebarPanel, label='Layer in Y')
        self.viewLayerY = wx.ComboBox(visualizationSidebarPanel, choices=["0.000"], style=wx.CB_DROPDOWN|wx.CB_READONLY)

        self.viewModeLayerZ = wx.RadioButton(visualizationSidebarPanel, label='Layer in Z')
        self.viewLayerZ = wx.ComboBox(visualizationSidebarPanel, choices=["0.000"], style=wx.CB_DROPDOWN|wx.CB_READONLY)

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
            (wx.StaticText(self, -1, ''), 0, wx.EXPAND), #Blank space
            (self.viewModeLayerX, 0, wx.EXPAND),
            (self.viewLayerX, 0, wx.EXPAND),
            (self.viewModeLayerY, 0, wx.EXPAND),
            (self.viewLayerY, 0, wx.EXPAND),
            (self.viewModeLayerZ, 0, wx.EXPAND),
            (self.viewLayerZ, 0, wx.EXPAND)
        ])

        viewModeSizer.Add(viewModeGrid)

        controlsBox = wx.StaticBox(visualizationSidebarPanel, label='Controls', size=(190, 200))
        controlsSizer = wx.StaticBoxSizer(controlsBox, wx.VERTICAL)

        controlsGrid = wx.GridSizer(1, 2, 10, 10)

        self.playStopBtn = wx.Button(visualizationSidebarPanel, -1, "Play")
        self.playStopBtn.Bind(wx.EVT_BUTTON, self.playStop)
        self.playStopBtn.Enable(False)

        self.currentTLabel = wx.StaticText(visualizationSidebarPanel, label="")

        controlsGrid.AddMany([
            (self.playStopBtn, 0, wx.EXPAND),
            (self.currentTLabel, 0, wx.EXPAND)
        ])

        controlsSizer.Add(controlsGrid)

        visualizationSidebar.AddMany([
            (inputDirSizer, 0, wx.EXPAND | wx.ALL, 5),
            (statsSizer, 0, wx.EXPAND | wx.ALL, 5),
            (self.readInputBtn, 0, wx.EXPAND | wx.ALL, 5),
            (controlsSizer, 0, wx.EXPAND | wx.ALL, 5),
            (viewModeSizer, 0, wx.EXPAND | wx.ALL, 5)
        ])

        visualizationSidebarPanel.SetSizer(visualizationSidebar)

        tabs.AddPage(designSidebarPanel, "Design")
        tabs.AddPage(visualizationSidebarPanel, "Visualization")

        tabs.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

        content.Add(self.grid, 1, wx.EXPAND)
        content.Add(self.canvas, 1, wx.EXPAND)

        self.grid.Show()
        self.canvas.Hide()

        self.togglePreviewStatus = 0

        layout.Add(tabs, 0, wx.EXPAND)
        layout.Add(content, 1, wx.EXPAND)

        self.SetSizer(layout)
        self.Layout()
        self.Refresh()

        self.grid.updateSize()

        self.updateParameters()

    def startValidDirectoryTimer(self, evt):
        self.validDirectoryTimer.Start(1000, wx.TIMER_ONE_SHOT)

        self.statsValidPathValue.SetLabel("--")
        self.statsAtomsFileValue.SetLabel("--")
        self.statsDataFilesValue.SetLabel("--")
        self.statsNumberDataFilesValue.SetLabel("--")

        self.readInputBtn.Enable(False)
        self.playStopBtn.Enable(False)

        self.viewModeAllLayers.Enable(False)
        self.viewModeLayerX.Enable(False)
        self.viewModeLayerY.Enable(False)
        self.viewModeLayerZ.Enable(False)

        self.canvas.playStatus = 'stop'
        self.playStopBtn.SetLabel('Play')

        self.canvas.setDataset({}, {})

    def validateInputDirectory(self, evt):
        directory = self.inputDirCtrl.GetValue()

        error = False

        if os.path.exists(directory):
            self.directory = directory

            self.statsValidPathValue.SetLabel("Yes")

            os.chdir(directory)

            atoms_file = glob.glob(self.atoms_file_format)
            if len(atoms_file):
                self.atoms_file = atoms_file.pop()

                self.statsAtomsFileValue.SetLabel("Yes")

                data_files = glob.glob(self.data_files_format)
                if(len(data_files)):
                    self.data_files = data_files

                    self.statsDataFilesValue.SetLabel("Yes")
                    self.statsNumberDataFilesValue.SetLabel(str(len(data_files)))

                    self.readInputBtn.Enable(True)

                else:
                    error = 'No data files'
                    self.statsDataFilesValue.SetLabel("No")
            else:
                error = 'No atoms file'
                self.statsAtomsFileValue.SetLabel("No")
        else:
            error = 'Path does not exist'
            self.statsValidPathValue.SetLabel("No")

        if error:
            self.input_directory = self.atoms_file = self.data_files = False
            # print "Invalid directory: %s" % error

    def readInputFiles(self, evt):
        # self.atoms_file
        # self.data_files

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

        regex = re.compile(self.data_files_format.replace("*", "([0-9]*)"))

        for data_file in self.data_files:
            data_at_t = { 'intensity': 0, 'atoms': {} }

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

                        data_at_t['atoms'][atom_id] = (vector_x, vector_y, vector_z)

                        if first_line:
                            data_at_t['intensity'] = float(line.pop(0))
                    except:
                        pass

                    first_line = False

                dataset[int(t)] = data_at_t

                f.close()

        self.playStopBtn.Enable(True)
        self.viewModeAllLayers.Enable(True)
        self.viewModeLayerX.Enable(True)
        self.viewModeLayerY.Enable(True)
        self.viewModeLayerZ.Enable(True)
        self.canvas.setDataset(atoms, dataset)

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


    def setT(self, t):
        self.currentTLabel.SetLabel("t: " + str(t))

    def playStop(self, evt):
        if self.canvas.playStatus == 'stop':
            self.canvas.playStatus = 'play'
            self.playStopBtn.SetLabel('Stop')
            self.canvas.play(True)
        else:
            self.canvas.playStatus = 'stop'
            self.playStopBtn.SetLabel('Play')

    def openDirDialog(self, evt):
        dlg = wx.DirDialog(self, "Choose a directory:",
            style=wx.DD_DEFAULT_STYLE
            | wx.DD_DIR_MUST_EXIST
            | wx.DD_CHANGE_DIR
        )

        if dlg.ShowModal() == wx.ID_OK:
            self.inputDirCtrl.SetValue(dlg.GetPath())

        dlg.Destroy()

    def OnPageChanged(self, evt):
        # 0 = Design
        # 1 = Visualization

        selection = evt.GetSelection()

        if selection == 0:
            self.canvas.Hide()
            self.grid.Show()
            self.togglePreviewStatus = 0
            self.allowParameterInput(True)
        else:
            self.canvas.setAtoms({}, {})
            self.canvas.restartPosition()
            self.canvas.Show()
            self.grid.Hide()
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

            # wx.MessageBox('Data exported to export.dat file.', 'Info', wx.OK | wx.ICON_INFORMATION)

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
            # line = [atom_id]
            #     + ['{0:.10f}'.format(x) for x in atom]
            #     + [len(neighbors)]
            #     + neighbors
            #     + ([0] * (number_of_neighbors - len(neighbors)))

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
            self.allowParameterInput(True)
        else:
            self.canvas.Show()
            self.grid.Hide()
            self.togglePreviewStatus = 1
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