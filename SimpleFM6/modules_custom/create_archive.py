#!/usr/bin/env python3
"""
create a tar or tgz or zip archive
"""
import os
import stat
from PyQt6.QtWidgets import (QDialog,QGridLayout,QBoxLayout,QLabel,QPushButton,QComboBox,QLineEdit,QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (QIcon,QFontMetrics,QFont)
import subprocess
import shutil

#  module_type: this appears in the menu
def mmodule_name():
    return "Compress data"

# 1 : one item selected - 2 : more than one item selected - 3 : one or more items selected- 4 on background - 5 always
# action type
def mmodule_type(mainLView):
    if mainLView.selection:
        # index = mainLView.selection[0]
        # path = mainLView.fileModel.fileInfo(index).absoluteFilePath()
        # if os.path.islink(path):
            # return 0
        if shutil.which("tar") or shutil.which("7z"):
            return 3
        else:
            return 0


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


class compressData(QDialog):
    def __init__(self, path_list, current_dir, parent=None):
        super(compressData, self).__init__(parent)
        self.current_dir = current_dir
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle("Compress data")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        # self.resize(600,250)
        #
        self.path_list = path_list
        #
        compressor_list = []
        # for zip
        if shutil.which("7z"):
            compressor_list.append("Zip")
            compressor_list.append("7z")
        #
        if shutil.which("tar"):
            compressor_list.append("Tar")
            # if shutil.which("gzip"):
                # compressor_list.append("TarGz")
        #
        grid = QGridLayout()
        grid.setContentsMargins(5,5,5,5)
        #
        label = QLabel("Type")
        #
        self.cb = QComboBox()
        self.cb.addItems(compressor_list)
        #
        label2 = QLabel("Name of the archive:")
        #
        self.le1 = QLineEdit()
        if len(self.path_list) == 1:
            self.le1.setText(os.path.basename(self.path_list[0]))
        #
        button1 = QPushButton("Compress")
        button1.clicked.connect(self.fcompress)
        #
        button_ok = QPushButton("     Exit     ")
        grid.addWidget(label, 0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self.cb, 0, 1, 1, 2, Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(label2, 1, 0, 1, 3)
        grid.addWidget(self.le1, 2, 0, 1, 3)
        grid.addWidget(button1, 3, 0, 1, 3)
        grid.addWidget(button_ok, 5, 0, 1, 3)
        self.setLayout(grid)
        button_ok.clicked.connect(self.close)
        self.exec()

    def fcompress(self):
        container_choosen = self.cb.currentText()
        if container_choosen == "Zip":
            archive_name = self.le1.text()
            if archive_name == "" or os.path.exists(os.path.join(self.current_dir, archive_name+".zip")):
                MyDialog("Info", "Choose a different name.")
            else:
                try:
                    for iitem in self.path_list:
                        subprocess.check_output("7z a '{}'.zip '{}'".format(os.path.join(self.current_dir, self.le1.text()), iitem), shell=True)
                    self.close()
                    MyDialog("Info", "Archive created:\n{}".format(self.le1.text()+".zip"))
                except Exception as E:
                    self.close()
                    MyDialog("ERROR", str(E))
        elif container_choosen == "7z":
            archive_name = self.le1.text()
            if archive_name == "" or os.path.exists(os.path.join(self.current_dir, archive_name+".7z")):
                MyDialog("Info", "Choose a different name.")
            else:
                try:
                    for iitem in self.path_list:
                        subprocess.check_output("7z a '{}'.7z '{}'".format(os.path.join(self.current_dir, self.le1.text()), iitem), shell=True)
                    self.close()
                    MyDialog("Info", "Archive created:\n{}".format(self.le1.text()+".7z"))
                except Exception as E:
                    self.close()
                    MyDialog("ERROR", str(E))
        elif container_choosen == "Tar":
            archive_name = self.le1.text()
            if archive_name == "" or os.path.exists(os.path.join(self.current_dir, archive_name+".tar")):
                MyDialog("Info", "Choose a different name.")
            else:
                try:
                    command = "cd '{0}' && tar -cf '{1}'.tar '{2}'".format(self.current_dir, self.le1.text(), os.path.basename(self.path_list[0]))
                    subprocess.check_output(command, shell=True)
                    #
                    if len(self.path_list) > 1:
                        for iitem in self.path_list[1:]:
                            command = "cd '{0}' && tar --append --file='{1}'.tar '{2}'".format(self.current_dir, self.le1.text(), os.path.basename(iitem))
                            subprocess.check_output(command, shell=True)
                    self.close()
                    MyDialog("Info", "Archive created:\n{}".format(self.le1.text()+".tar"))
                except Exception as E:
                    self.close()
                    MyDialog("ERROR", str(E))
        # elif container_choosen == "TarGz":
            # archive_name = self.le1.text()
            # if archive_name == "" or os.path.exists(os.path.join(self.current_dir, archive_name+".tar")) or os.path.exists(os.path.join(self.current_dir, archive_name+".tar.gz")):
                # MyDialog("Info", "Choose a different name.")
            # else:
                # try:
                    # command = "cd '{0}' && tar -cf '{1}'.tar '{2}'".format(self.current_dir, self.le1.text(), os.path.basename(self.path_list[0]))
                    # subprocess.check_output(command, shell=True)
                    # if len(self.path_list) > 1:
                        # for iitem in self.path_list[1:]:
                            # command = "cd '{0}' && tar --append --file='{1}'.tar '{2}'".format(self.current_dir, self.le1.text(), os.path.basename(iitem))
                            # subprocess.check_output(command, shell=True)
                    # command = "cd '{0}' && gzip '{1}'".format(self.current_dir, self.le1.text()+".tar")
                    # subprocess.call([command], shell=True)
                    # self.close()
                    # MyDialog("Info", "Archive created:\n{}".format(self.le1.text()+".tar.gz"))
                # except Exception as E:
                    # self.close()
                    # MyDialog("ERROR", str(E))

class ModuleCustom():
    
    def __init__(self, mainLView):
        current_dir = mainLView.lvDir
        index = mainLView.selection
        path_list = []
        skipped_items = []
        for idx in index:
            path = mainLView.fileModel.fileInfo(idx).absoluteFilePath()
            #
            if os.access(path, os.R_OK):
                path_list.append(path)
            else:
                skipped_items.append(os.path.basename(path))
        if skipped_items != []:
            ilist = "\n"
            skipped_items.sort()
            for iitem in skipped_items:
                ilist += iitem+"\n"
            MyDialog("Info", "The following items have been skipped:\n{}".format(ilist))
        if path_list != []:
            compressData(path_list, current_dir)
