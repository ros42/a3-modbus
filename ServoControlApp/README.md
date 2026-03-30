# Servo Control Application

Приложение для управления сервоприводами через USB-485 по протоколу Modbus RTU.

## Возможности

- **Чтение регистров** с двумя периодами опроса:
  - Быстрая группа: 200 мс (0.2 сек)
  - Медленная группа: 1000 мс (1 сек)

- **Запись регистров по условиям**:
  - Значение регистра больше порога
  - Значение регистра меньше порога
  - Определенный бит регистра = True
  - Определенный бит регистра = False

- **Настраиваемый интерфейс**:
  - Аналоговые индикаторы (Gauge)
  - Цифровые дисплеи
  - Индикаторы битов
  - Отображение в HEX и BIN форматах

- **Типы данных**:
  - int16, uint16
  - int32, uint32
  - float32

## Структура проекта

```
ServoControlApp/
├── main.py              # Главный файл приложения
├── modbus_client.py     # Клиент Modbus RTU
├── register_manager.py  # Менеджер регистров и условий
├── ui_widgets.py        # Пользовательские виджеты
├── config.json          # Файл конфигурации
├── build.py             # Скрипт сборки EXE
└── README.md            # Этот файл
```

## Установка зависимостей

```bash
pip install pyserial pymodbus PyQt6 pyinstaller
```

## Запуск приложения

```bash
python main.py [путь_к_конфигу]
```

По умолчанию используется `config.json` в текущей директории.

## Конфигурация

### Формат файла конфигурации (config.json)

#### Настройки Modbus

```json
{
    "modbus_settings": {
        "port": "/dev/ttyUSB0",
        "baudrate": 9600,
        "parity": "N",
        "stopbits": 1,
        "bytesize": 8,
        "timeout": 1.0,
        "slave_id": 1
    }
}
```

#### Регистры чтения

```json
{
    "read_registers": {
        "fast_group": {
            "period_ms": 200,
            "registers": [
                {
                    "name": "Motor_Speed",
                    "address": 1000,
                    "data_type": "int16",
                    "scale": 1.0,
                    "offset": 0.0
                }
            ]
        },
        "slow_group": {
            "period_ms": 1000,
            "registers": [...]
        }
    }
}
```

#### Условия записи

```json
{
    "write_registers": {
        "conditions": [
            {
                "name": "Enable_Motor",
                "register_address": 2000,
                "write_value": 1,
                "condition_type": "bit_true",
                "source_register": "Motor_Status",
                "bit_index": 0,
                "description": "Включить мотор когда бит 0 установлен"
            },
            {
                "name": "Disable_On_Overheat",
                "register_address": 2000,
                "write_value": 0,
                "condition_type": "value_greater",
                "source_register": "Motor_Temperature",
                "threshold": 80.0,
                "description": "Выключить мотор при перегреве > 80°C"
            }
        ]
    }
}
```

**Типы условий:**
- `value_greater` - значение больше порога
- `value_less` - значение меньше порога
- `bit_true` - бит установлен в 1
- `bit_false` - бит сброшен в 0

#### Настройка интерфейса

```json
{
    "ui_layout": {
        "widgets": [
            {
                "type": "gauge",
                "register": "Motor_Speed",
                "title": "Скорость мотора",
                "min_value": -3000,
                "max_value": 3000,
                "unit": "RPM",
                "position": {"row": 0, "column": 0}
            },
            {
                "type": "numeric_display",
                "register": "Motor_Temperature",
                "title": "Температура",
                "format": "{:.1f}",
                "unit": "°C",
                "position": {"row": 1, "column": 0}
            },
            {
                "type": "bit_indicator",
                "register": "Motor_Status",
                "title": "Статус мотора",
                "bits": [
                    {"index": 0, "label": "Motor Enabled", "color_on": "#00FF00", "color_off": "#FF0000"},
                    {"index": 1, "label": "Fault Active", "color_on": "#FF0000", "color_off": "#00FF00"}
                ],
                "position": {"row": 2, "column": 0, "colspan": 2}
            },
            {
                "type": "hex_display",
                "register": "Motor_Status",
                "title": "Статус (HEX)",
                "position": {"row": 3, "column": 0}
            },
            {
                "type": "binary_display",
                "register": "Motor_Status",
                "title": "Статус (BIN)",
                "position": {"row": 3, "column": 1}
            }
        ]
    }
}
```

**Типы виджетов:**
- `gauge` - аналоговый индикатор
- `numeric_display` - цифровой дисплей
- `bit_indicator` - индикаторы битов
- `hex_display` - отображение в HEX
- `binary_display` - отображение в BIN
- `progress_bar` - прогресс-бар

## Сборка в EXE

### Windows

```bash
python build.py
```

Для отладочной версии с консолью:

```bash
python build.py --debug
```

### Linux/Mac

```bash
python build.py
```

**Примечание:** В `build.py` для Linux/Mac замените `;` на `:` в строке `--add-data`.

## Использование

1. Откройте `config.json` и настройте параметры подключения Modbus
2. Добавьте регистры чтения в быструю или медленную группу
3. Настройте условия записи при необходимости
4. Настройте интерфейс под ваши нужды
5. Запустите приложение: `python main.py`
6. Нажмите "Настройки" для изменения параметров порта
7. Нажмите "Подключить" для начала работы

## Примеры использования

### Мониторинг температуры с аварийным отключением

```json
{
    "read_registers": {
        "slow_group": {
            "period_ms": 1000,
            "registers": [
                {
                    "name": "Temperature",
                    "address": 100,
                    "data_type": "int16",
                    "scale": 0.1,
                    "offset": 0.0
                }
            ]
        }
    },
    "write_registers": {
        "conditions": [
            {
                "name": "Emergency_Stop",
                "register_address": 200,
                "write_value": 0,
                "condition_type": "value_greater",
                "source_register": "Temperature",
                "threshold": 75.0
            }
        ]
    }
}
```

### Управление по битам статуса

```json
{
    "write_registers": {
        "conditions": [
            {
                "name": "Auto_Start",
                "register_address": 300,
                "write_value": 1,
                "condition_type": "bit_true",
                "source_register": "Status",
                "bit_index": 5
            }
        ]
    }
}
```

## Лицензия

MIT License
