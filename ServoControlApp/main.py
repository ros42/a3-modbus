"""
Servo Control Application - Modbus RTU USB-485 Drive Controller
Main application entry point
"""

import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QComboBox, QLineEdit, QSpinBox, QDialog, QDialogButtonBox, QGroupBox, QTabWidget, QMessageBox, QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QFont, QColor, QPalette
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import time

from modbus_client import ModbusClient
from register_manager import RegisterManager, ReadRegister, WriteCondition
from ui_widgets import GaugeWidget, NumericDisplay, BitIndicator, HexDisplay, BinaryDisplay


class DataType(Enum):
    INT16 = "int16"
    UINT16 = "uint16"
    INT32 = "int32"
    UINT32 = "uint32"
    FLOAT32 = "float32"


class ConditionType(Enum):
    VALUE_GREATER = "value_greater"
    VALUE_LESS = "value_less"
    BIT_TRUE = "bit_true"
    BIT_FALSE = "bit_false"


@dataclass
class ModbusSettings:
    port: str = "/dev/ttyUSB0"
    baudrate: int = 9600
    parity: str = "N"
    stopbits: int = 1
    bytesize: int = 8
    timeout: float = 1.0


class ConfigLoader:
    """Loads and validates configuration from JSON file"""
    
    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def parse_modbus_settings(config: Dict) -> ModbusSettings:
        settings = config.get('modbus_settings', {})
        return ModbusSettings(
            port=settings.get('port', '/dev/ttyUSB0'),
            baudrate=settings.get('baudrate', 9600),
            parity=settings.get('parity', 'N'),
            stopbits=settings.get('stopbits', 1),
            bytesize=settings.get('bytesize', 8),
            timeout=settings.get('timeout', 1.0)
        )
    
    @staticmethod
    def parse_read_registers(config: Dict) -> Dict[str, List[ReadRegister]]:
        read_config = config.get('read_registers', {})
        groups = {}
        
        for group_name, group_data in read_config.items():
            period_ms = group_data.get('period_ms', 1000)
            registers = []
            
            for reg in group_data.get('registers', []):
                registers.append(ReadRegister(
                    name=reg['name'],
                    address=reg['address'],
                    slave_id=reg.get('slave_id', 1),
                    data_type=reg.get('data_type', 'uint16'),
                    scale=reg.get('scale', 1.0),
                    offset=reg.get('offset', 0.0)
                ))
            
            groups[group_name] = {'period_ms': period_ms, 'registers': registers}
        
        return groups
    
    @staticmethod
    def parse_write_conditions(config: Dict) -> List[WriteCondition]:
        write_config = config.get('write_registers', {})
        conditions = []
        
        for cond in write_config.get('conditions', []):
            conditions.append(WriteCondition(
                name=cond['name'],
                register_address=cond['register_address'],
                write_value=cond['write_value'],
                condition_type=cond['condition_type'],
                source_register=cond['source_register'],
                threshold=cond.get('threshold'),
                bit_index=cond.get('bit_index'),
                description=cond.get('description', '')
            ))
        
        return conditions
    
    @staticmethod
    def parse_ui_layout(config: Dict) -> List[Dict]:
        return config.get('ui_layout', {}).get('widgets', [])


