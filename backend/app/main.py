import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json

from app.models import GestureAction, OrderMessage
from app.state import state
from app.physics import DronePhysicsSimulator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = []
simulator = DronePhysicsSimulator()

@app.post("/api/gesture")
async def receive_gesture(gesture: GestureAction):
    """Эндпоинт для приема сигнала от компьютерного зрения (MediaPipe)"""
    drone = state["drone"]
    
    if gesture.action == "come_here":
        # Если дрон висел в ожидании, разрешаем посадку/сброс
        if drone["status"] == "HOVERING":
            drone["hoverTimer"] = 0 # Сбрасываем таймер ожидания
            print("[API] Жест принят: Завершение доставки!")
            
    elif gesture.action == "abort":
        # Экстренное прерывание миссии
        if drone["status"] in ["FLYING_OUT", "HOVERING"]:
            drone["status"] = "EMERGENCY_ABORT"
            drone["hoverTimer"] = 0
            # Возвращаем заказ в очередь
            if drone["targetOrder"]:
                for o in state["orders"]:
                    if o["id"] == drone["targetOrder"]["id"]:
                        o["status"] = "pending"
            print("[API] Жест принят: ЭКСТРЕННАЯ ОТМЕНА!")
            
    return {"status": "accepted"}

@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    """Связь с фронтендом (Next.js)"""
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            msg = OrderMessage.parse_raw(data)
            
            if msg.type == "NEW_ORDER" and msg.order:
                state["orders"].append(msg.order)
            elif msg.type == "TOGGLE_DELIVERY":
                state["isDeliveryActive"] = not state["isDeliveryActive"]
                
    except WebSocketDisconnect:
        clients.remove(websocket)

async def simulation_loop():
    """Главный цикл симуляции (Game Loop) - 10 FPS"""
    dt = 0.1 
    truck_speed = 10.0 # Скорость грузовика
    
    while True:
        if state["isDeliveryActive"]:
            # --- 1. Движение грузовика ---
            truck = state["truck"]
            truck["y"] += truck_speed * truck["direction"] * dt
            if truck["y"] >= 176: 
                truck["y"] = 176
                truck["direction"] = -1
            if truck["y"] <= 24: 
                truck["y"] = 24
                truck["direction"] = 1

            # --- 2. Логика и физика Дрона ---
            drone = state["drone"]
            orders = state["orders"]
            
            if drone["status"] == "DOCKED":
                drone["x"] = truck["x"]
                drone["y"] = truck["y"]
                if drone["battery"] < 100:
                    drone["battery"] = min(100.0, drone["battery"] + 2.0) # Быстрая зарядка
                
                # Поиск заказа для дрона
                pending_order = next((o for o in orders if o["status"] == "pending" and o["assignedTo"] == "drone"), None)
                if pending_order and drone["battery"] > 30:
                    drone["targetOrder"] = pending_order
                    drone["status"] = "FLYING_OUT"
                    pending_order["status"] = "in_progress"
            
            else:
                # Определение цели
                target_pos = {"x": truck["x"], "y": truck["y"]} # По умолчанию летим на грузовик
                if drone["status"] == "FLYING_OUT" and drone["targetOrder"]:
                    target_pos = {"x": drone["targetOrder"]["house"]["x"], "y": drone["targetOrder"]["house"]["y"]}
                
                # Физический тик
                is_hovering = drone["status"] == "HOVERING"
                physics_result = simulator.tick(
                    payload_weight=drone["targetOrder"]["weight"] if drone["targetOrder"] else 0.0,
                    current_battery_pct=drone["battery"],
                    flight_mode="HOVER" if is_hovering else "CRUISE",
                    target_pos=target_pos,
                    current_pos={"x": drone["x"], "y": drone["y"]},
                    dt=dt
                )
                
                # Применяем новые данные
                drone["battery"] = physics_result["battery"]
                drone["x"] = physics_result["x"]
                drone["y"] = physics_result["y"]
                drone["eta"] = physics_result["distance_to_target"] / 25.0

                # Логика смены состояний
                if physics_result["distance_to_target"] < 2.0:
                    if drone["status"] == "FLYING_OUT":
                        drone["status"] = "HOVERING"
                        drone["hoverTimer"] = 6.0 if drone["targetOrder"]["deliveryType"] == 'window' else 3.0
                    
                    elif drone["status"] in ["RETURNING", "EMERGENCY_ABORT"]:
                        drone["status"] = "DOCKED"
                        drone["targetOrder"] = None
                
                # Логика зависания (у клиента)
                if drone["status"] == "HOVERING":
                    drone["hoverTimer"] -= dt
                    if drone["hoverTimer"] <= 0:
                        # Заказ доставлен
                        if drone["targetOrder"]:
                            drone["targetOrder"]["status"] = "delivered"
                        drone["status"] = "RETURNING"
                        drone["targetOrder"] = None

        # --- 3. Рассылка стейта всем клиентам ---
        for client in clients:
            try:
                await client.send_json(state)
            except:
                pass
                
        await asyncio.sleep(dt)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulation_loop())