import pymel.all as pymel
import maya.cmds as cmds
from python.libs import naming_utils
from python.libs import joint_utils
from python.libs import shapes
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def attach_class(node, net):
    """
    Adds a string attribute to a PyNode set to the virtual class identifier. Example node._class = '_TransformNode'
    :param node: PyNode to add attribute to.
    :param net: Network to associate the PyNode with IE: 'L_Leg_Net'
    :return: PyNode as a virtual class
    """
    if node.hasAttr('_class'):
        node.deleteAttr('_class')

    if node.hasAttr('Network'):
        node.deleteAttr('Network')

    #Ensuring that node is a vanilla pynode
    node = pymel.PyNode(node)

    node.addAttr('Network', dataType='string')
    node.Network.set(net.name())

    if isinstance(node, pymel.nodetypes.Joint):
        node.addAttr('_class', dataType='string')
        node._class.set('_JointNode')
        return pymel.PyNode(node)

    if isinstance(node, pymel.nodetypes.Transform):
        node.addAttr('_class', dataType='string')
        node._class.set('_TransformNode')
        new_node = pymel.PyNode(node)
        assert isinstance(new_node, TransformNode)
        return new_node

    if isinstance(node, pymel.nodetypes.Network):
        node.addAttr('_class', dataType='string')
        node._class.set('_LimbNode')
        return pymel.PyNode(node)

    log.warning('Could not find class for: '.format(node))


class BaseNode():
    """
    Subclass must also inherit leaf class with pymel.nodetype.dagnode as it's hierarchy. IE: 'pymel.nodetypes.Joint'
    This class contains some basic properties that are used for accessing other nodes
    """

    @property
    def network(self):
        if self.message.connections():
            for obj in self.message.connections():
                if obj.hasAttr('_class'):
                    return obj

        elif self.hasAttr('Network'):
            return pymel.PyNode(self.Network.get())

    @property
    def networkAttr(self):
        for obj in self.message.connections(plugs=True):
            if obj.node().hasAttr('_class'):
                return obj

    @property
    def main(self):
        for obj in self.network.message.connections():
            if obj.node().hasAttr('_class'):
                return obj

    @property
    def mainAttr(self):

        try:
            for obj in self.network.message.connections(plugs=True):
                if obj.node().hasAttr('_class'):
                    return obj
            return self.network.message.connections(plugs=True)[0]

        except:
            return None

    @property
    def jnts(self):
        return self.network.JOINTS.connections()

    @property
    def jntsAttr(self):
        return self.network.JOINTS

    @property
    def fk_jnts(self):
        return self.network.FK_JOINTS.connections()

    @property
    def fkJntsAttr(self):
        return self.network.FK_JOINTS

    @property
    def ik_jnts(self):
        return self.network.IK_JOINTS.connections()

    @property
    def ikJntsAttr(self):
        return self.network.IK_JOINTS

    @property
    def ik_ctrls(self):
        return self.network.IK_CTRLS.connections()

    @property
    def ikCtrlsAttr(self):
        return self.network.IK_CTRLS

    @property
    def fk_ctrls(self):
        return self.network.FK_CTRLS.connections()

    @property
    def pole_ctrls(self):
        return self.network.POLE.connections()

    @property
    def fkCtrlsAttr(self):
        return self.network.FK_CTRLS

    @property
    def ik_handles(self):
        return self.network.IK_HANDLE.connections()

    @property
    def switch(self):
        if self.network.SWITCH.connections():
            return self.network.SWITCH.connections()[0] # todo: This is busted since clavicle is overriding switch method, use self.network.switch for now
        else:
            return None

    @property
    def ikHandlesAttr(self):
        return self.network.IK_HANDLE

    @property
    def name_info(self):
        return naming_utils.ItemInfo(self)

    @property
    def _class(self):
        return self._class.get()

    @property
    def side(self):
        return self.network.Side.get()

    @property
    def region(self):
        return self.network.Region.get()

    @property
    def utility(self):
        try:
            return self.Utility.get()
        except:
            return None

    @property
    def joint_name(self):
        info = naming_utils.ItemInfo(self.name())
        return info.joint_name

    @property
    def base_name(self):
        info = naming_utils.ItemInfo(self.name())
        return info.base_name

    @property
    def info_index(self):
        info = naming_utils.ItemInfo(self.name())
        return info.index

    @property
    def limb_grp(self):
        # Using mel to speed up the code
        for obj in cmds.ls(type='transform'):
            if cmds.attributeQuery('Utility', node=obj, exists=True) and\
                    cmds.getAttr('{}.Utility'.format(obj)) == 'LimbGrp' and\
                    cmds.attributeQuery('Network', node=obj, exists=True) and\
                    cmds.getAttr('{}.Network'.format(obj)) == self.network.name():
                return pymel.PyNode(obj)

    def add_network_tag(self):
        self.add_tags({'Network': self.network.name()})

    def add_tags(self, tags):
        try:
            naming_utils.add_tags(self, tags)
        except Exception as ex:
            log.warning('Failed to add tags: {}, {}, {}'.format(self, tags, ex))

    def getRoot(self):
        return joint_utils.get_root(self)

    def getCtrlRig(self):
        """Return all control rig nodes, ignore skinning joints"""

        nodes = []

        for obj in cmds.ls(type='transform'):
            if cmds.attributeQuery('Network', node=obj, exists=True) and\
               cmds.getAttr('{}.Network'.format(obj)) == self.network.name() and obj not in self.jnts:
                nodes.append(pymel.PyNode(obj))

        return nodes

    def getMirroredCtrl(self):
        """
        Find the Limb network connection to Main Net and traverse the mirrored network
        which is connected to another index, either 0 or 1.

        For example: L_Elbow_FK_CTRL  >>> L_ARM_Net.FK_CTLS[2] >>> MAIN_NET.ARMS[ idx ]
        Traverse: MAIN_NET.ARMS[ !idx ] >>> R_ARM_Net.FK_CTLS[2] >>> R_Elbow_FK_CTRL

        :return: Mirrored CTRL or None if failed to find ctrl.
        """

        net_attr = self.networkAttr  # Storing the network attr'
        limb = self.mainAttr  # Storing the main limb attr

        if not limb:  # If the network is not a limb, like 'Main', There is mo mirrored ctrl.
            return None
        for idx, element in enumerate(limb.array().elements()):
            if idx != limb.index():  # Traverse through the other idx connection limb network
                mirror_net = limb.array().elementByLogicalIndex(idx).connections()[0]
                mirror_array = mirror_net.getAttr(net_attr.array().attrName())
                return mirror_array[net_attr.index()]

    def getLimbCtrls(self):
        return self.network.getLimbCtrls()


