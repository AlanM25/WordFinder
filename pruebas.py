import cv2
import numpy as np

def correct_perspective(img):
    """ Intenta corregir la perspectiva si la imagen está inclinada """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 200)
    
    # Detectar contornos y encontrar el más grande (posible borde de la sopa de letras)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return img  # Si no hay contornos, devuelve la imagen original
    
    max_contour = max(contours, key=cv2.contourArea)
    epsilon = 0.02 * cv2.arcLength(max_contour, True)
    approx = cv2.approxPolyDP(max_contour, epsilon, True)
    
    if len(approx) == 4:  # Si detecta un cuadrado o rectángulo
        pts_src = np.float32([point[0] for point in approx])
        pts_dst = np.float32([[0, 0], [800, 0], [800, 800], [0, 800]])
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
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    max_contour = max(contours, key=cv2.contourArea) if contours else None
    
    for cnt in contours:
        if cv2.contourArea(cnt) > 50 and (max_contour is None or not np.array_equal(cnt, max_contour)):
            center = get_centeroid(cnt)
            if center:
                yield center

def get_rows(centers, row_amt, row_h):
    centers = np.array(centers)
    d = row_h / row_amt
    for i in range(row_amt):
        f = centers[:, 1] - d * i
        a = centers[(f < d) & (f > 0)]
        yield a[a.argsort(0)[:, 0]]

# Carga la imagen y corrige perspectiva
img = cv2.imread("sopaNormal.jpg")
img = cv2.resize(img, (800, 800))
img = correct_perspective(img)  # Opcional: Endereza si está torcida

img_processed = process_img(img)
centers = list(get_centers(img_processed))

h, w, c = img.shape
count = 0

for row in get_rows(centers, 12, h):
    cv2.polylines(img, [row], False, (255, 0, 255), 2)
    for x, y in row:
        count += 1
        cv2.circle(img, (x, y), 10, (0, 0, 255), -1)  
        cv2.putText(img, str(count), (x - 10, y + 5), 1, cv2.FONT_HERSHEY_PLAIN, (0, 255, 255), 2)

cv2.imshow("Ordered", img)
cv2.imshow("Contornos", img_processed)

cv2.waitKey(0)
cv2.destroyAllWindows()
