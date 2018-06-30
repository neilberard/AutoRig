# Imports
from PySide2 import QtCore, QtWidgets
from python.qt.Qt import loadUiType
from python.qt.Qt import QtCore, QtWidgets

from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.OpenMaya as OpenMaya
import os
import logging
import pymel.core as pymel
import maya.cmds as cmds
from python.libs import build_ctrls, shapes

reload(build_ctrls)
reload(shapes)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Load UI File
ui_path = ui_file_name = os.path.dirname(__file__) + r'\make_ctrl.ui'
FormClass, BaseClass = loadUiType(ui_file_name)


class ControlBuilderWindow(QtWidgets.QMainWindow, FormClass):
    """
    Note: Remove callbacks whenever executing code that changes the selection.
    """

    def __init__(self):
        maya_main = None
        try:
            maya_main = wrapInstance(long(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)  # GET MAIN MAYA WINDOW
        except:
            pass
        super(ControlBuilderWindow, self).__init__(maya_main)  # PARENT WINDOW
        self.events = []
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)  # DELETE WINDOW ON CLOSE
        self.setupUi(self)
        self.setWindowTitle(type(self).__name__)
        self.resize(self.vlayout.sizeHint())  # Resize to widgets
        # Get shape list
        self.shape_list = shapes.remove_file_extension()
        self.cb_shape.blockSignals(True)  # Block combobox from sending signals when updating index.
        self.cb_shape.insertItems(0, self.shape_list)
        self.cb_shape.blockSignals(False)
        self.rot_matrix = None
        self.old_value = 1.0

        # self.axis = 'x'  # Orientation of the controller

        self.sel_list = []

        self.setup_callbacks()
        # Get sel list
        self.refresh()

    def setup_callbacks(self):
        self.remove_callbacks()
        self.events = [
                        OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self.refresh)
                      ]

    def remove_callbacks(self):
        for callback in self.events:
            try:
                OpenMaya.MEventMessage.removeCallback(callback)
            except:
                pass

    def refresh(self, *args, **kwargs):
        self.sel_list = pymel.selected()
        self.old_value = 1.0
        self.sldr.setValue(100)

    @QtCore.Slot()
    def on_btn_axis_x_clicked(self):
        self.axis = 'x'
        for obj in pymel.selected():
            obj.reset_axis()
            obj.set_axis('X')


        # self.ctrl_builder.set_ctrl_axis(self.axis)

    @QtCore.Slot()
    def on_btn_axis_y_clicked(self):
        self.axis = 'y'
        for obj in pymel.selected():
            obj.reset_axis()
            obj.set_axis('Y')
        # self.ctrl_builder.set_ctrl_axis(self.axis)

    @QtCore.Slot()
    def on_btn_axis_z_clicked(self):
        self.axis = 'z'
        for obj in pymel.selected():
            obj.reset_axis()
            obj.set_axis('Z')

    @QtCore.Slot()
    def on_btn_reset_clicked(self):
        # self.refresh()
        self.sldr.setValue(100)

    @QtCore.Slot()
    def on_sldr_valueChanged(self):

        sldr_value = self.sldr.value() * .01

        # scale = (sldr_value - self.old_value) + 1.0

        if sldr_value > 0.0:
            scale = (sldr_value / self.old_value)

            for sel in self.sel_list:

                sel.shapeSize.set(sel.shapeSize.get() + (sldr_value - self.old_value))

                sel.set_shape_size(scale)

                # for shape in sel.getShapes():
                #     pymel.scale(shape.cv[:], (scale, scale, scale))

            self.old_value = sldr_value


    @QtCore.Slot()
    def on_btn_color_clicked(self):
        log.info('on_btn_color_clicked')
        color_dialog = QtWidgets.QColorDialog()
        c = color_dialog.getColor()

        multi = 1.0/255.0  # Normalize Color values

        color = (c.red() * multi, c.green() * multi, c.blue() * multi, c.alpha() * multi)
        print color

        for obj in pymel.selected():
            obj.set_shape_color(color)

    @QtCore.Slot()
    def on_cb_shape_currentIndexChanged(self):
        self.sldr.setValue(100)
        for sel in pymel.selected():
            try:
                shape = sel.getShape()
                color = shape.overrideColorRGB.get()
                sel.set_shape(self.cb_shape.currentText())
                sel.set_shape_color(color)
                sel.set_axis(sel.shapeAxis.get())
                sel.set_shape_size(sel.shapeSize.get())
            except:
                pass

        # self.ctrl_builder.set_ctrl_types(self.cb_shape.currentText())

    @QtCore.Slot()
    def on_btn_cancel_clicked(self):
        # self.ctrl_builder.delete_ctrls()
        self.close()

    @QtCore.Slot()
    def on_btn_execute_clicked(self):
        log.info('on_btn_execute_clicked')
        # self.ctrl_builder.ctrls = []
        self.close()

    @QtCore.Slot()
    def closeEvent(self, *args):
        log.info('closing')
        self.remove_callbacks()
        # self.ctrl_builder.delete_ctrls()


def showUI():
    for widget in QtWidgets.QApplication.allWidgets():
        if type(widget).__name__ == ControlBuilderWindow.__name__:
            try:
                widget.close()
            except:
                pass
    BuilderWindow = ControlBuilderWindow()
    BuilderWindow.show()
    return BuilderWindow


"""
test code.
"""

# from Projects.AutoRig.python.ui import ct
# rl_builder_window
# reload(ctrl_builder_window)


# app = QtWidgets.QApplication([])
# win = RenameToolsWindow()
# win.show()
# app.exec_()

