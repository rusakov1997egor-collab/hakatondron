import cv2
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from gesture_reader import GestureReader


def main():
    """Тестирование распознавания жеста 'ко мне' с веб-камеры."""

    print("Инициализация веб-камеры...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ОШИБКА: Не удалось открыть веб-камеру!")
        return

    print("Инициализация GestureReader...")
    gesture_reader = GestureReader()

    print("\n" + "="*50)
    print("ТЕСТ РАСПОЗНАВАНИЯ ЖЕСТА 'ИДИ КО МНЕ'")
    print("="*50)
    print("Покажите руку в камеру и делайте зовущий жест")
    print("Нажмите 'q' для выхода")
    print("="*50 + "\n")

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("ОШИБКА: Не удалось прочитать кадр")
                break

            # Обработка кадра через GestureReader
            processed_frame, is_come_here = gesture_reader.process_frame(frame)

            # Если жест распознан - выводим в терминал
            if is_come_here:
                print("\n" + "="*50)
                print("=== ЖЕСТ РАСПОЗНАН ===")
                print("="*50 + "\n")

            # Отображение кадра
            cv2.imshow('Gesture Test - Press Q to quit', processed_frame)

            # Выход по нажатию 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nПрервано пользователем")

    finally:
        # Освобождение ресурсов
        cap.release()
        cv2.destroyAllWindows()
        print("\nТест завершен")


if __name__ == "__main__":
    main()
