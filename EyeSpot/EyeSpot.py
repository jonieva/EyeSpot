# coding=utf-8

import os, sys
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

import ui
from logic import *
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

        self.caseInfoFrameLayout.addWidget(qt.QLabel("Display the following images:"))

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



        # Editor
        row += 1
        self.editorWidget = ui.CustomEditorWidget(self.parent)
        self.editorWidget.setup()
        self.editorCollapsibleButton = self.editorWidget.editLabelMapsFrame
        self.editorCollapsibleButton.text = "Edit the current eye image"
        self.editorCollapsibleButton.collapsed = False
        # self.editorCollapsibleButton.visible = False
        self.layout.addWidget(self.editorCollapsibleButton)

        # self.volumeSelector = slicer.qMRMLNodeComboBox()
        # self.volumeSelector.nodeTypes = ( "vtkMRMLVectorVolumeNode", "" )
        # self.volumeSelector.selectNodeUponCreation = False
        # self.volumeSelector.addEnabled = False
        # self.volumeSelector.noneEnabled = False
        # self.volumeSelector.removeEnabled = False
        # self.volumeSelector.showHidden = False
        # self.volumeSelector.showChildNodeTypes = False
        # self.volumeSelector.setMRMLScene( slicer.mrmlScene )
        # self.volumeSelector.setToolTip( "Pick the image to edit" )
        # self.volumeSelector.enabled = False
        # self.mainAreaLayout.addWidget(self.volumeSelector, row, 1)

        # Select labelmap
        # row += 1
        # self.loadReportButton = ctk.ctkPushButton()
        # self.loadReportButton.text = "Load previous report"
        # self.loadReportButton.toolTip = "Load the previous annotations and colored areas for this case"
        # self.loadReportButton.enabled = False
        # # self.exampleButton.setIcon(qt.QIcon("{0}/Reload.png".format(SlicerUtil.CIP_ICON_DIR)))
        # # self.exampleButton.setIconSize(qt.QSize(20,20))
        # # self.exampleButton.setStyleSheet("font-weight:bold; font-size:12px" )
        # # self.exampleButton.setFixedWidth(200)
        # self.mainAreaLayout.addWidget(self.loadReportButton, row, 0)



        # self.labelmapSelector = slicer.qMRMLNodeComboBox()
        # self.labelmapSelector.nodeTypes = ( "vtkMRMLLabelMapVolumeNode", "" )
        # self.labelmapSelector.selectNodeUponCreation = False
        # self.labelmapSelector.addEnabled = False
        # self.labelmapSelector.noneEnabled = False
        # self.labelmapSelector.removeEnabled = False
        # self.labelmapSelector.showHidden = False
        # self.labelmapSelector.showChildNodeTypes = False
        # self.labelmapSelector.setMRMLScene( slicer.mrmlScene )
        # self.labelmapSelector.setToolTip( "Pick the image to edit" )
        # self.labelmapSelector.enabled = False
        # self.mainAreaLayout.addWidget(self.labelmapSelector, row, 1)

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

        self.redLesionsCheckbox = qt.QCheckBox()
        self.redLesionsCheckbox.setText("Red lesions")
        self.problemsFrameLayout.addWidget(self.redLesionsCheckbox, 0, 0)

        self.exudatesCheckbox = qt.QCheckBox()
        self.exudatesCheckbox.setText("Exudates")
        self.problemsFrameLayout.addWidget(self.exudatesCheckbox, 0, 1)

        self.microaneurysmsCheckbox = qt.QCheckBox()
        self.microaneurysmsCheckbox.setText("Microaneurysms")
        self.problemsFrameLayout.addWidget(self.microaneurysmsCheckbox, 0, 2)

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

        self.reportText = qt.QTextEdit()
        self.reportText.setStyleSheet("margin: 10px")
        self.diagnosisAreaLayout.addWidget(self.reportText)

        self.printReportButton = ctk.ctkPushButton()
        self.printReportButton.text = "Print report"
        self.diagnosisAreaLayout.addWidget(self.printReportButton)







        self.layout.addStretch(1)

        # Connections
        self.loadCaseButton.connect('clicked()', self.__onLoadCaseClicked__)
        # self.loadReportButton.connect('clicked()', self.__onLoadReportClicked__)
        self.printReportButton.connect('clicked()', self.__onPrintReportClicked__)
        self.showEnhancementCheckboxGroup.connect("buttonClicked (int)", self.__onEnhancementButtonGroupClicked__)
        self.resetButton.connect('clicked()', self.reset)


        SlicerUtil.changeLayout(6)
        compNodes = slicer.util.getNodes("vtkMRMLSliceCompositeNode*")
        for compNode in compNodes.itervalues():
            compNode.SetLinkedControl(True)
            compNode.SetLabelOpacity(0.3)

    def refreshUI(self):
        return
        # self.loadReportButton.enabled = self.logic.current2DVolume is not None
        for button in self.showEnhancementCheckboxGroup.buttons():
            button.setEnabled(self.logic.current2DVolume is not None)
        
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

        self.editorCollapsibleButton.visible = self.logic.currentLabelmapVolume is not None


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
            self.logic.current2DVolume = volume
            # Convert the 2D image in a scalar node
            self.logic.currentScalarVolume = self.logic.getScalarNodeFrom2DNode(volume)
            # set the scalar node as the active in the selector
            # self.volumeSelector.setCurrentNode(volume)
            # Create an empty labelmap volume
            nodeName = self.logic.current2DVolume.GetName() + "_label"
            self.logic.currentLabelmapVolume = self.logic.createNewLabelmap(self.logic.currentScalarVolume, nodeName)
            # Active the labelmap in the scene (but not the scalar node because we don't want a grayscale image in the scene
            self.setActiveVolumeId(None, self.logic.currentLabelmapVolume.GetID())
            # Set a default text for the report
            self.insertDefaultReportText()

        self.refreshUI()
        return loaded

    def insertDefaultReportText(self):
        cursor = qt.QTextCursor(self.reportText.document())
        cursor.insertHtml("Patient ID: <b>{0}</b>".format(self.logic.current2DVolume.GetName()))
        #cursor.insertHtml("Caso: {0}<br/>".format(self.logic.current2DVolume.GetName()))
        cursor.insertBlock()
        s = "No se han detectado anomalías"
        cursor.insertHtml(s.decode("utf-8"))


    def reset(self):
        slicer.mrmlScene.Clear(0)
        self.showEnhancementCheckboxGroup.buttons()[0].setChecked(True)
        self.__initVars__()
        self.refreshUI()

    def enter(self):
        """This is invoked every time that we select this module as the active module in Slicer (not only the first time)"""
        pass

    def exit(self):
        """This is invoked every time that we switch to another module (not only when Slicer is closed)."""
        pass

    def cleanup(self):
        """This is invoked as a destructor of the GUI when the module is no longer going to be used"""
        pass

    def __onLoadCaseClicked__(self):
        """ Load a new eye fundus image
        :return: True if an image was loaded
        """
        #f = qt.QFileDialog.getOpenFileName(slicer.util.mainWindow())
        dir = qt.QFileDialog.getExistingDirectory()
        if dir:
            dirName = os.path.basename(dir)
            for f in os.listdir(dir):
                print f
                if f.startswith(dirName + "."):
                    self.loadImage(os.path.join(dir, f))
                    return True
        return False

    def __onLoadReportClicked__(self):
        f = qt.QFileDialog.getOpenFileName(slicer.util.mainWindow())
        if f:
            (loaded, volume) = slicer.util.loadLabelVolume(f, returnNode=True)
            if loaded:
                selectionNode = slicer.app.applicationLogic().GetSelectionNode()
                self.volumeSelector.setCurrentNode(volume)
                selectionNode.SetReferenceActiveLabelVolumeID(volume.GetID())
                slicer.app.applicationLogic().PropagateVolumeSelection(0)
                self.currentLabelmapPath = f

    def __onPrintReportClicked__(self):
        self.logic.generateHtml(self.reportText.plainText)

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

        self.current2DVolume = None
        self.currentScalarVolume = None
        self.currentLabelmapVolume = None
        self.currentAnnotationsPath = None
        self.enhancedVolume = None

        p = self.getResourcePath("EyeSpot_Colors.ctbl")
        self.colorTableNode = slicer.modules.colors.logic().LoadColorFile(p)

    def getFolder(self, volume):
        return os.path.dirname(volume.GetStorageNode().GetFileName())

    def getScalarNodeFrom2DNode(self, vectorNode):
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
        if self.enhancedVolume is None:
            self.__calculateEnhancedVolume__()
        return self.enhancedVolume

    def __calculateEnhancedVolume__(self):
        self.enhancedVolume = self.current2DVolume

    def getResourcePath(self, fileName):
        """ Get a full path for the current resoure file name
        :param fileName:
        :return: full path to the corresponding file name in the Resources folder
        """
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), "Resources", fileName)

    def printMessage(self, message):
        print("This is your message: ", message)
        return "I have printed this message: " + message

    def generateHtml(self, reportText):
        """ Generate an html report based on the default template
        :param reportText: text of the report
        :return: html generated
        """
        templatePath = self.getResourcePath("EyeSpot_ReportTemplate.html")
        with open(templatePath, "r+b") as f:
            html = f.read()

        # Replace the description
        #expr = ".*<div id=\"divDescription\">(.*)</div>"
        #m = re.match(expr, s, re.DOTALL)
        repl = '''
<div id="divDescription">
(Description)
</div>'''
        myText = '''
<div id="divDescription">
{0}
</div>'''.format(self.__toHtml__(reportText))
        html = html.replace(repl, myText)
        print("Replaced text:")
        print(html)

        # save the file
        p = os.path.join(SlicerUtil.getModuleFolder("EyeSpot"), "results", "temp.html")
        print p
        with open(p, "w+b") as f:
            f.write(html)
        return html

    def __toHtml__(self, text):
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

# import re
# s='''
# <html>
# <head>
# <meta content="text/html; charset=ISO-8859-1"
# http-equiv="content-type">
# <title>EyeSpot</title>
# <style type="text/css">
# #divDescription {
# margin-bottom: 15px;
# margin-top: 15px;
# }
#
# </style>
# </head>
# <body>
# <big style="font-weight: bold;">EyeSpot Report</big><br>
# <div id="divDescription">
# (Description)
# </div>
# <img id="img1" style="width: 400px;" alt="eye_fundus"
# src="file:///Data/jonieva/OneDrive/EyeSpot/diaretdb1_v_1_1/resources/images/ddb1_fundusimages/image001.png"><br>
# <br>
# </body>
# </html>
# '''
#
#
# repl = '''<div id="divDescription">
# (Description)
# </div>'''
# myText = '''
# <div id="divDescription">
# New description
# </div>
# '''
# s.replace(repl, myText)
#
#
#
# expr = ".*<div id=\"divDescription\">(?P<descr>.*)</div>"
# m = re.match(expr, s, re.DOTALL)
# repl = "\g<descr>my description"
# re.sub(expr, repl, s, flags=re.DOTALL)
# m.group(1)
