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

        self.mainAreaCollapsibleButton = ctk.ctkCollapsibleButton()
        self.mainAreaCollapsibleButton.text = "Image and labels"
        self.mainAreaCollapsibleButton.collapsed = False
        self.layout.addWidget(self.mainAreaCollapsibleButton)
        self.mainAreaLayout = qt.QGridLayout(self.mainAreaCollapsibleButton)
        # Select image
        row = 0
        self.loadImageButton = ctk.ctkPushButton()
        self.loadImageButton .text = "Load image"
        self.loadImageButton .toolTip = "Load the image"
        self.mainAreaLayout.addWidget(self.loadImageButton, row, 0)

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
        row += 1
        self.loadReportButton = ctk.ctkPushButton()
        self.loadReportButton.text = "Load previous report"
        self.loadReportButton.toolTip = "Load the previous annotations and colored areas for this case"
        self.loadReportButton.enabled = False
        # self.exampleButton.setIcon(qt.QIcon("{0}/Reload.png".format(SlicerUtil.CIP_ICON_DIR)))
        # self.exampleButton.setIconSize(qt.QSize(20,20))
        # self.exampleButton.setStyleSheet("font-weight:bold; font-size:12px" )
        # self.exampleButton.setFixedWidth(200)
        self.mainAreaLayout.addWidget(self.loadReportButton, row, 0)

        # Report
        row += 1
        self.reportText = qt.QTextEdit()
        self.mainAreaLayout.addWidget(self.reportText, row, 0)

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

        # Report
        row += 1


        # Enhancement
        row += 1
        self.showEnhancementCheckbox = qt.QCheckBox()
        self.showEnhancementCheckbox.setText("Show enhancement")
        self.showEnhancementCheckbox.setEnabled(False)
        self.mainAreaLayout.addWidget(self.showEnhancementCheckbox, row, 0)

        # Reset button
        row += 1
        self.resetButton = ctk.ctkPushButton()
        self.resetButton.text = "Close case"
        self.resetButton.toolTip = "Close the current case"
        self.mainAreaLayout.addWidget(self.resetButton, row, 0)

        # Editor
        row += 1
        self.editorWidget = ui.CustomEditorWidget(self.parent)
        self.editorWidget.setup()
        self.editorCollapsibleButton = self.editorWidget.editLabelMapsFrame
        self.editorCollapsibleButton.text = "Edit the current eye image"
        self.editorCollapsibleButton.collapsed = False
        self.editorCollapsibleButton.visible = False


        self.layout.addStretch(1)

        # Connections
        self.loadImageButton.connect('clicked()', self.__onLoadImageClicked__)
        self.loadReportButton.connect('clicked()', self.__onLoadReportClicked__)
        self.resetButton.connect('clicked()', self.reset)
        self.showEnhancementCheckbox.connect("stateChanged(int)", self.__onshowEnhancementCheckboxStateChanged__)


    def refreshUI(self):
        self.loadReportButton.enabled = self.logic.current2DVolume is not None
        self.showEnhancementCheckbox.enabled = self.logic.current2DVolume is not None
        
        if self.showEnhancementCheckbox.isChecked():
            # Two windows
            SlicerUtil.changeLayout(29)
        else:
            # Red Slice only
            SlicerUtil.changeLayout(6)

        compNodes = slicer.util.getNodes("vtkMRMLSliceCompositeNode*")
        for compNode in compNodes.itervalues():
            compNode.SetLinkedControl(True)
            compNode.SetLabelOpacity(0.3)

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

    def __onLoadImageClicked__(self):
        """ Load a new eye fundus image
        :return:
        """
        f = qt.QFileDialog.getOpenFileName(slicer.util.mainWindow())
        if f:
            self.loadImage(f)


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

    def __onshowEnhancementCheckboxStateChanged__(self, state):
        # Get the enhanced volume
        enhancedVol = self.logic.getEnhancedVolume()
        # Assign it to the yellow slice
        slicer.mrmlScene.GetNodeByID('vtkMRMLSliceCompositeNodeYellow').SetBackgroundVolumeID(enhancedVol.GetID())
        slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeYellow').SetOrientationToAxial()

        # Link all the controls
        compNodes = slicer.util.getNodes("vtkMRMLSliceCompositeNode*")
        for compNode in compNodes.itervalues():
            compNode.SetLinkedControl(True)
        SlicerUtil.centerAllVolumes()
        SlicerUtil.refreshActiveWindows()
        self.refreshUI()

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

        p = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Resources", "EyeSpot_Colors.ctbl")
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

    def printMessage(self, message):
        print("This is your message: ", message)
        return "I have printed this message: " + message



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
