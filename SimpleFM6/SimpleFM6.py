#!/usr/bin/env python3

# version 1.6.6

from PyQt6.QtCore import (QTimer,QModelIndex,QFileSystemWatcher,QEvent,QObject,QUrl,QFileInfo,QRect,QStorageInfo,QMimeData,QMimeDatabase,QFile,QThread,Qt,pyqtSignal,QSize,QMargins,QDir,QByteArray,QItemSelection,QItemSelectionModel,QPoint)
from PyQt6.QtWidgets import (QStyleFactory, QTreeWidget,QTreeWidgetItem,QLayout,QHBoxLayout,QHeaderView,QTreeView,QSpacerItem,QScrollArea,QTextEdit,QSizePolicy,QBoxLayout,QLabel,QPushButton,QApplication,QDialog,QGridLayout,QMessageBox,QLineEdit,QTabWidget,QWidget,QGroupBox,QComboBox,QCheckBox,QProgressBar,QListView,QItemDelegate,QStyle,QFileIconProvider,QAbstractItemView,QFormLayout,QMenu)
from PyQt6.QtGui import (QFileSystemModel,QAction,QDrag,QPixmap,QStaticText,QTextOption,QIcon,QStandardItem,QStandardItemModel,QFontMetrics,QColor,QPalette,QClipboard,QPainter,QFont,QPen)
import dbus
import psutil
import sys
from pathlib import PosixPath
import os
import stat
from urllib.parse import unquote, quote
import shutil
import time
import datetime
import glob
import importlib
import subprocess
import pwd
import threading
from xdg.BaseDirectory import *
from xdg.DesktopEntry import *
from cfg import *


############## user directory names
USER_DIRS = os.path.join(os.path.expanduser("~"), ".config", "user-dirs.dirs")
FILE_DIRS_CONTENT_TEMP = []
if os.path.exists(USER_DIRS):
    ff = open(USER_DIRS, "r")
    FILE_DIRS_CONTENT_TEMP = ff.readlines()
    ff.close()

FILE_DIRS = []

DIR_XDG_DESKTOP_DIR=None
DIR_XDG_DOCUMENTS_DIR=None
DIR_XDG_DOWNLOAD_DIR=None
DIR_XDG_MUSIC_DIR=None
DIR_XDG_PICTURES_DIR=None
DIR_XDG_PUBLICSHARE_DIR=None
DIR_XDG_TEMPLATES_DIR=None
DIR_XDG_VIDEOS_DIR=None

def _find_dir_name(name):
    dir_name = None
    fdir_name = name.strip("\n").split("=")[1].strip('"')
    return fdir_name.split("/")[1].lstrip(" ").rstrip(" ")
    
for fdir in FILE_DIRS_CONTENT_TEMP:
    if "XDG_DESKTOP_DIR" in fdir:
        _dir_name = _find_dir_name(fdir)
        DIR_XDG_DESKTOP_DIR=_dir_name
        FILE_DIRS.append([_dir_name, "desktop"])
    #
    elif "XDG_DOCUMENTS_DIR" in fdir:
        _dir_name = _find_dir_name(fdir)
        DIR_XDG_DOCUMENTS_DIR=_dir_name
        FILE_DIRS.append([_dir_name, "folder-documents"])
    #
    elif "XDG_DOWNLOAD_DIR" in fdir:
        _dir_name = _find_dir_name(fdir)
        DIR_XDG_DOWNLOAD_DIR=_dir_name
        FILE_DIRS.append([_dir_name, "folder-download"])
    #
    elif "XDG_MUSIC_DIR" in fdir:
        _dir_name = _find_dir_name(fdir)
        DIR_XDG_MUSIC_DIR=_dir_name
        FILE_DIRS.append([_dir_name, "folder-music"])
    #
    elif "XDG_PICTURES_DIR" in fdir:
        _dir_name = _find_dir_name(fdir)
        DIR_XDG_PICTURES_DIR=_dir_name
        FILE_DIRS.append([_dir_name, "folder-pictures"])
    #
    elif "XDG_PUBLICSHARE_DIR" in fdir:
        _dir_name = _find_dir_name(fdir)
        DIR_XDG_PUBLICSHARE_DIR=_dir_name
        FILE_DIRS.append([_dir_name, "folder-publicshare"])
    #
    elif "XDG_TEMPLATES_DIR" in fdir:
        _dir_name = _find_dir_name(fdir)
        DIR_XDG_EMPLATES_DIR=_dir_name
        FILE_DIRS.append([_dir_name, "folder-templates"])
    #
    elif "XDG_VIDEOS_DIR" in fdir:
        _dir_name = _find_dir_name(fdir)
        DIR_XDG_VIDEOS_DIR=_dir_name
        FILE_DIRS.append([_dir_name, "folder-videos"])
##############


# the mimeapps.list used by this program
if USER_MIMEAPPSLIST:
    MIMEAPPSLIST = os.path.expanduser('~')+"/.config/mimeapps.list"
else:
    MIMEAPPSLIST = "mimeapps.list"

# create an empty mimeapps.list if it doesnt exist
if not os.path.exists(MIMEAPPSLIST):
    ff = open(MIMEAPPSLIST, "w")
    ff.write("[Default Applications]\n")
    ff.write("[Added Associations]\n")
    ff.write("[Removed Associations]\n")
    ff.close()


if OPEN_WITH:
    try:
        import Utility.open_with as OW
    except Exception as E:
        OPEN_WITH = 0


#
if ICON_SIZE > ITEM_WIDTH:
    ITEM_WIDTH = ICON_SIZE
    ITEM_HEIGHT = ITEM_WIDTH

if THUMB_SIZE > ITEM_HEIGHT:
    ITEM_HEIGHT = THUMB_SIZE

if THUMB_SIZE > ITEM_WIDTH:
    ITEM_WIDTH = THUMB_SIZE

# max number of items - 1 to show in the message dialog
ITEMSDELETED = 30

# with of the dialog windows
dialWidth = DIALOGWIDTH

# where to look for desktop files or default locations
if xdg_data_dirs:
    xdgDataDirs = list(set(xdg_data_dirs))
else:
    xdgDataDirs = ['/usr/local/share', '/usr/share', os.path.expanduser('~')+"/.local/share"]
# consistency
if "/usr/share" not in xdgDataDirs:
    xdgDataDirs.append("/usr/share")
if os.path.expanduser('~')+"/.local/share" not in xdgDataDirs:
    xdgDataDirs.append(os.path.expanduser('~')+"/.local/share")
if "/usr/share/" in xdgDataDirs:
    xdgDataDirs.remove("/usr/share/")

# only one trashcan tab at time
TrashIsOpen = 0

class firstMessage(QWidget):
    
    def __init__(self, *args):
        super().__init__()
        title = args[0]
        message = args[1]
        self.setWindowTitle(title)
        # self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        box = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        box.setContentsMargins(5,5,5,5)
        self.setLayout(box)
        label = QLabel(message)
        box.addWidget(label)
        button = QPushButton("Close")
        box.addWidget(button)
        button.clicked.connect(self.close)
        self.show()
        # # QDesktopWidget is no more available
        # self.center()

    # def center(self):
        # qr = self.frameGeometry()
        # cp = QDesktopWidget().availableGeometry().center()
        # qr.moveCenter(cp)
        # self.move(qr.topLeft())


if not os.path.exists("winsize.cfg"):
    try:
        with open("winsize.cfg", "w") as ifile:
            ifile.write("1200;900;False")
    except:
        app = QApplication(sys.argv)
        fm = firstMessage("Error", "The file winsize.cfg cannot be created.")
        sys.exit(app.exec())

if not os.access("winsize.cfg", os.R_OK):
    app = QApplication(sys.argv)
    fm = firstMessage("Error", "The file winsize.cfg cannot be read.")
    sys.exit(app.exec())

if not os.path.exists("Bookmarks"):
    try:
        ifile = open("Bookmarks", "w")
        ifile.close()
    except Exception as E:
        fm = firstMessage("Error", str(E))
        sys.exit(app.exec())

WINW = 800
WINH = 600
WINM = "False"
try:
    with open("winsize.cfg", "r") as ifile:
        fcontent = ifile.readline()
    aw, ah, am = fcontent.split(";")
    WINW = aw
    WINH = ah
    WINM = am.strip()
except:
    app = QApplication(sys.argv)
    fm = firstMessage("Error", "The file winsize.cfg cannot be read.\nRebuilded.")
    try:
        with open("winsize.cfg", "w") as ifile:
            ifile.write("800;600;False")
    except:
        pass
    sys.exit(app.exec())

isXDGDATAHOME = 1

if USE_THUMB == 1:
    try:
        from pythumb import *
    except Exception as E:
        USE_THUMB = 0

# trash module
if USE_TRASH:
    try:
        import trash_module
    except Exception as E:
        app = QApplication(sys.argv)
        fm = firstMessage("Error", "Error while importing the module:\n{}".format(str(E)))
        sys.exit(app.exec())

# additional text
if USE_AD:
    try:
        from custom_icon_text import fcit
    except Exception as E:
        app = QApplication(sys.argv)
        fm = firstMessage("Error", "Error while importing the module:\n{}".format(str(E)))
        USE_AD = 0

if not os.path.exists("modules_custom"):
    try:
        os.mkdir("modules_custom")
    except:
        app = QApplication(sys.argv)
        fm = firstMessage("Error", "Cannot create the modules_custom folder. Exiting...")
        sys.exit(app.exec())

sys.path.append("modules_custom")
mmod_custom = glob.glob("modules_custom/*.py")
list_custom_modules = []
for el in reversed(mmod_custom):
    try:
        ee = importlib.import_module(os.path.basename(el)[:-3])
        list_custom_modules.append(ee)
    except ImportError as ioe:
        app = QApplication(sys.argv)
        fm = firstMessage("Error", "Error while importing the plugin:\n{}".format(str(ioe)))
        sys.exit(app.exec())

if not os.path.exists("icons"):
    app = QApplication(sys.argv)
    fm = firstMessage("Error", "The folder icons doesn't exist. Exiting...")
    sys.exit(app.exec())

#
TCOMPUTER = 0

PKEXEC = "./pkexec.sh"

class clabel2(QLabel):
    def __init__(self, parent=None):
        super(clabel2, self).__init__(parent)
    
    def setText(self, text, wWidth):
        boxWidth = wWidth*QApplication.instance().devicePixelRatio()
        font = self.font()
        metric = QFontMetrics(font)
        string = text
        ctemp = ""
        ctempT = ""
        for cchar in string:
            ctemp += str(cchar)
            # to verify
            # width = metric.width(ctemp)
            # 0 is Qt.TextSingleLine
            width = metric.size(0, ctemp).width()
            if width < boxWidth:
                ctempT += str(cchar)
                continue
            else:
                ctempT += str(cchar)
                ctempT += "\n"
                ctemp = str(cchar)
        ntext = ctempT
        super(clabel2, self).setText(ntext)

# simple dialog message
# type - message - parent
class MyDialog(QMessageBox):
    def __init__(self, *args):
        super(MyDialog, self).__init__(args[-1])
        if args[0] == "Info":
            self.setIcon(QMessageBox.Icon.Information)
            self.setStandardButtons(QMessageBox.StandardButton.Ok)
        elif args[0] == "Error":
            self.setIcon(QMessageBox.Icon.Critical)
            self.setStandardButtons(QMessageBox.StandardButton.Ok)
        elif args[0] == "Question":
            self.setIcon(QMessageBox.Icon.Question)
            self.setStandardButtons(QMessageBox.StandardButton.Ok|QMessageBox.StandardButton.Cancel)
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle(args[0])
        self.resize(dialWidth,100)
        self.setText(args[1])
        retval = self.exec()
    
    def event(self, e):
        result = QMessageBox.event(self, e)
        #
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # 
        return result


# dialog message with info list
class MyMessageBox(QMessageBox):
    def __init__(self, *args):
        super(MyMessageBox, self).__init__(args[-1])
        self.setIcon(QMessageBox.Icon.Information)
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle(args[0])
        self.resize(dialWidth,100)
        self.setText(args[1])
        self.setInformativeText(args[2])
        self.setDetailedText("The details are as follows:\n\n"+args[3])
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        retval = self.exec()
    
    def event(self, e):
        result = QMessageBox.event(self, e)
        #
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        #
        textEdit = self.findChild(QTextEdit)
        if textEdit != None :
            textEdit.setMinimumHeight(0)
            textEdit.setMaximumHeight(16777215)
            textEdit.setMinimumWidth(0)
            textEdit.setMaximumWidth(16777215)
            textEdit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        #
        return result


# renaming dialog - from listview contextual menu - Paste and Merge
class MyDialogRename2(QDialog):
    def __init__(self, *args):
        super(MyDialogRename2, self).__init__(args[-1])
        self.item_name = args[0]
        self.dest_path = args[1]
        self.itemPath = os.path.join(self.dest_path, self.item_name)
        #
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle("Rename")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.resize(dialWidth,100)
        #
        mbox = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        mbox.setContentsMargins(5,5,5,5)
        self.setLayout(mbox)
        #
        label1 = QLabel("Old name:")
        mbox.addWidget(label1)
        #
        label2 = clabel2()
        label2.setText(self.item_name, self.size().width()-12)
        mbox.addWidget(label2)
        #
        label3 = QLabel("New name:")
        mbox.addWidget(label3)
        #
        self.lineedit = QLineEdit()
        self.lineedit.setText(self.item_name)
        self.lineedit.setCursorPosition(0)
        args_basename = QFileInfo(self.item_name).baseName()
        len_args_basename = len(args_basename)
        self.lineedit.setSelection(0 , len_args_basename)
        mbox.addWidget(self.lineedit)
        #
        box = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        mbox.addLayout(box)
        #
        button1 = QPushButton("OK")
        box.addWidget(button1)
        button1.clicked.connect(lambda:self.faccept(self.item_name))
        #
        button3 = QPushButton("Cancel")
        box.addWidget(button3)
        button3.clicked.connect(self.fcancel)
        #
        self.Value = ""
        self.exec()
    
    def getValues(self):
        return self.Value
    
    def faccept(self, item_name):
        newName = self.lineedit.text()
        newName = newName.lstrip(" ").rstrip(" ")
        if newName != "":
            if newName != item_name:
                if not os.path.exists(os.path.join(self.dest_path, newName)):
                    self.Value = newName
                    self.close()
    
    def fcancel(self):
        self.Value = -1
        self.close()
    
            
    # def closeEvent(self, event):
        # self.deleteLater()


# renaming dialog - when a new file is been created
class MyDialogRename3(QDialog):
    def __init__(self, *args):
        super(MyDialogRename3, self).__init__(args[-1])
        #
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle("Set a new name")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.resize(dialWidth,100)
        #
        mbox = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        mbox.setContentsMargins(5,5,5,5)
        self.setLayout(mbox)
        #
        label1 = QLabel("Choose a new name:")
        mbox.addWidget(label1)
        #
        self.lineedit = QLineEdit()
        self.lineedit.setText(args[0])
        self.lineedit.setCursorPosition(0)
        args_basename = QFileInfo(args[0]).baseName()
        len_args_basename = len(args_basename)
        self.lineedit.setSelection(0 , len_args_basename)
        mbox.addWidget(self.lineedit)
        #
        box = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        mbox.addLayout(box)
        #
        button1 = QPushButton("OK")
        box.addWidget(button1)
        button1.clicked.connect(lambda:self.faccept(args[0], args[1]))
        #
        button3 = QPushButton("Cancel")
        box.addWidget(button3)
        button3.clicked.connect(self.fcancel)
        #
        self.Value = ""
        self.exec()

    def getValues(self):
        return self.Value
    
    def faccept(self, item_name, destDir):
        newName = self.lineedit.text()
        newName = newName.lstrip(" ").rstrip(" ")
        if newName != "":
            if not os.path.exists(os.path.join(destDir, newName)):
                self.Value = newName
                self.close()
    
    def fcancel(self):
        self.Value = -1
        self.close()
    
    # def closeEvent(self, event):
        # self.deleteLater()

# dialog - open a file with another program
class otherApp(QDialog):

    def __init__(self, itemPath, parent):
        super(otherApp, self).__init__(parent)
        #
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle("Other application")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.resize(dialWidth,100)
        #
        grid = QGridLayout()
        grid.setContentsMargins(5,5,5,5)
        #
        label1 = QLabel("\nChoose the application:")
        grid.addWidget(label1, 0, 0, Qt.AlignmentFlag.AlignCenter)
        #
        self.lineedit = QLineEdit()
        grid.addWidget(self.lineedit, 1, 0)
        #
        button_box = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        grid.addLayout(button_box, 2, 0)
        #
        button1 = QPushButton("OK")
        button_box.addWidget(button1)
        button1.clicked.connect(self.faccept)
        #
        button3 = QPushButton("Cancel")
        button_box.addWidget(button3)
        button3.clicked.connect(self.fcancel)
        #
        self.setLayout(grid)
        self.Value = -1
        self.exec()
        
    def getValues(self):
        return self.Value
    
    def faccept(self):
        if self.lineedit.text() != "":
            self.Value = self.lineedit.text()
            self.close()
    
    def fcancel(self):
        self.Value = -1
        self.close()
    
    # def closeEvent(self, event):
        # self.deleteLater()

############ create a menu of installed applications
class PlistMenu(QDialog):
    def __init__(self, parent=None):
        super(PlistMenu, self).__init__(parent)
        #
        self.setWindowTitle("Open with...")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.resize(dialWidth, 100)
        #
        vbox = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        vbox.setContentsMargins(5,5,5,5)
        self.setLayout(vbox)
        # treewidget
        self.TWD = QTreeWidget()
        self.TWD.setHeaderLabels(["Applications"])
        self.TWD.setAlternatingRowColors(False)
        self.TWD.itemClicked.connect(self.fitem)
        vbox.addWidget(self.TWD)
        # buttons
        hbox = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        vbox.addLayout(hbox)
        #
        button1 = QPushButton("Ok")
        hbox.addWidget(button1)
        button1.clicked.connect(self.fexecute)
        #
        button2 = QPushButton("Cancel")
        hbox.addWidget(button2)
        button2.clicked.connect(self.fcancel)
        #### the menu
        ## populate the categories
        self.fpopMenu()
        # sort the view
        self.TWD.setSortingEnabled(True)
        self.TWD.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        #
        self.Value = []
        self.exec()

    # create a menu of installed applications
    def fpopMenu(self):
        # main categories
        Development = []
        Education = []
        Game = []
        Graphics = []
        Multimedia = []
        Network = []
        Office = []
        Settings = []
        System = []
        Utility = []
        Other = []
        #
        import Utility.pop_menu as pop_menu
        THE_MENU = pop_menu.getMenu().retList()
        for el in THE_MENU:
            cat = el[1]
            if cat == "Development":
                # name - category - exec - desktop file
                Development.append(["Development",el[0],el[2],el[3]])
            elif cat == "Education":
                Education.append(["Education",el[0],el[2],el[3]])
            elif cat == "Game":
                Game.append(["Game",el[0],el[2],el[3]])
            elif cat == "Graphics":
                Graphics.append(["Graphics",el[0],el[2],el[3]])
            elif cat == "Multimedia":
                Multimedia.append(["Multimedia",el[0],el[2],el[3]])
            elif cat == "Network":
                Network.append(["Network",el[0],el[2],el[3]])
            elif cat == "Office":
                Office.append(["Office",el[0],el[2],el[3]])
            elif cat == "Settings":
                Settings.append(["Settings",el[0],el[2],el[3]])
            elif cat == "System":
                System.append(["System",el[0],el[2],el[3]])
            elif cat == "Utility":
                Utility.append(["Utility",el[0],el[2],el[3]])
            else:
                Other.append(["Other",el[0],el[2],el[3]])
        #
        main_categories = ["Development","Education","Game",
                            "Graphics","Multimedia","Network",
                            "Office","Settings","System","Utility","Other"]
        for ccat in main_categories:
            tl = QTreeWidgetItem([ccat])
            self.TWD.addTopLevelItem(tl)
        #
        # populate the categories
        for ell in [Development,Education,Game,Graphics,Multimedia,Network,Office,Settings,System,Utility,Other]:
            if ell:
                # el: category - name - exec - desktop file
                for el in ell:
                    # find the index of the category in the treeview
                    witem = self.TWD.findItems(el[0], Qt.MatchFlag.MatchExactly, 0)[0]
                    idx = self.TWD.indexOfTopLevelItem(witem)
                    # add the item: name - exec
                    tw_child = QTreeWidgetItem([el[1], el[2], el[3]])
                    witem.addChild(tw_child)

    # an item in the treewidget is clicked
    def fitem(self, item, col):
        # exec - desktop file
        self.Value = [item.text(1), item.text(2)]
    
    def getValue(self):
        return self.Value
    
    def fexecute(self):
        self.close()
    
    def fcancel(self):
        self.Value = -1
        self.close()
    
    # def closeEvent(self, event):
        # self.deleteLater()


# calculate the folder size 
def folder_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for fl in filenames:
            flp = os.path.join(dirpath, fl)
            if os.access(flp, os.R_OK):
                if os.path.islink(flp):
                    continue
                total_size += os.path.getsize(flp)
    return total_size

# total size of the items in the list
def listTotSize(newList):
    total_size = 0
    skipped = ""
    for sitem in newList:
        try:
            if os.path.islink(sitem):
                # just a number
                total_size += 512
            elif os.path.isfile(sitem):
                item_size = QFileInfo(sitem).size()
                total_size += max(item_size, 512)
            elif os.path.isdir(sitem):
                item_size = self.folder_size(sitem)
                total_size += max(item_size, 512)
        except:
            skipped += sitem+"\n"
    #
    return total_size

def dest_size_free(path):
    disc_size_free = shutil.disk_usage(path).free
    return disc_size_free

def check_free_disc_space(path, dest):
    total_items_size = listTotSize(path)
    disc_free = dest_size_free(dest)
    return (disc_free > total_items_size)

def convert_size(fsize2):
    if fsize2 == 0 or fsize2 == 1:
        sfsize = str(fsize2)+" byte"
    elif fsize2//1024 == 0:
        sfsize = str(fsize2)+" bytes"
    elif fsize2//1048576 == 0:
        sfsize = str(round(fsize2/1024, 3))+" KB"
    elif fsize2//1073741824 == 0:
        sfsize = str(round(fsize2/1048576, 3))+" MB"
    elif fsize2//1099511627776 == 0:
        sfsize = str(round(fsize2/1073741824, 3))+" GiB"
    else:
        sfsize = str(round(fsize2/1099511627776, 3))+" GiB"
    return sfsize  


