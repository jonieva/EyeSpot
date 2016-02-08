# coding=utf-8

import os, sys
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import json
import ui
from logic import SlicerUtil, Util, Enhancer
#
# EyeSpot
#
class EyeSpot(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "EyeSpot"
        self.parent.categories = ["EyeSpot"]
        self.parent.contributors = "Jorge Onieva (jorge.onieva@gmail.com), EyeSpot team"
        self.parent.helpText = """Diagnose eye fundus images"""

#
# EyeSpotWidget
#

class EyeSpotWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """
    def __init__(self, parent):
        ScriptedLoadableModuleWidget.__init__(self, parent)
        self.logic = None
        self.__initVars__()

    def __initVars__(self):
        del self.logic
        self.logic = EyeSpotLogic()

    @property
    def isExpertMode(self):
        return self.expertModeCheckbox.checked

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        self.caseInfoCollapsibleButton = ctk.ctkCollapsibleButton()
        self.caseInfoCollapsibleButton.text = "Case information"
        self.caseInfoCollapsibleButton.collapsed = False
        self.layout.addWidget(self.caseInfoCollapsibleButton)
        self.caseAreaLayout = qt.QGridLayout(self.caseInfoCollapsibleButton)
        # Select case
        row = 0
        self.loadCaseButton = ctk.ctkPushButton()
        self.loadCaseButton.text = "Load case"
        self.loadCaseButton.toolTip = "Load a case folder"
        self.caseAreaLayout.addWidget(self.loadCaseButton, row, 0)

        # Reset button
        self.resetButton = ctk.ctkPushButton()
        self.resetButton.text = "Close case"
        self.resetButton.toolTip = "Close the current case"
        self.caseAreaLayout.addWidget(self.resetButton, row, 1)

        # Case info
        row += 1
        self.caseInfoFrame = qt.QFrame()
        self.caseInfoFrame.setFrameStyle(0x0002 | 0x0010)
        self.caseInfoFrame.lineWidth = 2
        self.caseInfoFrame.setStyleSheet("background-color: #EEEEEE; margin: 10px")
        self.caseAreaLayout.addWidget(self.caseInfoFrame, row, 0, 1, 2)

        self.caseInfoFrameLayout = qt.QGridLayout()
        self.caseInfoFrame.setLayout(self.caseInfoFrameLayout)

        self.caseIdLabel = qt.QLabel("Case id: ")
        self.caseIdLabel.setStyleSheet("font-weight: bold")
        self.caseInfoFrameLayout.addWidget(self.caseIdLabel, 0, 0)

        self.showEnhancementCheckboxGroup = qt.QButtonGroup()
        self.showJustOriginalButton = qt.QRadioButton("Original only")
        self.showJustOriginalButton.setChecked(True)
        self.showEnhancementCheckboxGroup.addButton(self.showJustOriginalButton, 0)
        self.caseInfoFrameLayout.addWidget(self.showJustOriginalButton, 1, 0)

        self.showOriginalPlusEnhancedButton = qt.QRadioButton("Original and enhanced")
        self.showEnhancementCheckboxGroup.addButton(self.showOriginalPlusEnhancedButton, 1)
        self.caseInfoFrameLayout.addWidget(self.showOriginalPlusEnhancedButton, 2, 0)

        self.showJustEnhancedButton = qt.QRadioButton("Enhanced only")
        self.showEnhancementCheckboxGroup.addButton(self.showJustEnhancedButton, 2)
        self.caseInfoFrameLayout.addWidget(self.showJustEnhancedButton, 3, 0)

         # Center Volumes button
        self.centerVolumesButton = ctk.ctkPushButton()
        self.centerVolumesButton.text = "Center image/s"
        self.centerVolumesButton.toolTip = "Center all the current visible images"
        self.centerVolumesButton.setFixedWidth(200)
        # self.centerVolumesButton.toolTip = "Load a case folder"
        self.caseInfoFrameLayout.addWidget(self.centerVolumesButton, 4, 0)

        # Enhancement fine tuning
        self.vascularFactorLabel = qt.QLabel("Vascular factor")
        self.vascularFactorLabel.setStyleSheet("font-weight: bold")
        self.caseInfoFrameLayout.addWidget(self.vascularFactorLabel, 0, 1)
        self.vascularFactorSlider = qt.QSlider()
        self.vascularFactorSlider.orientation = 2  # Vertical
        self.vascularFactorSlider.value = 5
        self.vascularFactorSlider.minimum = 0
        self.vascularFactorSlider.maximum = 10
        # self.vascularFactorSlider.setStyleSheet("margin-top:10px;padding-top:20px")
       # self.vascularFactorSlider.setToolTip("Move the slider for a fine tuning segmentation")
        self.caseInfoFrameLayout.addWidget(self.vascularFactorSlider, 1, 1, 4, 1, 0x0004)

        self.enhancementFactorLabel = qt.QLabel("Enhancement factor")
        self.enhancementFactorLabel.setStyleSheet("font-weight: bold")
        self.caseInfoFrameLayout.addWidget(self.enhancementFactorLabel, 0, 2)
        self.enhancementFactorSlider = qt.QSlider()
        self.enhancementFactorSlider.orientation = 2  # Vertical
        self.enhancementFactorSlider.minimum = 0
        self.enhancementFactorSlider.maximum = 10
        self.enhancementFactorSlider.value = 5
        # self.vascularFactorSlider.setStyleSheet("margin-top:10px;padding-top:20px")
       # self.vascularFactorSlider.setToolTip("Move the slider for a fine tuning segmentation")
        self.caseInfoFrameLayout.addWidget(self.enhancementFactorSlider, 1, 2, 4, 1, 0x0004)

        # Editor
        row += 1
        self.editorWidget = ui.CustomEditorWidget(self.parent)
        self.editorWidget.setup()
        self.editorCollapsibleButton = self.editorWidget.editLabelMapsFrame
        self.editorCollapsibleButton.text = "Edit the current eye image"
        self.editorCollapsibleButton.collapsed = False
        self.editorWidget.toolsColor.terminologyCollapsibleButton.setVisible(False)
        self.layout.addWidget(self.editorCollapsibleButton)

        ### DIAGNOSIS
        self.diagnosisCollapsibleButton = ctk.ctkCollapsibleButton()
        self.diagnosisCollapsibleButton.text = "Diagnosis"
        self.diagnosisCollapsibleButton.collapsed = False
        self.layout.addWidget(self.diagnosisCollapsibleButton)
        self.diagnosisAreaLayout = qt.QVBoxLayout(self.diagnosisCollapsibleButton)

        # Visual Acuity
        label = qt.QLabel("Visual acuity (VA): ")
        label.setStyleSheet("margin: 10px 0 0 10px; font-weight: bold")
        self.diagnosisAreaLayout.addWidget(label)
        self.vaFrame = qt.QFrame()
        self.vaFrame.setFrameStyle(0x0002 | 0x0010)
        self.vaFrame.lineWidth = 2
        self.vaFrame.setStyleSheet("background-color: #EEEEEE; margin: 10px")
        self.vaFrame.setFixedWidth(240)
        self.diagnosisAreaLayout.addWidget(self.vaFrame)

        self.vaFrameLayout = qt.QGridLayout(self.vaFrame)
        self.vaFrameLayout.addWidget(qt.QLabel("OS"), 0, 0)
        self.osLineEdit = qt.QLineEdit()
        self.osLineEdit.setFixedWidth(80)
        self.osLineEdit.setStyleSheet("background-color: white" )
        self.vaFrameLayout.addWidget(self.osLineEdit, 0, 1)

        self.vaFrameLayout.addWidget(qt.QLabel("OD"), 1, 0)
        self.odLineEdit = qt.QLineEdit()
        self.odLineEdit.setFixedWidth(80)
        self.odLineEdit.setStyleSheet("background-color: white" )
        self.vaFrameLayout.addWidget(self.odLineEdit, 1, 1)


        self.vaModalityButtonGroup = qt.QButtonGroup()
        self.scvaRadioButton = qt.QRadioButton()
        self.scvaRadioButton.setText("SCVA")
        self.vaFrameLayout.addWidget(self.scvaRadioButton, 0, 2)
        self.vaModalityButtonGroup.addButton(self.scvaRadioButton)

        self.bcvaRadioButton = qt.QRadioButton()
        self.bcvaRadioButton.setText("BCVA")
        self.vaFrameLayout.addWidget(self.bcvaRadioButton, 1, 2)
        self.vaModalityButtonGroup.addButton(self.bcvaRadioButton)

        self.ucvaRadioButton = qt.QRadioButton()
        self.ucvaRadioButton.setText("UCVA")
        self.vaFrameLayout.addWidget(self.ucvaRadioButton, 2, 2)
        self.vaModalityButtonGroup.addButton(self.ucvaRadioButton)

        # Problems detected
        label = qt.QLabel("Problems detected: ")
        label.setStyleSheet("margin: 10px 0 0 10px; font-weight: bold")
        self.diagnosisAreaLayout.addWidget(label)

        self.problemsFrame = qt.QFrame()
        self.problemsFrame.setFrameStyle(0x0002 | 0x0010)
        self.problemsFrame.lineWidth = 2
        self.problemsFrame.setStyleSheet("background-color: #EEEEEE; margin: 10px")
        self.diagnosisAreaLayout.addWidget(self.problemsFrame)

        self.problemsFrameLayout = qt.QGridLayout()
        self.problemsFrame.setLayout(self.problemsFrameLayout)
        self.problemsButtons = []

        self.microaneurysmsCheckbox = qt.QCheckBox()
        self.microaneurysmsCheckbox.setText("Microaneurysms")
        self.problemsFrameLayout.addWidget(self.microaneurysmsCheckbox, 0, 0)
        self.problemsButtons.append(self.microaneurysmsCheckbox)

        self.exudatesCheckbox = qt.QCheckBox()
        self.exudatesCheckbox.setText("Exudates")
        self.problemsFrameLayout.addWidget(self.exudatesCheckbox, 0, 1)
        self.problemsButtons.append(self.exudatesCheckbox)
        
        self.haemorrhagesCheckbox = qt.QCheckBox()
        self.haemorrhagesCheckbox.setText("Haemorrhages")
        self.problemsFrameLayout.addWidget(self.haemorrhagesCheckbox, 0, 2)
        self.problemsButtons.append(self.haemorrhagesCheckbox)

        self.cottonWoolSpotsCheckbox = qt.QCheckBox()
        self.cottonWoolSpotsCheckbox.setText("Cotton wool spots")
        self.problemsFrameLayout.addWidget(self.cottonWoolSpotsCheckbox, 1, 0)
        self.problemsButtons.append(self.cottonWoolSpotsCheckbox)
        
        self.NeovascularisationCheckbox = qt.QCheckBox()
        self.NeovascularisationCheckbox.setText("Neovascularisation")
        self.problemsFrameLayout.addWidget(self.NeovascularisationCheckbox, 1, 1)
        self.problemsButtons.append(self.NeovascularisationCheckbox)

        label = qt.QLabel("Diabetic retinopathy diagnosis: ")
        label.setStyleSheet("margin: 10px 0 0 10px; font-weight: bold")
        self.diagnosisAreaLayout.addWidget(label)

        # Diabetic Retinopathy diagnosis
        self.diabeticRetinopathyDiagnosisFrame = qt.QFrame()
        self.diabeticRetinopathyDiagnosisFrame.setFrameStyle(0x0002 | 0x0010)
        self.diabeticRetinopathyDiagnosisFrame.lineWidth = 2
        self.diabeticRetinopathyDiagnosisFrame.setStyleSheet("background-color: #EEEEEE; margin: 10px")
        self.diagnosisAreaLayout.addWidget(self.diabeticRetinopathyDiagnosisFrame)

        self.diabeticRetinopathyDiagnosisFrameLayout = qt.QHBoxLayout()
        self.diabeticRetinopathyDiagnosisFrame.setLayout(self.diabeticRetinopathyDiagnosisFrameLayout)

        self.diagnosisRadioButtonGroup = qt.QButtonGroup()
        for i in range(5):
            rb = qt.QRadioButton(str(i))
            self.diagnosisRadioButtonGroup.addButton(rb, i)
            self.diabeticRetinopathyDiagnosisFrameLayout.addWidget(rb)
        self.diagnosisRadioButtonGroup.buttons()[0].setChecked(True)

        # Additional comments
        label = qt.QLabel("Additional comments:")
        label.setStyleSheet("margin: 10px 0 0 10px; font-weight: bold")
        self.diagnosisAreaLayout.addWidget(label)
        row += 1

        self.additionalCommentsText = qt.QTextEdit()
        self.additionalCommentsText.setStyleSheet("margin: 10px")
        self.diagnosisAreaLayout.addWidget(self.additionalCommentsText)

        self.saveReportButton = ctk.ctkPushButton()
        self.saveReportButton.text = "Save report"
        self.saveReportButton.setFixedWidth(300)
        self.diagnosisAreaLayout.addWidget(self.saveReportButton)

        self.printReportButton = ctk.ctkPushButton()
        self.printReportButton.text = "Save and generate PDF"
        self.printReportButton.setFixedWidth(300)
        self.diagnosisAreaLayout.addWidget(self.printReportButton)

        self.expertModeCollapsibleButton = ctk.ctkCollapsibleButton()
        self.expertModeCollapsibleButton.text = "Expert mode"
        self.expertModeCollapsibleButton.collapsed = True
        self.layout.addWidget(self.expertModeCollapsibleButton)
        self.expertModeLayout = qt.QVBoxLayout(self.expertModeCollapsibleButton)
        self.expertModeCheckbox = qt.QCheckBox("Activate expert mode")
        self.expertModeCheckbox.checked = True
        self.expertModeLayout.addWidget(self.expertModeCheckbox)
        self.layout.addStretch(1)

        # Connections
        self.loadCaseButton.connect('clicked()', self.__onLoadCaseClicked__)
        # self.loadReportButton.connect('clicked()', self.__onLoadReportClicked__)
        self.showEnhancementCheckboxGroup.connect("buttonClicked (int)", self.__onEnhancementButtonGroupClicked__)
        self.centerVolumesButton.connect('clicked()', SlicerUtil.centerAllVolumes)
        self.vascularFactorSlider.connect('sliderReleased()', self.__onEnhancementFineTuning__)
        self.enhancementFactorSlider.connect('sliderReleased()', self.__onEnhancementFineTuning__)
        self.saveReportButton.connect('clicked()', self.__onSaveReportClicked__)
        self.printReportButton.connect('clicked()', self.__onPrintReportClicked__)
        self.resetButton.connect('clicked()', self.reset)
        self.expertModeCheckbox.connect("stateChanged(int)", self.__onExpertModeStateChanged__)
        slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.EndCloseEvent, self.__onSceneClosed__)

        # Set default layout Red
        SlicerUtil.changeLayoutRedSingle()

        self.refreshUI()

    @property
    def isCaseLoaded(self):
        return self.logic.current2DVectorVolume is not None

    def refreshUI(self):
        SlicerUtil.showToolbars(self.isExpertMode)
        lm = slicer.app.layoutManager()
        for key in ("Red", "Yellow"):
            sliceWidget = lm.sliceWidget(key)
            controller = sliceWidget.sliceController()
            controller.showLabelOutline(True)
            controller.visible = self.isExpertMode

        # Hide DataProbe module
        dataProbeCollapsibleButton = [b for b in slicer.util.mainWindow().findChildren("ctkCollapsibleButton")
                                      if b.text == "Data Probe"][0]
        dataProbeCollapsibleButton.setVisible(self.isExpertMode)

        # Link windows
        compNodes = slicer.util.getNodes("vtkMRMLSliceCompositeNode*")
        for compNode in compNodes.itervalues():
            compNode.SetLinkedControl(True)

        self.resetButton.visible = self.caseInfoFrame.visible = \
            self.editorCollapsibleButton.visible = self.diagnosisCollapsibleButton.visible = \
            self.isCaseLoaded or self.isExpertMode


        if self.isCaseLoaded:
            self.caseIdLabel.text = "Case Id: " + self.logic.current2DVectorVolume.GetName()

            for button in self.showEnhancementCheckboxGroup.buttons():
                button.setEnabled(self.logic.current2DVectorVolume is not None)

            if self.showEnhancementCheckboxGroup.checkedId() == 0:
                # Just original. Red Slice only
                SlicerUtil.changeLayout(6)
                # Hide enhancement fine tuning controls
                self.vascularFactorLabel.visible = self.vascularFactorSlider.visible = \
                    self.enhancementFactorLabel.visible = self.enhancementFactorSlider.visible = \
                    False
            elif self.showEnhancementCheckboxGroup.checkedId() == 1:
                # Original + Enhanced
                SlicerUtil.changeLayout(29)
                # Show enhancement fine tuning controls
                self.vascularFactorLabel.visible = self.vascularFactorSlider.visible = \
                    self.enhancementFactorLabel.visible = self.enhancementFactorSlider.visible = \
                    True
            elif self.showEnhancementCheckboxGroup.checkedId() == 2:
                # Just enhanced. Yellow Slice
                SlicerUtil.changeLayout(7)
                # Show enhancement fine tuning controls
                self.vascularFactorLabel.visible = self.vascularFactorSlider.visible = \
                    self.enhancementFactorLabel.visible = self.enhancementFactorSlider.visible = \
                    True

    def setActiveVolumeId(self, volumeId, labelmapId=None):
        selectionNode = slicer.app.applicationLogic().GetSelectionNode()
        if volumeId is not None and volumeId != "":
            selectionNode.SetReferenceActiveVolumeID(volumeId)
        if labelmapId is not None and labelmapId != "":
            selectionNode.SetReferenceActiveLabelVolumeID(labelmapId)
        slicer.app.applicationLogic().PropagateVolumeSelection(0)


    def insertDefaultReportText(self):
        cursor = qt.QTextCursor(self.additionalCommentsText.document())
        cursor.insertHtml("Patient ID: <b>{0}</b>".format(self.logic.current2DVectorVolume.GetName()))
        #cursor.insertHtml("Caso: {0}<br/>".format(self.logic.current2DVectorVolume.GetName()))
        cursor.insertBlock()
        s = "No se han detectado anomalías"
        cursor.insertHtml(s.decode("utf-8"))

    def getCurrentReportData(self):
        """ Get a dictionary with the current information of the GUI
        :return: dictionary with the content
        """
        report = {}
        # VA
        report[self.logic.getKey("OS")] = self.osLineEdit.text
        report[self.logic.getKey("OD")] = self.odLineEdit.text
        report[self.logic.getKey("VA Modality")] = \
            self.vaModalityButtonGroup.checkedButton().text if self.vaModalityButtonGroup.checkedButton() is not None \
            else ""

        # Problems checked
        for button in self.problemsButtons:
            s = button.text     # TODO: fix when multilanguage
            report[self.logic.getKey(s)] = button.isChecked()

        # Diabetic Retinopathy Score
        report[self.logic.getKey("Diabetic Retinopathy Score")] = self.diagnosisRadioButtonGroup.checkedId()

        # Additional comments
        report[self.logic.getKey("Additional Comments")] = self.additionalCommentsText.plainText

        return report

    def loadGUIFromReportData(self, data):
        """ Load the GUI values from a dictionary that contains the report data
        :param data: dictionary of data
        """
        # VA
        self.osLineEdit.text = data[self.logic.getKey("OS")]
        self.odLineEdit.text = data[self.logic.getKey("OD")]
        for button in self.vaModalityButtonGroup.buttons():
            if button.text == data[self.logic.getKey("VA Modality")]:
                button.setChecked(True)
                break

        # Problems
        for button in self.problemsButtons:
            button.setChecked(data[self.logic.getKey(button.text)])

        # Score
        score = str(data[self.logic.getKey("Diabetic Retinopathy Score")])
        for button in self.diagnosisRadioButtonGroup.buttons():
            if button.text == score:
                button.setChecked(True)
                break
        # Additional comments
        self.additionalCommentsText.plainText = data[self.logic.getKey("Additional comments")]

    def reset(self, closeScene=True):
        if closeScene:
            slicer.mrmlScene.Clear(0)
        self.showEnhancementCheckboxGroup.buttons()[0].setChecked(True)
        self.__initVars__()
        self.refreshUI()



    def enter(self):
        """This is invoked every time that we select this module as the active module in Slicer (not only the first time)"""
        self.__setLabelmapOutlines__()
        SlicerUtil.showToolbars(SlicerUtil.IsDevelopment)

    def exit(self):
        """This is invoked every time that we switch to another module (not only when Slicer is closed)."""
        pass

    def cleanup(self):
        """This is invoked as a destructor of the GUI when the module is no longer going to be used"""
        pass

    def __setLabelmapOutlines__(self):
        """ Configure the Red and Yellow Slice Views to paint just the border of the labelmap regions
        :return:
        """
        lm = slicer.app.layoutManager()
        controller = lm.sliceWidget("Red").sliceController()
        controller.showLabelOutline(True)
        controller = lm.sliceWidget("Yellow").sliceController()
        controller.showLabelOutline(True)


    def __onLoadCaseClicked__(self):
        """ Load a new eye fundus image
        :return: True if an image was loaded
        """
        dir = qt.QFileDialog.getExistingDirectory()
        if dir:
            # Close any opened case
            self.reset()
            if self.logic.loadCase(dir):
                self.setActiveVolumeId(self.logic.current2DVectorVolume.GetID(), self.logic.currentLabelmapVolume.GetID())
                if self.logic.currentReportData is not None:
                    self.loadGUIFromReportData(self.logic.currentReportData)
        self.refreshUI()

    def __onEnhancementFineTuning__(self):
        self.logic.enhancementFineTuning(self.vascularFactorSlider.value / 10.0, self.enhancementFactorSlider.value / 10.0)

    def __onSaveReportClicked__(self):
        reportPath = self.logic.saveReport(self.getCurrentReportData())
        qt.QMessageBox.information(slicer.util.mainWindow(), 'Report saved',
                'The report was saved successfully')
        self.refreshUI()

    def __onPrintReportClicked__(self):
        self.logic.printReport(self.getCurrentReportData(), self.__printReportCallback__)

    def __printReportCallback__(self, reportFile):
        if qt.QMessageBox.question(slicer.util.mainWindow(), 'Report printed',
                'The PDF was generated successfully. Do you want to open it now?',
                qt.QMessageBox.Yes|qt.QMessageBox.No) == qt.QMessageBox.Yes:
            # Open the pdf file
            Util.openFile(reportFile)
        self.refreshUI()

    def __onEnhancementButtonGroupClicked__(self, buttonId):
        self.refreshUI()

        if buttonId in (1,2):
            # Both or enhanced only. We have to retrieve the enhanced volume
            sliceNodeYellow = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeYellow')
            # Get the enhanced volume
            enhancedVol = self.logic.getEnhancedVolume()
            # Assign it to the yellow slice
            slicer.mrmlScene.GetNodeByID('vtkMRMLSliceCompositeNodeYellow').SetBackgroundVolumeID(enhancedVol.GetID())
            sliceNodeYellow.SetOrientationToAxial()
            # Assign the labelmap
            slicer.mrmlScene.GetNodeByID('vtkMRMLSliceCompositeNodeYellow').SetLabelVolumeID(self.logic.currentLabelmapVolume.GetID())
            if buttonId == 1:
                # Set the same field of view for the original and the enhanced volume
                fov = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed').GetFieldOfView()
                sliceNodeYellow.SetFieldOfView(fov[0], fov[1], 1)

    def __onExpertModeStateChanged__(self, state):
        self.refreshUI()

    def __onSceneClosed__(self, arg1, arg2):
        self.reset(False)
#
# EyeSpotLogic
#
class EyeSpotLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.    The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """
    def __init__(self):
        """Constructor. """
        ScriptedLoadableModuleLogic.__init__(self)

        self.current2DVectorVolume = None       # Original 2D image
        self.currentScalarVolume = None         # 3D volume to represent the original image
        self.currentLabelmapVolume = None       # Labelmap
        self.currentEnhancedVolume = None       # Enhanced 3D volume
        self.currentEnhancedImageArray = None   # Numpy array associated with the enhanced volume
        self.currentReportData = None           # Dictionary for the report data (lesions, comments, etc.)

        self.enhancer = None                    # Enhancer object

        # Customized colors for the labelmap
        p = self.getResourcePath("EyeSpot_Colors.ctbl")
        self.colorTableNode = slicer.modules.colors.logic().LoadColorFile(p)

        self.isCurrentReportSaved = False         # Current report has been saved

    def loadCase(self, directory):
        """ Load a new eye image and create a labelmap for it.
        It also sets the images as the active ones in the scene
        :param filePath: directory where all the images/data are stored
        :return: True if the image and has been successfully loaded
        """
        properties = {}
        properties['singleFile'] = True
        dirName = os.path.basename(os.path.normpath(directory))
        for f in os.listdir(directory):
            if f in (dirName + ".png", dirName + ".tiff"):
                # Load the main image
                p = os.path.join(directory, f)
                (loaded, volume) = slicer.util.loadVolume(p, properties, returnNode=True)
                if loaded:
                    self.current2DVectorVolume = volume
                    # Make sure that the volume is named as the directory to avoid wrong names
                    self.current2DVectorVolume.SetName(dirName)
                    self.currentCaseDir = directory
                    # Convert the 2D image in a scalar node
                    self.currentScalarVolume = self.getScalarNodeFrom2DNode(volume)
            elif f == dirName + "_label.nrrd":
                # Load a previously existing labelmap
                p = os.path.join(directory, f)
                (loaded, volume) = slicer.util.loadLabelVolume(p, returnNode=True)
                if loaded:
                    self.currentLabelmapVolume = volume
            # TODO: reuse already calculated enhanced volume. We will need to calculate the needed matrixes
            # elif f == dirName + "_enh.nrrd":
            #     # Load a previously existing enhanced volume
            #     p = os.path.join(directory, f)
            #     (loaded, volume) = slicer.util.loadVolume(p, returnNode=True)
            #     if loaded:
            #         # Create all the required structures for the Enhanced volume
            #         self.currentEnhancedVolume = volume
            #         self.currentEnhancedImageArray = slicer.util.array(self.currentEnhancedVolume.GetID())
            #         self.enhancer = Enhancer(self.currentEnhancedImageArray[0])
            elif f == "report.json":
                p = os.path.join(directory, f)
                with open(p) as f:
                    self.currentReportData = json.load(f)

        # If the labelmap didn't exist, create a new one
        if self.currentLabelmapVolume is None:
            nodeName = os.path.basename(self.__getReportImagePath__(1)).replace(".png", "")
            self.currentLabelmapVolume = self.createNewLabelmap(self.currentScalarVolume, nodeName)

        # Use our customized colors
        displayNode = self.currentLabelmapVolume.GetDisplayNode()
        displayNode.SetAndObserveColorNodeID(self.colorTableNode.GetID())

        return self.currentScalarVolume is not None

    def getCurrentDataFolder(self):
        """ Get the folder where the original image was loaded from, where we will store all the related information
        :return:
        """
        return os.path.dirname(self.current2DVectorVolume.GetStorageNode().GetFileName())

    def getScalarNodeFrom2DNode(self, vectorNode):
        """ Get a 3D vtkMRMLScalarVolumeNode (1 slice) from a vtkMRMLVectorVolumeNode
        :param vectorNode:
        :return: output volume
        """
        extract = vtk.vtkImageExtractComponents()
        extract.SetComponents(0,1,2)
        luminance = vtk.vtkImageLuminance()
        extract.SetInputConnection(vectorNode.GetImageDataConnection())
        luminance.SetInputConnection(extract.GetOutputPort())
        luminance.Update()
        ijkToRAS = vtk.vtkMatrix4x4()
        vectorNode.GetIJKToRASMatrix(ijkToRAS)

        outputVolume = slicer.mrmlScene.CreateNodeByClass("vtkMRMLScalarVolumeNode")
        slicer.mrmlScene.AddNode(outputVolume)
        outputVolume.SetName(vectorNode.GetName() + "_3D")
        outputVolume.SetIJKToRASMatrix(ijkToRAS)
        outputVolume.SetImageDataConnection(luminance.GetOutputPort())
        return outputVolume

    def createNewLabelmap(self, scalarNode, nodeName):
        """ Create a new labelmap based on a scalar node
        :param scalarNode: scalar node
        :param nodeName: name of the node
        :return: new labelmap node
        """
        logic = slicer.modules.volumes.logic()
        node = logic.CreateAndAddLabelVolume(scalarNode, nodeName)
        # Make sure that the node name is correct, because sometimes the scene adds a suffix
        node.SetName(nodeName)
        return node

    def getEnhancedVolume(self):
        """ Get the enhanced volume for the current case.
        Note the volume will be cached
        :return: enhanced volume
        """
        if self.currentEnhancedVolume is None:
            self.__calculateEnhancedVolume__()
        return self.currentEnhancedVolume

    def __calculateEnhancedVolume__(self):
        """ Calculate the enhanced volume for the first time
        :return:
        """
        logic = slicer.modules.volumes.logic()
        self.currentEnhancedVolume = logic.CloneVolume(self.current2DVectorVolume, self.current2DVectorVolume.GetName() + "_enh")
        #self.currentEnhancedVectorVolume = slicer.vtkMRMLVectorVolumeNode()
        #self.currentEnhancedVectorVolume.Copy(self.current2DVectorVolume)
        #slicer.mrmlScene.AddNode(self.currentEnhancedVectorVolume)
        self.currentEnhancedImageArray = slicer.util.array(self.currentEnhancedVolume.GetID())

        # Set a storage node for the volume and load the data
        #image_array = slicer.util.array(self.current2DVectorVolume.GetName())
        #image_array = image_array[0]    # Remove "extra" dimension
        self.enhancer = Enhancer(self.currentEnhancedImageArray[0])
        self.enhancementFineTuning()
        #self.currentEnhancedVectorVolume = self.currentScalarVolume

    def enhancementFineTuning(self, vascularFactor=0.5, enhancementFactor=0.5):
        """ Adjust the enhancement with fine tuning params
        :param vascularFactor: 0-1 value
        :param enhancementFactor: 0-1 value
        """
        output_array = self.enhancer.execute_enhancement(vascularFactor, enhancementFactor)
        self.currentEnhancedImageArray[0, :, :, :] = output_array[:,:,:]
        self.currentEnhancedVolume.Modified()   # Refresh display

    def getResourcePath(self, fileName=""):
        """ Get a full path for the current resoure file name
        :param fileName:
        :return: full path to the corresponding file name in the Resources folder
        """
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), "Resources", fileName)

    def saveReport(self, currentValuesDict):
        """ Save a JSON text file with the current values of the GUI stored in a dictionary.
        It also saves the current enhanced and labelmap volumes
        :param currentValuesDict: dictionary of values
        :return: file where the report was stored
        """
        p = os.path.join(self.getCurrentDataFolder(), "report.json")
        with open(p, "w+b") as f:
            json.dump(currentValuesDict, f)

        # Save the labelmap
        if self.currentLabelmapVolume.GetStorageNode() is None:
            SlicerUtil.saveNewNode(self.currentLabelmapVolume,
                    os.path.join(self.getCurrentDataFolder(), self.currentLabelmapVolume.GetName() + ".nrrd"))
        else:
            self.currentLabelmapVolume.GetStorageNode().WriteData(self.currentLabelmapVolume)

        # Save the enhanced volume
        if self.getEnhancedVolume().GetStorageNode() is None:
            SlicerUtil.saveNewNode(self.currentEnhancedVolume,
                    os.path.join(self.getCurrentDataFolder(), self.currentEnhancedVolume.GetName() + ".nrrd"))
        else:
            self.currentEnhancedVolume.GetStorageNode().WriteData(self.currentEnhancedVolume)

        self.isCurrentReportSaved = True
        return p

    def getKey(self, description):
        """ Get a string formatted with the chosen format for keys used in the template.
        Ex: getKey("Cotton lesions") = "@@COTTON_LESIONS@@"
        :param description:
        :return:
        """
        return "@@{0}@@".format(description.replace(" ", "_").upper())


    def __printSnapshots__(self):
        """ Generate snapshots of all the volumes to be displayed in the report
        """
        # Save a png file from different images.
        # We manipulate the widget to have the aspect that we want for the screenshot
        lm = slicer.app.layoutManager()

        # Take original image with Labelmap
        # Change to Red
        SlicerUtil.changeLayoutRedSingle()
        sliceWidget = lm.sliceWidget("Red")
        controller = sliceWidget.sliceController()
        controller.fitSliceToBackground()
        # Hide the slider bar (just show the picture)
        controller.hide()
        sliceView = sliceWidget.sliceView()
        sliceView.cornerAnnotation().ClearAllTexts()
        sliceView.scheduleRender()
        # Take the snapshot
        SlicerUtil.takeSnapshot(os.path.join(self.getCurrentDataFolder(), self.__getReportImagePath__(1)),
                                type=slicer.qMRMLScreenShotDialog.Red, hideAnnotations=True)

        # Restore the regular controller
        controller.show()

        # Enhanced (with and without labelmap)
        SlicerUtil.changeLayoutYellowSingle()

        # If the user didn't open the enhanced volume yet, force it
        enhancedVol = self.getEnhancedVolume()
        yellowCompositeNode = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceCompositeNodeYellow')
        if yellowCompositeNode.GetBackgroundVolumeID() != enhancedVol.GetID():
            yellowCompositeNode.SetBackgroundVolumeID(enhancedVol.GetID())
            yellowSliceNode = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeYellow')
            yellowSliceNode.SetOrientationToAxial()
            # Assign the labelmap
            yellowCompositeNode.SetLabelVolumeID(self.currentLabelmapVolume.GetID())

        controller = lm.sliceWidget("Yellow").sliceController()
        controller.fitSliceToBackground()
        # Hide the slider bar (just show the picture)
        controller.hide()
        # Take the snapshot
        SlicerUtil.takeSnapshot(os.path.join(self.getCurrentDataFolder(), self.__getReportImagePath__(3)),
                                type=slicer.qMRMLScreenShotDialog.Yellow, hideAnnotations=True)

        # Remove the labelmap
        controller.setLabelMapHidden(True)
        # Take the snapshot
        SlicerUtil.takeSnapshot(os.path.join(self.getCurrentDataFolder(), self.__getReportImagePath__(2)),
                                type=slicer.qMRMLScreenShotDialog.Yellow, hideAnnotations=True)


        # Restore the regular controller
        controller.show()
        controller.setLabelMapHidden(False)

    def printReport(self, currentValuesDict, callback):
        """ Generate a html report file and print it
        :param currentValuesDict: dictionary of GUI values
        """
        if not self.isCurrentReportSaved:
            # Save the report first
            self.saveReport(currentValuesDict)

        # Generate the snapshots of the images
        self.__printSnapshots__()

        self.callback = callback
        # Generate the html code
        html = self.__generateHtml__(currentValuesDict)

        # Write the html to a temp file
        p = os.path.join(self.getCurrentDataFolder(), "report.html")
        with open(p, "w+b") as f:
            f.write(html)

        self.webView = qt.QWebView()
        self.webView.settings().setAttribute(qt.QWebSettings.DeveloperExtrasEnabled, True)
        self.webView.connect('loadFinished(bool)', self.__webViewFormLoadedCallback__)
        self.webView.show()
        u = qt.QUrl(p)
        self.webView.setUrl(u)

    def __webViewFormLoadedCallback__(self, loaded):
        """ Function that is invoked when a webview has finished loading a URL
        :param loaded:
        """
        if loaded:
            outputFileName = os.path.join(self.getCurrentDataFolder(), "report.pdf")
            printer = qt.QPrinter(qt.QPrinter.HighResolution)
            printer.setOutputFormat(qt.QPrinter.PdfFormat)
            printer.setOutputFileName(outputFileName)
            self.webView.print_(printer)
            self.webView.close()
            # Call the callback
            self.callback(outputFileName)
            self.callback = None


    def __getReportImagePath__(self, imageType):
        if imageType==0:
            # Original image
            return self.current2DVectorVolume.GetStorageNode().GetFileName()
        elif imageType==1:
            # Original + Labelmap
            return self.current2DVectorVolume.GetStorageNode().GetFileName() + "_label.png"
        elif imageType==2:
            # Enhanced only
            return self.current2DVectorVolume.GetStorageNode().GetFileName() + "_enh.png"
        elif imageType==3:
            # Enhanced labeled
            return self.current2DVectorVolume.GetStorageNode().GetFileName() + "_enh_label.png"
        else:
            raise AttributeError("Invalid image type ({0})".format(imageType))

    def __generateHtml__(self, currentValuesDict):
        """ Generate an html report based on the default template
        :param currentValuesDict: text of the report
        :return: path of the html generated file
        """
        templatePath = self.getResourcePath("EyeSpot_ReportTemplate.html")
        with open(templatePath, "r+b") as f:
            html = f.read()

        # myText = '''<div id="divDescription">{0}</div>'''.format(self.__toHtml__(reportText))
        html = html.replace(self.getKey("Resources Folder"), self.getResourcePath())

        # VA
        for key in ("OS", "OD"):
            key = self.getKey(key)
            repl = currentValuesDict[key] if currentValuesDict[key] else "-"
            html = html.replace(key, repl)
        repl = currentValuesDict[self.getKey("VA Modality")] if currentValuesDict[self.getKey("VA Modality")] else ""
        html = html.replace(self.getKey("VA Modality"), repl)

        # Problems
        for key in (self.getKey("Microaneurysms"), self.getKey("Exudates"), self.getKey("Haemorrhages"),
                    self.getKey("Cotton wool spots"), self.getKey("Neovascularisation")):
            html = html.replace(key, "<span style='color: red; font-weight: bold'>YES</span>" if currentValuesDict[key] else "NO")

        # Score
        html = html.replace(self.getKey("Diabetic Retinopathy Score"), str(currentValuesDict[self.getKey("Diabetic Retinopathy Score")]))

        # Images
        html = html.replace(self.getKey("Image Original"), self.__getReportImagePath__(0))
        html = html.replace(self.getKey("Image Labeled"),  self.__getReportImagePath__(1))
        html = html.replace(self.getKey("Image Enhanced"), self.__getReportImagePath__(2))
        html = html.replace(self.getKey("Image Enhanced Labeled"), self.__getReportImagePath__(3))

        # Additional comments
        html = html.replace(self.getKey("Additional comments"), self.__textEncodeToHtml__(currentValuesDict[self.getKey("Additional comments")]))

        return html

    def __textEncodeToHtml__(self, text):
        """ Encode a plain text in html
        :param text:
        :return:
        """
        text = text.encode('ascii', 'xmlcharrefreplace')
        text = text.replace("\n", "<br/>")
        return text


class EyeSpotTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_EyeSpot_PrintMessage()

    def test_EyeSpot_PrintMessage(self):
        self.delayDisplay("Starting the test")
        logic = EyeSpotLogic()

        myMessage = "Print this test message in console"
        logging.info("Starting the test with this message: " + myMessage)
        expectedMessage = "I have printed this message: " + myMessage
        logging.info("The expected message would be: " + expectedMessage)
        responseMessage = logic.printMessage(myMessage)
        logging.info("The response message was: " + responseMessage)
        self.assertTrue(responseMessage == expectedMessage)
        self.delayDisplay('Test passed!')
