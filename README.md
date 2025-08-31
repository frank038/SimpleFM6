# SimpleFM6
A file manager written in PyQt6. It's the Qt6 version with some enhancements of my SimpleFM (Qt5 toolkit).

Requirements:
- python3
- pyqt6
- python3-xdg
- python3-psutil

Recommended:
- any terminal that can execute commands in this way: TERMINAL -e COMMAND). To be setted in the config file.

Optionals:
- pkexec (alternatively internal bash scripts using su/sudo can be used)
- udisk2 and python3-dbus.mainloop.pyqt6 (for mass storage devices)
- pdftocairo, ffmpegthumbnailer (for thumbnailers)
- 7z (for custom actions)
- md5sum - sha256sum - sha1sum - tar - a terminal (for custom actions)
- archivemount (and 7z for mounting archive files - custom action)
- coreurils at least 8.31.

Features:
- thumbnailers
- trashcan
- mass storages
- bookmarks
- mounts some archive files through archivemount (more types can be added if supported by archivemount) 
- custom actions
- custom thumbnailers
- custom folder icon
- sticky selection (also) by pressing in the circle
- manages the permissions of multiple files at once (without checking the previous state of each of them, obviously)
- can be used under Xorg and under Wayland
- and more...

Thumbnail and device features are to be enabled in the config file.

The file simplefmdaemon6.py is a dbus implementation of the freedesktop.org's file manager interface (let user launch SimpleFM6 from a browser after a file has been downloaded). The full path of the file SimpleFM6.sh has to be setted in the file simplefmdaemon6.py at line 23. Alternatively, a simplest but limited method is to associate SimpleFM6 to folders as default program for that mimetype, and creating a desktop file launching SimpleFM.sh.

The 'Shift key' behaviour: to select a certain amount of contiguous items, select the first, press the shift key and select the last; to move the selected items by using the shift key, press the shift key and start dragging the last selected item.

Middle click on the button in the bar to open that folder in a new tab.

Pkexec: a different solution has been implemented to avoid it: if chosed in the config file, sudo - with user password - will be used; alternatively, also the su command - with the root password - can be used, just comment out the sudo section and uncomment the su section in the file pkexec.sh. A dialog for asking the password will appear.

Customizations throu the cfg.py file.

Some custom modules are disabled: just remove "-t" from its file name to be enabled and relaunch the program.

The default operation while dragging one or more items is copy; press shift for the move action.

![My image](https://github.com/frank038/SimpleFM6/blob/main/screenshot2.jpg)
