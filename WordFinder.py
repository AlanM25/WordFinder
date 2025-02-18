"""
Las sopas de letras de este programa son ejemplos
proporcionados por:

https://www.superteacherworksheets.com/generator-word-search.html

Con la configuración de nivel Basico 12*8
y la fuente de letras en Mayusculas

"""


import cv2
import numpy as np
from letter import Letter
import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QSize, pyqtSignal

def correct_perspective(img):
    """ Corrige perspectiva sin girar la imagen """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 200)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return img  # Si no hay contornos, devuelve la imagen original
    
    max_contour = max(contours, key=cv2.contourArea)
    epsilon = 0.02 * cv2.arcLength(max_contour, True)
    approx = cv2.approxPolyDP(max_contour, epsilon, True)
    
    if len(approx) == 4:  # Solo si detecta un rectángulo
        approx = sorted(approx, key=lambda x: x[0][1])  # Ordena por la coordenada Y

        if approx[0][0][0] > approx[1][0][0]:  
            approx[0], approx[1] = approx[1], approx[0]  # Asegura que el punto superior izquierdo sea correcto
        
        if approx[2][0][0] > approx[3][0][0]:  
            approx[2], approx[3] = approx[3], approx[2]  # Asegura que el punto inferior izquierdo sea correcto

        # Ajustar puntos para evitar volteo/espejo
        pts_src = np.float32([approx[0][0], approx[1][0], approx[2][0], approx[3][0]])
        pts_dst = np.float32([[0, 0], [800, 0], [0, 800], [800, 800]])
        
        M = cv2.getPerspectiveTransform(pts_src, pts_dst)
        img = cv2.warpPerspective(img, M, (800, 800))
    
    return img

