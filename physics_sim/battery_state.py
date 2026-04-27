import time
import json
import math

class DronePhysicsSimulator:
    def __init__(self):
        # Окружение
        self.rho = 1.225  # Плотность воздуха
        self.wind = {'x': 2.0, 'y': -1.0}  # Вектор ветра (м/с)
        
        # Параметры дрона
        self.mass_empty = 1.2    # кг
        self.payload_kg = 0.0     # Текущий груз
        self.drag_coeff = 0.45    # Cd
        self.area = 0.06          # м2
        self.max_speed = 10.0     # м/с (ограничим для стабильности)
        
        # Навигация (координаты)
        self.position = {'lat': 55.7558, 'lng': 37.6173} # Москва
        self.target = {'lat': 55.7590, 'lng': 37.6250}
        self.state = "IDLE"
        
        # Энергетика
        self.battery_capacity_wh = 100.0
        self.energy_left = 100.0  # Wh
        self.base_power_hover = 150.0  # Ватт

    @property
    def battery_percent(self):
        """Считаем процент заряда на лету для совместимости с циклом"""
        return round((self.energy_left / self.battery_capacity_wh) * 100, 2)

    def calculate_power(self):
        """Считаем мощность на основе скорости и ветра"""
        total_mass = self.mass_empty + self.payload_kg
        p_hover = self.base_power_hover * (total_mass / self.mass_empty)
        
        # Если дрон висит, считаем только p_hover
        if self.state == "HOVER" or self.state == "IDLE":
            return p_hover
        
        # Добавляем сопротивление воздуха при движении
        v_rel_x = self.max_speed - self.wind['x']
        v_rel_y = 0 - self.wind['y'] # упростим для одного направления
        v_rel_mag = math.sqrt(v_rel_x**2 + v_rel_y**2)
        
        f_drag = 0.5 * self.rho * (v_rel_mag**2) * self.drag_coeff * self.area
        p_drag = f_drag * v_rel_mag
        return p_hover + p_drag

    def update_battery(self, dt_seconds=1):
        """Обновляем заряд (старое название для совместимости)"""
        power = self.calculate_power()
        energy_consumed = (power * dt_seconds) / 3600
        
        # Штраф за низкий заряд
        efficiency = 1.0 if self.battery_percent > 20 else 0.85
        self.energy_left -= (energy_consumed / efficiency)
        self.energy_left = max(0, self.energy_left)

    def move_towards_target(self):
        """Простая логика движения к цели"""
        if self.battery_percent <= 0:
            self.state = "CRASHED"
            return

        # Имитируем сближение по координатам
        dist_lat = self.target['lat'] - self.position['lat']
        dist_lng = self.target['lng'] - self.position['lng']
        
        if abs(dist_lat) < 0.0001 and abs(dist_lng) < 0.0001:
            self.state = "HOVER" # Долетели
        else:
            self.state = "CRUISE"
            self.position['lat'] += dist_lat * 0.1 # Плавный подлет
            self.position['lng'] += dist_lng * 0.1

    def get_telemetry_json(self):
        """Тот самый JSON, который ждет фронтенд"""
        return json.dumps({
            "lat": round(self.position['lat'], 6),
            "lng": round(self.position['lng'], 6),
            "battery": self.battery_percent,
            "power_w": round(self.calculate_power(), 1),
            "state": self.state,
            "payload": self.payload_kg
        })

# --- БЛОК ТЕСТИРОВАНИЯ ---
if __name__ == "__main__":
    drone = DronePhysicsSimulator()
    drone.payload_kg = 2.5 # Тяжелая посылка
    
    print("--- Запуск симуляции (Ветер: 2.0 м/с x, -1.0 м/с y) ---")
    
    try:
        while drone.battery_percent > 0:
            drone.update_battery(dt_seconds=10) # Шаг 10 секунд для скорости
            drone.move_towards_target()
            
            print(drone.get_telemetry_json())
            
            if drone.state == "HOVER" and drone.payload_kg > 0:
                print(">>> ЦЕЛЬ ДОСТИГНУТА. СБРОС ГРУЗА.")
                drone.payload_kg = 0.0 
                # Меняем цель на базу (возврат)
                drone.target = {'lat': 55.7558, 'lng': 37.6173}
                
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nСимуляция прервана.")