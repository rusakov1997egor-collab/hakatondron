from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import math
from .navigation import NavigationGrid, DroneNavigator

app = FastAPI(
    title="Hybrid Logistics API",
    description="API для симуляции доставки грузовик-дрон",
    version="1.4.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ПРЕПЯТСТВИЯ (ПОЛНАЯ КАРТА ИЗ ФРОНТЕНДА 45 ДОМОВ) ---
HOUSES = [
    {'x': 30, 'y': 40, 'width': 90, 'height': 30, 'rot': 0}, {'x': 15, 'y': 55, 'width': 30, 'height': 60, 'rot': 0},
    {'x': 40, 'y': 85, 'width': 100, 'height': 30, 'rot': 0}, {'x': 40, 'y': 65, 'width': 30, 'height': 50, 'rot': 0},
    {'x': 15, 'y': 85, 'width': 30, 'height': 40, 'rot': 0}, {'x': 20, 'y': 70, 'width': 30, 'height': 30, 'rot': 45},
    {'x': 45, 'y': 135, 'width': 120, 'height': 30, 'rot': 15}, {'x': 35, 'y': 120, 'width': 30, 'height': 70, 'rot': 15},
    {'x': 15, 'y': 140, 'width': 30, 'height': 50, 'rot': 15}, {'x': 65, 'y': 120, 'width': 30, 'height': 40, 'rot': 15},
    {'x': 25, 'y': 155, 'width': 50, 'height': 30, 'rot': 15}, {'x': 45, 'y': 185, 'width': 100, 'height': 30, 'rot': 0},
    {'x': 45, 'y': 165, 'width': 100, 'height': 30, 'rot': 0}, {'x': 15, 'y': 175, 'width': 30, 'height': 70, 'rot': 0},
    {'x': 10, 'y': 190, 'width': 40, 'height': 40, 'rot': 0}, {'x': 10, 'y': 160, 'width': 40, 'height': 40, 'rot': 0},
    {'x': 70, 'y': 175, 'width': 30, 'height': 50, 'rot': 0}, {'x': 86, 'y': 60, 'width': 25, 'height': 120, 'rot': 0},
    {'x': 86, 'y': 100, 'width': 25, 'height': 150, 'rot': 0}, {'x': 86, 'y': 140, 'width': 25, 'height': 120, 'rot': 0},
    {'x': 8, 'y': 110, 'width': 25, 'height': 100, 'rot': 0}, {'x': 25, 'y': 110, 'width': 60, 'height': 25, 'rot': 0},
    {'x': 170, 'y': 40, 'width': 90, 'height': 30, 'rot': 0}, {'x': 185, 'y': 55, 'width': 30, 'height': 60, 'rot': 0},
    {'x': 165, 'y': 105, 'width': 80, 'height': 30, 'rot': 0}, {'x': 165, 'y': 75, 'width': 80, 'height': 30, 'rot': 0},
    {'x': 190, 'y': 90, 'width': 30, 'height': 50, 'rot': 0}, {'x': 135, 'y': 90, 'width': 30, 'height': 70, 'rot': 0},
    {'x': 155, 'y': 140, 'width': 100, 'height': 30, 'rot': -10}, {'x': 165, 'y': 125, 'width': 30, 'height': 50, 'rot': -10},
    {'x': 140, 'y': 155, 'width': 40, 'height': 40, 'rot': -10}, {'x': 185, 'y': 155, 'width': 30, 'height': 50, 'rot': -10},
    {'x': 145, 'y': 185, 'width': 80, 'height': 30, 'rot': 0}, {'x': 145, 'y': 165, 'width': 80, 'height': 30, 'rot': 0},
    {'x': 175, 'y': 175, 'width': 30, 'height': 50, 'rot': 0}, {'x': 125, 'y': 175, 'width': 30, 'height': 40, 'rot': 0},
    {'x': 190, 'y': 185, 'width': 30, 'height': 40, 'rot': 0}, {'x': 190, 'y': 165, 'width': 30, 'height': 40, 'rot': 0},
    {'x': 180, 'y': 70, 'width': 40, 'height': 40, 'rot': -45}, {'x': 130, 'y': 95, 'width': 30, 'height': 60, 'rot': 0},
    {'x': 114, 'y': 60, 'width': 25, 'height': 120, 'rot': 0}, {'x': 114, 'y': 100, 'width': 25, 'height': 150, 'rot': 0},
    {'x': 114, 'y': 140, 'width': 25, 'height': 120, 'rot': 0}, {'x': 195, 'y': 110, 'width': 25, 'height': 100, 'rot': 0},
    {'x': 175, 'y': 110, 'width': 60, 'height': 25, 'rot': 0}
]

# Уменьшаем cell_size для более точной навигации
nav_grid = NavigationGrid(width=200, height=200, cell_size=2)
for house in HOUSES:
    # Безопасное извлечение ключей (w/width, h/height), чтобы не было ошибок
    w = house.get("width", house.get("w", 20))
    h = house.get("height", house.get("h", 20))
    rot = house.get("rot", 0)
    
    # Добавляем препятствие с отступом 2.0
    nav_grid.add_obstacle(house["x"], house["y"], w, h, rot=rot, safety_margin=1.0)

current_simulation_state = {
    "truck": {"x": 100, "y": 24, "status": "moving", "direction": 1},
    "drone": {
        "x": 100, "y": 24, "status": "DOCKED", "battery": 100, 
        "eta": 0, "hoverTimer": 0, "targetOrder": None,
        # ДОБАВЛЯЕМ ТВОИ ПОЛЯ:
        "angle": 0,
        "time": 0,
        "distance": 0,
        "remaining_time": 0
    },
    "orders": [], "isDeliveryActive": False
}

class GestureRequest(BaseModel):
    action: str

@app.post("/api/gesture")
async def handle_gesture(gesture: GestureRequest):
    global current_simulation_state
    if gesture.action == "abort":
        current_simulation_state["drone"]["status"] = "EMERGENCY_ABORT"
        return {"status": "aborted"}
    return {"status": "ok"}

@app.websocket("/ws/telemetry")
async def drone_telemetry(websocket: WebSocket):
    await websocket.accept()
    global current_simulation_state
    drone_navigator = DroneNavigator(nav_grid)
    
    async def receive_commands():
        try:
            while True:
                data = await websocket.receive_json()
                if data.get("type") == "NEW_ORDER": current_simulation_state["orders"].append(data["order"])
                elif data.get("type") == "TOGGLE_DELIVERY": current_simulation_state["isDeliveryActive"] = not current_simulation_state["isDeliveryActive"]
        except WebSocketDisconnect: pass

    async def send_telemetry():
        try:
            while True:
                state = current_simulation_state
                if state["isDeliveryActive"]:
                    truck, drone = state["truck"], state["drone"]
                    
                    # --- ФИЗИКА ГРУЗОВИКА И ЛОГИКА ПВЗ ---
                    truck["y"] += 0.5 * truck["direction"]

                    # Доехали до ПВЗ (Верхняя точка)
                    if truck["y"] >= 176: 
                        truck["y"], truck["direction"] = 176, -1
                        
                        # ЛОГИКА РАЗГРУЗКИ:
                        # Проходим по всем заказам и завершаем те, что тяжелее 2.5 кг
                        for order in state["orders"]:
                            if order["weight"] > 2.5 and order["status"] == "pending":
                                order["status"] = "delivered"
                                # Можно добавить принт в консоль для отладки
                                print(f"Грузовик доставил тяжелый заказ {order['id']} в ПВЗ")

                    # Вернулись на Склад (Нижняя точка)
                    elif truck["y"] <= 24: 
                        truck["y"], truck["direction"] = 24, 1
                        # Тут можно добавить логику «загрузки» новых заказов со склада, 
                        # если вы решите это реализовывать. Пока просто едем дальше.

                    # Сохраняем позицию ДО хода для расчета физики
                    old_x, old_y = drone["x"], drone["y"]

                    # --- ЛОГИКА СОСТОЯНИЙ ДРОНА ---
                    if drone["status"] == "DOCKED":
                        drone["x"], drone["y"] = truck["x"], truck["y"]
                        drone["angle"], drone["time"], drone["distance"], drone["remaining_time"] = 0, 0, 0, 0
                        drone_navigator.clear()
                        
                        for order in reversed(state["orders"]):
                            if order["status"] == "pending" and order["assignedTo"] == "drone":
                                order["status"], drone["targetOrder"], drone["status"] = "in_progress", order, "FLYING_OUT"
                                drone_navigator.set_destination((drone["x"], drone["y"]), (order["house"]["x"], order["house"]["y"]), speed=2.5)
                                break

                    elif drone["status"] in ["FLYING_OUT", "RETURNING", "EMERGENCY_ABORT"]:
                        # Движение
                        drone["x"], drone["y"], reached = drone_navigator.update_position((drone["x"], drone["y"]))
                        
                        # ФИЗИЧЕСКИЕ РАСЧЕТЫ (Твоя часть)
                        step_dist = math.hypot(drone["x"] - old_x, drone["y"] - old_y)
                        drone["distance"] += step_dist
                        drone["time"] += 0.1
                        if step_dist > 0.01:
                            drone["angle"] = math.degrees(math.atan2(drone["y"] - old_y, drone["x"] - old_x))

                        # Проверки достижение цели
                        if reached:
                            if drone["status"] == "FLYING_OUT":
                                drone["x"], drone["y"] = drone["targetOrder"]["house"]["x"], drone["targetOrder"]["house"]["y"]
                                drone["status"] = "HOVERING"
                                drone["hoverTimer"] = 50 if drone["targetOrder"]["deliveryType"] == "window" else 0
                            else: # Вернулся на грузовик
                                drone["status"], drone["x"], drone["y"] = "DOCKED", truck["x"], truck["y"]
                                if drone["targetOrder"] and drone["targetOrder"]["status"] != "delivered":
                                    drone["targetOrder"]["status"] = "pending"
                                drone["targetOrder"] = None
                                drone_navigator.clear()

                    elif drone["status"] == "HOVERING":
                        if drone["hoverTimer"] > 0: 
                            drone["hoverTimer"] -= 1
                        else:
                            drone["targetOrder"]["status"], drone["status"] = "delivered", "RETURNING"
                            drone_navigator.set_destination((drone["x"], drone["y"]), (truck["x"], truck["y"]), speed=3.5)

                    # --- ЭНЕРГОПОТРЕБЛЕНИЕ И ПРОГНОЗ ---
                    if drone["status"] != "DOCKED":
                        consumption = 0.2 # Базовый расход
                        drone["battery"] = max(0, drone["battery"] - (consumption * 0.1))
                        drone["remaining_time"] = round((drone["battery"] / consumption) / 60, 1)
                    else:
                        drone["battery"] = min(100, drone["battery"] + 0.3)
                        drone["remaining_time"] = 0

                    # Умное слежение за грузовиком при возврате
                    if drone["status"] in ["RETURNING", "EMERGENCY_ABORT"] and drone_navigator.waypoints:
                        end_x, end_y = drone_navigator.waypoints[-1]
                        if math.hypot(truck["x"] - end_x, truck["y"] - end_y) > 5.0:
                            drone_navigator.set_destination((drone["x"], drone["y"]), (truck["x"], truck["y"]), speed=3.5)

                await websocket.send_json(state)
                await asyncio.sleep(0.1)
        except WebSocketDisconnect: pass

    await asyncio.gather(receive_commands(), send_telemetry())