# DAG CLASSES
class JointNode(pymel.nodetypes.Joint, BaseNode):
    """ this is an example of how to create your own subdivisions of existing nodes. """

    NODE_TYPE = 'JointNode'

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances the node in the scene """

        kwargs['type'] = cls.__melnode__
        return [node for node in pymel.ls(*args, **kwargs) if isinstance(node, cls)]

    @classmethod
    def _isVirtual(cls, obj, name):
        """PyMEL code should not be used inside the callback, only API and maya.cmds. """
        fn = pymel.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute('_class'):
                plug = fn.findPlug('_class')
                if plug.asString() == '_JointNode':
                    return True
                return False
        except:
            pass
        return False

    @classmethod
    def _preCreateVirtual(cls, **kwargs):
        """This is called before creation. python allowed."""
        return kwargs

    @classmethod
    def _postCreateVirtual(cls, newNode):
        """ This is called before creation, pymel/cmds allowed."""

        pymel.addAttr(newNode, longName='_class', dataType='string')
        newNode._class.set('_JointNode')


class TransformNode(BaseNode, pymel.nodetypes.Transform):
    """ this is an example of how to create your own subdivisions of existing nodes. """

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances the node in the scene """

        kwargs['type'] = cls.__melnode__
        return [node for node in pymel.ls(*args, **kwargs) if isinstance(node, cls)]

    @classmethod
    def _isVirtual(cls, obj, name):
        """PyMEL code should not be used inside the callback, only API and maya.cmds. """
        fn = pymel.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute('_class'):
                plug = fn.findPlug('_class')
                if plug.asString() == '_TransformNode':
                    return True
                return False
        except:
            pass
        return False

    @classmethod
    def _preCreateVirtual(cls, **kwargs):
        """This is called before creation. python allowed."""
        return kwargs

    @classmethod
    def _postCreateVirtual(cls, newNode):
        """ This is called before creation, pymel/cmds allowed."""
        newNode.addAttr('_class', dataType='string')
        newNode._class.set('_TransformNode')


