'''HSBuild_RIG'''
import pymel.core as pymel

from python.libs import build_ctrls
from python.libs import general_utils
from python.libs import joint_utils
from python.libs import naming_utils, virtual_classes, consts, pose_utils

reload(build_ctrls)
reload(joint_utils)
reload(naming_utils)
reload(general_utils)
reload(virtual_classes)
reload(consts)
reload(pose_utils)

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

@general_utils.undo
def delete_rig():

    for net in pymel.ls(type='network'):

        if net.main.jnts[0].getParent():
            net.main.jnts[0].setParent(None)

        try:
            pymel.delete(net.getCtrlRig())

        except Exception as ex:
            log.warning(ex)
            pass

    pymel.delete(pymel.ls(type='network'))

    for jnt in pymel.ls(type='joint'):
        attr_list = jnt.listAttr(userDefined=True, leaf=True)

        for attr in attr_list:
            attr.delete()
    try:
        pymel.delete(['L_Clavicle', 'L_Hip'])
    except:
        pass


def group_limb(net, name=None):
    log.info('Grouping: {}'.format(net))
    # LimbGRP
    if name:
        limb_grp_name = name
    else:
        limb_grp_name = naming_utils.concatenate([net.side, net.region, 'GRP'])
    limb_grp = pymel.group(empty=True, name=limb_grp_name)
    limb_grp.rotateOrder.set(net.jnts[0].rotateOrder.get())
    limb_grp.setMatrix(net.jnts[0].getMatrix(worldSpace=True), worldSpace=True)
    limb_grp = virtual_classes.attach_class(limb_grp, net)
    naming_utils.add_tags(limb_grp, {'Network': net.name(), 'Utility': 'LimbGrp'})

    # Group Ctrl Rig
    log.info('Grouping CTRLS')
    for node in net.getCtrlRig():
        root = joint_utils.get_root(node)
        if root and root != limb_grp and root != net.main.ROOT[0].get():  # Todo: Simplify this logic
            root.setParent(limb_grp)

    return limb_grp


