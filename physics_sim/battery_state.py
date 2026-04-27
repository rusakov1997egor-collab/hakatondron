<<<<<<< HEAD
import math
import time

class DronePhysicsSimulator:
    def __init__(self):
        # Константы
        self.rho = 1.225
        self.drag_coeff = 0.45
        self.area = 0.06
        self.base_power_hover = 150.0 
        self.battery_capacity_wh = 100.0
        
        # Накопительные данные (состояние внутри симулятора)
        self.total_flight_time = 0.0   # в секундах
        self.total_distance = 0.0      # в метрах
        
    def tick(self, payload_weight, current_battery_pct, flight_mode, dt=0.1):
        """
        Обсчитывает один шаг времени.
        Возвращает: (новый_заряд, время_полета, пройденный_путь)
        """
        # 1. Тяга и мощность
        total_mass = 1.2 + payload_weight
        p_hover = self.base_power_hover * (total_mass / 1.2)
        
        # Скорость: 10 м/с в круизе, 0 при зависании
        speed = 10.0 if flight_mode == "CRUISE" else 0.0
        
        # Аэродинамика
        f_drag = 0.5 * self.rho * (speed**2) * self.drag_coeff * self.area
        p_drag = f_drag * speed
        total_power = p_hover + p_drag
        
        # 2. Энергопотребление
        energy_consumed_wh = (total_power * dt) / 3600
        pct_drop = (energy_consumed_wh / self.battery_capacity_wh) * 100
        new_battery_pct = max(0, current_battery_pct - pct_drop)
        
        # 3. ОДОМЕТРИЯ (Новое!)
        # Путь = Скорость * Время
        distance_step = speed * dt
        self.total_distance += distance_step
        self.total_flight_time += dt
        
        # Возвращаем обновленные данные
        return (
            round(new_battery_pct, 4), 
            round(self.total_flight_time, 2), 
            round(self.total_distance, 2)
        )

# --- ТЕСТ ДЛЯ САНЬКА ---
if __name__ == "__main__":
    sim = DronePhysicsSimulator()
    current_bat = 100.0
    
    print("Тестируем одометрию (полет 5 секунд на скорости 10 м/с)...")
    for _ in range(50): # 50 тиков по 0.1 сек = 5 секунд
        current_bat, f_time, f_dist = sim.tick(1.0, current_bat, "CRUISE")
    
    print(f"Результат: Пройдено {f_dist} метров за {f_time} секунд.")
    print(f"Остаток заряда: {current_bat}%")
=======
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
>>>>>>> a2b7340fb466840853c3f8a614590873129be31a