class WorkerThread(QThread):
    """Background thread for Modbus communication"""
    data_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, modbus_client: ModbusClient, register_manager: RegisterManager, groups_config: Dict):
        super().__init__()
        self.modbus_client = modbus_client
        self.register_manager = register_manager
        self.groups_config = groups_config  # {group_name: {'period_ms': int, 'registers': List[ReadRegister]}}
        self.running = False
    
    def run(self):
        self.running = True
        last_read_time = {group: 0.0 for group in self.groups_config}
        
        while self.running:
            current_time = time.time()
            
            try:
                # Read registers grouped by slave_id (no grouping logic - each slave independent)
                for group_name, group_data in self.groups_config.items():
                    period_ms = group_data.get('period_ms', 1000)
                    
                    if (current_time - last_read_time[group_name]) * 1000 >= period_ms:
                        for reg in group_data['registers']:
                            # Set slave_id for this read operation
                            self.modbus_client.set_slave_id(reg.slave_id)
                            
                            value = self.modbus_client.read_register(reg.address, reg.data_type)
                            if value is not None:
                                scaled_value = value * reg.scale + reg.offset
                                self.register_manager.update_register_value(reg.name, scaled_value)
                        
                        last_read_time[group_name] = current_time
                
                # Check write conditions
                all_values = self.register_manager.get_all_values()
                write_ops = self.register_manager.check_write_conditions(all_values)
                
                for addr, value in write_ops:
                    # Use slave_id from the first register or default to 1
                    success = self.modbus_client.write_register(addr, value)
                    if success:
                        print(f"Written {value} to register {addr}")
                
                # Emit data for UI
                self.data_ready.emit(all_values)
                
            except Exception as e:
                self.error_occurred.emit(str(e))
            
            time.sleep(0.05)  # Small delay to prevent CPU hogging
    
    def stop(self):
        self.running = False
        self.wait()


