import time
import json
import math

class DronePhysicsSimulator:
    def __init__(self):
        # Окружение
        self.rho = 1.225
        self.wind = {'x': 2.0, 'y': -1.0} # Ветер в м/с
        
        # Параметры дрона
        self.mass_empty = 1.2
        self.payload_kg = 0.0
        self.drag_coeff = 0.45
        self.area = 0.06
        self.max_speed = 10.0 # Метров в секунду
        
        # Навигация (теперь в метрах на плоскости)
        self.position = {'x': 0.0, 'y': 0.0} # Начало координат
        self.target = {'x': 100.0, 'y': 150.0} # Цель в 180 метрах от старта
        self.state = "IDLE"
        
        # Энергетика
        self.battery_capacity_wh = 100.0
        self.energy_left = 100.0
        self.base_power_hover = 150.0

    @property
    def battery_percent(self):
        return round((self.energy_left / self.battery_capacity_wh) * 100, 2)

    def calculate_power(self):
        total_mass = self.mass_empty + self.payload_kg
        p_hover = self.base_power_hover * (total_mass / self.mass_empty)
        
        if self.state in ["HOVER", "IDLE"]:
            return p_hover
        
        # Считаем относительную скорость (движение + ветер)
        # Для простоты считаем, что дрон летит к цели на макс. скорости
        v_rel_x = self.max_speed - self.wind['x']
        v_rel_y = 0 - self.wind['y']
        v_rel_mag = math.sqrt(v_rel_x**2 + v_rel_y**2)
        
        f_drag = 0.5 * self.rho * (v_rel_mag**2) * self.drag_coeff * self.area
        p_drag = f_drag * v_rel_mag
        return p_hover + p_drag

    def update_battery(self, dt_seconds=1):
        power = self.calculate_power()
        energy_consumed = (power * dt_seconds) / 3600
        efficiency = 1.0 if self.battery_percent > 20 else 0.85
        self.energy_left -= (energy_consumed / efficiency)
        self.energy_left = max(0, self.energy_left)

    def move_towards_target(self, dt_seconds=1):
        if self.battery_percent <= 0:
            self.state = "CRASHED"
            return

        # Линейная алгебра: вектор направления к цели
        dx = self.target['x'] - self.position['x']
        dy = self.target['y'] - self.position['y']
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 1.0: # Если ближе 1 метра — долетели
            self.state = "HOVER"
        else:
            self.state = "CRUISE"
            # Двигаемся со скоростью max_speed м/с
            step = self.max_speed * dt_seconds
            self.position['x'] += (dx / distance) * step
            self.position['y'] += (dy / distance) * step

    def get_telemetry_json(self):
        return json.dumps({
            "x": round(self.position['x'], 2),
            "y": round(self.position['y'], 2),
            "battery": self.battery_percent,
            "power_w": round(self.calculate_power(), 1),
            "state": self.state,
            "payload": self.payload_kg
        })

# --- ТЕСТОВЫЙ ЗАПУСК ---
if __name__ == "__main__":
    drone = DronePhysicsSimulator()
    drone.payload_kg = 2.0
    
    print(f"Старт. Цель: {drone.target}. Ветер: {drone.wind}")
    
    try:
        while drone.battery_percent > 0:
            drone.update_battery(dt_seconds=1)