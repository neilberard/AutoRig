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
                axis='',
                shape='Circle',
                size=1.0,
                name=None,
                offset=False,
                mirrored=False):

    """

    :param jnt: This will set ctrl orientation to jnt specified.
    :param network: This will add a tag for network specified.
    :param attr: This will connect the ctrl message to the net attr specified.
    :param tags:
    :param axis: This will rotate the ctrl shape by 90 or -90 degrees based on axis, ie '-z', 'x'
    :param shape: Shape to import based on file name, ie "Cube01"
    :param size:
    :param name:
    :param offset: Create an Offset Group for the ctrl
    :param mirrored: Scale by -X
    :return: Ctrl Node.
    """

    if not name and jnt:
        info = naming_utils.ItemInfo(jnt)
        name = naming_utils.concatenate([info.side, info.base_name, info.joint_name, 'CTRL'])

    elif not name:
        name = 'Ctrl'

    ctrl = virtual_classes.CtrlNode()
    pymel.rename(ctrl, name)
    ctrl.set_shape(shape)

    if mirrored:
        ctrl.setScale((-1, 1, 1))
    ctrl.freeze_transform()

    if tags:
        naming_utils.add_tags(ctrl, tags)

    if network:
        naming_utils.add_tags(ctrl, {'Network': network})

    naming_utils.add_tags(ctrl, {'Type': 'CTRL'})

    # Shape Scale Attr
    ctrl.addAttr('shapeSize', attributeType='float')
    ctrl.shapeSize.set(size)

    # Shape Axis
    ctrl.addAttr('shapeAxis', dataType='string')
    ctrl.shapeAxis.set(axis)

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

    if axis:
        ctrl.set_axis(axis)

    return ctrl



"""TEST CODE"""

# if __name__ == '__main__':
#
#     ctrls = CreateCtrl(jnt=pymel.selected()[0])
#     print ctrls.get_ctrl_distance()









