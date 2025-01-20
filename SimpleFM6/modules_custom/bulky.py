#!/usr/bin/env python3
"""
multiple rename of the selected items - bulky
"""
import os
import stat
from PyQt6.QtWidgets import (QDialog,QGridLayout,QBoxLayout,QLabel,QPushButton,QComboBox,QLineEdit,QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (QIcon)
import pathlib
import subprocess
import shutil

# action name: this appears in the menu
def mmodule_name():
    return "Bulk rename"

# 1 : one item selected - 2 : more than one item selected - 3 : one or more items selected- 4 on background - 5 always
# action type
def mmodule_type(mainLView):
    if mainLView.selection:
        if len(mainLView.selection) > 1 and shutil.which("bulky"):
            return 2
        else:
            return 0
        
class ModuleCustom():
    def __init__(self, mainLView):
        current_dir = mainLView.lvDir
        index = mainLView.selection
        path_list = ""
        #
        for idx in index:
            if path_list:
                path_list += " "
            path = mainLView.fileModel.fileInfo(idx).absoluteFilePath()
            #
            # if os.access(path, os.R_OK):
            path_list += pathlib.Path(path).as_uri()
        #
        try:
            #subprocess.check_output("bulky {}".format(path_list), shell=True)
            os.system("bulky {}".format(path_list))
        except Exception as E:
            MyDialog("ERROR", str(E))


class MyDialog(QDialog):
    def __init__(self, *args, parent=None):
        super(MyDialog, self).__init__(parent)
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle(args[0])
        # self.resize(400,300)
        # main box
        mbox = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        mbox.setContentsMargins(5,5,5,5)
        self.setLayout(mbox)
        #
        label = QLabel(args[1])
        label.setWordWrap(True)
        mbox.addWidget(label)
        #
        button_ok = QPushButton("     Ok     ")
        mbox.addWidget(button_ok)
        #
        button_ok.clicked.connect(self.close)
        self.exec()
