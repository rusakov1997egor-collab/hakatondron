import time
import json
import math

class DronePhysicsSimulator:
    def __init__(self):
        # Базовые константы (не меняются)
        self.rho = 1.225
        self.drag_coeff = 0.45
        self.area = 0.06
        self.base_power_hover = 150.0 # Ватт
        self.battery_capacity_wh = 100.0
        
        # Внутреннее состояние (накапливается внутри класса)
        self.total_flight_time = 0.0 # Секунды
        self.x = 0.0
        self.y = 0.0

    def tick(self, payload_weight, current_battery_pct, flight_mode, dt=0.1):
        """
        Главный метод для Артема. 
        dt=0.1, так как он вызывает это 10 раз в секунду.
        """
        # 1. Расчет мощности
        # Вес влияет на базовое потребление
        total_mass = 1.2 + payload_weight
        p_hover = self.base_power_hover * (total_mass / 1.2)
        
        # Режим полета влияет на скорость и сопротивление
        speed = 10.0 if flight_mode == "CRUISE" else 0.0
        
        # Сила сопротивления (упрощенно для тика)
        f_drag = 0.5 * self.rho * (speed**2) * self.drag_coeff * self.area
        p_drag = f_drag * speed
        
        total_power = p_hover + p_drag
        
        # 2. Расчет расхода заряда за этот "тик"
        # Энергия = Мощность * Время (в часах)
        energy_consumed_wh = (total_power * dt) / 3600
        
        # Переводим Wh расхода в проценты от общей емкости
        pct_drop = (energy_consumed_wh / self.battery_capacity_wh) * 100
        
        # 3. Обновляем состояние
        new_battery_pct = max(0, current_battery_pct - pct_drop)
        self.total_flight_time += dt
        
        # 4. Возвращаем кортеж данных для бэкенда
        return round(new_battery_pct, 4), round(self.total_flight_time, 2)

    def update_position(self, x, y):
        """Если Артему нужно будет обновлять координаты внутри класса"""
        self.x = x
        self.y = y

# --- ТЕСТОВЫЙ ЗАПУСК ---
if __name__ == "__main__":
    drone = DronePhysicsSimulator()
    drone.payload_kg = 2.0
    
    print(f"Старт. Цель: {drone.target}. Ветер: {drone.wind}")
    
    try:
        while drone.battery_percent > 0:
            drone.update_battery(dt_seconds=1)