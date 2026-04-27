import cv2
import mediapipe as mp
from typing import Tuple, Optional
import numpy as np
from collections import deque


class GestureReader:
    """
    Класс для распознавания жестов руки с помощью MediaPipe.
    Основная задача - детекция жеста 'иди ко мне' (beckoning gesture).
    """

    def __init__(self, history_size: int = 10, movement_threshold: float = 0.03):
        """
        Инициализация детектора жестов.

        Args:
            history_size: количество кадров для отслеживания истории движения
            movement_threshold: порог изменения расстояния для детекции жеста
        """
        # Инициализация MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # Создание детектора рук
        # max_num_hands=1 - отслеживаем только одну руку для упрощения
        # min_detection_confidence - минимальная уверенность для детекции
        # min_tracking_confidence - минимальная уверенность для трекинга
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

        # История позиций кончиков пальцев для отслеживания движения
        # Используем deque для эффективного добавления/удаления элементов
        self.fingertip_history = deque(maxlen=history_size)
        self.movement_threshold = movement_threshold

        print(f"[GestureReader] Инициализирован. История: {history_size} кадров, порог: {movement_threshold}")

    def _calculate_distance(self, point1: tuple, point2: tuple) -> float:
        """
        Вычисление евклидова расстояния между двумя точками.

        Args:
            point1: координаты первой точки (x, y)
            point2: координаты второй точки (x, y)

        Returns:
            Расстояние между точками
        """
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def _detect_beckoning_gesture(self, hand_landmarks) -> bool:
        """
        Детекция жеста 'иди ко мне' на основе движения пальцев.

        Логика:
        1. Вычисляем среднее расстояние от кончиков пальцев до запястья
        2. Сохраняем в историю
        3. Если расстояние уменьшается (пальцы движутся к ладони) - это жест 'ко мне'

        Args:
            hand_landmarks: landmarks руки от MediaPipe

        Returns:
            True если обнаружен жест 'ко мне', иначе False
        """
        # Индексы ключевых точек MediaPipe:
        # 0 - запястье (WRIST)
        # 4 - кончик большого пальца (THUMB_TIP)
        # 8 - кончик указательного пальца (INDEX_FINGER_TIP)
        # 12 - кончик среднего пальца (MIDDLE_FINGER_TIP)
        # 16 - кончик безымянного пальца (RING_FINGER_TIP)
        # 20 - кончик мизинца (PINKY_TIP)

        wrist = hand_landmarks.landmark[0]
        fingertips = [
            hand_landmarks.landmark[4],   # Большой палец
            hand_landmarks.landmark[8],   # Указательный
            hand_landmarks.landmark[12],  # Средний
            hand_landmarks.landmark[16],  # Безымянный
            hand_landmarks.landmark[20],  # Мизинец
        ]

        # Вычисляем среднее расстояние от кончиков пальцев до запястья
        distances = []
        for fingertip in fingertips:
            dist = self._calculate_distance(
                (fingertip.x, fingertip.y),
                (wrist.x, wrist.y)
            )
            distances.append(dist)

        avg_distance = np.mean(distances)

        # Добавляем текущее расстояние в историю
        self.fingertip_history.append(avg_distance)

        # Нужно минимум 5 кадров для анализа тренда
        if len(self.fingertip_history) < 5:
            return False

        # Проверяем тренд: расстояние должно уменьшаться
        # (пальцы движутся к ладони - зовущий жест)
        history_list = list(self.fingertip_history)
        recent_avg = np.mean(history_list[-3:])  # Последние 3 кадра
        older_avg = np.mean(history_list[-6:-3])  # Предыдущие 3 кадра

        # Если разница превышает порог и расстояние уменьшается - это жест
        distance_change = older_avg - recent_avg

        return distance_change > self.movement_threshold

    def process_frame(self, frame: cv2.Mat) -> Tuple[cv2.Mat, bool]:
        """
        Обработка кадра: детекция руки и распознавание жеста.

        Args:
            frame: входной кадр из OpenCV (BGR формат)

        Returns:
            Tuple из двух элементов:
            - frame с нарисованным скелетом руки
            - is_come_here: True если обнаружен жест 'ко мне'
        """
        # MediaPipe работает с RGB, OpenCV использует BGR
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Обработка кадра через MediaPipe
        results = self.hands.process(frame_rgb)

        is_come_here = False

        # Если рука обнаружена
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Отрисовка скелета руки на кадре
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )

                # Детекция жеста 'ко мне'
                is_come_here = self._detect_beckoning_gesture(hand_landmarks)

                # Визуальная индикация жеста
                if is_come_here:
                    # Зеленый текст "COME HERE!" в верхней части кадра
                    cv2.putText(
                        frame,
                        "COME HERE!",
                        (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.5,
                        (0, 255, 0),
                        3
                    )
        else:
            # Если рука не обнаружена, очищаем историю
            self.fingertip_history.clear()

        return frame, is_come_here

    def reset_history(self):
        """Сброс истории движений (полезно при смене сцены)."""
        self.fingertip_history.clear()

    def __del__(self):
        """Освобождение ресурсов при удалении объекта."""
        if hasattr(self, 'hands'):
            self.hands.close()
