__author__ = 'abaker'

"""
    @project: Pholidota
    @author: Austin Baker
    @created: 6/07/2015
    @license: http://opensource.org/licenses/mit-license.php

    The MIT License (MIT)

    Copyright (c) 2015 Austin Baker

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.

    USAGE:
"""

'''
============================================================
---   IMPORT MODULES
============================================================
'''
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


'''
============================================================
---   GRAPHICS CLASSES
============================================================
'''
class NodeLine(QGraphicsPathItem):
    def __init__(self, pointA, pointB):
        super(NodeLine, self).__init__()
        self._pointA = pointA
        self._pointB = pointB
        self._source = None
        self._target = None
        self.setZValue(-1)
        self.setBrush(QBrush())
        self.pen = QPen()
        self.pen.setStyle(Qt.SolidLine)
        self.pen.setWidth(2)
        self.pen.setColor(QColor(255,20,20,255))
        self.setPen(self.pen)

    def mousePressEvent(self, event):
        self.pointB = event.pos()

    def mouseMoveEvent(self, event):
        self.pointB = event.pos()

    def updatePath(self):
        path = QPainterPath()
        path.moveTo(self.pointA)
        dx = self.pointB.x() - self.pointA.x()
        dy = self.pointB.y() - self.pointA.y()
        ctrl1 = QPointF(self.pointA.x() + dx * 0.25, self.pointA.y() + dy * 0.1)
        ctrl2 = QPointF(self.pointA.x() + dx * 0.75, self.pointA.y() + dy * 0.9)
        path.cubicTo(ctrl1, ctrl2, self.pointB)
        self.setPath(path)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.drawPath(self.path())

    @property
    def pointA(self):
        return self._pointA

    @pointA.setter
    def pointA(self, point):
        self._pointA = point
        self.updatePath()

    @property
    def pointB(self):
        return self._pointB

    @pointB.setter
    def pointB(self, point):
        self._pointB = point
        self.updatePath()

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, widget):
        self._source = widget

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, widget):
        self._target = widget


