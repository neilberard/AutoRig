import pymel.core as pymel
import siteCustomize
import os
from shelves import shelf_builder

script_path = os.path.join(siteCustomize.ROOT_DIR, 'shelves')
icon_path = os.path.join(siteCustomize.ROOT_DIR, 'icons')

mspath = os.getenv('MAYA_SCRIPT_PATH')


new_script_path = "{};{}".format(mspath, script_path)
os.environ["MAYA_SCRIPT_PATH"] = new_script_path

if "XBMLANGPATH" in os.environ:
    os.environ["XBMLANGPATH"] = "{};{};".format(os.environ["XBMLANGPATH"], icon_path)

else:
    os.environ["XBMLANGPATH"] = '{};'.format(icon_path)



pymel.evalDeferred('shelf_builder.customShelf()')