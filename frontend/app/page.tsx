'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Truck, Navigation, Battery, Camera, Package, AlertOctagon, CheckCircle2, Crosshair, X, Plus, Home, Bell, Wind, ArrowUp } from 'lucide-react';

const MAX_DRONE_PAYLOAD = 2.5; 
const INVENTORY = [
  { id: '1', name: 'Аптечка первой помощи', weight: 0.5, icon: '💊' },
  { id: '2', name: 'Горячая пицца', weight: 0.8, icon: '🍕' },
  { id: '3', name: 'Смартфон', weight: 0.3, icon: '📱' },
  { id: '4', name: 'Ноутбук', weight: 2.1, icon: '💻' },
  { id: '5', name: 'Набор гантелей', weight: 5.0, icon: '🏋️' },
];

const HOUSES = [
  // === ЛЕВЫЙ БЕРЕГ (Разреженный Юг -> Плотный Север) ===
  { id: 'h1', name: 'Бизнес-парк Юг (Корпус А)', x: 30, y: 40, w: 90, h: 30, rot: 0 },
  { id: 'h2', name: 'Бизнес-парк Юг (Корпус Б)', x: 15, y: 55, w: 30, h: 60, rot: 0 },
  { id: 'h3', name: 'Инновационный центр (Секция 1)', x: 40, y: 85, w: 100, h: 30, rot: 0 },
  { id: 'h4', name: 'Инновационный центр (Секция 2)', x: 40, y: 65, w: 30, h: 50, rot: 0 },
  { id: 'h5', name: 'Квартал Инноваций (Пристройка)', x: 15, y: 85, w: 30, h: 40, rot: 0 },
  { id: 'h6', name: 'Башня Связи', x: 20, y: 70, w: 30, h: 30, rot: 45 },
  { id: 'h7', name: 'ЖК Диагональ - Линия А', x: 45, y: 135, w: 120, h: 30, rot: 15 },
  { id: 'h8', name: 'ЖК Диагональ - Линия Б', x: 35, y: 120, w: 30, h: 70, rot: 15 },
  { id: 'h9', name: 'ЖК Диагональ - Флигель', x: 15, y: 140, w: 30, h: 50, rot: 15 },
  { id: 'h10', name: 'ЖК Диагональ - Паркинг', x: 65, y: 120, w: 30, h: 40, rot: 15 },
  { id: 'h11', name: 'ЖК Диагональ - Башня', x: 25, y: 155, w: 50, h: 30, rot: 15 },
  { id: 'h12', name: 'Северный Колодец (Север)', x: 45, y: 185, w: 100, h: 30, rot: 0 },
  { id: 'h13', name: 'Северный Колодец (Юг)', x: 45, y: 165, w: 100, h: 30, rot: 0 },
  { id: 'h14', name: 'Северный Колодец (Запад)', x: 15, y: 175, w: 30, h: 70, rot: 0 },
  { id: 'h15', name: 'Угловая Башня 1', x: 10, y: 190, w: 40, h: 40, rot: 0 },
  { id: 'h16', name: 'Угловая Башня 2', x: 10, y: 160, w: 40, h: 40, rot: 0 },
  { id: 'h17', name: 'Блок Обслуживания (Л)', x: 70, y: 175, w: 30, h: 50, rot: 0 },
  { id: 'h36', name: 'ЖК Магистраль Л-1', x: 86, y: 60, w: 25, h: 120, rot: 0 },
  { id: 'h37', name: 'ЖК Магистраль Л-2', x: 86, y: 100, w: 25, h: 150, rot: 0 },
  { id: 'h38', name: 'ЖК Магистраль Л-3', x: 86, y: 140, w: 25, h: 120, rot: 0 },
  { id: 'h42', name: 'Окраина Запад (Блок 1)', x: 8, y: 110, w: 25, h: 100, rot: 0 },
  { id: 'h43', name: 'Окраина Запад (Блок 2)', x: 25, y: 110, w: 60, h: 25, rot: 0 },

  // === ПРАВЫЙ БЕРЕГ (Разреженный Юг -> Плотный Север) ===
  { id: 'h18', name: 'Торговая Галерея (Главная)', x: 170, y: 40, w: 90, h: 30, rot: 0 },
  { id: 'h19', name: 'Торговая Галерея (Склад)', x: 185, y: 55, w: 30, h: 60, rot: 0 },
  { id: 'h20', name: 'ЖК Полуостров - Север', x: 165, y: 105, w: 80, h: 30, rot: 0 },
  { id: 'h21', name: 'ЖК Полуостров - Юг', x: 165, y: 75, w: 80, h: 30, rot: 0 },
  { id: 'h22', name: 'ЖК Полуостров - Восток', x: 190, y: 90, w: 30, h: 50, rot: 0 },
  { id: 'h23', name: 'Административное здание', x: 135, y: 90, w: 30, h: 70, rot: 0 },
  { id: 'h24', name: 'ЖК Каскад - Основание', x: 155, y: 140, w: 100, h: 30, rot: -10 },
  { id: 'h25', name: 'ЖК Каскад - Крыло 1', x: 165, y: 125, w: 30, h: 50, rot: -10 },
  { id: 'h26', name: 'ЖК Каскад - Крыло 2', x: 140, y: 155, w: 40, h: 40, rot: -10 },
  { id: 'h27', name: 'ЖК Каскад - Башня', x: 185, y: 155, w: 30, h: 50, rot: -10 },
  { id: 'h28', name: 'ЖК Ступени (Блок 1)', x: 145, y: 185, w: 80, h: 30, rot: 0 },
  { id: 'h29', name: 'ЖК Ступени (Блок 2)', x: 145, y: 165, w: 80, h: 30, rot: 0 },
  { id: 'h30', name: 'ЖК Ступени (Переход)', x: 175, y: 175, w: 30, h: 50, rot: 0 },
  { id: 'h31', name: 'ЖК Ступени (Блок 3)', x: 125, y: 175, w: 30, h: 40, rot: 0 },
  { id: 'h32', name: 'Квартал-Башня (П-В)', x: 190, y: 185, w: 30, h: 40, rot: 0 },
  { id: 'h33', name: 'Квартал-Башня (П-Н)', x: 190, y: 165, w: 30, h: 40, rot: 0 },
  { id: 'h34', name: 'Отель Южный', x: 180, y: 70, w: 40, h: 40, rot: -45 },
  { id: 'h35', name: 'Бизнес-Башня (П)', x: 130, y: 95, w: 30, h: 60, rot: 0 },
  { id: 'h39', name: 'ЖК Магистраль П-1', x: 114, y: 60, w: 25, h: 120, rot: 0 },
  { id: 'h40', name: 'ЖК Магистраль П-2', x: 114, y: 100, w: 25, h: 150, rot: 0 },
  { id: 'h41', name: 'ЖК Магистраль П-3', x: 114, y: 140, w: 25, h: 120, rot: 0 },
  { id: 'h44', name: 'Окраина Восток (Блок 1)', x: 195, y: 110, w: 25, h: 100, rot: 0 },
  { id: 'h45', name: 'Окраина Восток (Блок 2)', x: 175, y: 110, w: 60, h: 25, rot: 0 },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  
  const [orders, setOrders] = useState<any[]>([]);
  const [isDeliveryActive, setIsDeliveryActive] = useState(false);
  const [showToast, setShowToast] = useState(false);
  
  // Уведомление для пользователя
  const [clientNotification, setClientNotification] = useState<{title: string, message: string, type: string} | null>(null);
  const lastNotifiedOrderId = useRef<string | null>(null);

  // Болванка для ветра (рандомизатор)
  const [wind, setWind] = useState({ speed: 4.2, direction: 45 });

  const [truck, setTruck] = useState({ x: 100, y: 24, status: 'moving', direction: 1 });
  const [drone, setDrone] = useState({
    x: 100, 
    y: 24, 
    status: 'DOCKED', 
    battery: 100, 
    targetOrder: null as any, 
    eta: 0, 
    hoverTimer: 0,
    // Новые поля:
    angle: 0,
    time: 0,
    distance: 0,
    remaining_time: 0
  });
  const ws = useRef<WebSocket | null>(null);
  const [cart, setCart] = useState<any[]>([]);
  const [selectedHouse, setSelectedHouse] = useState(HOUSES[0]);
  const [deliveryType, setDeliveryType] = useState('window');

  const cartWeight = cart.reduce((sum, item) => sum + item.weight, 0);
  const isOverweight = cartWeight > MAX_DRONE_PAYLOAD;

  const addToCart = (item: any) => setCart([...cart, item]);
  const removeFromCart = (index: number) => setCart(cart.filter((_, i) => i !== index));
  
  const handleCheckout = () => {
    if (cart.length === 0) return;
    const newOrder = {
      id: Math.random().toString(36).substring(2, 7).toUpperCase(),
      house: selectedHouse,
      items: [...cart],
      weight: cartWeight,
      deliveryType: deliveryType,
      status: 'pending',
      assignedTo: isOverweight ? 'truck' : 'drone'
    };
    
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'NEW_ORDER', order: newOrder }));
    } else {
      setOrders(prev => [...prev, newOrder]);
    }
    
    setCart([]);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8000/ws/telemetry');
    ws.current.onmessage = (event) => {
    const serverState = JSON.parse(event.data);
    setTruck(serverState.truck);
    setOrders(serverState.orders);
    setIsDeliveryActive(serverState.isDeliveryActive);

    // Обновляем дрон, сохраняя старые значения, если новых нет в пакете
    setDrone(prev => ({
      ...prev,
      ...serverState.drone
    }));
  };
    return () => { if (ws.current) ws.current.close(); };
  }, []);

  // Симуляция изменения погодных условий
  useEffect(() => {
    const interval = setInterval(() => {
      setWind(prev => ({
        speed: Math.max(0.5, prev.speed + (Math.random() - 0.5) * 1.5),
        direction: (prev.direction + (Math.random() - 0.5) * 30) % 360
      }));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  // --- ЛОГИКА УВЕДОМЛЕНИЙ ПРИ ПОДЛЕТЕ ---
  useEffect(() => {
    if (drone.status === 'HOVERING' && drone.targetOrder) {
      if (lastNotifiedOrderId.current !== drone.targetOrder.id) {
        lastNotifiedOrderId.current = drone.targetOrder.id;

        if (drone.targetOrder.deliveryType === 'window') {
          setClientNotification({
            title: 'Дрон ожидает за окном!',
            message: 'Система DronePort активирована. Пожалуйста, заберите ваш заказ.',
            type: 'window'
          });
        } else if (drone.targetOrder.deliveryType === 'porch') {
          setClientNotification({
            title: 'Заказ доставлен к подъезду!',
            message: 'Дрон успешно спустил товар лебедкой и возвращается на базу.',
            type: 'porch'
          });
        }
        
        // Скрываем уведомление через 8 секунд
        setTimeout(() => setClientNotification(null), 8000);
      }
    }
  }, [drone.status, drone.targetOrder]);

  const triggerEmergency = () => {
    fetch('http://localhost:8000/api/gesture', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'abort' })
    }).catch(err => console.error(err));
  };

  // Визуальное масштабирование дрона (имитация высоты)
  let droneScale = 1;
  if (drone.status === 'HOVERING' && drone.targetOrder) {
    droneScale = drone.targetOrder.deliveryType === 'window' ? 1.5 : 0.7;
  } else if (drone.status === 'FLYING_OUT' || drone.status === 'RETURNING') {
    droneScale = 1.2; // В полете дрон чуть выше
  }

  if (activeTab === 'client') {
    return (
      <div className="min-h-screen bg-slate-900 text-slate-100 p-6 flex justify-center items-center font-sans">
        <div className="max-w-4xl w-full grid grid-cols-1 md:grid-cols-2 gap-8">
          
          <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-2xl">
            <h2 className="text-2xl font-bold mb-6 text-white flex items-center gap-2">
              <Package className="text-cyan-400" /> Сборка заказа
            </h2>
            <div className="space-y-3">
              {INVENTORY.map(item => (
                <button key={item.id} onClick={() => addToCart(item)} className="w-full flex justify-between items-center p-4 bg-slate-700 hover:bg-slate-600 rounded-xl transition-colors text-left">
                  <span className="text-xl flex items-center gap-3">{item.icon} <span className="text-sm font-medium">{item.name}</span></span>
                  <span className="text-slate-400 text-sm">{item.weight.toFixed(1)} кг</span>
                </button>
              ))}
            </div>
            
            <div className="mt-8">
              <label className="text-sm text-slate-400 mb-2 block">Адрес доставки:</label>
              <select className="w-full bg-slate-900 border border-slate-600 rounded-lg p-3 text-white" value={selectedHouse.id} onChange={(e) => setSelectedHouse(HOUSES.find(h => h.id === e.target.value) || HOUSES[0])}>
                {HOUSES.map(h => <option key={h.id} value={h.id}>{h.name}</option>)}
              </select>
            </div>
          </div>

          <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-2xl flex flex-col">
            <h2 className="text-2xl font-bold mb-6 text-white flex justify-between">
              Корзина <span className="text-cyan-400 text-lg bg-cyan-900/30 px-3 py-1 rounded-full">{cartWeight.toFixed(1)} кг</span>
            </h2>

            <div className="mb-6 p-4 bg-slate-900 rounded-xl border border-slate-700">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-slate-400">Грузоподъемность</span>
                <span className={isOverweight ? 'text-red-400 font-bold' : 'text-emerald-400'}>{cartWeight.toFixed(1)} / {MAX_DRONE_PAYLOAD} кг</span>
              </div>
              <div className="h-3 w-full bg-slate-700 rounded-full overflow-hidden">
                <div className={`h-full transition-all duration-300 ${isOverweight ? 'bg-red-500' : 'bg-emerald-500'}`} style={{ width: `${Math.min(100, (cartWeight / MAX_DRONE_PAYLOAD) * 100)}%` }} />
              </div>
            </div>

            {!isOverweight && cart.length > 0 && (
              <div className="mb-6">
                <h3 className="text-sm text-slate-400 mb-3">Опции "Последнего метра":</h3>
                <div className="grid grid-cols-2 gap-3">
                  <button onClick={() => setDeliveryType('window')} className={`p-3 rounded-xl border flex flex-col items-center gap-2 transition-all ${deliveryType === 'window' ? 'bg-cyan-900/40 border-cyan-400 text-cyan-200' : 'bg-slate-700 border-slate-600 text-slate-400'}`}>
                    <Crosshair size={24} /> <span className="text-xs text-center">Доставка в окно<br/>(DronePort)</span>
                  </button>
                  <button onClick={() => setDeliveryType('porch')} className={`p-3 rounded-xl border flex flex-col items-center gap-2 transition-all ${deliveryType === 'porch' ? 'bg-cyan-900/40 border-cyan-400 text-cyan-200' : 'bg-slate-700 border-slate-600 text-slate-400'}`}>
                    <Home size={24} /> <span className="text-xs text-center">На крыльцо<br/>(Лебедка)</span>
                  </button>
                </div>
              </div>
            )}

            <div className="flex-1 overflow-y-auto mb-6 border-t border-slate-700 pt-4 space-y-2">
              {cart.map((item, idx) => (
                <div key={idx} className="flex justify-between items-center text-sm bg-slate-900 p-2 rounded">
                  <span>{item.icon} {item.name}</span>
                  <button onClick={() => removeFromCart(idx)} className="text-slate-500 hover:text-red-400"><X size={16} /></button>
                </div>
              ))}
            </div>

            <button onClick={handleCheckout} disabled={cart.length === 0} className={`w-full py-4 rounded-xl font-bold text-lg transition-colors flex items-center justify-center gap-2 ${cart.length === 0 ? 'bg-slate-700 text-slate-500 cursor-not-allowed' : isOverweight ? 'bg-orange-600 hover:bg-orange-500 text-white' : 'bg-emerald-600 hover:bg-emerald-500 text-white'}`}>
              <CheckCircle2 /> {isOverweight ? 'В очередь (Грузовик)' : 'В очередь (Дрон)'}
            </button>
            <button onClick={() => setActiveTab('dashboard')} className="mt-4 text-slate-400 hover:text-white text-sm text-center w-full underline">Перейти в Дашборд</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 font-sans overflow-hidden select-none relative">
      
      {/* КЛИЕНТСКОЕ УВЕДОМЛЕНИЕ */}
      {clientNotification && (
        <div className="absolute bottom-6 left-6 z-[100] bg-slate-900/95 backdrop-blur border border-cyan-800 rounded-xl p-4 shadow-[0_0_25px_rgba(6,182,212,0.3)] transition-all duration-300 flex items-start gap-4 min-w-[300px] border-l-4 border-l-cyan-400">
          <div className="bg-cyan-950 p-2 rounded-full mt-1">
            <Bell size={20} className="text-cyan-400 animate-pulse" />
          </div>
          <div>
            <div className="text-[10px] text-cyan-500 font-bold uppercase tracking-wider mb-1">Уведомление пользователю</div>
            <h4 className="text-white font-bold text-sm mb-1">{clientNotification.title}</h4>
            <p className="text-slate-400 text-xs leading-relaxed">{clientNotification.message}</p>
          </div>
          <button onClick={() => setClientNotification(null)} className="absolute top-3 right-3 text-slate-500 hover:text-white"><X size={14} /></button>
        </div>
      )}

      {/* ЛЕВАЯ ПАНЕЛЬ: КАРТА */}
      <div className="w-[65%] relative border-r border-slate-800 bg-[#e5e5e0] shadow-inner overflow-hidden">
        <button onClick={() => setActiveTab('client')} className="absolute top-4 left-4 z-50 bg-slate-900 hover:bg-slate-800 p-2 rounded border border-slate-700 text-sm flex items-center gap-2 text-white shadow-lg">
          <Plus size={16}/> Клиентское приложение
        </button>

        <div className="absolute top-0 bottom-0 left-1/2 w-10 -ml-5 bg-[#1e3a8a] flex justify-center shadow-[0_0_15px_rgba(30,58,138,0.2)]">
          <div className="w-1 h-full border-l-[3px] border-dashed border-white/40"></div>
        </div>
        {/* СКЛАД (НИЗ ДОРОГИ) */}
        <div className="absolute z-20 flex flex-col items-center" 
            style={{ left: '50%', bottom: '12%', transform: 'translate(-50%, 50%)' }}>
          <div className="bg-slate-900 border-2 border-orange-500 p-2 rounded-lg shadow-[0_0_15px_rgba(249,115,22,0.4)]">
            <Home size={24} className="text-orange-500" />
          </div>
          <span className="mt-1 text-[10px] font-bold text-slate-800 bg-orange-100 px-1 rounded">СКЛАД</span>
        </div>

        {/* ПВЗ (ВЕРХ ДОРОГИ) */}
        <div className="absolute z-20 flex flex-col items-center" 
            style={{ left: '50%', bottom: '88%', transform: 'translate(-50%, 50%)' }}>
          <div className="bg-slate-900 border-2 border-emerald-500 p-2 rounded-lg shadow-[0_0_15px_rgba(16,185,129,0.4)]">
            <Package size={24} className="text-emerald-500" />
          </div>
          <span className="mt-1 text-[10px] font-bold text-slate-800 bg-emerald-100 px-1 rounded">ПВЗ (DROP-OFF)</span>
        </div>
        {HOUSES.map(h => (
          <div key={h.id} className="absolute bg-[#e11d48] border-4 border-[#be123c] rounded shadow-2xl flex flex-col items-center justify-center text-white/40 font-bold overflow-hidden"
            style={{ left: `${h.x / 2}%`, bottom: `${h.y / 2}%`, width: `${h.w}px`, height: `${h.h}px`, transform: `translate(-50%, 50%) rotate(${h.rot}deg)` }}>
            {drone.status === 'HOVERING' && drone.targetOrder?.house.id === h.id && (
               <div className={`absolute inset-0 border-[6px] animate-ping opacity-90 ${drone.targetOrder.deliveryType === 'window' ? 'border-cyan-400' : 'border-emerald-400'}`}></div>
            )}
          </div>
        ))}

        {drone.status !== 'DOCKED' && (
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-10">
            <line x1={`${truck.x / 2}%`} y1={`${100 - truck.y / 2}%`} x2={`${drone.x / 2}%`} y2={`${100 - drone.y / 2}%`} stroke="rgba(6, 182, 212, 0.6)" strokeWidth="3" strokeDasharray="6,6" />
          </svg>
        )}

        {/* ГРУЗОВИК */}
        <div className="absolute w-12 h-24 bg-slate-800 rounded-md shadow-[0_10px_25px_rgba(0,0,0,0.6)] z-20 flex flex-col items-center justify-end pb-2 border-b-4 border-slate-900 transition-transform"
          style={{ left: `${truck.x / 2}%`, bottom: `${truck.y / 2}%`, transform: `translate(-50%, 50%) ${truck.direction === -1 ? 'rotate(180deg)' : ''}` }}>
          <Truck size={20} className="text-white mb-2 opacity-50" />
          <div className="w-8 h-8 bg-slate-900 border border-cyan-500/50 rounded flex items-center justify-center relative">
            <div className="w-4 h-4 rounded-full bg-cyan-900 flex items-center justify-center"><span className="text-[8px] text-cyan-400 font-bold">H</span></div>
            {drone.status === 'DOCKED' && (
               <div className="absolute inset-0 flex items-center justify-center">
                 <Navigation size={18} fill="cyan" stroke="cyan" className="animate-pulse drop-shadow-[0_0_8px_rgba(6,182,212,1)]" />
               </div>
            )}
          </div>
        </div>

        {/* ДРОН С АНИМАЦИЕЙ МАСШТАБА */}
        {drone.status !== 'DOCKED' && (
          <div className="absolute z-30 flex flex-col items-center"
            style={{ 
              left: `${drone.x / 2}%`, bottom: `${drone.y / 2}%`, 
              transform: `translate(-50%, 50%) scale(${droneScale})`,
              transition: 'left 0.1s linear, bottom 0.1s linear, transform 1s ease-in-out' 
            }}>
            <div className={`p-2 rounded-full ${drone.status === 'EMERGENCY_ABORT' ? 'bg-red-500/20' : 'bg-cyan-500/20'} backdrop-blur-sm border ${drone.status === 'EMERGENCY_ABORT' ? 'border-red-500' : 'border-cyan-500'} shadow-[0_10px_20px_rgba(0,0,0,0.5)]`}>
              <Navigation size={24} fill={drone.status === 'EMERGENCY_ABORT' ? "#ef4444" : "#06b6d4"} 
                className={`${drone.status === 'HOVERING' ? 'animate-bounce' : ''} ${drone.status === 'EMERGENCY_ABORT' ? 'animate-spin' : ''}`}
                style={{ transform: drone.status === 'RETURNING' || drone.status === 'EMERGENCY_ABORT' ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.5s ease' }} 
              />
            </div>
            <div className="mt-1 bg-slate-900/80 px-2 py-0.5 rounded text-[10px] font-mono border border-slate-700 text-cyan-300 shadow-md">
              DRN [{Math.floor(drone.battery)}%]
            </div>
          </div>
        )}
      </div>

      {/* ПРАВАЯ ПАНЕЛЬ: УПРАВЛЕНИЕ */}
      <div className="w-[35%] flex flex-col bg-slate-950 p-4 border-l border-slate-800 z-40 overflow-y-auto">
        {drone.status === 'EMERGENCY_ABORT' && <div className="absolute inset-0 bg-red-900/20 animate-pulse pointer-events-none z-0"></div>}

        <h1 className="text-xl font-bold text-white mb-6 tracking-wider flex items-center gap-2 relative z-10"><AlertOctagon className="text-cyan-500" /> HUB COMMAND</h1>

        {/* --- НОВЫЙ БЛОК: ПОГОДНЫЕ УСЛОВИЯ (ВЕТЕР) --- */}
        <div className="bg-slate-900 border border-slate-700 rounded-xl p-4 mb-4 relative z-10">
          <div className="flex justify-between items-center mb-3">
             <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
               <Wind size={16} /> Погодные условия
             </h2>
             <span className="text-[10px] font-mono text-cyan-400 border border-cyan-800 bg-cyan-900/50 px-2 py-0.5 rounded animate-pulse">
               ДАТЧИК АКТИВЕН
             </span>
          </div>
          <div className="flex items-center gap-6">
             <div className="w-14 h-14 rounded-full border-2 border-slate-700 flex items-center justify-center bg-slate-950 relative shadow-inner">
               <span className="absolute top-1 text-[8px] text-slate-500 font-bold">N</span>
               <span className="absolute right-1 text-[8px] text-slate-500 font-bold">E</span>
               <span className="absolute bottom-1 text-[8px] text-slate-500 font-bold">S</span>
               <span className="absolute left-1 text-[8px] text-slate-500 font-bold">W</span>
               {/* Стрелка ветра (плавно крутится) */}
               <ArrowUp size={20} className="text-cyan-400 transition-transform duration-1000" style={{ transform: `rotate(${wind.direction}deg)` }} />
             </div>
             <div className="flex flex-col">
               <span className="text-2xl font-mono text-white transition-all">
                 {wind.speed.toFixed(1)} <span className="text-sm text-slate-500">м/с</span>
               </span>
               <span className="text-xs text-slate-400 font-mono mt-1">Вектор: {Math.round(wind.direction)}°</span>
             </div>
          </div>
        </div>

        <div className={`rounded-xl border p-4 mb-4 relative z-10 transition-colors ${drone.status === 'EMERGENCY_ABORT' ? 'bg-red-950/50 border-red-800' : 'bg-slate-900 border-slate-700'}`}>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Телеметрия дрона</h2>
            <span className={`px-2 py-1 text-xs font-mono rounded ${drone.status === 'DOCKED' ? 'bg-slate-800 text-slate-400' : drone.status === 'EMERGENCY_ABORT' ? 'bg-red-600 text-white animate-pulse' : 'bg-cyan-900/50 text-cyan-400 border border-cyan-800'}`}>
              {drone.status}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs font-mono mb-4">
            {/* Координаты */}
            <div className="bg-slate-950 p-2 rounded border border-slate-800 text-slate-400">
              POS: X: {(drone.x / 2).toFixed(1)} Y: {(drone.y / 2).toFixed(1)}
            </div>
            
            {/* Твое время полета (берем из drone.time, которое считает бэкенд) */}
            <div className="bg-slate-950 p-2 rounded border border-slate-800 text-slate-400">
              FLIGHT TIME: {drone.time ? Math.floor(drone.time) : 0}s
            </div>

            {/* Угол поворота из твоей физики */}
            <div className="bg-slate-950 p-2 rounded border border-slate-800 text-slate-400">
              YAW: {drone.angle ? drone.angle.toFixed(1) : 0}°
            </div>

            {/* Оставшееся время (расчетное) */}
            <div className="bg-slate-950 p-2 rounded border border-slate-800 text-cyan-500 font-bold">
              EST. REMAINING: {drone.remaining_time ? drone.remaining_time : '--'} min
            </div>

            {/* Дистанция */}
            <div className="bg-slate-950 p-2 rounded border border-slate-800 text-slate-400">
              DIST: {drone.distance ? drone.distance.toFixed(1) : 0} m
            </div>

            {/* Расчетное время прибытия */}
            <div className="bg-slate-950 p-2 rounded border border-slate-800 text-slate-400">
              ETA: {drone.status !== 'DOCKED' && drone.status !== 'HOVERING' ? `${drone.eta?.toFixed(1)}s` : '--'}
            </div>
          </div>
          {/* 2. ИНДИКАТОР ЗАРЯДА */}
          <div className="mb-4 space-y-1">
            <div className="flex justify-between text-[10px] font-mono text-slate-500 uppercase tracking-tighter">
              <span>Power System</span>
              <span className={drone.battery < 20 ? 'text-red-500 animate-pulse font-bold' : 'text-cyan-400'}>
                {drone.battery ? drone.battery.toFixed(1) : 100}%
              </span>
            </div>
            <div className="h-2 w-full bg-slate-950 rounded-full border border-slate-800 p-0.5">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${
                  drone.battery > 50 ? 'bg-emerald-500' : drone.battery > 20 ? 'bg-orange-500' : 'bg-red-600'
                }`}
                style={{ width: `${drone.battery || 100}%` }}
              />
            </div>
          </div>
          {/* FPV КАМЕРА */}
          <div className="relative w-full h-32 bg-black rounded-lg border border-slate-700 overflow-hidden flex items-center justify-center">
            {drone.status === 'HOVERING' && drone.targetOrder?.deliveryType === 'window' ? (
              <>
                <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] opacity-20 mix-blend-screen"></div>
                <div className="absolute top-2 left-2 text-[10px] text-green-500 font-mono flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span> REC</div>
                <div className="w-16 h-16 border-2 border-green-500 relative flex items-center justify-center">
                   <div className="absolute -top-1 -left-1 w-2 h-2 border-t-2 border-l-2 border-green-400"></div><div className="absolute -top-1 -right-1 w-2 h-2 border-t-2 border-r-2 border-green-400"></div>
                   <div className="absolute -bottom-1 -left-1 w-2 h-2 border-b-2 border-l-2 border-green-400"></div><div className="absolute -bottom-1 -right-1 w-2 h-2 border-b-2 border-r-2 border-green-400"></div>
                   <span className="text-green-500 font-mono text-[8px] animate-pulse">ARUCO_LOCKED</span>
                </div>
                <div className="absolute bottom-2 text-center w-full text-[10px] text-green-500 font-mono bg-black/50 py-1">СКАНИРОВАНИЕ ФАСАДА... OK</div>
              </>
            ) : drone.status === 'HOVERING' && drone.targetOrder?.deliveryType === 'porch' ? (
              <div className="text-slate-500 font-mono text-xs flex flex-col items-center"><Camera size={24} className="mb-2 opacity-50"/> Спуск лебедки</div>
            ) : (
              <div className="text-slate-700 font-mono text-xs flex flex-col items-center"><Camera size={24} className="mb-2"/> ОЖИДАНИЕ</div>
            )}
          </div>
        </div>

        <button onClick={triggerEmergency} disabled={drone.status === 'DOCKED' || drone.status === 'EMERGENCY_ABORT' || drone.status === 'RETURNING'}
          className={`relative z-10 w-full py-3 rounded-lg font-bold text-sm uppercase tracking-widest transition-all shadow-lg mb-4 border ${(drone.status === 'DOCKED' || drone.status === 'EMERGENCY_ABORT' || drone.status === 'RETURNING') ? 'bg-slate-800 text-slate-600 border-slate-700 cursor-not-allowed' : 'bg-red-600 hover:bg-red-500 text-white border-red-500 hover:shadow-[0_0_15px_rgba(239,68,68,0.5)]'}`}>
          {drone.status === 'EMERGENCY_ABORT' ? 'Возврат на базу...' : 'ABORT (СИМУЛЯЦИЯ ЖЕСТА)'}
        </button>

        <div className="flex-1 relative z-10 flex flex-col">
          <div className="flex justify-between items-center mb-3">
            <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Очередь (TSP-D)</h2>
            <button onClick={() => { if (ws.current) { ws.current.send(JSON.stringify({ type: 'TOGGLE_DELIVERY' })); } else setIsDeliveryActive(!isDeliveryActive); }}
              className={`px-4 py-1.5 rounded font-bold text-xs uppercase tracking-wide transition-all shadow-md ${isDeliveryActive ? 'bg-orange-600 hover:bg-orange-500 text-white shadow-[0_0_10px_rgba(234,88,12,0.4)]' : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-[0_0_10px_rgba(16,185,129,0.4)]'}`}>
              {isDeliveryActive ? 'ПРИОСТАНОВИТЬ' : 'НАЧАТЬ РАЗВОЗ'}
            </button>
          </div>
          
          <div className="space-y-3 overflow-y-auto pr-1">
            {[...orders].reverse().map((order: any) => (
              <div key={order.id} className="bg-slate-900 p-3 rounded-lg border border-slate-800 text-sm">
                <div className="flex justify-between items-center border-b border-slate-800 pb-2 mb-2">
                  <span className="font-mono text-cyan-500 font-bold">#{order.id}</span>
                  <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${order.status === 'delivered' ? 'bg-emerald-900/50 text-emerald-400' : order.status === 'in_progress' ? 'bg-blue-900/50 text-blue-400' : 'bg-slate-800 text-slate-400'}`}>{order.status}</span>
                </div>
                <div className="text-slate-400 text-xs mb-2">Dest: <span className="text-slate-200">{order.house.name}</span> | Type: {order.deliveryType}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}