import cv2
import numpy as np


abecedario_path = "abecedario.png"
letras_path = "letras.png"
#letras_path = "sopaNormal.jpg"


abc = cv2.imread(abecedario_path)
gray_abc = cv2.cvtColor(abc, cv2.COLOR_BGR2GRAY)


gray_abc = cv2.bilateralFilter(src=gray_abc, d=9, sigmaColor=75, sigmaSpace=75)


abc_edged = cv2.Canny(gray_abc, 30, 200)


abc_contours, abc_hierarchy = cv2.findContours(abc_edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


abc_contours = sorted(abc_contours, key=lambda c: cv2.boundingRect(c)[0])


if len(abc_contours) == 0:
    print("No se encontraron contornos en la imagen del abecedario.")
    exit()
contour_A = abc_contours[0]


imageOr = cv2.imread(letras_path)
image = cv2.imread(letras_path)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


gray = cv2.bilateralFilter(src=gray, d=9, sigmaColor=75, sigmaSpace=75)


edged = cv2.Canny(gray, 30, 200)


contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])

match_threshold = 0.33 

for c in contours:
   
    if cv2.contourArea(c) < 50:
        continue

    
    similarity = cv2.matchShapes(contour_A, c, cv2.CONTOURS_MATCH_I1, 0.0)
    print("Similitud:", similarity)
    if similarity < match_threshold:
        print("Contorno similar a 'A' detectado")
        
        hull = cv2.convexHull(c)
       
        (x_center, y_center), radius = cv2.minEnclosingCircle(hull)
        center = (int(x_center), int(y_center))
        radius = int(radius)
        cv2.circle(imageOr, center, radius, (0, 255, 0), 2)  

       
        """ rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        box = np.array(box, dtype=np.int32)
        cv2.drawContours(imageOr, [box], 0, (0, 255, 0), 2) """

# Mostrar el resultado
#cv2.imshow("Abecedario Edged", abc_edged)
cv2.imshow("Letras con la A Encerrada", imageOr)
cv2.imshow("Bordes", edged)
cv2.waitKey(0)
cv2.destroyAllWindows()