def build_ikfk_limb(jnts, net, fk_size=2.0, fk_shape='Circle', ik_size=1.0, ik_shape='Cube01', pole_size=1.0, pole_shape='Cube01', ikfk_size=1.0, ikfk_shape='IKFK', region='', side=''):

    """
    :param jnts:
    :param net:
    :param fk_size:
    :param fk_shape:
    :param ik_size:
    :param ik_shape:
    :param pole_size:
    :param pole_shape:
    :param ikfk_size:
    :param ikfk_shape:
    :param region:
    :param side:
    :return:
    """

    #NET NODE
    if not net:
        net = virtual_classes.LimbNode()
        naming_utils.add_tags(net, tags={'Region': region, 'Side': side})
        naming_utils.add_message_attr(net, attributes=['JOINTS',
                                                       'IK_JOINTS',
                                                       'FK_JOINTS',
                                                       'IK_CTRL',
                                                       'FK_CTRL',
                                                       'POLE',
                                                       'ANNO',
                                                       'IK_HANDLE',
                                                       'SWITCH',
                                                       'ORIENTCONSTRAINT',
                                                       'POINTCONSTRAINT'])

    assert isinstance(net, virtual_classes.LimbNode)

    jnts = joint_utils.get_joint_chain(jnts)

    # Attach virtual class
    for idx, jnt in enumerate(jnts):
        try:
            jnts[idx] = virtual_classes.attach_class(jnt, net=net)
            jnt.message.connect(net.jntsAttr[idx])
            jnts[idx].add_network_tag()

        except Exception as ex:
            log.warning(ex)

    # IK FK
    fk_jnts, ik_jnts = joint_utils.build_ik_fk_joints(jnts, net)

    log.info('Building IK FK:')

    # FK CTRLS
    increment = fk_size/len(fk_jnts)

    for idx, fk_jnt in enumerate(fk_jnts):

        size = fk_size - (increment * idx) + (fk_size/2)

        ctrl_name = naming_utils.concatenate([net.Side.get(),
                                              net.jnts[idx].name_info.base_name,
                                              net.jnts[idx].name_info.joint_name,
                                              net.jnts[idx].name_info.index,
                                              'FK',
                                              'CTRL'])
        ctrl_tags = {'Utility': 'FK', 'Axis': 'XY'}  # todo: add support for alternate mirror axis
        if idx <= 3:
            ctrl = build_ctrls.create_ctrl(jnt=fk_jnt, name=ctrl_name, network=net, attr=net.FK_CTRLS, tags=ctrl_tags, size=size, shape=fk_shape, axis='X')

    for idx, fk in enumerate(net.fk_ctrls):
        if idx > 0:
            fk.setParent(net.fk_ctrls[idx-1])

    for fk, jnt in zip(net.fk_ctrls, net.fk_jnts):
        parent_constraint = pymel.parentConstraint(fk, jnt)
        naming_utils.add_tags(parent_constraint, tags={'Network': net.name()})

    # Create offsets
    joint_utils.create_offset_groups([x for x in net.fk_ctrls], net)

    # IK Handle
    ikhandle_name = naming_utils.concatenate([net.jnts[2].name_info.side,
                                              net.jnts[2].name_info.base_name,
                                              net.jnts[2].name_info.joint_name,
                                              net.jnts[2].name_info.index, 'IK', 'HDL'])
    ikhandle = pymel.ikHandle(startJoint=net.ik_jnts[0], endEffector=net.ik_jnts[2], name=ikhandle_name)[0]
    naming_utils.add_tags(ikhandle, {'Network': net.name(), 'Utility': 'IK'})
    ikhandle.message.connect(net.ikHandlesAttr[0])
    log.info('Building IK CTRLS: {}, {}'.format(ikhandle_name, type(ikhandle)))
    ik_handle_offset = joint_utils.create_offset_groups(ikhandle, net)

    # Ik Ctrl
    ik_ctrl_name = naming_utils.concatenate([net.Side.get(),
                                             jnts[2].name_info.base_name,
                                             jnts[2].name_info.joint_name,
                                             'IK',
                                             'CTRL'])
    ikctrl = build_ctrls.create_ctrl(name=ik_ctrl_name, network=net, attr=net.IK_CTRLS, shape=ik_shape, size=ik_size, tags={'Utility': 'IK'}, axis='Y')
    ikctrl.rotateOrder.set(net.jnts[2].rotateOrder.get())
    ikctrl.rotate.set((0, 0, 0))
    ikctrl.setTranslation(net.jnts[2].getTranslation(worldSpace=True), worldSpace=True)
    orient_constraint = pymel.orientConstraint(ikctrl, ik_handle_offset, maintainOffset=True)
    naming_utils.add_tags(orient_constraint, {'Network': net.name(), 'Utility': 'IK'})
    pymel.pointConstraint(ikctrl, ik_handle_offset)
    joint_utils.create_offset_groups(ikctrl, net)

    # POLE Ctrl
    pos, rot = joint_utils.get_pole_position(fk_jnts)
    pole_name = naming_utils.concatenate([net.jnts[2].name_info.base_name,
                                          net.jnts[2].name_info.joint_name,
                                          net.jnts[2].name_info.side,
                                          'Pole',
                                          'CTRL'])
    pole = build_ctrls.create_ctrl(name=pole_name, network=net, shape=pole_shape, size=pole_size, tags={'Utility': 'IK'})
    pole.setTranslation(pos, space='world')
    pole.message.connect(net.POLE[0])
    joint_utils.create_offset_groups(pole, name='Offset', net=net)
    pymel.poleVectorConstraint(pole, ikhandle)

    # Annotation. Line between pole and mid ik_jnts joint
    anno_name = naming_utils.concatenate([net.jnts[1].name_info.base_name, net.jnts[1].name_info.joint_name])
    annotation, anno_parent, locator, point_constraint_a, point_constraint_b = general_utils.build_annotation(pole, net.ik_jnts[1], tags={'Network': net.name(), 'Region': net.Region.get(), 'Side': net.Side.get(), 'Utility': 'IK'}, net=net, name=anno_name)
    for grp in [annotation, anno_parent, locator, point_constraint_a]:
        naming_utils.add_tags(grp, tags={'Network': net.name()})

    # Switch CTRL
    switch_name = naming_utils.concatenate([net.jnts[2].name_info.base_name, net.jnts[2].name_info.joint_name, 'IKFK', 'CTRL'])
    switch_tags = {'Type': 'Switch', 'Utility': 'IKFK'}
    switch = build_ctrls.create_ctrl(jnt=net.jnts[2], name=switch_name, network=net, attr=net.SWITCH, tags=switch_tags, shape=ikfk_shape, size=ikfk_size, axis='X')
    switch_offset = joint_utils.create_offset_groups(switch)
    pymel.parentConstraint([jnts[2], switch_offset])

    # plusMinusAverage
    switch_util = general_utils.make_switch_utility(switch, tags={'Network': net.name(), 'Type': 'Switch', 'Utility': 'IKFK'})
    for orient, point in zip(net.ORIENTCONSTRAINT.listConnections(), net.POINTCONSTRAINT.listConnections()):
        switch_util.output1D.connect(point.w0)
        switch_util.output1D.connect(orient.w0)
    for orient, point in zip(net.ORIENTCONSTRAINT.listConnections(), net.POINTCONSTRAINT.listConnections()):
        switch.IKFK.connect(point.w1)
        switch.IKFK.connect(orient.w1)

    # IK Snap Loc
    ik_loc_name = naming_utils.concatenate([net.jnts[2].name_info.base_name, net.jnts[2].name_info.joint_name, 'Snap', 'LOC'])
    ik_loc = pymel.spaceLocator(name=ik_loc_name)
    ik_loc.message.connect(net.IK_SNAP_LOC[0])
    naming_utils.add_tags(ik_loc, {'Network': net.name(), 'Utility': 'IK'})

    ik_loc.rotateOrder.set(net.jnts[2].rotateOrder.get())
    ik_loc.rotate.set((0, 0, 0))
    pymel.pointConstraint([net.jnts[2], ik_loc])
    orient_constraint = pymel.orientConstraint([net.jnts[2], ik_loc], maintainOffset=True)
    naming_utils.add_tags(orient_constraint, {'Network': net.name()})

    # FK Vis Condition
    fk_vis_condition = general_utils.make_condition(secondTerm=1.0, net=net, name=naming_utils.concatenate([net.name(), 'VisCon', 'FK']))
    switch_util.output1D.connect(fk_vis_condition.firstTerm)

    # IK Vis Condition
    ik_vis_condition = general_utils.make_condition(secondTerm=1.0, net=net, name=naming_utils.concatenate([net.name(), 'VisCon', 'IK']))
    switch.IKFK.connect(ik_vis_condition.firstTerm)

    # Connect Visibility
    for obj in net.getCtrlRig():
        if obj.hasAttr('Utility') and obj.Utility.get() == 'IK':
            ik_vis_condition.outColorR.connect(obj.visibility)

        if obj.hasAttr('Utility') and obj.Utility.get() == 'FK':
            fk_vis_condition.outColorR.connect(obj.visibility)


