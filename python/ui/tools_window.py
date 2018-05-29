# Imports
# from PySide2 import QtCore, QtWidgets, QtGui
from PySide2 import QtCore, QtWidgets
from python.qt.Qt import loadUiType
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.OpenMaya as OpenMaya
import os
import logging
import pymel.core as pymel

# Libs
from python.interop.utils import attr_utils
from python.libs import build_ctrls, joint_utils, pose_utils, ikfk_switch
from python.ui import ctrl_builder_window
from python.modules import build_rig


reload(build_rig)
reload(ctrl_builder_window)
reload(attr_utils)
reload(ikfk_switch)
reload(build_ctrls)
reload(joint_utils)
reload(pose_utils)


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Load UI File
ui_path = ui_file_name = os.path.dirname(__file__) + r'\tools_window.ui'
FormClass, BaseClass = loadUiType(ui_file_name)


class ToolsWindow(QtWidgets.QMainWindow, FormClass):
    def __init__(self):
        maya_main = wrapInstance(long(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)  # GET MAIN MAYA WINDOW
        super(ToolsWindow, self).__init__(maya_main)  # PARENT WINDOW
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)  # DELETE WINDOW ON CLOSE

        log.info(self.__class__.__name__)
        self.setupUi(self)
        self.events = []
        self.pb_main.hide()  # Hide Progress Bar
        self.setup_callbacks()  # Add Callbacks

    def setup_callbacks(self):
        self.remove_callbacks()
        self.events = [
            OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self.update_cb_ctrl_space)
        ]
    def remove_callbacks(self):
        for callback in self.events:
            OpenMaya.MEventMessage.removeCallback(callback)


    # @QtCore.Slot(): Decorator based on widget name that connects QT signal.
    @QtCore.Slot()
    def on_btn_unlock_attr_clicked(self):
        attr_utils.unlock_attributes(nodes=pymel.selected())

    @QtCore.Slot()
    def on_btn_fk_ctrls_clicked(self):
        builder_window = ctrl_builder_window.showUI()

    @QtCore.Slot()
    def on_btn_rename_clicked(self):
        from python.HacknSlash.python.ui import rename_tools_window
        rename_tools_window.showUI()

    @QtCore.Slot()
    def on_btn_build_ikfk_clicked(self):
        with pymel.UndoChunk():
            joint_utils.build_ik_fk_joints(joints=pymel.selected())

    @QtCore.Slot()
    def on_btn_offset_transforms_clicked(self):
        with pymel.UndoChunk():
            joint_utils.create_offset_groups(objects=pymel.selected())

    @QtCore.Slot()
    def on_btn_delete_controls_clicked(self):
        pass
        # hs_clean.cleanup()

    @QtCore.Slot()
    def on_btn_make_switch_clicked(self):
        with pymel.UndoChunk():
            HS_IK.make_switch_utility(pymel.selected()[0])

    @QtCore.Slot()
    def on_btn_build_humanoid_clicked(self):
        log.info('on_btn_build_humanoid_clicked')
        self.remove_callbacks()
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.pb_main.setValue(0)
        self.pb_main.show()
        build_rig.build_humanoid_rig(self.pb_main, mirror=False)
        self.setup_callbacks()

    @QtCore.Slot()
    def on_btn_delete_all_ctrls_clicked(self):
        log.info('on_btn_delete_all_ctrls_clicked')
        build_rig.delete_rig()

    @QtCore.Slot()
    def on_btn_mirror_ctrls_clicked(self):
        log.info('on_btn_mirror_ctrls_clicked')
        pose_utils.mirror_ctrls(pymel.selected())

    @QtCore.Slot()
    def on_btn_reset_rig_clicked(self):
        log.info('on_btn_reset_rig_clicked')
        pose_utils.reset_rig()

    @QtCore.Slot()
    def on_btn_to_ik_clicked(self):
        log.info('on_btn_to_ik_clicked')
        ikfk_switch.switch_to_ik()

    @QtCore.Slot()
    def on_btn_to_fk_clicked(self):
        log.info('on_btn_to_fk_clicked')
        ikfk_switch.switch_to_fk()

    @QtCore.Slot()
    def on_btn_select_all_ctrls_clicked(self):
        log.info('btn_select_all_ctrls')
        pose_utils.select_all_ctrls()

    def update_cb_ctrl_space(self, *args, **kwargs):
        self.cb_space.clear()

        if pymel.selected():
            sel = pymel.selected()[-1]
            if sel.hasAttr('Space'):
                self.cb_space.addItems(sel.Space.getEnums().keys())


    @QtCore.Slot()
    def closeEvent(self, *args):
        self.remove_callbacks()

def showUI():
    for widget in QtWidgets.QApplication.allWidgets():
        if type(widget).__name__ == ToolsWindow.__name__:
            try:
                widget.close()
            except:
                pass
    rename_tools_window = ToolsWindow()
    rename_tools_window.show()


"""test Code"""
# if __name__ == '__main__':
#     app = QtWidgets.QApplication([])
#     win = ToolsWindow()
#     win.show()
#     app.exec_()

#C:\Program Files\Autodesk\Maya2017\bin\mayapy E:\Python_Projects\Projects\AutoRig\python\ui\tools_window.py

# from Projects.AutoRig.python.ui import tools_window
# tools_window.showUI()

# reload(tools_window_ui)
# win = tools_window_ui.ToolsWindow()
# win.show()


