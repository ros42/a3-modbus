"""
Register Manager - Manages read/write registers and conditions
Handles register organization, value storage, and condition checking
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum


@dataclass
class ReadRegister:
    """Represents a register to be read from Modbus device"""
    name: str
    address: int
    slave_id: int = 1
    data_type: str = "uint16"
    scale: float = 1.0
    offset: float = 0.0
    value: Optional[float] = None
    
    def get_scaled_value(self) -> Optional[float]:
        """Get the scaled and offset value"""
        if self.value is None:
            return None
        return self.value * self.scale + self.offset


@dataclass
class WriteCondition:
    """Represents a conditional write operation"""
    name: str
    register_address: int
    write_value: int
    condition_type: str  # value_greater, value_less, bit_true, bit_false
    source_register: str
    threshold: Optional[float] = None
    bit_index: Optional[int] = None
    description: str = ""
    last_triggered: bool = False


class RegisterManager:
    """Manages all registers and write conditions"""
    
    def __init__(self):
        self.registers: Dict[str, ReadRegister] = {}
        self.slave_groups: Dict[int, List[str]] = {}  # slave_id -> list of register names
        self.write_conditions: List[WriteCondition] = []
        self.memory_registers: Dict[str, Any] = {}  # Intermediate memory registers
    
    def add_register(self, register: ReadRegister, slave_id: int = None):
        """
        Add a register to be monitored
        
        Args:
            register: ReadRegister object
            slave_id: Slave ID for this register (from register.slave_id if not specified)
        """
        self.registers[register.name] = register
        
        # Use provided slave_id or from register
        sid = slave_id if slave_id is not None else register.slave_id
        
        if sid not in self.slave_groups:
            self.slave_groups[sid] = []
        
        if register.name not in self.slave_groups[sid]:
            self.slave_groups[sid].append(register.name)
    
    def remove_register(self, name: str):
        """Remove a register by name"""
        if name in self.registers:
            # Remove from all slave groups
            for sid in self.slave_groups:
                if name in self.slave_groups[sid]:
                    self.slave_groups[sid].remove(name)
            del self.registers[name]
    
    def update_register_value(self, name: str, value: float):
        """Update the value of a register"""
        if name in self.registers:
            self.registers[name].value = value
    
    def get_register_value(self, name: str) -> Optional[float]:
        """Get the current value of a register"""
        if name in self.registers:
            reg = self.registers[name]
            return reg.get_scaled_value()
        return None
    
    def get_raw_register_value(self, name: str) -> Optional[float]:
        """Get the raw (unscaled) value of a register"""
        if name in self.registers:
            return self.registers[name].value
        return None
    
    def get_all_values(self) -> Dict[str, Any]:
        """Get all register values as a dictionary"""
        values = {}
        for name, reg in self.registers.items():
            values[name] = reg.get_scaled_value()
        # Include memory registers
        values.update(self.memory_registers)
        return values
    
    def get_slave_group_registers(self, slave_id: int) -> List[ReadRegister]:
        """Get all registers for a specific slave ID"""
        if slave_id not in self.slave_groups:
            return []
        return [self.registers[name] for name in self.slave_groups[slave_id] if name in self.registers]
    
    def get_all_slave_ids(self) -> List[int]:
        """Get list of all configured slave IDs"""
        return list(self.slave_groups.keys())
    
    def add_memory_register(self, name: str, initial_value: Any = None):
        """Add an intermediate memory register"""
        self.memory_registers[name] = initial_value
    
    def update_memory_register(self, name: str, value: Any):
        """Update a memory register value"""
        self.memory_registers[name] = value
    
    def get_memory_register(self, name: str) -> Any:
        """Get a memory register value"""
        return self.memory_registers.get(name)
    
    def remove_memory_register(self, name: str):
        """Remove a memory register"""
        if name in self.memory_registers:
            del self.memory_registers[name]
    
    def add_write_condition(self, condition: WriteCondition):
        """Add a write condition"""
        self.write_conditions.append(condition)
    
    def remove_write_condition(self, name: str):
        """Remove a write condition by name"""
        self.write_conditions = [c for c in self.write_conditions if c.name != name]
    
    def check_bit(self, value: int, bit_index: int) -> bool:
        """Check if a specific bit is set"""
        if value is None:
            return False
        return bool(value & (1 << bit_index))
    
    def check_write_conditions(self, current_values: Dict[str, Any]) -> List[Tuple[int, int]]:
        """
        Check all write conditions and return list of (address, value) tuples to write
        
        Args:
            current_values: Dictionary of current register values
        
        Returns:
            List of (register_address, write_value) tuples
        """
        writes_to_perform = []
        
        for condition in self.write_conditions:
            source_value = current_values.get(condition.source_register)
            
            if source_value is None:
                continue
            
            should_write = False
            
            if condition.condition_type == "value_greater":
                if condition.threshold is not None and source_value > condition.threshold:
                    should_write = True
                    
            elif condition.condition_type == "value_less":
                if condition.threshold is not None and source_value < condition.threshold:
                    should_write = True
                    
            elif condition.condition_type == "bit_true":
                if condition.bit_index is not None:
                    # Convert to int for bit operations
                    int_value = int(source_value)
                    if self.check_bit(int_value, condition.bit_index):
                        should_write = True
                        
            elif condition.condition_type == "bit_false":
                if condition.bit_index is not None:
                    int_value = int(source_value)
                    if not self.check_bit(int_value, condition.bit_index):
                        should_write = True
            
            # Only trigger on state change to avoid continuous writing
            if should_write and not condition.last_triggered:
                writes_to_perform.append((condition.register_address, condition.write_value))
                condition.last_triggered = True
            elif not should_write:
                condition.last_triggered = False
        
        return writes_to_perform
    
    def get_register_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a register"""
        if name not in self.registers:
            return None
        
        reg = self.registers[name]
        # Find which slave group this register belongs to
        slave_id = None
        for sid, names in self.slave_groups.items():
            if name in names:
                slave_id = sid
                break
        
        return {
            'name': reg.name,
            'address': reg.address,
            'slave_id': reg.slave_id,
            'data_type': reg.data_type,
            'scale': reg.scale,
            'offset': reg.offset,
            'current_value': reg.get_scaled_value(),
            'raw_value': reg.value,
            'slave_group': slave_id
        }
    
    def list_registers(self) -> List[Dict[str, Any]]:
        """List all registered registers"""
        return [self.get_register_info(name) for name in self.registers]
    
    def list_write_conditions(self) -> List[Dict[str, Any]]:
        """List all write conditions"""
        conditions_info = []
        for cond in self.write_conditions:
            conditions_info.append({
                'name': cond.name,
                'register_address': cond.register_address,
                'write_value': cond.write_value,
                'condition_type': cond.condition_type,
                'source_register': cond.source_register,
                'threshold': cond.threshold,
                'bit_index': cond.bit_index,
                'description': cond.description,
                'last_triggered': cond.last_triggered
            })
        return conditions_info