def build_spine(jnts, net, fk_size=2.0):
    assert isinstance(net, virtual_classes.SplineIKNet)

    info = naming_utils.ItemInfo(jnts[0])
    new_name = naming_utils.concatenate([info.side,
                                         info.base_name,
                                         info.joint_name,
                                         info.index,
                                         ])

    for idx, jnt in enumerate(jnts):
        virtual_classes.attach_class(jnt, net)

    points = [x.getTranslation(worldSpace=True) for x in jnts]
    spine_curve = pymel.curve(p=points, degree=1)
    naming_utils.add_tags(spine_curve, {'Network': net.name()})

    # Ik handle
    ikhandle, effector = pymel.ikHandle(startJoint=jnts[0],
                                        endEffector=jnts[-1],
                                        solver='ikSplineSolver',
                                        createCurve=False,
                                        curve=spine_curve,
                                        rootOnCurve=True,
                                        parentCurve=False,
                                        rootTwistMode=False)
    naming_utils.add_tags(ikhandle, {'Network': net.name()})
    naming_utils.add_tags(effector, {'Network': net.name()})

    for i in spine_curve.cv.indices():
        cluster, cluster_handle = pymel.cluster(spine_curve.cv[i])
        cluster_handle.message.connect(net.CLUSTER_HANDLE[i])
        virtual_classes.attach_class(cluster_handle, net=net)
        naming_utils.add_tags(cluster_handle, {'Network': net.name()})
        naming_utils.add_tags(cluster, {'Network': net.name()})
        offset = joint_utils.create_offset_groups(cluster_handle)[0]
        offset.setPivots(cluster_handle.getRotatePivot())
        naming_utils.add_tags(offset, {'Network': net.name()})

    naming_utils.add_tags(ikhandle, {'Network': net.name()})
    ikhandle.message.connect(net.IK_HANDLE[0])

    def make_ctrl(jnt, children=None, shape='Cube01', size=1.0):
        """

        :param jnt:
        :param children: list of clusters to parent to ctrl
        :param shape:
        :return:
        """
        name = naming_utils.concatenate([jnt.name_info.joint_name,
                                         jnt.name_info.index,
                                         'CTRL'])
        ctrl = build_ctrls.create_ctrl(name=name, shape=shape, network=net, attr=net.IK_CTRLS, offset=False, size=size)
        ctrl.setTranslation(jnt.getTranslation(worldSpace=True))

        for cluster in children:
            cluster.getRoot().setParent(ctrl)
        return ctrl

    # Pelvis CTRL
    pelvis_ctrl = make_ctrl(net.jnts[1], children=net.clusters[0:2], shape='Spine01', size=1.0)
    # Mid CTRL
    mid_ctrl = make_ctrl(net.jnts[2], children=net.clusters[2:3], shape='Spine01', size=1.0)
    # Chest CTRL
    chest_ctrl = make_ctrl(net.jnts[3], children=net.clusters[3:5], shape='Chest', size=1.0)
    # COG
    cog = build_ctrls.create_ctrl(network=net, attr=net.COG, shape='Circle', size=5, name='COG', offset=False, axis='Y')
    cog.setTranslation(net.jnts[1].getTranslation(worldSpace=True))

    chest_ctrl.setParent(mid_ctrl)
    mid_ctrl.setParent(cog)
    pelvis_ctrl.setParent(cog)

    # Offsets
    joint_utils.create_offset_groups([chest_ctrl, mid_ctrl, pelvis_ctrl, cog], net=net)

    # Ik Spline Twist
    net.ik_handles[0].dTwistControlEnable.set(1)
    net.ik_handles[0].dWorldUpType.set(4)
    net.ik_handles[0].dForwardAxis.set(0)

    net.ik_ctrls[0].worldMatrix[0].connect(net.ik_handles[0].dWorldUpMatrix)
    net.ik_ctrls[2].worldMatrix[0].connect(net.ik_handles[0].dWorldUpMatrixEnd)

    net.ik_handles[0].dWorldUpAxis.set(3)

    net.ik_handles[0].dWorldUpVector.set(0, 0, 1)
    net.ik_handles[0].dWorldUpVectorEnd.set(0, 0, 1)


    # Prevent double transforms on the spine curve
    curve_offset_a = joint_utils.create_offset_groups(spine_curve, net=net)
    curve_offset_b = joint_utils.create_offset_groups(curve_offset_a, net=net)
    curve_offset_a[0].inheritsTransform.set(False)


def build_reverse_foot_rig(net):

    assert isinstance(net, virtual_classes.LimbNode)
    #Set attrs
    foot_ik_ctrl = net.ik_ctrls[0]
    foot_ik_ctrl.addAttr('Ankle_Roll', at='float', keyable=True)
    foot_ik_ctrl.addAttr('Ball_Roll', at='float', keyable=True)
    foot_ik_ctrl.addAttr('Ball_Twist', at='float', keyable=True)
    foot_ik_ctrl.addAttr('Toe_Roll', at='float', keyable=True)
    foot_ik_ctrl.addAttr('Toe_Twist', at='float', keyable=True)
    foot_ik_ctrl.addAttr('Toe_Wiggle', at='float', keyable=True)
    foot_ik_ctrl.addAttr('Left_Bank', at='float', keyable=True)
    foot_ik_ctrl.addAttr('Right_Bank', at='float', keyable=True)

    # Build Foot IK Handles
    ikhandle_name = naming_utils.concatenate([net.jnts[3].name_info.side,
                                              net.jnts[3].name_info.base_name,
                                              net.jnts[3].name_info.joint_name,
                                              net.jnts[3].name_info.index, 'IK', 'HDL'])
    ikhandle_a = pymel.ikHandle(startJoint=net.ik_jnts[2], endEffector=net.ik_jnts[3], name=ikhandle_name)[0]
    ikhandle_a.message.connect(net.IK_HANDLE[1])
    ikhandle_name = naming_utils.concatenate([net.jnts[4].name_info.side,
                                              net.jnts[4].name_info.base_name,
                                              net.jnts[4].name_info.joint_name,
                                              net.jnts[4].name_info.index, 'IK', 'HDL'])
    ikhandle_b = pymel.ikHandle(startJoint=net.ik_jnts[3], endEffector=net.ik_jnts[4], name=ikhandle_name)[0]
    ikhandle_b.message.connect(net.IK_HANDLE[2])

    # Storing Ankle IK Handle parent for later.
    ankle_ik_grp = net.ik_handles[0].getParent()

    def build_grp(transform=None, children=None, name=None, net=None):
        grp_name = naming_utils.concatenate([net.side, net.region, name, 'GRP'])
        grp = pymel.group(empty=True, name=grp_name)
        grp.rotateOrder.set(transform.rotateOrder.get())
        grp.setMatrix(transform.getMatrix(worldSpace=True), worldSpace=True)
        pymel.makeIdentity(grp, apply=True)
        for child in children:
            child.setParent(grp)
        virtual_classes.attach_class(grp, net=net)
        return grp

    # Ball Roll
    ball_roll_grp = build_grp(name='BallRoll', transform=net.jnts[3], children=[net.ik_handles[0], net.ik_handles[1]], net=net)
    foot_ik_ctrl.Ball_Roll.connect(ball_roll_grp.rotateX)

    # Toe Wiggle
    toe_wiggle_grp = build_grp(name='ToeWiggle', transform=net.jnts[3], children=[net.ik_handles[2]], net=net)
    foot_ik_ctrl.Toe_Wiggle.connect(toe_wiggle_grp.rotateX)

    # Toe Pivot
    toe_roll_grp = build_grp(name='ToeRoll', transform=net.jnts[4], children=[ball_roll_grp, toe_wiggle_grp], net=net)
    foot_ik_ctrl.Toe_Roll.connect(toe_roll_grp.rotateX)
    foot_ik_ctrl.Toe_Twist.connect(toe_roll_grp.rotateY)

    # Ball Twist
    ball_twist_grp = build_grp(name='BallTwist', transform=net.jnts[3], children=[toe_roll_grp], net=net)
    foot_ik_ctrl.Ball_Twist.connect(ball_twist_grp.rotateY)

    # Left Bank
    left_bank_grp = build_grp(name='LeftBank', transform=net.jnts[3], children=[ball_twist_grp], net=net)
    foot_ik_ctrl.Left_Bank.connect(left_bank_grp.rotateZ)

    # Right Bank
    right_bank_grp = build_grp(name='RightBank', transform=net.jnts[3], children=[left_bank_grp], net=net)
    foot_ik_ctrl.Right_Bank.connect(right_bank_grp.rotateZ)

    # Ankle Roll
    ankle_roll_grp = build_grp(name='AnkleRoll', transform=net.jnts[2], children=[right_bank_grp], net=net)
    foot_ik_ctrl.Ankle_Roll.connect(ankle_roll_grp.rotateX)

    pymel.parent(ankle_roll_grp, ankle_ik_grp)


