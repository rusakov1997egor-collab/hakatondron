import cv2
import numpy as np
from typing import Tuple
from collections import deque
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class GestureReader:
    """
    Класс для распознавания жеста: открытая ладонь -> кулак = "coming"
    Использует MediaPipe HandLandmarker (новый API)
    """

    def __init__(self, history_size: int = 15):
        """Инициализация детектора жестов."""

        print("[GestureReader] Загрузка MediaPipe HandLandmarker...")

        # Скачиваем модель если нужно
        import urllib.request
        import os

        model_path = 'hand_landmarker.task'
        if not os.path.exists(model_path):
            print("Скачивание модели hand_landmarker.task...")
            url = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
            urllib.request.urlretrieve(url, model_path)
            print("Модель скачана!")

        # Создаем HandLandmarker
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

        # История состояний
        self.hand_state_history = deque(maxlen=history_size)

        # Флаги
        self.gesture_detected = False
        self.cooldown_frames = 0
        self.cooldown_duration = 30

        # Счетчик кадров для timestamp
        self.frame_count = 0

        print("[GestureReader] Инициализирован (MediaPipe HandLandmarker)")

    def _count_extended_fingers(self, hand_landmarks) -> int:
        """Подсчет выпрямленных пальцев."""

        fingers_extended = 0

        # Индексы кончиков и оснований пальцев
        finger_tips = [8, 12, 16, 20]  # Указательный, средний, безымянный, мизинец
        finger_pips = [6, 10, 14, 18]  # Средние фаланги

        # Проверяем 4 пальца (кроме большого)
        for tip, pip in zip(finger_tips, finger_pips):
            if hand_landmarks[tip].y < hand_landmarks[pip].y:
                fingers_extended += 1

        # Большой палец (проверяем по X)
        if abs(hand_landmarks[4].x - hand_landmarks[3].x) > 0.05:
            fingers_extended += 1

        return fingers_extended

    def _detect_gesture(self) -> bool:
        """Детекция жеста: открытая -> закрытая."""

        if len(self.hand_state_history) < 10:
            return False

        history_list = list(self.hand_state_history)

        # Была открыта -> стала закрыта
        recent_closed = sum(history_list[-5:]) == 0
        previous_open = sum(history_list[-10:-5]) >= 3

        return previous_open and recent_closed

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, bool]:
        """Обработка кадра."""

        # Cooldown
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
            if self.cooldown_frames == 0:
                self.gesture_detected = False

        # Конвертируем в MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Детекция
        self.frame_count += 1
        timestamp_ms = self.frame_count * 33  # ~30 FPS
        detection_result = self.detector.detect_for_video(mp_image, timestamp_ms)

        hand_detected = False
        is_open = False
        finger_count = 0

        # Обрабатываем результаты
        if detection_result.hand_landmarks:
            for hand_landmarks in detection_result.hand_landmarks:
                hand_detected = True

                # Рисуем landmarks
                h, w = frame.shape[:2]
                for landmark in hand_landmarks:
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

                # Рисуем соединения
                connections = [
                    (0, 1), (1, 2), (2, 3), (3, 4),  # Большой
                    (0, 5), (5, 6), (6, 7), (7, 8),  # Указательный
                    (0, 9), (9, 10), (10, 11), (11, 12),  # Средний
                    (0, 13), (13, 14), (14, 15), (15, 16),  # Безымянный
                    (0, 17), (17, 18), (18, 19), (19, 20),  # Мизинец
                    (5, 9), (9, 13), (13, 17)  # Ладонь
                ]

                for connection in connections:
                    start_idx, end_idx = connection
                    start = hand_landmarks[start_idx]
                    end = hand_landmarks[end_idx]
                    start_point = (int(start.x * w), int(start.y * h))
                    end_point = (int(end.x * w), int(end.y * h))
                    cv2.line(frame, start_point, end_point, (0, 255, 0), 2)

                # Считаем пальцы
                finger_count = self._count_extended_fingers(hand_landmarks)
                is_open = finger_count >= 4

                # Показываем счетчик
                cv2.putText(frame, f"Fingers: {finger_count}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                self.hand_state_history.append(is_open)
                break

        # Статус
        if hand_detected:
            state_text = "OPEN HAND" if is_open else "CLOSED HAND"
            color = (0, 255, 0) if is_open else (0, 0, 255)
        else:
            state_text = "NO HAND - Show your hand"
            color = (128, 128, 128)
            self.hand_state_history.clear()

        cv2.putText(frame, state_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Детекция жеста
        is_come_here = False
        if not self.gesture_detected and self.cooldown_frames == 0:
            if self._detect_gesture():
                is_come_here = True
                self.gesture_detected = True
                self.cooldown_frames = self.cooldown_duration
                self.hand_state_history.clear()

        # Отображение
        if self.gesture_detected:
            h, w = frame.shape[:2]
            cv2.putText(frame, "COMING!", (w//2 - 150, h//2),
                       cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 255, 0), 5)

        return frame, is_come_here

    def reset_history(self):
        """Сброс истории."""
        self.hand_state_history.clear()
        self.gesture_detected = False
        self.cooldown_frames = 0

    def __del__(self):
        """Очистка."""
        if hasattr(self, 'detector'):
            self.detector.close()
