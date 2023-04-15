# -*- coding: utf-8 -*-
"""
@author: raph988

A GUI to load images and run the alignement. It also can be run directly in differentiel.py script.
"""


import os
import cv2
import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget, QDialog, QMessageBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt

from PySide2 import QtGui


from differentiel import RealignImages


class DropableButton(QPushButton):
  
    def __init__(self, title, parent):
        super(DropableButton, self).__init__(title, parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('text/plain'):
            e.accept()
        else:
            e.ignore() 

    def dropEvent(self, e):
        self.setText(e.mimeData().text())



class Template(QMainWindow):
    
    def __init__(self, parent=None, ui_path="", w_title= "My window"):
        super(Template, self).__init__(parent)
        self.setWindowTitle(w_title)
        
        ui_path = os.path.join(ui_path)
        if not os.path.exists(ui_path): 
            s = "Unable to load UI from "+ui_path
            raise Exception(s)
        
#        self.ui = QtUiTools.QUiLoader().load(ui_path)
        self.ui = QUiLoader().load(ui_path)
        if self.ui is None: return
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.ui)
        
        if isinstance(self, QDialog):
            self.setLayout(self.layout)
        elif isinstance(self, QMainWindow):
            main_w = QWidget()
            main_w.setLayout(self.layout)
            self.setCentralWidget(main_w)
        
        self.path_1 = None
        self.path_2 = None
        self.resulting_images = None
        self.c = self.palette().color(QtGui.QPalette.Background)
        self.default_bg_color = "" + str(self.c.red()) +" "+ str(self.c.green()) +" "+ str(self.c.blue())
        
        self.setupIHM()
        
        
    def setupIHM(self):
        self.ui.button_1.clicked.connect(self.loadImage)
        self.ui.button_2.clicked.connect(self.loadImage)
        self.setAcceptDrops(True)
        self.droppable_zone_1 = [self.ui.groupBox_1, self.ui.line_1, self.ui.button_1]
        self.droppable_zone_2 = [self.ui.groupBox_2,self.ui.line_2, self.ui.button_2]
        self.droppable_items = self.droppable_zone_1 + self.droppable_zone_2
        self.dragLeaveEvent(None)
        self.ui.button_cancel.clicked.connect(self.close)
        self.ui.line_1.textChanged[str].connect(self.check_paths)
        self.ui.line_2.textChanged[str].connect(self.check_paths)
        self.ui.button_run.clicked.connect(self.runAlignement)
        self.ui.button_run.setEnabled(False)
        self.ui.button_save.setEnabled(False)
        self.ui.button_save.clicked.connect(self.saveResult)
        
    def loadImage(self):
        sender = self.sender()
        path = self.loadFile()
        if path is None: return 
        
        if sender == self.ui.button_1:
            self.ui.line_1.setText(path)
            self.path_1 = path
        elif sender == self.ui.button_2:
            self.path_2 = path
            self.ui.line_2.setText(path)
    
    def loadFile(self):
        res = QFileDialog.getOpenFileName(self, caption="Open Image", dir="", filter="Image Files (*.png *.jpg *.bmp)")
        if res is None: return res
        else: return res[0]
    def loadDirectory(self, title, current_dir=""):
        res = QFileDialog.getExistingDirectory(self, caption=title, dir=current_dir, options=QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if res is None: return res
        else: return res[0]
    
    def check_paths(self, text):
        if os.path.exists(self.ui.line_1.text()) and self.path_2 is not None and os.path.exists(self.ui.line_2.text()):
            self.ui.button_run.setEnabled(True)
        else: self.ui.button_run.setEnabled(False)
    
    
    def runAlignement(self):
        
        cut_bottom = self.ui.spinBox.value()
        if cut_bottom == 0: cut_bottom = None
        try:
            self.resulting_images = RealignImages(self.path_1, self.path_2, cut_bottom)
        except Exception as e:
            QMessageBox.warning("Something bad occured...", str(e))
            return 
        
        self.ui.button_save.setEnabled(True)
        if self.ui.cb_save.isChecked():
            self.saveResult()
        else: 
            cv2.imshow("Image 1", self.resulting_images[0])
            cv2.imshow("Image 2", self.resulting_images[1])
            cv2.waitKey(0), cv2.destroyAllWindows()
    
    
    def saveResult(self):
        slash = ""
        if "\\" in self.path_1: slash = "\\"
        elif "/" in self.path_1: slash = "/"
        
        dir_1 = self.path_1.split(slash)[-2]
        file_1_ext = self.path_1.split(".")[-1]
        file_2_ext = self.path_2.split(".")[-1]
        
        path = self.loadDirectory("Save in the directory...", current_dir=dir_1)
        if path is None:  return
        
        cv2.imwrite(self.path_1.replace(file_1_ext,"_aligned."+file_1_ext), self.resulting_images[0])
        cv2.imwrite(self.path_2.replace(file_2_ext,"_aligned."+file_2_ext), self.resulting_images[1])
        
    
    
    def colorize_zone(self, w_zone, default=True):
        if default is False:
            color = Qt.red
        else:
            color = Qt.gray
            
        for w in w_zone:
            p = w.palette()
            p.setColor(w.backgroundRole(), color)
            w.setPalette(p)
    
    
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            w_target = self.childAt(e.pos())
            if w_target in self.droppable_zone_1:
                e.accept()
                self.ui.setStyleSheet("QGroupBox#groupBox_2 { background-color: "+self.default_bg_color+";}")
                self.ui.setStyleSheet("QGroupBox#groupBox_1 { background-color: lightgray;}")
            if w_target in self.droppable_zone_2:
                e.accept()
                self.ui.setStyleSheet("QGroupBox#groupBox_1 { background-color: "+self.default_bg_color+";}")
                self.ui.setStyleSheet("QGroupBox#groupBox_2 { background-color: lightgray;}")
    
    
    def dragLeaveEvent(self, e):
        ss = "QGroupBox#groupBox_1 { background-color: "+self.default_bg_color+";} \
            QGroupBox#groupBox_2 { background-color: "+self.default_bg_color+";}"
        self.ui.setStyleSheet(ss)
        
        
    def dropEvent(self, e):
        w_target = self.childAt(e.pos())
#        print("dropped on", w_target.objectName())
        
        text = None
        if e.mimeData().hasText():
            e.accept()
            text = e.mimeData().text()
        elif e.mimeData().hasUrls():
            e.accept()
            e.setDropAction(Qt.CopyAction)
            url = e.mimeData().urls()[0]
            text = str(url.toLocalFile())
        
        if text is None: return
        
        if w_target in self.droppable_zone_1:
            self.path_1 = text
            self.ui.line_1.setText(text)
        elif w_target in self.droppable_zone_2:
            self.path_2 = text
            self.ui.line_2.setText(text)
        self.dragLeaveEvent(e)
        
        
        
def UseIHM():
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    ui_path="./realign.ui"
    if not os.path.exists(ui_path):
        ui_path = "realign.ui"
        
#    window = Template(ui_path="C:/Users/raphael abele/Documents/Qt/Realign_IHM/realign.ui", w_title= "Realignement tool")
    window = Template(ui_path=ui_path, w_title= "Realignement tool")
    window.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
    
    
    
if __name__ == '__main__':
    UseIHM()
    
    
    
    
    