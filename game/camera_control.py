import cv2
import numpy as np
import mediapipe as mp
import time


class CameraController:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.pose = mp.solutions.pose.Pose(
            model_complexity=0,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        )

        self.last_action_time = 0
        self.debounce = 0.35  # segundos
        self.left_right_hist = []

    def get_action(self):
        ok, frame = self.cap.read()
        if not ok:
            return None

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.pose.process(rgb)
        if not res.pose_landmarks:
            return None

        lm = res.pose_landmarks.landmark
        now = time.time()

        def P(i):
            return np.array([lm[i].x * w, lm[i].y * h])

        lw, rw, nose = P(15), P(16), P(0)
        lh, rh = P(23), P(24)
        ls, rs = P(11), P(12)

        mid_shoulder_x = (ls[0] + rs[0]) / 2
        mid_hip_y = (lh[1] + rh[1]) / 2
        head_y = nose[1]

        jump = (lw[1] < head_y) and (rw[1] < head_y)
        duck = (mid_hip_y - head_y) < h * 0.22

        tilt = (mid_shoulder_x - w / 2) / (w * 0.5)
        self.left_right_hist.append(tilt)
        if len(self.left_right_hist) > 5:
            self.left_right_hist.pop(0)
        tilt_avg = float(np.mean(self.left_right_hist))

        left = tilt_avg < -0.25
        right = tilt_avg > 0.25

        if now - self.last_action_time < self.debounce:
            return None

        action = None
        if jump:
            action = "JUMP"
        elif duck:
            action = "DUCK"
        elif left:
            action = "LEFT"
        elif right:
            action = "RIGHT"

        if action:
            self.last_action_time = now
        return action

    def close(self):
        """Fecha os recursos da câmera e do MediaPipe com segurança."""
        try:
            if hasattr(self, "pose") and self.pose:
                self.pose.close()
        except Exception:
            pass

        try:
            if hasattr(self, "cap") and self.cap:
                self.cap.release()
        except Exception:
            pass

        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
