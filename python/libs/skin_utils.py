import pymel.core as pymel

def skin_mesh(meshes):
    skin_list = []

    for jnt in pymel.ls(type='joint'):
        if jnt.hasAttr('_skin') and jnt._skin.get() == 'True':
            print jnt._skin.get()
            skin_list.append(jnt)

    skin_list.extend(meshes)

    pymel.skinCluster(skin_list, toSelectedBones=True, maximumInfluences=4)