def build_clavicle(jnts, net):

    if net.side == 'L':
        ctrl = build_ctrls.create_ctrl(jnt=jnts[0], network=net, attr=net.FK_CTRLS, shape='Clavicle', mirrored=True, axis='Z')
    else:
        ctrl = build_ctrls.create_ctrl(jnt=jnts[0], network=net, attr=net.FK_CTRLS, shape='Clavicle', axis='-X')  # todo: '-X' is really unintuitive, look into this further.

    offset = joint_utils.create_offset_groups(ctrl, net=net)
    naming_utils.add_tags(ctrl, {'Utility': 'FK', 'Axis': 'XY'})
    pymel.parentConstraint([ctrl, jnts[0]])


def build_head(jnts, net):

    head_ctrl = None
    neck_ctrl = None

    for jnt in jnts:
        info = naming_utils.ItemInfo(jnt)

        if info.joint_name == 'Head':
            head_ctrl = build_ctrls.create_ctrl(jnt, shape='Head01', size=1, attr=net.FK_CTRLS, network=net)
            pymel.parentConstraint([head_ctrl, jnt])

        elif info.joint_name == 'Neck':
            neck_ctrl = build_ctrls.create_ctrl(jnt, name=naming_utils.concatenate([info.joint_name, 'CTRL']), size=2.0, attr=net.FK_CTRLS, network=net, shape='Neck01')
            pymel.parentConstraint([neck_ctrl, jnt])

    head_ctrl.setParent(neck_ctrl)

    joint_utils.create_offset_groups(head_ctrl, net=net)
    joint_utils.create_offset_groups(neck_ctrl, net=net)


def build_hand(jnts, net, ctrl_size=0.6):

    ctrls = []

    for jnt in jnts:
        name = naming_utils.concatenate([jnt.side, jnt.base_name, jnt.joint_name, jnt.info_index, 'CTRL'])

        parent = jnt.getParent()

        parent_name = naming_utils.concatenate([parent.side, parent.base_name, parent.joint_name, parent.info_index, 'CTRL'])

        ctrl = build_ctrls.create_ctrl(jnt=jnt, network=net, size=ctrl_size, name=name, attr=net.FK_CTRLS, axis='X')
        ctrls.append(ctrl)
        pymel.parentConstraint([ctrl, jnt])

        if pymel.objExists(parent_name):
            parent_ctrl = pymel.PyNode(parent_name)

            ctrl.setParent(parent_ctrl)

    for ctrl in ctrls:
        joint_utils.create_offset_groups(ctrl)


def build_main(net, ctrl_size=15):
    main_name = 'Main_CTRL'
    root_name = 'Root_CTRL'
    world_name = 'World_CTRL'
    main_ctrl = build_ctrls.create_ctrl(name=main_name, shape='Arrows02', attr=net.MAIN_CTRL, size=ctrl_size, network=net)
    world_ctrl = build_ctrls.create_ctrl(name=world_name, attr=net.MAIN_CTRL, size=12, network=net)
    root_ctrl = build_ctrls.create_ctrl(name=root_name, shape='WorldPos01', attr=net.MAIN_CTRL, size=8, network=net)
    root_ctrl.setParent(world_ctrl)
    main_ctrl.setParent(world_ctrl)


