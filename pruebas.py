import cv2
import numpy as np
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
        cv2.THRESH_BINARY_INV, 11, 2
    )

    # Aplicar dilatación con kernel más pequeño
    kernel = np.ones((2, 2), np.uint8)
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

        if cv2.contourArea(cnt) > 130 and (max_contour is None or not np.array_equal(cnt, max_contour)):
            center = get_centeroid(cnt)
            if center:
                letter = Letter(cnt,center)
                figures.append(letter)
                yield center
    

def get_rows(centers, row_amt, row_h):
    centers = np.array(centers)
    d = row_h / row_amt
    for i in range(row_amt):
        f = centers[:, 1] - d * i
        a = centers[(f < d) & (f > 0)]
        yield a[a.argsort(0)[:, 0]]

sentence = "coco"
figures = []

abc = cv2.imread("abecedario.png")
abc = process_img(abc)

# Carga la imagen y corrige perspectiva
img = cv2.imread("prueba2.jpg")
img = cv2.resize(img, (800, 800))
img = correct_perspective(img)
img = correct_perspective(img)
# Opcional: Endereza si está torcida
img2 = correct_perspective(img)

img_processed = process_img(img)
centers = list(get_centers(img_processed))
contours, hierarchy = cv2.findContours(img_processed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
abc_contours, _ = cv2.findContours(abc, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
abc_contours = sorted(abc_contours, key=lambda c: cv2.boundingRect(c)[0])

h, w, c = img.shape
count = 0

letter = abc_contours[0]

for c in figures:
    if cv2.contourArea(c.contour) < 130:
        continue
    
    similarity = cv2.matchShapes(letter,c.contour,cv2.CONTOURS_MATCH_I1, 0.0)
    if similarity < 0.33:
        hull = cv2.convexHull(c.contour)
        (x_center, y_center), radius = cv2.minEnclosingCircle(hull)
        center = (int(x_center), int(y_center))
        radius = int(radius)
        cv2.circle(img2, center, radius, (0, 255, 0), 2)  
    

for row in get_rows(centers, 8, h):
    cv2.polylines(img, [row], False, (255, 0, 255), 2)
    for x, y in row:
        count += 1
        cv2.circle(img, (x, y), 10, (0, 0, 255), -1)  
        cv2.putText(img, str(count), (x - 10, y + 5), 1, cv2.FONT_HERSHEY_PLAIN, (0, 255, 255), 2)

cv2.imshow("Ordered", img)
cv2.imshow("Circulos", img2)
cv2.imshow("Contornos", img_processed)
cv2.imshow("Abecedario", abc)

cv2.waitKey(0)
cv2.destroyAllWindows()