class SettingsDialog(QDialog):
    """Dialog for configuring Modbus settings"""
    
    def __init__(self, settings: ModbusSettings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки Modbus")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Port settings
        port_group = QGroupBox("Порт")
        port_layout = QGridLayout()
        
        self.port_edit = QLineEdit(settings.port)
        port_layout.addWidget(QLabel("Порт:"), 0, 0)
        port_layout.addWidget(self.port_edit, 0, 1)
        
        self.baudrate_combo = QComboBox()
        baudrates = ["2400", "4800", "9600", "19200", "38400", "57600", "115200"]
        self.baudrate_combo.addItems(baudrates)
        self.baudrate_combo.setCurrentText(str(settings.baudrate))
        port_layout.addWidget(QLabel("Скорость:"), 1, 0)
        port_layout.addWidget(self.baudrate_combo, 1, 1)
        
        port_group.setLayout(port_layout)
        layout.addWidget(port_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_settings(self) -> ModbusSettings:
        return ModbusSettings(
            port=self.port_edit.text(),
            baudrate=int(self.baudrate_combo.currentText())
        )


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config_path: str):
        super().__init__()
        self.config_path = config_path
        self.config = ConfigLoader.load_config(config_path)
        self.settings = ConfigLoader.parse_modbus_settings(self.config)
        
        self.register_manager = RegisterManager()
        self.modbus_client = ModbusClient(self.settings)
        self.worker_thread = None
        
        # Initialize registers from config
        self._initialize_registers()
        
        self.init_ui()
        self.setWindowTitle(f"{self.config.get('app_name', 'Servo Control')} v{self.config.get('version', '1.0')}")
    
    def _initialize_registers(self):
        """Initialize registers from configuration"""
        groups = ConfigLoader.parse_read_registers(self.config)
        
        for group_name, group_data in groups.items():
            for reg in group_data['registers']:
                # Add register with its slave_id
                self.register_manager.add_register(reg, reg.slave_id)
        
        # Add write conditions
        conditions = ConfigLoader.parse_write_conditions(self.config)
        for cond in conditions:
            self.register_manager.add_write_condition(cond)
        
        # Store groups config for worker thread
        self.groups_config = groups
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("Подключить")
        self.connect_btn.clicked.connect(self.toggle_connection)
        toolbar_layout.addWidget(self.connect_btn)
        
        self.settings_btn = QPushButton("Настройки")
        self.settings_btn.clicked.connect(self.open_settings)
        toolbar_layout.addWidget(self.settings_btn)
        
        self.status_label = QLabel("Отключено")
        self.status_label.setStyleSheet("color: red;")
        toolbar_layout.addWidget(self.status_label)
        
        toolbar_layout.addStretch()
        
        main_layout.addLayout(toolbar_layout)
        
        # Main content area with tabs
        self.tabs = QTabWidget()
        
        # Dashboard tab
        dashboard_widget = QWidget()
        self.dashboard_layout = QGridLayout()
        dashboard_widget.setLayout(self.dashboard_layout)
        self.tabs.addTab(dashboard_widget, "Панель управления")
        
        # Registers tab
        registers_widget = QWidget()
        self.registers_layout = QVBoxLayout()
        registers_widget.setLayout(self.registers_layout)
        self.tabs.addTab(registers_widget, "Регистры")
        
        main_layout.addWidget(self.tabs)
        
        central_widget.setLayout(main_layout)
        
        # Build UI from config
        self._build_ui_from_config()
    
    def _build_ui_from_config(self):
        """Build UI widgets based on configuration"""
        widgets_config = ConfigLoader.parse_ui_layout(self.config)
        
        self.ui_widgets = {}
        
        for widget_cfg in widgets_config:
            widget_type = widget_cfg.get('type')
            register_name = widget_cfg.get('register')
            title = widget_cfg.get('title', '')
            position = widget_cfg.get('position', {})
            
            row = position.get('row', 0)
            col = position.get('column', 0)
            colspan = position.get('colspan', 1)
            
            widget = None
            
            if widget_type == 'gauge':
                widget = GaugeWidget(
                    title=title,
                    min_value=widget_cfg.get('min_value', 0),
                    max_value=widget_cfg.get('max_value', 100),
                    unit=widget_cfg.get('unit', '')
                )
            elif widget_type == 'numeric_display':
                widget = NumericDisplay(
                    title=title,
                    format_str=widget_cfg.get('format', '{:.2f}'),
                    unit=widget_cfg.get('unit', '')
                )
            elif widget_type == 'bit_indicator':
                bits = widget_cfg.get('bits', [])
                widget = BitIndicator(title=title, bits_config=bits)
            elif widget_type == 'hex_display':
                widget = HexDisplay(title=title)
            elif widget_type == 'binary_display':
                widget = BinaryDisplay(title=title)
            
            if widget and register_name:
                self.ui_widgets[register_name] = widget
                self.dashboard_layout.addWidget(widget, row, col, 1, colspan)
        
        # Add stretch to fill remaining space
        self.dashboard_layout.setRowStretch(10, 1)
        self.dashboard_layout.setColumnStretch(10, 1)
    
    def toggle_connection(self):
        """Toggle Modbus connection"""
        if self.worker_thread is None:
            # Connect
            try:
                self.modbus_client.connect()
                self.worker_thread = WorkerThread(self.modbus_client, self.register_manager, self.groups_config)
                self.worker_thread.data_ready.connect(self.update_ui)
                self.worker_thread.error_occurred.connect(self.show_error)
                self.worker_thread.start()
                
                self.connect_btn.setText("Отключить")
                self.status_label.setText("Подключено")
                self.status_label.setStyleSheet("color: green;")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка подключения", str(e))
        else:
            # Disconnect
            self.worker_thread.stop()
            self.worker_thread.wait()
            self.worker_thread = None
            self.modbus_client.disconnect()
            
            self.connect_btn.setText("Подключить")
            self.status_label.setText("Отключено")
            self.status_label.setStyleSheet("color: red;")
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings = dialog.get_settings()
            # Save to config
            self.config['modbus_settings'] = {
                'port': self.settings.port,
                'baudrate': self.settings.baudrate
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
    
    def update_ui(self, values: Dict[str, Any]):
        """Update UI widgets with new values"""
        for name, value in values.items():
            if name in self.ui_widgets:
                self.ui_widgets[name].update_value(value)
    
    def show_error(self, error_msg: str):
        """Show error message"""
        self.status_label.setText(f"Ошибка: {error_msg}")
        self.status_label.setStyleSheet("color: orange;")
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.worker_thread:
            self.worker_thread.stop()
            self.worker_thread.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    config_path = "config.json"
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    
    window = MainWindow(config_path)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