def build_space_switching(main_net):
    """Connect Limbs with space switching"""

    def make_space_grp(ctrl, orient=False, point=True, name='Space', parent=True):
        log.info('Building Space Group {}'.format(ctrl))

        space_grp = virtual_classes.TransformNode(name=naming_utils.concatenate([ctrl.name(), name]))
        naming_utils.add_tags(space_grp, {'Network': ctrl.network.name()})
        space_grp.setTranslation(ctrl.getTranslation(worldSpace=True), worldSpace=True)
        if point:
            pymel.pointConstraint([ctrl, space_grp], maintainOffset=False)
        if orient:
            pymel.orientConstraint([ctrl, space_grp], maintainOffset=True)
        if parent:
            space_grp.setParent(space_grp.limb_grp)

        return space_grp

    def make_space_switch(ctrl, enums=None, targets=None, name='SpaceSwitch', con_type='orient'):
        """Makes a group that is constrained to multiple targets"""

        if not enums:
            enums = ':'.join([x.name() for x in targets])

        ctrl.addAttr('Space', attributeType='enum', enumName=enums, keyable=True)

        info = naming_utils.ItemInfo(ctrl.name())

        space_switch_grp = pymel.group(empty=True, name=naming_utils.concatenate([ctrl.name(), name]))
        naming_utils.add_tags(space_switch_grp, {'Network': ctrl.network.name()})

        if con_type == 'orient':
            space_con = pymel.orientConstraint(targets + [space_switch_grp])
            offset_con = pymel.orientConstraint([space_switch_grp, ctrl.getParent()], maintainOffset=True)

        elif con_type == 'parent':
            space_con = pymel.parentConstraint(targets + [space_switch_grp], maintainOffset=True)
            offset_con = pymel.parentConstraint([space_switch_grp, ctrl.getParent()], maintainOffset=True)
        else:
            return

        for idx, obj in enumerate(targets):
            space_condition = general_utils.make_condition(secondTerm=idx, net=main_net, name=naming_utils.concatenate([info.base_name, info.joint_name, info.index, name, 'CON']))
            naming_utils.add_tags(space_condition, {'Network': ctrl.network.name()})
            ctrl.Space.connect(space_condition.firstTerm)
            attr = '{}{}{}'.format(space_con, '.w', idx)
            space_condition.outColorR.connect(attr)

        space_switch_grp.setParent(ctrl.limb_grp)
        return space_switch_grp

    chest_ctrl_space = make_space_grp(main_net.spine[0].ik_ctrls[-1], orient=True)
    pelvis_ctrl_space = make_space_grp(main_net.spine[0].ik_ctrls[0], orient=True)
    neck_ctrl_space = make_space_grp(main_net.head[0].fk_ctrls[0], orient=True)
    head_ctrl_space = make_space_grp(main_net.head[0].fk_ctrls[1], orient=True)
    main_ctrl_space = make_space_grp(main_net.main_ctrl[0], orient=True)
    main_ctrl_space.setParent(main_net.main_ctrl[0])

    # Neck Space Switch
    make_space_switch(main_net.head[0].fk_ctrls[0], targets=[chest_ctrl_space, main_ctrl_space])
    # Head Space Switch
    head_space_switch = make_space_switch(main_net.head[0].fk_ctrls[1], targets=[neck_ctrl_space, main_ctrl_space])

    # Parent Constraint Head Limb to Torso
    pymel.parentConstraint([main_net.spine[0].ik_ctrls[-1], main_net.head[0].fk_ctrls[0].getParent()], maintainOffset=True, skipRotate=('x', 'y', 'z'))

    # Space Switch for Arms and Legs and Hands
    for index, clavicle in enumerate(main_net.clavicles):
        log.info('# Space Switch for Arms and Legs and Hands')

        clavicle_ctrl_space = make_space_grp(clavicle.fk_ctrls[0], orient=True)
        foot_ctrl_space = make_space_grp(main_net.legs[index].ik_ctrls[0], orient=True)

        # FK ARM Switch
        make_space_switch(main_net.arms[index].fk_ctrls[0], targets=[clavicle_ctrl_space, main_ctrl_space, head_ctrl_space, pelvis_ctrl_space])
        # Clavicle Switch
        make_space_switch(clavicle.fk_ctrls[0], targets=[chest_ctrl_space, main_ctrl_space, head_ctrl_space, pelvis_ctrl_space])
        # IK Arm Switch
        make_space_switch(main_net.arms[index].ik_ctrls[0], targets=[main_ctrl_space, clavicle_ctrl_space, head_ctrl_space, pelvis_ctrl_space], con_type='parent')
        # Arm Pole Switch
        make_space_switch(main_net.arms[index].pole_ctrls[0], targets=[main_ctrl_space, clavicle_ctrl_space, head_ctrl_space, pelvis_ctrl_space], con_type='parent')
        # FK Leg Switch
        make_space_switch(main_net.legs[index].fk_ctrls[0], targets=[main_ctrl_space, pelvis_ctrl_space])
        # IK Leg Switch
        make_space_switch(main_net.legs[index].ik_ctrls[0], targets=[main_ctrl_space, pelvis_ctrl_space], con_type='parent')
        # IK Leg Pole Switch
        make_space_switch(main_net.legs[index].pole_ctrls[0], targets=[main_ctrl_space, pelvis_ctrl_space, foot_ctrl_space], con_type='parent')

        # FK ARM Parent Constraint
        pymel.parentConstraint([clavicle.fk_ctrls[0], main_net.arms[index].fk_ctrls[0].getParent()], maintainOffset=True, skipRotate=('x', 'y', 'z'))
        # IK ARM Parent Constraint
        pymel.parentConstraint([clavicle.fk_ctrls[0], main_net.arms[index].ik_jnts[0]], maintainOffset=True, skipRotate=('x', 'y', 'z'))
        # Clavicle Parent Constraint
        pymel.parentConstraint([main_net.spine[0].ik_ctrls[-1], clavicle.fk_ctrls[0].getParent()], maintainOffset=True, skipRotate=('x', 'y', 'z'))

        # FK Leg Parent Constraint
        pymel.parentConstraint([main_net.spine[0].ik_ctrls[0], main_net.legs[index].fk_ctrls[0].getParent()], maintainOffset=True, skipRotate=('x', 'y', 'z'))
        # Ik Leg Parent Constraint
        pymel.parentConstraint([main_net.spine[0].ik_ctrls[0], main_net.legs[index].ik_jnts[0]], maintainOffset=True, skipRotate=('x', 'y', 'z'))

        # Parent Constraint Hands
        pymel.parentConstraint([main_net.arms[index].jnts[-1], main_net.hands[index].limb_grp], maintainOffset=True)


