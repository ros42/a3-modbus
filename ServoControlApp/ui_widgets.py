"""
UI Widgets for Servo Control Application
Custom widgets for displaying register values in various formats
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QFontMetrics
import math


class GaugeWidget(QWidget):
    """Analog gauge widget for displaying numeric values"""
    
    def __init__(self, title: str = "", min_value: float = 0, max_value: float = 100, unit: str = ""):
        super().__init__()
        self.title = title
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = (min_value + max_value) / 2
        self.unit = unit
        
        self.setMinimumSize(200, 200)
        self.setMaximumSize(300, 300)
        
    def update_value(self, value: float):
        """Update the gauge value"""
        if value is not None:
            self.current_value = value
            self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 2 - 20
        
        # Draw background circle
        painter.setBrush(QBrush(QColor("#f0f0f0")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # Calculate angle based on value
        value_range = self.max_value - self.min_value
        if value_range != 0:
            normalized = (self.current_value - self.min_value) / value_range
        else:
            normalized = 0.5
        
        # Clamp normalized value
        normalized = max(0, min(1, normalized))
        
        # Gauge goes from -135° to +135° (270° total)
        start_angle = 135 * 16  # Qt uses 1/16th of a degree
        span_angle = -270 * 16
        
        # Draw arc background
        painter.setPen(QPen(QColor("#d0d0d0"), 8))
        painter.drawArc(center_x - radius, center_y - radius, radius * 2, radius * 2, 
                       start_angle, span_angle)
        
        # Draw value arc (green to red gradient based on value)
        if normalized < 0.5:
            color = QColor(0, 255, 0)
        elif normalized < 0.75:
            color = QColor(255, 255, 0)
        else:
            color = QColor(255, 0, 0)
        
        painter.setPen(QPen(color, 8))
        current_angle = start_angle + int(span_angle * normalized)
        painter.drawArc(center_x - radius, center_y - radius, radius * 2, radius * 2,
                       start_angle, current_angle - start_angle)
        
        # Draw needle
        needle_length = radius - 15
        needle_angle = math.radians(135 - 270 * normalized)
        needle_x = center_x + needle_length * math.cos(needle_angle)
        needle_y = center_y - needle_length * math.sin(needle_angle)
        
        painter.setPen(QPen(QColor("#333333"), 3))
        painter.drawLine(center_x, center_y, int(needle_x), int(needle_y))
        
        # Draw center dot
        painter.setBrush(QBrush(QColor("#333333")))
        painter.drawEllipse(center_x - 8, center_y - 8, 16, 16)
        
        # Draw title
        painter.setPen(QColor("#333333"))
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        title_rect = painter.fontMetrics().boundingRect(self.title)
        painter.drawText(center_x - title_rect.width() // 2, 30, self.title)
        
        # Draw value
        font = QFont("Arial", 18, QFont.Weight.Bold)
        painter.setFont(font)
        value_text = f"{self.current_value:.1f} {self.unit}"
        value_rect = painter.fontMetrics().boundingRect(value_text)
        painter.drawText(center_x - value_rect.width() // 2, center_y + 50, value_text)
        
        # Draw min/max labels
        font = QFont("Arial", 9)
        painter.setFont(font)
        painter.drawText(center_x - radius, center_y + radius - 10, f"{self.min_value}")
        painter.drawText(center_x + radius - 40, center_y + radius - 10, f"{self.max_value}")


class NumericDisplay(QWidget):
    """Numeric display widget"""
    
    def __init__(self, title: str = "", format_str: str = "{:.2f}", unit: str = ""):
        super().__init__()
        self.title = title
        self.format_str = format_str
        self.unit = unit
        self.current_value = 0.0
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.title_label)
        
        self.value_label = QLabel("0.00")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setFont(QFont("Consolas", 24, QFont.Weight.Bold))
        self.value_label.setStyleSheet("color: #0066cc; background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        layout.addWidget(self.value_label)
        
        self.unit_label = QLabel(unit)
        self.unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_label.setFont(QFont("Arial", 10))
        layout.addWidget(self.unit_label)
        
        self.setLayout(layout)
        self.setMinimumWidth(150)
    
    def update_value(self, value: float):
        """Update the displayed value"""
        if value is not None:
            self.current_value = value
            formatted = self.format_str.format(value)
            self.value_label.setText(f"{formatted} {self.unit}".strip())


class BitIndicator(QWidget):
    """Widget for displaying individual bits of a register"""
    
    def __init__(self, title: str = "", bits_config: list = None):
        super().__init__()
        self.title = title
        self.bits_config = bits_config or []
        self.current_value = 0
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # Bits grid
        self.bits_layout = QGridLayout()
        self.bit_labels = {}
        
        for i, bit_cfg in enumerate(self.bits_config):
            index = bit_cfg.get('index', i)
            label = bit_cfg.get('label', f'Bit {index}')
            color_on = bit_cfg.get('color_on', '#00FF00')
            color_off = bit_cfg.get('color_off', '#FF0000')
            
            bit_frame = QFrame()
            bit_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
            bit_frame.setMinimumHeight(40)
            
            bit_layout = QHBoxLayout(bit_frame)
            bit_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            bit_label = QLabel(label)
            bit_label.setFont(QFont("Arial", 9))
            bit_layout.addWidget(bit_label)
            
            status_label = QLabel("●")
            status_label.setFont(QFont("Arial", 16))
            status_label.setStyleSheet(f"color: {color_off};")
            bit_layout.addWidget(status_label)
            
            self.bits_layout.addWidget(bit_frame, i // 4, i % 4)
            self.bit_labels[index] = {'status': status_label, 'color_on': color_on, 'color_off': color_off}
        
        layout.addLayout(self.bits_layout)
        self.setLayout(layout)
    
    def update_value(self, value: int):
        """Update bit indicators based on value"""
        if value is not None:
            self.current_value = int(value)
            
            for bit_index, labels in self.bit_labels.items():
                is_set = bool(self.current_value & (1 << bit_index))
                color = labels['color_on'] if is_set else labels['color_off']
                labels['status'].setStyleSheet(f"color: {color};")


class HexDisplay(QWidget):
    """Widget for displaying value in hexadecimal format"""
    
    def __init__(self, title: str = ""):
        super().__init__()
        self.title = title
        self.current_value = 0
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title if title else "HEX")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 10))
        layout.addWidget(title_label)
        
        self.value_label = QLabel("0x0000")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        self.value_label.setStyleSheet("color: #cc6600;")
        layout.addWidget(self.value_label)
        
        self.setLayout(layout)
        self.setMinimumWidth(120)
    
    def update_value(self, value: int):
        """Update the hex display"""
        if value is not None:
            self.current_value = int(value)
            if self.current_value >= 0:
                self.value_label.setText(f"0x{self.current_value:04X}")
            else:
                # Handle negative numbers
                self.value_label.setText(f"-0x{abs(self.current_value):04X}")


class BinaryDisplay(QWidget):
    """Widget for displaying value in binary format"""
    
    def __init__(self, title: str = ""):
        super().__init__()
        self.title = title
        self.current_value = 0
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title if title else "BIN")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 10))
        layout.addWidget(title_label)
        
        self.value_label = QLabel("0000 0000 0000 0000")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setFont(QFont("Consolas", 12))
        self.value_label.setStyleSheet("color: #0066cc;")
        layout.addWidget(self.value_label)
        
        self.setLayout(layout)
        self.setMinimumWidth(180)
    
    def update_value(self, value: int):
        """Update the binary display"""
        if value is not None:
            self.current_value = int(value)
            # Handle both positive and negative values (16-bit representation)
            if self.current_value >= 0:
                bin_value = self.current_value & 0xFFFF
            else:
                bin_value = self.current_value & 0xFFFF
            
            bin_str = f"{bin_value:016b}"
            # Add space every 4 bits for readability
            formatted = ' '.join([bin_str[i:i+4] for i in range(0, 16, 4)])
            self.value_label.setText(formatted)


class ProgressBar(QWidget):
    """Simple progress bar widget"""
    
    def __init__(self, title: str = "", min_value: float = 0, max_value: float = 100):
        super().__init__()
        self.title = title
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = min_value
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        layout.addWidget(title_label)
        
        self.bar_frame = QFrame()
        self.bar_frame.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        self.bar_frame.setMinimumHeight(20)
        bar_layout = QVBoxLayout(self.bar_frame)
        bar_layout.setContentsMargins(2, 2, 2, 2)
        
        self.bar_label = QLabel("")
        self.bar_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.bar_label.setStyleSheet("background-color: #4CAF50; color: white; padding-left: 5px;")
        bar_layout.addWidget(self.bar_label)
        
        layout.addWidget(self.bar_frame)
        
        self.value_label = QLabel(f"{min_value}")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
        
        self.setLayout(layout)
    
    def update_value(self, value: float):
        """Update progress bar value"""
        if value is not None:
            self.current_value = value
            value_range = self.max_value - self.min_value
            
            if value_range > 0:
                percentage = ((value - self.min_value) / value_range) * 100
                percentage = max(0, min(100, percentage))
            else:
                percentage = 0
            
            self.bar_label.setStyleSheet(f"background-color: #4CAF50; width: {percentage}%;")
            self.bar_label.setText(f"{percentage:.0f}%")
            self.value_label.setText(f"{value:.2f}")
