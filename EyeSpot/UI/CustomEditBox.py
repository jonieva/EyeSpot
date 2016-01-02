from __main__ import qt, slicer
#import EditorLib
from EditorLib import EditUtil, EditBox

class CustomEditBox(EditBox):
    '''
    Class that customizes the available tools in the editor
    '''
    def __init__(self, activeTools, parent, optionsFrame=None):
        """Constructor. Just invokes the parent's constructor"""
        self.activeTools = activeTools
        EditBox.__init__(self, parent, optionsFrame)

    def create(self):
        """Overriden from the parent. Called in init method. Similar to parent's one but restricting the available options"""
        # the buttons
        self.rowFrames = []
        self.actions = {}
        self.buttons = {}
        self.icons = {}
        self.callbacks = {}

        self.findEffects()

        self.mainFrame = qt.QFrame(self.parent)
        self.mainFrame.objectName = 'MainFrame'
        vbox = qt.QVBoxLayout()
        self.mainFrame.setLayout(vbox)
        self.parent.layout().addWidget(self.mainFrame)

        # create all of the buttons that are going to be used
        self.createButtonRow(self.activeTools)
        self.toolsActiveToolFrame = qt.QFrame(self.parent)
        self.toolsActiveTool = qt.QLabel(self.toolsActiveToolFrame)
        self.toolsActiveToolName = qt.QLabel(self.toolsActiveToolFrame)

        self.updateUndoRedoButtons()

        self.setDefaultParams()

    def setDefaultParams(self):
        """Configure here all the required params for any LabelEffect (Paint, Draw, ect.)"""
        self.editUtil = EditUtil.EditUtil()
        self.parameterNode = self.editUtil.getParameterNode()

        self.parameterNode.SetParameter("LabelEffect,paintOver", "1") # Enable paintOver
        self.parameterNode.SetParameter("LabelEffect,paintThreshold", "0")   # Enable Threshold checkbox