def build_lower_limb_roll_jnts(main_net, roll_jnt_count=3, up_axis='+Z'):
    """
    This method is driven by the rotation the end jnt such as wrist using an aim constraint.
    :param main_net:
    :param roll_jnt_count:
    :param up_axis:
    :return:
    """

    increment = 1.0/float(roll_jnt_count)

    def create_driver_rig(jnt_a, jnt_b, net, up_axis=None):

        info = naming_utils.ItemInfo(jnt_a)

        # Driver Group
        grp_name = naming_utils.concatenate([info.side, info.base_name, info.joint_name, 'Roll', 'GRP'])
        grp = virtual_classes.TransformNode(name=grp_name)
        naming_utils.add_tags(grp, {'Network': net.name()})
        pymel.parentConstraint([jnt_a, grp])
        grp.setParent(grp.limb_grp)

        # Driver A
        new_name = naming_utils.concatenate([info.side, info.base_name, info.joint_name, 'Driver', 'A'])
        driver_a = pymel.duplicate(jnt_a, name=new_name)[0]
        pymel.delete(driver_a.getChildren())
        driver_a.setTranslation(jnt_b.getTranslation(worldSpace=True), worldSpace=True)
        driver_a.setParent(grp)

        # UP Axis Locator
        new_name = naming_utils.concatenate([info.side, info.base_name, info.joint_name, 'World', 'Up'])
        up_loc = pymel.spaceLocator(name=new_name)
        naming_utils.add_tags(up_loc, {'Network': net.name()})
        up_loc.setTranslation(driver_a.getTranslation(worldSpace=True), worldSpace=True)
        up_loc.setRotation(driver_a.getRotation(worldSpace=True), worldSpace=True)

        # Connect locator
        up_loc.setParent(grp)

        # Place the up locator to up axis offset.
        attr = pymel.PyNode('{}.translate{}'.format(up_loc.name(), up_axis[-1]))
        value = float('{}{}'.format(up_axis[0], 10))
        attr.set(attr.get() + value)

        pymel.parentConstraint([jnt_b, up_loc], maintainOffset=True)
        aim_vector = joint_utils.get_aim_vector(jnt_b)

        # Aim Constriant
        pymel.aimConstraint([jnt_a, driver_a], aimVector=(aim_vector), upVector=(0, 0, 1), worldUpObject=up_loc, worldUpType='Object')

        return driver_a

    def create_joints(jnt_a, jnt_b, net):
        """
        :param jnt_a: Start Joint
        :param jnt_b: End Joint
        :param net: Limb Network node
        :param lower_limb: This uses an aim constraint method for end driven rotation, the default uses a ikSc Solver
        for upper arm and upper leg rotation that is driven by the parent jnt.
        :param up_axis: For placement of the up locator, must be specified as positive or negative. '+Z', '-X', '+Y'
        :return:
        """

        driver_a = create_driver_rig(jnt_a, jnt_b, net, up_axis=up_axis)

        info = naming_utils.ItemInfo(jnt_a)

        # Create Roll Joint
        for roll_idx in range(roll_jnt_count):

            weight_b = (increment * roll_idx) + increment
            weight_a = 1 - weight_b

            name = naming_utils.concatenate([info.side, info.base_name, info.joint_name, 'Roll', consts.INDEX[roll_idx]])
            type = naming_utils.concatenate([info.base_name, info.joint_name, 'Roll', consts.INDEX[roll_idx]])
            dup_jnt = pymel.duplicate(jnt_a, name=name)[0]
            dup_jnt.radius.set(8)
            dup_jnt.setAttr('otherType', type)

            naming_utils.add_tags(dup_jnt, {'_skin': 'True'})
            pymel.delete(dup_jnt.getChildren())
            # Parent Roll joint to Jnt A
            dup_jnt.setParent(jnt_a)
            naming_utils.add_tags(dup_jnt, {'Network': net.name(), 'Utility': 'Roll'})
            point_con = pymel.pointConstraint([jnt_a, jnt_b, dup_jnt])

            # Point Constraint weight
            point_con.w0.set(weight_a)
            point_con.w1.set(weight_b)

            # Multiply/Divide Node
            name = naming_utils.concatenate([info.side, info.base_name, info.joint_name, 'Multi', consts.INDEX[roll_idx]])
            multi_utility = pymel.shadingNode('multiplyDivide', name=name, asUtility=True)
            naming_utils.add_tags(multi_utility, {'Network': net.name(), 'Utility': 'Roll'})

            # Using Driver A for the Wrist and Ankle
            driver_a.rotateX.connect(multi_utility.input1X)
            multi_utility.input2X.set(weight_b)
            multi_utility.outputX.connect(dup_jnt.rotateX)

    # idx[0] LEFT Side, idx[1] Right Side
    for idx in range(2):

        # Add ForeArm
        create_joints(main_net.arms[idx].jnts[1], main_net.arms[idx].jnts[2], main_net.arms[idx])

        # Add Ankle
        create_joints(main_net.legs[idx].jnts[1], main_net.legs[idx].jnts[2], main_net.legs[idx])


