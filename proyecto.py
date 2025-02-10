import cv2
import numpy as np
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QSize, pyqtSignal
from PIL import Image, ImageQt

class MiEtiqueta(QtWidgets.QLabel):
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet("border: 1px solid black;")

    def mousePressEvent(self, e):
        self.clicked.emit()

class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(10, 10, 900, 600)
        self.center()

        # Crear componentes
        self.viewer = MiEtiqueta()  # Vista original
        self.viewer2 = MiEtiqueta()  # Vista con la palabra marcada

        self.buttonOpen = QtWidgets.QPushButton("Abrir Imagen")
        BUTTON_SIZE = QSize(200, 50)
        self.buttonOpen.setMinimumSize(BUTTON_SIZE)
        self.buttonOpen.clicked.connect(self.upload_image)

        self.textInput = QtWidgets.QLineEdit()
        self.textInput.setMinimumSize(BUTTON_SIZE)

        self.enterButton = QtWidgets.QPushButton("Buscar")
        self.enterButton.setMinimumSize(BUTTON_SIZE)
        self.enterButton.clicked.connect(self.search_word)

        self.guardarImagen = QtWidgets.QPushButton("Guardar")
        self.guardarImagen.setMinimumSize(BUTTON_SIZE)

        # Crear Layout
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.buttonOpen, 0, 0, 1, 1)
        layout.addWidget(self.guardarImagen, 0, 3, 1, 1)
        layout.addWidget(self.textInput, 0, 1, 1, 1)
        layout.addWidget(self.enterButton, 0, 2, 1, 1)
        layout.addWidget(self.viewer, 1, 0, 1, 2)
        layout.addWidget(self.viewer2, 1, 2, 1, 2)

        # Inicializar imágenes
        self.image = None
        self.original_image = None

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def upload_image(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg *.bmp)")
        if file_path:
            self.image = cv2.imread(file_path)
            self.original_image = self.image.copy()
            self.display_image(self.image, self.viewer)

    def display_image(self, img, viewer):
        qimg = ImageQt.ImageQt(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
        pixmap = QtGui.QPixmap.fromImage(qimg)
        viewer.setPixmap(pixmap)
        viewer.setScaledContents(True)

    def search_word(self):
        word = self.textInput.text()
        if word and self.image is not None:
            # Restaurar la imagen original para eliminar cualquier marcado anterior
            self.image = self.original_image.copy()

            # Convertir la imagen a escala de grises
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            # Binarizar la imagen (umbral)
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
            
            # Buscar la palabra en la sopa de letras
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self.mark_word_in_image(word, contours)

    def mark_word_in_image(self, word, contours):
        """ Resalta las letras de la palabra en la imagen """
        color = (0, 255, 0)  # Verde
        for contour in contours:
            # Usamos bounding box para detectar las letras
            x, y, w, h = cv2.boundingRect(contour)
            roi = self.original_image[y:y+h, x:x+w]
            cv2.rectangle(self.image, (x, y), (x+w, y+h), color, 2)
        self.display_image(self.image, self.viewer2)  # Mostrar en viewer2

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setWindowTitle("Sopa de Letras")
    window.show()
    sys.exit(app.exec())
