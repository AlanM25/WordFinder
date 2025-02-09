from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QSize, pyqtSignal
import cv2
import numpy as np

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

        self.viewer = MiEtiqueta()
        self.viewer2 = MiEtiqueta()

        self.buttonOpen = QtWidgets.QPushButton("Open Image")
        BUTTON_SIZE = QSize(200, 50)
        self.buttonOpen.setMinimumSize(BUTTON_SIZE)
        self.buttonOpen.clicked.connect(self.handleOpen)

        self.textInput = QtWidgets.QLineEdit()
        self.textInput.setMinimumSize(BUTTON_SIZE)

        self.enterButton = QtWidgets.QPushButton("Buscar")
        self.enterButton.setMinimumSize(BUTTON_SIZE)
        self.enterButton.clicked.connect(self.handleSearch)

        self.guardarImagen = QtWidgets.QPushButton("Guardar")
        self.guardarImagen.setMinimumSize(BUTTON_SIZE)
        self.guardarImagen.clicked.connect(self.handleSave)

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.buttonOpen, 0, 0, 1, 1)
        layout.addWidget(self.guardarImagen, 0, 3, 1, 1)
        layout.addWidget(self.textInput, 0, 1, 1, 1)
        layout.addWidget(self.enterButton, 0, 2, 1, 1)
        layout.addWidget(self.viewer, 1, 0, 1, 2)
        layout.addWidget(self.viewer2, 1, 2, 1, 2)

        self.image = None
        self.image_copy = None
        self._path = ""

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def handleOpen(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose File", "", "Images(*.jpg *.png)")
        if path:
            self._path = path
            self.updateImage()

    def updateImage(self):
        self.image = cv2.imread(self._path)
        self.image_copy = self.image.copy()
        self.showImage()

    def showImage(self):
        image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        height, width, _ = image_rgb.shape
        bytes_per_line = 3 * width
        q_image = QtGui.QImage(image_rgb.data, width, height, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
        pixmap = QtGui.QPixmap(q_image)
        self.viewer.setPixmap(pixmap)

    def handleSearch(self):
        palabra = self.textInput.text().strip().upper()
        if not palabra:
            QtWidgets.QMessageBox.warning(self, "Error", "Por favor ingresa una palabra.")
            return
        self.buscarPalabra(palabra)

    def buscarPalabra(self, palabra):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        resultado = self.image_copy.copy()
        letras_detectadas = []

        # Detectar letras y sus posiciones
        for c in contours:
            letter_coords = self.detectarLetra(c)
            if letter_coords:
                x, y, w, h = letter_coords
                letra_img = thresh[y:y+h, x:x+w]
                letra_img_resized = cv2.resize(letra_img, (20, 20))
                letra = self.reconocerLetra(letra_img_resized)
                if letra != '?':  # Ignorar letras desconocidas
                    letras_detectadas.append((letra, (x, y, w, h)))

        # Ordenar las letras detectadas por posición (de izquierda a derecha y de arriba a abajo)
        letras_detectadas.sort(key=lambda l: (l[1][1], l[1][0]))

        # Buscar la palabra en la secuencia de letras detectadas
        secuencia_letras = ''.join([letra for letra, _ in letras_detectadas])
        if palabra in secuencia_letras:
            QtWidgets.QMessageBox.information(self, "Resultado", f"Palabra '{palabra}' encontrada.")

            # Marcar las letras de la palabra encontrada
            start_index = secuencia_letras.find(palabra)
            for i in range(start_index, start_index + len(palabra)):
                _, (x, y, w, h) = letras_detectadas[i]
                cv2.rectangle(resultado, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Marcar en rojo
        else:
            QtWidgets.QMessageBox.warning(self, "Resultado", f"Palabra '{palabra}' no encontrada.")

        # Mostrar la imagen con las letras marcadas
        self.mostrarEnViewer2(resultado)

    def detectarLetra(self, c):
        M = cv2.moments(c)
        if M["m00"] > 0:
            x, y, w, h = cv2.boundingRect(c)
            area = cv2.contourArea(c)
            if area > 300:  # Filtrar los contornos más pequeños
                return (x, y, w, h)
        return None

    def reconocerLetra(self, letra_img):
        letras = {
            'C': 'abecedario/c.png',
            'O': 'abecedario/o.png',
        }

        for letra, img_path in letras.items():
            letra_ref = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if letra_ref is None:
                print(f"Error: No se pudo cargar la imagen para la letra '{letra}' en '{img_path}'")
                continue

            letra_ref_resized = cv2.resize(letra_ref, (20, 20))
            if np.array_equal(letra_img, letra_ref_resized):
                return letra

        return '?'  # Retorna '?' si no se reconoce la letra

    def mostrarEnViewer2(self, imagen):
        image_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        height, width, _ = image_rgb.shape
        bytes_per_line = 3 * width
        q_image = QtGui.QImage(imagen.data, width, height, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
        pixmap = QtGui.QPixmap(q_image)
        self.viewer2.setPixmap(pixmap)

    def handleSave(self):
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", "", "Images (*.jpg *.png)")
        if fileName:
            cv2.imwrite(fileName, self.image_copy)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setWindowTitle("Sopa de Letras")
    window.show()
    sys.exit(app.exec())