class NodeSocket(QGraphicsItem):
    def __init__(self, rect, parent, socketType):
        super(NodeSocket, self).__init__(parent)
        self.rect = rect
        self.type = socketType

        # Brush.
        self.brush = QBrush()
        self.brush.setStyle(Qt.SolidPattern)
        self.brush.setColor(QColor(180,20,90,255))

        # Pen.
        self.pen = QPen()
        self.pen.setStyle(Qt.SolidLine)
        self.pen.setWidth(1)
        self.pen.setColor(QColor(20,20,20,255))

        # Lines.
        self.outLines = []
        self.inLines = []

    def shape(self):
        path = QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def boundingRect(self):
        return QRectF(self.rect)

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawEllipse(self.rect)

    def mousePressEvent(self, event):
        if self.type == 'out':
            rect = self.boundingRect()
            pointA = QPointF(rect.x() + rect.width()/2, rect.y() + rect.height()/2)
            pointA = self.mapToScene(pointA)
            pointB = self.mapToScene(event.pos())
            self.newLine = NodeLine(pointA, pointB)
            self.outLines.append(self.newLine)
            self.scene().addItem(self.newLine)
        elif self.type == 'in':
            rect = self.boundingRect()
            pointA = self.mapToScene(event.pos())
            pointB = QPointF(rect.x() + rect.width()/2, rect.y() + rect.height()/2)
            pointB = self.mapToScene(pointB)
            self.newLine = NodeLine(pointA, pointB)
            self.inLines.append(self.newLine)
            self.scene().addItem(self.newLine)
        else:
            super(NodeSocket, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.type == 'out':
            pointB = self.mapToScene(event.pos())
            self.newLine.pointB = pointB
        elif self.type == 'in':
            pointA = self.mapToScene(event.pos())
            self.newLine.pointA = pointA
        else:
            super(NodeSocket, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        item = self.scene().itemAt(event.scenePos().toPoint(), QTransform())
        if self.type == 'out' and item.type == 'in':
            self.newLine.source = self
            self.newLine.target = item
            item.parentItem().Input.inLines.append(self.newLine)
            self.newLine.pointB = item.getCenter()
        elif self.type == 'in' and item.type == 'out':
            self.newLine.source = item
            self.newLine.target = self
            item.parentItem().Output.outLines.append(self.newLine)
            self.newLine.pointA = item.getCenter()
        else:
            super(NodeSocket, self).mouseReleaseEvent(event)

    def getCenter(self):
        rect = self.boundingRect()
        center = QPointF(rect.x() + rect.width()/2, rect.y() + rect.height()/2)
        center = self.mapToScene(center)
        return center


class NodeItem(QGraphicsItem):
    def __init__(self):
        super(NodeItem, self).__init__()
        self.name = None
        self.rect = QRect(0,0,100,60)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.initUi()

        # Brush.
        self.brush = QBrush()
        self.brush.setStyle(Qt.SolidPattern)
        self.brush.setColor(QColor(80,0,90,255))

        # Pen.
        self.pen = QPen()
        self.pen.setStyle(Qt.SolidLine)
        self.pen.setWidth(1)
        self.pen.setColor(QColor(20,20,20,255))

        self.selPen = QPen()
        self.selPen.setStyle(Qt.SolidLine)
        self.selPen.setWidth(1)
        self.selPen.setColor(QColor(0,255,255,255))

    def initUi(self):
        self.Input = NodeSocket(QRect(-10,20,20,20), self, 'in')
        self.Output = NodeSocket(QRect(90,20,20,20), self, 'out')

    def shape(self):
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def boundingRect(self):
        return QRectF(self.rect)

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush)
        if self.isSelected():
            painter.setPen(self.selPen)
        else:
            painter.setPen(self.pen)
        painter.drawRect(self.rect)

    def mouseMoveEvent(self, event):
        super(NodeItem, self).mouseMoveEvent(event)
        for line in self.Output.outLines:
            line.pointA = line.source.getCenter()
            line.pointB = line.target.getCenter()
        for line in self.Input.inLines:
            line.pointA = line.source.getCenter()
            line.pointB = line.target.getCenter()

    def contextMenuEvent(self, event):
        menu = QMenu()
        make = menu.addAction('make')
        makeFromHere = menu.addAction('make from here')
        debugConnections = menu.addAction('debug connections')
        selectedAction = menu.exec_(event.screenPos())

        if selectedAction == debugConnections:
            print('Input')
            for idx,line in enumerate(self.Input.inLines):
                print('  Line {0}'.format(idx))
                print('    pointA: {0}'.format(line.pointA))
                print('    pointB: {0}'.format(line.pointB))
            print('Output')
            for idx,line in enumerate(self.Output.outLines):
                print('  Line {0}'.format(idx))
                print('    pointA: {0}'.format(line.pointA))
                print('    pointB: {0}'.format(line.pointB))

class NodeView(QGraphicsView):
    """
    QGraphicsView for displaying the nodes.

    :param scene: QGraphicsScene.
    :param parent: QWidget.
    """
    def __init__(self, scene, parent):
        super(NodeView, self).__init__(parent)
        self.setObjectName('View')
        self.setScene(scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.drag = False

    def wheelEvent(self, event):
        """
        Zooms the QGraphicsView in/out.

        :param event: QGraphicsSceneWheelEvent.
        """
        inFactor = 1.25
        outFactor = 1 / inFactor
        oldPos = self.mapToScene(event.pos())
        #print(event.angleDelta().y())
        #if event.angleDelta().y() > 0: # &gt; 0:
            #zoomFactor = inFactor
        #else:
            #zoomFactor = outFactor
        #self.scale(zoomFactor, zoomFactor)
        newPos = self.mapToScene(event.pos())
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton and event.modifiers() == Qt.AltModifier:
            self.setDragMode(QGraphicsView.NoDrag)
            self.drag = True
            self.prevPos = event.pos()
            self.setCursor(Qt.SizeAllCursor)
        elif event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.RubberBandDrag)
        super(NodeView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag:
            delta = (self.mapToScene(event.pos()) - self.mapToScene(self.prevPos)) * -1.0
            center = QPoint(self.viewport().width()/2 + delta.x(), self.viewport().height()/2 + delta.y())
            newCenter = self.mapToScene(center)
            self.centerOn(newCenter)
            self.prevPos = event.pos()
            return
        super(NodeView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drag:
            self.drag = False
            self.setCursor(Qt.ArrowCursor)
        super(NodeView, self).mouseReleaseEvent(event)


'''
============================================================
---   UI CLASSES
============================================================
'''
class SideBar(QFrame):
    def __init__(self, parent):
        super(SideBar, self).__init__(parent)
        self.setObjectName('SideBar')
        self.initUi()

    def initUi(self):
        # Frame.
        self.setFixedWidth(200)

        # Central Layout.
        self.CentralLayout = QVBoxLayout(self)

        # Buttons.
        self.AddBoxButton = QPushButton('Add Box')
        self.CentralLayout.addWidget(self.AddBoxButton)

        # Connections.
        self.initConnections()

    def initConnections(self):
        self.AddBoxButton.clicked.connect(self.clickedAddBoxButton)

    def clickedAddBoxButton(self):
        window = self.window()
        box = NodeItem()
        window.Scene.addItem(box)
        box.setPos(window.Scene.width()/2, window.Scene.height()/2)


class NodeWindow(QMainWindow):
    def __init__(self):
        super(NodeWindow, self).__init__()
        self.setWindowTitle('Node Window')
        self.initUi()

    def initUi(self):
        # Window.
        self.setMinimumSize(400,200)

        # Central Widget.
        self.CentralWidget = QFrame()
        self.CentralWidget.setObjectName('CentralWidget')
        self.setCentralWidget(self.CentralWidget)

        # Central Layout.
        self.CentralLayout = QHBoxLayout(self.CentralWidget)

        # GraphicsView.
        self.Scene = QGraphicsScene()
        self.Scene.setObjectName('Scene')
        self.Scene.setSceneRect(0,0,32000,32000)
        self.View = NodeView(self.Scene, self)
        self.CentralLayout.addWidget(self.View)

        # Side Bar.
        self.SideBar = SideBar(self)
        self.CentralLayout.addWidget(self.SideBar)

        # Color.
        self.initColor()

    def initColor(self):
        windowCss = '''
        QFrame {
            background-color: rgb(90,90,90);
            border: 1px solid rgb(90,70,30);
        }
        QFrame#SideBar {
            background-color: rgb(50,50,50);
            border: 1px solid rgb(255,255,255);
        }'''
        self.setStyleSheet(windowCss)


'''
============================================================
---   SHOW WINDOW
============================================================
'''
#class Window(QMainWindow):
    #def __init__(self):
        #QMainWindow.__init__(self)
        #self.resize(640,480)
        #self.add=Add(self)
        #self.entry1=Entry(self)
        #self.entry2=Entry(self)

if __name__=="__main__":
    import sys
    app=QApplication(sys.argv)
    win=NodeWindow()
    win.show()
    sys.exit(app.exec_())

#def mayaMainWindow():
    #"""
    #Return the Maya main window widget as a Python object

    #:return: Maya Main Window.
    #"""
    #mainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
    #return wrapInstance(long(mainWindowPtr), QWidget)

#if __name__ == '__main__':
    #mayaWindow = mayaMainWindow()
    #nodeWindow = NodeWindow(mayaWindow)
    #nodeWindow.show()
    

## DEPRECATED
'''
import sys, time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

class Entry(QLineEdit):
    def __init__(self,parent=None):
        QLineEdit.__init__(self,parent)
        self.resize(75,50)
    def paintEvent(self,event):
        painter=QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawEllipse(54,25,20,20)
        painter.drawRect(QRect(0,0,self.width()-22,self.height()-1))
        font=QFont('Arial',13)
        painter.setFont(font)
        painter.drawText(QPoint(22,22),self.text())
        painter.end()
        #movements from https://stackoverflow.com/questions/12219727/dragging-moving-a-qpushbutton-in-pyqt
    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()         
        super(Entry, self).mousePressEvent(event)
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)
            self.__mouseMovePos = globalPos
        super(Entry, self).mouseMoveEvent(event)
    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos 
            if moved.manhattanLength() > 3:
                event.ignore()
                return
        super(Entry, self).mouseReleaseEvent(event)
class Add(QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        self.resize(75,50)
    def paintEvent(self, event):
        #use QPainter for a custom look
        painter=QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawEllipse(0,25,20,20)
        painter.drawEllipse(0,0,20,20)
        painter.drawRect(QRect(20,0,34,49))
        painter.drawEllipse(53,24,20,20)
        font=QFont('Arial',13)
        painter.setFont(font)
        painter.drawText(QPoint(22,22),"Add")
        painter.end()
    #movements from https://stackoverflow.com/questions/12219727/dragging-moving-a-qpushbutton-in-pyqt  
    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()
        super(Add, self).mousePressEvent(event)
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)
            self.__mouseMovePos = globalPos
        super(Add, self).mouseMoveEvent(event)
    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos 
            if moved.manhattanLength() > 3:
                event.ignore()
                return
        super(Add, self).mouseReleaseEvent(event)
class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.resize(640,480)
        self.add=Add(self)
        self.entry1=Entry(self)
        self.entry2=Entry(self)
if __name__=="__main__":
    app=QApplication(sys.argv)
    win=Window()
    win.show()
    sys.exit(app.exec_())
'''