def build_upper_limb_roll_jnts(main_net, roll_jnt_count=3):
    """Add roll jnts, count must be at least 1"""

    increment = 1.0/float(roll_jnt_count)

    def create_joints(jnt_a, jnt_b, net, lower_limb=False, up_axis='-Z'):
        """
        :param jnt_a: Start Joint
        :param jnt_b: End Joint
        :param net: Limb Network node
        :param lower_limb: This uses an aim constraint method for end driven rotation, the default uses a ikSc Solver
        for upper arm and upper leg rotation that is driven by the parent jnt.
        :param up_axis: For placement of the up locator, must be specified as positive or negative. '+Z', '-X', '+Y'
        :return:
        """

        driver_a, driver_b = create_driver_rig(jnt_a, jnt_b, net, reverse=lower_limb, up_axis=up_axis)

        info = naming_utils.ItemInfo(jnt_a)

        # Create Roll Joint
        for roll_idx in range(roll_jnt_count):

            weight_b = increment * roll_idx
            weight_a = 1 - weight_b

            name = naming_utils.concatenate([info.side, info.base_name, info.joint_name, 'Roll', consts.INDEX[roll_idx]])
            type = naming_utils.concatenate([info.base_name, info.joint_name, 'Roll', consts.INDEX[roll_idx]])

            dup_jnt = pymel.duplicate(jnt_a, name=name)[0]
            dup_jnt.radius.set(8)
            dup_jnt.setAttr('otherType', type)

            naming_utils.add_tags(dup_jnt, {'_skin': 'True'})
            pymel.delete(dup_jnt.getChildren())
            # Parent Roll joint to Jnt A
            dup_jnt.setParent(jnt_a)

            naming_utils.add_tags(dup_jnt, {'Network': net.name(), 'Utility': 'Roll'})
            point_con = pymel.pointConstraint([jnt_a, jnt_b, dup_jnt])

            # Weighting toward child
            point_con.w0.set(weight_a)
            point_con.w1.set(weight_b)

            # Multi Node
            name = naming_utils.concatenate([info.side, info.base_name, info.joint_name, 'Multi', consts.INDEX[roll_idx]])
            multi_utility = pymel.shadingNode('multiplyDivide', name=name, asUtility=True)
            naming_utils.add_tags(multi_utility, {'Network': net.name(), 'Utility': 'Roll'})

            # Using jnt_a for Shoulder and Upper Leg
            driver_a.rotateX.connect(multi_utility.input1X)
            multi_utility.input2X.set(weight_a)
            multi_utility.outputX.connect(dup_jnt.rotateX)

    def create_driver_rig(jnt_a, jnt_b, net, reverse=False, up_axis=None):

        info = naming_utils.ItemInfo(jnt_a)

        # Driver Group
        grp_name = naming_utils.concatenate([info.side, info.base_name, info.joint_name, 'Roll', 'GRP'])
        grp = virtual_classes.TransformNode(name=grp_name)
        naming_utils.add_tags(grp, {'Network': net.name()})
        pymel.parentConstraint([jnt_a, grp])
        grp.setParent(grp.limb_grp)

        # Driver A
        new_name = naming_utils.concatenate([info.side, info.base_name, info.joint_name, 'Driver', 'A'])
        driver_a = pymel.duplicate(jnt_a, name=new_name)[0]
        pymel.delete(driver_a.getChildren())
        driver_a.setTranslation(jnt_b.getTranslation(worldSpace=True), worldSpace=True)
        driver_a.setParent(grp)

        # Driver B
        new_name = naming_utils.concatenate([info.side, info.base_name, info.joint_name, 'Driver', 'B'])
        driver_b = pymel.duplicate(jnt_a, name=new_name)[0]
        pymel.delete(driver_b.getChildren())
        driver_b.setParent(driver_a)

        ikhandle_name = naming_utils.concatenate([info.side, info.base_name, info.joint_name, 'Roll', 'IK'])
        ikhandle = pymel.ikHandle(startJoint=driver_a, endEffector=driver_b, name=ikhandle_name, solver='ikSCsolver')[0]
        ikhandle.setParent(grp)
        pymel.parentConstraint([jnt_a.getParent(), ikhandle], maintainOffset=True)


        return driver_a, driver_b

    # Add Upper Arm Roll
    # idx[0] LEFT Side, idx[1] Right Side
    for idx in range(2):
        # UpperArm
        create_joints(main_net.arms[idx].jnts[0], main_net.arms[idx].jnts[1], main_net.arms[idx])

        # UpperLeg
        create_joints(main_net.legs[idx].jnts[0], main_net.legs[idx].jnts[1], main_net.legs[idx])


def set_ctrl_colors(main_net, ctrls):

    for ctrl in ctrls:

        shapes = ctrl.getShapes()

        for shape in shapes:
            if ctrl.side == 'L':
                shape.overrideRGBColors.set(1)
                shape.overrideEnabled.set(1)
                shape.overrideColorRGB.set((1.0, 0.0, 0.0))

            if ctrl.side == 'R':
                shape.overrideRGBColors.set(1)
                shape.overrideEnabled.set(1)
                shape.overrideColorRGB.set((0.0, 0.0, 1.0))

            if ctrl.side == 'Center':
                shape.overrideRGBColors.set(1)
                shape.overrideEnabled.set(1)
                shape.overrideColorRGB.set((1.0, 1.0, 0.0))


def lock_ctrls(main_net, ctrls):

    # Lock Scale
    for ctrl in ctrls:
        ctrl.setAttr('scaleX', lock=True, keyable=False, channelBox=False)
        ctrl.setAttr('scaleY', lock=True, keyable=False, channelBox=False)
        ctrl.setAttr('scaleZ', lock=True, keyable=False, channelBox=False)

        # FK CTRLS Lock Translate
        if ctrl.utility == 'FK':
            ctrl.setAttr('translateX', lock=True, keyable=False, channelBox=False)
            ctrl.setAttr('translateY', lock=True, keyable=False, channelBox=False)
            ctrl.setAttr('translateZ', lock=True, keyable=False, channelBox=False)


        pass

