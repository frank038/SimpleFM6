#!/usr/bin/env python3

"""
archivemount program service
find all archive mounted by archivemount
autostart module name must be in the form: autostart_WHATEVER_NAME
in the case of errors, just remove the file fuse_mounted in /tmp/archivemount
"""
import os
from PyQt6.QtWidgets import (QDialog,QBoxLayout,QLabel,QPushButton,QApplication,QMenu)
from PyQt6.QtGui import (QIcon)
from PyQt6.QtCore import (Qt,QSize)
from cfg import TOOLBAR_BUTTON_SIZE

#  module_name: useless
def mmodule_name():
    return "Autostart archivemount"

# 1 : one item selected - 2 : more than one item selected - 3 : one or more items selected- 4 on background - 5 always - 6 autostart
# action type
def mmodule_type(win):
    return 6

#
class ModuleCustom():
    def __init__(self, win):
        self.win = win
        base_dest_dir = "/tmp/archivemount"
        try:
            if not os.path.exists(base_dest_dir):
                os.mkdir(base_dest_dir)
        except Exception as E:
            MyDialog("ERROR", "\n{}".format(str(E)))
        #
        self.fuse_mounted = os.path.join(base_dest_dir, "fuse_mounted")
        try:
            # empty or create an useless file
            if not os.listdir(base_dest_dir):
                try:
                    with open(self.fuse_mounted, "w") as ff:
                        ff.write("")
                except Exception as E:
                    MyDialog("ERROR", "\n{}.".format(str(E)))
            ### get the mounted archives
            # file name - mount point name (without /tmp/archivemount)
            fuse_mounted_list = []
            with open(self.fuse_mounted, "r") as ff:
                fuse_mounted_list = ff.readlines()
            # add the buttons
            for idx in range(0,len(fuse_mounted_list),2):
                # with full path
                file_name = fuse_mounted_list[idx].strip("\n")
                # only mount name
                mount_name = fuse_mounted_list[idx+1].strip("\n")
                #
                dest_dir = os.path.join(base_dest_dir, mount_name)
                #
                if os.path.exists(dest_dir):
                    self.media_btn = QPushButton(QIcon("icons/fuse-archive.png"),None)
                    if TOOLBAR_BUTTON_SIZE:
                        self.media_btn.setIconSize(QSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE))
                    # 
                    # if mount_name == file_name:
                        # self.media_btn.setToolTip(file_name)
                    # else:
                    self.media_btn.setToolTip(file_name+" - ("+mount_name+")")
                    #
                    self.media_btn_menu = QMenu()
                    self.media_btn_menu.addAction("Open", lambda x=dest_dir: self.fusermountf(x))
                    self.media_btn_menu.addAction("Umount", lambda x=dest_dir,y=self.media_btn: self.fuserumountf(x,y))
                    self.media_btn.setMenu(self.media_btn_menu)
                    self.win.disk_box.addWidget(self.media_btn)
        except Exception as E:
            MyDialog("ERROR", "\n{}.".format(str(E)))
    

    # open an archive, or open the tab
    def fusermountf(self, dest_dir):
        num_tabs = self.win.mtab.count()
        tab_found = None
        for i in range(num_tabs):
            i_tab_text = self.win.mtab.tabText(i)
            if i_tab_text == os.path.basename(dest_dir):
                tab_found = i
                break
        if tab_found == None:
            self.win.openDir(dest_dir, 1)
        else:
            self.win.mtab.setCurrentIndex(tab_found)
    
    # umount the mounted archive
    def fuserumountf(self, dest_dir, btn):
        ret = os.system("fusermount -u '{}'".format(dest_dir))
        if ret == 0:
            # btn.deleteLater()
            #
            try:
                archive_mount_name = os.path.basename(dest_dir)
                os.rmdir(dest_dir)
                fuse_mounted_list = []
                with open(self.fuse_mounted, "r") as ff:
                    fuse_mounted_list = ff.readlines()
                #
                len_fuse_mounted_list = len(fuse_mounted_list)
                # first: archive name - second: mount name
                for idx in range(len_fuse_mounted_list-1, -1, -2):
                    # mount name
                    item_mount = fuse_mounted_list[idx]
                    # # archive name
                    # item_name = fuse_mounted_list[idx-1]
                    #
                    # close the tabs
                    num_tabs = self.win.mtab.count()
                    for i in range(num_tabs):
                        curr_tab_text = self.win.mtab.tabText(i)
                        if curr_tab_text == archive_mount_name:
                            self.win.mtab.removeTab(i)
                            break
                    #
                    # remove the button
                    btn.deleteLater()
                    #
                    if os.path.basename(dest_dir) == item_mount.strip("\n"):
                        del fuse_mounted_list[idx]
                        del fuse_mounted_list[idx-1]
                with open(self.fuse_mounted, "w") as ff:
                    for item in fuse_mounted_list:
                        ff.write(item)
            except Exception as E:
                MyDialog("Info", "Error while umount the folder\n{}\n{}".format(dest_dir, str(E)))
            # open one tab if there are none
            num_tabs = self.win.mtab.count()
            if num_tabs == 0:
                self.win.openDir(os.path.expanduser("~"), 1)
        else:
            MyDialog("Info", "Error while umounting the folder\n{}\n{}".format(dest_dir, ret))


class MyDialog(QDialog):
    def __init__(self, *args, parent=None):
        super(MyDialog, self).__init__(parent)
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle(args[0])
        # self.resize(500,300)
        # main box
        mbox = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        mbox.setContentsMargins(5,5,5,5)
        self.setLayout(mbox)
        #
        label = QLabel(args[1])
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mbox.addWidget(label)
        #
        button_ok = QPushButton("     Ok     ")
        mbox.addWidget(button_ok)
        #
        button_ok.clicked.connect(self.close)
        self.exec()
