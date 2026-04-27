import cv2
import threading
import time
from typing import Optional


class StreamReader:
    """
    Класс для стабильного чтения видеопотока (RTSP/HTTP) в отдельном потоке.
    Использует threading для предотвращения задержек при обработке кадров.
    """

    def __init__(self, stream_url: str, reconnect_delay: int = 5):
        """
        Инициализация потокового ридера.

        Args:
            stream_url: URL потока (RTSP/HTTP)
            reconnect_delay: задержка перед переподключением в секундах
        """
        self.stream_url = stream_url
        self.reconnect_delay = reconnect_delay

        # Текущий кадр и блокировка для потокобезопасности
        self.frame = None
        self.lock = threading.Lock()

        # Флаги состояния
        self.is_running = False
        self.is_connected = False

        # Поток для чтения
        self.thread = None
        self.capture = None

    def start(self):
        """Запуск потока чтения."""
        if self.is_running:
            return

        self.is_running = True
        self.thread = threading.Thread(target=self._read_stream, daemon=True)
        self.thread.start()

    def stop(self):
        """Остановка потока чтения."""
        self.is_running = False

        if self.thread is not None:
            self.thread.join(timeout=2.0)

        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def _connect(self) -> bool:
        """
        Подключение к потоку.

        Returns:
            True если подключение успешно, иначе False
        """
        try:
            self.capture = cv2.VideoCapture(self.stream_url)

            # Настройка буфера для минимизации задержки
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            if self.capture.isOpened():
                self.is_connected = True
                print(f"[StreamReader] Подключено к {self.stream_url}")
                return True
            else:
                print(f"[StreamReader] Не удалось открыть поток {self.stream_url}")
                return False

        except Exception as e:
            print(f"[StreamReader] Ошибка подключения: {e}")
            return False

    def _read_stream(self):
        """Основной цикл чтения кадров в отдельном потоке."""
        while self.is_running:
            # Подключение или переподключение
            if not self.is_connected:
                if not self._connect():
                    time.sleep(self.reconnect_delay)
                    continue

            # Чтение кадра
            ret, frame = self.capture.read()

            if ret:
                # Обновление текущего кадра потокобезопасно
                with self.lock:
                    self.frame = frame
            else:
                # Потеря соединения
                print("[StreamReader] Потеря соединения, переподключение...")
                self.is_connected = False
                if self.capture is not None:
                    self.capture.release()
                    self.capture = None
                time.sleep(self.reconnect_delay)

    def read(self) -> Optional[cv2.Mat]:
        """
        Получение последнего кадра.

        Returns:
            Последний прочитанный кадр или None если кадр недоступен
        """
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def is_available(self) -> bool:
        """
        Проверка доступности кадров.

        Returns:
            True если есть доступные кадры
        """
        with self.lock:
            return self.frame is not None
