import math
import heapq
from typing import List, Tuple, Optional

class NavigationGrid:
    """Сетка для поиска пути с идеальным обходом препятствий и сглаживанием"""

    def __init__(self, width: int = 200, height: int = 200, cell_size: int = 2):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_width = int(width / cell_size) + 1
        self.grid_height = int(height / cell_size) + 1
        self.obstacles = set()

    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        gx = int(x / self.cell_size)
        gy = int(y / self.cell_size)
        return (max(0, min(gx, self.grid_width - 1)), max(0, min(gy, self.grid_height - 1)))

    def grid_to_world(self, gx: int, gy: int) -> Tuple[float, float]:
        return (gx * self.cell_size + self.cell_size / 2, gy * self.cell_size + self.cell_size / 2)

    def add_obstacle(self, x: float, y: float, w_pixels: float, h_pixels: float, rot: float = 0, safety_margin: float = 1.0):
        w_u = w_pixels / 4.0
        h_u = h_pixels / 4.0
        
        bw = max(w_u, h_u) if rot != 0 else w_u
        bh = max(w_u, h_u) if rot != 0 else h_u

        # Считаем границы
        x1 = max(0, x - (bw / 2) - safety_margin)
        y1 = max(0, y - (bh / 2) - safety_margin)
        x2 = min(self.width, x + (bw / 2) + safety_margin)
        y2 = min(self.height, y + (bh / 2) + safety_margin)

        # ИДЕАЛЬНАЯ РАСТЕРИЗАЦИЯ: Округляем так, чтобы хитбоксы не кровоточили на соседние клетки
        gx1 = int(math.ceil(x1 / self.cell_size))
        gy1 = int(math.ceil(y1 / self.cell_size))
        gx2 = int(math.floor(x2 / self.cell_size))
        gy2 = int(math.floor(y2 / self.cell_size))

        for gx in range(gx1, gx2 + 1):
            for gy in range(gy1, gy2 + 1):
                if 0 <= gx < self.grid_width and 0 <= gy < self.grid_height:
                    self.obstacles.add((gx, gy))

    def is_line_clear(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> bool:
        """Raycasting: Проверяет, есть ли прямая видимость между двумя точками"""
        dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        if dist == 0: return True
        
        steps = int(dist / self.cell_size) * 2 + 1
        for i in range(1, steps): # Игнорируем саму точку старта и финиша
            t = i / steps
            x = p1[0] + (p2[0] - p1[0]) * t
            y = p1[1] + (p2[1] - p1[1]) * t
            gx, gy = self.world_to_grid(x, y)
            if (gx, gy) in self.obstacles:
                return False
        return True

    def get_path(self, start_world: Tuple[float, float], goal_world: Tuple[float, float]) -> List[Tuple[float, float]]:
        start = self.world_to_grid(*start_world)
        goal = self.world_to_grid(*goal_world)

        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        IGNORE_RADIUS_SQ = 12 ** 2 # Зона пробития стен для финальной посадки

        while frontier:
            _, current = heapq.heappop(frontier)

            if current == goal:
                break

            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]:
                nx, ny = current[0] + dx, current[1] + dy
                
                if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                    next_node = (nx, ny)
                    
                    dist_to_goal_sq = (nx - goal[0])**2 + (ny - goal[1])**2
                    if next_node in self.obstacles and dist_to_goal_sq > IGNORE_RADIUS_SQ:
                        continue
                        
                    new_cost = cost_so_far[current] + math.hypot(dx, dy)
                    if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_cost
                        priority = new_cost + math.hypot(goal[0] - nx, goal[1] - ny)
                        heapq.heappush(frontier, (priority, next_node))
                        came_from[next_node] = current

        if goal not in came_from:
            return [goal_world]

        curr = goal
        path = []
        while curr != start:
            path.append(self.grid_to_world(*curr))
            curr = came_from[curr]
        path.reverse()
        
        if path:
            path[-1] = goal_world

        # --- МАГИЯ СГЛАЖИВАНИЯ (STRING PULLING) ---
        if len(path) > 2:
            smoothed = [path[0]]
            i = 0
            while i < len(path) - 1:
                furthest = i + 1
                # Ищем самую дальнюю точку, которую видно по прямой
                for j in range(len(path) - 1, i, -1):
                    if self.is_line_clear(path[i], path[j]):
                        furthest = j
                        break
                smoothed.append(path[furthest])
                i = furthest
            path = smoothed

        return path


class DroneNavigator:
    def __init__(self, grid: NavigationGrid):
        self.grid = grid
        self.waypoints = []
        self.current_waypoint_index = 0
        self.speed = 2.5

    def set_destination(self, current_pos: Tuple[float, float], goal_pos: Tuple[float, float], speed: float):
        self.speed = speed
        self.waypoints = self.grid.get_path(current_pos, goal_pos)
        self.current_waypoint_index = 0

    def update_position(self, current_pos: Tuple[float, float]) -> Tuple[float, float, bool]:
        if not self.waypoints or self.current_waypoint_index >= len(self.waypoints):
            return (current_pos[0], current_pos[1], True)

        target = self.waypoints[self.current_waypoint_index]
        dx = target[0] - current_pos[0]
        dy = target[1] - current_pos[1]
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            self.current_waypoint_index += 1
            if self.current_waypoint_index >= len(self.waypoints):
                return (target[0], target[1], True)
            target = self.waypoints[self.current_waypoint_index]
            dx, dy = target[0] - current_pos[0], target[1] - current_pos[1]
            dist = math.hypot(dx, dy)

        if dist == 0:
            return (current_pos[0], current_pos[1], False)

        new_x = current_pos[0] + (dx / dist) * self.speed
        new_y = current_pos[1] + (dy / dist) * self.speed

        return (new_x, new_y, False)

    def clear(self):
        self.waypoints = []
        self.current_waypoint_index = 0