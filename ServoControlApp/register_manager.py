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
        self.fast_group: List[str] = []  # Names of registers in fast group (200ms)
        self.slow_group: List[str] = []  # Names of registers in slow group (1000ms)
        self.write_conditions: List[WriteCondition] = []
    
    def add_register(self, register: ReadRegister, group: str = "slow"):
        """
        Add a register to be monitored
        
        Args:
            register: ReadRegister object
            group: Group name ('fast' for 200ms, 'slow' for 1000ms)
        """
        self.registers[register.name] = register
        
        if group.lower() == 'fast' or 'fast' in group.lower():
            self.fast_group.append(register.name)
        else:
            self.slow_group.append(register.name)
    
    def remove_register(self, name: str):
        """Remove a register by name"""
        if name in self.registers:
            if name in self.fast_group:
                self.fast_group.remove(name)
            if name in self.slow_group:
                self.slow_group.remove(name)
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
        return values
    
    def get_fast_group_registers(self) -> List[ReadRegister]:
        """Get all registers in the fast group"""
        return [self.registers[name] for name in self.fast_group if name in self.registers]
    
    def get_slow_group_registers(self) -> List[ReadRegister]:
        """Get all registers in the slow group"""
        return [self.registers[name] for name in self.slow_group if name in self.registers]
    
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
        return {
            'name': reg.name,
            'address': reg.address,
            'data_type': reg.data_type,
            'scale': reg.scale,
            'offset': reg.offset,
            'current_value': reg.get_scaled_value(),
            'raw_value': reg.value,
            'group': 'fast' if name in self.fast_group else 'slow'
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
