import cv2
import mediapipe as mp
import math
import time
import serial

#SERIAL (ESP32) 
try:
    ser = serial.Serial('COM6', 115200, timeout=1)  
    time.sleep(2)
    print("ESP32 Connected")
except:
    ser = None
    print("ESP32 NOT Connected")

# MEDIAPIPE 
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    refine_landmarks=True,
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Eye landmark indices
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# FUNCTIONS 
def euclidean(p1, p2):
    return math.dist(p1, p2)

def eye_aspect_ratio(eye):
    v1 = euclidean(eye[1], eye[5])
    v2 = euclidean(eye[2], eye[4])
    h = euclidean(eye[0], eye[3])
    return (v1 + v2) / (2.0 * h)

# CAMERA 
IP_CAMERA_URL = "http://192.0.0.4:8080/video"  # CHANGE THIS
cap = cv2.VideoCapture(IP_CAMERA_URL)

#  THRESHOLDS 
EYE_CLOSED_THRESHOLD = 0.22
CLOSED_EYES_TIME = 2.0  # seconds

eye_closed_start = None
alert_active = False

# MAIN LOOP 
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print(" Camera not responding")
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    if result.multi_face_landmarks:
        face = result.multi_face_landmarks[0]
        h, w, _ = frame.shape

        left_eye = []
        right_eye = []

        # LEFT EYE
        for idx in LEFT_EYE:
            lm = face.landmark[idx]
            x, y = int(lm.x * w), int(lm.y * h)
            left_eye.append((x, y))
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        # RIGHT EYE
        for idx in RIGHT_EYE:
            lm = face.landmark[idx]
            x, y = int(lm.x * w), int(lm.y * h)
            right_eye.append((x, y))
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        # EAR Calculation
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0

        # DROWSINESS LOGIC 
        if avg_ear < EYE_CLOSED_THRESHOLD:
            if eye_closed_start is None:
                eye_closed_start = time.time()

            elif time.time() - eye_closed_start >= CLOSED_EYES_TIME:
                if not alert_active:
                    alert_active = True
                    if ser:
                        ser.write(b'A')  #  ALERT ON
        else:
            eye_closed_start = None
            if alert_active:
                alert_active = False
                if ser:
                    ser.write(b'N')  #  NORMAL

        # DISPLAY 
        cv2.putText(frame, f"EAR: {avg_ear:.2f}", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)

        if alert_active:
            cv2.putText(frame, "DROWSINESS ALERT!", (30, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 255), 3)

    cv2.imshow("Driver Drowsiness Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

# CLEANUP
cap.release()
cv2.destroyAllWindows()
if ser:
    ser.close()
