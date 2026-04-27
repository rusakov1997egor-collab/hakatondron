# Глобальное состояние системы
state = {
    "isDeliveryActive": False,
    "truck": {
        "x": 100, 
        "y": 24, 
        "status": "moving", 
        "direction": 1
    },
    "drone": {
        "x": 100, 
        "y": 24,
        "status": "DOCKED", # DOCKED, FLYING_OUT, HOVERING, RETURNING, EMERGENCY_ABORT
        "battery": 100.0,
        "targetOrder": None,
        "hoverTimer": 0,
        "eta": 0.0
    },
    "orders": []
}