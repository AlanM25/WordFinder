"""
Las sopas de letras de este programa son ejemplos
proporcionados por:

https://www.superteacherworksheets.com/generator-word-search.html


"""


import cv2
import numpy as np
import math
from letter import Letter

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
    global abc, datasetCenters
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
                    orderDataset.append(letter)
                    break
            count += 1
            cv2.circle(abc, (x, y), 10, (0, 0, 255), -1)  
            cv2.putText(abc, str(count), (x - 10, y + 5), 1, cv2.FONT_HERSHEY_PLAIN, (0, 255, 255), 2)
    datasetCenters = orderDataset
    cv2.imshow("Dataset", abc)
    
        
    
def prepareImg():
    global img, figures
    img = cv2.imread("prueba2.jpg")
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
    global img2
    img2 = cv2.imread("prueba2.jpg")
    img2 = cv2.resize(img2, (800,800))
    img2 = correct_perspective(img2)
    img2 = correct_perspective(img2)
    
    
        
    
sentence = "TOYS"

datasetCenters = []
figures = []
similarity = {
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

abc = None
prepareDataset()

img = None
prepareImg()

img2= None
prepareImg2()

letA = datasetCenters[4].getContour()
print(cv2.contourArea(letA))

for c in figures:
    similarity = cv2.matchShapes(letA,c.getContour(),cv2.CONTOURS_MATCH_I1, 0.0)
    if similarity < 71 :
        hull = cv2.convexHull(c.getContour())
        (x_center, y_center), radius = cv2.minEnclosingCircle(hull)
        center = (int(x_center), int(y_center))
        radius = int(radius)
        cv2.circle(img2, center, radius, (0, 255, 0), 2) 


cv2.imshow("OrderImg", img)
cv2.imshow("img2", img2)
cv2.waitKey(0)
cv2.destroyAllWindows()