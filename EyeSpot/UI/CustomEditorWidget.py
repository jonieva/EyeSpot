'''
Created on Sep 29, 2014

@author: Jorge Onieva (Brigham and Women's Hospital)
'''
from Editor import EditorWidget
from __main__ import qt, slicer

from .CustomEditBox import CustomEditBox


class CustomEditorWidget(EditorWidget):
    """Customized Slicer Editor which contains just some the tools that we need for the eye marks.
    Note that the master volume and the labelmap will be invisible for the user and have to be created in advance"""
    def __init__(self, parent=None, showVolumesFrame=False,
                 activeTools=("DefaultTool", "DrawEffect", "RectangleEffect", "EraseLabel",
                              "PreviousCheckPoint", "NextCheckPoint")):
        """Constructor. Just invokes the parent's constructor"""         
        self.activeTools = activeTools
        # self.__masterVolume__ = scalarNode
        # self.__labelmapVolume__ = labelmapNode
        EditorWidget.__init__(self, parent, showVolumesFrame)

    @property
    def masterVolume(self):
        return slicer.util.getNode(self.helper.masterSelector.currentNodeID)

    @masterVolume.setter
    def masterVolume(self, value):
        self.helper.setMasterVolume(value)

    @property
    def labelmapVolume(self):
        return slicer.util.getNode(self.helper.mergeSelector.currentNodeID)

    @labelmapVolume.setter
    def labelmapVolume(self, value):
        #self.helper.merge = value
        #self.helper.mergeSelector.setCurrentNode(value)
        self.helper.setMergeVolume(value)

    def createEditBox(self):
        """Override the parent's method. Builds the editor with a limited set of tools"""
        self.editBoxFrame = qt.QFrame(self.effectsToolsFrame)
        self.editBoxFrame.objectName = 'EditBoxFrame'
        self.editBoxFrame.setLayout(qt.QVBoxLayout())
        self.effectsToolsFrame.layout().addWidget(self.editBoxFrame)
        self.toolsBox = CustomEditBox(self.activeTools, self.editBoxFrame, optionsFrame=self.effectOptionsFrame)
        
    def setThresholds(self, min, max):
        """Set the threshold for all the allowed effects"""
        self.toolsBox.setThresholds(min, max)