import cv2
import numpy as np

# Rutas de las imágenes
abecedario_path = "abecedario.png"
letras_path = "letras.png"

#############################
# 1. Extraer el contorno de la "A" a partir del abecedario
#############################
# Cargar y procesar la imagen del abecedario
abc = cv2.imread(abecedario_path)
gray_abc = cv2.cvtColor(abc, cv2.COLOR_BGR2GRAY)
gray_abc = cv2.GaussianBlur(gray_abc, (5, 5), 0)
gray_abc = cv2.bilateralFilter(src=gray_abc, d=9, sigmaColor=75, sigmaSpace=75)
abc_edged = cv2.Canny(gray_abc, 30, 200)

# Encontrar contornos en el abecedario
abc_contours, abc_hierarchy = cv2.findContours(abc_edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Ordenar los contornos de izquierda a derecha usando la coordenada x del rectángulo delimitador
abc_contours = sorted(abc_contours, key=lambda c: cv2.boundingRect(c)[0])

# Se asume que el primer contorno corresponde a la letra "A"
if len(abc_contours) == 0:
    print("No se encontraron contornos en la imagen del abecedario.")
    exit()
contour_A = abc_contours[2]

#############################
# 2. Procesar la imagen de la sopa de letras
#############################
imageOr = cv2.imread(letras_path)
image = cv2.imread(letras_path)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#gray = cv2.GaussianBlur(gray, (5, 5), 0)
gray = cv2.bilateralFilter(src=gray, d=9, sigmaColor=75, sigmaSpace=75)
#gray = cv2.medianBlur(gray, 5)
edged = cv2.Canny(gray, 30, 200)

# Encontrar contornos en la imagen de letras
contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Definir un umbral de similitud para considerar que dos formas son iguales.
# (Mientras menor sea el valor devuelto por cv2.matchShapes, mayor similitud tienen)
match_threshold = 0.50  # Ajusta este valor según tus imágenes

for c in contours:
    # Filtrar contornos muy pequeños para evitar ruido
    if cv2.contourArea(c) < 50:
        continue

    # Comparar el contorno actual con el contorno de la "A"
    similarity = cv2.matchShapes(contour_A, c, cv2.CONTOURS_MATCH_I1, 0.0)
    # Si la similitud es menor que el umbral, consideramos que es una "A"
    print(similarity)
    if similarity < match_threshold:
        print("Si entro")
        M = cv2.moments(c)
        if M["m00"] > 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            x, y, w, h = cv2.boundingRect(c)
            radius = max(w, h) // 2 + 5
            cv2.circle(imageOr, (cX, cY), radius, (0, 255, 0), 2)  # Círculo verde para la "A"

# Mostrar el resultado
cv2.imshow("Letras con la A Encerrada", imageOr)
cv2.imshow("Bordes", edged)
cv2.waitKey(0)
cv2.destroyAllWindows()