# property dialog for one item
class propertyDialog(QDialog):
    def __init__(self, itemPath, parent):
        super(propertyDialog, self).__init__(parent)
        self.itemPath = itemPath
        self.window = parent
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        #
        self.imime = ""
        self.imime = QMimeDatabase().mimeTypeForFile(self.itemPath, QMimeDatabase.MatchMode.MatchDefault)
        # the program pkexec/pkexec.sh is used
        self.CAN_CHANGE_OWNER = 1
        if PKEXEC_PROG == 1:
            if not shutil.which("pkexec"):
                self.CAN_CHANGE_OWNER = 0
        #
        storageInfoIsReadOnly = 1
        if os.path.exists(os.path.realpath(self.itemPath)):
            if stat.S_ISREG(os.stat(self.itemPath).st_mode) or stat.S_ISDIR(os.stat(self.itemPath).st_mode) or stat.S_ISLNK(os.stat(self.itemPath).st_mode):
                try:
                    storageInfo = QStorageInfo(self.itemPath)
                    storageInfoIsReadOnly = storageInfo.isReadOnly()
                except:
                    pass
            else:
                if os.access(os.path.dirname(self.itemPath), os.W_OK):
                    storageInfoIsReadOnly = 0
        else:
            if os.access(os.path.dirname(self.itemPath), os.W_OK):
                storageInfoIsReadOnly = 0
        #
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle("Property")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.resize(dialWidth, 100)
        #
        vbox = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        vbox.setContentsMargins(5,5,5,5)
        self.setLayout(vbox)
        #
        self.gtab = QTabWidget()
        self.gtab.setContentsMargins(5,5,5,5)
        self.gtab.setMovable(False)
        self.gtab.setElideMode(Qt.TextElideMode.ElideRight)
        self.gtab.setTabsClosable(False)
        vbox.addWidget(self.gtab)
        #
        page1 = QWidget()
        self.gtab.addTab(page1, "General")
        self.grid1 = QGridLayout()
        page1.setLayout(self.grid1)
        #
        labelName = QLabel("<i>Name</i>")
        self.grid1.addWidget(labelName, 0, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.labelName2 = clabel2()
        self.labelName2.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.grid1.addWidget(self.labelName2, 0, 1, 1, 4, Qt.AlignmentFlag.AlignLeft)
        #
        labelMime = QLabel("<i>MimeType</i>")
        self.grid1.addWidget(labelMime, 2, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.labelMime2 = QLabel()
        self.grid1.addWidget(self.labelMime2, 2, 1, 1, 4, Qt.AlignmentFlag.AlignLeft)
        #
        if os.path.isfile(itemPath) or os.path.isdir(itemPath):
            labelOpenWith = QLabel("<i>Open With...</i>")
            self.grid1.addWidget(labelOpenWith, 3, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.btnOpenWith = QPushButton("----------")
            self.btnOpenWith.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            self.btnOpenWith.clicked.connect(self.fbtnOpenWith)
            self.grid1.addWidget(self.btnOpenWith, 3, 1, 1, 4, Qt.AlignmentFlag.AlignLeft)
            self.btnOpenWithPopulate()
        #
        labelSize = QLabel("<i>Size</i>")
        self.grid1.addWidget(labelSize, 4, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.labelSize2 = QLabel()
        self.grid1.addWidget(self.labelSize2, 4, 1, 1, 4, Qt.AlignmentFlag.AlignLeft)
        #
        if not os.path.exists(self.itemPath):
            if os.path.islink(self.itemPath):
                self.labelName2.setText(os.path.basename(self.itemPath), self.size().width()-12)
                self.labelMime2.setText("Broken link")
                labelSize.hide()
                self.labelSize2.hide()
                label_real_link = QLabel("<i>To Path</i>")
                self.grid1.addWidget(label_real_link, 5, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
                label_real_link2 = clabel2()
                label_real_link2.setText(os.path.realpath(self.itemPath), self.size().width()-12)
                self.grid1.addWidget(label_real_link2, 5, 1, 1, 4, Qt.AlignmentFlag.AlignLeft)
                #
                button1 = QPushButton("OK")
                button1.clicked.connect(self.faccept)
                hbox = QBoxLayout(QBoxLayout.Direction.LeftToRight)
                vbox.addLayout(hbox)
                hbox.addWidget(button1)
                self.adjustSize()
                #
                self.exec()
        elif os.path.exists(self.itemPath):
            if os.path.islink(self.itemPath):
                label_real_link = QLabel("<i>To Path</i>")
                self.grid1.addWidget(label_real_link, 5, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
                label_real_link2 = clabel2()
                label_real_link2.setText(os.path.realpath(self.itemPath), self.size().width()-12)
                self.grid1.addWidget(label_real_link2, 5, 1, 1, 4, Qt.AlignmentFlag.AlignLeft)
            #
            labelCreation = QLabel("<i>Creation</i>")
            self.grid1.addWidget(labelCreation, 6, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.labelCreation2 = QLabel()
            self.grid1.addWidget(self.labelCreation2, 6, 1, 1, 4, Qt.AlignmentFlag.AlignLeft)
            #
            labelModification = QLabel("<i>Modification</i>")
            self.grid1.addWidget(labelModification, 7, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.labelModification2 = QLabel()
            self.grid1.addWidget(self.labelModification2, 7, 1, 1, 4, Qt.AlignmentFlag.AlignLeft)
            #
            labelAccess = QLabel("<i>Access</i>")
            self.grid1.addWidget(labelAccess, 8, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.labelAccess2 = QLabel()
            self.grid1.addWidget(self.labelAccess2, 8, 1, 1, 4, Qt.AlignmentFlag.AlignLeft)
            # disc usage
            num_partitions = len(psutil.disk_partitions())
            file_mountpoint = ""
            data_mountpoint = None
            if num_partitions == 1:
                data_mountpoint = psutil.disk_partitions()[0]
                file_mountpoint = data_mountpoint.mountpoint
            else:
                for ppart in psutil.disk_partitions():
                    if ppart.mountpoint == "/":
                        continue
                    p_mount_point = ppart.mountpoint+"/"
                    if self.itemPath[0:len(p_mount_point)] == p_mount_point:
                        data_mountpoint = ppart
                        file_mountpoint = ppart.mountpoint
            if data_mountpoint == None:
                for ppart in psutil.disk_partitions():
                    if ppart.mountpoint == "/":
                        data_mountpoint = ppart
                        file_mountpoint = "/"
                        break
            if file_mountpoint == "/":
                file_mountpoint = "Root"
            elif file_mountpoint == "/boot":
                file_mountpoint = "Boot"
            elif file_mountpoint == "/home":
                file_mountpoint = "Home"
            label_partition = QLabel("<i>Disc {}</i>".format(file_mountpoint))
            self.grid1.addWidget(label_partition, 9, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
            label_partition2 = QLabel()
            disc_size = convert_size(psutil.disk_usage(data_mountpoint.mountpoint).total)
            disc_used = convert_size(psutil.disk_usage(data_mountpoint.mountpoint).used)
            label_partition2.setText("{} / {}".format(disc_size, disc_used))
            self.grid1.addWidget(label_partition2, 9, 1, 1, 4, Qt.AlignmentFlag.AlignLeft)
            ###### tab 2
            page2 = QWidget()
            self.gtab.addTab(page2, "Permissions")
            vboxp2 = QBoxLayout(QBoxLayout.Direction.TopToBottom)
            page2.setLayout(vboxp2)
            #
            gBox1 = QGroupBox("Ownership")
            vboxp2.addWidget(gBox1)
            self.grid2 = QGridLayout()
            gBox1.setLayout(self.grid2)
            #
            labelgb11 = QLabel("<i>Owner</i>")
            self.grid2.addWidget(labelgb11, 0, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.labelgb12 = QLabel()
            self.grid2.addWidget(self.labelgb12, 0, 1, 1, 5, Qt.AlignmentFlag.AlignLeft)
            #
            labelgb21 = QLabel("<i>Group</i>")
            self.grid2.addWidget(labelgb21, 1, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.labelgb22 = QLabel()
            self.grid2.addWidget(self.labelgb22, 1, 1, 1, 5, Qt.AlignmentFlag.AlignLeft)
            #
            gBox2 = QGroupBox("Permissions")
            vboxp2.addWidget(gBox2)
            self.grid3 = QGridLayout()
            gBox2.setLayout(self.grid3)
            if storageInfoIsReadOnly:
                gBox2.setEnabled(False)
            #
            labelOwnerPerm = QLabel("<i>Owner</i>")
            self.grid3.addWidget(labelOwnerPerm, 0, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.combo1 = QComboBox()
            self.combo1.addItems(["Read and Write", "Read", "Forbidden"])
            self.grid3.addWidget(self.combo1, 0, 1, 1, 5, Qt.AlignmentFlag.AlignLeft)
            #
            labelGroupPerm = QLabel("<i>Group</i>")
            self.grid3.addWidget(labelGroupPerm, 1, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.combo2 = QComboBox()
            self.combo2.addItems(["Read and Write", "Read", "Forbidden"])
            self.grid3.addWidget(self.combo2, 1, 1, 1, 5, Qt.AlignmentFlag.AlignLeft)
            #
            labelOtherPerm = QLabel("<i>Others</i>")
            self.grid3.addWidget(labelOtherPerm, 2, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.combo3 = QComboBox()
            self.combo3.addItems(["Read and Write", "Read", "Forbidden"])
            self.grid3.addWidget(self.combo3, 2, 1, 1, 5, Qt.AlignmentFlag.AlignLeft)
            #
            self.combo1.activated.connect(self.fcombo1)
            self.combo2.activated.connect(self.fcombo2)
            self.combo3.activated.connect(self.fcombo3)
            #
            # change owner button
            self.own_btn = QPushButton("Change")
            if self.CAN_CHANGE_OWNER:
                self.own_btn.clicked.connect(lambda:self.on_change_owner(me = os.path.basename(os.getenv("HOME"))))
            self.grid2.addWidget(self.own_btn, 0, 6, 1, 1, Qt.AlignmentFlag.AlignLeft)
            # change group button
            self.grp_btn = QPushButton("Change")
            if self.CAN_CHANGE_OWNER:
                self.grp_btn.clicked.connect(lambda:self.on_change_grp(me = os.path.basename(os.getenv("HOME"))))
            self.grid2.addWidget(self.grp_btn, 1, 6, 1, 1, Qt.AlignmentFlag.AlignLeft)
            # folder access - file executable
            self.cb1 = QCheckBox()
            ## set the initial state
            fileInfo = QFileInfo(self.itemPath)
            perms = fileInfo.permissions()
            # folder access - file execution
            if perms & QFile.Permission.ExeOwner:
                self.cb1.setChecked(True)
            #
            self.cb1.stateChanged.connect(self.fcb1)
            self.grid3.addWidget(self.cb1, 4, 0, 1, 5, Qt.AlignmentFlag.AlignLeft)
            # immutable file button
            self.ibtn = QPushButton()
            self.ibtn.clicked.connect(self.ibtn_pkexec)
            self.grid3.addWidget(self.ibtn, 4, 6, 1, 1, Qt.AlignmentFlag.AlignLeft)
            if not self.CAN_CHANGE_OWNER:
                self.ibtn.setEnabled(False)
            #
            button1 = QPushButton("OK")
            button1.clicked.connect(self.faccept)
            #
            hbox = QBoxLayout(QBoxLayout.Direction.LeftToRight)
            vbox.addLayout(hbox)
            hbox.addWidget(button1)
            # populate all
            self.tab()
            self.adjustSize()
            self.exec()
    
    #
    # def comboOpenWithPopulate(self):
    def btnOpenWithPopulate(self):
        self.defApp = getDefaultApp(self.itemPath).defaultApplication()
        listPrograms_temp = getAppsByMime(self.itemPath).appByMime()
        #
        for iprog in listPrograms_temp:
            if iprog[0] == self.defApp or iprog[0] == self.defApp.split("/")[-1]:
                self.btnOpenWith.setText(iprog[1])
                return
        #    else:
        self.btnOpenWith.setText("----------")
    
    
    # see comboOpenWithPopulate
    def fbtnOpenWith(self):
        if self.imime or not self.imime.isNull():
            from Utility import assmimeL as AL
            if self.imime.name() in ["application/x-zerosize", "application/x-trash", "application/x-desktop"]:
                self.AW = AL.MainWin("text/plain", self)
            else:
                self.AW = AL.MainWin(self.imime.name(), self)
            if self.AW.exec() == QDialog.DialogCode.Accepted:
                ret = self.AW.getValue()
                if ret:
                    self.btnOpenWithPopulate()
        
        
    # set or unset the immutable flag
    def ibtn_pkexec(self):
        # unset
        if "i" in subprocess.check_output(['lsattr', self.itemPath]).decode()[:19]:
            # ret = None
            try:
                if PKEXEC_PROG == 1:
                    ret = subprocess.run(["pkexec", "chattr", "-i", self.itemPath])
                elif PKEXEC_PROG == 2:
                    # subprocess.run([PKEXEC, "2", self.itemPath])
                    passWord(self.itemPath, 2, None)
            except:
                pass
            # # if success
            # if ret:
                # if ret.returncode == 0:
            try:
                if "i" not in subprocess.check_output(['lsattr', self.itemPath]).decode()[:19]:
                    self.ibtn.setText("Not Immutable")
            except:
                pass
        # set
        else:
            # SYS_PASSWORD = passWord("archive_name", None).arpass
            # if not SYS_PASSWORD:
                # MyDialog("Info", "Cancelled.", None)
                # return
            # else:
                # return
            # ret = None
            try:
                if PKEXEC_PROG == 1:
                    ret = subprocess.run(["pkexec", "chattr", "+i", self.itemPath])
                elif PKEXEC_PROG == 2:
                    # subprocess.run([PKEXEC, "1", self.itemPath])
                    passWord(self.itemPath, 1, None)
            except:
                pass
            # # if success
            # if ret:
                # if ret.returncode == 0:
            try:
                if "i" in subprocess.check_output(['lsattr', self.itemPath]).decode()[:19]:
                    self.ibtn.setText("Immutable")
            except:
                pass
        # repopulate
        self.tab()
        
    
    # populate the property dialog
    def tab(self):
        # folder access - file executable
        if os.path.isdir(self.itemPath):
            self.cb1.setText('folder access')
        elif os.path.isfile(self.itemPath):
            self.cb1.setText('Executable')
        else:
            self.cb1.setText('Executable')
        #
        # set or unset the immutable flag
        if self.CAN_CHANGE_OWNER:
            if os.access(self.itemPath, os.R_OK):
                if os.path.isfile(self.itemPath) and not os.path.islink(self.itemPath):
                    try:
                        if "i" in subprocess.check_output(['lsattr', self.itemPath]).decode()[:19]:
                            self.ibtn.setText("Immutable")
                        else:
                            self.ibtn.setText("Not Immutable")
                    except:
                        self.ibtn.setEnabled(False)
                        self.ibtn.hide()
                else:
                    self.ibtn.setEnabled(False)
                    self.ibtn.hide()
            else:
                self.ibtn.setEnabled(False)
                self.ibtn.hide()
        else:
            self.ibtn.setEnabled(False)
            self.ibtn.hide()
        #
        fileInfo = QFileInfo(self.itemPath)
        self.labelName2.setText(fileInfo.fileName(), self.size().width()-12)
        self.labelMime2.setText(self.imime.name())
        #
        if not os.path.exists(self.itemPath):
            if os.path.islink(self.itemPath):
                self.labelSize2.setText("(Broken Link)")
            else:
                self.labelSize2.setText("Unrecognizable")
        if os.path.isfile(self.itemPath):
            if os.access(self.itemPath, os.R_OK):
                self.labelSize2.setText(convert_size(QFileInfo(self.itemPath).size()))
            else:
                self.labelSize2.setText("(Not readable)")
        elif os.path.isdir(self.itemPath):
            if os.access(self.itemPath, os.R_OK):
                self.labelSize2.setText(str(convert_size(folder_size(self.itemPath))))
            else:
                self.labelSize2.setText("(Not readable)")
        else:
            self.labelSize2.setText("0")
        #
        if os.path.exists(self.itemPath):
            if DATE_TIME == 0:
                mctime = datetime.datetime.fromtimestamp(os.stat(self.itemPath).st_ctime).strftime('%c')
            elif DATE_TIME == 1:
                try:
                    mctime1 = subprocess.check_output(["stat", "-c", "%W", self.itemPath], universal_newlines=False).decode()
                    mctime2 = subprocess.check_output(["date", "-d", "@{}".format(mctime1)], universal_newlines=False).decode()
                    mctime = mctime2.strip("\n")
                except:
                    mctime = datetime.datetime.fromtimestamp(os.stat(self.itemPath).st_ctime).strftime('%c')
            #
            mmtime = datetime.datetime.fromtimestamp(os.stat(self.itemPath).st_mtime).strftime('%c')
            matime = datetime.datetime.fromtimestamp(os.stat(self.itemPath).st_atime).strftime('%c')
            #
            self.labelCreation2.setText(str(mctime))
            self.labelModification2.setText(str(mmtime))
            self.labelAccess2.setText(str(matime))
            #
            self.labelgb12.setText(fileInfo.owner())
            self.labelgb22.setText(fileInfo.group())
            # file owner
            if self.CAN_CHANGE_OWNER:
                me = os.path.basename(os.getenv("HOME"))
                if me != fileInfo.owner():
                    self.own_btn.setEnabled(True)
                else:
                    self.own_btn.setEnabled(False)
            else:
                self.own_btn.setEnabled(False)
            # file group
            if self.CAN_CHANGE_OWNER:
                me = os.path.basename(os.getenv("HOME"))
                if me != fileInfo.group():
                    self.grp_btn.setEnabled(True)
                else:
                    self.grp_btn.setEnabled(False)
            else:
                self.grp_btn.setEnabled(False)
            #####
            perms = fileInfo.permissions()
            # folder access - file execution
            if perms & QFile.Permission.ExeOwner:
                if not self.cb1.checkState():
                    self.cb1.setChecked(True)
            #
            nperm = self.fgetPermissions()
            #
            if nperm[0] + nperm[1] + nperm[2] in [6, 7]:
                self.combo1.setCurrentIndex(0)
            elif nperm[0] + nperm[1] + nperm[2] in [4, 5]:
                self.combo1.setCurrentIndex(1)
            else:
                self.combo1.setCurrentIndex(2)
            #
            if nperm[3] + nperm[4] + nperm[5] in [6, 7]:
                self.combo2.setCurrentIndex(0)
            elif nperm[3] + nperm[4] + nperm[5] in [4, 5]:
                self.combo2.setCurrentIndex(1)
            else:
                self.combo2.setCurrentIndex(2)
            #
            if nperm[6] + nperm[7] + nperm[8] in [6, 7]:
                self.combo3.setCurrentIndex(0)
            elif nperm[6] + nperm[7] + nperm[8] in [4, 5]:
                self.combo3.setCurrentIndex(1)
            else:
                self.combo3.setCurrentIndex(2)
    
    
    # change the owner to me
    def on_change_owner(self, me):
        # ret = None
        try:
            if PKEXEC_PROG == 1:
                ret = subprocess.run(["pkexec", "chown", me, self.itemPath])
            elif PKEXEC_PROG == 2:
                # subprocess.run([PKEXEC, "3", self.itemPath])
                passWord(self.itemPath, 3, None)
        except:
            pass
        # # if success
        # if ret:
            # if ret.returncode == 0:
        self.tab()
    
    # 
    # change the group to mine
    def on_change_grp(self, me):
        # ret = None
        try:
            if PKEXEC_PROG == 1:
                ret = subprocess.run(["pkexec", "chgrp", me, self.itemPath])
            elif PKEXEC_PROG == 2:
                # subprocess.run([PKEXEC, "4", self.itemPath])
                passWord(self.itemPath, 4, None)
        except:
            pass
        # # if success
        # if ret:
            # if ret.returncode == 0:
        self.tab()
    
    def tperms(self, perms):
        tperm = ""
        tperm = str(perms[0] + perms[1] + perms[2])+str(perms[3] + perms[4] + perms[5])+str(perms[6] + perms[7] + perms[8])
        return tperm
    
    # folder access - file executable
    def fcb1(self, state):
        perms = self.fgetPermissions()
        #
        if state == 2:
            perms[2] = 1
            perms[5] = 1
            perms[8] = 1
            tperm =self.tperms(perms)
            try:
                os.chmod(self.itemPath, int("{}".format(int(tperm)), 8))
            except Exception as E:
                MyDialog("Error", str(E), self.window)
        else:
            perms[2] = 0
            perms[5] = 0
            perms[8] = 0
            tperm =self.tperms(perms)
            try:
                os.chmod(self.itemPath, int("{}".format(int(tperm)), 8))
            except Exception as E:
                MyDialog("Error", str(E), self.window)
        # repopulate
        self.tab()
    
    # 
    def fcombo1(self, index):
        perms = self.fgetPermissions()
        if index == 0:
            perms[0] = 4
            perms[1] = 2
        elif index == 1: 
            perms[0] = 4
            perms[1] = 0
        elif index == 2:
            perms[0] = 0
            perms[1] = 0
        #
        tperm = self.tperms(perms)
        try:
            os.chmod(self.itemPath, int("{}".format(tperm), 8))
        except Exception as E:
            MyDialog("Error", str(E), self.window)
        # repopulate
        self.tab()
    
    def fcombo2(self, index):
        perms = self.fgetPermissions()
        if index == 0:
            perms[3] = 4
            perms[4] = 2
        elif index == 1: 
            perms[3] = 4
            perms[4] = 0
        elif index == 2:
            perms[3] = 0
            perms[4] = 0

        tperm = self.tperms(perms)
        try:
            os.chmod(self.itemPath, int("{}".format(tperm), 8))
        except Exception as E:
            MyDialog("Error", str(E), self.window)
        # repopulate
        self.tab()
    
    def fcombo3(self, index):
        perms = self.fgetPermissions()
        if index == 0:
            perms[6] = 4
            perms[7] = 2
        elif index == 1: 
            perms[6] = 4
            perms[7] = 0
        elif index == 2:
            perms[6] = 0
            perms[7] = 0

        tperm = self.tperms(perms)
        try:
            os.chmod(self.itemPath, int("{}".format(tperm), 8))
        except Exception as E:
            MyDialog("Error", str(E), self.window)
        # repopulate
        self.tab()


    def fgetPermissions(self):
        perms = QFile(self.itemPath).permissions()
        # 
        permissions = []
        #
        if perms & QFile.Permission.ReadOwner:
            permissions.append(4)
        else:
            permissions.append(0)
        if perms & QFile.Permission.WriteOwner:
            permissions.append(2)
        else:
            permissions.append(0)
        if perms & QFile.Permission.ExeOwner:
            permissions.append(1)
        else:
            permissions.append(0)
        #
        if perms & QFile.Permission.ReadGroup:
            permissions.append(4)
        else:
            permissions.append(0)
        if perms & QFile.Permission.WriteGroup:
            permissions.append(2)
        else:
            permissions.append(0)
        if perms & QFile.Permission.ExeGroup:
            permissions.append(1)
        else:
            permissions.append(0)
        #
        if perms & QFile.Permission.ReadOther:
            permissions.append(4)
        else:
            permissions.append(0)
        if perms & QFile.Permission.WriteOther:
            permissions.append(2)
        else:
            permissions.append(0)
        if perms & QFile.Permission.ExeOther:
            permissions.append(1)
        else:
            permissions.append(0)
        #
        return permissions
    
    def faccept(self):
        self.close()
    
    # def closeEvent(self, event):
        # self.deleteLater()


# property dialog for more than one item
class propertyDialogMulti(QDialog):
    def __init__(self, item_list, total_size, parent):
        super(propertyDialogMulti, self).__init__(parent)
        #
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle("Property")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.resize(dialWidth, 100)
        #
        self.item_list = item_list
        self.window = parent
        #
        vbox = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        vbox.setContentsMargins(5,5,5,5)
        self.setLayout(vbox)
        #
        self.gtab = QTabWidget()
        self.gtab.setContentsMargins(5,5,5,5)
        self.gtab.setMovable(False)
        self.gtab.setElideMode(Qt.TextElideMode.ElideRight)
        self.gtab.setTabsClosable(False)
        vbox.addWidget(self.gtab)
        #
        page1 = QWidget()
        self.gtab.addTab(page1, "General")
        self.grid1 = QGridLayout()
        page1.setLayout(self.grid1)
        #
        ####### tab 1
        self.grid1.setRowStretch(0, 1)
        # label1 = QLabel("<i>Number of items&nbsp;&nbsp;&nbsp;</i> {}".format(itemNum))
        # vbox.addWidget(label1)
        label1 = QLabel("<i>Number of items&nbsp;&nbsp;&nbsp;</i>")
        self.grid1.addWidget(label1, 1, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
        label1a = QLabel(str(len(self.item_list)))
        self.grid1.addWidget(label1a, 1, 1, 1, 4, Qt.AlignmentFlag.AlignLeft)
        #
        # label2 = QLabel("<i>Total size of the items&nbsp;&nbsp;&nbsp;</i> {}".format(itemSize))
        # vbox.addWidget(label2)
        label2 = QLabel("<i>Total size&nbsp;&nbsp;&nbsp;</i>")
        self.grid1.addWidget(label2, 2, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
        label2a = QLabel(str(total_size))
        self.grid1.addWidget(label2a, 2, 1, 1, 4, Qt.AlignmentFlag.AlignLeft)
        #
        self.grid1.setRowStretch(3, 1)
        ##### tab 2
        page2 = QWidget()
        self.gtab.addTab(page2, "Permissions")
        vboxp2 = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        page2.setLayout(vboxp2)
        ##
        gBox1 = QGroupBox("Ownership")
        vboxp2.addWidget(gBox1)
        self.grid2 = QGridLayout()
        gBox1.setLayout(self.grid2)
        ##
        labelgb11 = QLabel("<i>Owner</i>")
        self.grid2.addWidget(labelgb11, 0, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.labelgb12 = QLabel("Change to: "+os.path.basename(os.getenv("HOME")))
        self.grid2.addWidget(self.labelgb12, 0, 1, 1, 5, Qt.AlignmentFlag.AlignLeft)
        ##
        labelgb21 = QLabel("<i>Group</i>")
        self.grid2.addWidget(labelgb21, 1, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.labelgb22 = QLabel("Change to: "+os.path.basename(os.getenv("HOME")))
        self.grid2.addWidget(self.labelgb22, 1, 1, 1, 5, Qt.AlignmentFlag.AlignLeft)
        ## change owner button
        self.own_btn = QPushButton("Change")
        self.own_btn.setCheckable(True)
        # if self.CAN_CHANGE_OWNER:
            # self.own_btn.clicked.connect(lambda:self.on_change_owner(me = os.path.basename(os.getenv("HOME"))))
        self.grid2.addWidget(self.own_btn, 0, 6, 1, 1, Qt.AlignmentFlag.AlignLeft)
        ## change group button
        self.grp_btn = QPushButton("Change")
        self.grp_btn.setCheckable(True)
        # if self.CAN_CHANGE_OWNER:
            # self.grp_btn.clicked.connect(lambda:self.on_change_grp(me = os.path.basename(os.getenv("HOME"))))
        self.grid2.addWidget(self.grp_btn, 1, 6, 1, 1, Qt.AlignmentFlag.AlignLeft)
        #
        ## apply the modifications 1
        button1 = QPushButton("Apply")
        # vbox.addWidget(button1)
        self.grid2.addWidget(button1, 2, 0, 1, 8, Qt.AlignmentFlag.AlignCenter)
        button1.clicked.connect(self._apply1)
        ##
        gBox2 = QGroupBox("Permissions")
        vboxp2.addWidget(gBox2)
        self.grid3 = QGridLayout()
        gBox2.setLayout(self.grid3)
        # if storageInfoIsReadOnly:
            # gBox2.setEnabled(False)
        ##
        labelOwnerPerm = QLabel("<i>Owner</i>")
        self.grid3.addWidget(labelOwnerPerm, 0, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.combo1 = QComboBox()
        # self.combo1.addItems(["Read and Write", "Read", "Forbidden"])
        self.combo1.addItems(["Read and Write", "Read"])
        self.combo1.setCurrentIndex(0)
        self.grid3.addWidget(self.combo1, 0, 1, 1, 5, Qt.AlignmentFlag.AlignLeft)
        self.btna1 = QPushButton("Apply")
        self.btna1.clicked.connect(lambda:self._apply2(1))
        self.grid3.addWidget(self.btna1, 0, 1, 1, 6, Qt.AlignmentFlag.AlignRight)
        ##
        labelGroupPerm = QLabel("<i>Group</i>")
        self.grid3.addWidget(labelGroupPerm, 1, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.combo2 = QComboBox()
        self.combo2.addItems(["Read and Write", "Read", "Forbidden"])
        self.combo2.setCurrentIndex(0)
        self.grid3.addWidget(self.combo2, 1, 1, 1, 5, Qt.AlignmentFlag.AlignLeft)
        # self.btna2 = QPushButton("Apply")
        # self.btna2.clicked.connect(lambda:self._apply2(2))
        # self.grid3.addWidget(self.btna2, 1, 1, 1, 6, Qt.AlignmentFlag.AlignRight)
        ##
        labelOtherPerm = QLabel("<i>Others</i>")
        self.grid3.addWidget(labelOtherPerm, 2, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.combo3 = QComboBox()
        self.combo3.addItems(["Read and Write", "Read", "Forbidden"])
        self.combo3.setCurrentIndex(0)
        self.grid3.addWidget(self.combo3, 2, 1, 1, 5, Qt.AlignmentFlag.AlignLeft)
        # self.btna3 = QPushButton("Apply")
        # self.btna3.clicked.connect(lambda:self._apply2(3))
        # self.grid3.addWidget(self.btna3, 2, 1, 1, 6, Qt.AlignmentFlag.AlignRight)
        #
        # self.combo1.activated.connect(self.fcombo1)
        # self.combo2.activated.connect(self.fcombo2)
        # self.combo3.activated.connect(self.fcombo3)
        #
        #
        gBox3 = QGroupBox("Other permissions")
        vboxp2.addWidget(gBox3)
        self.grid4 = QGridLayout()
        gBox3.setLayout(self.grid4)
        ## folder access - file executable
        self.cb1 = QCheckBox()
        self.cb1.setText("Toggle executable")
        ## set the initial state
        # fileInfo = QFileInfo(self.itemPath)
        # perms = fileInfo.permissions()
        # folder access - file execution
        # if perms & QFile.Permission.ExeOwner:
            # self.cb1.setChecked(True)
        #
        # self.cb1.stateChanged.connect(self.fcb1)
        self.grid4.addWidget(self.cb1, 4, 0, 1, 5, Qt.AlignmentFlag.AlignLeft)
        ## immutable file button
        self.ibtn = QPushButton("Toggle immutable")
        self.ibtn.setCheckable(True)
        # self.ibtn.clicked.connect(self.ibtn_pkexec)
        self.grid4.addWidget(self.ibtn, 4, 6, 1, 1, Qt.AlignmentFlag.AlignLeft)
        # if not self.CAN_CHANGE_OWNER:
            # self.ibtn.setEnabled(False)
        ## apply the modifications 2
        button2 = QPushButton("Apply")
        # vbox.addWidget(button1)
        self.grid4.addWidget(button2, 5, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        button2.clicked.connect(lambda:self._apply2(4))
        ##
        button3 = QPushButton("Apply")
        # vbox.addWidget(button1)
        self.grid4.addWidget(button3, 5, 6, 1, 1, Qt.AlignmentFlag.AlignCenter)
        button3.clicked.connect(lambda:self._apply2(5))
        ###
        button1 = QPushButton("OK")
        button1.clicked.connect(self.faccept)
        #
        hbox = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        vbox.addLayout(hbox)
        hbox.addWidget(button1)
        #
        self.exec()
    
    #
    def _apply1(self):
        _set_own = 0
        _set_grp = 0
        if self.own_btn.isChecked():
            _set_own = 1
        if self.grp_btn.isChecked():
            _set_grp = 1
        #
        ret = 0
        if _set_own == 1 or _set_grp == 1:
            _ret = retDialogBox2("Apply the changes?\n", self)
            ret = _ret.getValue()
        #
        if ret:
            _list = ""
            for item in self.item_list:
                if _list:
                    _list += " "
                _list += "'"+item+"'"
            try:
                if PKEXEC_PROG == 1:
                    if not shutil.which("pkexec"):
                        MyDialog("Error", "pkexec not found",None)
                        return
                    comm = 'pkexec sh -c "chown linux {}"'.format(_list)
                    ret = os.system(comm)
                    if ret != 0:
                        MyDialog("Error", "Error with some items.", None)
                # elif PKEXEC_PROG == 2:
                    # # subprocess.run([PKEXEC, "3", self.itemPath])
                    # passWord(self.itemPath, 3, None)
            except Exception as E:
                MyDialog("Error", str(E), None)
        
    
    def _apply2(self, _t):
        _ret = retDialogBox2("Apply the changes?\n", self)
        ret = _ret.getValue()
        if ret != 1:
            return
        #
        _btn = 0
        # permissions
        if _t == 1:
            _idx1 = self.combo1.currentIndex()
            _idx2 = self.combo2.currentIndex()
            _idx3 = self.combo3.currentIndex()
            #
            if _idx1 == 0:
                _btn = 600
            elif _idx1 == 1:
                _btn = 400
            #
            if _idx2 == 0:
                _btn += 60
            elif _idx2 == 1:
                _btn += 40
            #
            if _idx3 == 0:
                _btn += 6
            elif _idx3 == 1:
                _btn += 4
        #
        elif _t == 4:
            # executable
            if self.cb1.isChecked():
                _btn = 4
            elif not self.cb1.isChecked():
                _btn = 41
        elif _t == 5:
            # immutable
            if self.ibtn.isChecked():
                _btn = 5
            elif not self.ibtn.isChecked():
                _btn = 6
        #
        _items_failure = []
        _num_items_failure = 0
        # limit the number of items to report
        _num_i_f = 20
        # executable
        if _btn == 4:
            for item in self.item_list:
                try:
                    if os.path.islink(item) or os.path.isdir(item):
                        continue
                    comm = "chmod u+x '{}'".format(item)
                    ret = os.system(comm)
                    if ret != 0:
                        if _num_items_failure < _num_i_f:
                            _items_failure.append([str(item)])
                        _num_items_failure += 1
                except Exception as E:
                    if _num_items_failure < _num_i_f:
                        _items_failure.append([str(item)+" : "+str(E)])
                    _num_items_failure += 1
        elif _btn == 41:
            for item in self.item_list:
                try:
                    if os.path.islink(item) or os.path.isdir(item):
                        continue
                    comm = "chmod u-x '{}'".format(item)
                    ret = os.system(comm)
                    if ret != 0:
                        if _num_items_failure < _num_i_f:
                            _items_failure.append([str(item)])
                        _num_items_failure += 1
                except Exception as E:
                    if _num_items_failure < _num_i_f:
                        _items_failure.append([str(item)+" : "+str(E)])
                    _num_items_failure += 1
        # immutable
        elif _btn == 5:
            _list = ""
            for item in self.item_list:
                if _list:
                    _list += " "
                _list += "'"+item+"'"
            try:
                comm = 'pkexec sh -c "chattr +i {}"'.format(_list)
                ret = os.system(comm)
                if ret != 0:
                    if _num_items_failure < _num_i_f:
                        _items_failure.append([str(item)])
                    _num_items_failure += 1
            except Exception as E:
                if _num_items_failure < _num_i_f < 20:
                    _items_failure.append(["Toggle immutable: "+str(E)])
                _num_items_failure += 1
        elif  _btn == 6:
            _list = ""
            for item in self.item_list:
                if _list:
                    _list += " "
                _list += "'"+item+"'"
            try:
                comm = 'pkexec sh -c "chattr -i {}"'.format(_list)
                ret = os.system(comm)
                if ret != 0:
                    if _num_items_failure < _num_i_f:
                        _items_failure.append([str(item)])
                    _num_items_failure += 1
            except Exception as E:
                if _num_items_failure < _num_i_f:
                    _items_failure.append(["Toggle immutable: "+str(E)])
                _num_items_failure += 1
        # permissions
        elif _btn > 100:
            for item in self.item_list:
                try:
                    if os.path.islink(item):
                        continue
                    if os.path.isdir(item) and not os.path.islink(item):
                        comm = "chmod {} '{}'".format(_btn+100, item)
                        ret = os.system(comm)
                        if ret != 0:
                            if _num_items_failure < _num_i_f:
                                _items_failure.append([str(item)])
                            _num_items_failure += 1
                    else:
                        comm = "chmod {} '{}'".format(_btn, item)
                        ret = os.system(comm)
                        if ret != 0:
                            if _num_items_failure < _num_i_f:
                                _items_failure.append([str(item)+" : "+str(E)])
                            _num_items_failure += 1
                except Exception as E:
                    if _num_items_failure < _num_i_f:
                        _items_failure.append([str(item)+" : "+str(E)])
                    _num_items_failure += 1
        #
        if _items_failure:
            dialogList = ""
            for el in _items_failure:
                dialogList += el[0]+"\n"
            #
            if _num_items_failure > len(_items_failure):
                dialogList += "(and others...)\n"
            #
            ret = retDialogBox("Info", "Error with these items.", "", dialogList, self.window)
            #
            # if ret.getValue():
            
    
    def faccept(self):
        self.close()
    
    # def closeEvent(self, event):
        # self.deleteLater()
    
    
#  dialog: yes no question
class retDialogBox2(QMessageBox):
    def __init__(self, *args):
        super(retDialogBox2, self).__init__(args[-1])
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle("Question")
        self.setIcon(QMessageBox.Icon.Question)
        self.resize(dialWidth, 100)
        self.setText(args[0])
        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        #
        self.Value = None
        retval = self.exec()
        #
        if retval == QMessageBox.StandardButton.Yes:
            self.Value = 1
        elif retval == QMessageBox.StandardButton.Cancel:
            self.Value = 0
    
    def getValue(self):
        return self.Value
    
    def event(self, e):
        result = QMessageBox.event(self, e)
        #
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        #
        return result  



# dialog - for file with the execution bit
class execfileDialog(QDialog):
    def __init__(self, itemPath, flag, parent):
        super(execfileDialog, self).__init__(parent)
        self.itemPath = itemPath
        self.flag = flag
        #
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle("Info")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.resize(dialWidth, 100)
        #
        vbox = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        vbox.setContentsMargins(5,5,5,5)
        self.setLayout(vbox)
        #
        label1 = QLabel("This is an executable file.\nWhat do you want to do?")
        vbox.addWidget(label1)
        hbox = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        vbox.addLayout(hbox)
        #
        if self.flag == 0 or self.flag == 3:
            button1 = QPushButton("Open")
            hbox.addWidget(button1)
            button1.clicked.connect(self.fopen)
        if self.flag != 3:
            button2 = QPushButton("Execute")
            hbox.addWidget(button2)
            button2.clicked.connect(self.fexecute)
        button3 = QPushButton("Cancel")
        hbox.addWidget(button3)
        button3.clicked.connect(self.fcancel)
        self.Value = 0
        self.exec()

    def getValue(self):
        return self.Value

    def fopen(self):
        self.Value = 1
        self.close()
    
    def fexecute(self):
        self.Value = 2
        self.close()
    
    def fcancel(self):
        self.Value = -1
        self.close()
    
    # def closeEvent(self, event):
        # self.deleteLater()


# dialog - whit item list and return of the choise
class retDialogBox(QMessageBox):
    def __init__(self, *args):
        super(retDialogBox, self).__init__(args[-1])
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle(args[0])
        if args[0] == "Info":
            self.setIcon(QMessageBox.Icon.Information)
        elif args[0] == "Error":
            self.setIcon(QMessageBox.Icon.Critical)
        elif args[0] == "Question":
            self.setIcon(QMessageBox.Icon.Question)
        self.resize(dialWidth, 100)
        self.setText(args[1])
        self.setInformativeText(args[2])
        self.setDetailedText("The details are as follows:\n\n"+args[3])
        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        #
        self.Value = None
        retval = self.exec()
        #
        if retval == QMessageBox.StandardButton.Yes:
            self.Value = 1
        elif retval == QMessageBox.StandardButton.Cancel:
            self.Value = 0
    
    def getValue(self):
        return self.Value
    
    def event(self, e):
        result = QMessageBox.event(self, e)
        #
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        #
        textEdit = self.findChild(QTextEdit)
        if textEdit != None :
            textEdit.setMinimumHeight(0)
            textEdit.setMaximumHeight(16777215)
            textEdit.setMinimumWidth(0)
            textEdit.setMaximumWidth(16777215)
            textEdit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        #
        return result

# dialog - Paste-n-Merge - choose the default action
# if an item at destination has the same name
# as the item to be copied
class pasteNmergeDialog(QDialog):
    
    def __init__(self, parent, destination, ltitle, item_type):
        super(pasteNmergeDialog, self).__init__(parent)
        # 
        self.destination = destination
        self.ltitle = ltitle
        self.item_type = item_type
        #
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle("Paste and Merge")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.resize(dialWidth, 100)
        #
        vbox = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        vbox.setContentsMargins(5,5,5,5)
        self.setLayout(vbox)
        #
        if self.item_type == "folder":
            label1 = QLabel("The folder\n"+self.ltitle+"\nexists in\n{}.".format(os.path.dirname(self.destination))+"\nPlease choose the default action for all folders.\nThis choise cannot be changed afterwards.\n")
        elif self.item_type == "file":
            label1 = QLabel("The file\n"+self.ltitle+"\nexists in\n{}.".format(os.path.dirname(self.destination))+"\nPlease choose the default action for all files.\nThis choise cannot be changed afterwards.\n")
        vbox.addWidget(label1)
        #
        hbox = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        vbox.addLayout(hbox)
        # skip all the items
        skipButton = QPushButton("Skip")
        skipButton.setToolTip("File and folders with the same name will be skipped.")
        hbox.addWidget(skipButton)
        skipButton.clicked.connect(lambda:self.fsetValue(1))
        # merge or overwrite all the items
        if self.item_type == "folder":
            overwriteButton = QPushButton("Merge")
            overwriteButton.setToolTip("All the folders will be merged.")
        elif self.item_type == "file":
            overwriteButton = QPushButton("Overwrite")
            overwriteButton.setToolTip("All the files will be overwritten.")
        hbox.addWidget(overwriteButton)
        overwriteButton.clicked.connect(lambda:self.fsetValue(2))
        # add an preformatted extension to the items
        automaticButton = QPushButton("Automatic")
        automaticButton.setToolTip("A suffix will be added to files an folders.")
        hbox.addWidget(automaticButton)
        automaticButton.clicked.connect(lambda:self.fsetValue(4))
        # backup the existen item(s)
        backupButton = QPushButton("Backup")
        backupButton.setToolTip("The original file or folder will be backed up.")
        hbox.addWidget(backupButton)
        backupButton.clicked.connect(lambda:self.fsetValue(5))
        # abort the operation
        cancelButton = QPushButton("Cancel")
        cancelButton.setToolTip("Abort.")
        hbox.addWidget(cancelButton)
        cancelButton.clicked.connect(self.fcancel)
        #
        self.Value = 0
        self.exec()
    
    def getValue(self):
        return self.Value
    
    def fsetValue(self, n):
        self.Value = n
        self.close()
    
    def fcancel(self):
        self.Value = -1
        self.close()
    
    # def closeEvent(self, event):
        # self.deleteLater()
    

################################
# for item copying - Paste and Merge function
class copyThread2(QThread):
    
    sig = pyqtSignal(list)
    
    def __init__(self, action, newList, atype, pathdest, parent=None):
        super(copyThread2, self).__init__(parent)
        # action: 1 copy - 2 cut
        self.action = action
        # the list of the items
        self.newList = newList
        # 1 skip - 2 overwrite - 3 rename - 4 automatic suffix - 5 backup the existent items
        self.atype = atype
        # for folders
        self.atypeDir = atype
        # destination path
        self.pathdest = pathdest
        #
        # ask for a new name from a dialog
        self.sig.connect(self.getdatasygnal)
        # used for main program-thread communication
        self.reqNewNm = ""
    
    def getdatasygnal(self, l=None):
        if l[0] == "SendNewAtype" or l[0] == "SendNewDtype":
            self.reqNewNm = l[1]

    def run(self):
        time.sleep(1)
        self.item_op()
    
    ## self.atype 4 or 5
    # add a suffix to the filename if the file exists at destination
    def faddSuffix(self, dest):
        # it exists or it is a broken link
        if os.path.exists(dest) or os.path.islink(dest):
            i = 1
            dir_name = os.path.dirname(dest)
            bname = os.path.basename(dest)
            dest = ""
            while i:
                nn = bname+"_("+str(i)+")"
                if os.path.exists(os.path.join(dir_name, nn)):
                    i += 1
                else:
                    dest = os.path.join(dir_name, nn)
                    i = 0
            #
            return dest
    
    # add the suffix to the name
    def faddSuffix2(self, dts, dest):
        new_name = os.path.basename(dest)+dts
        dest = os.path.join(os.path.dirname(dest), new_name)
        return dest
        
    # the work on each item
    # self.atype: 1 skip - 2 overwrite - 4 automatic suffix - 5 backup the existent items
    def item_op(self):
        items_skipped = ""
        # limit the number of items to be reported if something goes wrong - 30
        not_to_skip = 0
        num_not_to_skip = 30
        not_to_skip_msg = "(+ others)"
        # action: copy 1 - cut 2
        action = self.action
        newList = self.newList
        total_size = 1
        incr_size = 1
        # common suffix if date - the same date for all items
        commSfx = ""
        if USE_DATE:
            z = datetime.datetime.now()
            #dY, dM, dD, dH, dm, ds, dms
            commSfx = "_{}.{}.{}_{}.{}.{}".format(z.year, z.month, z.day, z.hour, z.minute, z.second)
        
        self.sig.emit(["Starting...", 0, total_size])
        #
        # the default action for all files in the dir to be copied...
        # ... if an item with the same name already exist at destination
        dirfile_dcode = 0
        # for the items in the dir: 1 skip - 2 replace - 4 automatic - 5 backup
        for dfile in newList:
            # the user can interrupt the operation for the next items
            if self.isInterruptionRequested():
                if not_to_skip > 30:
                    items_skipped += "\n{}".format(not_to_skip_msg)
                self.sig.emit(["Cancelled", 1, 1, items_skipped])
                return
            #
            time.sleep(0.001)
            #
            # one signal for each element in the list
            self.sig.emit(["mSending", os.path.basename(dfile)])
            #
            # item is dir and not link to dir
            if os.path.isdir(dfile) and not os.path.islink(dfile):
                tdest = os.path.join(self.pathdest, os.path.basename(dfile))
                # recursive copying - not allowed
                len_dfile = len(dfile)
                # if tdest[0:len_dfile] == dfile and not tdest == dfile:
                if os.path.dirname(tdest) == dfile and not tdest == dfile:
                    items_skipped += "Recursive copying:\n{}".format(os.path.basename(dfile))
                    continue
                # # trying to copy a dir into itself - do not uncomment
                # if dfile == os.path.dirname(tdest):
                    # items_skipped += "Same folder:\n{}.".format(os.path.basename(dfile))
                    # continue
                # it isnt the exactly same item
                elif dfile != tdest:
                    #
                    # the dir doesnt exist at destination or it is a broken link
                    if not os.path.exists(tdest):
                        try:
                            # check broken link
                            if os.path.islink(tdest):
                                ret = ""
                                if USE_DATE:
                                    ret = self.faddSuffix2(commSfx, tdest)
                                else:
                                    ret = self.faddSuffix(tdest)
                                shutil.move(tdest, ret)
                                items_skipped += "{}:\nRenamed (broken link).\n------------\n".format(tdest)
                            #
                            if action == 1:
                                shutil.copytree(dfile, tdest, symlinks=True, ignore=None, copy_function=shutil.copy2, ignore_dangling_symlinks=False)
                            elif action == 2:
                                shutil.move(dfile, tdest)
                        except Exception as E:
                            not_to_skip += 1
                            if not_to_skip < num_not_to_skip:
                                items_skipped += "{}:\n{}\n------------\n".format(tdest, str(E))
                            # reset
                            self.reqNewNm = ""
                    #
                    # exists at destination a folder with the same name
                    elif os.path.exists(tdest):
                        # get the default choise (one choise for all folders to copy in the main dir)
                        if self.atypeDir == -4:
                            self.sig.emit(["ReqNewDtype", tdest, os.path.basename(tdest)])
                            while self.reqNewNm == "":
                                time.sleep(1)
                            else:
                                # 
                                self.atypeDir = self.reqNewNm
                                # reset
                                self.reqNewNm = ""
                        #
                        # -1 abort if cancelled
                        if self.atypeDir == -1:
                            items_skipped += "Operation aborted by the user.\n"
                            break
                        # 1 skip
                        elif self.atypeDir == 1:
                            # items_skipped += "{}:\n{}\n------------\n".format(dfile, "Folder skipped by the user.")
                            continue
                        #
                        # new dir name if an item exists at destination with the same name
                        newDestDir = ""
                        #
                        # 4 automatic - rename the item to copy
                        if self.atypeDir == 4:
                            if USE_DATE:
                                newDestDir = self.faddSuffix2(commSfx, tdest)
                            else:
                                newDestDir = self.faddSuffix(tdest)
                            # first create the dir
                            try:
                                os.makedirs(newDestDir)
                            except Exception as E:
                                not_to_skip += 1
                                if not_to_skip < num_not_to_skip:
                                    items_skipped += "{}:\n{}\n------------\n".format(newDestDir, str(E))
                                continue
                            # copy or move
                            try:
                                for sdir,ddir,ffile in os.walk(dfile):
                                    if action == 1:
                                        for dr in ddir:
                                            shutil.copytree(os.path.join(sdir, dr), os.path.join(newDestDir, dr), symlinks=True, ignore=None, copy_function=shutil.copy2, ignore_dangling_symlinks=False)
                                        for ff in ffile:
                                            shutil.copy2(os.path.join(sdir, ff), newDestDir, follow_symlinks=False)
                                    elif action == 2:
                                        for dr in ddir:
                                            shutil.move(os.path.join(sdir, dr), newDestDir)
                                        for ff in ffile:
                                            shutil.move(os.path.join(sdir, ff), newDestDir)
                            except Exception as E:
                                not_to_skip += 1
                                if not_to_skip < num_not_to_skip:
                                    items_skipped += "{}:\n{}\n------------\n".format(newDestDir, str(E))
                                continue
                            try:
                                if action == 2:
                                    shutil.rmtree(dfile)
                            except Exception as E:
                                not_to_skip += 1
                                if not_to_skip < num_not_to_skip:
                                    items_skipped += "{}:\n{}\n------------\n".format(newDestDir, str(E))
                                continue
                        # 5 backup - rename the item at destination and copy
                        elif self.atypeDir == 5:
                            # rename the dir
                            try:
                                ret = ""
                                if USE_DATE:
                                    ret = self.faddSuffix2(commSfx, tdest)
                                else:
                                    ret = self.faddSuffix(tdest)
                                os.rename(tdest, os.path.join(os.path.dirname(tdest),ret))
                            except Exception as E:
                                not_to_skip += 1
                                if not_to_skip < num_not_to_skip:
                                    items_skipped += "{}:\n{}\n------------\n".format(tdest, str(E))
                                continue
                            # copy or move
                            try:
                                if action == 1:
                                    shutil.copytree(dfile, tdest, symlinks=True, ignore=None, copy_function=shutil.copy2, ignore_dangling_symlinks=False)
                                elif action == 2:
                                    shutil.move(dfile, tdest)
                            except Exception as E:
                                not_to_skip += 1
                                if not_to_skip < num_not_to_skip:
                                    items_skipped += "{}:\n{}\n------------\n".format(dfile, str(E))
                                continue
                        #
                        # 2 merge - broken link or not folder
                        if self.atypeDir == 2:
                            try:
                                if os.path.islink(tdest):
                                    os.unlink(tdest)
                                elif not os.path.isdir(tdest):
                                    os.remove(tdest)
                            except Exception as E:
                                not_to_skip += 1
                                if not_to_skip < num_not_to_skip:
                                    items_skipped += "{}:\n{}\n------------\n".format(tdest, str(E))
                                continue
                            #
                            todest = tdest
                            # 
                            # sdir has full path
                            for sdir,ddir,ffile in os.walk(dfile):
                                # temp_dir = sdir[len(dfile)+1:]
                                temp_dir = os.path.relpath(sdir, dfile)
                                # 1 - create the subdirs if the case
                                for dr in ddir:
                                    todest2 = os.path.join(todest, temp_dir, dr)
                                    if not os.path.exists(todest2):
                                        # require python >= 3.3
                                        os.makedirs(todest2, exist_ok=True)
                                #
                                # 2 - copy the files
                                for item_file in ffile:
                                    # the item at destination
                                    dest_item = os.path.join(todest, temp_dir, item_file)
                                    #
                                    # at destination exists or is a broken link
                                    if os.path.exists(dest_item) or os.path.islink(dest_item):
                                        # eventually the source file - it could not exist
                                        source_item = os.path.join(dfile, sdir, item_file)
                                        source_item_skipped = os.path.join(os.path.basename(dfile), sdir, item_file)
                                        # atype choosing dialog if dirfile_dcode is 0 (no choises previously made)
                                        if dirfile_dcode == 0:
                                            self.sig.emit(["ReqNewAtype", tdest, os.path.basename(dest_item)])
                                            while self.reqNewNm == "":
                                                time.sleep(1)
                                            else:
                                                # dcode
                                                dirfile_dcode = self.reqNewNm
                                                # also for files outside this folder
                                                self.atype = dirfile_dcode
                                                # reset
                                                self.reqNewNm = ""
                                        #
                                        # -1 means cancelled from the rename dialog
                                        if dirfile_dcode == -1:
                                            items_skipped += "Operation cancelled by the user\n------------\n"
                                            break
                                        # 1 skip
                                        elif dirfile_dcode == 1:
                                            # items_skipped += "{}:\n{}\n------------\n".format(fpsitem, "Skipped.")
                                            continue
                                        # 2 overwrite
                                        elif dirfile_dcode == 2:
                                            try:
                                                # link
                                                if os.path.islink(dest_item):
                                                    os.unlink(dest_item)
                                                # dir
                                                elif os.path.isdir(dest_item):
                                                    shutil.rmtree(dest_item)
                                                # copy or overwrite
                                                if action == 1:
                                                    shutil.copy2(source_item, dest_item, follow_symlinks=False)
                                                elif action == 2:
                                                    shutil.move(source_item, dest_item)
                                            except Exception as E:
                                                not_to_skip += 1
                                                if not_to_skip < num_not_to_skip:
                                                    items_skipped += "{}:\n{}\n------------\n".format(source_item_skipped, str(E))
                                        # 4 automatic
                                        elif dirfile_dcode == 4:
                                            try:
                                                ret = ""
                                                if USE_DATE:
                                                    ret = self.faddSuffix2(commSfx, dest_item)
                                                else:
                                                    ret = self.faddSuffix(dest_item)
                                                iNewName = os.path.join(os.path.dirname(dest_item),ret)
                                                if action == 1:
                                                    shutil.copy2(source_item, iNewName, follow_symlinks=False)
                                                elif action == 2:
                                                    shutil.move(source_item, iNewName)
                                            except Exception as E:
                                                not_to_skip += 1
                                                if not_to_skip < num_not_to_skip:
                                                    items_skipped += "{}:\n{}\n------------\n".format(source_item_skipped, str(E))
                                        # 5 backup the existent file
                                        elif dirfile_dcode == 5:
                                            try:
                                                ret = ""
                                                if USE_DATE:
                                                    ret = self.faddSuffix2(commSfx, dest_item)
                                                else:
                                                    ret = self.faddSuffix(dest_item)
                                                shutil.move(dest_item, ret)
                                                if action == 1:
                                                    shutil.copy2(source_item, dest_item, follow_symlinks=False)
                                                elif action == 2:
                                                    shutil.move(source_item, dest_item)
                                            except Exception as E:
                                                not_to_skip += 1
                                                if not_to_skip < num_not_to_skip:
                                                    items_skipped += "{}:\n{}\n------------\n".format(source_item_skipped, str(E))
                                    # doesnt exist at destination
                                    else:
                                        try:
                                            if action == 1:
                                                shutil.copy2(os.path.join(sdir,item_file), dest_item, follow_symlinks=False)
                                            elif action == 2:
                                                shutil.move(os.path.join(sdir,item_file), dest_item)
                                        except Exception as E:
                                            not_to_skip += 1
                                            if not_to_skip < num_not_to_skip:
                                                items_skipped += "{}:\n{}\n------------\n".format(os.path.join(sdir,item_file), str(E))
                        #
                        #############
                # origin and destination are the exactly same directory
                else:
                    if action == 1:
                        try:
                            ret = ""
                            if USE_DATE:
                                ret = self.faddSuffix2(commSfx, dfile)
                            else:
                                ret = self.faddSuffix(dfile)
                            shutil.copytree(dfile, ret, symlinks=True, ignore=None, copy_function=shutil.copy2, ignore_dangling_symlinks=False)
                            # items_skipped += "{}:\nCopied and Renamed:\n{}\n------------\n".format(os.path.basename(tdest), os.path.basename(ret))
                        except Exception as E:
                            not_to_skip += 1
                            if not_to_skip < num_not_to_skip:
                                items_skipped += "{}:\n{}\n------------\n".format(os.path.basename(dfile), str(E))
                    # elif action == 2:
                        # pass
            # item is file or link/broken link or else
            else:
                # check for an item with the same name at destination
                tdest = os.path.join(self.pathdest, os.path.basename(dfile))
                # if not the exactly same item
                if dfile != tdest:
                    if os.path.exists(tdest):
                        if self.atype == -4:
                            self.sig.emit(["ReqNewAtype", tdest, os.path.basename(tdest)])
                            while self.reqNewNm == "":
                                time.sleep(1)
                            else:
                                # 
                                self.atype = self.reqNewNm
                                # also for files isside folders
                                dirfile_dcode = self.atype
                                # reset
                                self.reqNewNm = ""
                        # -1 cancel
                        if self.atype == -1:
                            items_skipped += "Operation aborted by the user.\n"
                            break
                        # 1 skip
                        elif self.atype == 1:
                            # items_skipped += "{}:\n{}\n------------\n".format(dfile, "Skipped.")
                            continue
                        # 2 overwrite
                        elif self.atype == 2:
                            try:
                                if action == 1:
                                    shutil.copy2(dfile, tdest, follow_symlinks=False)
                                elif action == 2:
                                    shutil.move(dfile, tdest)
                            except Exception as E:
                                not_to_skip += 1
                                if not_to_skip < num_not_to_skip:
                                    items_skipped += "{}:\n{}\n------------\n".format(dfile, str(E))
                        # 4 automatic
                        elif self.atype == 4:
                            try:
                                ret = ""
                                if USE_DATE:
                                    ret = self.faddSuffix2(commSfx, tdest)
                                else:
                                    ret = self.faddSuffix(tdest)
                                #
                                if action == 1:
                                    shutil.copy2(dfile, ret, follow_symlinks=False)
                                elif action == 2:
                                    shutil.move(dfile, ret)
                            except Exception as E:
                                not_to_skip += 1
                                if not_to_skip < num_not_to_skip:
                                    items_skipped += "{}:\n{}\n------------\n".format(dfile, str(E))
                        # 5 backup the existent files
                        elif self.atype == 5:
                            try:
                                ret = ""
                                if USE_DATE:
                                    ret = self.faddSuffix2(commSfx, tdest)
                                else:
                                    ret = self.faddSuffix(tdest)
                                shutil.move(tdest, ret)
                                if action == 1:
                                    shutil.copy2(dfile, tdest, follow_symlinks=False)
                                elif action == 2:
                                    shutil.move(dfile, tdest)
                            except Exception as E:
                                not_to_skip += 1
                                if not_to_skip < num_not_to_skip:
                                    items_skipped += "{}:\n{}\n------------\n".format(dfile, str(E))
                    # it doesnt exist at destination
                    else:
                        # if broken link rename
                        if os.path.islink(tdest):
                            try:
                                ret = ""
                                if USE_DATE:
                                    ret = self.faddSuffix2(commSfx, tdest)
                                else:
                                    ret = self.faddSuffix(tdest)
                                shutil.move(tdest, ret)
                                items_skipped += "{}:\nRenamed (broken link)\n------------\n".format(tdest)
                            except Exception as E:
                                not_to_skip += 1
                                if not_to_skip < num_not_to_skip:
                                    items_skipped += "{}:\n{}\n------------\n".format(dfile, str(E))
                        #
                        try:
                            if action == 1:
                                shutil.copy2(dfile, tdest, follow_symlinks=False)
                            elif action == 2:
                                shutil.move(dfile, tdest)
                        except Exception as E:
                            not_to_skip += 1
                            if not_to_skip < num_not_to_skip:
                                items_skipped += "{}:\n{}\n------------\n".format(dfile, str(E))
                # if it is the exactly same item
                else:
                    if action == 1:
                        try:
                            ret = ""
                            if USE_DATE:
                                ret = self.faddSuffix2(commSfx, tdest)
                            else:
                                ret = self.faddSuffix(tdest)
                            shutil.copy2(dfile, ret, follow_symlinks=False)
                            # items_skipped += "{}:\nCopied and Renamed:\n{}\n------------\n".format(tdest, ret)
                        except Exception as E:
                            not_to_skip += 1
                            if not_to_skip < num_not_to_skip:
                                items_skipped += "{}:\n{}\n------------\n".format(tdest, str(E))
                    elif action == 2:
                        items_skipped += "{}:\n{}\n------------\n".format(dfile, "Exactly the same item.")
        #
        # DONE
        if not_to_skip > 30:
            items_skipped += "\n{}".format(not_to_skip_msg)
        self.sig.emit(["mDone", 1, 1, items_skipped])


# Paste and Merge function
class copyItems2():
    def __init__(self, action, newList, atype, pathdest, window):
        self.action = action
        self.newList = newList
        self.atype = atype
        self.pathdest = pathdest
        self.window = window
        #
        self.newDtype = ""
        self.newAtype = ""
        # check if free disc size at destination
        free_space_left = check_free_disc_space(self.newList, self.pathdest)
        #
        if free_space_left:
            self.myDialog()
        else:
            MyDialog("Info", "Not enough space on disc.", None)
    
    def myDialog(self):
        self.mydialog = QDialog(parent = self.window)
        self.mydialog.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.mydialog.setWindowTitle("Copying...")
        self.mydialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.mydialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.mydialog.resize(dialWidth,100)
        # 
        grid = QGridLayout()
        grid.setContentsMargins(5,5,5,5)
        #
        self.label1 = clabel2()
        self.label1.setText("Processing...", self.mydialog.size().width()-12)
        grid.addWidget(self.label1, 0, 0, 1, 4, Qt.AlignmentFlag.AlignCenter)
        #
        self.label2 = QLabel("")
        grid.addWidget(self.label2, 1, 0, 1, 4, Qt.AlignmentFlag.AlignCenter)
        #
        self.pb = QProgressBar()
        self.pb.setMinimum(0)
        self.pb.setMaximum(100)
        self.pb.setValue(0)
        grid.addWidget(self.pb, 3, 0, 1, 4, Qt.AlignmentFlag.AlignCenter)
        #
        self.button1 = QPushButton("Close")
        self.button1.clicked.connect(self.fbutton1)
        grid.addWidget(self.button1, 4, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        #
        self.button1.setEnabled(False)
        #
        self.button2 = QPushButton("Abort")
        self.button2.clicked.connect(self.fbutton2)
        grid.addWidget(self.button2, 4, 2, 1, 2, Qt.AlignmentFlag.AlignCenter)
        #
        # number of items in the list
        self.numItemList = len(self.newList)
        # number of items processed
        self.numItemProc = 0
        #
        self.mydialog.setLayout(grid)
        self.mythread = copyThread2(self.action, self.newList, self.atype, self.pathdest)
        self.mythread.sig.connect(self.threadslot)
        self.mythread.start()
        #
        self.mydialog.exec()
   
    
    def threadslot(self, aa):
        # from directories
        if aa[0] == "ReqNewDtype":
            # 1 skip - 2 overwrite - 4 automatic - 5 backup
            sNewDtype = pasteNmergeDialog(self.window, aa[1], aa[2], "folder").getValue()
            self.mythread.sig.emit(["SendNewDtype", sNewDtype])
            self.newDtype = sNewDtype
        # from any files
        elif aa[0] == "ReqNewAtype":
            # 1 skip - 2 overwrite - 4 automatic - 5 backup
            sNewAtype = pasteNmergeDialog(self.window, aa[1], aa[2], "file").getValue()
            self.mythread.sig.emit(["SendNewAtype", sNewAtype])
            self.newAtype = sNewAtype
        # copying process
        elif aa[0] == "mSending":
            self.label1.setText(aa[1], self.mydialog.size().width()-12)
            self.numItemProc += 1
            self.label2.setText("Items: {}/{}".format(self.numItemProc,self.numItemList))
            self.pb.setValue(int(self.numItemProc/self.numItemList*100))
        # the copying process ends
        elif aa[0] == "mDone":
            self.label1.setText("Done", self.mydialog.size().width()-12)
            if self.numItemProc == self.numItemList:
                self.pb.setValue(100)
            # change the button state
            self.button1.setEnabled(True)
            self.button2.setEnabled(False)
            # something happened with some items
            if len(aa) == 4 and aa[3] != "":
                MyMessageBox("Info", "Something happened with some items", "", aa[3], self.window)
        # operation interrupted by the user
        elif aa[0] == "Cancelled":
            self.label1.setText("Cancelled.", self.mydialog.size().width()-12)
            self.label2.setText("Items: {}/{}".format(self.numItemProc,self.numItemList))
            self.pb.setValue(int(self.numItemProc/self.numItemList*100))
            # change the button state
            self.button1.setEnabled(True)
            self.button2.setEnabled(False)
            # something happened with some items
            if len(aa) == 4 and aa[3] != "":
                MyMessageBox("Info", "Something happened with some items", "", aa[3], self.window)
    
    def fbutton1(self):
        self.mydialog.close()

    def fbutton2(self):
        self.mythread.requestInterruption()

#################################

# dialog for asking the password
class passWord(QDialog):
    def __init__(self, ppath, ttype, parent):
        super(passWord, self).__init__(parent)
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle("Password")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.resize(dialWidth,100)
        #
        self.ppath = ppath
        self.ttype = ttype
        # main box
        mbox = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        mbox.setContentsMargins(5,5,5,5)
        # label
        self.label = QLabel("Enter The Password:")
        mbox.addWidget(self.label)
        # checkbox
        self.ckb = QCheckBox("Hide/Show the password")
        self.ckb.setChecked(True)
        self.ckb.toggled.connect(self.on_checked)
        mbox.addWidget(self.ckb)
        # lineedit
        self.le1 = QLineEdit()
        self.le1.setEchoMode(QLineEdit.Password)
        mbox.addWidget(self.le1)
        ##
        button_box = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        button_box.setContentsMargins(0,0,0,0)
        mbox.addLayout(button_box)
        #
        button_ok = QPushButton("     Accept     ")
        button_box.addWidget(button_ok)
        #
        button_close = QPushButton("     Cancel     ")
        button_box.addWidget(button_close)
        #
        self.setLayout(mbox)
        button_ok.clicked.connect(self.setpswd)
        button_close.clicked.connect(self.close)
        #
        self.exec()
    
    def on_checked(self):
        if self.ckb.isChecked():
            self.le1.setEchoMode(QLineEdit.Password)
        else:
            self.le1.setEchoMode(QLineEdit.Normal)
    
    def setpswd(self):
        passwd = self.le1.text()
        if passwd:
            if self.ttype == 1:
                try:
                    subprocess.run([PKEXEC, "1", passwd, self.ppath])
                except:
                    pass
            elif self.ttype == 2:
                try:
                    subprocess.run([PKEXEC, "2", passwd, self.ppath])
                except:
                    pass
            elif self.ttype == 3:
                try:
                    subprocess.run([PKEXEC, "3", passwd, self.ppath])
                except:
                    pass
            elif self.ttype == 4:
                try:
                    subprocess.run([PKEXEC, "4", passwd, self.ppath])
                except:
                    pass
        self.close()
    
    # def closeEvent(self, event):
        # self.deleteLater()

# 
class MyQlist(QListView):
    def __init__(self):
        super(MyQlist, self).__init__()
        self.verticalScrollBar().setSingleStep(25)
        self.customMimeType = "application/x-customqt5archiver"
        self.user_action = 0
        self.selected_item = None
        #
        #
        # ###########
        # cssa = ("QScrollBar:vertical {"
    # "border: 0px solid #999999;"
    # "background:white;"
    # "width:8px;"
    # "margin: 0px 0px 0px 0px;"
# "}"
# "QScrollBar::handle:vertical {")
        # cssb = ("min-height: 0px;"
    # "border: 0px solid red;"
    # "border-radius: 4px;"
    # "background-color: {};".format(scroll_handle_col))
        # cssc = ("}"
# "QScrollBar::add-line:vertical {"       
    # "height: 0px;"
    # "subcontrol-position: bottom;"
    # "subcontrol-origin: margin;"
# "}"
# "QScrollBar::sub-line:vertical {"
    # "height: 0 px;"
    # "subcontrol-position: top;"
    # "subcontrol-origin: margin;"
# "}")
        # #
        # if scroll_handle_col:
            # css = cssa+cssb+cssc
            # self.verticalScrollBar().setStyleSheet(css)
    
    # def keyPressEvent(self, e):
        # # if e.key() == Qt.Key.Key_K:
            # # print("k")
        # if (e.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            # print("shift")
    
    
    def startDrag(self, supportedActions):
        item_list = []
        for index in self.selectionModel().selectedIndexes():
            filepath = index.data(Qt.ItemDataRole.UserRole+1)
            try:
                # regular files or folders (not fifo, etc.)
                if stat.S_ISREG(os.stat(filepath).st_mode) or stat.S_ISDIR(os.stat(filepath).st_mode) or stat.S_ISLNK(os.stat(filepath).st_mode):
                    item_list.append(QUrl.fromLocalFile(filepath))
                else:
                    continue
            except:
                continue
        #
        drag = QDrag(self)
        if len(item_list) > 1:
            if USE_EXTENDED_DRAG_ICON == 0:
                pixmap = QPixmap("icons/items_multi.png").scaled(ICON_SIZE, ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
            else:
                painter = None
                #
                if USE_EXTENDED_DRAG_ICON == 1:
                    # number of selected items
                    num_item = min(NUM_OVERLAY, len(self.selectionModel().selectedIndexes()))
                    #
                    num_col_tmp = num_item ** (1/2)
                    num_col = 0
                    if (num_col_tmp - int(num_col_tmp)) > 0:
                        num_col = int(num_col_tmp) + 1
                    else:
                        num_col = int(num_col_tmp)
                    #
                    num_row_tmp = num_item / num_col
                    num_row = 0
                    if (num_row_tmp - int(num_row_tmp)) > 0:
                        num_row = int(num_row_tmp) + 1
                    else:
                        num_row = int(num_row_tmp)
                    #
                    poffsetW = 4
                    poffsetH = 4
                    psizeW = mini_icon_size * num_col + (poffsetW * num_col + poffsetW)
                    psizeH = mini_icon_size * num_row + (poffsetH * num_row + poffsetH)
                    pixmap = QPixmap(psizeW, psizeH)
                    pixmap.fill(QColor(253,253,253,0))
                    incr_offsetW = poffsetW
                    incr_offsetH = poffsetH
                    #
                    model = self.model()
                    # to verify
                    pixel_ratio = self.devicePixelRatio()
                    # 
                    for i in range(num_item):
                        index = self.selectionModel().selectedIndexes()[i]
                        filepath = index.data(Qt.ItemDataRole.UserRole+1)
                        if stat.S_ISREG(os.stat(filepath).st_mode) or stat.S_ISDIR(os.stat(filepath).st_mode) or stat.S_ISLNK(os.stat(filepath).st_mode):
                            file_icon = model.fileIcon(index)
                            pixmap1 = file_icon.pixmap(QSize(int(mini_icon_size/pixel_ratio), int(mini_icon_size/pixel_ratio)))
                            if not painter:
                                painter = QPainter(pixmap)
                            # limit the number of overlays
                            if i < NUM_OVERLAY:
                                woffset = int((int(mini_icon_size/pixel_ratio) - int(pixmap1.size().width()/pixel_ratio))/2)
                                hoffset = int((int(mini_icon_size/pixel_ratio) - int(pixmap1.size().height()/pixel_ratio))/2)
                                # 
                                tmp_col = i/num_col
                                if i and tmp_col % 1 == 0:
                                    incr_offsetW = 4
                                    incr_offsetH += (poffsetH + int(mini_icon_size/pixel_ratio))
                                #
                                painter.drawPixmap(incr_offsetW+woffset, incr_offsetH+hoffset, pixmap1)
                                #
                                incr_offsetW += (poffsetW + int(mini_icon_size/pixel_ratio))
                            else:
                                break
                        else:
                            continue
                #
                elif USE_EXTENDED_DRAG_ICON == 2:
                    # number of selected items
                    num_item = len(self.selectionModel().selectedIndexes())
                    poffsetW = X_EXTENDED_DRAG_ICON
                    poffsetH = Y_EXTENDED_DRAG_ICON
                    psizeW = ICON_SIZE + (min(NUM_OVERLAY, num_item) * poffsetW) - poffsetW
                    psizeH = ICON_SIZE + (min(NUM_OVERLAY, num_item) * poffsetH) - poffsetH
                    pixmap = QPixmap(psizeW, psizeH)
                    pixmap.fill(QColor(253,253,253,0))
                    incr_offsetW = poffsetW
                    incr_offsetH = poffsetH
                    #
                    model = self.model()
                    #
                    pixel_ratio = self.devicePixelRatio()
                    #
                    for i in reversed(range(min(NUM_OVERLAY, num_item))):
                        index = self.selectionModel().selectedIndexes()[i]
                        filepath = index.data(Qt.ItemDataRole.UserRole+1)
                        if stat.S_ISREG(os.stat(filepath).st_mode) or stat.S_ISDIR(os.stat(filepath).st_mode) or stat.S_ISLNK(os.stat(filepath).st_mode):
                            file_icon = model.fileIcon(index)
                            pixmap1 = file_icon.pixmap(QSize(int(ICON_SIZE/pixel_ratio), int(ICON_SIZE/pixel_ratio)))
                            if not painter:
                                painter = QPainter(pixmap)
                                woffset = int((int(ICON_SIZE/pixel_ratio) - int(pixmap1.size().width()/pixel_ratio))/2)
                                ioffset = int((int(ICON_SIZE/pixel_ratio) - int(pixmap1.size().height()/pixel_ratio))/2)
                                painter.drawPixmap(int(psizeW-ICON_SIZE+woffset), int(psizeH-ICON_SIZE+ioffset), pixmap1)
                            else:
                                # limit the number of overlays
                                if i < NUM_OVERLAY:
                                    woffset = int((int(ICON_SIZE/pixel_ratio) - int(pixmap1.size().width()/pixel_ratio))/2)
                                    ioffset = int((int(ICON_SIZE/pixel_ratio) - int(pixmap1.size().height()/pixel_ratio))/2)
                                    painter.drawPixmap(int(psizeW-ICON_SIZE-incr_offsetW+woffset), int(psizeH-ICON_SIZE-incr_offsetH+ioffset), pixmap1)
                                    incr_offsetW += poffsetW
                                    incr_offsetH += poffsetH
                                else:
                                    break
                        else:
                            continue
                #
                painter.end()
        #
        elif len(item_list) == 1:
            try:
                model = self.model()
                for i in range(len(self.selectionModel().selectedIndexes())):
                    index = self.selectionModel().selectedIndexes()[i]
                    filepath = index.data(Qt.ItemDataRole.UserRole+1)
                    if stat.S_ISREG(os.stat(filepath).st_mode) or stat.S_ISDIR(os.stat(filepath).st_mode) or stat.S_ISLNK(os.stat(filepath).st_mode):
                        file_icon = model.fileIcon(index)
                        pixmap = file_icon.pixmap(QSize(ICON_SIZE, ICON_SIZE))
                        break
                    else:
                        continue
            except:
                pixmap = QPixmap("icons/empty.svg").scaled(ICON_SIZE, ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
        else:
            return
        #
        drag.setPixmap(pixmap)
        data = QMimeData()
        data.setUrls(item_list)
        drag.setMimeData(data)
        drag.setHotSpot(pixmap.rect().topLeft())
        if self.selected_item in item_list:
            drag.exec(Qt.DropAction.CopyAction|Qt.DropAction.MoveAction|Qt.DropAction.LinkAction, Qt.DropAction.CopyAction)

    
    def mousePressEvent(self, event):
        self.selected_item = None
        if event.button() == Qt.MouseButton.LeftButton or event.button() == Qt.MouseButton.RightButton:
            # pointedItem = self.indexAt(event.pos())
            pointedItem = self.indexAt(event.position().toPoint())
            if pointedItem.isValid():
                ifp = self.model().data(pointedItem, QFileSystemModel.Roles.FilePathRole)
                ifp_url = QUrl.fromLocalFile(ifp)
                self.selected_item = ifp_url
            #
            super(QListView,self).mousePressEvent(event)
        elif event.button() == Qt.MouseButton.RightButton:
            super(QListView,self).mousePressEvent(event)
    
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
            # pointedItem = self.indexAt(event.pos())
            # if not pointedItem.isValid():
                # event.ignore()
                # return
            # ifp = self.model().data(pointedItem, QFileSystemModel.Roles.FilePathRole)
            # ifp_url = QUrl.fromLocalFile(ifp)
            # if ifp_url in event.mimeData().urls():
                # event.accept()
            # else:
                # event.ignore()
        else:
            event.ignore()


    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(self.customMimeType):
            # a folder in the destination directory
            # pointedItem = self.indexAt(event.pos())
            pointedItem = self.indexAt(event.position().toPoint())
            if pointedItem.isValid():
                ifp = self.model().data(pointedItem, QFileSystemModel.Roles.FilePathRole)
                if os.path.isdir(ifp):
                    dest_dir = QFileInfo(ifp)
                    if not dest_dir.isWritable():
                        event.ignore()
                        return
            #
            event.acceptProposedAction()
            return
        #
        # if event.pos().y() > self.viewport().size().height() - 100:
            # step = 10
            # self.verticalScrollBar().setValue(self.verticalScrollBar().value() + step)
        # elif event.pos().y() < 100:
            # step = -10
            # self.verticalScrollBar().setValue(self.verticalScrollBar().value() + step)
        # to verify
        # if event.answerRect().y() > self.viewport().size().height() - 40:
        if event.position().toPoint().y() > self.viewport().size().height() - 40:
            step = 10
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + step)
        # elif event.answerRect().y() < 40:
        elif event.position().toPoint().y() < 40:
            step = -10
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + step)
        
        #
        dest_path = self.model().rootPath()
        curr_dir = QFileInfo(dest_path)
        if not curr_dir.isWritable():
            event.ignore()
        #
        if event.mimeData().hasUrls:
            if isinstance(event.source(), MyQlist):
                # pointedItem = self.indexAt(event.pos())
                pointedItem = self.indexAt(event.position().toPoint())
                if pointedItem.isValid():
                    ifp = self.model().data(pointedItem, QFileSystemModel.Roles.FilePathRole)
                    if os.path.isdir(ifp):
                        for uurl in event.mimeData().urls():
                            if uurl.toLocalFile() == ifp:
                                event.ignore()
                                break
                        else:
                            event.acceptProposedAction()
                    else:
                        event.ignore()
                else:
                    event.ignore()
            else:
                event.acceptProposedAction()
    
    
    def dropEvent(self, event):
        if event.mimeData().hasFormat(self.customMimeType):
            ddata_temp = event.mimeData().data(self.customMimeType)
            ddata = str(ddata_temp, 'utf-8').split("\n")
            #
            # if os.path.exists(ddata[0]):
                # try:
                    # ifile = open(os.path.join(ddata[0], "where_to_extract"), "w")
                    # ifile.write(self.model().rootPath())
                    # ifile.close()
                # except Exception as E:
                    # MyDialog("Error", str(E), None)
                    # event.ignore()
                #
            if ddata[0] == "R":
                data = QByteArray()
                dest_path = self.model().rootPath()
                drop_data = "{}\n{}".format("A", dest_path)
                data.append(bytes(drop_data, encoding="utf-8"))
                mimedata = QMimeData()
                mimedata.setData(self.customMimeType, data)
                QApplication.clipboard().setMimeData(mimedata)
                #
                event.accept()
            else:
                data = QByteArray()
                drop_data = "{}\n{}".format("E", "")
                data.append(bytes(drop_data, encoding="utf-8"))
                mimedata = QMimeData()
                mimedata.setData(self.customMimeType, data)
                QApplication.clipboard().setMimeData(mimedata)
                #
                event.ignore()
            return
        ######################
        self.user_action = 0
        dest_path = self.model().rootPath()
        curr_dir = QFileInfo(dest_path)
        if not curr_dir.isWritable():
            MyDialog("Info", "The current folder is not writable: "+os.path.basename(dest_path), None)
            event.ignore()
            return
        if event.mimeData().hasUrls():
            event.accept()
            filePathsTemp = []
            # web address list
            webPaths = []
            #
            for uurl in event.mimeData().urls():
                # check if the element is a local file
                if uurl.isLocalFile():
                    filePathsTemp.append(str(uurl.toLocalFile()))
                else:
                    webUrl = uurl.url()
                    if webUrl[0:5] == "http:" or webUrl[0:6] == "https:":
                        webPaths.append(webUrl)
            # TO-DO for more than one item
            if webPaths:
                if len(webPaths) == 1:
                    path_to_store = dest_path
                    #
                    # pointedItem = self.indexAt(event.pos())
                    pointedItem = self.indexAt(event.position().toPoint())
                
                    if pointedItem.isValid():
                        ifp = self.model().data(pointedItem, QFileSystemModel.Roles.FilePathRole)
                        if os.path.isdir(ifp):
                            if os.access(ifp, os.W_OK):
                                path_to_store = ifp
                            else:
                                MyDialog("Info", "The following folder in not writable: "+os.path.basename(ifp), None)
                                event.ignore()
                                return
                    #
                    data_req = event.mimeData().html()
                    if data_req[0:4] == "<img":
                        event.accept()
                        dd1 = data_req.rfind("src=")
                        dd2 = data_req[dd1+5:].find('"')
                        data_path = str(data_req[dd1+5:dd1+dd2+5])
                        data_name = os.path.basename(data_path)
                        #
                        data_req = event.mimeData().data('application/octet-stream')
                        if not data_req.isEmpty():
                            with open(path_to_store+"/"+data_name, 'wb') as ff:
                                ff.write(data_req)
                        else:
                            event.ignore()
                            MyDialog("Info", "No data.", None)
                            return
                    else:
                        event.ignore()
                        MyDialog("Info", "Not supported.", None)
                        return
                #
                else:
                    event.ignore()
                    MyDialog("Info", "Not supported.", None)
                    return
            #
            filePaths = filePathsTemp
            # if not empty
            if filePaths:
                # pointedItem = self.indexAt(event.pos())
                pointedItem = self.indexAt(event.position().toPoint())
                #
                USER_HOME = os.path.expanduser("~")
                event_action = event.proposedAction()
                # into folder
                if pointedItem.isValid():
                    ifp = self.model().data(pointedItem, QFileSystemModel.Roles.FilePathRole)
                    # move the items if the pointer folder is in the HOME directory
                    if filePaths[0][0:len(USER_HOME)] == ifp[0:len(USER_HOME)]:
                        #
                        # if not is_wayland:
                        # pointedItem = self.tview.indexAt(position)
                        # position = event.pos()
                        position = event.position().toPoint()
                        #
                        menu = QMenu("Menu", self)
                        #
                        copyAction = QAction("Copy", self)
                        copyAction.uaction = "copy"
                        copyAction.triggered.connect(self.fdragdrop)
                        menu.addAction(copyAction)
                        #
                        moveAction = QAction("Move", self)
                        moveAction.uaction = "move"
                        moveAction.triggered.connect(self.fdragdrop)
                        menu.addAction(moveAction)
                        #
                        menu.addSeparator()
                        #
                        cancelAction = QAction("Cancel", self)
                        cancelAction.uaction = "cancel"
                        cancelAction.triggered.connect(self.fdragdrop)
                        menu.addAction(cancelAction)
                        #
                        menu.exec(self.mapToGlobal(position))
                        #
                        if self.user_action:
                            # event_action = self.user_action
                            if self.user_action == 1:
                                _event_action = Qt.DropAction.CopyAction
                            elif self.user_action == 2:
                                _event_action = Qt.DropAction.MoveAction
                        else:
                            event.ignore()
                            return
                        if os.path.isdir(ifp):
                            if os.access(ifp, os.W_OK):
                                PastenMerge(ifp, _event_action, filePaths, None)
                                return
                            else:
                                MyDialog("Info", "The following folder in not writable: "+os.path.basename(ifp), None)
                                return
                    #
                    if os.path.isdir(ifp):
                        if os.access(ifp, os.W_OK):
                            PastenMerge(ifp, event_action, filePaths, None)
                        else:
                            MyDialog("Info", "The following folder in not writable: "+os.path.basename(ifp), None)
                            return
                    # not folder
                    else:
                        PastenMerge(dest_path, event_action, filePaths, None)
                # background
                else:
                    PastenMerge(dest_path, event_action, filePaths, None)
            else:
                event.ignore()
        else:
            event.ignore()
    
    def fdragdrop(self):
        if self.sender().uaction == "copy":
            self.user_action = 1
        elif self.sender().uaction == "move":
            self.user_action = 2
    

class itemDelegate(QItemDelegate):

    def __init__(self, parent=None):
        super(itemDelegate, self).__init__(parent)
    
    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        iicon = index.data(QFileSystemModel.Roles.FileIconRole)
        if not iicon:
            return
        ppath = index.data(QFileSystemModel.Roles.FilePathRole)
        # additional icon text
        if USE_AD:
            iaddtext = index.data(34)
        else:
            iaddtext = None
        #
        painter.restore()
        #
        _is_thumb = 0
        if not iicon.name():
            pixmap = iicon.pixmap(QSize(THUMB_SIZE, THUMB_SIZE))
            _is_thumb = 1
        else:
            pixmap = iicon.pixmap(QSize(ICON_SIZE, ICON_SIZE))
        #
        pixel_ratio = pixmap.devicePixelRatio()
        #
        size_pixmap = pixmap.size()
        pw = int(size_pixmap.width()/pixel_ratio)
        ph = int(size_pixmap.height()/pixel_ratio)
        #
        xpad = int((ITEM_WIDTH - pw) / 2)
        ypad = int((ITEM_HEIGHT - ph) / 2)
        # # shadow
        # if USE_SHADOW and _is_thumb:
            # painter.save()
            # pen = QPen(QColor(0,0,0, 40))
            # pen.setWidth(6)
            # pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            # painter.setPen(pen)
            # x1 = option.rect.x() + xpad + 2
            # y1 = option.rect.y() + ypad + ph
            # x2 = x1 + pw - 4
            # y2 = y1
            # painter.drawLine(x1, y1, x2, y2)
            # #
            # pen = QPen(QColor(0,0,0, 160))
            # pen.setWidth(3)
            # pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            # painter.setPen(pen)
            # x1 = option.rect.x() + xpad + 1
            # y1 = option.rect.y() + ypad + ph
            # x2 = x1 + pw - 2
            # y2 = y1
            # painter.drawLine(x1, y1, x2, y2)
            # #
            # painter.restore()
        #
        painter.drawPixmap(int(option.rect.x() + xpad),int(option.rect.y() + ypad), -1,-1, pixmap,0,0,-1,-1)
        #
        # draw a colored border around the thumbnail image
        if USE_THUMB and USE_BORDERS == 2:
            # empiric method: draw a border if any name is not found
            if iicon.name() == "":
                painter.save()
                img_w = pw
                img_h = ph
                pen = QPen(QColor(BORDER_COLOR_R,BORDER_COLOR_G,BORDER_COLOR_B))
                pwidth = BORDER_WIDTH
                pen.setWidth(pwidth)
                painter.setPen(pen)
                painter.drawRect(option.rect.x() + xpad,option.rect.y() + ypad,pw-pwidth+BORDER_WIDTH,ph-pwidth+BORDER_WIDTH)
                painter.restore()
        #
        #
        # text color
        if TCOLOR == 2:
            painter.save()
            pen = QPen(QColor(TRED,TGREEN,TBLUE))
            painter.setPen(pen)
        # other text
        if iaddtext:
            st1 = QStaticText("<i>"+iaddtext+"</i>")
            st1.setTextWidth(ITEM_WIDTH)
            to1 = QTextOption(Qt.AlignmentFlag.AlignCenter)
            to1.setWrapMode(QTextOption.WrapMode.WrapAnywhere)
            st1.setTextOption(to1)
            st1.setTextFormat(Qt.TextFormat.RichText)
            painter.drawStaticText(option.rect.x(), option.rect.y()+ITEM_HEIGHT, st1)
            hh1 = st1.size().height()
        else:
            hh1 = 0
        #
        qstring = index.data(QFileSystemModel.Roles.FileNameRole)
        st = QStaticText(qstring)
        st.setTextWidth(ITEM_WIDTH)
        to = QTextOption(Qt.AlignmentFlag.AlignCenter)
        to.setWrapMode(QTextOption.WrapMode.WrapAnywhere)
        st.setTextOption(to)
        painter.drawStaticText(option.rect.x(), option.rect.y()+ITEM_HEIGHT+int(hh1), st)
        #
        if TCOLOR == 2:
            painter.restore()
        #
        if not os.path.isdir(ppath):
            if not index.data(QFileSystemModel.Roles.FilePermissions) & QFile.Permission.WriteUser.value or not index.data(QFileSystemModel.Roles.FilePermissions) & QFile.Permission.ReadUser.value:
                ppixmap = QPixmap('icons/emblem-readonly.svg').scaled(ICON_SIZE2, ICON_SIZE2, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
                painter.drawPixmap(option.rect.x(), int(option.rect.y()+ITEM_HEIGHT-ICON_SIZE2),-1,-1, ppixmap,0,0,-1,-1)
            #
            if os.path.islink(ppath):
                lpixmap = QPixmap('icons/emblem-symbolic-link.svg').scaled(ICON_SIZE2, ICON_SIZE2, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
                painter.drawPixmap(int(option.rect.x()+ITEM_WIDTH-ICON_SIZE2), int(option.rect.y()+ITEM_HEIGHT-ICON_SIZE2),-1,-1, lpixmap,0,0,-1,-1)
        else:
            if not index.data(QFileSystemModel.Roles.FilePermissions) & QFile.Permission.WriteUser.value or not index.data(QFileSystemModel.Roles.FilePermissions) & QFile.Permission.ReadUser.value or not index.data(QFileSystemModel.Roles.FilePermissions) & QFile.Permission.ExeOwner.value:
                ppixmap = QPixmap('icons/emblem-readonly.svg').scaled(ICON_SIZE2, ICON_SIZE2, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
                painter.drawPixmap(option.rect.x(), int(option.rect.y()+ITEM_HEIGHT-ICON_SIZE2),-1,-1, ppixmap,0,0,-1,-1)
            # link emblem
            if os.path.islink(ppath):
                lpixmap = QPixmap('icons/emblem-symbolic-link.svg').scaled(ICON_SIZE2, ICON_SIZE2, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
                painter.drawPixmap(int(option.rect.x()+ITEM_WIDTH-ICON_SIZE2), int(option.rect.y()+ITEM_HEIGHT-ICON_SIZE2),-1,-1, lpixmap,0,0,-1,-1)
        ## FJINE DAD FARE
        # # link icon
        # if os.path.islink(ppath):
        # lpixmap = QPixmap('icons/emblem-symbolic-link.svg').scaled(ICON_SIZE2, ICON_SIZE2, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
        # painter.drawPixmap(int(option.rect.x()+ITEM_WIDTH-ICON_SIZE2), int(option.rect.y()+ITEM_HEIGHT-ICON_SIZE2),-1,-1, lpixmap,0,0,-1,-1)
        #
        painter.save()
        if option.state & QStyle.StateFlag.State_Selected:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QColor(CIRCLE_COLOR))
            painter.setPen(QColor(CIRCLE_COLOR))
            painter.drawEllipse(QRect(option.rect.x()+1,option.rect.y()+1,CIRCLE_SIZE,CIRCLE_SIZE))
            # tick symbol
            painter.setPen(QColor(TICK_COLOR))
            text = '<div style="font-size:{}px">{}</div>'.format(TICK_SIZE, TICK_CHAR)
            st = QStaticText(text)
            tx = int(option.rect.x()+1+((CIRCLE_SIZE - st.size().width())/2))
            ty = int(option.rect.y()+1+((CIRCLE_SIZE - st.size().height())/2))
            painter.drawStaticText(tx, ty, st)
        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QColor(CIRCLE_COLOR))
            painter.setPen(QColor(CIRCLE_COLOR))
            painter.drawEllipse(QRect(option.rect.x()+1,option.rect.y()+1,CIRCLE_SIZE,CIRCLE_SIZE))
        painter.restore()
        
    
    def sizeHint(self, option, index):
        # additional text
        if USE_AD:
            iaddtext = index.data(34)
            st1 = QStaticText(iaddtext)
            st1.setTextWidth(ITEM_WIDTH)
            to1 = QTextOption(Qt.AlignmentFlag.AlignCenter)
            to1.setWrapMode(QTextOption.WrapMode.WrapAnywhere)
            st1.setTextOption(to1)
            hh1 = st1.size().height()
        else:
            hh1 = 0
        #
        qstring = index.data(QFileSystemModel.Roles.FileNameRole)
        st = QStaticText(qstring)
        st.setTextWidth(ITEM_WIDTH)
        to = QTextOption(Qt.AlignmentFlag.AlignCenter)
        to.setWrapMode(QTextOption.WrapMode.WrapAnywhere)
        st.setTextOption(to)
        ww = st.size().width()
        hh = st.size().height()
        return QSize(int(ww), int(hh)+int(hh1)+ITEM_HEIGHT+ITEM_HEIGHT_GAP)


# used for main
class IconProvider(QFileIconProvider):
    # # set the icon theme
    # if ICON_THEME:
        # QIcon.setThemeName(ICON_THEME)
    
    def evaluate_pixbuf(self, ifull_path, imime):
        hmd5 = "Null"
        hmd5 = create_thumbnail(ifull_path, imime)
        #
        file_icon = "Null"
        if hmd5 != "Null":
            file_icon = QIcon(QPixmap(XDG_CACHE_LARGE+"/"+str(hmd5)+".png"))
        #
        return file_icon
    
    
    def icon(self, fileInfo):
        if isinstance(fileInfo, QFileInfo):
            info = fileInfo
            ireal_path = os.path.realpath(fileInfo.absoluteFilePath())
            if fileInfo.exists():
                if fileInfo.isFile():
                    if search_for_file_type == 1:
                        imime = QMimeDatabase().mimeTypeForFile(ireal_path, QMimeDatabase.MatchMode.MatchDefault)
                    else:
                        imime = QMimeDatabase().mimeTypeForFile(ireal_path, QMimeDatabase.MatchMode.MatchContent)
                    #
                    if imime:
                        try:
                            if USE_THUMB == 1:
                                file_icon = self.evaluate_pixbuf(ireal_path, imime.name())
                                if file_icon != "Null":
                                    return file_icon
                                # else:
                            file_icon = QIcon.fromTheme(imime.iconName())
                            if not file_icon.isNull():
                                return file_icon
                            else:
                                file_icon = QIcon.fromTheme(imime.genericIconName())
                                if not file_icon.isNull():
                                    return file_icon
                                else:
                                    file_icon = QIcon.fromTheme("text-plain")
                                    if not file_icon.isNull():
                                        return file_icon
                                    else:
                                        pxmi = QPixmap("icons/empty.svg").scaled(ICON_SIZE, ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
                                        return QIcon(pxmi)
                            # else:
                                # file_icon = QIcon.fromTheme(imime.iconName())
                                # if not file_icon.isNull():
                                    # return file_icon
                                # else:
                                    # # return QIcon("icons/empty.svg")
                                    # pxmi = QPixmap("icons/empty.svg").scaled(ICON_SIZE, ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
                                    # return QIcon(pxmi)
                        except:
                            file_icon = QIcon.fromTheme("text-plain")
                            if not file_icon.isNull():
                                return file_icon
                            else:
                                pxmi = QPixmap("icons/empty.svg").scaled(ICON_SIZE, ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
                                return QIcon(pxmi)
                #
                elif fileInfo.isDir():
                    # use custom icons
                    if USE_FOL_CI:
                        if fileInfo.exists():
                            ireal_path = os.path.realpath(fileInfo.absoluteFilePath())
                            # exists the file .directory in the dir - set the custom icon
                            dir_path = os.path.join(ireal_path, ".directory")
                            icon_name = None
                            # only for home dir
                            if os.path.exists(dir_path) and dir_path[0:6] == "/home/":
                                try:
                                    with open(dir_path,"r") as f:
                                        dcontent = f.readlines()
                                    for el in dcontent:
                                        if "Icon=" in el:
                                            icon_name = el.split("=")[1].strip("\n")
                                            break
                                except:
                                    icon_name = None
                            #
                            if icon_name:
                                icon_name_path = os.path.join(ireal_path, icon_name)
                                if os.path.exists(icon_name_path):
                                    return QIcon(icon_name_path)
                                else:
                                    return QIcon.fromTheme("folder")
                    # 
                    if os.path.dirname(os.path.realpath(fileInfo.absoluteFilePath())) == os.path.expanduser("~"):
                        if FILE_DIRS:
                            for _ddir in FILE_DIRS:
                                if fileInfo.fileName().lower() == _ddir[0].lower():
                                    _user_dir_name = _ddir[1]
                                    if QIcon.hasThemeIcon(_user_dir_name):
                                        return QIcon.fromTheme(_user_dir_name)
                    #
                    if QIcon.hasThemeIcon("folder-{}".format(fileInfo.fileName().lower())):
                        return QIcon.fromTheme("folder-{}".format(fileInfo.fileName().lower()), QIcon.fromTheme("folder"))
                    else:
                        return QIcon.fromTheme("folder", QIcon("icons/folder.svg"))
                    # 
                    # # if QIcon.hasThemeIcon("folder-{}".format(fileInfo.fileName().lower())):
                        # # return QIcon.fromTheme("folder-{}".format(fileInfo.fileName().lower()), QIcon.fromTheme("folder"))
                    # # elif fileInfo.fileName() == "Desktop":
                        # # return QIcon.fromTheme("folder_home", QIcon.fromTheme("folder"))
                    # # elif fileInfo.fileName() == "Public":
                        # # return QIcon.fromTheme("folder-publicshare", QIcon.fromTheme("folder"))
                    # # else:
                        # # return QIcon.fromTheme("folder", QIcon("icons/folder.svg"))
            else:
                file_icon = QIcon.fromTheme("text-plain")
                if not file_icon.isNull():
                    return file_icon
                else:
                    pxmi = QPixmap("icons/empty.svg").scaled(ICON_SIZE, ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
                    return QIcon(pxmi)
        return super(IconProvider, self).icon(fileInfo)

########################### MAIN WINDOW ############################

# 1
class MainWin(QWidget):
    
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        #
        self.setWindowIcon(QIcon("icons/file-manager-blue.svg"))
        #
        if FOLDER_TO_OPEN == "HOME":
            HOME = os.path.expanduser('~')
        else:
            if os.path.exists(FOLDER_TO_OPEN):
                if os.access(FOLDER_TO_OPEN, os.R_OK):
                    HOME = FOLDER_TO_OPEN
                else:
                    HOME = os.path.expanduser('~')
            else:
                HOME = os.path.expanduser('~')
        #
        self.resize(int(WINW), int(WINH))
        if WINM == "True":
            self.showMaximized()
        #
        self.setWindowTitle("SimpleFM6")
        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), "icons", "file-manager-blue.svg")))
        #
        # main box
        self.vbox = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.vbox.setContentsMargins(QMargins(2,2,2,2))
        self.setLayout(self.vbox)
        # tool box - 
        self.obox1 = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.obox1.setContentsMargins(QMargins(0,0,0,0))
        self.vbox.addLayout(self.obox1)
        #### buttons
        # home button
        hbtn = QPushButton(QIcon.fromTheme("user-home"), None)
        if TOOLBAR_BUTTON_SIZE:
            hbtn.setIconSize(QSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE))
        hbtn.setToolTip("Home")
        hbtn.clicked.connect(lambda:self.openDir(HOME, 1))
        self.obox1.addWidget(hbtn, 0, Qt.AlignmentFlag.AlignLeft)
        # root button
        rootbtn = QPushButton(QIcon.fromTheme("computer"), None)
        if TOOLBAR_BUTTON_SIZE:
            rootbtn.setIconSize(QSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE))
        rootbtn.setToolTip("Computer")
        rootbtn.clicked.connect(lambda:self.openDir("/", 1))
        self.obox1.addWidget(rootbtn, 0, Qt.AlignmentFlag.AlignLeft)
        #
        # trash button
        global USE_TRASH
        if USE_TRASH:
            # check the Trash folder and its subfolders exist
            trash_path = os.path.join(os.path.expanduser("~"), ".local/share/Trash")
            if not os.path.exists(trash_path):
                try:
                    os.makedirs(os.path.join(trash_path, "expunged"))
                    os.makedirs(os.path.join(trash_path, "files"))
                    os.makedirs(os.path.join(trash_path, "info"))
                except:
                    USE_TRASH = 0
        if USE_TRASH:
            self.tbtn = QPushButton(QIcon.fromTheme("user-trash"), None)
            if TOOLBAR_BUTTON_SIZE:
                self.tbtn.setIconSize(QSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE))
            self.tbtn.setToolTip("Recycle Bin")
            self.obox1.addWidget(self.tbtn, 0, Qt.AlignmentFlag.AlignLeft)
            if not isXDGDATAHOME:
                self.tbtn.setEnabled(False)
            else:
                self.tbtn.clicked.connect(lambda:openTrash(self, "HOME"))
            #
            # check for changes in the trash directories
            fPath = [os.path.join(trash_module.mountPoint("HOME").find_trash_path(), "files")]
            self.fileSystemWatcher = QFileSystemWatcher(fPath)
            self.fileSystemWatcher.directoryChanged.connect(self.checkTrash)
            #
            # check the trash state: empty or not empty
            self.checkTrash()
        #
        # show treeview of the current folder
        if ALTERNATE_VIEW:
            altBtn = QPushButton(QIcon("icons/alternate.svg"), "")
            if TOOLBAR_BUTTON_SIZE:
                altBtn.setIconSize(QSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE))
            altBtn.setToolTip("Alternate view")
            altBtn.clicked.connect(self.faltview)
            self.obox1.addWidget(altBtn, 0, Qt.AlignmentFlag.AlignLeft)
        #
        ### the bookmark menu
        self.bookmarkBtn = QPushButton(QIcon("icons/bookmarks.svg"), "")
        if TOOLBAR_BUTTON_SIZE:
            self.bookmarkBtn.setIconSize(QSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE))
        self.obox1.addWidget(self.bookmarkBtn)
        self.bookmarkBtnMenu = QMenu()
        self.bookmarkBtnMenu.setToolTipsVisible(True)
        self.bookmarkBtn.setMenu(self.bookmarkBtnMenu)
        # populate
        self.on_setBtnBookmarks()
        #
        ## a new device has been added or removed
        if USE_MEDIA:
            from dbus.mainloop.pyqt6 import DBusQtMainLoop
            # box for media devices
            self.disk_box = QBoxLayout(QBoxLayout.Direction.LeftToRight)
            self.disk_box.setContentsMargins(QMargins(0,0,0,0))
            self.obox1.addLayout(self.disk_box) #, Qt.AlignmentFlag.AlignRight)
            #
            DBusQtMainLoop(set_as_default=True)
            self.bus = dbus.SystemBus()
            #
            self.proxy = self.bus.get_object("org.freedesktop.UDisks2", "/org/freedesktop/UDisks2")
            #
            self.iface = dbus.Interface(self.proxy, "org.freedesktop.DBus.ObjectManager")
            #
            #
            self.iface.connect_to_signal('InterfacesAdded', self.device_added_callback)
            self.iface.connect_to_signal('InterfacesRemoved', self.device_removed_callback)
            #
            self.on_pop_devices()
            #
        # close buttons
        qbtn = QPushButton(QIcon.fromTheme("window-close"), "")
        if BUTTON_SIZE:
            qbtn.setIconSize(QSize(BUTTON_SIZE, BUTTON_SIZE))
        qbtn.setToolTip("Exit")
        qbtn.clicked.connect(self.close)
        self.obox1.addWidget(qbtn, 1, Qt.AlignmentFlag.AlignRight)
        ####
        self.mtab = QTabWidget()
        self.mtab.setContentsMargins(QMargins(0,0,0,0))
        self.mtab.setMovable(True)
        self.mtab.setElideMode(Qt.TextElideMode.ElideRight)
        self.mtab.setTabsClosable(True)
        self.mtab.tabCloseRequested.connect(self.closeTab)
        #
        self.vbox.addWidget(self.mtab)
        #### autostart
        for el in list_custom_modules[:]:
            if el.__name__[0:10] == "autostart_":
                if el.mmodule_type(self) == 6:
                    try:
                        el.ModuleCustom(self)
                        list_custom_modules.remove(el)
                    except Exception as E:
                        MyDialog("Error", str(E), self)
        ####
        parg = ""
        self._lvFile = None
        # self._scroll_listview = None
        # self._scroll_idx = None
        if len(sys.argv) > 1:
            parg = sys.argv[1]
            # remove the last slash character if useless
            if parg != "trash://" and len(parg) > 1 and parg[-1] == "/":
                parg = parg[:-1]
            #
            # for i in range(1, len(sys.argv) -1):
                # parg += sys.argv[i]+" "
            # parg += sys.argv[len(sys.argv) - 1]
        # if parg != "" and parg != "/":
            # if parg[-1] == "/":
                # parg = parg[0:-1]
        #
        if os.path.dirname(parg) == "":
            self.openDir(HOME, 1)
        elif parg == "trash://":
            if USE_TRASH:
                openTrash(self, "HOME")
            else:
                self.openDir(HOME, 1)
        else:
            # "//" is not a directory
            if len(parg) > 1 and parg.strip("/") == "":
                parg = ""
            if os.path.exists(parg) and os.access(parg, os.R_OK):
                self.openDir(parg, 1)
            else:
                # get a message if the item is missing
                self._lvFile = os.path.basename(parg)
                # cycle throu the path backward to find an existent or accessible directory
                path = os.path.dirname(parg)
                while not os.path.exists(path) or not os.access(path, os.R_OK):
                    path = os.path.dirname(path)
                    if path == "":
                        path = HOME
                        break
                #
                self.openDir(path, 1)
        # for closing open tabs
        self.device_mountPoint = []

    
    # check its state: empty or not empty
    def checkTrash(self):
        trash_path = os.path.join(os.path.expanduser("~"), ".local/share/Trash")
        tmp = os.listdir(os.path.join(trash_path, "files"))
        if tmp:
            trash_icon = QIcon.fromTheme("user-trash-full")
        else:
            trash_icon = QIcon.fromTheme("user-trash")
        self.tbtn.setIcon(trash_icon)
    
    
    # add a new connected device
    def device_added_callback(self, *args):
        for k in args[1]:
            kk = "org.freedesktop.UDisks2.Filesystem"
            if k == kk:
                mobject = self.iface.GetManagedObjects()
                self.on_add_partition(args[0], mobject[args[0]])
    
    
    # remove the disconnected device
    def device_removed_callback(self, *args):
        for k in args[1]:
            kk = "org.freedesktop.UDisks2.Filesystem"
            if k == kk:
                for i in range(self.disk_box.count()):
                    item = self.disk_box.itemAt(i).widget()
                    if isinstance(item, QPushButton):
                        if item.menu():
                            if item.menu().block_device == args[0]:
                                item.deleteLater()
                                # close the tabs
                                for el in self.device_mountPoint[:]:
                                    if el[0] == item.menu().device:
                                        self.close_open_tab(el[1])
                                        self.device_mountPoint.remove(el)
                                break
                
    
    # get all the partitions at start
    def on_pop_devices(self):
        mobject = self.iface.GetManagedObjects()
        for k in mobject:
            #
            if "loop" in k:
                continue
            if 'ram' in k:
                continue
            #
            for ky in  mobject[k]:
                kk = "org.freedesktop.UDisks2.Block"
                if  str(ky) == kk:
                    bd = self.bus.get_object('org.freedesktop.UDisks2', k)
                    file_system =  bd.Get('org.freedesktop.UDisks2.Block', 'IdType', dbus_interface='org.freedesktop.DBus.Properties')
                    if file_system:
                        self.on_add_partition(k, mobject[k])
                        break
    
    # the device is added to the view
    # def on_add_partition(self, k, bus, kmobject):
    def on_add_partition(self, k, kmobject):
        for ky in kmobject:
            kk = "org.freedesktop.UDisks2.Block"
            if  str(ky) == kk:
                bd = self.bus.get_object('org.freedesktop.UDisks2', k)
                #
                drive = bd.Get('org.freedesktop.UDisks2.Block', 'Drive', dbus_interface='org.freedesktop.DBus.Properties')
                #
                if str(drive) == "/":
                    continue
                # 
                if "org.freedesktop.UDisks2.PartitionTable" in kmobject.keys():
                    continue
                #
                pdevice = bd.Get('org.freedesktop.UDisks2.Block', 'Device', dbus_interface='org.freedesktop.DBus.Properties')
                pdevice_dec = bytearray(pdevice).replace(b'\x00', b'').decode('utf-8')
                # skip unwanted device in the bar
                if pdevice_dec in MEDIA_SKIP:
                    continue
                #
                # do not show the disk in which the OS has been installed, and the boot partition
                ret_mountpoint = self.get_device_mountpoint(str(pdevice_dec))
                if ret_mountpoint == "/" or ret_mountpoint[0:5] == "/boot" or ret_mountpoint[0:5] == "/home":
                    continue
                #
                label = bd.Get('org.freedesktop.UDisks2.Block', 'IdLabel', dbus_interface='org.freedesktop.DBus.Properties')
                #
                size = bd.Get('org.freedesktop.UDisks2.Block', 'Size', dbus_interface='org.freedesktop.DBus.Properties')
                #
                ### 
                bd2 = self.bus.get_object('org.freedesktop.UDisks2', drive)
                #
                media_type = bd2.Get('org.freedesktop.UDisks2.Drive', 'Media', dbus_interface='org.freedesktop.DBus.Properties')
                if not media_type:
                    media_type = "N"
                #
                is_optical = bd2.Get('org.freedesktop.UDisks2.Drive', 'Optical', dbus_interface='org.freedesktop.DBus.Properties')
                #
                media_available = bd2.Get('org.freedesktop.UDisks2.Drive', 'MediaAvailable', dbus_interface='org.freedesktop.DBus.Properties')
                #
                if media_available == 0:
                    if not is_optical:
                        continue
                #
                conn_bus = bd2.Get('org.freedesktop.UDisks2.Drive', 'ConnectionBus', dbus_interface='org.freedesktop.DBus.Properties')
                #
                vendor = bd2.Get('org.freedesktop.UDisks2.Drive', 'Vendor', dbus_interface='org.freedesktop.DBus.Properties')
                model = bd2.Get('org.freedesktop.UDisks2.Drive', 'Model', dbus_interface='org.freedesktop.DBus.Properties')
                #
                if str(label):
                    disk_name = str(label)
                else:
                    if str(vendor) and str(model):
                        disk_name = str(vendor)+" - "+str(model)+" - "+str(convert_size(size))
                    elif str(vendor):
                        disk_name = str(vendor)+" - "+str(convert_size(size))
                    elif str(model):
                        disk_name = str(model)+" - "+str(convert_size(size))
                    else:
                        disk_name = str(pdevice_dec)+" - "+str(convert_size(size))
                #
                if is_optical:
                    drive_type = 5 # 0 disk - 5 optical
                else:
                    drive_type = 0 # 0 disk - 5 optical
                #
                dicon = self.getDevice(media_type, drive_type, conn_bus)
                #
                media_btn = QPushButton(QIcon(dicon),"")
                if TOOLBAR_BUTTON_SIZE:
                    media_btn.setIconSize(QSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE))
                self.disk_box.addWidget(media_btn)
                media_btn.setToolTip(disk_name)
                media_btn_menu = QMenu()
                media_btn_menu.block_device = k
                media_btn_menu.device = str(pdevice_dec)
                media_btn_menu.drive = drive
                media_btn.setMenu(media_btn_menu)
                media_btn_menu.aboutToShow.connect(self.btn_menu_open)

    
    # before the menu opens
    def btn_menu_open(self):
        self.on_populate_mediaBtn()

    
    # populate the media button
    def on_populate_mediaBtn(self):
        self.sender().clear()
        # get the device mount point
        ddevice = self.sender().device
        ddrive = self.sender().drive
        block_device = self.sender().block_device
        ret_mountpoint = self.get_device_mountpoint(ddevice)
        # if ret_mountpoint == "/" or ret_mountpoint[0:5] == "/boot" or ret_mountpoint[0:5] == "/home":
            # baction = self.sender().addAction("Property", lambda:self.media_property(block_device, ret_mountpoint, ddrive, ddevice))
            # return
        if ret_mountpoint == "N":
            baction = self.sender().addAction("Open", lambda:self.open_device(ret_mountpoint, ddevice))
            baction = self.sender().addAction("Mount", lambda:self.mount_device(ret_mountpoint, ddevice))
        else:
            baction = self.sender().addAction("Open", lambda:self.open_device(ret_mountpoint, ddevice))
            baction = self.sender().addAction("Unmount", lambda:self.mount_device(ret_mountpoint, ddevice))
        # the device is ejectable
        ret_eject = self.get_device_can_eject(ddrive)
        if ret_eject:
            baction = self.sender().addAction("Eject", lambda:self.eject_media(ddrive, ret_mountpoint, ddevice))
        # property
        baction = self.sender().addAction("Property", lambda:self.media_property(block_device, ret_mountpoint, ddrive, ddevice))
    
    # open the folder
    def open_device(self, mountpoint, ddevice):
        # first mount the device
        if mountpoint == "N":
            ret = self.mount_device(mountpoint, ddevice)
            if ret == -1:
                MyDialog("Info", "The device cannot be mounted.", self)
                return
            else:
                mountpoint = ret
        #
        if mountpoint:
            self.openDir(mountpoint, 1)
            self.device_mountPoint.append([ddevice, mountpoint])
    
    # close the open tabs
    def close_open_tab(self, mountpoint):
        num_tabs = self.mtab.count()
        for i in reversed(range(num_tabs)):
            if self.mtab.tabToolTip(i)[0:len(mountpoint)] == mountpoint:
                self.mtab.widget(i).deleteLater()
                self.mtab.removeTab(i)
        #
        num_tabs = self.mtab.count()
        # open one tab if any
        if num_tabs == 0:
            self.openDir(os.path.expanduser('~'), 1)
    
    # mount - unmount the device
    def mount_device(self, mountpoint, ddevice):
        if mountpoint == "N":
            ret = self.on_mount_device(ddevice, 'Mount')
            if ret == -1:
                MyDialog("Info", "The device cannot be mounted.", self)
                return 
        else:
            ret = self.on_mount_device(ddevice, 'Unmount')
            if ret == -1:
                # MyDialog("Info", "The device cannot be unmounted.", self)
                MyDialog("Info", "Device busy.", self)
                return -1
            # close the open tabs
            if ret == None:
                self.close_open_tab(mountpoint)
        #
        return ret
                
    
    # self.mount_device
    def on_mount_device(self, ddevice, operation):
        ddev = ddevice.split("/")[-1]
        progname = 'org.freedesktop.UDisks2'
        objpath = os.path.join('/org/freedesktop/UDisks2/block_devices', ddev)
        intfname = 'org.freedesktop.UDisks2.Filesystem'
        try:
            obj  = self.bus.get_object(progname, objpath)
            intf = dbus.Interface(obj, intfname)
            # return the mount point or None if unmount
            ret = intf.get_dbus_method(operation, dbus_interface='org.freedesktop.UDisks2.Filesystem')([])
            return ret
        except:
            return -1
    
    # eject the media
    def eject_media(self, ddrive, mountpoint, ddevice):
        # first unmount if the case
        if mountpoint != "N":
            ret = self.mount_device(mountpoint, ddevice)
            if ret == -1:
                # MyDialog("Info", "Device busy.", self)
                return
        # 
        bd2 = self.bus.get_object('org.freedesktop.UDisks2', ddrive)
        can_poweroff = bd2.Get('org.freedesktop.UDisks2.Drive', 'CanPowerOff', dbus_interface='org.freedesktop.DBus.Properties')
        # 
        ret = self.on_eject(ddrive)
        if ret == -1:
            MyDialog("Info", "The device cannot be ejected.", self)
            return
        #
        if can_poweroff:
            try:
                ret = self.on_poweroff(ddrive)
                # if ret == -1:
                    # MyDialog("Info", "The device cannot be turned off.", self)
            except:
                pass
        # # close the open tabs
        # self.close_open_tab(mountpoint)
    
    # self.eject_media
    def on_eject(self, ddrive):
        progname = 'org.freedesktop.UDisks2'
        objpath  = ddrive
        intfname = 'org.freedesktop.UDisks2.Drive'
        try:
            methname = 'Eject'
            obj  = self.bus.get_object(progname, objpath)
            intf = dbus.Interface(obj, intfname)
            ret = intf.get_dbus_method(methname, dbus_interface='org.freedesktop.UDisks2.Drive')([])
            return ret
        except:
            return -1
    
    # self.eject_media1
    def on_poweroff(self, ddrive):
        progname = 'org.freedesktop.UDisks2'
        objpath  = ddrive
        intfname = 'org.freedesktop.UDisks2.Drive'
        try:
            methname = 'PowerOff'
            obj  = self.bus.get_object(progname, objpath)
            intf = dbus.Interface(obj, intfname)
            ret = intf.get_dbus_method(methname, dbus_interface='org.freedesktop.UDisks2.Drive')([])
            return ret
        except:
            return -1
    
    # get the device mount point
    def get_device_mountpoint(self, ddevice):
        ddev = ddevice.split("/")[-1]
        mount_point = self.on_get_mounted(ddev)
        return mount_point
    
    # the device is ejectable
    def get_device_can_eject(self, drive):
        bd2 = self.bus.get_object('org.freedesktop.UDisks2', drive)
        # try:
        can_eject = bd2.Get('org.freedesktop.UDisks2.Drive', 'Ejectable', dbus_interface='org.freedesktop.DBus.Properties')
        # except Exception as E:
            # # return False
            # return 1
        return can_eject
    
    # get the mount point or return N
    def on_get_mounted(self, ddev):
        path = os.path.join('/org/freedesktop/UDisks2/block_devices/', ddev)
        bd = self.bus.get_object('org.freedesktop.UDisks2', path)
        try:
            mountpoint = bd.Get('org.freedesktop.UDisks2.Filesystem', 'MountPoints', dbus_interface='org.freedesktop.DBus.Properties')
            if mountpoint:
                mountpoint = bytearray(mountpoint[0]).replace(b'\x00', b'').decode('utf-8')
                return mountpoint
            else:
                return "N"
        except:
            return "N"
    
    # the device properties
    def media_property(self, k, mountpoint, ddrive, ddevice):
        bd = self.bus.get_object('org.freedesktop.UDisks2', k)
        label = bd.Get('org.freedesktop.UDisks2.Block', 'IdLabel', dbus_interface='org.freedesktop.DBus.Properties')
        bd2 = self.bus.get_object('org.freedesktop.UDisks2', ddrive)
        vendor = bd2.Get('org.freedesktop.UDisks2.Drive', 'Vendor', dbus_interface='org.freedesktop.DBus.Properties')
        model = bd2.Get('org.freedesktop.UDisks2.Drive', 'Model', dbus_interface='org.freedesktop.DBus.Properties')
        size = bd.Get('org.freedesktop.UDisks2.Block', 'Size', dbus_interface='org.freedesktop.DBus.Properties')
        file_system =  bd.Get('org.freedesktop.UDisks2.Block', 'IdType', dbus_interface='org.freedesktop.DBus.Properties')
        read_only = bd.Get('org.freedesktop.UDisks2.Block', 'ReadOnly', dbus_interface='org.freedesktop.DBus.Properties')
        ### 
        media_type = bd2.Get('org.freedesktop.UDisks2.Drive', 'Media', dbus_interface='org.freedesktop.DBus.Properties')
        if not media_type:
            conn_bus = bd2.Get('org.freedesktop.UDisks2.Drive', 'ConnectionBus', dbus_interface='org.freedesktop.DBus.Properties')
            if conn_bus:
                media_type = conn_bus
            else:
                media_type = "N"
        #
        if not label:
            label = "(Not set)"
        if mountpoint == "N":
            mountpoint = "(Not mounted)"
            device_size = str(convert_size(size))
        else:
            mountpoint_size = convert_size(psutil.disk_usage(mountpoint).used)
            device_size = str(convert_size(size))+" - ("+mountpoint_size+")"
        if not vendor:
            vendor = "(None)"
        if not model:
            model = "(None)"
        data = [label, vendor, model, device_size, file_system, bool(read_only), mountpoint, ddevice, media_type]
        devicePropertyDialog(data, self)
        
        
    # get the device icon
    def getDevice(self, media_type, drive_type, connection_bus):
        if "flash" in media_type:
            return "icons/media-flash.svg"
        if "optical" in media_type:
            return "icons/media-optical.svg"
        if connection_bus == "usb" and drive_type == 0:
            return "icons/media-removable.svg"
        if drive_type == 0:
            return "icons/drive-harddisk.svg"
        elif drive_type == 5:
            return "icons/media-optical.svg"
        #
        return "icons/drive-harddisk.svg"
    
    #
    def showEvent(self, event):
        if self._lvFile:
            if not os.path.exists(self._lvFile):
                MyDialog("Error", "Cannot be found:\n{}".format(self._lvFile), self)
                self._lvFile = None
            # else:
                # self._scroll_listview.selectionModel().select(self._scroll_idx, QItemSelectionModel.SelectionFlag.Select)
                # self._scroll_listview.scrollTo(self._scroll_idx, QAbstractItemView.ScrollHint.EnsureVisible)
                # self._scroll_listview = None
                # self._scroll_idx = None
    
    #
    def closeEvent(self, event):
        self.on_close()
    
    #
    def on_close(self):
        new_w = self.size().width()
        new_h = self.size().height()
        if new_w != int(WINW) or new_h != int(WINH):
            # WINW = width
            # WINH = height
            # WINM = maximized
            isMaximized = self.isMaximized()
            if isMaximized == True and WINM == "True":
                QApplication.instance().quit()
                return
            #
            try:
                ifile = open("winsize.cfg", "w")
                if isMaximized:
                    if WINM == "False":
                        ifile.write("{};{};{}".format(WINW, WINH, isMaximized))
                else:
                    ifile.write("{};{};False".format(new_w, new_h))
                ifile.close()
            except Exception as E:
                MyDialog("Error", str(E), self)
        QApplication.instance().quit()
    
    
    # populate the bookmarks
    def on_setBtnBookmarks(self):
        fb = open("Bookmarks", "r")
        fbdata = fb.readlines()
        fb.close()
        #
        for item in fbdata:
            path = item.strip("\n")
            baction = self.bookmarkBtnMenu.addAction(os.path.basename(path), self.on_bookmark_action)
            baction.setToolTip(path)
    
    # add a bookmark to its menu
    def setBtnBookmarks(self, path):
        try:
            fb = open("Bookmarks", "a")
            fb.write(path+"\n")
            fb.close()
            baction = self.bookmarkBtnMenu.addAction(os.path.basename(path), self.on_bookmark_action)
            baction.setToolTip(path)
        except Exception as E:
            MyDialog("Error", str(E), self)
    
    # remove the bookmark
    def unsetBtnBookmarks(self, path):
        try:
            fb = open("Bookmarks", "r")
            fbdata = fb.readlines()
            fb.close()
            fbdata.remove(path+"\n")
            fb = open("Bookmarks", "w")
            for iitem in fbdata:
                fb.write(iitem)
            fb.close()
            for iitem in self.bookmarkBtnMenu.actions():
                if iitem.toolTip() == path:
                    self.bookmarkBtnMenu.removeAction(iitem)
                    break
        except Exception as E:
            MyDialog("Error", str(E), self)
    
    # the bookmark action - or remove the useless bookmark
    def on_bookmark_action(self):
        bpath = self.sender().toolTip()
        if os.path.exists(bpath):
            self.openDir(bpath, 1)
        # the bookmark points to a missed folder
        else:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Icon.Question)
            msgBox.setWindowTitle("Question")
            msgtext = "The folder\n{}\ndoesn't exist anymore.\nDo you want to remove its bookmark?".format(bpath)
            msgBox.setText(msgtext)
            msgBox.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            #
            returnValue = msgBox.exec()
            if returnValue == QMessageBox.StandardButton.Ok:
                try:
                    fb = open("Bookmarks", "r")
                    fbdata = fb.readlines()
                    fb.close()
                except Exception as E:
                    MyDialog("Error", str(E), self)
                    return
                # remove the bookmark
                for item in fbdata[:]:
                    if bpath == item.strip("\n"):
                        fbdata.remove(item)
                        self.bookmarkBtnMenu.removeAction(self.sender())
                        break
                # update the file
                try:
                    fb = open("Bookmarks", "w")
                    for item in fbdata:
                        fb.write(item)
                    fb.close()
                except Exception as E:
                    MyDialog("Error", str(E), self)
                    return
            else:
                return
    
    # open a new folder - used also by computer and home buttons
    def openDir(self, ldir, flag):
        page = QWidget()
        if not os.path.exists(ldir):
            ldir = "/"
            clv = LView(ldir, self, flag)
        else:
            folder_to_open = ""
            if os.path.isdir(ldir):
                fpath = ldir
                folder_to_open = os.path.basename(fpath)
                if not folder_to_open:
                    if fpath == "/":
                        folder_to_open = "Root"
            else:
                fpath = os.path.dirname(ldir)
                folder_to_open = os.path.basename(fpath)
            #
            self.mtab.addTab(page, folder_to_open or "Root")
            self.mtab.setTabToolTip(self.mtab.count()-1, fpath)
            #
            clv = LView(ldir, self, flag)
        page.setLayout(clv)
        self.mtab.setCurrentIndex(self.mtab.count()-1)
        
    
    def closeTab(self, index):
        if self.mtab.count() > 1:
            if  self.mtab.tabText(index) == "Media":
                global TCOMPUTER
                TCOMPUTER = 0
            #
            if self.mtab.tabText(index) == "Recycle Bin - Home":
                global TrashIsOpen
                TrashIsOpen = 0
            #
            self.mtab.removeTab(index)
    
    # open the current folder into the alternate view
    def faltview(self):
        flag = 1
        # the dir to open
        ldir = self.mtab.tabToolTip(self.mtab.currentIndex())
        page = QWidget()
        if not os.path.exists(ldir):
            ldir = "/"
            clv = cTView(ldir, self, flag)
        else:
            if os.path.isdir(ldir):
                self.mtab.addTab(page, os.path.basename(ldir) or "ROOT")
                self.mtab.setTabToolTip(self.mtab.count()-1, ldir)
            elif os.path.isfile(ldir) or os.path.islink(ldir):
                self.mtab.addTab(page, os.path.basename(os.path.dirname(ldir)) or "ROOT")
                self.mtab.setTabToolTip(self.mtab.count()-1, os.path.dirname(ldir))
            else:
                ldir = os.path.dirname(ldir)
                self.mtab.addTab(page, os.path.basename(ldir) or "ROOT")
                self.mtab.setTabToolTip(self.mtab.count()-1, ldir)
            clv = cTView(ldir, self, flag)
        #
        page.setLayout(clv)
        self.mtab.setCurrentIndex(self.mtab.count()-1)


# simple info dialog
class devicePropertyDialog(QDialog):
    def __init__(self, data, parent):
        super(devicePropertyDialog, self).__init__(parent)
        self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        self.setWindowTitle("Device Properties")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.resize(dialWidth,100)
        # data = [label, vendor, model, size, file_system, read_only, mountpoint, ddevice, media_type]
        self.data = data
        #
        grid = QGridLayout()
        grid.setContentsMargins(5,5,5,5)
        #
        label0 = QLabel("<i>Label</i>")
        grid.addWidget(label0, 1, 0, Qt.AlignmentFlag.AlignLeft)
        label0_data = QLabel(data[0])
        grid.addWidget(label0_data, 1, 1, Qt.AlignmentFlag.AlignLeft)
        #
        label1 = QLabel("<i>Vendor</i>")
        grid.addWidget(label1, 2, 0, Qt.AlignmentFlag.AlignLeft)
        label1_data = QLabel(data[1])
        grid.addWidget(label1_data, 2, 1, Qt.AlignmentFlag.AlignLeft)
        #
        label2 = QLabel("<i>Model</i>")
        grid.addWidget(label2, 3, 0, Qt.AlignmentFlag.AlignLeft)
        label2_data = QLabel(data[2])
        grid.addWidget(label2_data, 3, 1, Qt.AlignmentFlag.AlignLeft)
        #
        label3 = QLabel("<i>Size (Used)</i>")
        grid.addWidget(label3, 4, 0, Qt.AlignmentFlag.AlignLeft)
        label3_data = QLabel(data[3])
        grid.addWidget(label3_data, 4, 1, Qt.AlignmentFlag.AlignLeft)
        #
        label4 = QLabel("<i>File System</i>")
        grid.addWidget(label4, 5, 0, Qt.AlignmentFlag.AlignLeft)
        label4_data = QLabel(data[4])
        grid.addWidget(label4_data, 5, 1, Qt.AlignmentFlag.AlignLeft)
        #
        label5 = QLabel("<i>Read Only</i>")
        grid.addWidget(label5, 6, 0, Qt.AlignmentFlag.AlignLeft)
        label5_data = QLabel(str(data[5]))
        grid.addWidget(label5_data, 6, 1, Qt.AlignmentFlag.AlignLeft)
        #
        label6 = QLabel("<i>Mount Point</i>")
        grid.addWidget(label6, 7, 0, Qt.AlignmentFlag.AlignLeft)
        label6_data = QLabel(data[6])
        grid.addWidget(label6_data, 7, 1, Qt.AlignmentFlag.AlignLeft)
        #
        label7 = QLabel("<i>Device</i>")
        grid.addWidget(label7, 8, 0, Qt.AlignmentFlag.AlignLeft)
        label7_data = QLabel(data[7])
        grid.addWidget(label7_data, 8, 1, Qt.AlignmentFlag.AlignLeft)
        #
        label8 = QLabel("<i>Media Type</i>")
        grid.addWidget(label8, 9, 0, Qt.AlignmentFlag.AlignLeft)
        label8_data = QLabel(data[8])
        grid.addWidget(label8_data, 9, 1, Qt.AlignmentFlag.AlignLeft)
        #
        button_ok = QPushButton("     Ok     ")
        grid.addWidget(button_ok, 12, 0, 1, 2, Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(grid)
        button_ok.clicked.connect(self.close)
        self.exec()
    
    # def closeEvent(self, event):
        # self.deleteLater()


# for LView
class QFileSystemModel2(QFileSystemModel):
    
    def columnCount(self, parent = QModelIndex()):
        if USE_AD:
            return super(QFileSystemModel2, self).columnCount()+3
        else:
            return super(QFileSystemModel2, self).columnCount()+2

    def data(self, index, role):
        # additional text
        if USE_AD:
            if role == (34):
                return fcit(index.data(Qt.ItemDataRole.UserRole + 1))
        return super(QFileSystemModel2, self).data(index, role)


# path button box
class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=1):
        super(FlowLayout, self).__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        # to verify
        return Qt.Orientation(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, int(width), 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margin, _, _, _ = self.getContentsMargins()
        size += QSize(2 * margin, 2 * margin)
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        #
        for item in self.itemList:
            wid = item.widget()
            if wid == None:
                continue
            spaceX = self.spacing() + wid.style().layoutSpacing(QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            #
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            #
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        return y + lineHeight - rect.y()

# function for executing the command
def _flaunch_prog(r_defApp, path, USE_TERM):
    _has_arg = 0
    try:
        if len(r_defApp) > 1:
            _has_arg = 2
            for eel in r_defApp[:]:
                if eel == "%f":
                    ridx = r_defApp.index(eel)
                    r_defApp[ridx] = path
                    _has_arg = 1
                    break
                elif eel == "%F":
                    ridx = r_defApp.index(eel)
                    r_defApp[ridx] = path
                    _has_arg = 1
                    break
                elif eel == "%u":
                    ridx = r_defApp.index(eel)
                    r_defApp[ridx] = "file://"+path
                    _has_arg = 1
                    break
                elif eel == "%U":
                    ridx = r_defApp.index(eel)
                    r_defApp[ridx] = "file://"+path
                    _has_arg = 1
                    break
        # 
        if _has_arg == 2:
            MyDialog("Info", "Cannot open the file this way:\n{}.".format(r_defApp), None) 
            return
        elif _has_arg == 0:
            r_defApp.append(path)
        #
        if USE_TERM:
            subprocess.Popen([USER_TERMINAL, "-e"]+r_defApp)
        else:
            subprocess.Popen(r_defApp)
    except Exception as E:
        MyDialog("Error", str(E), None)        


class LView(QBoxLayout):
    # dir/file to open - MainWin - flag: 1 new tab - 0 same tab
    def __init__(self, TLVDIR, window, flag, parent=None):
        super(LView, self).__init__(QBoxLayout.Direction.TopToBottom, parent)
        self.window = window
        self.flag = flag
        self.setContentsMargins(QMargins(0,0,0,0))
        self.setSpacing(0)
        self.lvDir = "/"
        # the file passed as argument - half implemented
        self.lvFile = ""
        #
        if TLVDIR != "/":
            if os.path.exists(TLVDIR):
                if os.path.isdir(TLVDIR):
                    self.lvDir = TLVDIR
                elif os.path.isfile(TLVDIR) or os.path.islink(TLVDIR):
                    self.lvDir = os.path.dirname(TLVDIR)
                    self.lvFile = os.path.basename(TLVDIR)
                else:
                    self.lvDir = os.path.dirname(TLVDIR)
        #
        #### history and buttons box
        self.bhicombo = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.bhicombo.setContentsMargins(QMargins(0,0,0,0))
        self.bhicombo.setSpacing(0)
        #
        # history of the opened folders (of the current view)
        self.insertLayout(0, self.bhicombo)
        #
        # button change history/scroll
        self.change_btn = QPushButton(QIcon("icons/alternate.svg"), "")
        self.change_btn.setToolTip("Switch history/buttons")
        if BUTTON_SIZE:
            self.change_btn.setIconSize(QSize(BUTTON_SIZE, BUTTON_SIZE))
        self.change_btn.setCheckable(True)
        self.change_btn.clicked.connect(self.on_change_btn)
        self.bhicombo.addWidget(self.change_btn)
        #
        _step = 30
        self.buttonbar_left_btn = QPushButton(QIcon("icons/go-previous-symbolic.svg"), "")
        self.buttonbar_left_btn.setToolTip("Scroll to left")
        self.buttonbar_left_btn.clicked.connect(lambda:self.on_buttonbar_action(-1*_step))
        self.bhicombo.addWidget(self.buttonbar_left_btn)
        #
        self.buttonbar_right_btn = QPushButton(QIcon("icons/go-next-symbolic.svg"), "")
        self.buttonbar_right_btn.setToolTip("Scroll to right")
        self.buttonbar_right_btn.clicked.connect(lambda:self.on_buttonbar_action(_step))
        self.bhicombo.addWidget(self.buttonbar_right_btn)
        if BUTTON_SIZE:
            self.buttonbar_left_btn.setIconSize(QSize(BUTTON_SIZE, BUTTON_SIZE))
            self.buttonbar_left_btn.setMaximumWidth(self.buttonbar_left_btn.iconSize().width())
            self.buttonbar_right_btn.setIconSize(QSize(BUTTON_SIZE, BUTTON_SIZE))
            self.buttonbar_right_btn.setMaximumWidth(self.buttonbar_right_btn.iconSize().width())
        #
        self.hicombo = QComboBox()
        self.hicombo.setEditable(True)
        if BUTTON_SIZE:
            self.hicombo.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        if FLOW_WIDGET == 1:
            self.hicombo.hide()
        self.bhicombo.addWidget(self.hicombo, 1)
        self.hicombo.activated.connect(self.fhbmenuction)
        self.hicombo.insertItem(0, self.lvDir)
        self.hicombo.setCurrentIndex(0)
        #
        ### path button box
        self.scroll_widget = QWidget()
        self.scroll_widget.setContentsMargins(QMargins(0,0,0,0))
        #
        self.scroll_layout = QHBoxLayout()
        self.scroll_layout.setContentsMargins(QMargins(0,0,0,0))
        self.scroll_layout.setSpacing(0)
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll = QScrollArea()
        self.scroll.setFrameStyle(0)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.installEventFilter(self)
        self.scroll.setContentsMargins(QMargins(0,0,0,0))
        self.scroll.setObjectName("taskscrollarea")
        self.scroll.setStyleSheet("#taskscrollarea {border: 0px solid; padding: 0px; margin: 0px;}")
        self.scroll.setWidgetResizable(True)
        self.scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        self.scroll.setWidget(self.scroll_widget)
        self.box_pb = self.scroll_layout
        #
        if FLOW_WIDGET == 0:
            self.scroll.hide()
            self.buttonbar_left_btn.hide()
            self.buttonbar_right_btn.hide()
        self.bhicombo.addWidget(self.scroll, 1)
        #
        self.on_box_pb(self.lvDir)
        #
        if FLOW_WIDGET == 0:
            self.change_btn.setChecked(True)
        ####
        ####
        # self.fmf = 0
        self.selection = None
        self.listview = MyQlist()
        self.listview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.listview.setViewMode(QListView.ViewMode.IconMode)
        #
        # the background color
        if USE_BACKGROUND_COLOUR == 1:
            palette = self.listview.palette()
            palette.setColor(QPalette.ColorRole.Base, QColor(ORED,OGREEN,OBLUE))
            self.listview.setPalette(palette)
        #
        self.listview.setSpacing(ITEM_SPACE)
        self.listview.setSelectionMode(self.listview.SelectionMode.ExtendedSelection)
        self.listview.setResizeMode(QListView.ResizeMode.Adjust)
        self.addWidget(self.listview, 1)
        if USE_AD:
            self.fileModel = QFileSystemModel2()
        else:
            self.fileModel = QFileSystemModel()
        self.fileModel.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot | QDir.Filter.System)
        self.listview.setModel(self.fileModel)
        self.listview.viewport().setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.listview.setItemDelegate(itemDelegate())
        self.fileModel.setIconProvider(IconProvider())
        #
        self.listview.setRootIndex(self.fileModel.setRootPath(self.lvDir))
        self.listview.clicked.connect(self.singleClick)
        self.listview.doubleClicked.connect(self.doubleClick)
        # clear the selection after loading a new directory
        self.fileModel.rootPathChanged.connect(self.on_dir_changed)
        self.fileModel.directoryLoaded.connect(self.on_dir_loaded)
        # double click check
        self._pp = 0
        #
        self.label2 = QLabel()
        self.label3 = QLabel()
        self.label6 = QLabel()
        self.label6.setWordWrap(True)
        self.label6.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label7 = QLabel()
        self.label8 = QLabel()
        #
        self.page1UI()
        #
        self.listview.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.listview.customContextMenuRequested.connect(self.onRightClick)
        #
        self.listview.selectionModel().selectionChanged.connect(self.lselectionChanged)
        #
        self.tabLabels()
        #
        if USE_TRASH:
            self.clickable2(self.listview).connect(self.itemsToTrash)
        elif USE_DELETE:
            self.clickable2(self.listview).connect(self.fdeleteAction)
        # # OPTIONALLY DISABLED
        # if USE_THUMB == 1:
            # thread = thumbThread(self.lvDir, self.listview)
            # thread.start()
        #
        # # highlight the file passed as argument
        # if self.lvFile:
            # index = self.fileModel.index(os.path.join(self.lvDir, self.lvFile))
            # self.listview.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select)
            # # scroll to it
            # self.listview.scrollTo(index, QAbstractItemView.ScrollHint.EnsureVisible)
            # self.lvFile = None
        #
        # catch the middle button click from the mouse
        self.listview.viewport().installEventFilter(self)
        # the button pressed in self.box_pb
        self.box_pb_btn = None
        # item are added in the selected item list if clicked at its top-left position
        self.static_items = False
        # a file has been added - hidden items are still skipped
        self.fileModel.rowsInserted.connect(self.rowInserted)
        self.fileModel.rowsRemoved.connect(self.rowRemoved)
        
    def on_buttonbar_action(self, _value):
        # self.scroll.horizontalScrollBar().setValue( self.scroll.horizontalScrollBar().value()+_value )
        if _value > 0:
            _max = self.scroll.horizontalScrollBar().maximum()
            self.scroll.horizontalScrollBar().setValue( self.scroll.horizontalScrollBar().value()+_max )
        elif _value < 0:
            _min = self.scroll.horizontalScrollBar().minimum()
            self.scroll.horizontalScrollBar().setValue( _min )
        
    def on_change_btn(self):
        if self.sender().isChecked():
            self.hicombo.show()
            self.scroll.hide()
            self.buttonbar_left_btn.hide()
            self.buttonbar_right_btn.hide()
        else:
            self.hicombo.hide()
            self.scroll.show()
            self.buttonbar_left_btn.show()
            self.buttonbar_right_btn.show()
    
    # the root dir is changed
    def on_dir_changed(self, _path):
        if _path == self.lvDir:
            return
        # disable the selection mode
        self.listview.setSelectionMode(self.listview.SelectionMode.NoSelection)
        
    def _f_on_dir_loaded(self):
        # enable again the selection mode
        self.listview.setSelectionMode(self.listview.SelectionMode.ExtendedSelection)
        
    # the dir finished to be loaded
    def on_dir_loaded(self, _path):
        if _path == self.lvDir:
            # highlight the file passed as argument
            if self.lvFile:
                index = self.fileModel.index(os.path.join(self.lvDir, self.lvFile))
                self.listview.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select)
                # scroll to it
                self.listview.scrollTo(index, QAbstractItemView.ScrollHint.EnsureVisible)
                #
                # if not os.path.exists(self.lvFile):
                    # MyDialog("Error", "Cannot be found:\n{}".format(self.lvFile), self.window)
                #
                self.lvFile = None
            return
        # the previous folder
        upperdir = self.lvDir
        # the new root dir
        self.lvDir = _path
        # scroll to top
        self.listview.verticalScrollBar().setValue(0)
        # tab name and tooltip
        self.window.mtab.setTabText(self.window.mtab.currentIndex(), os.path.basename(self.lvDir))
        self.window.mtab.setTabToolTip(self.window.mtab.currentIndex(), self.lvDir)
        # add the path into the history
        self.hicombo.insertItem(0, self.lvDir)
        self.hicombo.setCurrentIndex(0)
        #
        self.tabLabels()
        # path button box
        if self._pp == 1:
            self.on_box_pb(self.lvDir)
            self._pp = 0
            #
            _timer = QTimer()
            # deselect eventually selection after a dir change - empiric method
            _timer.singleShot(500, self._f_on_dir_loaded)
        elif self._pp == 2:
            self._pp = 0
            self._f_on_dir_loaded()
        #
        # highlight the previous folder
        _ln_lvdir = len(self.lvDir)
        _other = upperdir[_ln_lvdir:]
        if upperdir[0:_ln_lvdir] == self.lvDir:
            # if _other:
                # upperdir = upperdir[0:_ln_lvdir]+"/"+_other.split("/")[1]
            #
            if os.path.exists(upperdir):
                index = self.fileModel.index(upperdir)
                # select the item - scroll to it - skip hidden folders
                if not index.data(QFileSystemModel.Roles.FileNameRole)[0] == ".":
                    self.listview.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select)
                    self.listview.scrollTo(index, QAbstractItemView.ScrollHint.EnsureVisible)
                    # self.window._scroll_listview = self.listview
                    # self.window._scroll_idx = index
    #
    def rowInserted(self, idx):
        self.tabLabels()
        
    #
    def rowRemoved(self, idx):
        self.tabLabels()
    
    # change the dir throu the button in the path bar
    def on_change_dir(self, path):
        if os.access(path, os.R_OK):
            try:
                self.listview.clearSelection()
                # self.lvDir = path
                # self.window.mtab.setTabText(self.window.mtab.currentIndex(), os.path.basename(self.lvDir))
                # self.window.mtab.setTabToolTip(self.window.mtab.currentIndex(), self.lvDir)
                self.listview.setRootIndex(self.fileModel.setRootPath(path))
                # self.tabLabels()
                # # scroll to top
                # self.listview.verticalScrollBar().setValue(0)
                # # add the path into the history
                # self.hicombo.insertItem(0, self.lvDir)
                # self.hicombo.setCurrentIndex(0)
                # return 1
                self._pp = 2
                return 1
            except Exception as E:
                MyDialog("Error", str(E), self.window)
                return -1
        else:
            MyDialog("Error", path+"\n\n   Not readable", self.window)
            return 0
    
    # see on_box_pb
    def btn_change_dir(self):
        # ppath = []
        # for i in range(self.box_pb.count()):
            # item = self.box_pb.itemAt(i)
            # if isinstance(item.widget(), QPushButton):
                # ppath.append(item.widget().text())
                # if i == self.sender().ind:
                    # break
        # #
        # new_path = os.path.join(*ppath)
        #
        new_path = self.sender()._path
        # #
        # if os.path.exists(new_path):
            # if new_path != self.lvDir:
                # self.on_btn_change_dir(new_path)
        # else:
            # MyDialog("Info", "The folder \n{}\ndoes not exist.".format(new_path), self.window)
        #
        if new_path != self.lvDir:
            self.on_btn_change_dir(new_path)
        
    # see btn_change_dir
    def on_btn_change_dir(self, new_path):
        if os.path.exists(new_path) and os.path.isdir(new_path):
            # 1 success 0 not readable -1 error
            ret = self.on_change_dir(new_path)
            # if not change directory the previous button will be rechecked
            # VERIFY
            if ret == 1:
                self.sender().setChecked(True)
                self.box_pb_btn = self.sender()
            else:
                self.box_pb_btn.setChecked(True)
        else:
            self.box_pb_btn.setChecked(True)
            MyDialog("Info", "The folder \n{}\ndoes not exist.".format(new_path), self.window)
    
    # populate the path buttons box
    def on_box_pb(self, ddir):
        # empty the box
        for i in reversed(range(self.box_pb.count())):
            item = self.box_pb.itemAt(i).widget()
            item.deleteLater()
        # repopulate
        if ddir == "/":
            ppath = ["/"]
        else:
            ppath = ddir.split("/")
        # remove the last empty item
        if len(ppath) > 1 and ppath[-1] in ["","."]:
            ppath.pop()
        #
        ppath_len = len(ppath)
        for p in range(0, ppath_len):
            if p == 0:
                # pb = QPushButton(QIcon("icons/drive-harddisk.svg"), "/")
                pb = QPushButton(QIcon("icons/drive-harddisk.svg"), "")
                # set the index as button attribute
                pb.ind = 0
                pb._path = "/"
                if BUTTON_SIZE:
                    pb.setIconSize(QSize(BUTTON_SIZE, BUTTON_SIZE))
                pb.setMaximumWidth(pb.iconSize().width()+4)
                pb.setToolTip("Root")
            else:
                pb = QPushButton(ppath[p])
                pb.ind = p
                pb._path = "/".join( ppath[0:p+1] )
                if BUTTON_SIZE:
                    pb.setIconSize(QSize(BUTTON_SIZE, BUTTON_SIZE))
            pb.setAutoExclusive(True)
            pb.setCheckable(True)
            pb.clicked.connect(self.btn_change_dir)
            pb.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
            self.box_pb.addWidget(pb)
            pb.installEventFilter(self)
            pb.setObjectName('pbwidget')
            #
            if p == (ppath_len -1):
                pb.setChecked(True)
                self.box_pb_btn = pb
        #
        _max = self.scroll.horizontalScrollBar().maximum()
        self.scroll.horizontalScrollBar().setValue( self.scroll.horizontalScrollBar().value()+_max )
        
    #
    def fhbmenuction(self, idx):
        path = self.hicombo.itemText(idx)
        # open the folder in a new tab
        if os.path.exists(path):
            if os.access(path, os.R_OK):
                self.window.openDir(path, 1)
                return
        #
        MyDialog("Error", "Folder not readable", self.window)
    
    #
    def eventFilter(self, obj, event):
        # if FLOW_WIDGET:
        if event.type() == QEvent.Type.Wheel and obj is self.scroll:
            ddelta = event.angleDelta()
            hbar = self.scroll.horizontalScrollBar()
            hbar.setValue(hbar.value()-ddelta.y())
            return True
        # # the shift key is been pressed
        # modifiers = QApplication.keyboardModifiers()
        # if (modifiers & Qt.KeyboardModifier.ShiftModifier):
            # print("shift")
            # return True
        # 
        # select items continuosly without deselecting the others
        if event.type() == QEvent.Type.MouseButtonPress:
            if not hasattr(event, "button"):
                return False
            #
            if event.button() == Qt.MouseButton.LeftButton:
                # itemIdx = self.listview.indexAt(event.pos())
                itemIdx = self.listview.indexAt(event.position().toPoint())
                item_rect = self.listview.visualRect(itemIdx)
                # item selected at top-left
                topLeft = QRect(item_rect.x(), item_rect.y(), CIRCLE_SIZE, CIRCLE_SIZE)
                # if event.pos() in topLeft:
                if event.position().toPoint() in topLeft:
                    self.static_items = True
                    self.listview.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
                else:
                    if self.static_items == True:
                        self.static_items = False
                        self.listview.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
            # open the folder with the mouse middle button
            elif event.button() == Qt.MouseButton.MiddleButton:
                # button box
                if obj.objectName() == 'pbwidget':
                    # new_path_temp = []
                    # for i in range(self.box_pb.indexOf(obj)+1):
                        # new_path_temp.append(self.box_pb.itemAt(i).widget().text())
                    # new_path = os.path.join(*new_path_temp)
                    new_path = obj._path
                    if os.path.exists(new_path):
                        # # open the folder in the same view
                        # self.on_btn_change_dir(new_path)
                        # obj.setChecked(True)
                        try:
                            # open the selected folder in a new tab
                            self.fnewtabAction(new_path, 1)
                        except Exception as E:
                            MyDialog("Error", str(E), self.window)
                    else:
                        MyDialog("Info", "The folder \n{}\ndoes not exist.".format(new_path), self.window)
                    #
                    return QObject.event(obj, event)
                # else:
                    # # folders
                    # # itemSelected = self.listview.indexAt(event.pos()).data()
                    # itemSelected = self.listview.indexAt(event.position().toPoint()).data()
                    # if itemSelected:
                        # itemSelectedPath = os.path.join(self.lvDir, itemSelected)
                        # if os.path.isdir(itemSelectedPath):
                            # if os.access(itemSelectedPath, os.R_OK):
                                # if IN_SAME == 1:
                                    # try:
                                        # # open the selected folder in a new tab
                                        # self.fnewtabAction(itemSelectedPath, 1)
                                    # except Exception as E:
                                        # MyDialog("Error", str(E), self.window)
                                # else:
                                    # # open the selected folder in the same tab
                                    # try:
                                        # self.listview.clearSelection()
                                        # # self.lvDir = itemSelectedPath
                                        # _lvDir = itemSelectedPath
                                        # # self.window.mtab.setTabText(self.window.mtab.currentIndex(), os.path.basename(self.lvDir))
                                        # # self.window.mtab.setTabToolTip(self.window.mtab.currentIndex(), self.lvDir)
                                        # # self.listview.setRootIndex(self.fileModel.setRootPath(self.lvDir))
                                        # self.listview.setRootIndex(self.fileModel.setRootPath(_lvDir))
                                        # # self.tabLabels()
                                        # # # scroll to top
                                        # # self.listview.verticalScrollBar().setValue(0)
                                        # # # add the path into the history
                                        # # self.hicombo.insertItem(0, self.lvDir)
                                        # # self.hicombo.setCurrentIndex(0)
                                        # # #
                                        # # self.on_box_pb(self.lvDir)
                                        # self._pp = 1
                                    # except Exception as E:
                                        # MyDialog("Error", str(E), self.window)
                            # else:
                                # MyDialog("Info", itemSelected+"\nNot readable", self.window)
        #
        return QObject.event(obj, event)

    #  send to trash or delete the selected items - function
    def itemsToTrash(self):
        if self.selection:
            # only items in the HOME dir or in mass storages
            len_home = len(os.path.expanduser("~"))
            if self.lvDir[0:len_home] == os.path.expanduser("~") or self.flag in [3,4]:
                  self.ftrashAction()
    
    # send to trash or delete the selected items
    def clickable2(self, widget):
        class Filter(QObject):
            clicked = pyqtSignal()
            def eventFilter(self, obj, event):
                if obj == widget:
                    if event.type() == QEvent.Type.KeyRelease:
                        if event.key() == Qt.Key.Key_Delete:
                            self.clicked.emit()
                return False
        #
        filter = Filter(widget)
        widget.installEventFilter(filter)
        return filter.clicked
    
    # status bar - current folder content
    def tabLabels(self):
        if not os.path.exists(self.lvDir):
            self.label2.setText("<i>Unreadable</i>")
            self.label6.setText("")
            self.label3.setText("")
            self.label7.setText("")
            self.label8.setText("")
        else:
            self.label2.setText("<i>Items </i>")
            num_items, hidd_items = self.num_itemh(self.lvDir)
            self.label6.setText(str(num_items)+"    ")
            self.label3.setText("<i>Hiddens </i>")
            self.label7.setText(str(hidd_items))
            self.label8.setText("")
    
    # return the amount of the visible items and the hidden items
    def num_itemh(self, ddir):
        file_folder = os.listdir(ddir)
        total_item = len(file_folder)
        for el in file_folder[:]:
            if el.startswith("."):
              file_folder.remove(el)
        visible_item = len(file_folder)
        hidden_item = total_item - visible_item
        return visible_item, hidden_item
    
    def page1UI(self):
        upbtn = QPushButton()
        upbtn.setIcon(QIcon(QPixmap("icons/go-up.svg")))
        if BUTTON_SIZE:
            upbtn.setIconSize(QSize(BUTTON_SIZE, BUTTON_SIZE))
        # upbtn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        upbtn.setToolTip("go up")
        upbtn.clicked.connect(self.upButton)
        self.bhicombo.addWidget(upbtn)
        #
        invbtn = QPushButton()
        if BUTTON_SIZE:
            invbtn.setIconSize(QSize(BUTTON_SIZE, BUTTON_SIZE))
        invbtn.setIcon(QIcon(QPixmap("icons/invert.svg")))
        # invbtn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        invbtn.clicked.connect(self.finvbtn)
        invbtn.setToolTip("Invert the selection")
        self.bhicombo.addWidget(invbtn)
        #
        self.hidbtn = QPushButton()
        self.hidbtn.setCheckable(True)
        if BUTTON_SIZE:
            self.hidbtn.setIconSize(QSize(BUTTON_SIZE, BUTTON_SIZE))
        self.hidbtn.setIcon(QIcon(QPixmap("icons/hidden.svg")))
        # self.hidbtn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.hidbtn.clicked.connect(self.fhidbtn)
        self.hidbtn.setToolTip("Show the hidden Items")
        self.bhicombo.addWidget(self.hidbtn)
        # status box
        hboxd = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        hboxd.setContentsMargins(QMargins(0,0,0,0))
        hboxd.addWidget(self.label2)
        hboxd.addWidget(self.label6) #items #size
        hboxd.addWidget(self.label3)
        hboxd.addWidget(self.label7) #hidden #mimetype
        hboxd.addWidget(self.label8) #broken link - unrecognizabel - etc.
        hboxd.addStretch(1)
        #
        self.insertLayout(3, hboxd)
    
    #
    def singleClick(self, index):
        time.sleep(0.1)
        self.label2.setText("")
        self.label3.setText("")
        self.label6.setText("") #size
        self.label7.setText("") #mimetype
        self.label8.setText("") #broken link - unrecognizabel - etc.
        #
        path = self.fileModel.fileInfo(index).absoluteFilePath()
        file_info = QFileInfo(path)
        #
        if os.path.islink(path):
            real_path = os.path.realpath(path)
            if os.path.exists(real_path):
                # mimetype
                imime = QMimeDatabase().mimeTypeForFile(real_path, QMimeDatabase.MatchMode.MatchDefault)
                self.label7.setText(imime.name())
            # size
            if os.path.isfile(real_path):
                if os.access(real_path, os.R_OK):
                    self.label6.setText(convert_size(file_info.size())+"    ")
                else:
                    self.label6.setText("(Not readable)"+"    ")
            elif os.path.isdir(real_path):
                if os.access(real_path, os.R_OK):
                    # self.label6.setText(str(QDir(path).count()-2))
                    num_items, hidd_items = self.num_itemh(real_path)
                    self.label2.setText("<i>Items </i>")
                    self.label6.setText(str(num_items)+"    ")
                    self.label3.setText("<i>Hiddens </i>")
                    self.label7.setText(str(hidd_items))
                else:
                    self.label6.setText("(Not readable)"+"    ")
            # link - broken link
            real_path_short = real_path
            if len(real_path) > 50:
                real_path_short = real_path[0:23]+"..."+real_path[-24:]
            if not os.path.exists(real_path):
                # self.label8.setText("Broken link to: {}".format(real_path_short))
                self.label8.setText("Broken link")
            else:
                # self.label8.setText("<i>&nbsp;&nbsp;&nbsp;&nbsp;Link to</i>: {}".format(real_path_short))
                self.label8.setText("<i>&nbsp;&nbsp;&nbsp;&nbsp;Link type</i>")
        elif os.path.isfile(path):
            # mimetype
            imime = QMimeDatabase().mimeTypeForFile(path, QMimeDatabase.MatchMode.MatchDefault)
            self.label7.setText(imime.name())
            # size
            if os.access(path, os.R_OK):
                self.label6.setText(convert_size(file_info.size())+"    ")
            else:
                self.label6.setText("(Not readable)"+"    ")
        elif os.path.isdir(path):
            # mimetype
            imime = QMimeDatabase().mimeTypeForFile(path, QMimeDatabase.MatchMode.MatchDefault)
            self.label7.setText(imime.name())
            # item count
            if os.access(path, os.R_OK):
                num_items, hidd_items = self.num_itemh(path)
                self.label2.setText("<i>Items </i>")
                self.label6.setText(str(num_items)+"    ")
                self.label3.setText("<i>Hiddens </i>")
                self.label7.setText(str(hidd_items))
            else:
                self.label6.setText("(Not readable)"+"    ")
        else:
            try:
                # mimetype
                imime = QMimeDatabase().mimeTypeForFile(path, QMimeDatabase.MatchMode.MatchDefault)
                self.label7.setText(imime.name())
            except: pass
        #
        # self.listview.viewport().update()
    
    # double click
    def doubleClick(self, index):
        path = self.fileModel.fileInfo(index).absoluteFilePath()
        if not os.path.exists(path):
            MyDialog("Info", "It doesn't exist.", self.window)
            return
        if os.path.isdir(path):
            if os.access(path, os.R_OK):
                try:
                    self.listview.clearSelection()
                    # self.lvDir = path
                    # self.window.mtab.setTabText(self.window.mtab.currentIndex(), os.path.basename(self.lvDir))
                    # self.window.mtab.setTabToolTip(self.window.mtab.currentIndex(), self.lvDir)
                    self.listview.setRootIndex(self.fileModel.setRootPath(path))
                    # self.tabLabels()
                    # # scroll to top
                    # self.listview.verticalScrollBar().setValue(0)
                    # # add the path into the history
                    # self.hicombo.insertItem(0, self.lvDir)
                    # self.hicombo.setCurrentIndex(0)
                    # #
                    # self.on_box_pb(self.lvDir)
                    #
                    self._pp = 1
                except Exception as E:
                    MyDialog("Error", str(E), self.window)
                    self._pp = 0
            else:
                MyDialog("Info", path+"\n\n   Not readable", self.window)
        #
        elif os.path.isfile(path):
            perms = QFileInfo(path).permissions()
            imime = QMimeDatabase().mimeTypeForFile(path, QMimeDatabase.MatchMode.MatchDefault).name()
            # executable file
            if imime == "application/x-desktop":
                ret = execfileDialog(path, 0, self.window).getValue()
                if ret == 2:
                    # desktop file
                    _onlyShowIn = DesktopEntry(path).getOnlyShowIn()
                    _de = None
                    try:
                        _de = os.environ['XDG_CURRENT_DESKTOP'].lower()
                    except KeyError:
                        try:
                            _de = os.environ['XDG_SESSION_DESKTOP'].lower()
                        except KeyError:
                            try:
                                _de = os.environ['WINDOW_MANAGER'].lower()
                            except:
                                pass
                    #
                    _de_found = 2
                    if _onlyShowIn:
                        _de_found = 0
                        for eel in _onlyShowIn:
                            if eel.lower() == _de:
                                _de_found = 1
                                break
                    if _de_found == 0:
                        MyDialog("Info", "Cannot execute this file.", self.window)
                        return
                    #
                    progExec = DesktopEntry(path).getExec()
                    progTryExec = DesktopEntry(path).getTryExec()
                    progPath = DesktopEntry(path).getPath()
                    progTerm = DesktopEntry(path).getTerminal()
                    #
                    if shutil.which(progExec):
                        if progTerm:
                            TTERM = None
                            if USER_TERMINAL:
                                TTERM = USER_TERMINAL
                            try:
                                TTERM = os.environ["TERMINAL"]
                            except KeyError:
                                pass
                            #
                            if not TTERM:
                                MyDialog("Info", "No terminal found or setted.", self.window)
                                return
                            #
                            try:
                                if progPath:
                                    # os.system("cd {0} && {1} -e {2}".format(progPath, TTERM, progExec))
                                    os.system("cd {0}".format(progPath))
                                # else
                                subprocess.Popen([TTERM, "-e", progExec])
                            except Exception as E:
                                MyDialog("Error", str(E), self.window)
                        else:
                            try:
                                if progPath:
                                    # os.system("cd {0} && {1}".format(progPath, progExec))
                                    os.system("cd {0}".format(progPath))
                                # else:
                                subprocess.Popen([progExec])
                            except Exception as E:
                                MyDialog("Error", str(E), self.window)
                    else:
                        MyDialog("Info", "{} not found.".format(progExec), self.window)
                    return
            #
            if (perms & QFile.Permission.ExeOwner):
                imime = QMimeDatabase().mimeTypeForFile(path, QMimeDatabase.MatchMode.MatchDefault).name()
                if imime == "application/x-sharedlib":
                    ret = execfileDialog(path, 1, self.window).getValue()
                else:
                    ret = execfileDialog(path, 0, self.window).getValue()
                #
                if ret == 2:
                    try:
                        subprocess.Popen(path, shell=True, cwd=os.path.dirname(path))
                    except Exception as E:
                        MyDialog("Error", str(E), self.window)
                    finally:
                        return
                elif ret == -1:
                    return
            #
            defApp = getDefaultApp(path).defaultApplication()
            #
            listPrograms = getAppsByMime(os.path.join(self.lvDir, path)).appByMime()
            USE_TERM = False
            #
            if defApp != "None":
                #
                if listPrograms:
                    for iprog in listPrograms:
                        # if iprog[2]:
                        if iprog[0] == defApp:
                            USE_TERM = DesktopEntry(iprog[2]).getTerminal()
                        # # skip programs working in terminal - bool True or False
                        # if USE_TERM:
                            # return
                        break
                # execute the command
                r_defApp = defApp.split(" ")
                # self._flaunch_prog(r_defApp, path, USE_TERM)
                _flaunch_prog(r_defApp, path, USE_TERM)
            else:
                MyDialog("Info", "No programs found.", self.window)
    
    # # function for executing the command
    # def _flaunch_prog(self, r_defApp, path, USE_TERM):
        # try:
            # for eel in r_defApp[:]:
                # if eel == "%f":
                    # ridx = r_defApp.index(eel)
                    # r_defApp[ridx] = path
                    # break
                # elif eel == "%F":
                    # ridx = r_defApp.index(eel)
                    # r_defApp[ridx] = path
                    # break
                # elif eel == "%u":
                    # ridx = r_defApp.index(eel)
                    # r_defApp[ridx] = "file://"+path
                    # break
                # elif eel == "%U":
                    # ridx = r_defApp.index(eel)
                    # r_defApp[ridx] = "file://"+path
                    # break
            # #
            # if USE_TERM:
                # subprocess.Popen([USER_TERMINAL, "-e"]+r_defApp)
            # else:
                # subprocess.Popen(r_defApp)
        # except Exception as E:
            # MyDialog("Error", str(E), self.window)
    
    #
    def lselectionChanged(self):
        self.selection = self.listview.selectionModel().selectedIndexes()
        if self.selection == []:
            self.tabLabels()
        else:
            self.label2.setText("<i>Selected Items </i>")
            self.label6.setText(str(len(self.selection)))
            self.label3.setText("")
            self.label7.setText("")
            self.label8.setText("")
        ###########
        # if len(self.selection) == 1:
            # return
        # if self.selection == []:
            # self.tabLabels()
        #
        # else:
            # total_size = 0
            # for iitem in self.selection:
                # path = self.fileModel.fileInfo(iitem).absoluteFilePath()
                # #
                # if os.path.islink(path):
                    # # just a number
                    # total_size += 512
                # elif os.path.isfile(path):
                    # total_size += QFileInfo(path).size()
                # elif os.path.isdir(path):
                    # total_size += folder_size(path)
                # else:
                    # # just a number
                    # total_size += 512
            # self.label2.setText("<i>Selected Items </i>")
            # self.label6.setText(str(len(self.selection)))
            # self.label3.setText("<i>&nbsp;&nbsp;&nbsp;&nbsp;Size </i>")
            # self.label7.setText(str(convert_size(total_size)))
            # self.label8.setText("")
    
    # mouse right click on the pointed item
    def onRightClick(self, position):
        if self.flag == 0:
            return
        time.sleep(0.2)
        #
        if self.selection:
            if self.selection[0] == None:
                return
        #
        pointedItem = self.listview.indexAt(position)
        vr = self.listview.visualRect(pointedItem)
        if pointedItem.isValid() and not vr:
            return
        pointedItem2 = self.listview.indexAt(QPoint(int(vr.x()),int(vr.y())))
        # in case of sticky selection
        if self.static_items == True:
            self.static_items = False
            self.listview.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
            if pointedItem2 and not pointedItem2 in self.selection:
                # deselect all
                self.listview.clearSelection()
                self.selection = [pointedItem2]
                # select the item
                self.listview.setCurrentIndex(pointedItem2)
        # the items
        if vr:
            # the data of the selected item at the bottom
            self.singleClick(pointedItem)
            #
            itemName = self.fileModel.data(pointedItem2, Qt.ItemDataRole.DisplayRole)
            menu = QMenu("Menu", self.listview)
            if MENU_H_COLOR:
                csaa = "QMenu { "
                csab = "background: {}".format(QPalette.ColorRole.Window)
                csac = "; margin: 1px; padding: 5px 5px 5px 5px;}"
                csad = " QMenu::item:selected { "
                csae = "background-color: {};".format(MENU_H_COLOR)
                csaf = " padding: 10px;}"
                # padding: 1 top - 2 right - 3 bottom - 4 left
                csag = " QMenu::item:!selected {padding: 2px 15px 2px 10px;}"
                csa = csaa+csab+csac+csad+csae+csaf+csag
                menu.setStyleSheet(csa)
            try:
                ipath = self.fileModel.fileInfo(self.selection[0]).absoluteFilePath()
            except:
                ipath = ""
            if not os.path.exists(ipath):
                if not os.path.islink(ipath):
                    MyDialog("Info", "It doesn't exist.", self.window)
                    return
            #
            if self.selection != None:
                if len(self.selection) == 1:
                    if os.path.isfile(os.path.join(self.lvDir, itemName)):
                        subm_openwithAction= menu.addMenu("Open with...")
                        listPrograms = getAppsByMime(os.path.join(self.lvDir, itemName)).appByMime()
                        #
                        ii = 0
                        defApp = getDefaultApp(os.path.join(self.lvDir, itemName)).defaultApplication()
                        # r_defApp = defApp
                        # if defApp:
                            # for eel in ["%f","%F","%u","%U"]:
                                # r_defApp = r_defApp.strip(eel).rstrip(" ")
                        progActionList = []
                        if listPrograms:
                            # for iprog in listPrograms[::2]:
                            for iprog in listPrograms:
                                # # skip programs working in terminal - bool True or False
                                USE_TERM = False
                                if iprog[2]:
                                    USE_TERM = DesktopEntry(iprog[2]).getTerminal()
                                # if USE_TERM:
                                    # continue
                                # if iprog == r_defApp:
                                if iprog[0] == defApp:
                                    # # progActionList.insert(0, QAction("{} - {} (Default)".format(os.path.basename(iprog), listPrograms[ii+1]), self))
                                    # progActionList.insert(0, QAction("{} (Default)".format(listPrograms[ii+1]), self))
                                    prog_str = "{} (Default)".format(iprog[1])
                                    if USE_TERM:
                                        prog_str = "{} (Default - terminal)".format(iprog[1])
                                    progActionList.insert(0, QAction(prog_str, self))
                                    # progActionList.insert(1, iprog[0])
                                    progActionList.insert(1, iprog)
                                else:
                                    # # progActionList.append(QAction("{} - {}".format(os.path.basename(iprog), listPrograms[ii+1]), self))
                                    # progActionList.append(QAction("{}".format(listPrograms[ii+1]), self))
                                    prog_str = "{}".format(iprog[1])
                                    if USE_TERM:
                                        prog_str = "{} (terminal)".format(iprog[1])
                                    progActionList.append(QAction(prog_str, self))
                                    # progActionList.append(iprog[0])
                                    progActionList.append(iprog)
                                ii += 2
                            ii = 0
                            for paction in progActionList[::2]:
                                paction.triggered.connect(lambda checked, index=ii:self.fprogAction(progActionList[index+1], os.path.join(self.lvDir, itemName)))
                                subm_openwithAction.addAction(paction)
                                ii += 2
                        subm_openwithAction.addSeparator()
                        otherAction = QAction("Other Program")
                        otherAction.triggered.connect(lambda:self.fotherAction(os.path.join(self.lvDir, itemName)))
                        subm_openwithAction.addAction(otherAction)
                        #
                        menu.addSeparator()
                    elif os.path.isdir(os.path.join(self.lvDir, itemName)):
                        newtabAction = QAction("Open in a new tab")
                        newtabAction.triggered.connect(lambda:self.fnewtabAction(os.path.join(self.lvDir, itemName), self.flag))
                        menu.addAction(newtabAction)
                        menu.addSeparator()
            #
            copyAction = QAction("Copy", self)
            copyAction.triggered.connect(lambda:self.fcopycutAction("copy"))
            menu.addAction(copyAction)
            #
            if self.flag == 1 or self.flag == 3:
                copyAction = QAction("Cut", self)
                copyAction.triggered.connect(lambda:self.fcopycutAction("cut"))
                menu.addAction(copyAction)
            # can paste into the hovered directory
            if os.path.isdir(os.path.join(self.lvDir, itemName)):
                if self.flag == 1 or self.flag == 3:
                    pasteNmergeAction = QAction("Paste", self)
                    pasteNmergeAction.triggered.connect(lambda d:PastenMerge(os.path.join(self.lvDir, itemName), -3, "", self.window))
                    menu.addAction(pasteNmergeAction)
                    # check the clipboard for data
                    clipboard = QApplication.clipboard()
                    mimeData = clipboard.mimeData(QClipboard.Mode.Clipboard)
                    if "x-special/gnome-copied-files" not in mimeData.formats():
                        pasteNmergeAction.setEnabled(False)
            #
            if USE_TRASH:
                # only items in the HOME dir or in mass storages
                len_home = len(os.path.expanduser("~"))
                if self.lvDir[0:len_home] == os.path.expanduser("~") or self.flag in [3,4]:
                    if self.flag == 1 or self.flag == 3:
                        if isXDGDATAHOME:
                            trashAction = QAction("Trash", self)
                            trashAction.triggered.connect(self.ftrashAction)
                            menu.addAction(trashAction)
            #
            # delete function
            if USE_DELETE:
                if self.flag == 1 or self.flag == 3:
                    deleteAction = QAction("Delete", self)
                    deleteAction.triggered.connect(self.fdeleteAction)
                    menu.addAction(deleteAction)
            #
            if self.flag == 1 or self.flag == 3:
                if self.selection and len(self.selection) == 1:
                    menu.addSeparator()
                    renameAction = QAction("Rename", self)
                    renameAction.triggered.connect(lambda:self.frenameAction(ipath))
                    menu.addAction(renameAction)
            #
            ###### custom actions
            # ## search for new modules
            # mmod_custom_new = glob.glob("modules_custom/*.py")
            # global list_custom_modules
            # global mmod_custom
            # list_custom_modules_new = []
            # list_custom_modules_temp = list_custom_modules[:]
            # for el in reversed(mmod_custom_new):
                # try:
                    # # new module
                    # if el not in mmod_custom:
                        # # da python 3.4 exec_module invece di import_module
                        # ee = importlib.import_module(os.path.basename(el)[:-3])
                        # list_custom_modules.append(ee)
                # except ImportError as ioe:
                    # pass
            # ## search for removed modules
            # for el in list_custom_modules_temp:
                # el_name = str(el.__name__)
                # el_name_path = os.path.join("modules_custom", el_name)+".py"
                # if str(el_name_path) not in mmod_custom_new:
                    # del sys.modules[el_name]
                    # list_custom_modules.remove(el)
            # # concinstency
            # mmod_custom = mmod_custom_new
            # del list_custom_modules_temp
            #
            ## populate
            if len(list_custom_modules) > 0:
                menu.addSeparator()
                subm_customAction = menu.addMenu("Actions")
                listActions = []
                for el in list_custom_modules:
                    if el.mmodule_type(self) == 1 and self.selection and len(self.selection) == 1:
                        icustomAction = QAction(el.mmodule_name(), self)
                        listActions.append(icustomAction)
                        listActions.append(el)
                        listActions.append(1)
                    elif el.mmodule_type(self) == 2 and self.selection and len(self.selection) > 1:
                        icustomAction = QAction(el.mmodule_name(), self)
                        listActions.append(icustomAction)
                        listActions.append(el)
                        listActions.append(2)
                    elif el.mmodule_type(self) == 3 and self.selection and len(self.selection) > 0:
                        icustomAction = QAction(el.mmodule_name(), self)
                        listActions.append(icustomAction)
                        listActions.append(el)
                        listActions.append(3)
                    elif el.mmodule_type(self) == 5:
                        icustomAction = QAction(el.mmodule_name(), self)
                        listActions.append(icustomAction)
                        listActions.append(el)
                        listActions.append(5)
                #
                ii = 0
                for paction in listActions[::3]:
                    paction.triggered.connect(lambda checked, index=ii:self.ficustomAction(listActions[index+1], listActions[index+2]))
                    subm_customAction.addAction(paction)
                    ii += 3
            # bookmarks
            menu.addSeparator()
            if os.path.isdir(ipath):
                with open("Bookmarks", "r") as fb:
                    fbdata = fb.readlines()
                if ipath+"\n" in fbdata:
                    baction = QAction("Remove Bookmark", self)
                    baction.triggered.connect(lambda:self.window.unsetBtnBookmarks(ipath))
                    menu.addAction(baction)
                else:
                    baction = QAction("Add Bookmark", self)
                    baction.triggered.connect(lambda:self.window.setBtnBookmarks(ipath))
                    menu.addAction(baction)
            #
            menu.addSeparator()
            if self.selection and len(self.selection) == 1:
                propertyAction = QAction("Property", self)
                propertyAction.triggered.connect(lambda:self.fpropertyAction(ipath))
                menu.addAction(propertyAction)
            #
            elif self.selection and len(self.selection) > 1:
                propertyAction = QAction("Property", self)
                propertyAction.triggered.connect(self.fpropertyActionMulti)
                menu.addAction(propertyAction)
            #
            menu.exec(self.listview.mapToGlobal(position))
        ## background
        else:
            if not os.path.exists(self.lvDir):
                MyDialog("Info", "It doesn't exist.", self.window)
                return
            self.listview.clearSelection()
            menu = QMenu("Menu", self.listview)
            if MENU_H_COLOR:
                csaa = "QMenu { "
                csab = "background: {}".format(QPalette.ColorRole.Window)
                csac = "; margin: 1px; padding: 5px 5px 5px 5px;}"
                csad = " QMenu::item:selected { "
                csae = "background-color: {};".format(MENU_H_COLOR)
                csaf = " padding: 10px;}"
                csag = " QMenu::item:!selected {padding: 2px 15px 2px 10px;}"
                csa = csaa+csab+csac+csad+csae+csaf+csag
                menu.setStyleSheet(csa)
            #
            if self.flag == 1 or self.flag == 3:
                newFolderAction = QAction("New Folder", self)
                newFolderAction.triggered.connect(self.fnewFolderAction)
                menu.addAction(newFolderAction)
                newFileAction = QAction("New File", self)
                newFileAction.triggered.connect(self.fnewFileAction)
                menu.addAction(newFileAction)
                #
                templateDir = None
                optTemplateDir = os.path.join(os.path.expanduser("~"), TEMPLATE_DIR)
                if os.path.exists(optTemplateDir):
                    templateDir = optTemplateDir
                    #
                    menu.addSeparator()
                    subm_templatesAction= menu.addMenu(TEMPLATE_DIR)
                    listTemplate = os.listdir(templateDir)
                    #
                    progActionListT = []
                    for ifile in listTemplate:
                        progActionListT.append(QAction(ifile))
                        progActionListT.append(ifile)
                    ii = 0
                    for paction in progActionListT[::2]:
                        paction.triggered.connect(lambda checked, index=ii:self.ftemplateAction(progActionListT[index+1]))
                        subm_templatesAction.addAction(paction)
                        ii += 2
            #
            if self.flag == 1 or self.flag == 3:
                pasteNmergeAction = QAction("Paste", self)
                pasteNmergeAction.triggered.connect(lambda d:PastenMerge(self.lvDir, -3, "", self.window))
                menu.addAction(pasteNmergeAction)
                # check the clipboard for data
                clipboard = QApplication.clipboard()
                mimeData = clipboard.mimeData(QClipboard.Mode.Clipboard)
                if "x-special/gnome-copied-files" not in mimeData.formats():
                    pasteNmergeAction.setEnabled(False)
            #
            menu.addSeparator()
            subm_customAction = menu.addMenu("Actions")
            #
            if len(list_custom_modules) > 0:
                listActions = []
                for el in list_custom_modules:
                    if el.mmodule_type(self) == 4 or el.mmodule_type(self) == 5:
                        bcustomAction = QAction(el.mmodule_name(), self)
                        listActions.append(bcustomAction)
                        listActions.append(el)
                #
                ii = 0
                for paction in listActions[::2]:
                    paction.triggered.connect(lambda checked, index=ii:self.fbcustomAction(listActions[index+1]))
                    subm_customAction.addAction(paction)
                    ii += 2
            # bookmarks
            menu.addSeparator()
            if os.path.isdir(self.lvDir):
                with open("Bookmarks", "r") as fb:
                    fbdata = fb.readlines()
                if self.lvDir+"\n" in fbdata:
                    baction = QAction("Remove Bookmark", self)
                    baction.triggered.connect(lambda:self.window.unsetBtnBookmarks(self.lvDir))
                    menu.addAction(baction)
                else:
                    baction = QAction("Add Bookmark", self)
                    baction.triggered.connect(lambda:self.window.setBtnBookmarks(self.lvDir))
                    menu.addAction(baction)
            #
            menu.exec(self.listview.mapToGlobal(position))
    
    # show a menu with all the installed applications
    def fotherAction(self, itemPath):
        if OPEN_WITH:
            self.cw = OW.listMenu(itemPath)
            self.cw.show()
        else:
            ret = otherApp(itemPath, self.window).getValues()
            if ret == -1:
                return
            if shutil.which(ret):
                try:
                    subprocess.Popen([ret, itemPath])
                except Exception as E:
                    MyDialog("Error", str(E), self.window)
            else:
                MyDialog("Info", "The program\n"+ret+"\ncannot be found", self.window)
    
    # copy the template choosen - the rename dialog appears
    def ftemplateAction(self, templateName):
        templateDir = None
        optTemplateDir = os.path.join(os.path.expanduser("~"), TEMPLATE_DIR)
        if os.path.exists(optTemplateDir):
           templateDir = optTemplateDir
        else:
            return
        #
        if os.access(self.lvDir, os.W_OK): 
            ret = self.wrename3(templateName, self.lvDir)
            if ret != -1 or not ret:
                destPath = os.path.join(self.lvDir, ret)
                if not os.path.exists(destPath):
                    try:
                        shutil.copy(os.path.join(templateDir, templateName), destPath)
                    except Exception as E:
                        MyDialog("Error", str(E), self.window)
    
    # launch the application choosen
    def fprogAction(self, iprog, path):
        defApp = iprog[0]
        USE_TERM = DesktopEntry(iprog[2]).getTerminal()
        # execute the command
        r_defApp = defApp.split(" ")
        # self._flaunch_prog(r_defApp, path, USE_TERM)
        _flaunch_prog(r_defApp, path, USE_TERM)
    
    # a new tab opens
    def fnewtabAction(self, ldir, flag):
        #
        if os.access(ldir, os.R_OK):
            self.window.openDir(ldir, flag)
        else:
            MyDialog("Info", "Cannot open the folder: "+os.path.basename(ldir), self.window)

    # send to trash the selected items
    def ftrashAction(self):
        if self.selection:
            list_items = []
            for item in self.selection:
                list_items.append(self.fileModel.fileInfo(item).absoluteFilePath())
            #
            # if more than 30 items no list
            if len(self.selection) < ITEMSDELETED:
                dialogList = ""
                for item in list_items:
                    dialogList += os.path.basename(item)+"\n"
                ret = retDialogBox("Question", "Do you really want to move these items to the trashcan?", "", dialogList, self.window)
            else:
                ret = retDialogBox("Question", "Do you really want to move these items to the trashcan?", "", "Too many items.\n", self.window)
            #
            if ret.getValue():
                TrashModule(list_items, self.window)
                self.listview.viewport().update()
        
    # bypass the trashcan
    def fdeleteAction(self):
        if self.selection:
            list_items = []
            for item in self.selection:
                list_items.append(self.fileModel.fileInfo(item).absoluteFilePath())
            
            # if more than 30 items no list
            if len(self.selection) < ITEMSDELETED:
                dialogList = ""
                for item in list_items:
                    dialogList += os.path.basename(item)+"\n"
                ret = retDialogBox("Question", "Do you really want to delete these items?", "", dialogList, self.window)
            else:
                ret = retDialogBox("Question", "Do you really want to delete these items?", "", "Too many items.\n", self.window)
            #
            if ret.getValue():
                self.fdeleteItems(list_items)
                self.listview.viewport().update()
    
    # related to self.fdeleteAction
    def fdeleteItems(self, listItems):
        #
        # something happened with some items
        items_skipped = ""
        #
        for item in listItems:
            # time.sleep(0.001)
            if os.path.islink(item):
                try:
                    os.remove(item)
                except Exception as E:
                    items_skipped += os.path.basename(item)+"\n"+str(E)+"\n\n"
            elif os.path.isfile(item):
                try:
                    os.remove(item)
                except Exception as E:
                    items_skipped += os.path.basename(item)+"\n"+str(E)+"\n\n"
            elif os.path.isdir(item):
                try:
                    shutil.rmtree(item)
                except Exception as E:
                    items_skipped += os.path.basename(item)+"\n"+str(E)+"\n\n"
            # not regular files or folders 
            else:
                items_skipped += os.path.basename(item)+"\n"+"Only files and folders can be deleted."+"\n\n"
        #
        if items_skipped != "":
            MyMessageBox("Info", "Items not deleted:", "", items_skipped, self.window)
    
    # create a new folder
    def fnewFolderAction(self):
        if os.access(self.lvDir, os.W_OK): 
            ret = self.wrename3("New Folder", self.lvDir)
            if ret != -1 or not ret:
                destPath = os.path.join(self.lvDir, ret)
                if not os.path.exists(destPath):
                    try:
                        os.mkdir(destPath)
                    except Exception as E:
                        MyDialog("Error", str(E), self.window)
    
    # 
    def fnewFileAction(self):
        if os.access(self.lvDir, os.W_OK): 
            ret = self.wrename3("Text file.txt", self.lvDir)
            if ret != -1 or not ret:
                destPath = os.path.join(self.lvDir, ret)
                if not os.path.exists(destPath):
                    try:
                        iitem = open(destPath,'w')
                        iitem.close()
                    except Exception as E:
                        MyDialog("Error", str(E), self.window)
        
    # new file or folder
    def wrename3(self, ditem, dest_path):
        ret = MyDialogRename3(ditem, self.lvDir, self.window).getValues()
        if ret == -1:
                return ret
        elif not ret:
            return -1
        else:
            return ret
    
    # from contextual menu
    def frenameAction(self, ipath):
        ibasename = os.path.basename(ipath)
        idirname = os.path.dirname(ipath)
        inew_name = self.wrename2(ibasename, idirname)

        if inew_name != -1:
            try:
                shutil.move(ipath, inew_name)
            except Exception as E:
                MyDialog("Error", str(E), self.window)
    
    
    def fpropertyAction(self, ipath):
        propertyDialog(ipath, self.window)
    
    
    def fpropertyActionMulti(self):
        # size of all the selected items
        iSize = 0
        # # number of the selected items
        # iNum = len(self.selection)
        #
        item_list = []
        for iitem in self.selection:
            try:
                item = self.fileModel.fileInfo(iitem).absoluteFilePath()
                #
                if os.path.islink(item):
                    iSize += 512
                    continue
                elif os.path.isfile(item):
                    iSize += QFileInfo(item).size()
                    item_list.append(item)
                elif os.path.isdir(item):
                    iSize += folder_size(item)
                    item_list.append(item)
                # else:
                    # QFileInfo(item).size()
            except:
                iSize += 0
        #
        # propertyDialogMulti(convert_size(iSize), iNum, self.window)
        propertyDialogMulti(item_list, convert_size(iSize), self.window)
    
    # 
    def ficustomAction(self, el, menuType):
        if menuType == 1:
            items_list = []
            items_list.append(self.fileModel.fileInfo(self.selection[0]).absoluteFilePath())
            el.ModuleCustom(self)
        elif menuType == 2:
            items_list = []
            for iitem in self.selection:
                items_list.append(self.fileModel.fileInfo(iitem).absoluteFilePath())
            el.ModuleCustom(self)
        elif menuType == 3:
            items_list = []
            for iitem in self.selection:
                items_list.append(self.fileModel.fileInfo(iitem).absoluteFilePath())
            el.ModuleCustom(self)
        elif menuType == 5:
            items_list = []
            for iitem in self.selection:
                items_list.append(self.fileModel.fileInfo(iitem).absoluteFilePath())
            el.ModuleCustom(self)
    
    
    def fbcustomAction(self, el):
        el.ModuleCustom(self)
    
    # from contextual menu
    def wrename2(self, ditem, dest_path):
        ret = ditem
        ret = MyDialogRename2(ditem, dest_path, self.window).getValues()
        if ret == -1:
                return ret
        elif not ret:
            return -1
        else:
            return os.path.join(dest_path, ret)
    
    #
    def fcopycutAction(self, action):
        if action == "copy":
            item_list = "copy\n"
        elif action == "cut":
            item_list = "cut\n"
        #
        for iindex in self.selection:
            iname = iindex.data(QFileSystemModel.Roles.FileNameRole)
            iname_fp = os.path.join(self.lvDir, iname)
            ## readable or broken link
            if os.access(iname_fp,os.R_OK) or os.path.islink(iname_fp):
                iname_quoted = quote(iname, safe='/:?=&')
                if iindex != self.selection[-1]:
                    iname_final = "file://{}\n".format(os.path.join(self.lvDir, iname_quoted))
                    item_list += iname_final
                else:
                    iname_final = "file://{}".format(os.path.join(self.lvDir, iname_quoted))
                    item_list += iname_final
        #
        if item_list == "copy\n":
            clipboard = QApplication.clipboard()
            clipboard.clear()
            return
        #
        clipboard = QApplication.clipboard()
        data = QByteArray()
        data.append(bytes(item_list, encoding="utf-8"))
        qmimdat = QMimeData()
        qmimdat.setData("x-special/gnome-copied-files", data)
        clipboard.setMimeData(qmimdat, QClipboard.Mode.Clipboard)
    
    # go to the upper directory
    def upButton(self):
        if self.lvDir != "/":
            path = os.path.dirname(self.lvDir)
            # the path can be unreadable for any reasons
            if not os.access(path, os.R_OK):
                MyDialog("Error", "The folder\n"+path+"\nis not readable anymore.", self.window)
                return
            # check for an existent directory
            while not os.path.exists(path):
                path = os.path.dirname(path)
            #
            self.listview.clearSelection()
            # # highlight the upper folder
            # upperdir = self.lvDir
            # self.lvDir = path
            # self.window.mtab.setTabText(self.window.mtab.currentIndex(), os.path.basename(self.lvDir) or "ROOT")
            # self.window.mtab.setTabToolTip(self.window.mtab.currentIndex(), self.lvDir)
            self.listview.setRootIndex(self.fileModel.setRootPath(path))
            # #
            # self.tabLabels()
            #
            # ## highlight the file passed as argument
            # if os.path.exists(upperdir):
                # index = self.fileModel.index(upperdir)
                # # skip hidden folders
                # if not index.data(QFileSystemModel.Roles.FileNameRole)[0] == ".":
                    # self.listview.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select)
                    # self.listview.scrollTo(index, QAbstractItemView.ScrollHint.EnsureVisible)
            # #
            # self.hicombo.insertItem(0, self.lvDir)
            # self.hicombo.setCurrentIndex(0)
            # #
            # self.on_box_pb(self.lvDir)
            #
            self._pp = 1
            
    
    # invert the selection
    def finvbtn(self):
        rootIndex = self.listview.rootIndex()
        numOfItems = self.fileModel.rowCount(rootIndex)
        first = self.fileModel.index(0,0,rootIndex)
        last = self.fileModel.index(numOfItems-1,0,rootIndex)
        selection = QItemSelection(first, last)
        self.listview.selectionModel().select(selection, QItemSelectionModel.SelectionFlag.Toggle)
    
    # toggle show hidden items
    def fhidbtn(self):
        # if self.fmf == 0:
        if self.sender().isChecked():
            self.fileModel.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot | QDir.Filter.System | QDir.Filter.Hidden)
            # self.fmf = 1
            self.listview.scrollToTop()
            self.sender().setToolTip("Hide the hidden Items")
        else:
            self.listview.clearSelection()
            #
            self.fileModel.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot | QDir.Filter.System)
            # self.fmf = 0
            self.listview.scrollToTop()
            self.sender().setToolTip("Show the hidden Items")
            

###########################

class clabel(QLabel):
    
    def __init__(self, parent=None):
        super(clabel, self).__init__(parent)
    
    def setText(self, text, wWidth):
        # boxWidth = wWidth-400*QApplication.instance().devicePixelRatio()
        boxWidth = (wWidth-400)
        font = self.font()
        metric = QFontMetrics(font)
        string = text
        ctemp = ""
        ctempT = ""
        for cchar in string:
            ctemp += str(cchar)
            # width = metric.width(ctemp)
            # to verify
            width = metric.size(0, ctemp).width()
            if width < boxWidth:
                ctempT += str(cchar)
                continue
            else:
                ctempT += "\n"
                ctempT += str(cchar)
                ctemp = str(cchar)
        ntext = ctempT
        super(clabel, self).setText(ntext)


# OPTIONALLY DISABLED
# class thumbThread(threading.Thread):
    
    # def __init__(self, fpath, listview):
        # threading.Thread.__init__(self)
        # self.event = threading.Event()
        # self.fpath = fpath
        # self.listview = listview
    
    # def run(self):
        # list_dir = os.listdir(self.fpath)
        # while not self.event.is_set():
            # for iitem in list_dir:
                # item_fpath = os.path.join(self.fpath, iitem)
                # if os.path.exists(item_fpath):
                    # if stat.S_ISREG(os.stat(item_fpath).st_mode):
                        # hmd5 = "Null"
                        # imime = QMimeDatabase().mimeTypeForFile(iitem, QMimeDatabase.MatchMode.MatchDefault)
                        # hmd5 = create_thumbnail(item_fpath, imime.name())
                        # self.event.wait(0.05)
            # self.event.set()
        # #self.listview.viewport().update()


# find the applications installed for a given mimetype
class getAppsByMime():
    def __init__(self, path):
        self.path = path
        # three list from mimeapps.list: association added and removed and default applications
        self.lA = []
        self.lR = []
        self.lD = []
        # path of the mimeapps.list
        self.MIMEAPPSLIST = MIMEAPPSLIST
        #
        self.apps_dir_home = os.path.expanduser('~')+"/.local/share"
        self.apps_dir_home_list = os.listdir(os.path.join(self.apps_dir_home, "applications"))

    
    def appByMime(self):
        listPrograms = []
        imimetype = QMimeDatabase().mimeTypeForFile(self.path, QMimeDatabase.MatchMode.MatchDefault).name()
        if imimetype in ["application/x-zerosize", "application/x-trash", "application/x-desktop"]:
            mimetype = "text/plain"
        else:
            mimetype = imimetype
        # the action for the mimetype also depends on the file mimeapps.list in the home folder 
        #lAdded,lRemoved,lDefault = self.addMime(mimetype)
        lAdded,lRemoved = self.addMime(mimetype)
        #
        for ddir in xdgDataDirs:
            applicationsPath = os.path.join(ddir, "applications")
            if os.path.exists(applicationsPath):
                desktopFiles = os.listdir(applicationsPath)
                for idesktop in desktopFiles:
                    temp_list = []
                    # those in the home have priority
                    if ddir != self.apps_dir_home:
                        if idesktop in self.apps_dir_home_list:
                            continue
                    if idesktop.endswith(".desktop"):
                        # skip the removed associations
                        if idesktop in lRemoved:
                            continue
                        # 
                        desktopPath = os.path.join(applicationsPath, idesktop)
                        # consinstency - do not crash if the desktop file is malformed
                        try:
                            if mimetype in DesktopEntry(desktopPath).getMimeTypes():
                                mimeProg2 = DesktopEntry(desktopPath).getExec()
                                # replace $HOME with home path
                                if mimeProg2[0:5].upper() == "$HOME":
                                    mimeProg2 = os.path.expanduser("~")+"/"+mimeProg2[5:]
                                # replace ~ with home path
                                elif mimeProg2[0:1] == "~":
                                    mimeProg2 = os.path.expanduser("~")+"/"+mimeProg2[1:]
                                #
                                if mimeProg2:
                                    mimeProg = mimeProg2.split()[0]
                                else:
                                    # return
                                    continue
                                retw = shutil.which(mimeProg)
                                #
                                if retw is not None:
                                    if os.path.exists(retw):
                                        # listPrograms.append(retw)
                                        
                                        ######
                                        # execArgs = [" %f", " %F", " %u", " %U", " %d", " %D", " %n", " %N", " %k", " %v"]
                                        # for aargs in execArgs:
                                            # if aargs in mimeProg2:
                                                # mimeProg2 = mimeProg2.strip(aargs)
                                        # listPrograms.append(mimeProg2)
                                        temp_list.append(mimeProg2)
                                        ######
                                        
                                        try:
                                            progName = DesktopEntry(desktopPath).getName()
                                            if progName != "":
                                                # listPrograms.append(progName)
                                                temp_list.append(progName)
                                            else:
                                                # listPrograms.append("None")
                                                temp_list.append("None")
                                        except:
                                            # listPrograms.append("None")
                                            temp_list.append("None")
                                    #
                                    temp_list.append(desktopPath)
                                    listPrograms.append(temp_list)
                        
                        except Exception as E:
                            MyDialog("Error", str(E), self.window)
        # 
        # from the lAdded list
        for idesktop in lAdded:
            temp_list = []
            # skip the removed associations
            if idesktop in lRemoved:
                continue
            desktopPath = ""
            #
            # check if the idesktop is in xdgDataDirs - use it if any
            #
            for ddir in xdgDataDirs:
                applicationsPath = os.path.join(ddir, "applications")
                if os.path.exists(applicationsPath):
                    # those in the home have priority
                    if ddir != self.apps_dir_home:
                        if idesktop in self.apps_dir_home_list:
                            continue
                    if idesktop in os.listdir(applicationsPath):
                        desktopPath = os.path.join(applicationsPath, idesktop)
            #
            mimeProg2 = DesktopEntry(desktopPath).getExec()
            #
            if mimeProg2:
                mimeProg = mimeProg2.split()[0]
            else:
                continue
            retw = shutil.which(mimeProg)
            if retw is not None:
                if os.path.exists(retw):
                    # skip the existent applications
                    if retw in listPrograms:
                        continue
                    #
                    temp_list.append(mimeProg2)
                    try:
                        progName = DesktopEntry(desktopPath).getName()
                        if progName != "":
                            temp_list.append(progName)
                        else:
                            temp_list.append("None")
                    except:
                         temp_list.append("None")
                    #
                    temp_list.append(desktopPath)
                    listPrograms.append(temp_list)
        #
        return listPrograms


    # function that return mimetypes added and removed (and default applications) in the mimeappss.list
    def addMime(self, mimetype):
        # call the function
        self.fillL123()
        #
        lAdded = []
        lRemoved = []
        lDefault = []
        #
        for el in self.lA:
            # if mimetype in el:
            if "=" in el:
                if el.split("=")[0] == mimetype:
                    # item is type list
                    item = el.replace(mimetype+"=","").strip("\n").split(";")
                    lAdded = self.delNull(item)
                    break
        #
        for el in self.lR:
            # if mimetype in el:
            if "=" in el:
                if el.split("=")[0] == mimetype:
                    item = el.replace(mimetype+"=","").strip("\n").split(";")
                    lRemoved = self.delNull(item)
                    break
        #
        for el in self.lD:
            # if mimetype in el:
            if "=" in el:
                if el.split("=")[0] == mimetype:
                    item = el.replace(mimetype+"=","").strip("\n").split(";")
                    lDefault = self.delNull(item)
                    break
        #
        #return lAdded,lRemoved,lDefault
        return lAdded,lRemoved

    # function that return mimetypes added, removed in the mimeappss.list
    def fillL123(self):
        # mimeapps.list can have up to three not mandatory sectors
        # lists of mimetypes added or removed - reset
        lAdded = []
        lRemoved = []
        lDefault = []
        lista = []
        #
        # reset
        lA1 = []
        lR1 = []
        lD1 = []
        #
        if not os.path.exists(self.MIMEAPPSLIST):
            return
        #
        # all the file in lista: one row one item added to lista
        with open(self.MIMEAPPSLIST, "r") as f:
            lista = f.readlines()
        #
        # marker
        x = ""
        for el in lista:
            if el == "[Added Associations]\n":
                x = "A"
            elif el == "[Removed Associations]\n":
                x = "R"
            elif el == "[Default Applications]\n":
                x = "D"
            #
            if el:
                if x == "A":
                    lA1.append(el)
                elif x == "R":
                    lR1.append(el)
                elif x == "D":
                    lD1.append(el) 
        #
        # attributions
        self.lA = lA1
        self.lR = lR1
        self.lD = lD1


    # remove the null elements in the list
    def delNull(self,e):
        return [i for i in e if i != ""]


# find the default application for a given mimetype if any
# using xdg-mime
class getDefaultApp():
    
    def __init__(self, path):
        self.path = path
        
    def defaultApplication(self):
        ret = shutil.which("xdg-mime")
        if ret:
            imime = QMimeDatabase().mimeTypeForFile(self.path, QMimeDatabase.MatchMode.MatchDefault).name()
            #
            if imime in ["application/x-zerosize", "application/x-trash", "application/x-desktop"]:
                mimetype = "text/plain"
            else:
                mimetype = imime
            #
            associatedDesktopProgram = None
            #
            if USER_MIMEAPPSLIST:
                try:
                    associatedDesktopProgram = subprocess.check_output([ret, "query", "default", mimetype], universal_newlines=False).decode()
                except:
                    return "None"
            else:
                associatedDesktopProgram = self.defaultApplication2(mimetype)
            #
            if associatedDesktopProgram:
                for ddir in xdgDataDirs:
                    if ddir[-1] == "/":
                        ddir = ddir[:-1]
                    desktopPath = os.path.join(ddir+"/applications", associatedDesktopProgram.strip())
                    #
                    if os.path.exists(desktopPath):
                        applicationName = DesktopEntry(desktopPath).getTryExec()
                        applicationName2 = DesktopEntry(desktopPath).getExec()
                        #
                        if not applicationName:
                            if applicationName2:
                                # need revision
                                applicationName = applicationName2.split()[0]
                            else:
                                return "None"
                        applicationPath = shutil.which(applicationName)
                        if applicationPath:
                            if os.path.exists(applicationPath):
                                # return applicationPath
                                return applicationName2
                            else:
                                MyDialog("Info", "{} cannot be found".format(applicationPath), None)
                        else:
                            return "None"
                #
                # no apps found
                return "None"
            else:
                return "None"
        #
        else:
            MyDialog("Error", "xdg-mime cannot be found", None)
        
    # function that found the default program for the given mimetype
    def defaultApplication2(self, mimetype):
        # lists of mimetypes added or removed
        lista = []
        # all the file in lista: one row one item added to lista
        with open(MIMEAPPSLIST, "r") as f:
            lista = f.readlines()
        # marker
        x = ""
        for el in lista:
            if el == "[Added Associations]\n":
                x = "A"
            elif el == "[Removed Associations]\n":
                x = "R"
            elif el == "[Default Applications]\n":
                x = "D"
            #
            if x == "D":
                if el:
                    if el == "\n":
                        continue
                    if el[0:len(mimetype)+1] == mimetype+"=":
                        desktop_file = el.split("=")[1].strip("\n").strip(";")
                        return desktop_file
        # nothing found
        return "None"


# Paste and Merge function - utility
class PastenMerge():
    
    def __init__(self, lvDir, action, dlist, window):
        self.lvDir = lvDir
        # -3 if not DnD - or 1 or 2
        self.action = action
        self.dlist = dlist
        self.window = window
        self.fpasteNmergeAction()
    
    # make the list of all the item to be copied - find the action
    def fmakelist(self):
        filePaths = []
        #
        clipboard = QApplication.clipboard()
        mimeData = clipboard.mimeData(QClipboard.Mode.Clipboard)
        #
        got_quoted_data = []
        for f in mimeData.formats():
            #
            if f == "x-special/gnome-copied-files":
                data = mimeData.data(f)
                got_quoted_data = data.data().decode().split("\n")
                got_action = got_quoted_data[0]
                if got_action == "copy":
                    self.action = 1
                elif got_action == "cut":
                    self.action = 2
                filePaths = [unquote(x)[7:] for x in got_quoted_data[1:]]
        #
        return filePaths
    
    # paste and merge function
    def fpasteNmergeAction(self):
        # copy/paste
        if self.action == -3:
            # make the list of the items
            filePaths = self.fmakelist()
            if filePaths:
                # execute the copying copy/cut operations
                # self.action: 1 copy - 2 cut - 4 make link
                copyItems2(self.action, filePaths, -4, self.lvDir, self.window)
        # DnD - 1 copy - 2 cut - 4 link (not supported)
        elif self.action == Qt.DropAction.CopyAction or self.action == Qt.DropAction.MoveAction:
            if self.dlist:
                # execute the copying copy/cut operations
                # self.action: 1 copy - 2 cut - 4 make link
                if self.action == Qt.DropAction.CopyAction:
                    _action = 1
                elif self.action == Qt.DropAction.MoveAction:
                    _action = 2
                copyItems2(_action, self.dlist, -4, self.lvDir, self.window)


###################### THE HOME TRASHCAN #######################

class openTrash(QBoxLayout):
    def __init__(self, window, tdir, parent=None):
        super(openTrash, self).__init__(QBoxLayout.Direction.TopToBottom, parent)
        self.window = window
        self.tdir = tdir
        self.setContentsMargins(QMargins(0,0,0,0))
        global TrashIsOpen
        if TrashIsOpen:
            return
        TrashIsOpen = 1
        #
        # self.window.fileSystemWatcher.directoryChanged.connect(self.trash_directory_changed)
        # the list of trashed items - fake names
        self.list_trashed_items = []
        #
        page = QWidget()
        #
        self.ilist = QListView()
        self.ilist.setSpacing(10)
        # the background color
        if USE_BACKGROUND_COLOUR == 1:
            palette = self.ilist.palette()
            palette.setColor(QPalette.ColorRole.Base, QColor(ORED,OGREEN,OBLUE))
            self.ilist.setPalette(palette)
        #
        self.ilist.clicked.connect(self.flist)
        self.ilist.doubleClicked.connect(self.flist2)
        self.addWidget(self.ilist, 0)
        #
        self.ilist.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ilist.setWrapping(True)
        self.ilist.setWordWrap(True)
        #
        self.model = QStandardItemModel(self.ilist)
        self.ilist.setModel(self.model)
        #
        self.ilist.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ilist.customContextMenuRequested.connect(self.onRightClick)
        #
        obox = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        obox.setContentsMargins(QMargins(5,5,5,5))
        self.insertLayout(1, obox)
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        #
        self.label1 = QLabel("<i>Name</i>")
        self.label2 = QLabel("<i>Origin</i>")
        self.label3 = QLabel("<i>Deletion date</i>")
        self.label4 = QLabel("<i>Type</i>")
        self.label5 = QLabel("<i>Size</i>")
        self.label6 = clabel()
        self.label7 = clabel()
        self.label8 = QLabel("")
        # self.label9 = QLabel("")
        self.label9 = clabel()
        self.label10 = QLabel("")
        layout.addRow(self.label1, self.label6)
        layout.addRow(self.label2, self.label7)
        layout.addRow(self.label3, self.label8)
        layout.addRow(self.label4, self.label9)
        layout.addRow(self.label5, self.label10)
        #
        obox.insertLayout(0, layout, 1)
        box2 = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        box2.setContentsMargins(QMargins(0,0,0,0))
        obox.insertLayout(1, box2, 0)
        #
        button1 = QPushButton("R")
        button1.setToolTip("Restore the selected items")
        button1.clicked.connect(self.ftbutton1)
        box2.addWidget(button1)
        # 
        button2 = QPushButton("D")
        button2.setToolTip("Delete the selected items")
        button2.clicked.connect(self.ftbutton2)
        box2.addWidget(button2)
        #
        button3 = QPushButton("E")
        button3.setToolTip("Empty the Recycle Bin")
        button3.clicked.connect(self.ftbutton3)
        box2.addWidget(button3)
        #
        if self.tdir == "HOME":
            ttag = "Home"
        else:
            ttag = os.path.basename(str(self.tdir))
        self.window.mtab.addTab(page, "Recycle Bin - {}".format(ttag))
        page.setLayout(self)
        self.window.mtab.setCurrentIndex(self.window.mtab.count()-1)
        # populate the QListView model
        self.popTrash()
    
    # populate the QListView model
    def popTrash(self):
        llista = trash_module.ReadTrash(self.tdir).return_the_list()
        if llista == -2:
            MyDialog("Info", "The trash directory and its subfolders have some problem.", self.window)
            return
        if llista == -1:
            MyDialog("Info", "Got some problem during the reading of the trashed items.\nSolve the issue manually.", self.window)
            return
        if llista != -1:
            for item in llista:
                if self.tdir == "HOME":
                    prefix_real_name = os.path.expanduser('~')
                else:
                    prefix_real_name = self.tdir
                real_name = os.path.join(prefix_real_name, item.realname)
                fake_name = item.fakename
                deletion_date = item.deletiondate
                item = QStandardItem(3,1)
                item.setData(os.path.basename(real_name), Qt.ItemDataRole.DisplayRole)
                item.setData(real_name, Qt.ItemDataRole.UserRole)
                item.setData(fake_name, Qt.ItemDataRole.UserRole+1)
                item.setData(deletion_date, Qt.ItemDataRole.UserRole+2)
                Tpath = trash_module.mountPoint(self.tdir).find_trash_path()
                item_path = os.path.join(Tpath, "files", fake_name)
                item.setIcon(self.iconItem(item_path))
                item.setCheckable(True)
                self.model.appendRow(item)
                self.list_trashed_items.append(fake_name+".trashinfo")
    
    # the trashcan content changed
    def trash_directory_changed(self, ddir):
        Tinfo = os.path.join(os.path.dirname(ddir), "info")
        updated_list = os.listdir(Tinfo)
        if len(updated_list) > len(self.list_trashed_items):
            item_added = [x for x in updated_list if x not in self.list_trashed_items]
            #
            for iitem in item_added:
                if not os.path.exists(os.path.join(Tinfo, iitem)):
                    continue
                try:
                    with open(os.path.join(Tinfo, iitem), 'r') as read_data:
                        read_data.readline()
                        fake_name = os.path.splitext(os.path.basename(iitem))[0]
                        real_name = unquote(read_data.readline())[5:].rstrip()
                        deletion_date = read_data.readline()[13:].rstrip()
                        item = QStandardItem(3,1)
                        item.setData(os.path.basename(real_name), Qt.ItemDataRole.DisplayRole)
                        item.setData(real_name, Qt.ItemDataRole.UserRole)
                        item.setData(fake_name, Qt.ItemDataRole.UserRole+1)
                        item.setData(deletion_date, Qt.ItemDataRole.UserRole+2)
                        item_path = os.path.join(ddir, fake_name)
                        item.setIcon(self.iconItem(item_path))
                        item.setCheckable(True)
                        self.model.appendRow(item)
                        self.list_trashed_items.append(fake_name+".trashinfo")
                except Exception as E:
                    MyDialog("Error", str(E), self.window)
        #
        elif len(updated_list) < len(self.list_trashed_items):
            item_deleted = [x for x in self.list_trashed_items if x not in updated_list]
            for eitem in item_deleted:
                i = 0
                while self.model.item(i):
                    iitem = self.model.item(i)
                    if os.path.splitext(eitem)[0] == iitem.data(Qt.ItemDataRole.UserRole+1):
                        index = iitem.index()
                        self.model.removeRow(index.row())
                        self.list_trashed_items.remove(eitem)
                        break
                    i += 1
        #
        else:
            # improvements: a file exists in the dir files but not its info file
            pass
    
    
    def iconItem(self, item):
        path = item
        imime = QMimeDatabase().mimeTypeForFile(path, QMimeDatabase.MatchMode.MatchDefault)
        if imime:
            try:
                file_icon = QIcon.fromTheme(imime.iconName())
                if file_icon.isNull():
                    file_icon = QIcon.fromTheme(imime.genericIconName(), QIcon("icons/empty.svg"))
                return file_icon
            except:
                return QIcon("icons/empty.svg")
        else:
            return QIcon("icons/empty.svg")
    
    # restore the selected items
    def ftbutton1(self):
        checkedItems = []
        i = 0
        while self.model.item(i):
            if self.model.item(i).checkState() == Qt.CheckState.Checked:
                checkedItems.append(self.model.item(i))
            i += 1
        #
        for iitem in checkedItems:
            restore_items = []
            index = iitem.index()
            RestoreTrashedItems.fakename = index.data(Qt.ItemDataRole.UserRole+1)
            RestoreTrashedItems.realname = index.data(Qt.ItemDataRole.UserRole)
            #
            restore_items.append(RestoreTrashedItems)
            #
            ret = trash_module.RestoreTrash(self.tdir, restore_items).itemsRestore()
            if ret == -2:
                MyDialog("Error", "The items cannot be restored.\nDo it manually.", self.window)
                return
            if ret != [1,-1]:
                MyDialog("Info", ret, self.window)
            else:
                self.model.removeRow(index.row())
                self.label6.setText("", self.window.size().width())
                self.label7.setText("", self.window.size().width())
                self.label8.setText("")
                # self.label9.setText("")
                self.label9.setText("", self.window.size().width())
                self.label10.setText("")
                #
                self.list_trashed_items.remove(RestoreTrashedItems.fakename+".trashinfo")
    
    # delete the selected item
    def ftbutton2(self):
        checkedItems = []
        i = 0
        while self.model.item(i):
            if self.model.item(i).checkState() == Qt.CheckState.Checked:
                checkedItems.append(self.model.item(i))
            i += 1
        #
        for iitem in checkedItems:
            restore_items = []
            index = iitem.index()
            RestoreTrashedItems.fakename = index.data(Qt.ItemDataRole.UserRole+1)
            RestoreTrashedItems.realname = index.data(Qt.ItemDataRole.UserRole)
            #
            restore_items.append(RestoreTrashedItems)
            #
            ret = trash_module.deleteTrash(self.tdir, restore_items).itemsDelete()
            if ret == -2:
                MyDialog("Info", "The items cannot be deleted.\nDo it manually.", self.window)
                return
            #
            if ret != [1,-1]:
                MyDialog("Info", ret, self.window)
            else:
                self.model.removeRow(index.row())
                self.label6.setText("", self.window.size().width())
                self.label7.setText("", self.window.size().width())
                self.label8.setText("")
                # self.label9.setText("")
                self.label9.setText("", self.window.size().width())
                self.label10.setText("")
    
    # empty the recycle bin
    def ftbutton3(self):
        ret = trash_module.emptyTrash(self.tdir).tempty()
        if ret == -2:
            MyDialog("Info", "The Recycle Bin cannot be empty.\nDo it manually.", self.window)
            return
        self.model.clear()
        self.label6.setText("", self.window.size().width())
        self.label7.setText("", self.window.size().width())
        self.label8.setText("")
        # self.label9.setText("")
        self.label9.setText("", self.window.size().width())
        self.label10.setText("")
        if ret == -1:
            MyDialog("Info", "Error with some files in the Recycle Bin.\nTry to remove them manually.", self.window)
    
    # single click on item
    def flist(self, index):
        real_name = index.data(Qt.ItemDataRole.UserRole)
        itemName = os.path.basename(real_name)
        itemPath = os.path.dirname(real_name)
        #
        fake_name = index.data(Qt.ItemDataRole.UserRole+1)
        #
        deletionDate = index.data(Qt.ItemDataRole.UserRole+2)
        #
        self.label6.setText(itemName, self.window.size().width())
        self.label7.setText(itemPath, self.window.size().width())
        self.label8.setText(str(deletionDate).replace("T", " - "))
        #
        Tpath = trash_module.mountPoint(self.tdir).find_trash_path()
        fpath = os.path.join(Tpath, "files", fake_name)
        imime = QMimeDatabase().mimeTypeForFile(fpath, QMimeDatabase.MatchMode.MatchDefault)
        # self.label9.setText(imime.name())
        self.label9.setText(imime.name(), self.window.size().width())
        #
        if not os.path.exists(fpath):
            self.label10.setText("(Broken Link)")
        elif os.path.isfile(fpath):
            if os.access(fpath, os.R_OK):
                self.label10.setText(convert_size(QFileInfo(fpath).size()))
            else:
                self.label10.setText("(Not readable)")
        elif os.path.isdir(fpath):
            if os.access(fpath, os.R_OK):
                self.label10.setText(convert_size(folder_size(fpath)))
            else:
                self.label10.setText("(Not readable)")
    
    # double click on item
    def flist2(self, index):
        fake_name = index.data(Qt.ItemDataRole.UserRole+1)
        Tpath = trash_module.mountPoint(self.tdir).find_trash_path()
        path = os.path.join(Tpath, "files", fake_name)
        #
        if os.path.isdir(path):
            if os.access(path, os.R_OK):
                try:
                    self.window.openDir(path, 0)
                except Exception as E:
                    MyDialog("Error", str(E), self.window)
            else:
                MyDialog("Info", path+"\n\n   Not readable", self.window)
        elif os.path.isfile(path):
            perms = QFileInfo(path).permissions()
            # can be execute
            if perms & QFile.Permission.ExeOwner:
                MyDialog("Info", "Cannot execute this file.", self.window)
                return
                # imime = QMimeDatabase().mimeTypeForFile(path, QMimeDatabase.MatchMode.MatchDefault).name()
                # #
                # if imime == "application/x-desktop":
                    # MyDialog("Info", "Cannot execute this file.", self.window)
                    # return
                # #
                # if imime == "application/x-sharedlib":
                    # MyDialog("Info", "This is a binary file.", self.window)
                    # return
                # else:
                    # ret = execfileDialog(path, 3, self.window).getValue()
                # if ret == 2:
                    # try:
                        # subprocess.Popen(path, shell=True)
                    # except Exception as E:
                        # MyDialog("Error", str(E), self.window)
                    # finally:
                        # return
                # elif ret == -1:
                    # return
            #
            defApp = getDefaultApp(path).defaultApplication()
            #
            listPrograms = getAppsByMime(path).appByMime()
            USE_TERM = False
            #
            if defApp != "None":
                #
                if listPrograms:
                    for iprog in listPrograms:
                        # if iprog[2]:
                        if iprog[0] == defApp:
                            USE_TERM = DesktopEntry(iprog[2]).getTerminal()
                        # # skip programs working in terminal - bool True or False
                        # if USE_TERM:
                            # return
                        break
                #
                # execute the command
                r_defApp = defApp.split(" ")
                # self._flaunch_prog(r_defApp, path, USE_TERM)
                _flaunch_prog(r_defApp, path, USE_TERM)
    
    # # function for executing the command
    # def _flaunch_prog(self, r_defApp, path, USE_TERM):
        # try:
            # for eel in r_defApp[:]:
                # if eel == "%f":
                    # ridx = r_defApp.index(eel)
                    # r_defApp[ridx] = path
                    # break
                # elif eel == "%F":
                    # ridx = r_defApp.index(eel)
                    # r_defApp[ridx] = path
                    # break
                # elif eel == "%u":
                    # ridx = r_defApp.index(eel)
                    # r_defApp[ridx] = "file://"+path
                    # break
                # elif eel == "%U":
                    # ridx = r_defApp.index(eel)
                    # r_defApp[ridx] = "file://"+path
                    # break
            # #
            # if USE_TERM:
                # subprocess.Popen([USER_TERMINAL, "-e"]+r_defApp)
            # else:
                # subprocess.Popen(r_defApp)
        # except Exception as E:
            # MyDialog("Error", str(E), self.window)
    
    
    # show a menu
    def onRightClick(self, position):
        time.sleep(0.1)
        pointedItem = self.ilist.indexAt(position)
        if not pointedItem.isValid():
            return
        vr = self.ilist.visualRect(pointedItem)
        if pointedItem.isValid() and not vr:
            return
        pointedItem2 = self.ilist.indexAt(QPoint(int(vr.x()),int(vr.y())))
        if not pointedItem2.isValid():
            return
        if vr:
            # populate the data
            self.flist(pointedItem)
            #
            itemName = self.model.data(pointedItem2, Qt.ItemDataRole.UserRole+1)
            menu = QMenu("Menu", self.ilist)
            if MENU_H_COLOR:
                csaa = "QMenu { "
                csab = "background: {}".format(QPalette.ColorRole.Window)
                csac = "; margin: 1px; padding: 5px 5px 5px 5px;}"
                csad = " QMenu::item:selected { "
                csae = "background-color: {};".format(MENU_H_COLOR)
                csaf = " padding: 10px;}"
                csag = " QMenu::item:!selected {padding: 2px 15px 2px 10px;}"
                csa = csaa+csab+csac+csad+csae+csaf+csag
                menu.setStyleSheet(csa)
            Tpath = trash_module.mountPoint(self.tdir).find_trash_path()
            if os.path.isfile(os.path.join(Tpath, "files", itemName)):
                subm_openwithAction= menu.addMenu("Open with...")
                listPrograms = getAppsByMime(os.path.join(Tpath, "files", itemName)).appByMime()
                #
                ii = 0
                defApp = getDefaultApp(os.path.join(Tpath, "files", itemName)).defaultApplication()
                # r_defApp = defApp
                # if defApp:
                    # for eel in ["%f","%F","%u","%U"]:
                        # r_defApp = r_defApp.strip(eel).rstrip(" ")
                progActionList = []
                if listPrograms:
                    for iprog in listPrograms:
                        USE_TERM = False
                        if iprog[2]:
                            USE_TERM = DesktopEntry(iprog[2]).getTerminal()
                        # if USE_TERM:
                            # continue
                        #
                        if iprog[0] == defApp:
                            # progActionList.insert(0, QAction("{} - {} (Default)".format(os.path.basename(iprog), listPrograms[ii+1]), self))
                            prog_str = "{} (Default)".format(iprog[1])
                            if USE_TERM:
                                prog_str = "{} (Default - terminal)".format(iprog[1])
                            progActionList.insert(0, QAction(prog_str, self))
                            progActionList.insert(1, iprog)
                        else:
                            # progActionList.append(QAction("{} - {}".format(os.path.basename(iprog), listPrograms[ii+1]), self))
                            prog_str = "{}".format(iprog[1])
                            if USE_TERM:
                                prog_str = "{} (terminal)".format(iprog[1])
                            progActionList.append(QAction(prog_str, self))
                            progActionList.append(iprog)
                        ii += 2
                    #
                    ii = 0
                    for paction in progActionList[::2]:
                        paction.triggered.connect(lambda checked, index=ii:self.fprogAction(progActionList[index+1], os.path.join(Tpath, "files", itemName)))
                        subm_openwithAction.addAction(paction)
                        ii += 2
                subm_openwithAction.addSeparator()
                otherAction = QAction("Other Program")
                otherAction.triggered.connect(lambda:self.fotherAction(os.path.join(Tpath, "files", itemName)))
                subm_openwithAction.addAction(otherAction)
            #
            menu.exec(self.ilist.mapToGlobal(position))
    
    # launch the application choosen
    def fprogAction(self, iprog, path):
        defApp = iprog[0]
        USE_TERM = DesktopEntry(iprog[2]).getTerminal()
        # execute the command
        r_defApp = defApp.split(" ")
        # self._flaunch_prog(r_defApp, path, USE_TERM)
        _flaunch_prog(r_defApp, path, USE_TERM)
    
    # show a menu with all the installed applications
    def fotherAction(self, itemPath):
        if OPEN_WITH:
            self.cw = OW.listMenu(itemPath)
            self.cw.show()
        else:
            ret = otherApp(itemPath, self.window).getValues()
            if ret == -1:
                return
            if shutil.which(ret):
                try:
                    subprocess.Popen([ret, itemPath])
                except Exception as E:
                    MyDialog("Error", str(E), self.window)
            else:
                MyDialog("Info", "The program\n"+ret+"\ncannot be found", self.window)



class RestoreTrashedItems():
    def __init__(self):
        self.fakename = ""
        self.realname = ""
        #self.deletiondate = ""


class TrashModule():
    
    def __init__(self, list_items, window):
        self.list_items = list_items
        self.window = window
        self.trash_path = self.find_trash_path(self.list_items[0])
        self.Tfiles = os.path.join(self.trash_path, "files")
        self.Tinfo = os.path.join(self.trash_path, "info")
        self.can_trash = 0
        self.Ttrash_can_trash()
        #
        if self.can_trash:
            self.Tcan_trash(self.list_items)

    def find_trash_path(self, path):
        mount_point = ""
        while not os.path.ismount(path):
            path = os.path.dirname(path)
        mount_point = path
        #
        if mount_point == "/home" or mount_point == "/":
            trash_path = os.path.join(os.path.expanduser("~"), ".local/share/Trash")
        else:
            user_id = os.getuid()
            trash_path = os.path.join(mount_point, ".Trash-"+str(user_id))
        return trash_path

    def Ttrash_can_trash(self):
        if not os.path.exists(self.trash_path):
            if os.access(os.path.dirname(self.trash_path), os.W_OK):
                try:
                    os.mkdir(self.trash_path, 0o700)
                    os.mkdir(self.Tfiles, 0o700)
                    os.mkdir(self.Tinfo, 0o700)
                    self.can_trash = 1
                except Exception as E:
                    MyDialog("Error", str(E), self.window)
                    return
                finally:
                    return
            else:
                MyDialog("Info", "Cannot create the Trash folder.", self.window)
                return
        #
        if not os.access(self.Tfiles, os.W_OK):
            MyDialog("Info", "Cannot create the files folder.", self.window)
            return
        if not os.access(self.Tinfo, os.W_OK):
            MyDialog("Info", "Cannot create the info folder.", self.window)
            return
        #
        if os.access(self.trash_path, os.W_OK):
            if not os.path.exists(self.Tfiles):
                try:
                    os.mkdir(self.Tfiles, 0o700)
                except Exception as E:
                    MyDialog("Error", str(E), self.window)
                    return
            #
            if not os.path.exists(self.Tinfo):
                try:
                    os.mkdir(self.Tinfo, 0o700)
                except Exception as E:
                    MyDialog("Error", str(E), self.window)
                    return
            #
            self.can_trash = 1
            return
        #
        else:
            MyDialog("Info", "The Trash folder has wrong permissions.", self.window)
            return
        
    def Tcan_trash(self, list_items):
        for item_path in list_items:
            item = os.path.basename(item_path)
            tnow = datetime.datetime.now()
            del_time = tnow.strftime("%Y-%m-%dT%H:%M:%S")
            item_uri = quote("file://{}".format(item_path), safe='/:?=&')[7:]
            if os.path.exists(os.path.join(self.Tinfo, item+".trashinfo")):
                basename, suffix = os.path.splitext(item)
                i = 2
                aa = basename+"."+str(i)+suffix+".trashinfo"
                #
                while os.path.exists(os.path.join(self.Tinfo, basename+"."+str(i)+suffix+".trashinfo")):
                    i += 1
                else:
                    item = basename+"."+str(i)+suffix
            #
            try:
                shutil.move(item_path, os.path.join(self.Tfiles, item))
            except Exception as E:
                MyDialog("Error", str(E), self.window)
                continue
            ifile = open(os.path.join(self.Tinfo, "{}.trashinfo".format(item)),"w")
            ifile.write("[Trash Info]\n")
            ifile.write("Path={}\n".format(item_uri))
            ifile.write("DeletionDate={}\n".format(del_time))
            ifile.close()


###################### END TRASHCAN #####################

#################### TREEVIEW
# for treeview
class itemDelegateT(QItemDelegate):
    
    def __init__(self, parent=None):
        super(itemDelegateT, self).__init__(parent)
        # store the max text width from all the FileNameRole
        self.max = 0

    def paint(self, painter, option, index):
        column = index.column()
        painter.save()
        #
        if option.state & QStyle.StateFlag.State_Selected:
            painter.setBrush(option.palette.color(QPalette.ColorRole.Highlight))
            painter.setPen(option.palette.color(QPalette.ColorRole.Highlight))
            painter.drawRect(QRect(option.rect.x(),option.rect.y(),ITEM_WIDTH_ALT+self.max,ITEM_HEIGHT_ALT))
        #
        painter.restore()
        #
        if column == 0:
            iicon = index.data(QFileSystemModel.Roles.FileIconRole)
            ppath = index.data(QFileSystemModel.Roles.FilePathRole)
            if iicon:
                # icon
                pixmap = iicon.pixmap(QSize(ICON_SIZE_ALT, ICON_SIZE_ALT))
                pixel_ratio = pixmap.devicePixelRatio()
                size_pixmap = pixmap.size()
                pw =int( size_pixmap.width()/pixel_ratio)
                ph = int(size_pixmap.height()/pixel_ratio)
                xpad = int((ITEM_WIDTH_ALT - pw) / 2)
                ypad = int((ITEM_HEIGHT_ALT - ph) / 2)
                painter.drawPixmap(option.rect.x() + xpad,option.rect.y() + ypad, -1,-1, pixmap,0,0,-1,-1)
                # text
                painter.save()
                if TCOLOR:
                    if option.state & QStyle.StateFlag.State_Selected:
                        painter.setPen(option.palette.color(QPalette.ColorRole.HighlightedText))
                    else:
                        painter.setPen(QColor(TRED,TGREEN,TBLUE))
                else:
                    if option.state & QStyle.StateFlag.State_Selected:
                        painter.setPen(option.palette.color(QPalette.ColorRole.HighlightedText))
                #
                qstring = index.data(QFileSystemModel.Roles.FileNameRole)
                st = QStaticText(qstring)
                hh = int(st.size().height())
                to = QTextOption(Qt.AlignmentFlag.AlignLeft)
                st.setTextOption(to)
                painter.drawStaticText(option.rect.x()+ITEM_WIDTH_ALT, option.rect.y()+int(hh/2), st)
                #
                painter.restore()
                # permissions icon
                if not os.path.isdir(ppath):
                    if not index.data(QFileSystemModel.Roles.FilePermissions) & QFile.Permission.WriteUser.value or not index.data(QFileSystemModel.Roles.FilePermissions) & QFile.Permission.ReadUser.value:
                        ppixmap = QPixmap('icons/emblem-readonly.svg').scaled(ICON_SIZE2_ALT, ICON_SIZE2_ALT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
                        painter.drawPixmap(option.rect.x(), int(option.rect.y()+ITEM_HEIGHT_ALT-ICON_SIZE2_ALT),-1,-1, ppixmap,0,0,-1,-1)
                    # 
                    if os.path.islink(ppath):
                        lpixmap = QPixmap('icons/emblem-symbolic-link.svg').scaled(ICON_SIZE2_ALT, ICON_SIZE2_ALT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
                        painter.drawPixmap(int(option.rect.x()+ITEM_WIDTH_ALT-ICON_SIZE2_ALT), int(option.rect.y()+ITEM_HEIGHT_ALT-ICON_SIZE2_ALT),-1,-1, lpixmap,0,0,-1,-1)
                else:
                    if not index.data(QFileSystemModel.Roles.FilePermissions) & QFile.Permission.WriteUser.value or not index.data(QFileSystemModel.Roles.FilePermissions) & QFile.Permission.ReadUser.value or not index.data(QFileSystemModel.Roles.FilePermissions) & QFile.Permission.ExeOwner.value:
                        ppixmap = QPixmap('icons/emblem-readonly.svg').scaled(ICON_SIZE2_ALT, ICON_SIZE2_ALT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
                        painter.drawPixmap(option.rect.x(), int(option.rect.y()+ITEM_HEIGHT_ALT-ICON_SIZE2_ALT),-1,-1, ppixmap,0,0,-1,-1)
                    # link emblem
                    if os.path.islink(ppath):
                        lpixmap = QPixmap('icons/emblem-symbolic-link.svg').scaled(ICON_SIZE2_ALT, ICON_SIZE2_ALT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
                        painter.drawPixmap(int(option.rect.x()+ITEM_WIDTH_ALT-ICON_SIZE2_ALT), int(option.rect.y()+ITEM_HEIGHT_ALT-ICON_SIZE2_ALT),-1,-1, lpixmap,0,0,-1,-1)
                # # link icon
                # if os.path.islink(ppath):
                    # lpixmap = QPixmap('icons/emblem-symbolic-link.svg').scaled(ICON_SIZE2_ALT, ICON_SIZE2_ALT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
                    # painter.drawPixmap(int(option.rect.x()+ITEM_WIDTH_ALT-ICON_SIZE2_ALT), int(option.rect.y()+ITEM_HEIGHT_ALT-ICON_SIZE2_ALT),-1,-1, lpixmap,0,0,-1,-1)
        else:
            QItemDelegate.paint(self, painter, option, index)

    def sizeHint(self, option, index):
        # file name
        qstring = index.data(QFileSystemModel.Roles.FileNameRole)
        st = QStaticText(qstring)
        to = QTextOption(Qt.AlignmentFlag.AlignLeft)
        st.setTextOption(to)
        ww = int(st.size().width())
        if ITEM_WIDTH_ALT+ww > self.max:
            self.max = ITEM_WIDTH_ALT+ww
        return QSize(ITEM_WIDTH_ALT+ww, ITEM_HEIGHT_ALT)

# treeview
class cTView(QBoxLayout):
    def __init__(self, TLVDIR, window, flag, parent=None):
        super(cTView, self).__init__(QBoxLayout.Direction.TopToBottom, parent)
        self.window = window
        self.flag = flag
        self.setContentsMargins(QMargins(0,0,0,0))
        self.lvDir = "/"
        # the file passed as argument - half implemented
        self.lvFile = ""
        #
        if TLVDIR != "/":
            if os.path.exists(TLVDIR):
                if os.path.isdir(TLVDIR):
                    self.lvDir = TLVDIR
                elif os.path.isfile(TLVDIR) or os.path.islink(TLVDIR):
                    self.lvDir = os.path.dirname(TLVDIR)
                    self.lvFile = os.path.basename(TLVDIR)
                else:
                    self.lvDir = os.path.dirname(TLVDIR)
        #
        # the filter for show/hide hidden items
        self.fmf = 0
        # the item selected
        self.selection = None
        #
        # the treeview widget
        self.tview = QTreeView()
        # folder dont expand
        self.tview.setItemsExpandable(False)
        # no expanding icon on folders
        self.tview.setRootIsDecorated(False)
        # rows have alternate colours
        self.tview.setAlternatingRowColors(True)
        #
        # self.tview.setSelectionMode(3)
        self.tview.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        # 
        self.tview.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        self.tview.setItemDelegate(itemDelegateT())
        self.tview.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tview.customContextMenuRequested.connect(self.onRightClick)
        self.tview.setSortingEnabled(True)
        self.tview.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        # DnD
        self.tview.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
        # self.tview.setDragEnabled(True)
        # self.tview.setAcceptDrops(True)
        # self.tview.setDropIndicatorShown(True)
        # default model
        self.tmodel = QFileSystemModel(self.tview)
        self.fileModel = self.tmodel
        self.window.fileModel = self.tmodel
        # 
        self.tmodel.setIconProvider(IconProvider())
        self.tmodel.setReadOnly(False)
        root = self.tmodel.setRootPath(self.lvDir)
        self.tview.setModel(self.tmodel)
        self.tview.setRootIndex(root)
        # 
        self.tview.setIconSize(QSize(ICON_SIZE_ALT, ICON_SIZE_ALT))
        #
        self.tview.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        #
        self.tview.selectionModel().selectionChanged.connect(self.lselectionChanged)
        #
        if USE_TRASH:
            self.clickable2(self.tview).connect(self.itemsToTrash)
        elif USE_DELETE:
            self.clickable2(self.tview).connect(self.fdeleteAction)
        #
        self.tview.doubleClicked.connect(self.doubleClick)
        self.tview.clicked.connect(self.singleClick)
        #
        # the background color
        if USE_BACKGROUND_COLOUR == 1:
            palette = self.tview.palette()
            palette.setColor(QPalette.ColorRole.Base, QColor(ORED,OGREEN,OBLUE))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(ORED2,OGREEN2,OBLUE2))
            self.tview.setPalette(palette)
        #
        self.addWidget(self.tview, 1)
    
    # set the model in MainWin
    def setfModel(self):
        self.window.fileModel = self.fileModel

    # send to trash or delete the selected items
    def clickable2(self, widget):
        class Filter(QObject):
            clicked = pyqtSignal()
            def eventFilter(self, obj, event):
                if obj == widget:
                    if event.type() == QEvent.Type.KeyRelease:
                        if event.key() == Qt.Key.Key_Delete:
                            self.clicked.emit()
                return False
        #
        filter = Filter(widget)
        widget.installEventFilter(filter)
        return filter.clicked
    
    # single click
    def singleClick(self, index):
        self.tview.viewport().update()
    
    # double click on item
    def doubleClick(self, index):
        path = self.tmodel.fileInfo(index).absoluteFilePath()
        #
        if not os.path.exists(path):
            MyDialog("Info", "It doesn't exist.", self.window)
            return
        #
        if os.path.isdir(path):
            if os.access(path, os.R_OK):
                try:
                    self.tview.clearSelection()
                    self.lvDir = path
                    self.window.mtab.setTabText(self.window.mtab.currentIndex(), os.path.basename(self.lvDir))
                    self.window.mtab.setTabToolTip(self.window.mtab.currentIndex(), self.lvDir)
                    self.tview.setRootIndex(self.fileModel.setRootPath(path))
                    # scroll to top
                    self.tview.verticalScrollBar().setValue(0)
                except Exception as E:
                    MyDialog("Error", str(E), self.window)
            else:
                MyDialog("Info", path+"\n\n   Not readable", self.window)
        elif os.path.isfile(path):
            perms = QFileInfo(path).permissions()
            if perms & QFile.Permission.ExeOwner:
                imime = QMimeDatabase().mimeTypeForFile(path, QMimeDatabase.MatchMode.MatchDefault).name()
                if imime == "application/x-desktop":
                    MyDialog("Info", "Cannot execute this file.", self.window)
                    return
                if imime == "application/x-sharedlib":
                    ret = execfileDialog(path, 1, self.window).getValue()
                else:
                    ret = execfileDialog(path, 0, self.window).getValue()
                #
                if ret == 2:
                    try:
                        subprocess.Popen(path, shell=True, cwd=os.path.dirname(path))
                    except Exception as E:
                        MyDialog("Error", str(E), self.window)
                    finally:
                        return
                elif ret == -1:
                    return
            #
            defApp = getDefaultApp(path).defaultApplication()
            #
            listPrograms = getAppsByMime(os.path.join(self.lvDir, path)).appByMime()
            USE_TERM = False
            #
            if defApp != "None":
                #
                if listPrograms:
                    for iprog in listPrograms:
                        # if iprog[2]:
                        if iprog[0] == defApp:
                            USE_TERM = DesktopEntry(iprog[2]).getTerminal()
                        # # skip programs working in terminal - bool True or False
                        # if USE_TERM:
                            # return
                        break
                #
                # execute the command
                r_defApp = defApp.split(" ")
                # self._flaunch_prog(r_defApp, path, USE_TERM)
                _flaunch_prog(r_defApp, path, USE_TERM)
            else:
                MyDialog("Info", "No programs found.", self.window)
    
    # # function for executing the command
    # def _flaunch_prog(self, r_defApp, path, USE_TERM):
        # try:
            # for eel in r_defApp[:]:
                # if eel == "%f":
                    # ridx = r_defApp.index(eel)
                    # r_defApp[ridx] = path
                    # break
                # elif eel == "%F":
                    # ridx = r_defApp.index(eel)
                    # r_defApp[ridx] = path
                    # break
                # elif eel == "%u":
                    # ridx = r_defApp.index(eel)
                    # r_defApp[ridx] = "file://"+path
                    # break
                # elif eel == "%U":
                    # ridx = r_defApp.index(eel)
                    # r_defApp[ridx] = "file://"+path
                    # break
            # #
            # if USE_TERM:
                # subprocess.Popen([USER_TERMINAL, "-e"]+r_defApp)
            # else:
                # subprocess.Popen(r_defApp)
        # except Exception as E:
            # MyDialog("Error", str(E), self.window)
    
    
    #  send to trash or delete the selected items - function
    def itemsToTrash(self):
        if self.selection:
            # only items in the HOME dir or in mass storages
            len_home = len(os.path.expanduser("~"))
            if self.lvDir[0:len_home] == os.path.expanduser("~") or self.flag in [3,4]:
                  self.ftrashAction()
    
    def lselectionChanged(self):
        self.selection_temp = self.tview.selectionModel().selectedIndexes()
        self.selection = []
        for el in self.selection_temp:
            if el.column() == 0:
                self.selection.append(el)

    # mouse right click on the pointed item
    def onRightClick(self, position):
        if self.flag == 0:
            return
        time.sleep(0.2)
        #
        if self.selection:
            if self.selection[0] == None:
                return
        #
        pointedItem = self.tview.indexAt(position)
        vr = self.tview.visualRect(pointedItem)
        if pointedItem.isValid() and not vr:
            return
        pointedItem2 = self.tview.indexAt(QPoint(int(vr.x()),int(vr.y())))
        # the items
        if vr:
            itemName = self.tmodel.data(pointedItem2, Qt.ItemDataRole.DisplayRole)
            #
            if not os.path.exists(os.path.join(self.lvDir, itemName)):
                MyDialog("Info", "It doesn't exist.", self.window)
                return
            #
            menu = QMenu("Menu", self.tview)
            if MENU_H_COLOR:
                csaa = "QMenu { "
                csab = "background: {}".format(QPalette.ColorRole.Window)
                csac = "; margin: 1px; padding: 5px 5px 5px 5px;}"
                csad = " QMenu::item:selected { "
                csae = "background-color: {};".format(MENU_H_COLOR)
                csaf = " padding: 10px;}"
                csag = " QMenu::item:!selected {padding: 2px 15px 2px 10px;}"
                csa = csaa+csab+csac+csad+csae+csaf+csag
                menu.setStyleSheet(csa)
            #
            if self.selection != None:
                if len(self.selection) == 1:
                    if os.path.isfile(os.path.join(self.lvDir, itemName)):
                        subm_openwithAction= menu.addMenu("Open with...")
                        listPrograms = getAppsByMime(os.path.join(self.lvDir, itemName)).appByMime()
                        ii = 0
                        defApp = getDefaultApp(os.path.join(self.lvDir, itemName)).defaultApplication()
                        # r_defApp = defApp
                        # if defApp:
                            # for eel in ["%f","%F","%u","%U"]:
                                # r_defApp = r_defApp.strip(eel).rstrip(" ")
                        progActionList = []
                        if listPrograms:
                            for iprog in listPrograms:
                                USE_TERM = False
                                if iprog[2]:
                                    USE_TERM = DesktopEntry(iprog[2]).getTerminal()
                                # if USE_TERM:
                                    # continue
                                #
                                # if iprog == r_defApp:
                                if iprog[0] == defApp:
                                    # progActionList.insert(0, QAction("{} - {} (Default)".format(os.path.basename(iprog), listPrograms[ii+1]), self))
                                    prog_str = "{} (Default)".format(iprog[1])
                                    if USE_TERM:
                                        prog_str = "{} (Default - terminal)".format(iprog[1])
                                    progActionList.insert(0, QAction(prog_str, self))
                                    progActionList.insert(1, iprog)
                                else:
                                    # progActionList.append(QAction("{} - {}".format(os.path.basename(iprog), listPrograms[ii+1]), self))
                                    prog_str = "{}".format(iprog[1])
                                    if USE_TERM:
                                        prog_str = "{} (terminal)".format(iprog[1])
                                    progActionList.append(QAction(prog_str, self))
                                    progActionList.append(iprog)
                                ii += 2
                            ii = 0
                            for paction in progActionList[::2]:
                                paction.triggered.connect(lambda checked, index=ii:self.fprogAction(progActionList[index+1], os.path.join(self.lvDir, itemName)))
                                subm_openwithAction.addAction(paction)
                                ii += 2
                        subm_openwithAction.addSeparator()
                        otherAction = QAction("Other Program")
                        otherAction.triggered.connect(lambda:self.fotherAction(os.path.join(self.lvDir, itemName)))
                        subm_openwithAction.addAction(otherAction)
                        #
                        menu.addSeparator()
                    elif os.path.isdir(os.path.join(self.lvDir, itemName)):
                        newtabAction = QAction("Open in a new tab")
                        newtabAction.triggered.connect(lambda:self.fnewtabAction(os.path.join(self.lvDir, itemName), self.flag))
                        menu.addAction(newtabAction)
                        menu.addSeparator()
            #
            menu.addSeparator()
            if self.flag == 1 or self.flag == 3:
                newFolderAction = QAction("New Folder", self)
                newFolderAction.triggered.connect(self.fnewFolderAction)
                menu.addAction(newFolderAction)
                newFileAction = QAction("New File", self)
                newFileAction.triggered.connect(self.fnewFileAction)
                menu.addAction(newFileAction)
                #
                templateDir = None
                optTemplateDir = os.path.join(os.path.expanduser("~"), TEMPLATE_DIR)
                if os.path.exists(optTemplateDir):
                    templateDir = optTemplateDir
                    #
                    menu.addSeparator()
                    subm_templatesAction= menu.addMenu(TEMPLATE_DIR)
                    listTemplate = os.listdir(templateDir)

                    progActionListT = []
                    for ifile in listTemplate:
                        progActionListT.append(QAction(ifile))
                        progActionListT.append(ifile)
                    ii = 0
                    for paction in progActionListT[::2]:
                        paction.triggered.connect(lambda checked, index=ii:self.ftemplateAction(progActionListT[index+1]))
                        subm_templatesAction.addAction(paction)
                        ii += 2
            #
            menu.addSeparator()
            copyAction = QAction("Copy", self)
            copyAction.triggered.connect(lambda:self.fcopycutAction("copy"))
            menu.addAction(copyAction)
            #
            if self.flag == 1 or self.flag == 3:
                copyAction = QAction("Cut", self)
                copyAction.triggered.connect(lambda:self.fcopycutAction("cut"))
                menu.addAction(copyAction)
            #
            if self.flag == 1 or self.flag == 3:
                pasteNmergeAction = QAction("Paste", self)
                pasteNmergeAction.triggered.connect(lambda d:PastenMerge(self.lvDir, -3, "", self.window))
                menu.addAction(pasteNmergeAction)
                # check the clipboard for data
                clipboard = QApplication.clipboard()
                mimeData = clipboard.mimeData(QClipboard.Mode.Clipboard)
                if "x-special/gnome-copied-files" not in mimeData.formats():
                    pasteNmergeAction.setEnabled(False)
            #
            menu.addSeparator()
            #
            if USE_TRASH:
                # only items in the HOME dir or in mass storages
                len_home = len(os.path.expanduser("~"))
                if self.lvDir[0:len_home] == os.path.expanduser("~") or self.flag in [3,4]:
                    if self.flag == 1 or self.flag == 3:
                        if isXDGDATAHOME:
                            trashAction = QAction("Trash", self)
                            trashAction.triggered.connect(self.ftrashAction)
                            menu.addAction(trashAction)
            # delete function
            if USE_DELETE:
                if self.flag == 1 or self.flag == 3:
                    deleteAction = QAction("Delete", self)
                    deleteAction.triggered.connect(self.fdeleteAction)
                    menu.addAction(deleteAction)
            #
            if self.flag == 1 or self.flag == 3:
                if self.selection and len(self.selection) == 1:
                    menu.addSeparator()
                    renameAction = QAction("Rename", self)
                    ipath = self.tmodel.fileInfo(self.selection[0]).absoluteFilePath()
                    renameAction.triggered.connect(lambda:self.frenameAction(ipath))
                    menu.addAction(renameAction)
            #
            menu.addSeparator()
            subm_customAction = menu.addMenu("Actions")
            #
            if len(list_custom_modules) > 0:
                listActions = []
                for el in list_custom_modules:
                    if el.mmodule_type(self) == 1 and self.selection and len(self.selection) == 1:
                        icustomAction = QAction(el.mmodule_name(), self)
                        listActions.append(icustomAction)
                        listActions.append(el)
                        listActions.append(1)
                    elif el.mmodule_type(self) == 2 and self.selection and len(self.selection) > 1:
                        icustomAction = QAction(el.mmodule_name(), self)
                        listActions.append(icustomAction)
                        listActions.append(el)
                        listActions.append(2)
                    elif el.mmodule_type(self) == 3 and self.selection and len(self.selection) > 0:
                        icustomAction = QAction(el.mmodule_name(), self)
                        listActions.append(icustomAction)
                        listActions.append(el)
                        listActions.append(3)
                    elif el.mmodule_type(self) == 4 or el.mmodule_type(self) == 5:
                        icustomAction = QAction(el.mmodule_name(), self)
                        listActions.append(icustomAction)
                        listActions.append(el)
                        listActions.append(5)
                ii = 0
                for paction in listActions[::3]:
                    paction.triggered.connect(lambda checked, index=ii:self.ficustomAction(listActions[index+1], listActions[index+2]))
                    subm_customAction.addAction(paction)
                    ii += 3
            #
            menu.addSeparator()
            # upButton
            upAction = QAction("Go Up", self)
            upAction.triggered.connect(self.upButton)
            menu.addAction(upAction)
            # show the hidden items
            hiddenAction = QAction("Hidden items", self)
            hiddenAction.triggered.connect(self.fhidbtn)
            menu.addAction(hiddenAction)
            #
            menu.addSeparator()
            if self.selection and len(self.selection) == 1:
                ipath = self.tmodel.fileInfo(self.selection[0]).absoluteFilePath()
                if os.path.exists(ipath):
                    propertyAction = QAction("Property", self)
                    propertyAction.triggered.connect(lambda:self.fpropertyAction(ipath))
                    menu.addAction(propertyAction)
            #
            elif self.selection and len(self.selection) > 1:
                propertyAction = QAction("Property", self)
                propertyAction.triggered.connect(self.fpropertyActionMulti)
                menu.addAction(propertyAction)
            #
            menu.exec(self.tview.mapToGlobal(position))
        # background
        else:
            menu = QMenu("Menu", self.tview)
            if MENU_H_COLOR:
                csaa = "QMenu { "
                csab = "background: {}".format(QPalette.ColorRole.Window)
                csac = "; margin: 1px; padding: 5px 5px 5px 5px;}"
                csad = " QMenu::item:selected { "
                csae = "background-color: {};".format(MENU_H_COLOR)
                csaf = " padding: 10px;}"
                csag = " QMenu::item:!selected {padding: 2px 15px 2px 10px;}"
                csa = csaa+csab+csac+csad+csae+csaf+csag
                menu.setStyleSheet(csa)
            #
            if self.flag == 1 or self.flag == 3:
                newFolderAction = QAction("New Folder", self)
                newFolderAction.triggered.connect(self.fnewFolderAction)
                menu.addAction(newFolderAction)
                newFileAction = QAction("New File", self)
                newFileAction.triggered.connect(self.fnewFileAction)
                menu.addAction(newFileAction)
                #
                templateDir = None
                optTemplateDir = os.path.join(os.path.expanduser("~"), TEMPLATE_DIR)
                if os.path.exists(optTemplateDir):
                    templateDir = optTemplateDir
                    #
                    menu.addSeparator()
                    subm_templatesAction= menu.addMenu(TEMPLATE_DIR)
                    listTemplate = os.listdir(templateDir)

                    progActionListT = []
                    for ifile in listTemplate:
                        progActionListT.append(QAction(ifile))
                        progActionListT.append(ifile)
                    ii = 0
                    for paction in progActionListT[::2]:
                        paction.triggered.connect(lambda checked, index=ii:self.ftemplateAction(progActionListT[index+1]))
                        subm_templatesAction.addAction(paction)
                        ii += 2
                #
                menu.addSeparator()
                # paste operation
                pasteNmergeAction = QAction("Paste", self)
                pasteNmergeAction.triggered.connect(lambda d:PastenMerge(self.lvDir, -3, "", self.window))
                menu.addAction(pasteNmergeAction)
                # check the clipboard for data
                clipboard = QApplication.clipboard()
                mimeData = clipboard.mimeData(QClipboard.Mode.Clipboard)
                if "x-special/gnome-copied-files" not in mimeData.formats():
                    pasteNmergeAction.setEnabled(False)
            #
            menu.addSeparator()
            #
            subm_customAction = menu.addMenu("Actions")
            #
            if len(list_custom_modules) > 0:
                listActions = []
                for el in list_custom_modules:
                    if el.mmodule_type(self) == 1 and self.selection and len(self.selection) == 1:
                        icustomAction = QAction(el.mmodule_name(), self)
                        listActions.append(icustomAction)
                        listActions.append(el)
                        listActions.append(1)
                    elif el.mmodule_type(self) == 2 and self.selection and len(self.selection) > 1:
                        icustomAction = QAction(el.mmodule_name(), self)
                        listActions.append(icustomAction)
                        listActions.append(el)
                        listActions.append(2)
                    elif el.mmodule_type(self) == 3 and self.selection and len(self.selection) > 0:
                        icustomAction = QAction(el.mmodule_name(), self)
                        listActions.append(icustomAction)
                        listActions.append(el)
                        listActions.append(3)
                    elif el.mmodule_type(self) == 4:
                        icustomAction = QAction(el.mmodule_name(), self)
                        listActions.append(icustomAction)
                        listActions.append(el)
                        listActions.append(4)
                    elif el.mmodule_type(self) == 5:
                        icustomAction = QAction(el.mmodule_name(), self)
                        listActions.append(icustomAction)
                        listActions.append(el)
                        listActions.append(5)
                ii = 0
                for paction in listActions[::3]:
                    paction.triggered.connect(lambda checked, index=ii:self.ficustomAction(listActions[index+1], listActions[index+2]))
                    subm_customAction.addAction(paction)
                    ii += 3
            #
            menu.addSeparator()
            # upButton
            upAction = QAction("Go Up", self)
            upAction.triggered.connect(self.upButton)
            menu.addAction(upAction)
            # show the hidden items
            hiddenAction = QAction("Hidden items", self)
            hiddenAction.triggered.connect(self.fhidbtn)
            menu.addAction(hiddenAction)
            #
            menu.exec(self.tview.mapToGlobal(position))
    
        
    # launch the application choosen
    def fprogAction(self, iprog, path):
        defApp = iprog[0]
        USE_TERM = DesktopEntry(iprog[2]).getTerminal()
        # execute the command
        r_defApp = defApp.split(" ")
        # self._flaunch_prog(r_defApp, path, USE_TERM)
        _flaunch_prog(r_defApp, path, USE_TERM)
    
    def fnewFolderAction(self):
        if os.access(self.lvDir, os.W_OK): 
            ret = self.wrename3("New Folder", self.lvDir)
            if ret != -1 or not ret:
                destPath = os.path.join(self.lvDir, ret)
                if not os.path.exists(destPath):
                    try:
                        os.mkdir(destPath)
                    except Exception as E:
                        MyDialog("Error", str(E), self.window)
    
    def fnewFileAction(self):
        if os.access(self.lvDir, os.W_OK): 
            ret = self.wrename3("Text file.txt", self.lvDir)
            if ret != -1 or not ret:
                destPath = os.path.join(self.lvDir, ret)
                if not os.path.exists(destPath):
                    try:
                        iitem = open(destPath,'w')
                        iitem.close()
                    except Exception as E:
                        MyDialog("Error", str(E), self.window)
    
    def ftemplateAction(self, templateName):
        templateDir = None
        optTemplateDir = os.path.join(os.path.expanduser("~"), TEMPLATE_DIR)
        if os.path.exists(optTemplateDir):
            templateDir = optTemplateDir
        else:
            return
        #
        if os.access(self.lvDir, os.W_OK): 
            ret = self.wrename3(templateName, self.lvDir)
            if ret != -1 or not ret:
                destPath = os.path.join(self.lvDir, ret)
                if not os.path.exists(destPath):
                    try:
                        shutil.copy(os.path.join(templateDir, templateName), destPath)
                    except Exception as E:
                        MyDialog("Error", str(E), self.window)
    
    # new file or folder
    def wrename3(self, ditem, dest_path):
        #
        ret = MyDialogRename3(ditem, self.lvDir, self.window).getValues()
        if ret == -1:
                return ret
        elif not ret:
            return -1
        else:
            return ret

    # show a menu with all the installed applications
    def fotherAction(self, itemPath):
        if OPEN_WITH:
            self.cw = OW.listMenu(itemPath)
            self.cw.show()
        else:
            ret = otherApp(itemPath, self.window).getValues()
            if ret == -1:
                return
            if shutil.which(ret):
                try:
                    subprocess.Popen([ret, itemPath])
                except Exception as E:
                    MyDialog("Error", str(E), self.window)
            else:
                MyDialog("Info", "The program\n"+ret+"\ncannot be found", self.window)

    #
    def fcopycutAction(self, action):
        if action == "copy":
            item_list = "copy\n"
        elif action == "cut":
            item_list = "cut\n"
        #
        for iindex in self.selection:
            iname = iindex.data(QFileSystemModel.Roles.FileNameRole)
            iname_fp = os.path.join(self.lvDir, iname)
            ## readable or broken link
            if os.access(iname_fp,os.R_OK) or os.path.islink(iname_fp):
                iname_quoted = quote(iname, safe='/:?=&')
                if iindex != self.selection[-1]:
                    iname_final = "file://{}\n".format(os.path.join(self.lvDir, iname_quoted))
                    item_list += iname_final
                else:
                    iname_final = "file://{}".format(os.path.join(self.lvDir, iname_quoted))
                    item_list += iname_final
        #
        if item_list == "copy\n":
            clipboard = QApplication.clipboard()
            clipboard.clear()
            return
        #
        clipboard = QApplication.clipboard()
        data = QByteArray()
        data.append(bytes(item_list, encoding="utf-8"))
        qmimdat = QMimeData()
        qmimdat.setData("x-special/gnome-copied-files", data)
        clipboard.setMimeData(qmimdat, QClipboard.Mode.Clipboard)

    # items in the trash can
    def ftrashAction(self):
        if self.selection:
            list_items = []
            for item in self.selection:
                list_items.append(self.tmodel.fileInfo(item).absoluteFilePath())
            # if more than 30 items no list
            if len(self.selection) < ITEMSDELETED:
                dialogList = ""
                for item in list_items:
                    dialogList += os.path.basename(item)+"\n"
                ret = retDialogBox("Question", "Do you really want to move these items to the trashcan?", "", dialogList, self.window)
            else:
                ret = retDialogBox("Question", "Do you really want to move these items to the trashcan?", "", "Too many items.\n", self.window)
            #
            if ret.getValue():
                TrashModule(list_items, self.window)
                self.tview.viewport().update()
    
    # bypass the trashcan
    def fdeleteAction(self):
        if self.selection:
            list_items = []
            for item in self.selection:
                list_items.append(self.tmodel.fileInfo(item).absoluteFilePath())
            #
            # if more than 30 items no list
            if len(self.selection) < ITEMSDELETED:
                dialogList = ""
                for item in list_items:
                    dialogList += os.path.basename(item)+"\n"
                ret = retDialogBox("Question", "Do you really want to delete these items?", "", dialogList, self.window)
            else:
                ret = retDialogBox("Question", "Do you really want to delete these items?", "", "Too many items.\n", self.window)
            #
            if ret.getValue():
                self.fdeleteItems(list_items)
                self.tview.viewport().update()
    
    #
    def fdeleteItems(self, listItems):
        # something happened with some items
        items_skipped = ""
        #
        for item in listItems:
            time.sleep(0.1)
            if os.path.islink(item):
                try:
                    os.remove(item)
                except Exception as E:
                    items_skipped += os.path.basename(item)+"\n"+str(E)+"\n\n"
            elif os.path.isfile(item):
                try:
                    os.remove(item)
                except Exception as E:
                    items_skipped += os.path.basename(item)+"\n"+str(E)+"\n\n"
            elif os.path.isdir(item):
                try:
                    shutil.rmtree(item)
                except Exception as E:
                    items_skipped += os.path.basename(item)+"\n"+str(E)+"\n\n"
            # not regular files or folders 
            else:
                items_skipped += os.path.basename(item)+"\n"+"Only files and folders can be deleted."+"\n\n"
        #
        if items_skipped != "":
            MyMessageBox("Info", "Items not deleted:", "", items_skipped, self.window)

    
    def wrename2(self, ditem, dest_path):
        ret = ditem
        ret = MyDialogRename2(ditem, dest_path, self.window).getValues()
        if ret == -1:
                return ret
        elif not ret:
            return -1
        else:
            return os.path.join(dest_path, ret)
    
    def frenameAction(self, ipath):
        ibasename = os.path.basename(ipath)
        idirname = os.path.dirname(ipath)
        inew_name = self.wrename2(ibasename, idirname)
        #
        if inew_name != -1:
            try:
                shutil.move(ipath, inew_name)
            except Exception as E:
                MyDialog("Error", str(E), self.window)

    def ficustomAction(self, el, menuType):
        if menuType == 1:
            items_list = []
            items_list.append(self.tmodel.fileInfo(self.selection[0]).absoluteFilePath())
            el.ModuleCustom(self)
        elif menuType == 2:
            items_list = []
            for iitem in self.selection:
                items_list.append(self.tmodel.fileInfo(iitem).absoluteFilePath())
            el.ModuleCustom(self)
        elif menuType == 3:
            items_list = []
            for iitem in self.selection:
                items_list.append(self.tmodel.fileInfo(iitem).absoluteFilePath())
            el.ModuleCustom(self)
        elif menuType == 4:
            el.ModuleCustom(self)
        elif menuType == 5:
            items_list = []
            for iitem in self.selection:
                items_list.append(self.tmodel.fileInfo(iitem).absoluteFilePath())
            el.ModuleCustom(self)
    
    def fpropertyActionMulti(self):
        # size of all the selected items
        iSize = 0
        # # number of the selected items
        # iNum = len(self.selection)
        item_list = []
        for iitem in self.selection:
            try:
                item = self.tmodel.fileInfo(iitem).absoluteFilePath()
                #
                if os.path.islink(item):
                    iSize += 512
                    continue
                elif os.path.isfile(item):
                    iSize += QFileInfo(item).size()
                    item_list.append(item)
                elif os.path.isdir(item):
                    iSize += folder_size(item)
                    item_list.append(item)
                # else:
                    # QFileInfo(item).size()
            except:
                iSize += 0
        #
        # propertyDialogMulti(convert_size(iSize), iNum, self.window)
        propertyDialogMulti(item_list, convert_size(iSize), self.window)
    
    # item property dialog
    def fpropertyAction(self, ipath):
        propertyDialog(ipath, self.window)


    # go to the parent folder
    def upButton(self):
        if self.lvDir != "/":
            path = os.path.dirname(self.lvDir)
            # the path can be unreadable for any reasons
            if not os.access(path, os.R_OK):
                MyDialog("Error", "The folder\n"+path+"\nis not readable anymore.", self.window)
                return
            # check for an existent directory
            while not os.path.exists(path):
                path = os.path.dirname(path)
            #
            self.tview.clearSelection()
            # to highlight the upper folder
            upperdir = self.lvDir
            self.lvDir = path
            self.window.mtab.setTabText(self.window.mtab.currentIndex(), os.path.basename(self.lvDir) or "ROOT")
            self.window.mtab.setTabToolTip(self.window.mtab.currentIndex(), self.lvDir)
            self.tview.setRootIndex(self.tmodel.setRootPath(path))
            #
            index = self.tmodel.index(upperdir)
            # skip hidden folders
            if not index.data(QFileSystemModel.Roles.FileNameRole)[0] == ".":
                self.tview.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select)
                self.tview.scrollTo(index, QAbstractItemView.ScrollHint.EnsureVisible)


    def fhidbtn(self):
        if self.fmf == 0:
            self.tview.clearSelection()
            self.tmodel.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot | QDir.Filter.System | QDir.Filter.Hidden)
            self.fmf = 1
            self.tview.scrollToTop()
        else:
            self.tview.clearSelection()
            self.tmodel.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot | QDir.Filter.System)
            self.fmf = 0
            self.tview.scrollToTop()

############## END TREEVIEW

###################

if __name__ == '__main__':
    
    # if is_wayland:
        # QApplication.instance().setAttribute(Qt.AA_EnableHighDpiScaling)
    
    app = QApplication(sys.argv)
    
    # app.setAttribute(Qt.AA_EnableHighDpiScaling)
    
    # set new style globally
    if theme_style:
        appStyle = QStyleFactory.create(theme_style)
        app.setStyle(appStyle)
    # set the icon style globally
    if icon_theme:
        QIcon.setThemeName(icon_theme)
    #
    if use_font_size:
        app.setStyleSheet("QWidget{font-size:"+f"{use_font_size}"+"px;}")
    #
    # if HIRED != "" and HIGREEN != "" and HIBLUE != "":
        # palette = QPalette()
        # # palette.setColor(QPalette.ColorRole.Base, QColor(245, 245, 245))
        # # palette.setColor(QPalette.ColorRole.Window, QColor(225, 225, 225))
        # palette.setColor(QPalette.ColorRole.Highlight, QColor(HIRED, HIGREEN, HIBLUE))
        # app.setPalette(palette)
    #
    window = MainWin()
    window.show()
    ret = app.exec()
    sys.exit(ret)

####################
