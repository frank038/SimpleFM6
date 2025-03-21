#!/usr/bin/env python3
from PyQt6.QtGui import QImage
from PyQt6.QtCore import Qt

import subprocess

# pdftocairo required

list_mime = ['application/pdf']

def picture_to_img(fpath):
    
    try:
        data = subprocess.check_output(["pdftocairo", "-png", "-singlefile", "-scale-to", "256", "-q", fpath, "-"])
        img = QImage.fromData(data)
        
    except:
        return "Null"
    
    if not img.isNull():
        
        img_scaled = img #.scaled(256, 256, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
        
        return img_scaled
    else:
        return "Null"
