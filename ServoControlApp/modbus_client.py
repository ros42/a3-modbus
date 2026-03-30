"""
Modbus RTU Client for USB-485 communication
Handles reading and writing registers via Modbus protocol
"""

from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
from dataclasses import dataclass
from typing import Optional, Any
import struct


@dataclass
class ModbusSettings:
    port: str = "/dev/ttyUSB0"
    baudrate: int = 9600
    parity: str = "N"
    stopbits: int = 1
    bytesize: int = 8
    timeout: float = 1.0
    slave_id: int = 1


class ModbusClient:
    """Modbus RTU client for USB-485 communication"""
    
    def __init__(self, settings: ModbusSettings):
        self.settings = settings
        self.client: Optional[ModbusSerialClient] = None
        self.connected = False
    
    def connect(self) -> bool:
        """Establish connection to Modbus device"""
        try:
            self.client = ModbusSerialClient(
                port=self.settings.port,
                baudrate=self.settings.baudrate,
                parity=self.settings.parity,
                stopbits=self.settings.stopbits,
                bytesize=self.settings.bytesize,
                timeout=self.settings.timeout
            )
            
            if self.client.connect():
                self.connected = True
                print(f"Connected to {self.settings.port}")
                return True
            else:
                raise Exception(f"Failed to connect to {self.settings.port}")
        except Exception as e:
            self.connected = False
            raise Exception(f"Connection error: {str(e)}")
    
    def disconnect(self):
        """Close Modbus connection"""
        if self.client:
            self.client.close()
            self.connected = False
            print("Disconnected")
    
    def read_register(self, address: int, data_type: str = "uint16", count: int = 1) -> Optional[Any]:
        """
        Read holding register(s) from Modbus device
        
        Args:
            address: Register address
            data_type: Type of data (int16, uint16, int32, uint32, float32)
            count: Number of registers to read (for 32-bit types, use 2)
        
        Returns:
            Decoded value or None if error
        """
        if not self.connected or not self.client:
            return None
        
        try:
            # Determine number of registers based on data type
            if data_type in ['int32', 'uint32', 'float32']:
                count = 2
            else:
                count = 1
            
            result = self.client.read_holding_registers(address, count, slave=self.settings.slave_id)
            
            if result.isError():
                print(f"Error reading register {address}: {result}")
                return None
            
            registers = result.registers
            
            # Decode based on data type
            if data_type == 'uint16':
                return registers[0]
            elif data_type == 'int16':
                return struct.unpack('>h', struct.pack('>H', registers[0]))[0]
            elif data_type == 'uint32':
                value = (registers[0] << 16) | registers[1]
                return value
            elif data_type == 'int32':
                value = (registers[0] << 16) | registers[1]
                return struct.unpack('>i', struct.pack('>I', value))[0]
            elif data_type == 'float32':
                value = (registers[0] << 16) | registers[1]
                return struct.unpack('>f', struct.pack('>I', value))[0]
            else:
                return registers[0]
                
        except ModbusException as e:
            print(f"Modbus error: {e}")
            return None
        except Exception as e:
            print(f"Read error: {e}")
            return None
    
    def write_register(self, address: int, value: int) -> bool:
        """
        Write to holding register
        
        Args:
            address: Register address
            value: Value to write
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.client:
            return False
        
        try:
            result = self.client.write_register(address, value, slave=self.settings.slave_id)
            
            if result.isError():
                print(f"Error writing register {address}: {result}")
                return False
            
            return True
            
        except ModbusException as e:
            print(f"Modbus write error: {e}")
            return False
        except Exception as e:
            print(f"Write error: {e}")
            return False
    
    def write_multiple_registers(self, address: int, values: list) -> bool:
        """
        Write to multiple holding registers
        
        Args:
            address: Starting register address
            values: List of values to write
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.client:
            return False
        
        try:
            result = self.client.write_registers(address, values, slave=self.settings.slave_id)
            
            if result.isError():
                print(f"Error writing registers at {address}: {result}")
                return False
            
            return True
            
        except ModbusException as e:
            print(f"Modbus write error: {e}")
            return False
        except Exception as e:
            print(f"Write error: {e}")
            return False
    
    def read_coils(self, address: int, count: int = 1) -> Optional[list]:
        """Read discrete coils"""
        if not self.connected or not self.client:
            return None
        
        try:
            result = self.client.read_coils(address, count, slave=self.settings.slave_id)
            
            if result.isError():
                return None
            
            return result.bits
            
        except Exception as e:
            print(f"Coil read error: {e}")
            return None
    
    def write_coil(self, address: int, value: bool) -> bool:
        """Write to discrete coil"""
        if not self.connected or not self.client:
            return False
        
        try:
            result = self.client.write_coil(address, value, slave=self.settings.slave_id)
            
            if result.isError():
                return False
            
            return True
            
        except Exception as e:
            print(f"Coil write error: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if connected to Modbus device"""
        return self.connected and self.client is not None
