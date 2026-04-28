import math
import heapq
from typing import List, Tuple, Optional, Dict

class NavigationGrid:
    """Сетка для поиска пути с учетом препятствий"""

    def __init__(self, width: int = 200, height: int = 200, cell_size: int = 5):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_width = width // cell_size
        self.grid_height = height // cell_size
        self.obstacles = set()

    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """Конвертация мировых координат в координаты сетки"""
        gx = int(x / self.cell_size)
        gy = int(y / self.cell_size)
        return (
            max(0, min(gx, self.grid_width - 1)),
            max(0, min(gy, self.grid_height - 1))
        )

    def grid_to_world(self, gx: int, gy: int) -> Tuple[float, float]:
        """Конвертация координат сетки в мировые координаты"""
        return (gx * self.cell_size + self.cell_size / 2,
                gy * self.cell_size + self.cell_size / 2)

    def add_obstacle(self, x: float, y: float, width: float, height: float, safety_margin: float = 8.0):
        """Добавление препятствия с безопасным радиусом"""
        x1 = max(0, x - safety_margin)
        y1 = max(0, y - safety_margin)
        x2 = min(self.width, x + width + safety_margin)
        y2 = min(self.height, y + height + safety_margin)

        gx1, gy1 = self.world_to_grid(x1, y1)
        gx2, gy2 = self.world_to_grid(x2, y2)

        for gx in range(gx1, gx2 + 1):
            for gy in range(gy1, gy2 + 1):
                self.obstacles.add((gx, gy))

    def is_walkable(self, gx: int, gy: int) -> bool:
        """Проверка, можно ли пройти через клетку"""
        if gx < 0 or gx >= self.grid_width or gy < 0 or gy >= self.grid_height:
            return False
        return (gx, gy) not in self.obstacles

    def get_neighbors(self, gx: int, gy: int) -> List[Tuple[int, int, float]]:
        """Получение соседних проходимых клеток с весами"""
        neighbors = []
        # 8 направлений: вверх, вниз, влево, вправо + диагонали
        directions = [
            (0, 1, 1.0), (0, -1, 1.0), (1, 0, 1.0), (-1, 0, 1.0),  # прямые
            (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)  # диагонали
        ]

        for dx, dy, cost in directions:
            nx, ny = gx + dx, gy + dy
            if self.is_walkable(nx, ny):
                neighbors.append((nx, ny, cost))

        return neighbors

    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Эвристика для A* (диагональное расстояние)"""
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return (dx + dy) + (1.414 - 2) * min(dx, dy)

    def find_path(self, start: Tuple[float, float], goal: Tuple[float, float]) -> Optional[List[Tuple[float, float]]]:
        """A* поиск пути от start до goal в мировых координатах"""
        start_grid = self.world_to_grid(start[0], start[1])
        goal_grid = self.world_to_grid(goal[0], goal[1])

        if not self.is_walkable(*start_grid) or not self.is_walkable(*goal_grid):
            return None

        # A* алгоритм
        open_set = []
        heapq.heappush(open_set, (0, start_grid))
        came_from = {}
        g_score = {start_grid: 0}
        f_score = {start_grid: self.heuristic(start_grid, goal_grid)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal_grid:
                # Восстановление пути
                path = []
                while current in came_from:
                    wx, wy = self.grid_to_world(current[0], current[1])
                    path.append((wx, wy))
                    current = came_from[current]
                path.reverse()

                # Добавляем финальную точку
                path.append(goal)

                # Упрощение пути (удаление лишних точек на прямых линиях)
                return self.simplify_path(path)

            for nx, ny, move_cost in self.get_neighbors(current[0], current[1]):
                neighbor = (nx, ny)
                tentative_g = g_score[current] + move_cost

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal_grid)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None

    def simplify_path(self, path: List[Tuple[float, float]], tolerance: float = 0.5) -> List[Tuple[float, float]]:
        """Упрощение пути методом Ramer-Douglas-Peucker"""
        if len(path) < 3:
            return path

        def perpendicular_distance(point: Tuple[float, float], line_start: Tuple[float, float], line_end: Tuple[float, float]) -> float:
            """Расстояние от точки до линии"""
            x0, y0 = point
            x1, y1 = line_start
            x2, y2 = line_end

            dx = x2 - x1
            dy = y2 - y1

            if dx == 0 and dy == 0:
                return math.hypot(x0 - x1, y0 - y1)

            t = max(0, min(1, ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)))
            proj_x = x1 + t * dx
            proj_y = y1 + t * dy

            return math.hypot(x0 - proj_x, y0 - proj_y)

        def rdp(points: List[Tuple[float, float]], epsilon: float) -> List[Tuple[float, float]]:
            """Рекурсивный алгоритм упрощения"""
            if len(points) < 3:
                return points

            dmax = 0
            index = 0

            for i in range(1, len(points) - 1):
                d = perpendicular_distance(points[i], points[0], points[-1])
                if d > dmax:
                    index = i
                    dmax = d

            if dmax > epsilon:
                left = rdp(points[:index + 1], epsilon)
                right = rdp(points[index:], epsilon)
                return left[:-1] + right
            else:
                return [points[0], points[-1]]

        return rdp(path, tolerance)


class DroneNavigator:
    """Навигатор дрона с предрасчетом маршрута"""

    def __init__(self, grid: NavigationGrid):
        self.grid = grid
        self.waypoints: List[Tuple[float, float]] = []
        self.current_waypoint_index = 0
        self.speed = 2.5

    def set_destination(self, start: Tuple[float, float], goal: Tuple[float, float], speed: float = 2.5) -> bool:
        """Установка цели и расчет маршрута (вызывается ОДИН раз)"""
        self.speed = speed
        path = self.grid.find_path(start, goal)

        if path is None:
            # Если путь не найден, летим по прямой (fallback)
            self.waypoints = [goal]
            self.current_waypoint_index = 0
            return False

        self.waypoints = path
        self.current_waypoint_index = 0
        return True

    def update_position(self, current_pos: Tuple[float, float]) -> Tuple[float, float, bool]:
        """
        Обновление позиции дрона (вызывается каждый тик)
        Возвращает: (new_x, new_y, reached_destination)
        """
        if not self.waypoints or self.current_waypoint_index >= len(self.waypoints):
            return (current_pos[0], current_pos[1], True)

        target = self.waypoints[self.current_waypoint_index]
        dx = target[0] - current_pos[0]
        dy = target[1] - current_pos[1]
        dist = math.hypot(dx, dy)

        # Достигли текущей waypoint
        if dist < self.speed:
            self.current_waypoint_index += 1

            # Достигли финальной точки
            if self.current_waypoint_index >= len(self.waypoints):
                return (target[0], target[1], True)

            # Переходим к следующей waypoint
            return self.update_position(target)

        # Движемся к текущей waypoint
        new_x = current_pos[0] + (dx / dist) * self.speed
        new_y = current_pos[1] + (dy / dist) * self.speed

        return (new_x, new_y, False)

    def get_current_target(self) -> Optional[Tuple[float, float]]:
        """Получение текущей целевой точки"""
        if self.waypoints and self.current_waypoint_index < len(self.waypoints):
            return self.waypoints[self.current_waypoint_index]
        return None

    def clear(self):
        """Очистка маршрута"""
        self.waypoints = []
        self.current_waypoint_index = 0
