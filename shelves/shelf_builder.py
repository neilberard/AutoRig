import maya.cmds as mc
import siteCustomize
import os


def _null(*args):
    pass


class _shelf():
    '''A simple class to build shelves in maya. Since the build method is empty,
    it should be extended by the derived class to build the necessary shelf elements.
    By default it creates an empty shelf called "customShelf".'''

    def __init__(self, name="Auto_Rig"):
        self.name = name

        self.iconPath = os.path.join(siteCustomize.ROOT_DIR, 'icons', 'autorig_toolset.png')

        self.labelBackground = (0, 0, 0, 0)
        self.labelColour = (.9, .9, .9)

        self._cleanOldShelf()
        mc.setParent(self.name)
        self.build()

    def build(self):
        '''This method should be overwritten in derived classes to actually build the shelf
        elements. Otherwise, nothing is added to the shelf.'''
        pass

    def addButton(self, label, command=_null, doubleCommand=_null):
        '''Adds a shelf button with the specified label, command, double click command and image.'''
        mc.setParent(self.name)
        mc.shelfButton(width=37, height=37, image=self.iconPath, l=label, command=command, dcc=doubleCommand, imageOverlayLabel=label, olb=self.labelBackground, olc=self.labelColour)

    def addMenuItem(self, parent, label, command=_null, icon=""):
        '''Adds a shelf button with the specified label, command, double click command and image.'''

        return mc.menuItem(p=parent, l=label, c=command, i=self.iconPath)

    def addSubMenu(self, parent, label, icon=None):
        '''Adds a sub menu item with the specified label and icon to the specified parent popup menu.'''
        if icon:
            icon = self.iconPath + icon
        return mc.menuItem(p=parent, l=label, i=icon, subMenu=1)

    def _cleanOldShelf(self):
        '''Checks if the shelf exists and empties it if it does or creates it if it does not.'''
        if mc.shelfLayout(self.name, ex=1):
            if mc.shelfLayout(self.name, q=1, ca=1):
                for each in mc.shelfLayout(self.name, q=1, ca=1):
                    mc.deleteUI(each)
        else:
            mc.shelfLayout(self.name, p="ShelfLayout")


###################################################################################
'''This is an example shelf.'''
class customShelf(_shelf):
    def build(self):
        self.addButton(label="ATRIG", command="from python.ui import tools_window; reload(tools_window); tools_window.showUI()")
        # self.addButon("button2")0
        # self.addButon("popup")
        # p = mc.popupMenu(b=1)
        # self.addMenuItem(p, "popupMenuItem1")
        # self.addMenuItem(p, "popupMenuItem2")
        # sub = self.addSubMenu(p, "subMenuLevel1")
        # self.addMenuItem(sub, "subMenuLevel1Item1")
        # sub2 = self.addSubMenu(sub, "subMenuLevel2")
        # self.addMenuItem(sub2, "subMenuLevel2Item1")
        # self.addMenuItem(sub2, "subMenuLevel2Item2")
        # self.addMenuItem(sub, "subMenuLevel1Item2")
        # self.addMenuItem(p, "popupMenuItem3")
        # self.addButon("button3")

##################################################################################