class CtrlNode(TransformNode):

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances the node in the scene """

        kwargs['type'] = cls.__melnode__
        return [node for node in pymel.ls(*args, **kwargs) if isinstance(node, cls)]

    @classmethod
    def _isVirtual(cls, obj, name):
        """PyMEL code should not be used inside the callback, only API and maya.cmds. """
        fn = pymel.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute('_class'):
                plug = fn.findPlug('_class')
                if plug.asString() == '_CtrlNode':
                    return True
                return False
        except:
            pass
        return False

    @classmethod
    def _preCreateVirtual(cls, **kwargs):
        """This is called before creation. python allowed."""
        return kwargs

    @classmethod
    def _postCreateVirtual(cls, newNode):
        """ This is called before creation, pymel/cmds allowed."""
        newNode.addAttr('_class', dataType='string')
        newNode._class.set('_CtrlNode')
        newNode.addAttr('SHAPE', attributeType='message', multi=True)

    def freeze_transform(self):
        pymel.makeIdentity(self, a=True, t=1, r=1, s=1, n=0, pn=1)

    def set_shape(self, shape):
        pymel.delete(self.getShapes())
        shapes.make_shape(shape_type=shape, transform=self, name=shape)

    def set_shape_size(self, size):
        for shape in self.getShapes():
            pymel.scale(shape.cv[:], (size, size, size))

    def set_shape_color(self, color):
        shapes = self.getShapes()

        for shape in shapes:
            shape.overrideEnabled.set(1)
            shape.overrideRGBColors.set(1)
            shape.overrideColorRGB.set(color)

    def reset_axis(self):
        if self.shapeAxis.get() == 'X':
            self.set_axis('X')

        if self.shapeAxis.get() == 'Z':
            self.set_axis('Z')

        if self.shapeAxis.get() == 'Y':
            self.set_axis('Y')

        if self.shapeAxis.get() == '-X':
            self.set_axis('-X')

        if self.shapeAxis.get() == '-Z':
            self.set_axis('-Z')

        if self.shapeAxis.get() == '-Y':
            self.set_axis('-Y')


    def set_axis(self, axis):

        with pymel.UndoChunk():
            x_matrix = pymel.datatypes.Matrix([0.0, -1.0, 0.0, 0.0],
                                              [1.0, 0.0, 0.0, 0.0],
                                              [0.0, 0.0, 1.0, 0.0],
                                              [0.0, 0.0, 0.0, 1.0])

            neg_x_matrix = pymel.datatypes.Matrix([1.0, 0.0, 0.0, 0.0],
                                                  [0.0, 0.0, -1.0, 0.0],
                                                  [0.0, 1.0, 0.0, 0.0],
                                                  [0.0, 0.0, 0.0, 1.0])

            y_matrix = pymel.datatypes.Matrix([0.0, 0.0, -1.0, 0.0],
                                              [0.0, 1.0, 0.0, 0.0],
                                              [1.0, 0.0, 0.0, 0.0],
                                              [0.0, 0.0, 0.0, 1.0])

            neg_y_matrix = pymel.datatypes.Matrix([0.0, 0.0, 1.0, 0.0],
                                                  [0.0, 1.0, 0.0, 0.0],
                                                  [-1.0, 0.0, 0.0, 0.0],
                                                  [0.0, 0.0, 0.0, 1.0])

            z_matrix = pymel.datatypes.Matrix([1.0, 0.0, 0.0, 0.0],
                                              [0.0, 0.0, 1.0, 0.0],
                                              [0.0, -1.0, 0.0, 0.0],
                                              [0.0, 0.0, 0.0, 1.0])

            neg_z_matrix = pymel.datatypes.Matrix([0.0, -1.0, 0.0, 0.0],
                                                  [1.0, 0.0, 1.0, 0.0],
                                                  [0.0, 0.0, 1.0, 0.0],
                                                  [0.0, 0.0, 0.0, 1.0])

            if axis == 'X':
                for shape in self.getShapes():
                    for cv in shape.cv[:]:
                        cv.setPosition(cv.getPosition() * x_matrix)

            if axis == '-X':
                for shape in self.getShapes():
                    for cv in shape.cv[:]:
                        cv.setPosition(cv.getPosition() * neg_x_matrix)

            if axis == 'Y': # Default Y up
                for shape in self.getShapes():
                    for cv in shape.cv[:]:
                        cv.setPosition(cv.getPosition() * y_matrix)

            if axis == '-Y': # Default Y up
                for shape in self.getShapes():
                    for cv in shape.cv[:]:
                        cv.setPosition(cv.getPosition() * neg_y_matrix)

            if axis == 'Z':
                for shape in self.getShapes():
                    for cv in shape.cv[:]:
                        cv.setPosition(cv.getPosition() * z_matrix)

            if axis == '-Z':
                for shape in self.getShapes():
                    for cv in shape.cv[:]:
                        cv.setPosition(cv.getPosition() * neg_z_matrix)

            self.shapeAxis.set(axis)

            pymel.ogs(reset=True)

    def create_offset(self):
        grp = pymel.group(empty=True)
        self.setParent(grp)
        return grp


# NETWORK CLASSES
class LimbNode(pymel.nt.Network, BaseNode):
    """ this is an example of how to create your own subdivisions of existing nodes. """

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances the node in the scene """

        kwargs['type'] = cls.__melnode__
        return [node for node in pymel.ls(*args, **kwargs) if isinstance(node, cls)]

    @classmethod
    def _isVirtual(cls, obj, name):
        """PyMEL code should not be used inside the callback, only API and maya.cmds. """
        fn = pymel.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute('_class'):
                plug = fn.findPlug('_class')
                if plug.asString() == '_LimbNode':
                    return True
                return False
        except:
            pass
        return False

    @classmethod
    def _preCreateVirtual(cls, **kwargs):
        """This is called before creation. python allowed."""
        return kwargs

    @classmethod
    def _postCreateVirtual(cls, newNode):
        """ This is called before creation, pymel/cmds allowed."""
        newNode.addAttr('_class', dt='string')
        newNode._class.set('_LimbNode')
        newNode.addAttr('JOINTS', attributeType='message', multi=True)
        newNode.addAttr('IK_JOINTS', attributeType='message', multi=True)
        newNode.addAttr('FK_JOINTS', attributeType='message', multi=True)
        newNode.addAttr('IK_CTRLS', attributeType='message', multi=True)
        newNode.addAttr('FK_CTRLS', attributeType='message', multi=True)
        newNode.addAttr('CTRLS', attributeType='message', multi=True)
        newNode.addAttr('POLE', attributeType='message', multi=True)
        newNode.addAttr('SWITCH', attributeType='message', multi=True)
        newNode.addAttr('ORIENTCONSTRAINT', attributeType='message', multi=True)
        newNode.addAttr('POINTCONSTRAINT', attributeType='message', multi=True)
        newNode.addAttr('IK_HANDLE', attributeType='message', multi=True)
        newNode.addAttr('IK_SNAP_LOC', attributeType='message', multi=True)

    @property
    def network(self):
        return self

    def getLimbCtrls(self):
        nodes = []

        for obj in cmds.ls(type='transform'):
            if cmds.attributeQuery('Network', node=obj, exists=True) and\
               cmds.getAttr('{}.Network'.format(obj)) == self.network.name() and \
               cmds.attributeQuery('Type', node=obj, exists=True) and \
               cmds.getAttr('{}.Type'.format(obj)) == 'CTRL':
                nodes.append(pymel.PyNode(obj))

        return nodes


