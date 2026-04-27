import time
import json
import math

class DronePhysicsSimulator:
    def __init__(self, drone_id="alpha-1"):
        self.drone_id = drone_id
        self.base_weight_kg = 2.0
        self.power_constant_w_kg = 170
        self.battery_voltage_v = 22.2
        self.battery_capacity_ah = 10.0
        self.dod = 0.8
        
        self.state = "IDLE"
        self.payload_kg = 0.0
        self.battery_percent = 100.0
        
        # --- НОВЫЙ БЛОК: Координаты и скорость ---
        # Стартуем из какой-то точки (например, центр Москвы)
        self.current_lat = 55.751244
        self.current_lng = 37.618423
        
        # Цель - куда летим
        self.target_lat = 55.755814
        self.target_lng = 37.617635
        
        # Скорость изменения градусов (очень грубо для симуляции)
        self.speed_deg_per_tick = 0.0005 

    def calculate_auw(self):
        return self.base_weight_kg + self.payload_kg

    def calculate_aad(self):
        if self.state == "IDLE":
            return 0.2
        return (self.calculate_auw() * self.power_constant_w_kg) / self.battery_voltage_v

    def get_estimated_flight_time_minutes(self):
        aad = self.calculate_aad()
        if aad == 0:
            return 999
        current_usable_ah = (self.battery_percent / 100.0) * self.battery_capacity_ah * self.dod
        return round((current_usable_ah / aad) * 60, 2)

    def update_battery(self, dt_seconds=1):
        aad = self.calculate_aad()
        ah_consumed = aad * (dt_seconds / 3600.0)
        percent_consumed = (ah_consumed / self.battery_capacity_ah) * 100
        self.battery_percent -= percent_consumed
        if self.battery_percent < 0:
            self.battery_percent = 0

    # --- НОВЫЙ БЛОК: Логика движения ---
    def move_towards_target(self):
        """Перемещает дрона к цели с помощью векторов"""
        if self.state not in ["CRUISE", "RETURN"]:
            return # Двигаемся только если летим
            
        # Вектор направления D
        d_lat = self.target_lat - self.current_lat
        d_lng = self.target_lng - self.current_lng
        
        # Расстояние (длина вектора)
        distance = math.sqrt(d_lat**2 + d_lng**2)
        
        # Если расстояние меньше шага скорости - мы прилетели
        if distance < self.speed_deg_per_tick:
            self.current_lat = self.target_lat
            self.current_lng = self.target_lng
            self.state = "HOVER" # Прилетели, зависли у окна
            return
            
        # Нормализуем вектор и умножаем на скорость
        step_lat = (d_lat / distance) * self.speed_deg_per_tick
        step_lng = (d_lng / distance) * self.speed_deg_per_tick
        
        # Обновляем координаты
        self.current_lat += step_lat
        self.current_lng += step_lng

    # --- НОВЫЙ БЛОК: Генерация JSON ---
    def get_telemetry_json(self):
        """Собирает все данные в словарь и переводит в JSON строку"""
        data = {
            "drone_id": self.drone_id,
            "state": self.state,
            "coordinates": {
                "lat": round(self.current_lat, 6),
                "lng": round(self.current_lng, 6)
            },
            "battery": {
                "percent": round(self.battery_percent, 2),
                "amp_draw": round(self.calculate_aad(), 2),
                "est_time_min": self.get_estimated_flight_time_minutes()
            },
            "payload_kg": self.payload_kg
        }
        # json.dumps превращает словарь Python в правильную JSON-строку
        return json.dumps(data)

if __name__ == "__main__":
    drone = DronePhysicsSimulator()
    
    # Даем дрону посылку и отправляем в полет
    drone.state = "CRUISE"
    drone.payload_kg = 2.5
    
    try:
        while drone.battery_percent > 0:
            drone.update_battery(dt_seconds=60)
            drone.move_towards_target() # Двигаем дрона
            
            # Выводим JSON в консоль
            print(drone.get_telemetry_json())
            
            # Если дрон прилетел к цели и завис, сбрасываем груз
            if drone.state == "HOVER" and drone.payload_kg > 0:
                # В реальном проекте этот сброс произойдет по команде от модуля CV (по жесту руки)
                drone.payload_kg = 0.0 
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nСимуляция прервана.")