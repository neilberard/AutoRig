import pymel.core as pymel
import siteCustomize
import os


def skin_mesh(meshes):
    main_node = pymel.PyNode('Main_Net')

    skin_list = []

    for jnt in pymel.ls(type='joint'):
        if jnt.hasAttr('_skin') and jnt._skin.get() == 'True':
            print jnt._skin.get()
            skin_list.append(jnt)

    skin_list.extend(meshes)

    pymel.skinCluster(skin_list, toSelectedBones=True, maximumInfluences=4)

def import_range_of_motion():
    path = os.path.join(siteCustomize.ROOT_DIR, 'animations', 'rom.atom')
    print path

    pass