class SplineIKNet(LimbNode):
    """ this is an example of how to create your own subdivisions of existing nodes. """

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances the node in the scene """

        kwargs['type'] = cls.__melnode__
        return [node for node in pymel.ls(*args, **kwargs) if isinstance(node, cls)]

    @classmethod
    def _isVirtual(cls, obj, name):
        """PyMEL code should not be used inside the callback, only API and maya.cmds. """
        fn = pymel.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute('_class'):
                plug = fn.findPlug('_class')
                if plug.asString() == '_SplineIKNet':
                    return True
                return False
        except:
            pass
        return False

    @classmethod
    def _preCreateVirtual(cls, **kwargs):
        """This is called before creation. python allowed."""
        return kwargs

    @classmethod
    def _postCreateVirtual(cls, newNode):
        """ This is called before creation, pymel/cmds allowed."""
        newNode.addAttr('_class', dataType='string')
        newNode._class.set('_SplineIKNet')
        newNode.addAttr('JOINTS', attributeType='message', multi=True)
        newNode.addAttr('IK_HANDLE', attributeType='message', multi=True)
        newNode.addAttr('IK_CTRLS', attributeType='message', multi=True)
        newNode.addAttr('CLUSTER_HANDLE', attributeType='message', multi=True)
        newNode.addAttr('COG', attributeType='message', multi=True)

    @property
    def network(self):
        return self

    @property
    def clusters(self):
        return self.CLUSTER_HANDLE.connections()

    @property
    def cog(self):
        return self.COG.connections()

    @property
    def clustersAttr(self):
        return self.CLUSTER_HANDLE


class MainNode(LimbNode):
    """ this is an example of how to create your own subdivisions of existing nodes. """

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances the node in the scene """

        kwargs['type'] = cls.__melnode__
        return [node for node in pymel.ls(*args, **kwargs) if isinstance(node, cls)]

    @classmethod
    def _isVirtual(cls, obj, name):
        """PyMEL code should not be used inside the callback, only API and maya.cmds. """
        fn = pymel.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute('_class'):
                plug = fn.findPlug('_class')
                if plug.asString() == '_MainNode':
                    return True
                return False
        except:
            pass
        return False

    @classmethod
    def _preCreateVirtual(cls, **kwargs):
        """This is called before creation. python allowed."""
        return kwargs

    @classmethod
    def _postCreateVirtual(cls, newNode):
        """ This is called before creation, pymel/cmds allowed."""
        newNode.addAttr('_class', dataType='string')
        newNode._class.set('_MainNode')
        newNode.addAttr('MAIN_CTRL', attributeType='message', multi=True)
        newNode.addAttr('ARMS', attributeType='message', multi=True)
        newNode.addAttr('CLAVICLES', attributeType='message', multi=True)
        newNode.addAttr('LEGS', attributeType='message', multi=True)
        newNode.addAttr('SPINE', attributeType='message', multi=True)
        newNode.addAttr('HEAD', attributeType='message', multi=True)
        newNode.addAttr('HANDS', attributeType='message', multi=True)
        newNode.addAttr('ROOT', attributeType='message', multi=True)

    @property
    def network(self):
        return self

    @property
    def main(self):
        return self

    @property
    def jnts(self):
        return self.ROOT.connections()

    @property
    def main_ctrl(self):
        return self.MAIN_CTRL.connections()

    @property
    def arms(self):
        return self.ARMS.connections()

    @property
    def legs(self):
        return self.LEGS.connections()

    @property
    def clavicles(self):
        return self.CLAVICLES.connections()

    @property
    def spine(self):
        return self.SPINE.connections()

    @property
    def head(self):
        return self.HEAD.connections()

    @property
    def hands(self):
        return self.HANDS.connections()

    def getAllCtrls(self):  # todo: Add support for multiple rigs in a scene.

        nodes = []

        for obj in cmds.ls(type='transform'):
            if cmds.attributeQuery('Type', node=obj, exists=True) and cmds.getAttr('{}.Type'.format(obj)) == 'CTRL':
                nodes.append(pymel.PyNode(obj))
        return nodes


