import pymel.core as pymel
from python.libs import virtual_classes, ikfk_switch, general_utils
reload(ikfk_switch)
reload(virtual_classes)
reload(general_utils)


@general_utils.undo
def reset_rig():
    for obj in pymel.listTransforms():
        reset_ctrl(obj)


@general_utils.undo
def reset_selected():
    for obj in pymel.selected():
        reset_ctrl(obj)


@general_utils.undo
def reset_limb():
    ctrl = pymel.selected()[0]
    for obj in ctrl.getLimbCtrls():
        reset_ctrl(obj)

def reset_ctrl(obj):
    if obj.hasAttr('Type') and obj.Type.get() == 'CTRL':
        try:
            obj.setRotation((0, 0, 0))
            obj.setTranslation((0, 0, 0))
            obj.setScale((1, 1, 1))
            for attr in obj.listAttr(userDefined=True, scalar=True):
                if attr.name() != 'Offset':
                    attr.set(0)
        except:
            pass


def select_all_ctrls():
    pymel.select(None)
    selection_list = []

    for obj in pymel.listTransforms():
        if obj.hasAttr('Type') and obj.Type.get() == 'CTRL':
            selection_list.append(obj)

    pymel.select(selection_list)


def get_mirror_data(obj):
    """Returns mirrored obj with transforms{rot:'', pos:''} Note: Key 'Pos' not included with FK ctrls"""

    transforms = {}

    if obj.region == 'Spine' or obj.region == 'Head' or obj.region == 'Main':
        mirrored_obj = obj

    else:
        mirrored_obj = obj.getMirroredCtrl()
        if obj.network.switch:
            ikfk_value = obj.network.switch.IKFK.get()
            mirrored_obj.network.switch.IKFK.set(ikfk_value)

    pos = obj.getTranslation(worldSpace=False)
    rot = obj.getRotation(quaternion=True)

    # For IK CTRLs that are oriented to worldspace and require mirrored position.
    if not obj.hasAttr('Axis'):  # todo: add support for alternate mirror axis
        rot[0] = rot[0] * -1
        rot[3] = rot[3] * -1
        pos[0] = pos[0] * -1
        transforms['rot'] = rot
        transforms['pos'] = pos
    # Fk CTRL **Rotation only**
    else:
        transforms['rot'] = rot

    if obj.hasAttr('Space'):
        transforms['space'] = obj.getAttr('Space')

    return [mirrored_obj, transforms]

@general_utils.undo
def mirror_ctrls(ctrls):
    mirror_data = []

    for obj in ctrls:
        data = get_mirror_data(obj)
        mirror_data.append(data)

    for obj, transform in mirror_data:

        if 'space' in transform:
            obj.setAttr('Space', transform['space'])

        if 'pos' in transform:
            obj.setTranslation(transform['pos'])

        if 'rot' in transform:
            obj.setRotation(transform['rot'])




if __name__ == '__main__':
    mirror_ctrls(pymel.selected())
