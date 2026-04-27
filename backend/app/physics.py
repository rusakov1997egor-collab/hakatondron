import math

class DronePhysicsSimulator:
    def __init__(self):
        self.rho = 1.225
        self.drag_coeff = 0.45
        self.area = 0.06
        self.base_power_hover = 150.0 
        self.battery_capacity_wh = 100.0
        
        self.total_flight_time = 0.0
        self.total_distance = 0.0
        self.current_angle = 0.0

    def tick(self, payload_weight, current_battery_pct, flight_mode, target_pos, current_pos, wind_vector={'x': 0, 'y': 0}, dt=0.1):
        dx = target_pos['x'] - current_pos['x']
        dy = target_pos['y'] - current_pos['y']
        
        # Определяем угол полета
        if abs(dx) > 0.1 or abs(dy) > 0.1:
            radians = math.atan2(dy, dx)
            self.current_angle = math.degrees(radians)
        else:
            radians = math.radians(self.current_angle)

        total_mass = 1.2 + payload_weight
        p_hover = self.base_power_hover * (total_mass / 1.2)
        
        # Скорость дрона (адаптировано под сетку 200x200 Феди)
        speed = 25.0 if flight_mode == "CRUISE" else 0.0
        
        v_air_x = speed * math.cos(math.radians(self.current_angle)) - wind_vector['x']
        v_air_y = speed * math.sin(math.radians(self.current_angle)) - wind_vector['y']
        v_air_mag = math.sqrt(v_air_x**2 + v_air_y**2)
        
        f_drag = 0.5 * self.rho * (v_air_mag**2) * self.drag_coeff * self.area
        p_drag = f_drag * v_air_mag
        total_power = p_hover + p_drag
        
        drift_x = wind_vector['x'] * dt * 0.5
        drift_y = wind_vector['y'] * dt * 0.5

        energy_consumed_wh = (total_power * dt) / 3600
        pct_drop = (energy_consumed_wh / self.battery_capacity_wh) * 100
        new_battery_pct = max(0, current_battery_pct - pct_drop)
        
        self.total_distance += speed * dt
        self.total_flight_time += dt
        
        # РАССЧИТЫВАЕМ НОВЫЕ КООРДИНАТЫ ДЛЯ ФРОНТЕНДА
        new_x = current_pos['x'] + (math.cos(radians) * speed * dt)
        new_y = current_pos['y'] + (math.sin(radians) * speed * dt)
        
        return {
            "battery": round(new_battery_pct, 4),
            "x": new_x,
            "y": new_y,
            "distance_to_target": math.sqrt(dx**2 + dy**2)
        }