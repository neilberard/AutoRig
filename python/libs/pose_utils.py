import pymel.core as pymel
from python.libs import virtual_classes, ikfk_switch, general_utils
reload(ikfk_switch)
reload(virtual_classes)
reload(general_utils)

@general_utils.undo
def reset_rig():
    for obj in pymel.listTransforms():
        if obj.hasAttr('Type') and obj.Type.get() == 'CTRL':
            try:
                obj.setRotation((0, 0, 0))
                obj.setTranslation((0, 0, 0))
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


def get_mirrored_obj(obj):
    """
    Assumes that each set of limbs has only two elememts, Right or Left.
    :param obj: Any object that has a network node attachment
    :return: mirrored object.
    """

    net_attr = obj.message.connections(type=virtual_classes.LimbNode, plugs=True)[0]  # Storing the network attr
    limb = obj.network.message.connections(plugs=True)[0]  # Storing the main limb attr

    for idx, element in enumerate(limb.array().elements()):
        if idx != limb.index():  # Traverse through the other limb network
            mirror_net = limb.array().elementByLogicalIndex(idx).connections()[0]
            mirror_array = mirror_net.getAttr(net_attr.array().attrName())
            return mirror_array[net_attr.index()]


def get_mirror_data(obj):
    """Returns mirrored obj with transforms{rot:'', pos:''} Note: Key 'Pos' not included with FK ctrls"""

    transforms = {}

    if obj.region == 'Spine' or obj.region == 'Head' or obj.region == 'Main':
        mirrored_obj = obj

    else:

        mirrored_obj = obj.getMirroredCtrl()
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

    return [mirrored_obj, transforms]

@general_utils.undo
def mirror_ctrls(ctrls):
    mirror_data = []

    for obj in ctrls:
        data = get_mirror_data(obj)
        mirror_data.append(data)

    for obj, transform in mirror_data:

        print transform['rot']

        if 'pos' in transform:
            obj.setTranslation(transform['pos'])

        if 'rot' in transform:
            obj.setRotation(transform['rot'])


if __name__ == '__main__':
    mirror_ctrls(pymel.selected())
