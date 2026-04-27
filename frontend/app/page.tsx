'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Truck, Navigation, Battery, Camera, Package, AlertOctagon, CheckCircle2, Crosshair, X, Plus, Home } from 'lucide-react';

// --- КОНСТАНТЫ И БАЗЫ ДАННЫХ ---
const MAX_DRONE_PAYLOAD = 2.5; // кг
const DRONE_SPEED = 3.0; // Скорость увеличена под сетку 200x200
const TRUCK_SPEED = 1.0;

const INVENTORY = [
  { id: '1', name: 'Аптечка первой помощи', weight: 0.5, icon: '💊' },
  { id: '2', name: 'Горячая пицца', weight: 0.8, icon: '🍕' },
  { id: '3', name: 'Смартфон', weight: 0.3, icon: '📱' },
  { id: '4', name: 'Ноутбук', weight: 2.1, icon: '💻' },
  { id: '5', name: 'Набор гантелей', weight: 5.0, icon: '🏋️' },
];

// ОБНОВЛЕННАЯ КАРТА: 45 домов, добавлена плотная магистральная застройка вдоль дороги
const HOUSES = [
  // === ЛЕВЫЙ БЕРЕГ (Разреженный Юг -> Плотный Север) ===
  
  // Квартал 1: Малоэтажный бизнес-парк (L-образный, разреженный)
  { id: 'h1', name: 'Бизнес-парк Юг (Корпус А)', x: 30, y: 40, w: 90, h: 30, rot: 0 },
  { id: 'h2', name: 'Бизнес-парк Юг (Корпус Б)', x: 15, y: 55, w: 30, h: 60, rot: 0 },
  
  // Квартал 2: Инновационный центр (Т-образный)
  { id: 'h3', name: 'Инновационный центр (Секция 1)', x: 40, y: 85, w: 100, h: 30, rot: 0 },
  { id: 'h4', name: 'Инновационный центр (Секция 2)', x: 40, y: 65, w: 30, h: 50, rot: 0 },
  { id: 'h5', name: 'Квартал Инноваций (Пристройка)', x: 15, y: 85, w: 30, h: 40, rot: 0 },
  { id: 'h6', name: 'Башня Связи', x: 20, y: 70, w: 30, h: 30, rot: 45 },

  // Квартал 3: ЖК Диагональ (Сложная диагональная застройка)
  { id: 'h7', name: 'ЖК Диагональ - Линия А', x: 45, y: 135, w: 120, h: 30, rot: 15 },
  { id: 'h8', name: 'ЖК Диагональ - Линия Б', x: 35, y: 120, w: 30, h: 70, rot: 15 },
  { id: 'h9', name: 'ЖК Диагональ - Флигель', x: 15, y: 140, w: 30, h: 50, rot: 15 },
  { id: 'h10', name: 'ЖК Диагональ - Паркинг', x: 65, y: 120, w: 30, h: 40, rot: 15 },
  { id: 'h11', name: 'ЖК Диагональ - Башня', x: 25, y: 155, w: 50, h: 30, rot: 15 },

  // Квартал 4: Плотный ЖК Северный Колодец (С-образная структура)
  { id: 'h12', name: 'Северный Колодец (Север)', x: 45, y: 185, w: 100, h: 30, rot: 0 },
  { id: 'h13', name: 'Северный Колодец (Юг)', x: 45, y: 165, w: 100, h: 30, rot: 0 },
  { id: 'h14', name: 'Северный Колодец (Запад)', x: 15, y: 175, w: 30, h: 70, rot: 0 },
  { id: 'h15', name: 'Угловая Башня 1', x: 10, y: 190, w: 40, h: 40, rot: 0 },
  { id: 'h16', name: 'Угловая Башня 2', x: 10, y: 160, w: 40, h: 40, rot: 0 },
  { id: 'h17', name: 'Блок Обслуживания (Л)', x: 70, y: 175, w: 30, h: 50, rot: 0 },

  // НОВОЕ: МАГИСТРАЛЬНАЯ ЗАСТРОЙКА (ЛЕВАЯ СТОРОНА ВДОЛЬ ДОРОГИ)
  { id: 'h36', name: 'ЖК Магистраль Л-1', x: 86, y: 60, w: 25, h: 120, rot: 0 },
  { id: 'h37', name: 'ЖК Магистраль Л-2', x: 86, y: 100, w: 25, h: 150, rot: 0 },
  { id: 'h38', name: 'ЖК Магистраль Л-3', x: 86, y: 140, w: 25, h: 120, rot: 0 },

  // НОВОЕ: Замыкающие блоки на краю левого берега
  { id: 'h42', name: 'Окраина Запад (Блок 1)', x: 8, y: 110, w: 25, h: 100, rot: 0 },
  { id: 'h43', name: 'Окраина Запад (Блок 2)', x: 25, y: 110, w: 60, h: 25, rot: 0 },


  // === ПРАВЫЙ БЕРЕГ (Разреженный Юг -> Плотный Север) ===

  // Квартал 5: Торговая Галерея (L-образная, разреженная)
  { id: 'h18', name: 'Торговая Галерея (Главная)', x: 170, y: 40, w: 90, h: 30, rot: 0 },
  { id: 'h19', name: 'Торговая Галерея (Склад)', x: 185, y: 55, w: 30, h: 60, rot: 0 },
  
  // Квартал 6: ЖК Полуостров (С-образный комплекс)
  { id: 'h20', name: 'ЖК Полуостров - Север', x: 165, y: 105, w: 80, h: 30, rot: 0 },
  { id: 'h21', name: 'ЖК Полуостров - Юг', x: 165, y: 75, w: 80, h: 30, rot: 0 },
  { id: 'h22', name: 'ЖК Полуостров - Восток', x: 190, y: 90, w: 30, h: 50, rot: 0 },
  { id: 'h23', name: 'Административное здание', x: 135, y: 90, w: 30, h: 70, rot: 0 },

  // Квартал 7: ЖК Каскад (Повернутая Т-образная форма)
  { id: 'h24', name: 'ЖК Каскад - Основание', x: 155, y: 140, w: 100, h: 30, rot: -10 },
  { id: 'h25', name: 'ЖК Каскад - Крыло 1', x: 165, y: 125, w: 30, h: 50, rot: -10 },
  { id: 'h26', name: 'ЖК Каскад - Крыло 2', x: 140, y: 155, w: 40, h: 40, rot: -10 },
  { id: 'h27', name: 'ЖК Каскад - Башня', x: 185, y: 155, w: 30, h: 50, rot: -10 },

  // Квартал 8: ЖК Ступени (Плотная змейка у ПВЗ)
  { id: 'h28', name: 'ЖК Ступени (Блок 1)', x: 145, y: 185, w: 80, h: 30, rot: 0 },
  { id: 'h29', name: 'ЖК Ступени (Блок 2)', x: 145, y: 165, w: 80, h: 30, rot: 0 },
  { id: 'h30', name: 'ЖК Ступени (Переход)', x: 175, y: 175, w: 30, h: 50, rot: 0 },
  { id: 'h31', name: 'ЖК Ступени (Блок 3)', x: 125, y: 175, w: 30, h: 40, rot: 0 },
  { id: 'h32', name: 'Квартал-Башня (П-В)', x: 190, y: 185, w: 30, h: 40, rot: 0 },
  { id: 'h33', name: 'Квартал-Башня (П-Н)', x: 190, y: 165, w: 30, h: 40, rot: 0 },

  // Точечная застройка (Замыкающие)
  { id: 'h34', name: 'Отель Южный', x: 180, y: 70, w: 40, h: 40, rot: -45 },
  { id: 'h35', name: 'Бизнес-Башня (П)', x: 130, y: 95, w: 30, h: 60, rot: 0 },

  // НОВОЕ: МАГИСТРАЛЬНАЯ ЗАСТРОЙКА (ПРАВАЯ СТОРОНА ВДОЛЬ ДОРОГИ)
  { id: 'h39', name: 'ЖК Магистраль П-1', x: 114, y: 60, w: 25, h: 120, rot: 0 },
  { id: 'h40', name: 'ЖК Магистраль П-2', x: 114, y: 100, w: 25, h: 150, rot: 0 },
  { id: 'h41', name: 'ЖК Магистраль П-3', x: 114, y: 140, w: 25, h: 120, rot: 0 },

  // НОВОЕ: Замыкающие блоки на краю правого берега
  { id: 'h44', name: 'Окраина Восток (Блок 1)', x: 195, y: 110, w: 25, h: 100, rot: 0 },
  { id: 'h45', name: 'Окраина Восток (Блок 2)', x: 175, y: 110, w: 60, h: 25, rot: 0 },
];

