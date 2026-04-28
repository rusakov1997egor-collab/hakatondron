from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import math
from .navigation import NavigationGrid, DroneNavigator

app = FastAPI(
    title="Hybrid Logistics API",
    description="API для симуляции доставки грузовик-дрон",
    version="1.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ПРЕПЯТСТВИЯ (ДОМА) ---
HOUSES = [
    {"x": 30, "y": 50, "width": 25, "height": 30},
    {"x": 80, "y": 60, "width": 30, "height": 25},
    {"x": 140, "y": 45, "width": 28, "height": 35},
    {"x": 50, "y": 110, "width": 22, "height": 28},
    {"x": 120, "y": 100, "width": 35, "height": 30},
    {"x": 35, "y": 150, "width": 30, "height": 25},
    {"x": 90, "y": 140, "width": 25, "height": 32},
    {"x": 155, "y": 130, "width": 28, "height": 28},
]

# --- ИНИЦИАЛИЗАЦИЯ НАВИГАЦИОННОЙ СИСТЕМЫ ---
nav_grid = NavigationGrid(width=200, height=200, cell_size=5)
for house in HOUSES:
    nav_grid.add_obstacle(house["x"], house["y"], house["width"], house["height"], safety_margin=8.0)

# --- ГЛОБАЛЬНОЕ СОСТОЯНИЕ ---
current_simulation_state = {
    "truck": {"x": 100, "y": 24, "status": "moving", "direction": 1},
    "drone": {
        "x": 100, "y": 24,
        "status": "DOCKED", # DOCKED, FLYING_OUT, HOVERING, RETURNING, EMERGENCY_ABORT
        "battery": 100,
        "eta": 0,
        "hoverTimer": 0,
        "targetOrder": None
    },
    "orders": [],
    "isDeliveryActive": False
}

class GestureRequest(BaseModel):
    action: str

@app.get("/api/houses", tags=["Map"])
async def get_houses():
    """Получение списка домов (препятствий)"""
    return {"houses": HOUSES}

@app.post("/api/gesture", tags=["Computer Vision"])
async def handle_gesture(gesture: GestureRequest):
    global current_simulation_state
    if gesture.action == "abort":
        current_simulation_state["drone"]["status"] = "EMERGENCY_ABORT"
        return {"message": "Аварийный возврат!", "status": "aborted"}
    return {"message": "Жест не распознан"}

@app.websocket("/ws/telemetry")
async def drone_telemetry(websocket: WebSocket):
    await websocket.accept()
    global current_simulation_state

    # Создаем навигатор для этой сессии
    drone_navigator = DroneNavigator(nav_grid)
    
    async def receive_commands():
        try:
            while True:
                data = await websocket.receive_json()
                if data.get("type") == "NEW_ORDER":
                    current_simulation_state["orders"].append(data["order"])
                elif data.get("type") == "TOGGLE_DELIVERY":
                    current_simulation_state["isDeliveryActive"] = not current_simulation_state["isDeliveryActive"]
        except WebSocketDisconnect:
            pass

    async def send_telemetry():
        try:
            while True:
                state = current_simulation_state
                
                if state["isDeliveryActive"]:
                    # --- 1. ФИЗИКА ГРУЗОВИКА ---
                    truck = state["truck"]
                    truck["y"] += 0.5 * truck["direction"]
                    if truck["y"] >= 176:
                        truck["y"], truck["direction"] = 176, -1
                    elif truck["y"] <= 24:
                        truck["y"], truck["direction"] = 24, 1

                    # --- 2. ЛОГИКА ДРОНА ---
                    drone = state["drone"]

                    # Если дрон на базе — ищем для него заказ
                    if drone["status"] == "DOCKED":
                        drone["x"], drone["y"] = truck["x"], truck["y"]
                        drone_navigator.clear()  # Очищаем старый маршрут

                        for order in reversed(state["orders"]):
                            if order["status"] == "pending" and order["assignedTo"] == "drone":
                                order["status"] = "in_progress"
                                drone["targetOrder"] = order
                                drone["status"] = "FLYING_OUT"

                                # РАСЧЕТ МАРШРУТА (один раз!)
                                target = order["house"]
                                start_pos = (drone["x"], drone["y"])
                                goal_pos = (target["x"], target["y"])
                                drone_navigator.set_destination(start_pos, goal_pos, speed=2.5)
                                break

                    # Полет к клиенту
                    elif drone["status"] == "FLYING_OUT":
                        current_pos = (drone["x"], drone["y"])
                        new_x, new_y, reached = drone_navigator.update_position(current_pos)

                        drone["x"], drone["y"] = new_x, new_y

                        if reached:
                            target = drone["targetOrder"]["house"]
                            drone["x"], drone["y"] = target["x"], target["y"]
                            drone["status"] = "HOVERING"
                            # Если окно - ждем 5 сек (50 тиков), если крыльцо - бросаем сразу (0 тиков)
                            drone["hoverTimer"] = 50 if drone["targetOrder"]["deliveryType"] == "window" else 0

                    # Зависание у окна / сброс у подъезда
                    elif drone["status"] == "HOVERING":
                        if drone["hoverTimer"] > 0:
                            drone["hoverTimer"] -= 1
                        else:
                            drone["targetOrder"]["status"] = "delivered"
                            drone["status"] = "RETURNING"

                            # РАСЧЕТ МАРШРУТА ВОЗВРАТА (один раз!)
                            start_pos = (drone["x"], drone["y"])
                            goal_pos = (truck["x"], truck["y"])
                            drone_navigator.set_destination(start_pos, goal_pos, speed=3.5)

                    # Возврат на грузовик (или аварийный возврат)
                    elif drone["status"] in ["RETURNING", "EMERGENCY_ABORT"]:
                        # При аварийном возврате пересчитываем маршрут, если еще не сделали
                        if drone["status"] == "EMERGENCY_ABORT" and not drone_navigator.waypoints:
                            start_pos = (drone["x"], drone["y"])
                            goal_pos = (truck["x"], truck["y"])
                            drone_navigator.set_destination(start_pos, goal_pos, speed=3.5)

                        current_pos = (drone["x"], drone["y"])
                        new_x, new_y, reached = drone_navigator.update_position(current_pos)

                        drone["x"], drone["y"] = new_x, new_y

                        # Проверка близости к грузовику
                        dx, dy = truck["x"] - drone["x"], truck["y"] - drone["y"]
                        dist = math.hypot(dx, dy)

                        if dist < 3.0 or reached:
                            drone["status"] = "DOCKED"
                            drone["x"], drone["y"] = truck["x"], truck["y"]
                            if drone["targetOrder"] and drone["targetOrder"]["status"] != "delivered":
                                drone["targetOrder"]["status"] = "pending"  # Возвращаем в очередь при аварии
                            drone["targetOrder"] = None
                            drone_navigator.clear()
                    
                    # --- БАТАРЕЯ ---
                    if drone["status"] not in ["DOCKED"]:
                        drone["battery"] = max(0, drone["battery"] - 0.1)
                    else:
                        drone["battery"] = min(100, drone["battery"] + 0.3)

                await websocket.send_json(state)
                await asyncio.sleep(0.1) # 10 FPS
                
        except WebSocketDisconnect:
            pass

    await asyncio.gather(receive_commands(), send_telemetry())