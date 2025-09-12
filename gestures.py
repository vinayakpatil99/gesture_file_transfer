import cv2
import mediapipe as mp

class HandGesture:
    def __init__(self, max_num_hands=1, min_detection_confidence=0.6, min_tracking_confidence=0.6):
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils

    def detect(self, frame):
        """
        Detects hand and classifies simple gestures:
        returns (gesture, (cx, cy))
        gesture is one of: "open", "fist", None
        (cx, cy) are pixel coordinates of a central landmark to follow (landmark 9)
        """
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        if results.multi_hand_landmarks:
            handLms = results.multi_hand_landmarks[0]
            self.mp_draw.draw_landmarks(frame, handLms, mp.solutions.hands.HAND_CONNECTIONS)

            # fingertips indices: 8,12,16,20 (exclude thumb)
            tips = [8, 12, 16, 20]
            folded = 0
            for tip in tips:
                # Compare tip y to pip joint y (tip-2)
                if handLms.landmark[tip].y > handLms.landmark[tip - 2].y:
                    folded += 1

            # central coordinate (using landmark 9 - middle of the palm)
            cx = int(handLms.landmark[9].x * w)
            cy = int(handLms.landmark[9].y * h)

            if folded >= 3:
                return "fist", (cx, cy)
            elif folded == 0:
                return "open", (cx, cy)
            else:
                return None, (cx, cy)
        return None, (None, None)