class ClavicleNode(LimbNode):

    SUBNODE_TYPE = '_Clavicle'

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances of all characters in the scene """

        kwargs['type'] = cls.__melnode__
        return [node for node in pymel.ls(*args, **kwargs) if isinstance(node, cls)]

    @classmethod
    def _isVirtual(cls, obj, name):
        """PyMEL code should not be used inside the callback, only API and maya.cmds. """
        fn = pymel.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute('_class'):
                plug = fn.findPlug('_class')
                if plug.asString() == '_LimbNode':
                    if fn.hasAttribute('_subClass'):
                        plug = fn.findPlug('_subClass')
                        if plug.asString() == cls.SUBNODE_TYPE:
                            return True
                    return False
        except:
            pass
        return False

    @classmethod
    def _postCreateVirtual(cls, newNode):
        """ This is called before creation, pymel/cmds allowed."""
        LimbNode._postCreateVirtual(newNode)
        newNode.addAttr('_subClass', dt='string')
        newNode._subClass.set('_Clavicle')

    @property
    def network(self):
        return self

    @property
    def switch(self):
        try:
            attr = self.mainAttr
            net = self.main.arms[attr.index()]
            return net.switch
        except:
            log.warning('Failed to find IKFK, is this node hooked up to main?')

    def getLimbCtrls(self):
        ctrl_list = set()

        attr = self.mainAttr
        net = self.main.arms[attr.index()]

        for obj in pymel.listTransforms():
            # Clavicle CTRLS
            if obj.hasAttr('Type') and obj.Type.get() == 'CTRL' and obj.hasAttr('Network') and obj.Network.get() == self.network.name():
                ctrl_list.add(obj)
            # Get Arm CTRLS
            if obj.hasAttr('Type') and obj.Type.get() == 'CTRL' and obj.hasAttr('Network') and obj.Network.get() == net.name():
                ctrl_list.add(obj)

        return list(ctrl_list)


# Classes need to be registered to exist in the scene.
pymel.factories.registerVirtualClass(JointNode, nameRequired=False)
pymel.factories.registerVirtualClass(CtrlNode, nameRequired=False)
pymel.factories.registerVirtualClass(TransformNode, nameRequired=False)
pymel.factories.registerVirtualClass(SplineIKNet, nameRequired=False)
pymel.factories.registerVirtualClass(MainNode, nameRequired=False)
pymel.factories.registerVirtualClass(LimbNode, nameRequired=False)
pymel.factories.registerVirtualClass(ClavicleNode, nameRequired=False)
