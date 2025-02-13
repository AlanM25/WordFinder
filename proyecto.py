from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QSize, pyqtSignal
import cv2


class MiEtiqueta(QtWidgets.QLabel):
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.Lista = []
        self.setStyleSheet("border: 1px solid black;")

    def mousePressEvent(self, e):
        self.x = e.position().x()
        self.y = e.position().y()
        self.Lista.append((self.x, self.y))
        print(self.Lista)
        self.clicked.emit()


class Window(QtWidgets.QWidget):
    def Metodo(self):
        for i in self.viewer.Lista:
            ii = tuple(int(x) for x in i)
            self.OpenCV_image = cv2.circle(self.OpenCV_image, ii, 10, (255, 255, 0), 4)
        self.ActualizarPixMap()

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def __init__(self):
        super().__init__()
        self.setGeometry(10, 10, 900, 600)
        self.center()

        self.viewer = MiEtiqueta()
        self.viewer2 = MiEtiqueta()
        self.viewer.clicked.connect(self.Metodo)

        self.buttonOpen = QtWidgets.QPushButton("Open Image")
        BUTTON_SIZE = QSize(200, 50)
        self.buttonOpen.setMinimumSize(BUTTON_SIZE)
        self.buttonOpen.clicked.connect(self.handleOpen)

        self.textInput = QtWidgets.QLineEdit()
        self.textInput.setMinimumSize(BUTTON_SIZE)

        self.enterButton = QtWidgets.QPushButton("Buscar")
        self.enterButton.setMinimumSize(BUTTON_SIZE)
        self.enterButton.clicked.connect(self.handleTextInput)

        self.guardarImagen = QtWidgets.QPushButton("Guardar")
        self.guardarImagen.setMinimumSize(BUTTON_SIZE)
        self.guardarImagen.clicked.connect(self.handleSaveFile)

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.buttonOpen, 0, 0, 1, 1)
        layout.addWidget(self.guardarImagen, 0, 3, 1, 1)
        layout.addWidget(self.textInput, 0, 1, 1, 1)
        layout.addWidget(self.enterButton, 0, 2, 1, 1)
        layout.addWidget(self.viewer, 1, 0, 1, 2)
        layout.addWidget(self.viewer2, 1, 2, 1, 2)

    def handleTextInput(self):
        text = self.textInput.text()
        print(f"Texto ingresado: {text}")

    def handleSaveFile(self):
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", "", "Images(*.jpg *.png)")
        if fileName:
            cv2.imwrite(fileName, self.OpenCV_image)

    def handleOpen(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, "Choose File", "./", "Images(*.jpg *.png)")[0]
        if path:
            self._path = path
            self.ActualizarImagen()

    def ActualizarPixMap(self):
        QImageTemp = QtGui.QImage(cv2.cvtColor(self.OpenCV_image, cv2.COLOR_BGR2RGB),
                                  self.OpenCV_image.shape[1],
                                  self.OpenCV_image.shape[0],
                                  self.OpenCV_image.shape[1] * 3,
                                  QtGui.QImage.Format.Format_RGB888)
        pixmap = QtGui.QPixmap(QImageTemp)
        self.viewer.setPixmap(pixmap)

    def ActualizarImagen(self):
        self.OpenCV_image = cv2.imread(self._path)
        tamano = (self.viewer.size().width(), self.viewer.size().height())
        self.OpenCV_image = cv2.resize(self.OpenCV_image, tamano, interpolation=cv2.INTER_LINEAR)
        self.ActualizarPixMap()


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setWindowTitle("Image Editor")
    window.show()
    sys.exit(app.exec())
