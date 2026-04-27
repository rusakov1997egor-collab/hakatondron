from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Tuple
from enum import Enum
import asyncio
import uuid

app = FastAPI(
    title="Hybrid Logistics API",
    description="API для симуляции доставки грузовик-дрон (Виртуальный город)",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ENUMS ---
class DeliveryType(str, Enum):
    WINDOW = "window"
    PORCH = "porch"

# --- REST API МОДЕЛИ (Бизнес-логика) ---
class OrderItem(BaseModel):
    name: str
    weight_kg: float = Field(..., description="Вес товара в кг")

class OrderRequest(BaseModel):
    client_id: str
    x: float = Field(..., description="Координата X в виртуальном городе (например, от 0 до 100)")
    y: float = Field(..., description="Координата Y в виртуальном городе (например, от 0 до 100)")
    items: List[OrderItem]
    delivery_type: DeliveryType
    is_urgent: bool = False

class OrderResponse(BaseModel):
    order_id: str
    status: str
    estimated_delivery_time: int
    assigned_to: str

# --- WEBSOCKET МОДЕЛИ (Телеметрия от алгоритмистов) ---
class TruckState(BaseModel):
    x: float
    y: float
    status: str

class DroneState(BaseModel):
    id: str
    x: float
    y: float
    status: str
    battery: int
    eta: float
    payload_kg: float

class FullSimulationState(BaseModel):
    truck: TruckState
    drones: List[DroneState]
    full_path: List[Tuple[float, float]]

# --- ГЛОБАЛЬНОЕ СОСТОЯНИЕ ---
current_simulation_state = {
    "truck": {"x": 12.5, "y": 5.2, "status": "moving"},
    "drones": [
        {
            "id": "drone_1",
            "x": 15.0,
            "y": 8.0,
            "status": "returning",
            "battery": 42,
            "eta": 8.5,
            "payload_kg": 0.0
        }
    ],
    "full_path": [[0.0, 0.0], [12.5, 5.2], [20.0, 0.0], [20.0, 30.0]]
}

# --- REST ЭНДПОИНТЫ ---
@app.post("/api/orders", response_model=OrderResponse, tags=["Orders"])
async def create_order(order: OrderRequest):
    """Принимает заказ от клиента из приложения"""
    total_weight = sum(item.weight_kg for item in order.items)
    assigned = "truck" if total_weight > 2.5 else "drone"

    return OrderResponse(
        order_id=str(uuid.uuid4()),
        status="processing",
        estimated_delivery_time=15,
        assigned_to=assigned
    )

@app.post("/api/cv/gesture", tags=["Computer Vision"])
async def handle_gesture(gesture: str):
    """Экстренные прерывания от модуля камеры (MediaPipe)"""
    global current_simulation_state
    
    if gesture == "open_hand":
        current_simulation_state["drones"][0]["status"] = "EMERGENCY_ABORT"
        return {"message": "Дрон остановлен!", "status": "aborted"}
    elif gesture == "fist":
        current_simulation_state["drones"][0]["status"] = "landing"
        return {"message": "Посадка разрешена", "status": "landing"}

    return {"message": "Жест не распознан"}

# --- WEBSOCKET ЭНДПОИНТ ---
@app.websocket("/ws/telemetry")
async def drone_telemetry(websocket: WebSocket):
    """Стриминг данных для фронтенда (Дашборда оператора)"""
    await websocket.accept()
    global current_simulation_state
    
    try:
        while True:
            # Имитация жизни в симуляции 
            if current_simulation_state["drones"][0]["status"] != "EMERGENCY_ABORT":
                current_simulation_state["truck"]["x"] += 0.05
                current_simulation_state["drones"][0]["battery"] -= 1
                current_simulation_state["drones"][0]["eta"] -= 0.1
                
                # Имитация зарядки
                if current_simulation_state["drones"][0]["battery"] <= 0:
                    current_simulation_state["drones"][0]["battery"] = 100
                    current_simulation_state["drones"][0]["eta"] = 15.0
            
            state = FullSimulationState(**current_simulation_state)
            await websocket.send_json(state.model_dump())
            await asyncio.sleep(0.1) 
            
    except WebSocketDisconnect:
        print("Dashboard disconnected")