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