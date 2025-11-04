import cv2, time, numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    model_complexity=0,
    enable_segmentation=False,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6,
)

cap = cv2.VideoCapture(0)
W_SMOOTH = 5
left_right_hist = []
last_action_time = 0
DEBOUNCE = 0.35  # segundos
WINDOW_NAME = "Pose Control"


def decide_action(lm, img_w, img_h):
    # Pega pontos principais (normalizados)
    def P(i):
        return np.array([lm[i].x * img_w, lm[i].y * img_h])

    nose = P(mp_pose.PoseLandmark.NOSE.value)
    lw = P(mp_pose.PoseLandmark.LEFT_WRIST.value)
    rw = P(mp_pose.PoseLandmark.RIGHT_WRIST.value)
    ls = P(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
    rs = P(mp_pose.PoseLandmark.RIGHT_SHOULDER.value)
    lh = P(mp_pose.PoseLandmark.LEFT_HIP.value)
    rh = P(mp_pose.PoseLandmark.RIGHT_HIP.value)

    mid_shoulder_x = (ls[0] + rs[0]) / 2
    mid_hip_y = (lh[1] + rh[1]) / 2
    head_y = nose[1]

    # Heurísticas simples
    jump = (lw[1] < head_y) and (rw[1] < head_y)
    duck = (mid_hip_y - head_y) < img_h * 0.22

    # Esquerda/Direita por inclinação
    center_x = img_w / 2
    tilt = (mid_shoulder_x - center_x) / (img_w * 0.5)  # ~ -1 a 1
    left_right_hist.append(tilt)
    if len(left_right_hist) > W_SMOOTH:
        left_right_hist.pop(0)
    tilt_avg = np.mean(left_right_hist)

    left = tilt_avg < -0.25
    right = tilt_avg > 0.25

    # Gesto com mão direita cruzando a linha média
    mid_body_x = (lh[0] + rh[0]) / 2
    if rw[0] < mid_body_x - img_w * 0.05:
        left = True
    if rw[0] > mid_body_x + img_w * 0.15:
        right = True

    # Priorização
    if jump:
        return "JUMP"
    if duck:
        return "DUCK"
    if left:
        return "LEFT"
    if right:
        return "RIGHT"
    return None


def safe_release():
    # fecha tudo com segurança (sempre será chamado)
    try:
        pose.close()
    except Exception:
        pass
    try:
        if cap is not None:
            cap.release()
    except Exception:
        pass
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass


try:
    # opcional: criar explicitamente a janela (ajuda em alguns SOs)
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = pose.process(rgb)

        action = None
        if res.pose_landmarks:
            action = decide_action(res.pose_landmarks.landmark, w, h)

        now = time.time()
        if action and (now - last_action_time) > DEBOUNCE:
            print(action)
            last_action_time = now

        # Desenho opcional dos landmarks
        mp.solutions.drawing_utils.draw_landmarks(
            frame,
            res.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp.solutions.drawing_styles.get_default_pose_landmarks_style(),
        )

        cv2.putText(
            frame,
            f"ACTION: {action or '-'}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        cv2.imshow(WINDOW_NAME, frame)

        # 1) Teclas: ESC ou 'q'
        k = cv2.waitKey(1) & 0xFF
        if k == 27 or k == ord("q"):
            break

        # 2) Clique no X da janela (quando a janela some/fecha)
        # Se a janela não estiver mais visível, sai do loop
        visible = cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE)
        if visible < 1:
            break

except KeyboardInterrupt:
    # Permite parar com Ctrl+C no terminal
    pass
finally:
    safe_release()
