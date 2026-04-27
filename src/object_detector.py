from ultralytics import YOLO
import cv2
from typing import Tuple, List


class ObjectDetector:
    """
    Класс-обертка для детекции объектов с помощью YOLOv8.
    Используется для обнаружения помех (птицы, дроны, люди) в видеопотоке.
    """

    # Классы объектов, которые считаются помехами
    # Можно легко изменить этот список для добавления/удаления классов
    OBSTACLE_CLASSES = [
        'bird',      # Птицы - основная помеха
        'airplane',  # Самолеты - имитация других дронов
        'person',    # Люди - чтобы избежать столкновения
        # Дополнительные классы, которые можно добавить:
        # 'kite',    # Воздушные змеи
        # 'car',     # Машины на земле
        # 'truck',   # Грузовики
    ]

    def __init__(self, model_path: str = 'yolov8n.pt', confidence: float = 0.5):
        """
        Инициализация детектора объектов.

        Args:
            model_path: путь к модели YOLO (по умолчанию yolov8n.pt - легковесная версия)
            confidence: минимальный порог уверенности для детекции (0.0 - 1.0)
        """
        print(f"[ObjectDetector] Загрузка модели {model_path}...")

        # Загрузка модели YOLOv8
        self.model = YOLO(model_path)
        self.confidence = confidence

        print(f"[ObjectDetector] Модель загружена. Отслеживаемые классы: {self.OBSTACLE_CLASSES}")

    def process_frame(self, frame: cv2.Mat) -> Tuple[cv2.Mat, List[str]]:
        """
        Обработка кадра: детекция объектов и отрисовка bounding boxes.

        Args:
            frame: входной кадр из OpenCV

        Returns:
            Tuple из двух элементов:
            - frame с нарисованными рамками вокруг объектов
            - список названий обнаруженных объектов-помех
        """
        # Запуск инференса на кадре
        # verbose=False отключает вывод в консоль при каждом кадре
        results = self.model(frame, conf=self.confidence, verbose=False)

        # Список обнаруженных помех
        detected_obstacles = []

        # Обработка результатов (обычно один результат для одного кадра)
        for result in results:
            # Получение информации о детекциях
            boxes = result.boxes  # Bounding boxes
            names = result.names  # Словарь {class_id: class_name}

            # Проход по всем найденным объектам
            for box in boxes:
                # Получение класса объекта
                class_id = int(box.cls[0])
                class_name = names[class_id]
                confidence = float(box.conf[0])

                # Проверка, является ли объект помехой
                if class_name in self.OBSTACLE_CLASSES:
                    detected_obstacles.append(class_name)

                    # Получение координат bounding box
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # Отрисовка рамки (красный цвет для помех)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

                    # Отрисовка текста с названием класса и уверенностью
                    label = f"{class_name} {confidence:.2f}"

                    # Фон для текста (для лучшей читаемости)
                    (text_width, text_height), _ = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                    )
                    cv2.rectangle(
                        frame,
                        (x1, y1 - text_height - 10),
                        (x1 + text_width, y1),
                        (0, 0, 255),
                        -1
                    )

                    # Текст поверх фона
                    cv2.putText(
                        frame,
                        label,
                        (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2
                    )

        return frame, detected_obstacles

    def get_obstacle_classes(self) -> List[str]:
        """
        Получение списка отслеживаемых классов помех.

        Returns:
            Список названий классов
        """
        return self.OBSTACLE_CLASSES.copy()