// --- ВСПОМОГАТЕЛЬНАЯ МАТЕМАТИКА ---
const lerp = (start, end, amt) => (1 - amt) * start + amt * end;
const getDistance = (x1, y1, x2, y2) => Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard'); // 'client' | 'dashboard'
  
  // --- ГЛОБАЛЬНОЕ СОСТОЯНИЕ (БЭКЕНД) ---
  const [orders, setOrders] = useState([]);
  const [isDeliveryActive, setIsDeliveryActive] = useState(false); // НОВОЕ: Флаг активности доставки
  const [showToast, setShowToast] = useState(false); // НОВОЕ: Уведомление о добавлении заказа
  
  // Состояние грузовика (Ось X = 100, старт Y = 24 на сетке 200x200)
  const [truck, setTruck] = useState({ x: 100, y: 24, status: 'moving', direction: 1 });
  
  // Состояние дрона
  const [drone, setDrone] = useState({
    x: 100, y: 24,
    status: 'DOCKED', // DOCKED, FLYING_OUT, HOVERING, RETURNING, EMERGENCY_ABORT
    battery: 100,
    targetOrder: null,
    eta: 0,
    hoverTimer: 0
  });

  // --- СОСТОЯНИЕ КЛИЕНТСКОГО ПРИЛОЖЕНИЯ ---
  const [cart, setCart] = useState([]);
  const [selectedHouse, setSelectedHouse] = useState(HOUSES[0]);
  const [deliveryType, setDeliveryType] = useState('window'); // 'window' | 'porch'

  const cartWeight = cart.reduce((sum, item) => sum + item.weight, 0);
  const isOverweight = cartWeight > MAX_DRONE_PAYLOAD;

  // --- ЛОГИКА КЛИЕНТА (ОФОРМЛЕНИЕ ЗАКАЗА) ---
  const addToCart = (item) => setCart([...cart, item]);
  const removeFromCart = (index) => setCart(cart.filter((_, i) => i !== index));
  
  const handleCheckout = () => {
    if (cart.length === 0) return;
    const newOrder = {
      id: Math.random().toString(36).substring(2, 7).toUpperCase(),
      house: selectedHouse,
      items: [...cart],
      weight: cartWeight,
      deliveryType: deliveryType,
      status: 'pending', // pending, in_progress, delivered
      assignedTo: isOverweight ? 'truck' : 'drone'
    };
    setOrders(prev => [...prev, newOrder]);
    setCart([]);
    
    // Показываем уведомление и не перекидываем в дашборд сразу, чтобы можно было набрать очередь
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  // --- ФИЗИЧЕСКИЙ ДВИЖОК / СИМУЛЯТОР (ЦИФРОВОЙ ДВОЙНИК) ---
  useEffect(() => {
    if (!isDeliveryActive) return; // Симуляция на паузе, пока не нажата кнопка в дашборде

    const tickRate = 50; // 20 fps для плавности
    
    const interval = setInterval(() => {
      // 1. Движение грузовика (Ездит вверх-вниз по оси Y от 24 до 176)
      setTruck(prev => {
        let newY = prev.y + (TRUCK_SPEED * prev.direction);
        let newDir = prev.direction;
        if (newY >= 176) { newY = 176; newDir = -1; } // ПВЗ на Севере
        if (newY <= 24) { newY = 24; newDir = 1; }   // Хаб на Юге
        return { ...prev, y: newY, direction: newDir };
      });

      // 2. Логика Дрона (State Machine)
      setDrone(prevDrone => {
        let { x, y, status, battery, targetOrder, hoverTimer } = prevDrone;
        
        // Поиск нового заказа, если дрон на базе
        if (status === 'DOCKED') {
          // Зарядка
          if (battery < 100) battery = Math.min(100, battery + 1);
          
          // Дрон физически на грузовике
          x = truck.x;
          y = truck.y;

          const pendingDroneOrder = orders.find(o => o.status === 'pending' && o.assignedTo === 'drone');
          if (pendingDroneOrder && battery > 30) {
            targetOrder = pendingDroneOrder;
            status = 'FLYING_OUT';
            // Обновляем статус заказа
            setOrders(os => os.map(o => o.id === pendingDroneOrder.id ? { ...o, status: 'in_progress' } : o));
          }
        } 
        else if (status === 'FLYING_OUT' && targetOrder) {
          // Летим к клиенту
          const targetX = targetOrder.house.x;
          const targetY = targetOrder.house.y;
          const dist = getDistance(x, y, targetX, targetY);
          
          battery -= 0.1; // Разряд

          if (dist < 2.0) { // Дистанция захвата цели увеличена под сетку 200x200
            status = 'HOVERING';
            hoverTimer = targetOrder.deliveryType === 'window' ? 60 : 30; // У окна зависает дольше для ArUco
          } else {
            // Движение (Интерполяция)
            const angle = Math.atan2(targetY - y, targetX - x);
            x += Math.cos(angle) * DRONE_SPEED;
            y += Math.sin(angle) * DRONE_SPEED;
          }
        }
        else if (status === 'HOVERING' && targetOrder) {
          battery -= 0.05; // В режиме зависания разряд меньше
          hoverTimer -= 1;
          
          if (hoverTimer <= 0) {
            const completedOrderId = targetOrder.id;
            
            // Ищем следующий заказ в очереди, который назначен на дрона
            const nextOrder = orders.find(o => o.status === 'pending' && o.assignedTo === 'drone' && o.id !== completedOrderId);

            // МУЛЬТИ-ДОСТАВКА: Если есть следующий заказ и хватает батареи (> 40%)
            if (nextOrder && battery > 40) {
              status = 'FLYING_OUT';
              targetOrder = nextOrder; // Берем новую цель
              
              setOrders(os => os.map(o => {
                if (o.id === completedOrderId) return { ...o, status: 'delivered' };
                if (o.id === nextOrder.id) return { ...o, status: 'in_progress' };
                return o;
              }));
            } else {
              // Возврат на движущийся грузовик, если батарея садится или заказов нет
              status = 'RETURNING';
              targetOrder = null;
              
              setOrders(os => os.map(o => o.id === completedOrderId ? { ...o, status: 'delivered' } : o));
            }
          }
        }
        else if (status === 'RETURNING' || status === 'EMERGENCY_ABORT') {
          // Возврат на движущийся грузовик (Рандеву)
          const dist = getDistance(x, y, truck.x, truck.y);
          battery -= 0.15; // Возврат быстрее тратит батарею
          
          if (dist < 4.0) { // Дистанция посадки увеличена под сетку 200
            status = 'DOCKED';
          } else {
            const angle = Math.atan2(truck.y - y, truck.x - x);
            // Если Emergency - летим быстрее
            const speedMultiplier = status === 'EMERGENCY_ABORT' ? 1.5 : 1;
            x += Math.cos(angle) * DRONE_SPEED * speedMultiplier;
            y += Math.sin(angle) * DRONE_SPEED * speedMultiplier;
          }
        }

        return { x, y, status, battery, targetOrder, hoverTimer, eta: getDistance(x,y, truck.x, truck.y) / DRONE_SPEED };
      });
      
      // Авто-завершение заказов грузовика (для симуляции)
      setOrders(os => os.map(o => {
         if(o.assignedTo === 'truck' && o.status === 'pending') {
            // Если грузовик проезжает мимо дома
            if (Math.abs(truck.y - o.house.y) < 10) return { ...o, status: 'delivered' };
         }
         return o;
      }));

    }, tickRate);

    return () => clearInterval(interval);
  }, [truck.x, truck.y, truck.direction, orders, isDeliveryActive]); // Добавлен флаг isDeliveryActive

  // --- ЭКСТРЕННОЕ ПРЕРЫВАНИЕ (СИМУЛЯЦИЯ HDI/ЖЕСТА) ---
  const triggerEmergency = () => {
    if (drone.status === 'FLYING_OUT' || drone.status === 'HOVERING') {
      setDrone(prev => ({ ...prev, status: 'EMERGENCY_ABORT', hoverTimer: 0 }));
      if (drone.targetOrder) {
        // Возвращаем заказ в очередь
        setOrders(os => os.map(o => o.id === drone.targetOrder.id ? { ...o, status: 'pending' } : o));
      }
    }
  };

  // --- РЕНДЕР: КЛИЕНТСКОЕ ПРИЛОЖЕНИЕ ---
  if (activeTab === 'client') {
    return (
      <div className="min-h-screen bg-slate-900 text-slate-100 p-6 flex justify-center items-center font-sans">
        <div className="max-w-4xl w-full grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Левая колонка: Магазин */}
          <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-2xl">
            <h2 className="text-2xl font-bold mb-6 text-white flex items-center gap-2">
              <Package className="text-cyan-400" /> Сборка заказа
            </h2>
            <div className="space-y-3">
              {INVENTORY.map(item => (
                <button 
                  key={item.id}
                  onClick={() => addToCart(item)}
                  className="w-full flex justify-between items-center p-4 bg-slate-700 hover:bg-slate-600 rounded-xl transition-colors text-left"
                >
                  <span className="text-xl flex items-center gap-3">
                    {item.icon} <span className="text-sm font-medium">{item.name}</span>
                  </span>
                  <span className="text-slate-400 text-sm">{item.weight.toFixed(1)} кг</span>
                </button>
              ))}
            </div>
            
            <div className="mt-8">
              <label className="text-sm text-slate-400 mb-2 block">Адрес доставки:</label>
              <select 
                className="w-full bg-slate-900 border border-slate-600 rounded-lg p-3 text-white"
                value={selectedHouse.id}
                onChange={(e) => setSelectedHouse(HOUSES.find(h => h.id === e.target.value))}
              >
                {HOUSES.map(h => <option key={h.id} value={h.id}>{h.name}</option>)}
              </select>
            </div>
          </div>

          {/* Правая колонка: Корзина и Логика */}
          <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-2xl flex flex-col">
            <h2 className="text-2xl font-bold mb-6 text-white flex justify-between">
              Корзина 
              <span className="text-cyan-400 text-lg bg-cyan-900/30 px-3 py-1 rounded-full">{cartWeight.toFixed(1)} кг</span>
            </h2>

            {/* PAYLOAD BAR (Умная корзина) */}
            <div className="mb-6 p-4 bg-slate-900 rounded-xl border border-slate-700">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-slate-400">Грузоподъемность дрона</span>
                <span className={isOverweight ? 'text-red-400 font-bold' : 'text-emerald-400'}>
                  {cartWeight.toFixed(1)} / {MAX_DRONE_PAYLOAD} кг
                </span>
              </div>
              <div className="h-3 w-full bg-slate-700 rounded-full overflow-hidden">
                <div 
                  className={`h-full transition-all duration-300 ${isOverweight ? 'bg-red-500' : 'bg-emerald-500'}`}
                  style={{ width: `${Math.min(100, (cartWeight / MAX_DRONE_PAYLOAD) * 100)}%` }}
                />
              </div>
              {isOverweight && (
                <div className="mt-3 flex items-start gap-2 text-red-400 text-xs bg-red-900/20 p-2 rounded">
                  <AlertOctagon size={14} className="mt-0.5 shrink-0" />
                  Перевес! Этот заказ не может быть доставлен дроном. Система автоматически переназначит его на грузовик.
                </div>
              )}
            </div>

            {/* Выбор метода последней мили */}
            {!isOverweight && cart.length > 0 && (
              <div className="mb-6">
                <h3 className="text-sm text-slate-400 mb-3">Опции "Последнего метра":</h3>
                <div className="grid grid-cols-2 gap-3">
                  <button 
                    onClick={() => setDeliveryType('window')}
                    className={`p-3 rounded-xl border flex flex-col items-center gap-2 transition-all ${deliveryType === 'window' ? 'bg-cyan-900/40 border-cyan-400 text-cyan-200' : 'bg-slate-700 border-slate-600 text-slate-400'}`}
                  >
                    <Crosshair size={24} />
                    <span className="text-xs text-center">Доставка в окно<br/>(DronePort)</span>
                  </button>
                  <button 
                    onClick={() => setDeliveryType('porch')}
                    className={`p-3 rounded-xl border flex flex-col items-center gap-2 transition-all ${deliveryType === 'porch' ? 'bg-cyan-900/40 border-cyan-400 text-cyan-200' : 'bg-slate-700 border-slate-600 text-slate-400'}`}
                  >
                    <Home size={24} />
                    <span className="text-xs text-center">На крыльцо<br/>(Спуск лебедкой)</span>
                  </button>
                </div>
              </div>
            )}

            {/* Список товаров */}
            <div className="flex-1 overflow-y-auto mb-6 border-t border-slate-700 pt-4 space-y-2">
              {cart.map((item, idx) => (
                <div key={idx} className="flex justify-between items-center text-sm bg-slate-900 p-2 rounded">
                  <span>{item.icon} {item.name}</span>
                  <button onClick={() => removeFromCart(idx)} className="text-slate-500 hover:text-red-400">
                    <X size={16} />
                  </button>
                </div>
              ))}
              {cart.length === 0 && <div className="text-slate-500 text-center text-sm italic mt-10">Корзина пуста</div>}
            </div>

            {showToast && (
              <div className="mb-4 p-3 bg-emerald-900/50 border border-emerald-500 text-emerald-300 rounded text-center text-sm animate-pulse">
                ✅ Заказ успешно добавлен в очередь!
              </div>
            )}

            <button 
              onClick={handleCheckout}
              disabled={cart.length === 0}
              className={`w-full py-4 rounded-xl font-bold text-lg transition-colors flex items-center justify-center gap-2
                ${cart.length === 0 
                  ? 'bg-slate-700 text-slate-500 cursor-not-allowed' 
                  : isOverweight ? 'bg-orange-600 hover:bg-orange-500 text-white' : 'bg-emerald-600 hover:bg-emerald-500 text-white'}`}
            >
              <CheckCircle2 /> 
              {isOverweight ? 'В очередь (Грузовик)' : 'В очередь (Дрон)'}
            </button>
            <button 
              onClick={() => setActiveTab('dashboard')}
              className="mt-4 text-slate-400 hover:text-white text-sm text-center w-full underline"
            >
              Перейти в Дашборд Оператора
            </button>
          </div>
        </div>
      </div>
    );
  }

  // --- РЕНДЕР: ДАШБОРД ОПЕРАТОРА ---
  // ВАЖНО: Мы перевели рендер карты с 0-100 на 0-200.
  // CSS `left` и `bottom` получают значение `(val / 200) * 100%`, то есть просто `val / 2`.
  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 font-sans overflow-hidden select-none">
      
      {/* ЛЕВАЯ ПАНЕЛЬ: ГОРОД И КАРТА (65%) */}
      <div className="w-[65%] relative border-r border-slate-800 bg-[#e5e5e0] shadow-inner overflow-hidden">
        
        {/* Кнопка возврата */}
        <button 
          onClick={() => setActiveTab('client')}
          className="absolute top-4 left-4 z-50 bg-slate-900 hover:bg-slate-800 p-2 rounded border border-slate-700 text-sm flex items-center gap-2 text-white shadow-lg"
        >
          <Plus size={16}/> Клиентское приложение
        </button>

        {/* СИНЯЯ ДОРОГА (Ось X=100 -> left: 50%) */}
        <div className="absolute top-0 bottom-0 left-1/2 w-10 -ml-5 bg-[#1e3a8a] flex justify-center shadow-[0_0_15px_rgba(30,58,138,0.2)]">
          <div className="w-1 h-full border-l-[3px] border-dashed border-white/40"></div>
        </div>

        {/* ПВЗ (Северный хаб в конце дороги. Y=176 -> bottom: 88%) */}
        <div 
          className="absolute z-10 bg-[#1e3a8a] border-4 border-[#3b82f6] rounded-lg shadow-[0_0_20px_rgba(59,130,246,0.4)] flex flex-col items-center justify-center"
          style={{ left: '50%', bottom: '88%', transform: 'translate(-50%, 50%)', width: '240px', height: '100px' }}
        >
          <span className="text-blue-100 font-black tracking-widest text-xl mb-1">ПВЗ СЕВЕР</span>
          <span className="text-blue-300 text-xs font-mono uppercase tracking-wider">Конечная точка маршрута</span>
        </div>

        {/* ЖЕЛТЫЙ СКЛАД (В начале дороги. Y=24 -> bottom: 12%) */}
        <div 
          className="absolute z-10 flex flex-col justify-between"
          style={{ left: '50%', bottom: '12%', transform: 'translate(-50%, 50%)', width: '260px', height: '180px' }}
        >
          {/* Левое и правое крыло с внутренним двором */}
          <div className="flex justify-between w-full h-[120px]">
             <div className="w-[70px] h-full bg-[#fbbf24] border-4 border-[#d97706] rounded-t-sm shadow-lg" />
             <div className="flex-1 flex items-end justify-center pb-2 opacity-60">
               <Package size={54} className="text-[#d97706]" />
             </div>
             <div className="w-[70px] h-full bg-[#fbbf24] border-4 border-[#d97706] rounded-t-sm shadow-lg" />
          </div>
          {/* Нижний соединяющий блок */}
          <div className="w-full h-[60px] bg-[#fbbf24] border-4 border-[#d97706] rounded-b-sm shadow-xl flex items-center justify-center relative z-20">
             <span className="text-slate-900 font-black tracking-widest text-xl">СУПЕР-ХАБ</span>
          </div>
        </div>

        {/* КРАСНЫЕ ДОМА (Умная квартальная застройка) */}
        {HOUSES.map(h => (
          <div 
            key={h.id} 
            className="absolute bg-[#e11d48] border-4 border-[#be123c] rounded shadow-2xl flex flex-col items-center justify-center text-white/40 font-bold overflow-hidden"
            style={{ 
              left: `${h.x / 2}%`, 
              bottom: `${h.y / 2}%`, 
              width: `${h.w}px`,
              height: `${h.h}px`,
              transform: `translate(-50%, 50%) rotate(${h.rot}deg)` 
            }}
          >
            {/* Анимация маркера, если дрон завис у этого дома */}
            {drone.status === 'HOVERING' && drone.targetOrder?.house.id === h.id && drone.targetOrder.deliveryType === 'window' && (
               <div className="absolute inset-0 border-[6px] border-cyan-400 animate-ping opacity-90"></div>
            )}
          </div>
        ))}

        {/* ЛИНИЯ МАРШРУТА ДРОНА */}
        {drone.status !== 'DOCKED' && (
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-10">
            <line 
              x1={`${truck.x / 2}%`} y1={`${100 - truck.y / 2}%`} 
              x2={`${drone.x / 2}%`} y2={`${100 - drone.y / 2}%`} 
              stroke="rgba(6, 182, 212, 0.6)" strokeWidth="3" strokeDasharray="6,6" 
            />
          </svg>
        )}

        {/* ГРУЗОВИК */}
        <div 
          className="absolute w-12 h-24 bg-slate-800 rounded-md shadow-[0_10px_25px_rgba(0,0,0,0.6)] z-20 flex flex-col items-center justify-end pb-2 border-b-4 border-slate-900 transition-transform"
          style={{ 
            left: `${truck.x / 2}%`, 
            bottom: `${truck.y / 2}%`, 
            transform: `translate(-50%, 50%) ${truck.direction === -1 ? 'rotate(180deg)' : ''}` 
          }}
        >
          <Truck size={20} className="text-white mb-2 opacity-50" />
          {/* Посадочная площадка на грузовике */}
          <div className="w-8 h-8 bg-slate-900 border border-cyan-500/50 rounded flex items-center justify-center relative">
            <div className="w-4 h-4 rounded-full bg-cyan-900 flex items-center justify-center">
              <span className="text-[8px] text-cyan-400 font-bold">H</span>
            </div>
            {/* Отрисовка дрона на базе, если он пристыкован */}
            {drone.status === 'DOCKED' && (
               <div className="absolute inset-0 flex items-center justify-center">
                 <Navigation size={18} fill="cyan" stroke="cyan" className="animate-pulse drop-shadow-[0_0_8px_rgba(6,182,212,1)]" />
               </div>
            )}
          </div>
        </div>

        {/* ЛЕТЯЩИЙ ДРОН */}
        {drone.status !== 'DOCKED' && (
          <div 
            className="absolute z-30 flex flex-col items-center"
            style={{ 
              left: `${drone.x / 2}%`, bottom: `${drone.y / 2}%`, 
              transform: 'translate(-50%, 50%)',
              transition: 'left 0.1s linear, bottom 0.1s linear' // Для сглаживания между тиками
            }}
          >
            <div className={`p-2 rounded-full ${drone.status === 'EMERGENCY_ABORT' ? 'bg-red-500/20' : 'bg-cyan-500/20'} backdrop-blur-sm border ${drone.status === 'EMERGENCY_ABORT' ? 'border-red-500' : 'border-cyan-500'} shadow-lg`}>
              <Navigation 
                size={24} 
                fill={drone.status === 'EMERGENCY_ABORT' ? "#ef4444" : "#06b6d4"} 
                className={`${drone.status === 'HOVERING' ? 'animate-bounce' : ''} ${drone.status === 'EMERGENCY_ABORT' ? 'animate-spin' : ''}`}
                style={{ 
                  transform: drone.status === 'RETURNING' || drone.status === 'EMERGENCY_ABORT' ? 'rotate(180deg)' : 'rotate(0deg)' 
                }} 
              />
            </div>
            {/* Подпись дрона */}
            <div className="mt-1 bg-slate-900/80 px-2 py-0.5 rounded text-[10px] font-mono border border-slate-700 text-cyan-300 shadow-md">
              DRN-01 [{Math.floor(drone.battery)}%]
            </div>
          </div>
        )}

      </div>

      {/* ПРАВАЯ ПАНЕЛЬ: ТЕЛЕМЕТРИЯ И УПРАВЛЕНИЕ (35%) */}
      <div className="w-[35%] flex flex-col bg-slate-950 p-4 border-l border-slate-800 z-40 overflow-y-auto custom-scrollbar relative">
        
        {/* Мигающий фон при тревоге */}
        {drone.status === 'EMERGENCY_ABORT' && (
          <div className="absolute inset-0 bg-red-900/20 animate-pulse pointer-events-none z-0"></div>
        )}

        <h1 className="text-xl font-bold text-white mb-6 tracking-wider flex items-center gap-2 relative z-10">
          <AlertOctagon className="text-cyan-500" /> HUB COMMAND
        </h1>

        {/* ТЕЛЕМЕТРИЯ ДРОНА */}
        <div className={`rounded-xl border p-4 mb-6 relative z-10 transition-colors ${drone.status === 'EMERGENCY_ABORT' ? 'bg-red-950/50 border-red-800' : 'bg-slate-900 border-slate-700'}`}>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Телеметрия дрона</h2>
            <span className={`px-2 py-1 text-xs font-mono rounded ${
              drone.status === 'DOCKED' ? 'bg-slate-800 text-slate-400' : 
              drone.status === 'EMERGENCY_ABORT' ? 'bg-red-600 text-white animate-pulse' : 
              'bg-cyan-900/50 text-cyan-400 border border-cyan-800'
            }`}>
              {drone.status}
            </span>
          </div>

          {/* Батарея */}
          <div className="mb-4">
            <div className="flex justify-between text-xs mb-1 font-mono">
              <span className="text-slate-400">SOC (Батарея)</span>
              <span className={drone.battery < 20 ? 'text-red-400' : drone.battery < 50 ? 'text-yellow-400' : 'text-emerald-400'}>
                {drone.battery.toFixed(1)}%
              </span>
            </div>
            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-500 ${drone.battery < 20 ? 'bg-red-500' : drone.battery < 50 ? 'bg-yellow-500' : 'bg-emerald-500'}`}
                style={{ width: `${drone.battery}%` }}
              />
            </div>
          </div>

          {/* Координаты и ETA */}
          <div className="grid grid-cols-2 gap-2 text-xs font-mono mb-4">
            <div className="bg-slate-950 p-2 rounded border border-slate-800 text-slate-400">
              POS: X: {(drone.x / 2).toFixed(1)} Y: {(drone.y / 2).toFixed(1)}
            </div>
            <div className="bg-slate-950 p-2 rounded border border-slate-800 text-slate-400">
              ETA: {drone.status !== 'DOCKED' && drone.status !== 'HOVERING' ? `${drone.eta.toFixed(1)}s` : '--'}
            </div>
          </div>

          {/* КАМЕРА FPV (Симуляция ArUco) */}
          <div className="relative w-full h-32 bg-black rounded-lg border border-slate-700 overflow-hidden flex items-center justify-center">
            {drone.status === 'HOVERING' && drone.targetOrder?.deliveryType === 'window' ? (
              <>
                <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] opacity-20 mix-blend-screen"></div>
                <div className="absolute top-2 left-2 text-[10px] text-green-500 font-mono flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span> REC
                </div>
                {/* Рамка захвата ArUco */}
                <div className="w-16 h-16 border-2 border-green-500 relative flex items-center justify-center">
                   <div className="absolute -top-1 -left-1 w-2 h-2 border-t-2 border-l-2 border-green-400"></div>
                   <div className="absolute -top-1 -right-1 w-2 h-2 border-t-2 border-r-2 border-green-400"></div>
                   <div className="absolute -bottom-1 -left-1 w-2 h-2 border-b-2 border-l-2 border-green-400"></div>
                   <div className="absolute -bottom-1 -right-1 w-2 h-2 border-b-2 border-r-2 border-green-400"></div>
                   <span className="text-green-500 font-mono text-[8px] animate-pulse">ARUCO_LOCKED</span>
                </div>
                <div className="absolute bottom-2 text-center w-full text-[10px] text-green-500 font-mono bg-black/50 py-1">
                  СКАНИРОВАНИЕ ФАСАДА... OK
                </div>
              </>
            ) : drone.status === 'HOVERING' && drone.targetOrder?.deliveryType === 'porch' ? (
              <div className="text-slate-500 font-mono text-xs flex flex-col items-center">
                <Camera size={24} className="mb-2 opacity-50"/>
                Спуск лебедки (Крыльцо)
              </div>
            ) : (
              <div className="text-slate-700 font-mono text-xs flex flex-col items-center">
                <Camera size={24} className="mb-2"/>
                КАМЕРА ОТКЛЮЧЕНА
              </div>
            )}
          </div>
        </div>

        {/* КНОПКА ЭКСТРЕННОГО ПРЕРЫВАНИЯ (Симуляция жеста) */}
        <button 
          onClick={triggerEmergency}
          disabled={drone.status === 'DOCKED' || drone.status === 'EMERGENCY_ABORT' || drone.status === 'RETURNING'}
          className={`relative z-10 w-full py-3 rounded-lg font-bold text-sm uppercase tracking-widest transition-all shadow-lg mb-6 border
            ${(drone.status === 'DOCKED' || drone.status === 'EMERGENCY_ABORT' || drone.status === 'RETURNING')
              ? 'bg-slate-800 text-slate-600 border-slate-700 cursor-not-allowed' 
              : 'bg-red-600 hover:bg-red-500 text-white border-red-500 hover:shadow-[0_0_15px_rgba(239,68,68,0.5)]'
            }`}
        >
          {drone.status === 'EMERGENCY_ABORT' ? 'Возврат на базу...' : 'ABORT (СИМУЛЯЦИЯ ЖЕСТА)'}
        </button>

        {/* ОЧЕРЕДЬ ЗАКАЗОВ И ЗАПУСК */}
        <div className="flex-1 relative z-10 flex flex-col">
          <div className="flex justify-between items-center mb-3">
            <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Очередь (TSP-D)</h2>
            <button 
              onClick={() => setIsDeliveryActive(!isDeliveryActive)}
              className={`px-4 py-1.5 rounded font-bold text-xs uppercase tracking-wide transition-all shadow-md ${
                isDeliveryActive
                  ? 'bg-orange-600 hover:bg-orange-500 text-white shadow-[0_0_10px_rgba(234,88,12,0.4)]'
                  : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-[0_0_10px_rgba(16,185,129,0.4)]'
              }`}
            >
              {isDeliveryActive ? 'ПРИОСТАНОВИТЬ' : 'НАЧАТЬ РАЗВОЗ'}
            </button>
          </div>
          
          <div className="space-y-3 overflow-y-auto pr-1">
            {orders.length === 0 && <div className="text-slate-600 text-sm italic text-center mt-10">Нет активных заказов</div>}
            {[...orders].reverse().map(order => (
              <div key={order.id} className="bg-slate-900 p-3 rounded-lg border border-slate-800 text-sm">
                <div className="flex justify-between items-center border-b border-slate-800 pb-2 mb-2">
                  <span className="font-mono text-cyan-500 font-bold">#{order.id}</span>
                  <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase
                    ${order.status === 'delivered' ? 'bg-emerald-900/50 text-emerald-400' : 
                      order.status === 'in_progress' ? 'bg-blue-900/50 text-blue-400' : 'bg-slate-800 text-slate-400'}`}>
                    {order.status}
                  </span>
                </div>
                <div className="text-slate-400 text-xs mb-2">
                  Dest: <span className="text-slate-200">{order.house.name}</span> | Type: {order.deliveryType}
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className={order.weight > 2.5 ? 'text-red-400' : 'text-slate-400'}>Wgt: {order.weight.toFixed(1)}kg</span>
                  <span className={`px-2 py-0.5 rounded border ${order.assignedTo === 'truck' ? 'border-orange-500 text-orange-400' : 'border-cyan-500 text-cyan-400'}`}>
                    {order.assignedTo === 'truck' ? 'TRUCK' : 'DRONE'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}