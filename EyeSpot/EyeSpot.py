# coding=utf-8

import os, sys
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import json
import ui
from logic import SlicerUtil, Util
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

        self.caseInfoFrameLayout = qt.QVBoxLayout()
        self.caseInfoFrame.setLayout(self.caseInfoFrameLayout)

        self.caseIdLabel = qt.QLabel("Case id: ")
        self.caseInfoFrameLayout.addWidget(self.caseIdLabel)

        # self.caseInfoFrameLayout.addWidget(qt.QLabel("Display the following images:"))

        self.showEnhancementCheckboxGroup = qt.QButtonGroup()
        self.showJustOriginalButton = qt.QRadioButton("Original only")
        self.showJustOriginalButton.setChecked(True)
        self.showEnhancementCheckboxGroup.addButton(self.showJustOriginalButton, 0)
        self.caseInfoFrameLayout.addWidget(self.showJustOriginalButton)

        self.showOriginalPlusEnhancedButton = qt.QRadioButton("Original and enhanced")
        self.showEnhancementCheckboxGroup.addButton(self.showOriginalPlusEnhancedButton, 1)
        self.caseInfoFrameLayout.addWidget(self.showOriginalPlusEnhancedButton)

        self.showJustEnhancedButton = qt.QRadioButton("Enhanced only")
        self.showEnhancementCheckboxGroup.addButton(self.showJustEnhancedButton, 2)
        self.caseInfoFrameLayout.addWidget(self.showJustEnhancedButton)

        # Center Volumes button
        self.centerVolumesButton = ctk.ctkPushButton()
        self.centerVolumesButton.text = "Center image/s"
        self.centerVolumesButton.toolTip = "Center all the current visible images"
        self.centerVolumesButton.setFixedWidth(200)
        # self.centerVolumesButton.toolTip = "Load a case folder"
        self.caseInfoFrameLayout.addWidget(self.centerVolumesButton)

        # Editor
        row += 1
        self.editorWidget = ui.CustomEditorWidget(self.parent)
        self.editorWidget.setup()
        self.editorCollapsibleButton = self.editorWidget.editLabelMapsFrame
        self.editorCollapsibleButton.text = "Edit the current eye image"
        self.editorCollapsibleButton.collapsed = False
        self.editorWidget.toolsColor.terminologyCollapsibleButton.setVisible(False)
        self.layout.addWidget(self.editorCollapsibleButton)

        self.diagnosisCollapsibleButton = ctk.ctkCollapsibleButton()
        self.diagnosisCollapsibleButton.text = "Diagnosis"
        self.diagnosisCollapsibleButton.collapsed = False
        self.layout.addWidget(self.diagnosisCollapsibleButton)
        self.diagnosisAreaLayout = qt.QVBoxLayout(self.diagnosisCollapsibleButton)

        # Problems detected
        # row += 1
        label = qt.QLabel("Problems detected: ")
        label.setStyleSheet("margin: 10px 0 0 10px; font-weight: bold")
        self.diagnosisAreaLayout.addWidget(label)

        # row += 1
        self.problemsFrame = qt.QFrame()
        self.problemsFrame.setFrameStyle(0x0002 | 0x0010)
        self.problemsFrame.lineWidth = 2
        self.problemsFrame.setStyleSheet("background-color: #EEEEEE; margin: 10px")
        self.diagnosisAreaLayout.addWidget(self.problemsFrame)

        self.problemsFrameLayout = qt.QGridLayout()
        self.problemsFrame.setLayout(self.problemsFrameLayout)
        self.problemsButtonGroup = qt.QButtonGroup()

        self.redLesionsCheckbox = qt.QCheckBox()
        self.redLesionsCheckbox.setText("Red lesions")
        self.problemsFrameLayout.addWidget(self.redLesionsCheckbox, 0, 0)
        self.problemsButtonGroup.addButton(self.redLesionsCheckbox)

        self.exudatesCheckbox = qt.QCheckBox()
        self.exudatesCheckbox.setText("Exudates")
        self.problemsFrameLayout.addWidget(self.exudatesCheckbox, 0, 1)
        self.problemsButtonGroup.addButton(self.exudatesCheckbox)

        self.microaneurysmsCheckbox = qt.QCheckBox()
        self.microaneurysmsCheckbox.setText("Microaneurysms")
        self.problemsFrameLayout.addWidget(self.microaneurysmsCheckbox, 0, 2)
        self.problemsButtonGroup.addButton(self.microaneurysmsCheckbox)

        label = qt.QLabel("Diabetic retinopathy diagnosis: ")
        label.setStyleSheet("margin: 10px 0 0 10px; font-weight: bold")
        self.diagnosisAreaLayout.addWidget(label)

        # Diagnosis
        self.diagnosisFrame = qt.QFrame()
        self.diagnosisFrame.setFrameStyle(0x0002 | 0x0010)
        self.diagnosisFrame.lineWidth = 2
        self.diagnosisFrame.setStyleSheet("background-color: #EEEEEE; margin: 10px")
        self.diagnosisAreaLayout.addWidget(self.diagnosisFrame)

        self.diagnosisFrameLayout = qt.QHBoxLayout()
        self.diagnosisFrame.setLayout(self.diagnosisFrameLayout)

        self.diagnosisRadioButtonGroup = qt.QButtonGroup()
        for i in range(5):
            rb = qt.QRadioButton(str(i))
            self.diagnosisRadioButtonGroup.addButton(rb, i)
            self.diagnosisFrameLayout.addWidget(rb)
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
        self.diagnosisAreaLayout.addWidget(self.saveReportButton)

        self.printReportButton = ctk.ctkPushButton()
        self.printReportButton.text = "Print report"
        self.diagnosisAreaLayout.addWidget(self.printReportButton)


        self.layout.addStretch(1)

        # Connections
        self.loadCaseButton.connect('clicked()', self.__onLoadCaseClicked__)
        # self.loadReportButton.connect('clicked()', self.__onLoadReportClicked__)
        self.showEnhancementCheckboxGroup.connect("buttonClicked (int)", self.__onEnhancementButtonGroupClicked__)
        self.centerVolumesButton.connect('clicked()', SlicerUtil.centerAllVolumes)
        self.saveReportButton.connect('clicked()', self.__onSaveReportClicked__)
        self.printReportButton.connect('clicked()', self.__onPrintReportClicked__)
        self.resetButton.connect('clicked()', self.reset)

        # Set default layout Red
        SlicerUtil.changeLayout(6)
        compNodes = slicer.util.getNodes("vtkMRMLSliceCompositeNode*")
        for compNode in compNodes.itervalues():
            compNode.SetLinkedControl(True)
            compNode.SetLabelOpacity(0.3)

        self.refreshUI()

    @property
    def isCaseLoaded(self):
        return self.logic.current2DVectorVolume is not None

    def refreshUI(self):
        self.resetButton.setVisible(self.isCaseLoaded)
        self.caseInfoFrame.setVisible(self.isCaseLoaded)
        self.editorCollapsibleButton.setVisible(self.isCaseLoaded)
        self.diagnosisCollapsibleButton.setVisible(self.isCaseLoaded)


        if self.isCaseLoaded:
            self.caseIdLabel.text = "Case Id: " + self.logic.current2DVectorVolume.GetName()

            for button in self.showEnhancementCheckboxGroup.buttons():
                button.setEnabled(self.logic.current2DVectorVolume is not None)
        
            # if self.showEnhancementCheckbox.isChecked():
            #     # Two windows
            #     SlicerUtil.changeLayout(29)
            # else:
            #     # Red Slice only
            #     SlicerUtil.changeLayout(6)
            if self.showEnhancementCheckboxGroup.checkedId() == 0:
                # Just original. Red Slice only
                SlicerUtil.changeLayout(6)
            elif self.showEnhancementCheckboxGroup.checkedId() == 1:
                # Original + Enhanced
                SlicerUtil.changeLayout(29)
            elif self.showEnhancementCheckboxGroup.checkedId() == 2:
                # Just enhanced. Yellow Slice
                SlicerUtil.changeLayout(7)

    def setActiveVolumeId(self, volumeId, labelmapId=None):
        selectionNode = slicer.app.applicationLogic().GetSelectionNode()
        if volumeId is not None and volumeId != "":
            selectionNode.SetReferenceActiveVolumeID(volumeId)
        if labelmapId is not None and labelmapId != "":
            selectionNode.SetReferenceActiveLabelVolumeID(labelmapId)
        slicer.app.applicationLogic().PropagateVolumeSelection(0)

    def loadImage(self, filePath):
        """ Load a new eye image and create a labelmap for it.
        It also sets the images as the active ones in the scene
        :param filePath: file path for the image
        :return: True if the image and the labelmap have been sucessfully created
        """
        properties = {}
        properties['singleFile'] = True
        (loaded, volume) = slicer.util.loadVolume(filePath, properties, returnNode=True)
        if loaded:
            self.logic.current2DVectorVolume = volume
            self.logic.currentCaseDir = os.path.dirname(filePath)
            # Convert the 2D image in a scalar node
            self.logic.currentScalarVolume = self.logic.getScalarNodeFrom2DNode(volume)
            # set the scalar node as the active in the selector
            # self.volumeSelector.setCurrentNode(volume)
            # Create an empty labelmap volume
            nodeName = self.logic.current2DVectorVolume.GetName() + "_label"
            self.logic.currentLabelmapVolume = self.logic.createNewLabelmap(self.logic.currentScalarVolume, nodeName)
            # Active the labelmap in the scene (but not the scalar node because we don't want a grayscale image in the scene
            self.setActiveVolumeId(None, self.logic.currentLabelmapVolume.GetID())
            # Set a default text for the report
            #self.insertDefaultReportText()

        self.refreshUI()
        return loaded

    def insertDefaultReportText(self):
        cursor = qt.QTextCursor(self.additionalCommentsText.document())
        cursor.insertHtml("Patient ID: <b>{0}</b>".format(self.logic.current2DVectorVolume.GetName()))
        #cursor.insertHtml("Caso: {0}<br/>".format(self.logic.current2DVectorVolume.GetName()))
        cursor.insertBlock()
        s = "No se han detectado anomalías"
        cursor.insertHtml(s.decode("utf-8"))

    def getCurrentReportData(self):
        """ Get a dictionary with the current information of the UI
        :return:
        """
        report = {}
        # Problems checked
        for button in self.problemsButtonGroup.buttons():
            report[button.text] = button.isChecked()

        # Diabetic Retinopathy Score
        report["DiabeticRetinopathyScore"] = self.diagnosisRadioButtonGroup.checkedId()

        # Additional comments
        report["AdditionalComments"] = self.additionalCommentsText.plainText

        return report

    def reset(self):
        slicer.mrmlScene.Clear(0)
        self.showEnhancementCheckboxGroup.buttons()[0].setChecked(True)
        self.__initVars__()
        self.refreshUI()



    def enter(self):
        """This is invoked every time that we select this module as the active module in Slicer (not only the first time)"""
        self.__setLabelmapOutlines__()

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
        #f = qt.QFileDialog.getOpenFileName(slicer.util.mainWindow())
        dir = qt.QFileDialog.getExistingDirectory()
        if dir:
            dirName = os.path.basename(dir)
            for f in os.listdir(dir):
                if f == dirName + ".png":
                    self.loadImage(os.path.join(dir, f))
                    return True
        return False

    # def __onLoadReportClicked__(self):
    #     f = qt.QFileDialog.getOpenFileName(slicer.util.mainWindow())
    #     if f:
    #         (loaded, volume) = slicer.util.loadLabelVolume(f, returnNode=True)
    #         if loaded:
    #             selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    #             self.volumeSelector.setCurrentNode(volume)
    #             selectionNode.SetReferenceActiveLabelVolumeID(volume.GetID())
    #             slicer.app.applicationLogic().PropagateVolumeSelection(0)
    #             self.currentLabelmapPath = f



    def __onSaveReportClicked__(self):
        reportPath = self.logic.saveReport(self.getCurrentReportData())
        qt.QMessageBox.information(slicer.util.mainWindow(), 'Report saved',
                'The report was successfully saved in ' + reportPath)


    def __onPrintReportClicked__(self):
       self.logic.printReport(self.getCurrentReportData(), self.__printReportCallback__)

    def __printReportCallback__(self, reportFile):
        if qt.QMessageBox.question(slicer.util.mainWindow(), 'Report printed',
            'The report was generated successfully. Do you want to open it now?',
            qt.QMessageBox.Yes|qt.QMessageBox.No) == qt.QMessageBox.Yes:
            # Open the file
            Util.openFile()


    # def __onshowEnhancementCheckboxStateChanged__(self, state):
    #     # Get the enhanced volume
    #     enhancedVol = self.logic.getEnhancedVolume()
    #     # Assign it to the yellow slice
    #     slicer.mrmlScene.GetNodeByID('vtkMRMLSliceCompositeNodeYellow').SetBackgroundVolumeID(enhancedVol.GetID())
    #     slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeYellow').SetOrientationToAxial()
    #
    #     # Link all the controls
    #     compNodes = slicer.util.getNodes("vtkMRMLSliceCompositeNode*")
    #     for compNode in compNodes.itervalues():
    #         compNode.SetLinkedControl(True)
    #     SlicerUtil.centerAllVolumes()
    #     SlicerUtil.refreshActiveWindows()
    #     self.refreshUI()

    def __onEnhancementButtonGroupClicked__(self, buttonId):
        self.refreshUI()

        if buttonId in (1,2):
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

        self.current2DVectorVolume = None
        self.currentScalarVolume = None
        self.currentLabelmapVolume = None
        self.currentEnhancedVolume = None

        p = self.getResourcePath("EyeSpot_Colors.ctbl")
        self.colorTableNode = slicer.modules.colors.logic().LoadColorFile(p)

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
        # Use our customized colors
        displayNode = node.GetDisplayNode()
        displayNode.SetAndObserveColorNodeID(self.colorTableNode.GetID())
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
        logic = slicer.modules.volumes.logic()
        self.currentEnhancedVolume = logic.CloneVolume(self.currentScalarVolume, self.current2DVectorVolume.GetName() + "_enh")
        # self.currentEnhancedVectorVolume = slicer.vtkMRMLVectorVolumeNode()
        # self.currentEnhancedVectorVolume.Copy(self.current2DVectorVolume)
        # slicer.mrmlScene.AddNode(self.currentEnhancedVectorVolume)

        # Set a storage node for the volume and load the data


        a = slicer.util.array(self.currentEnhancedVolume.GetID())
        b = slicer.util.array(self.current2DVectorVolume.GetID())
        a[0, :, :] = b[0, :, :, 1]
        self.currentEnhancedVolume.GetImageData().Modified()
        #self.currentEnhancedVectorVolume = self.currentScalarVolume

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
        # Save a png file of the labelmap. We manipulate the widget to have the aspect that we want for the screenshot
        lm = slicer.app.layoutManager()
        SlicerUtil.changeLayout(6)
        controller = lm.sliceWidget("Red").sliceController()
        controller.fitSliceToBackground()
        # Hide the slider bar (just show the picture)
        controller.hide()
        # Take the snapshot
        SlicerUtil.snapshot(os.path.join(self.getCurrentDataFolder(), self.currentLabelmapVolume.GetName() + ".png"), slicer.qMRMLScreenShotDialog.Red)
        # Restore the regular controller
        controller.show()
        # TODO: save the enhanced volume
        return p



    def printReport(self, currentValuesDict, callback):
        """ Generate a html report file and print it
        :param currentValuesDict: dictionary of GUI values
        """
        self.callback = callback
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

    def __generateHtml__(self, currentValuesDict):
        """ Generate an html report based on the default template
        :param currentValuesDict: text of the report
        :return: path of the html generated file
        """
        templatePath = self.getResourcePath("EyeSpot_ReportTemplate.html")
        with open(templatePath, "r+b") as f:
            html = f.read()

        # Replace the description
        #expr = ".*<div id=\"divDescription\">(.*)</div>"
        #m = re.match(expr, s, re.DOTALL)

        # myText = '''<div id="divDescription">{0}</div>'''.format(self.__toHtml__(reportText))
        html = html.replace("@@RESOURCES_FOLDER@@", self.getResourcePath())
        html = html.replace("@@DIABETIC_RETINOPATHY_SCORE@@", str(currentValuesDict["DiabeticRetinopathyScore"]))
        html = html.replace("@@RED_LESIONS@@", "YES" if currentValuesDict["Red lesions"] else "NO")
        html = html.replace("@@EXUDATES@@", "YES" if currentValuesDict["Exudates"] else "NO")
        html = html.replace("@@MICROANEURYSMS@@", "YES" if currentValuesDict["Microaneurysms"] else "NO")
        html = html.replace("@@ADDITIONAL_COMMENTS@@", self.__toHtml__(currentValuesDict["AdditionalComments"]))
        html = html.replace("@@IMAGE_ORIGINAL@@", self.current2DVectorVolume.GetStorageNode().GetFileName())
        html = html.replace("@@IMAGE_ANNOTATED@@", self.currentLabelmapVolume.GetStorageNode().GetFileName().replace(".nrrd", ".png"))
        html = html.replace("@@IMAGE_ENHANCED@@", self.current2DVectorVolume.GetStorageNode().GetFileName())

        return html

    def __toHtml__(self, text):
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
