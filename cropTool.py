import sys
import os
import bisect
import pickle
import argparse

from PyQt5.QtCore import Qt,QSize
from PyQt5 import QtWidgets, QtCore, QtGui

class MyWidget(QtWidgets.QWidget):
    def __init__(self,img_dir,width=480,height=360,scale=1.5):
        super().__init__()
        self.scale = scale
        self.setGeometry(30,30,width*scale,height*scale)

        # set import dir
        self.img_dir = img_dir
        self.img_list = [f for f in os.listdir(self.img_dir) if f.endswith(".png")]
        self.img_list.sort(key=lambda x: int(x[:-4]))
        self.img_ptr = 0

        # init bbox info
        self.bbox_info = [[0,0,0,0] for _ in range(len(self.img_list))]
        self.annotation_list = [] # craft annotate in this session

        # init cancelHead
        self.cancelHead = None

        # set filename label
        self.filename = QtWidgets.QLabel(self)
        self.filename.setFixedWidth(500)
        self.filename.move(60,500)
        self.filename.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        pe = QtGui.QPalette()
        pe.setColor(QtGui.QPalette.WindowText,Qt.white)
        self.filename.setPalette(pe)

        # set control label
        self.control = QtWidgets.QLabel(self)
        self.control.setFixedHeight(200)
        self.control.setFixedWidth(500)
        self.control.move(250,330)
        self.control.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        pe2 = QtGui.QPalette()
        pe2.setColor(QtGui.QPalette.WindowText,Qt.white)
        self.control.setPalette(pe2)
        self.control.setText('[L] : load bbox   [S] : save bbox   [E] : erase interpolates this session\n[→] : next image   [←] : previous image   [>] : next × 10   [<] : previous × 10\n[C] : cancle bbox(from-to)[Q] : quit')

        # init to 0.png
        self.LT = QtCore.QPoint()
        self.RB = QtCore.QPoint()
        self.setPicture()

        self.show()

    def setPicture(self):
        img_path = os.path.join(self.img_dir,self.img_list[self.img_ptr])

        # show image
        oImage = QtGui.QImage(img_path)
        sImage = oImage.scaled(QSize(self.geometry().width(),self.geometry().height()))
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(sImage))                        
        self.setPalette(palette)

        # refresh filename
        self.filename.setText(img_path)

        # refresh bbox
        x1,y1,x2,y2 = self.bbox_info[self.img_ptr]
        self.LT.setX(x1)
        self.LT.setY(y1)
        self.RB.setX(x2)
        self.RB.setY(y2)

        self.update()

    def interpolates(self):
        aid = self.annotation_list.index(self.img_ptr)

        # left interpolated
        if aid > 0:
            box_start = self.annotation_list[aid-1]
            box_end = self.img_ptr
            x1_start,y1_start,x2_start,y2_start = self.bbox_info[box_start]
            x1_end,y1_end,x2_end,y2_end = self.bbox_info[box_end]
            for i in range(box_start+1,box_end):
                ratio = (i - box_start) / (box_end - box_start)
                x1_i = x1_start + (x1_end - x1_start) * ratio
                y1_i = y1_start + (y1_end - y1_start) * ratio
                x2_i = x2_start + (x2_end - x2_start) * ratio
                y2_i = y2_start + (y2_end - y2_start) * ratio
                self.bbox_info[i] = [x1_i,y1_i,x2_i,y2_i]

        # right interpolated
        if aid < len(self.annotation_list)-1:
            box_start = self.img_ptr
            box_end = self.annotation_list[aid+1]
            x1_start,y1_start,x2_start,y2_start = self.bbox_info[box_start]
            x1_end,y1_end,x2_end,y2_end = self.bbox_info[box_end]
            for i in range(box_start+1,box_end):
                ratio = (i - box_start) / (box_end - box_start)
                x1_i = x1_start + (x1_end - x1_start) * ratio
                y1_i = y1_start + (y1_end - y1_start) * ratio
                x2_i = x2_start + (x2_end - x2_start) * ratio
                y2_i = y2_start + (y2_end - y2_start) * ratio
                self.bbox_info[i] = [x1_i,y1_i,x2_i,y2_i]

    def cancelBBoxInterval(self):
        if self.cancelHead is None:
            self.cancelHead = self.img_ptr
            print('Cancel from',self.cancelHead)
        else:
            head,tail = min(self.cancelHead,self.img_ptr), max(self.cancelHead,self.img_ptr)
            for i in range(head,tail+1):
                self.bbox_info[i] = [0,0,0,0]
            self.cancelHead = None
            print('Cancel from',head,'to',tail)

    def saveCropFile(self):
        crop_filename = self.img_dir + '.crop'
        
        f = open(crop_filename,'w')

        for i,bbox in enumerate(self.bbox_info):
            bbox_unscaled = list(map(lambda z: z/self.scale, bbox))
            log = '{}\t{:3.2f}\t{:3.2f}\t{:3.2f}\t{:3.2f}\n'.format(i,*bbox_unscaled)
            f.write(log)

        f.close()

        print('Save!')

    def loadCropFile(self):
        crop_filename = self.img_dir + '.crop'
        if os.path.exists(crop_filename) is False:
            print(crop_filename,'is not exist')
        else:
            f = open(crop_filename,'r')
            contents = f.readlines()
            f.close()
            
            start_img = 0
            for content in contents:
                content = content.split()
                i = int(content[0])
                bbox = list(map(lambda z: float(z)*self.scale, content[1:]))
                if sum(bbox) > 0:
                    start_img = i
                self.bbox_info[i] = bbox
            self.img_ptr = start_img
            self.setPicture()
            print('Load!')

        
    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        if self.img_ptr in self.annotation_list:
            box_color = QtGui.QColor(50, 100, 255, 80)
        else:
            box_color = QtGui.QColor(255, 255, 10, 50)
        br = QtGui.QBrush(box_color)  
        qp.setBrush(br)   
        qp.drawRect(QtCore.QRect(self.LT, self.RB))     

    def mousePressEvent(self, event):
        if self.img_ptr not in self.annotation_list:
            bisect.insort(self.annotation_list,self.img_ptr)
        self.LT = event.pos()

    def mouseMoveEvent(self, event):
        self.RB = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        bbox = [self.LT.x(),self.LT.y(), self.RB.x(), self.RB.y()]
        if bbox[0] > bbox[2]:
            bbox[0],bbox[2] = bbox[2],bbox[0]
        if bbox[1] > bbox[3]:
            bbox[1],bbox[3] = bbox[3],bbox[1]
        self.bbox_info[self.img_ptr] =  bbox
        self.interpolates()

    def keyPressEvent(self, e):

        if e.key() == Qt.Key_Right:
            self.img_ptr = (self.img_ptr + 1) % len(self.img_list)
            self.setPicture()
        elif e.key() == Qt.Key_Period:
            self.img_ptr = (self.img_ptr + 10) % len(self.img_list)
            self.setPicture()
        elif e.key() == Qt.Key_Left:
            self.img_ptr = (self.img_ptr - 1) % len(self.img_list)
            self.setPicture()
        elif e.key() == Qt.Key_Comma:
            self.img_ptr = (self.img_ptr - 10) % len(self.img_list)
            self.setPicture()
        elif e.key() == Qt.Key_Space:
            for i,bbox in enumerate(self.bbox_info):
                if sum(bbox) > 0:
                    print('{}.png = ({} {} {} {})'.format(i,*bbox))
        elif e.key() == Qt.Key_C:
            self.cancelBBoxInterval()
        elif e.key() == Qt.Key_S:
            self.saveCropFile()
        elif e.key() == Qt.Key_L:
            self.loadCropFile()
        elif e.key() == Qt.Key_E:
            print('clear annotation list')
            self.annotation_list.clear()
        elif e.key() == Qt.Key_Q:
            self.close()

    


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-d')
    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)
    window = MyWidget(img_dir=args.d)
    window.show()
    app.aboutToQuit.connect(app.deleteLater)
    sys.exit(app.exec_())