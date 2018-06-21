import pymel.core as pymel
import siteCustomize
import os
import json
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


from python.libs import consts, virtual_classes


def export_pose(region, pose_name):

    dir_path = os.path.join(siteCustomize.ROOT_DIR, 'animations', 'poses', region)
    json_path = os.path.join(dir_path, pose_name, 'new.json')

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    json_path = json_path.replace('\\', '/')
    print json_path

    pose_data = {'key': 'this'}

    log.info('Exporting data in json file {}'.format(json_path))
    with open(json_path, 'w') as pose_json:
        json.dump(pose_data, pose_json, sort_keys=True, indent=4)
    log.info('Json export done')


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
    #
    # ctrl = pymel.selected()[0]
    #
    # export_pose(ctrl.region, pose_name='test')


    with pymel.UndoChunk():
        main = pymel.PyNode('Main_Net')
        root = main.jnts[0]
        bake_anim(root)
        export_anim(root)

    pymel.undo()
