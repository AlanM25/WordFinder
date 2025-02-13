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
        self.enterButton.clicked.connect(self.search_letter)

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

        self.image = None
        self.original_image = None
        self.contour_A = None

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def upload_image(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg *.bmp)")
        if file_path:
            self.image = cv2.imread(file_path)
            if self.image is None:
                QtWidgets.QMessageBox.warning(self, "Error", "No se pudo cargar la imagen.")
                return
            self.original_image = self.image.copy()
            self.display_image(self.image, self.viewer)
            self.extract_contour_A()  # Extraer contorno de referencia de la letra 'A'

    def display_image(self, img, viewer):
        # Convertir la imagen de OpenCV (BGR) a formato adecuado para PyQt6 (RGB)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        qimg = ImageQt.ImageQt(Image.fromarray(img_rgb))
        pixmap = QtGui.QPixmap.fromImage(qimg)
        viewer.setPixmap(pixmap)
        viewer.setScaledContents(True)

    def extract_contour_A(self):
        abecedario_path = "abecedario.png"  # Ruta del abecedario
        abc = cv2.imread(abecedario_path)
        if abc is None:
            QtWidgets.QMessageBox.warning(self, "Error", "No se pudo cargar la imagen del abecedario.")
            return
        gray_abc = cv2.cvtColor(abc, cv2.COLOR_BGR2GRAY)
        gray_abc = cv2.bilateralFilter(src=gray_abc, d=9, sigmaColor=75, sigmaSpace=75)
        abc_edged = cv2.Canny(gray_abc, 30, 200)
        abc_contours, _ = cv2.findContours(abc_edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        abc_contours = sorted(abc_contours, key=lambda c: cv2.boundingRect(c)[0])
        if len(abc_contours) > 0:
            self.contour_A = abc_contours[0]

    def search_letter(self):
        if self.image is None or self.contour_A is None:
            QtWidgets.QMessageBox.warning(self, "Error", "Primero debe cargar una imagen y extraer el contorno de referencia.")
            return

        match_threshold = 0.33
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(src=gray, d=9, sigmaColor=75, sigmaSpace=75)
        edged = cv2.Canny(gray, 30, 200)
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])

        for c in contours:
            if cv2.contourArea(c) < 50:
                continue
            similarity = cv2.matchShapes(self.contour_A, c, cv2.CONTOURS_MATCH_I1, 0.0)
            if similarity < match_threshold:
                hull = cv2.convexHull(c)
                (x_center, y_center), radius = cv2.minEnclosingCircle(hull)
                center = (int(x_center), int(y_center))
                radius = int(radius)
                cv2.circle(self.image, center, radius, (0, 255, 0), 2)

        self.display_image(self.image, self.viewer2)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setWindowTitle("Sopa de Letras")
    window.show()
    sys.exit(app.exec())
