import pymel.core as pymel
import siteCustomize
import os


def skin_mesh(meshes, main_node):
    """

    :param meshes:
    :param main_node: Main network node.
    :return:
    """
    try:
        pymel.skinCluster(meshes, edit=True, unbind=True)
    except:
        pass


    xml = 'body_skin_weights.xml'

    path = os.path.join(siteCustomize.ROOT_DIR, 'skin_data')
    root = main_node.spine[0].jnts[0]

    skin_list = []

    for jnt in root.listRelatives(allDescendents=True):
        if jnt.hasAttr('_skin') and jnt._skin.get() == 'True':
            skin_list.append(jnt)

    skin_list.append(root)

    skin_list.extend(meshes)

    skin_cluster = pymel.skinCluster(skin_list, toSelectedBones=True, maximumInfluences=4)


    pymel.deformerWeights(xml, im=True, deformer=skin_cluster, method='index', path=path)


def import_range_of_motion(main_net):
    pymel.select(main_net.getAllCtrls())

    path = os.path.join(siteCustomize.ROOT_DIR, 'animations', 'rom.atom')
    try:

        pymel.importFile(path, type='atomImport')
    except:
        pass

def clear_animation(main_net):
    for ctrl in main_net.getAllCtrls():
        pymel.cutKey(ctrl, clear=True)




    pass


