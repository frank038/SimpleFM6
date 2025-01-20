#!/usr/bin/env python3
from PyQt6.QtGui import QImage
from PyQt6.QtCore import Qt

import subprocess

# ffmpegthumbnailer required

list_mime = ['video/mp4', 'video/x-msvideo', 'video/x-flv', 'video/x-ms-wmv', 
            'video/quicktime', 'video/x-matroska', 'video/3gpp', 'video/mpeg', 
            'video/ogg', 'video/webm']

def picture_to_img(fpath):
    try:
        data = subprocess.check_output(["ffmpegthumbnailer", "-i", fpath, "-s", "256", "-f", "-o", "/dev/stdout"])
        img = QImage.fromData(data)
    except:
        return "Null"
    
    if not img.isNull():
        img_scaled = img #.scaled(256, 256, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
        return img_scaled
    else:
        return "Null"