def process_img(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Prueba adaptiveThreshold en lugar de Canny
    img_thresh = cv2.adaptiveThreshold(
        img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 9
    )

    # Aplicar dilatación con kernel más pequeño
    kernel = np.ones((1, 1), np.uint8)
    img_dilate = cv2.dilate(img_thresh, kernel, iterations=1)
    
    return img_dilate

def get_centeroid(cnt):
    M = cv2.moments(cnt)
    if M["m00"] == 0:
        return None
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    return cx, cy

def get_centers(img):
    global figures
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    max_contour = max(contours, key=cv2.contourArea) if contours else None
    
    for i, cnt in enumerate(contours):
        if hierarchy[0][i][3] != -1:  # Verifica si el contorno tiene un padre (hijo de otro)
            continue  # Ignora los contornos internos como el hueco de la "O"

        if cv2.contourArea(cnt) > 20:
            center = get_centeroid(cnt)
            if center:
                letter = Letter(cnt,center)
                figures.append(letter)
                yield center
                
def getCentersDataset(img):
    global datasetCenters
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    max_contour = max(contours, key=cv2.contourArea) if contours else None
    
    for i, cnt in enumerate(contours):
        if hierarchy[0][i][3] != -1:  # Verifica si el contorno tiene un padre (hijo de otro)
            continue  # Ignora los contornos internos como el hueco de la "O"

        if cv2.contourArea(cnt) > 20:
            center = get_centeroid(cnt)
            if center:
                letter = Letter(cnt,center)
                datasetCenters.append(letter)
                yield center
    

def get_rows(centers, row_amt, row_h):
    centers = np.array(centers)
    d = row_h / row_amt
    for i in range(row_amt):
        f = centers[:, 1] - d * i
        a = centers[(f < d) & (f > 0)]
        yield a[a.argsort(0)[:, 0]]
        
def prepareDataset():
    global abc, datasetCenters, dataSimilarity
    abc = cv2.imread("dataset.png")
    abc = cv2.resize(abc, (800,800))
    abc = correct_perspective(abc)
    abc = correct_perspective(abc)
    abc_processed = process_img(abc)
    datasetCentersList = list(getCentersDataset(abc_processed))
    #contours, hierarchy = cv2.findContours(abc_processed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    h, w, c = abc.shape
    count = 0
    orderDataset = []
    for row in get_rows(datasetCentersList, 9, w):
        for x, y in row:
            for letter in datasetCenters:
                if(letter.getCenter() == (x,y)):
                    letter.setSimilarity(dataSimilarity,count+1)
                    orderDataset.append(letter)
                    break
            count += 1
            cv2.circle(abc, (x, y), 10, (0, 0, 255), -1)  
            cv2.putText(abc, str(count), (x - 10, y + 5), 1, cv2.FONT_HERSHEY_PLAIN, (0, 255, 255), 2)
    datasetCenters = orderDataset
    
        
    
def prepareImg():
    global img, figures
    img = cv2.imread(ruta)
    img = cv2.resize(img, (800,800))
    img = correct_perspective(img)
    img = correct_perspective(img)
    img_processed = process_img(img)
    centersList = list(get_centers(img_processed))
    h, w, c = img.shape
    count = 0
    orderFigures = []
    for row in get_rows(centersList, 8, w):
        #cv2.polylines(img, [row], False, (255, 0, 255), 2)
        for x, y in row:
            for letter in figures:
                if(letter.getCenter() == (x,y)):
                    orderFigures.append(letter)
                    break
            count += 1
            cv2.circle(img, (x, y), 10, (0, 0, 255), -1)  
            cv2.putText(img, str(count), (x - 10, y + 5), 1, cv2.FONT_HERSHEY_PLAIN, (0, 255, 255), 2)
    figures = orderFigures
    
def prepareImg2():
    global img2, ruta
    img2 = cv2.imread(ruta)
    img2 = cv2.resize(img2, (800,800))
    img2 = correct_perspective(img2)
    img2 = correct_perspective(img2)
    
def foundSentence(sentence, soup): 
    sentence = sentence.upper()
    found = []
    result = []
    for i in range(len(soup)):
        letter = sentence[0]
        if soup[i].containsLetter(letter):
            subStr = sentence[1:]
            found.append(soup[i])
            for inc in [-13, -12,12, -11, -1, 1, 11, 13]:  # Iteramos sobre los incrementos
                result = inLine(found.copy(), soup, subStr, inc, i)
                if len(result) == len(sentence):
                    print(len(result))
                    return result
        else:
            found = []
        
def inLine(found,soup,sentence, increment, i):
    original = found
    for letter in sentence:
        i += increment
        if not (i>0):
            found = original
            return found
        try:
            if soup[i].containsLetter(letter):
                found.append(soup[i])
            else:
                found = original
                return found
        except IndexError:
                found = original
                return found
    return found

def finalResult():
    global img2
    result = foundSentence(sentence,figures)

    if result != None:
        for c in result:
            hull = cv2.convexHull(c.getContour())
            (x_center, y_center), radius = cv2.minEnclosingCircle(hull)
            center = (int(x_center), int(y_center))
            radius = int(radius)
            cv2.circle(img2, center, radius, (0, 255, 0), 2)  
    

class MiEtiqueta(QtWidgets.QLabel):
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.Lista = []
        self.setStyleSheet("border: 1px solid black;")


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
        global sentence
        text = self.textInput.text()
        if text :
            sentence = text
            finalResult()
            self.ActualizarImagen2()
        

    def handleSaveFile(self):
        global img2
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", "", "Images(*.jpg *.png)")
        if fileName:
            cv2.imwrite(fileName, self.Second_image)

    def handleOpen(self):
        global ruta,figures,datasetCenters
        
        path = QtWidgets.QFileDialog.getOpenFileName(self, "Choose File", "./", "Images(*.jpg *.png)")[0]
        if path:
            self._path = path
            ruta = self._path
            prepareDataset()
            prepareImg()
            prepareImg2()
            for c in figures:
                """ print(str(count) + " " + str(cv2.contourArea(c.getContour())))
                count += 1 """
                for letABC in datasetCenters:
                    similarity = cv2.matchShapes(letABC.getContour(),c.getContour(),cv2.CONTOURS_MATCH_I1, 0.0)
                    if similarity < letABC.getSimilarityValue():
                        c.setPosibleLetter(letABC.getLetter())
            self.ActualizarImagen()

    def ActualizarPixMap(self):
        QImageTemp = QtGui.QImage(cv2.cvtColor(self.OpenCV_image, cv2.COLOR_BGR2RGB),
                                  self.OpenCV_image.shape[1],
                                  self.OpenCV_image.shape[0],
                                  self.OpenCV_image.shape[1] * 3,
                                  QtGui.QImage.Format.Format_RGB888)
        pixmap = QtGui.QPixmap(QImageTemp)
        self.viewer.setPixmap(pixmap)

    def ActualizarImagen2(self):
        global img2
        self.Second_image = img2
        tamano = (self.viewer2.size().width(), self.viewer2.size().height())
        self.Second_image = cv2.resize(self.Second_image, tamano, interpolation=cv2.INTER_LINEAR)

        QImageTemp2 = QtGui.QImage(cv2.cvtColor(self.Second_image, cv2.COLOR_BGR2RGB),
                                   self.Second_image.shape[1],
                                   self.Second_image.shape[0],
                                   self.Second_image.shape[1] * 3,
                                   QtGui.QImage.Format.Format_RGB888)
        pixmap2 = QtGui.QPixmap(QImageTemp2)
        self.viewer2.setPixmap(pixmap2)

    def ActualizarImagen(self):
        self.OpenCV_image = cv2.imread(self._path)
        tamano = (self.viewer.size().width(), self.viewer.size().height())
        self.OpenCV_image = cv2.resize(self.OpenCV_image, tamano, interpolation=cv2.INTER_LINEAR)
        self.ActualizarPixMap()
    
    
    
ruta = ''  
sentence = ""
abc = None
img = None
img2= None

datasetCenters = []
figures = []
dataSimilarity = {
    'A':0.30,
    'B':0.30,
    'C':5.0,
    'D':0.10,
    #La letra E funciona muy mal agarra practicamente todas las letras
    'E':71,
    #Esta tambien funciona horrible
    'F':87,
    #Esta es preocupante por que agarra E y F antes que la G
    'G':68,
    #Esta agarra G
    'H':5,
    #Esta agarra muchas letras
    'I':10,
    #Este agarra I
    'J':4.5,
    'K':200,
    #Esto Agarra I
    'L':5.8,
    #Esto agarra N
    'M':1.5,
    #Esto agarra la M
    'N':1.4,
    #Esto agarra la Q
    'O':0.03,
    'P':0.30,
    #Es una gran ventaja esto
    'Q':0.02,
    'R':0.30,
    #Puta letra de mierda te odio
    'S':390,
    #Agarra Muchas letras
    'T':32,
    #Agarra Muchas letras
    'U':75.8,
    #No hay ninguna V
    'V':0.10,
    #Agarra N y M
    'W':1.1,
    #No hay ninguna X
    'X':0.10,
    #CHTM
    'Y':1350,
    #Agarra S y otras cosas
    'Z':9
}

app = QtWidgets.QApplication(sys.argv)
window = Window()
window.setWindowTitle("Soup")
window.show()
sys.exit(app.exec())


#letA = datasetCenters[4].getContour()
#print(cv2.contourArea(letA))