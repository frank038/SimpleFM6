#!/usr/bin/env python3
from PyQt6.QtGui import QImage
from PyQt6.QtCore import Qt

list_mime = ['image/x-portable-bitmap', 'image/gif', 'image/jpeg',
            'image/svg+xml', 'image/png', 'image/tiff', 'image/x-tga',
            'image/avif', 'image/webp']

def picture_to_img(fpath):
    
    try:
        img = QImage(fpath)
    except:
        return "Null"
    
    if not img.isNull():
        img_scaled = img.scaled(256, 256, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        # a QImage object is returned
        return img_scaled
    else:
        return "Null"