def build_humanoid_rig(progress_bar, mirror=True):
    """
    This function requires all joints in the scene to belong to a single hierarchy.
    :param progress_bar:
    :param mirror:
    :return:
    """

    clav = pymel.PyNode('R_Clavicle')
    pymel.mirrorJoint(clav, mirrorYZ=True, mirrorBehavior=True, searchReplace=("R_", "L_"))
    hip = pymel.PyNode('R_Hip')
    pymel.mirrorJoint(hip, mirrorYZ=True, mirrorBehavior=True, searchReplace=("R_", "L_"))

    networks = []
    jnt_dict = {}
    jnts = pymel.ls(type='joint')
    root = joint_utils.get_root(jnts[0])

    for jnt in jnts:
        info = naming_utils.ItemInfo(jnt)
        key = naming_utils.concatenate([info.side, info.region])

        jnt.setAttr('type', 'Other')
        jnt.setAttr('otherType', info.joint_name)

        if not info.side:
            jnt.setAttr('side', 'Center')

        if info.side == 'L':
            jnt.setAttr('side', 'Left')

        if info.side == 'R':
            jnt.setAttr('side', 'Right')

        if info.utility == 'Roll':
            continue

        if info.joint_name == 'Shoulder' or info.joint_name == 'Hip':
            naming_utils.add_tags(jnt, {'_skin': 'False'})

        else:
            naming_utils.add_tags(jnt, {'_skin': 'True'})

        if key in jnt_dict:
            jnt_dict[key].append(jnt)
        elif info.region:
            jnt_dict[key] = [jnt]

    progress_bar.setMaximum(len(jnt_dict) + 4)

    # Create Main
    main = virtual_classes.MainNode()
    networks.append(main)

    pymel.rename(main, 'Main_Net')
    naming_utils.add_tags(main, tags={'Type': 'Main', 'Region': 'Main', 'Side': 'Center'})

    # Connect Joint Root To Main Net
    root.message.connect(main.ROOT[0])

    # Create Network Nodes

    for key in sorted(jnt_dict.keys()):

        info = naming_utils.ItemInfo(key)
        if info.region == 'Spine':
            net = virtual_classes.SplineIKNet()
            net.message.connect(main.SPINE[0])
            networks.append(net)

        elif info.region == 'Arm':
            net = virtual_classes.LimbNode()
            idx = main.ARMS.getNumElements()
            net.message.connect(main.ARMS[idx])
            networks.append(net)

        elif info.region == 'Clavicle':
            net = virtual_classes.ClavicleNode()
            idx = main.CLAVICLES.getNumElements()
            net.message.connect(main.CLAVICLES[idx])
            networks.append(net)

        elif info.region == 'Leg':
            net = virtual_classes.LimbNode()
            idx = main.LEGS.getNumElements()
            net.message.connect(main.LEGS[idx])
            networks.append(net)

        elif info.region == 'Head':
            net = virtual_classes.LimbNode()
            idx = main.HEAD.getNumElements()
            net.message.connect(main.HEAD[idx])
            networks.append(net)

        elif info.region == 'Hand':
            # Hand has many joint chains, unique code to deal with it.
            net = virtual_classes.LimbNode()
            idx = main.HANDS.getNumElements()
            net.message.connect(main.HANDS[idx])
            networks.append(net)
            # Name Nodes
            pymel.rename(net, naming_utils.concatenate([key, 'Net']))
            naming_utils.add_tags(net, tags={'Type': 'IKFK', 'Region': info.region, 'Side': info.side})

            hand_dict = {}
            # Create a new dict with fingers as keys
            for jnt in jnt_dict[key]:
                jnt_info = naming_utils.ItemInfo(jnt.name())
                key = jnt_info.joint_name

                if key in hand_dict:
                    hand_dict[key].append(jnt)
                elif info.region:
                    hand_dict[key] = [jnt]

            for key in hand_dict.keys():
                for jnt in hand_dict[key]:
                    elem_idx = net.jntsAttr.getNumElements()
                    jnt.message.connect(net.jntsAttr[elem_idx])
                    virtual_classes.attach_class(jnt, net)

            continue

        else:
            net = virtual_classes.LimbNode()
            networks.append(net)
        info = naming_utils.ItemInfo(key)

        # Name Nodes
        pymel.rename(net, naming_utils.concatenate([key, 'Net']))
        naming_utils.add_tags(net, tags={'Type': 'IKFK', 'Region': info.region, 'Side': info.side})

        # Connect Joints
        for idx, jnt in enumerate(joint_utils.get_joint_chain(jnt_dict[key])):
            elem_idx = net.jntsAttr.getNumElements()
            jnt.message.connect(net.jntsAttr[elem_idx])
            virtual_classes.attach_class(jnt, net)

    print networks
    # networks = pymel.ls(type='network')
    # print networks
    # return

    # Build Main
    for net in networks:
        if net.region == 'Main':
            build_main(net=net)
            # Add Scale constraint
            root = net.ROOT.get()[0]

            pymel.scaleConstraint([net.main_ctrl[0], root])
            pymel.parentConstraint([net.main_ctrl[1], root])
            progress_bar.setValue(progress_bar.value() + 1)

    # Build Arms
    for net in networks:
        if net.region == 'Arm':
            build_ikfk_limb(jnts=net.jnts, net=net, ik_shape='Cube01', fk_size=2.0)
            pymel.orientConstraint([net.ik_ctrls[0], net.ik_jnts[2]], maintainOffset=True)
            grp = group_limb(net)
            grp.setParent(main.main_ctrl[0])
            progress_bar.setValue(progress_bar.value() + 1)

    # Build Clavicle
    for net in networks:
        if net.region == 'Clavicle':
            build_clavicle(jnts=net.jnts, net=net)
            grp = group_limb(net)
            grp.setParent(main.main_ctrl[0])
            progress_bar.setValue(progress_bar.value() + 1)

    # Build Legs
    for net in networks:
        if net.region == 'Leg':
            build_ikfk_limb(jnts=net.jnts, net=net, ik_shape='FootCube01', fk_size=1.5)  # todo: add support for mirrored joints
            build_reverse_foot_rig(net=net)
            grp = group_limb(net)
            grp.setParent(main.main_ctrl[0])
            progress_bar.setValue(progress_bar.value() + 1)

    # Build IK Spline
    for net in networks:
        if net.region == 'Spine':
            build_spine(jnts=net.jnts, net=net)
            grp = group_limb(net)
            grp.setParent(main.main_ctrl[0])
            progress_bar.setValue(progress_bar.value() + 1)

    # Build Head
    for net in networks:
        if net.region == 'Head':
            build_head(jnts=net.jnts, net=net)
            grp = group_limb(net)
            grp.setParent(main.main_ctrl[0])
            progress_bar.setValue(progress_bar.value() + 1)

    # Build Hands
    for net in networks:
        if net.region == 'Hand':
            build_hand(jnts=net.jnts, net=net)
            grp = group_limb(net)
            grp.setParent(main.main_ctrl[0])


    # Build Space Switching
    build_space_switching(main_net=main)
    progress_bar.setValue(progress_bar.value() + 1)

    # Build Roll Joints
    build_upper_limb_roll_jnts(main_net=main)
    progress_bar.setValue(progress_bar.value() + 1)
    build_lower_limb_roll_jnts(main_net=main, up_axis='+Z')
    progress_bar.setValue(progress_bar.value() + 1)

    progress_bar.setValue(progress_bar.maximum())
    progress_bar.hide()

    root = main.ROOT.get()[0]

    main_grp_name = 'Rig_GRP'
    main_grp = group_limb(main, name=main_grp_name)
    root.setParent(main_grp)

    # Colors
    ctrls = main.getAllCtrls()
    set_ctrl_colors(main, ctrls)

    # Lock Ctrls
    lock_ctrls(main, ctrls)





"""TEST CODE"""

if __name__ == '__main__':

    delete_rig()
    build_humanoid_rig()

    """Example"""
    # import pymel.core as pymel
    # from python.modules import build_rig
    # reload(build_rig)
    #
    # build_rig.build_ikfk_limb(jnts=pymel.selected(),
    #                           ik_shape='Cube01',
    #                           ik_size=0.3,
    #                           fk_size=0.3,
    #                           pole_size=0.3,
    #                           ikfk_size=0.3)











