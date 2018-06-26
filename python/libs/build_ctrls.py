import logging
import pymel.core as pymel
import maya.OpenMaya as om
from python.libs import consts, naming_utils
from python.libs import shapes
from python.libs import joint_utils
from python.libs import virtual_classes
reload(shapes)
reload(naming_utils)
reload(consts)
reload(joint_utils)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def create_ctrl(jnt=None,
                network=None,
                attr=None,
                tags=None,
                axis='z',
                shape='Circle',
                size=1.0,
                name=None,
                offset=False,
                mirrored=False):

    if not name and jnt:
        info = naming_utils.ItemInfo(jnt)
        name = naming_utils.concatenate([info.side, info.base_name, info.joint_name, 'CTRL'])

    elif not name:
        name = 'Ctrl'

    ctrl = virtual_classes.CtrlNode()
    pymel.rename(ctrl, name)
    ctrl.set_shape(shape)
    ctrl.set_axis(axis)

    if mirrored:
        ctrl.setScale((-1, -1, 1))
    ctrl.freeze_transform()

    if tags:
        naming_utils.add_tags(ctrl, tags)

    if network:
        naming_utils.add_tags(ctrl, {'Network': network})

    naming_utils.add_tags(ctrl, {'Type': 'CTRL'})

    if jnt:
        ctrl.rotateOrder.set(jnt.rotateOrder.get())
        ctrl.setMatrix(jnt.getMatrix(worldSpace=True), worldSpace=True)

    ctrl.setScale((size, size, size))
    pymel.makeIdentity(apply=True, scale=True)

    if offset:
        joint_utils.create_offset_groups(ctrl, name=naming_utils.concatenate([ctrl.name(), 'Offset']))

    if attr:
        idx = attr.getNumElements()
        ctrl.message.connect(attr[idx])

    return ctrl



"""TEST CODE"""

# if __name__ == '__main__':
#
#     ctrls = CreateCtrl(jnt=pymel.selected()[0])
#     print ctrls.get_ctrl_distance()









