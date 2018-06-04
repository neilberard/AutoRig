import pymel.core as pymel
import siteCustomize
import os


def skin_mesh(meshes, main_node):
    """

    :param meshes:
    :param main_node: Main network node.
    :return:
    """
    main_node = pymel.PyNode('Main_Net')
    root = main_node.spine[0].jnts[0]

    skin_list = []

    for jnt in root.listRelatives(allDescendents=True):
        if jnt.hasAttr('_skin') and jnt._skin.get() == 'True':
            print jnt._skin.get()
            skin_list.append(jnt)

    skin_list.extend(meshes)

    pymel.skinCluster(skin_list, toSelectedBones=True, maximumInfluences=4)

def import_range_of_motion():
    path = os.path.join(siteCustomize.ROOT_DIR, 'animations', 'rom.atom')
    print path

    pass


