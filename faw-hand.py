#IMPORTAR RECURSOS NECESARIOS.
import cv2
import mediapipe as mp
import math

#Auxiliares
colores_primarios = [(255, 0, 0),   # Rojo
                     (0, 255, 0),   # Verde
                     (0, 0, 255),   # Azul
                     (255, 255, 0), # Amarillo
                     (255, 0, 255), # Magenta
                     (0, 255, 255), # Cian
                     (255, 128, 0)  # Naranja
                    ]
color_activo = [0,0,0,0]
activa_circulo = [0,0,0,0]

#INICIAR SISTEMA DE DETECCIÓN.
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

#INICIAR CAMARA
cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    #COMPROBAR ENTRADA
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      continue
    #CONVERTIR IMAGEN A RGB
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = hands.process(image)

    #DIBUJAR PUNTOS DE DETECCIÓN
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      print (activa_circulo,color_activo)
      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)  

        #Econtrar coordenadas de la punta de los dedos
        # Obtener las coordenadas de las puntas de los dedos
        height, width, _ = image.shape  # Dimensiones de la imagen en píxeles
        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
        pinky_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
        
        # Calcular la distancia entre la punta del pulgar y las puntas de los otros dedos
        distancias = []
        i=0
        
        for finger_tip in [index_finger_tip, middle_finger_tip, ring_finger_tip, pinky_finger_tip]:
          point1 = (int(thumb_tip.x * width),int(thumb_tip.y * height))
          point2 = (int(finger_tip.x * width),int(finger_tip.y * height))
          if point1[0] == point2[0] and point1[1] == point2[1]:
            # Son iguales
            distancia = 51
          else:
            distancia = math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
            distancias.append(distancia)
            distancia_cm = distancia / 50 * 2.4
              # Actualizar el estado
            if activa_circulo[i] == 0:
                if distancia <= 50:
                    activa_circulo[i] = 1
            elif activa_circulo[i] == 1:
                if distancia > 50:
                    activa_circulo[i] = 2
            elif activa_circulo[i] == 2:
                if distancia <= 50:
                    activa_circulo[i] = 3
            elif activa_circulo[i] == 3:
                if distancia > 50:
                    activa_circulo[i] = 4
            elif activa_circulo[i] == 4:
                if distancia <= 50:
                    color_activo[i] = color_activo[i] + 1
                    if color_activo[i] == 7:
                      color_activo[i] = 0
                    activa_circulo[i] = 1
            if activa_circulo[i] ==1 or activa_circulo[i] == 2:
              cv2.circle(image,(point2[0],point2[1]),5,(0,255,0),-1)
              # Calcular el punto medio
              center = ((point1[0] + point2[0]) // 2, (point1[1] + point2[1]) // 2)
              # Calcular el radio como la mitad de la distancia entre los dos puntos
              radius = int(math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2) / 2)
              # Dibujar la línea entre los dos puntos
              cv2.line(image, point1, point2, (255, 0, 0), 2)
              # Agregar el texto de la distancia en cm a la imagen
              texto = f"Distancia: {distancia_cm:.2f} cm"
              cv2.putText(image, texto, center, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
              # Dibujar el círculo con el centro en el punto medio
              cv2.circle(image, center, radius, colores_primarios[color_activo[i]], 2)
          i = i + 1
            
        cv2.circle(image,(int(thumb_tip.x * width), int(thumb_tip.y * height)),5,(255,0,0),-1)
    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()
