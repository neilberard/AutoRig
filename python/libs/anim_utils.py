import pymel.core as pymel
import siteCustomize
import os
from python.libs import consts, virtual_classes


def bake_anim(root):
    root.setParent(None)

    start_time = int(pymel.playbackOptions(q=True, min=True))
    end_time = int(pymel.playbackOptions(q=True, max=True))

    # Note the hierarchy flag on bakeResults does not work as advertised, misses some children. Running through a loop.

    bake_jnts = root.listRelatives(allDescendents=True, type='joint')
    bake_jnts.append(root)
    pymel.bakeResults(bake_jnts, simulation=True, time=(start_time, end_time))


def export_anim(root):

    # Select Root
    pymel.select(root)

    scene_name = str(pymel.sceneName().basename().split('.')[0])
    path = os.path.join(siteCustomize.ROOT_DIR, 'animations', 'export', scene_name)
    path = path.replace('\\', '/')
    pymel.mel.eval('FBXResetExport()')

    pymel.mel.eval('FBXExportInAscii -v true')

    # EXPORT
    pymel.mel.eval('FBXExport -f "{0}" -s'.format(path))

if __name__ == '__main__':

    with pymel.UndoChunk():
        main = pymel.PyNode('Main_Net')
        root = main.jnts[0]
        bake_anim(root)
        export_anim(root)

    pymel.undo()
