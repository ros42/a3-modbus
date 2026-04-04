#!/usr/bin/env python3
"""
Config Editor Application - GUI for editing config.json
Compiled to exe using PyInstaller
"""

import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path


class ConfigEditorApp:
    """Main application for editing config.json"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Config Editor - Настройка конфигурации")
        self.root.geometry("900x700")
        
        self.config_path = None
        self.config_data = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Top toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(toolbar, text="Открыть файл", command=self.open_file).grid(row=0, column=0, padx=5)
        ttk.Button(toolbar, text="Сохранить", command=self.save_file).grid(row=0, column=1, padx=5)
        ttk.Button(toolbar, text="Сохранить как...", command=self.save_file_as).grid(row=0, column=2, padx=5)
        ttk.Button(toolbar, text="Создать новый", command=self.create_new).grid(row=0, column=3, padx=5)
        
        self.file_label = ttk.Label(toolbar, text="Файл не открыт")
        self.file_label.grid(row=0, column=4, padx=20)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Tabs
        self.general_tab = ttk.Frame(self.notebook, padding="10")
        self.modbus_tab = ttk.Frame(self.notebook, padding="10")
        self.read_regs_tab = ttk.Frame(self.notebook, padding="10")
        self.write_regs_tab = ttk.Frame(self.notebook, padding="10")
        self.ui_layout_tab = ttk.Frame(self.notebook, padding="10")
        self.json_tab = ttk.Frame(self.notebook, padding="10")
        
        self.notebook.add(self.general_tab, text="Общие")
        self.notebook.add(self.modbus_tab, text="Modbus настройки")
        self.notebook.add(self.read_regs_tab, text="Чтение регистров")
        self.notebook.add(self.write_regs_tab, text="Запись регистров")
        self.notebook.add(self.ui_layout_tab, text="UI Layout")
        self.notebook.add(self.json_tab, text="JSON вид")
        
        # Setup each tab
        self.setup_general_tab()
        self.setup_modbus_tab()
        self.setup_read_regs_tab()
        self.setup_write_regs_tab()
        self.setup_ui_layout_tab()
        self.setup_json_tab()
        
    def setup_general_tab(self):
        """Setup general settings tab"""
        # App name
        ttk.Label(self.general_tab, text="Имя приложения:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.app_name_var = tk.StringVar()
        ttk.Entry(self.general_tab, textvariable=self.app_name_var, width=50).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Version
        ttk.Label(self.general_tab, text="Версия:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.version_var = tk.StringVar()
        ttk.Entry(self.general_tab, textvariable=self.version_var, width=50).grid(row=1, column=1, sticky=tk.W, pady=5)
        
    def setup_modbus_tab(self):
        """Setup Modbus settings tab"""
        fields = [
            ("Порт:", "port", 0),
            ("Baudrate:", "baudrate", 1),
            ("Parity:", "parity", 2),
            ("Stopbits:", "stopbits", 3),
            ("Bytesize:", "bytesize", 4),
            ("Timeout:", "timeout", 5),
        ]
        
        self.modbus_vars = {}
        for i, (label, key, row) in enumerate(fields):
            ttk.Label(self.modbus_tab, text=label).grid(row=row, column=0, sticky=tk.W, pady=5)
            
            if key in ["baudrate", "stopbits", "bytesize"]:
                var = tk.IntVar()
            elif key == "timeout":
                var = tk.DoubleVar()
            else:
                var = tk.StringVar()
            
            self.modbus_vars[key] = var
            
            if key == "parity":
                combo = ttk.Combobox(self.modbus_tab, textvariable=var, width=47, values=["N", "E", "O"])
                combo.grid(row=row, column=1, sticky=tk.W, pady=5)
            elif key == "baudrate":
                combo = ttk.Combobox(self.modbus_tab, textvariable=var, width=47, 
                                    values=["2400", "4800", "9600", "19200", "38400", "57600", "115200"])
                combo.grid(row=row, column=1, sticky=tk.W, pady=5)
            else:
                entry = ttk.Entry(self.modbus_tab, textvariable=var, width=50)
                entry.grid(row=row, column=1, sticky=tk.W, pady=5)
    
    def setup_read_regs_tab(self):
        """Setup read registers tab"""
        # Fast group
        fast_frame = ttk.LabelFrame(self.read_regs_tab, text="Fast Group (быстрое чтение)", padding="10")
        fast_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10, padx=10)
        
        ttk.Label(fast_frame, text="Период (мс):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.fast_period_var = tk.IntVar()
        ttk.Spinbox(fast_frame, from_=10, to=10000, textvariable=self.fast_period_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Registers listbox with buttons
        self.fast_regs_listbox = tk.Listbox(fast_frame, height=8, width=80)
        self.fast_regs_listbox.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(fast_frame, text="Добавить регистр", command=lambda: self.add_register('fast')).grid(row=2, column=0, pady=5)
        ttk.Button(fast_frame, text="Редактировать", command=lambda: self.edit_register('fast')).grid(row=2, column=1, pady=5)
        ttk.Button(fast_frame, text="Удалить", command=lambda: self.delete_register('fast')).grid(row=2, column=2, pady=5)
        
        # Slow group
        slow_frame = ttk.LabelFrame(self.read_regs_tab, text="Slow Group (медленное чтение)", padding="10")
        slow_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10, padx=10)
        
        ttk.Label(slow_frame, text="Период (мс):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.slow_period_var = tk.IntVar()
        ttk.Spinbox(slow_frame, from_=10, to=10000, textvariable=self.slow_period_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        self.slow_regs_listbox = tk.Listbox(slow_frame, height=8, width=80)
        self.slow_regs_listbox.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(slow_frame, text="Добавить регистр", command=lambda: self.add_register('slow')).grid(row=2, column=0, pady=5)
        ttk.Button(slow_frame, text="Редактировать", command=lambda: self.edit_register('slow')).grid(row=2, column=1, pady=5)
        ttk.Button(slow_frame, text="Удалить", command=lambda: self.delete_register('slow')).grid(row=2, column=2, pady=5)
        
        self.fast_registers = []
        self.slow_registers = []
    
    def setup_write_regs_tab(self):
        """Setup write registers tab"""
        # Conditions listbox
        list_frame = ttk.Frame(self.write_regs_tab)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10, padx=10)
        self.write_regs_tab.columnconfigure(0, weight=1)
        self.write_regs_tab.rowconfigure(0, weight=1)
        
        self.conditions_listbox = tk.Listbox(list_frame, height=15, width=100)
        self.conditions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.conditions_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.conditions_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Buttons
        btn_frame = ttk.Frame(self.write_regs_tab)
        btn_frame.grid(row=1, column=0, sticky=tk.W, pady=10, padx=10)
        
        ttk.Button(btn_frame, text="Добавить условие", command=self.add_condition).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Редактировать", command=self.edit_condition).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_condition).grid(row=0, column=2, padx=5)
        
        self.write_conditions = []
    
    def setup_ui_layout_tab(self):
        """Setup UI layout tab"""
        # Widgets listbox
        list_frame = ttk.Frame(self.ui_layout_tab)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10, padx=10)
        self.ui_layout_tab.columnconfigure(0, weight=1)
        self.ui_layout_tab.rowconfigure(0, weight=1)
        
        self.widgets_listbox = tk.Listbox(list_frame, height=15, width=100)
        self.widgets_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.widgets_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.widgets_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Buttons
        btn_frame = ttk.Frame(self.ui_layout_tab)
        btn_frame.grid(row=1, column=0, sticky=tk.W, pady=10, padx=10)
        
        ttk.Button(btn_frame, text="Добавить виджет", command=self.add_widget).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Редактировать", command=self.edit_widget).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_widget).grid(row=0, column=2, padx=5)
        
        self.ui_widgets = []
    
    def setup_json_tab(self):
        """Setup JSON view tab"""
        # Text widget for raw JSON
        self.json_text = tk.Text(self.json_tab, wrap=tk.NONE, font=("Courier", 10))
        self.json_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10, padx=10)
        self.json_tab.columnconfigure(0, weight=1)
        self.json_tab.rowconfigure(0, weight=1)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(self.json_tab, orient=tk.VERTICAL, command=self.json_text.yview)
        y_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.json_text.configure(yscrollcommand=y_scrollbar.set)
        
        x_scrollbar = ttk.Scrollbar(self.json_tab, orient=tk.HORIZONTAL, command=self.json_text.xview)
        x_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.json_text.configure(xscrollcommand=x_scrollbar.set)
        
        # Update button
        ttk.Button(self.json_tab, text="Обновить из JSON", command=self.update_from_json).grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
    
    def open_file(self):
        """Open a config file"""
        filepath = filedialog.askopenfilename(
            title="Открыть файл конфигурации",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                
                self.config_path = filepath
                self.file_label.config(text=os.path.basename(filepath))
                self.load_data_to_ui()
                self.update_json_view()
                messagebox.showinfo("Успех", f"Файл {os.path.basename(filepath)} загружен!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")
    
    def save_file(self):
        """Save current config to file"""
        if not self.config_path:
            self.save_file_as()
            return
        
        try:
            self.collect_data_from_ui()
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Успех", "Конфигурация сохранена!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
    
    def save_file_as(self):
        """Save config to a new file"""
        filepath = filedialog.asksaveasfilename(
            title="Сохранить как",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            self.config_path = filepath
            self.file_label.config(text=os.path.basename(filepath))
            self.save_file()
    
    def create_new(self):
        """Create a new config"""
        if self.config_data and messagebox.askyesno("Подтверждение", "Текущие изменения будут потеряны. Продолжить?"):
            pass
        elif self.config_data:
            return
        
        self.config_data = {
            "app_name": "New Application",
            "version": "1.0.0",
            "modbus_settings": {
                "port": "/dev/ttyUSB0",
                "baudrate": 9600,
                "parity": "N",
                "stopbits": 1,
                "bytesize": 8,
                "timeout": 1.0
            },
            "read_registers": {
                "fast_group": {
                    "period_ms": 200,
                    "registers": []
                },
                "slow_group": {
                    "period_ms": 1000,
                    "registers": []
                }
            },
            "write_registers": {
                "conditions": []
            },
            "ui_layout": {
                "widgets": []
            }
        }
        
        self.config_path = None
        self.file_label.config(text="Новый файл")
        self.load_data_to_ui()
        self.update_json_view()
    
    def load_data_to_ui(self):
        """Load config data into UI controls"""
        # General tab
        self.app_name_var.set(self.config_data.get('app_name', ''))
        self.version_var.set(self.config_data.get('version', ''))
        
        # Modbus tab
        modbus = self.config_data.get('modbus_settings', {})
        for key, var in self.modbus_vars.items():
            value = modbus.get(key, '')
            if isinstance(var, tk.IntVar):
                var.set(int(value) if value else 0)
            elif isinstance(var, tk.DoubleVar):
                var.set(float(value) if value else 0.0)
            else:
                var.set(str(value))
        
        # Read registers tab
        read_regs = self.config_data.get('read_registers', {})
        fast_group = read_regs.get('fast_group', {})
        slow_group = read_regs.get('slow_group', {})
        
        self.fast_period_var.set(fast_group.get('period_ms', 200))
        self.slow_period_var.set(slow_group.get('period_ms', 1000))
        
        self.fast_registers = fast_group.get('registers', [])
        self.slow_registers = slow_group.get('registers', [])
        
        self.update_reg_listboxes()
        
        # Write registers tab
        write_regs = self.config_data.get('write_registers', {})
        self.write_conditions = write_regs.get('conditions', [])
        self.update_conditions_listbox()
        
        # UI layout tab
        ui_layout = self.config_data.get('ui_layout', {})
        self.ui_widgets = ui_layout.get('widgets', [])
        self.update_widgets_listbox()
    
    def collect_data_from_ui(self):
        """Collect data from UI controls into config_data"""
        # General
        self.config_data['app_name'] = self.app_name_var.get()
        self.config_data['version'] = self.version_var.get()
        
        # Modbus
        self.config_data['modbus_settings'] = {}
        for key, var in self.modbus_vars.items():
            value = var.get()
            if isinstance(var, tk.IntVar):
                self.config_data['modbus_settings'][key] = int(value) if value else 0
            elif isinstance(var, tk.DoubleVar):
                self.config_data['modbus_settings'][key] = float(value) if value else 0.0
            else:
                self.config_data['modbus_settings'][key] = str(value)
        
        # Read registers
        self.config_data['read_registers'] = {
            'fast_group': {
                'period_ms': self.fast_period_var.get(),
                'registers': self.fast_registers
            },
            'slow_group': {
                'period_ms': self.slow_period_var.get(),
                'registers': self.slow_registers
            }
        }
        
        # Write registers
        self.config_data['write_registers'] = {
            'conditions': self.write_conditions
        }
        
        # UI layout
        self.config_data['ui_layout'] = {
            'widgets': self.ui_widgets
        }
    
    def update_json_view(self):
        """Update JSON text view"""
        self.json_text.delete(1.0, tk.END)
        json_str = json.dumps(self.config_data, indent=4, ensure_ascii=False)
        self.json_text.insert(tk.END, json_str)
    
    def update_from_json(self):
        """Parse JSON from text widget and update UI"""
        try:
            json_str = self.json_text.get(1.0, tk.END)
            self.config_data = json.loads(json_str)
            self.load_data_to_ui()
            messagebox.showinfo("Успех", "Данные обновлены из JSON!")
        except json.JSONDecodeError as e:
            messagebox.showerror("Ошибка JSON", f"Неверный формат JSON:\n{str(e)}")
    
    # Register management methods
    def update_reg_listboxes(self):
        """Update register listboxes"""
        self.fast_regs_listbox.delete(0, tk.END)
        for reg in self.fast_registers:
            self.fast_regs_listbox.insert(tk.END, f"{reg['name']} (addr: {reg['address']}, type: {reg['data_type']})")
        
        self.slow_regs_listbox.delete(0, tk.END)
        for reg in self.slow_registers:
            self.slow_regs_listbox.insert(tk.END, f"{reg['name']} (addr: {reg['address']}, type: {reg['data_type']})")
    
    def add_register(self, group):
        """Add a new register"""
        dialog = RegisterDialog(self.root, "Добавить регистр")
        self.root.wait_window(dialog)  # Wait for dialog to close
        if dialog.result:
            reg = dialog.result
            if group == 'fast':
                self.fast_registers.append(reg)
            else:
                self.slow_registers.append(reg)
            self.update_reg_listboxes()
            self.update_json_view()
    
    def edit_register(self, group):
        """Edit selected register"""
        if group == 'fast':
            listbox = self.fast_regs_listbox
            regs = self.fast_registers
        else:
            listbox = self.slow_regs_listbox
            regs = self.slow_registers
        
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите регистр для редактирования")
            return
        
        index = selection[0]
        dialog = RegisterDialog(self.root, "Редактировать регистр", regs[index])
        self.root.wait_window(dialog)  # Wait for dialog to close
        if dialog.result:
            regs[index] = dialog.result
            self.update_reg_listboxes()
            self.update_json_view()
    
    def delete_register(self, group):
        """Delete selected register"""
        if group == 'fast':
            listbox = self.fast_regs_listbox
            regs = self.fast_registers
        else:
            listbox = self.slow_regs_listbox
            regs = self.slow_registers
        
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите регистр для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранный регистр?"):
            index = selection[0]
            regs.pop(index)
            self.update_reg_listboxes()
            self.update_json_view()
    
    # Condition management methods
    def update_conditions_listbox(self):
        """Update conditions listbox"""
        self.conditions_listbox.delete(0, tk.END)
        for cond in self.write_conditions:
            desc = cond.get('description', cond['name'])
            self.conditions_listbox.insert(tk.END, f"{cond['name']} - {desc}")
    
    def add_condition(self):
        """Add a new write condition"""
        dialog = ConditionDialog(self.root, "Добавить условие")
        self.root.wait_window(dialog)  # Wait for dialog to close
        if dialog.result:
            self.write_conditions.append(dialog.result)
            self.update_conditions_listbox()
            self.update_json_view()
    
    def edit_condition(self):
        """Edit selected condition"""
        selection = self.conditions_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите условие для редактирования")
            return
        
        index = selection[0]
        dialog = ConditionDialog(self.root, "Редактировать условие", self.write_conditions[index])
        self.root.wait_window(dialog)  # Wait for dialog to close
        if dialog.result:
            self.write_conditions[index] = dialog.result
            self.update_conditions_listbox()
            self.update_json_view()
    
    def delete_condition(self):
        """Delete selected condition"""
        selection = self.conditions_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите условие для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранное условие?"):
            index = selection[0]
            self.write_conditions.pop(index)
            self.update_conditions_listbox()
            self.update_json_view()
    
    # Widget management methods
    def update_widgets_listbox(self):
        """Update widgets listbox"""
        self.widgets_listbox.delete(0, tk.END)
        for widget in self.ui_widgets:
            desc = f"{widget['type']} - {widget.get('register', 'N/A')} - {widget.get('title', 'No title')}"
            pos = widget.get('position', {})
            desc += f" (row:{pos.get('row', 0)}, col:{pos.get('column', 0)})"
            self.widgets_listbox.insert(tk.END, desc)
    
    def add_widget(self):
        """Add a new UI widget"""
        dialog = WidgetDialog(self.root, "Добавить виджет")
        self.root.wait_window(dialog)  # Wait for dialog to close
        if dialog.result:
            self.ui_widgets.append(dialog.result)
            self.update_widgets_listbox()
            self.update_json_view()
    
    def edit_widget(self):
        """Edit selected widget"""
        selection = self.widgets_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите виджет для редактирования")
            return
        
        index = selection[0]
        dialog = WidgetDialog(self.root, "Редактировать виджет", self.ui_widgets[index])
        self.root.wait_window(dialog)  # Wait for dialog to close
        if dialog.result:
            self.ui_widgets[index] = dialog.result
            self.update_widgets_listbox()
            self.update_json_view()
    
    def delete_widget(self):
        """Delete selected widget"""
        selection = self.widgets_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите виджет для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранный виджет?"):
            index = selection[0]
            self.ui_widgets.pop(index)
            self.update_widgets_listbox()
            self.update_json_view()


class RegisterDialog(tk.Toplevel):
    """Dialog for adding/editing a register"""
    
    def __init__(self, parent, title, data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("500x450")
        self.resizable(True, True)
        
        self.result = None
        
        # Form fields
        fields = [
            ("Имя:", "name", tk.StringVar, data.get('name', '') if data else ''),
            ("Адрес:", "address", tk.IntVar, data.get('address', 0) if data else 0),
            ("Slave ID:", "slave_id", tk.IntVar, data.get('slave_id', 1) if data else 1),
            ("Тип данных:", "data_type", tk.StringVar, data.get('data_type', 'uint16') if data else 'uint16'),
        ]
        
        self.vars = {}
        for i, (label, key, var_type, default) in enumerate(fields):
            ttk.Label(self, text=label).grid(row=i, column=0, sticky=tk.W, pady=5, padx=10)
            
            if var_type == tk.StringVar:
                var = tk.StringVar(value=default)
                if key == 'data_type':
                    combo = ttk.Combobox(self, textvariable=var, width=40, 
                                        values=["int16", "uint16", "int32", "uint32", "float32"])
                    combo.grid(row=i, column=1, sticky=tk.W, pady=5)
                else:
                    ttk.Entry(self, textvariable=var, width=40).grid(row=i, column=1, sticky=tk.W, pady=5)
            elif var_type == tk.IntVar:
                var = tk.IntVar(value=default)
                if key == 'slave_id':
                    ttk.Spinbox(self, from_=1, to=247, textvariable=var, width=37).grid(row=i, column=1, sticky=tk.W, pady=5)
                else:
                    ttk.Spinbox(self, from_=0, to=65535, textvariable=var, width=37).grid(row=i, column=1, sticky=tk.W, pady=5)
            else:  # DoubleVar
                var = tk.DoubleVar(value=default)
                ttk.Entry(self, textvariable=var, width=40).grid(row=i, column=1, sticky=tk.W, pady=5)
            
            self.vars[key] = var
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="OK", command=self.ok).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.cancel).grid(row=0, column=1, padx=10)
        
        self.grab_set()
    
    def ok(self):
        """Save and close"""
        try:
            self.result = {
                'name': self.vars['name'].get(),
                'address': self.vars['address'].get(),
                'slave_id': self.vars['slave_id'].get(),
                'data_type': self.vars['data_type'].get()
            }
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Проверьте введенные данные:\n{str(e)}")
    
    def cancel(self):
        """Close without saving"""
        self.destroy()


class ConditionDialog(tk.Toplevel):
    """Dialog for adding/editing a write condition"""
    
    def __init__(self, parent, title, data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("550x500")
        self.resizable(True, True)
        
        self.result = None
        
        # Basic fields
        ttk.Label(self, text="Имя условия:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        self.name_var = tk.StringVar(value=data.get('name', '') if data else '')
        ttk.Entry(self, textvariable=self.name_var, width=50).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self, text="Адрес регистра:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        self.addr_var = tk.IntVar(value=data.get('register_address', 0) if data else 0)
        ttk.Spinbox(self, from_=0, to=65535, textvariable=self.addr_var, width=47).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self, text="Записываемое значение:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        self.value_var = tk.IntVar(value=data.get('write_value', 0) if data else 0)
        ttk.Spinbox(self, from_=-32768, to=65535, textvariable=self.value_var, width=47).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self, text="Тип условия:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=10)
        self.condition_type_var = tk.StringVar(value=data.get('condition_type', 'value_greater') if data else 'value_greater')
        condition_types = ["value_greater", "value_less", "bit_true", "bit_false"]
        combo = ttk.Combobox(self, textvariable=self.condition_type_var, width=47, values=condition_types)
        combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self, text="Исходный регистр:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=10)
        self.source_var = tk.StringVar(value=data.get('source_register', '') if data else '')
        ttk.Entry(self, textvariable=self.source_var, width=50).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self, text="Порог (threshold):").grid(row=5, column=0, sticky=tk.W, pady=5, padx=10)
        self.threshold_var = tk.DoubleVar(value=data.get('threshold', 0.0) if data else 0.0)
        ttk.Entry(self, textvariable=self.threshold_var, width=50).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self, text="Индекс бита:").grid(row=6, column=0, sticky=tk.W, pady=5, padx=10)
        self.bit_index_var = tk.IntVar(value=data.get('bit_index', 0) if data else 0)
        ttk.Spinbox(self, from_=0, to=15, textvariable=self.bit_index_var, width=47).grid(row=6, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self, text="Описание:").grid(row=7, column=0, sticky=tk.W, pady=5, padx=10)
        self.desc_var = tk.StringVar(value=data.get('description', '') if data else '')
        ttk.Entry(self, textvariable=self.desc_var, width=50).grid(row=7, column=1, sticky=tk.W, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="OK", command=self.ok).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.cancel).grid(row=0, column=1, padx=10)
        
        self.grab_set()
    
    def ok(self):
        """Save and close"""
        try:
            self.result = {
                'name': self.name_var.get(),
                'register_address': self.addr_var.get(),
                'write_value': self.value_var.get(),
                'condition_type': self.condition_type_var.get(),
                'source_register': self.source_var.get(),
                'threshold': self.threshold_var.get(),
                'bit_index': self.bit_index_var.get(),
                'description': self.desc_var.get()
            }
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Проверьте введенные данные:\n{str(e)}")
    
    def cancel(self):
        """Close without saving"""
        self.destroy()


class WidgetDialog(tk.Toplevel):
    """Dialog for adding/editing a UI widget"""
    
    def __init__(self, parent, title, data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("550x550")
        self.resizable(True, True)
        
        self.result = None
        
        # Type
        ttk.Label(self, text="Тип виджета:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        self.type_var = tk.StringVar(value=data.get('type', 'gauge') if data else 'gauge')
        widget_types = ["gauge", "numeric_display", "bit_indicator", "hex_display", "binary_display"]
        combo = ttk.Combobox(self, textvariable=self.type_var, width=47, values=widget_types)
        combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Register
        ttk.Label(self, text="Регистр:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        self.register_var = tk.StringVar(value=data.get('register', '') if data else '')
        ttk.Entry(self, textvariable=self.register_var, width=50).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Title
        ttk.Label(self, text="Заголовок:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        self.title_var = tk.StringVar(value=data.get('title', '') if data else '')
        ttk.Entry(self, textvariable=self.title_var, width=50).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Position
        ttk.Label(self, text="Строка (row):").grid(row=3, column=0, sticky=tk.W, pady=5, padx=10)
        self.row_var = tk.IntVar(value=data.get('position', {}).get('row', 0) if data else 0)
        ttk.Spinbox(self, from_=0, to=100, textvariable=self.row_var, width=47).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self, text="Колонка (column):").grid(row=4, column=0, sticky=tk.W, pady=5, padx=10)
        self.col_var = tk.IntVar(value=data.get('position', {}).get('column', 0) if data else 0)
        ttk.Spinbox(self, from_=0, to=100, textvariable=self.col_var, width=47).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self, text="Colspan:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=10)
        self.colspan_var = tk.IntVar(value=data.get('position', {}).get('colspan', 1) if data else 1)
        ttk.Spinbox(self, from_=1, to=10, textvariable=self.colspan_var, width=47).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Gauge-specific
        ttk.Label(self, text="Min значение:").grid(row=6, column=0, sticky=tk.W, pady=5, padx=10)
        self.min_var = tk.IntVar(value=data.get('min_value', 0) if data else 0)
        ttk.Entry(self, textvariable=self.min_var, width=50).grid(row=6, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self, text="Max значение:").grid(row=7, column=0, sticky=tk.W, pady=5, padx=10)
        self.max_var = tk.IntVar(value=data.get('max_value', 100) if data else 100)
        ttk.Entry(self, textvariable=self.max_var, width=50).grid(row=7, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self, text="Единица измерения:").grid(row=8, column=0, sticky=tk.W, pady=5, padx=10)
        self.unit_var = tk.StringVar(value=data.get('unit', '') if data else '')
        ttk.Entry(self, textvariable=self.unit_var, width=50).grid(row=8, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self, text="Формат:").grid(row=9, column=0, sticky=tk.W, pady=5, padx=10)
        self.format_var = tk.StringVar(value=data.get('format', '{:.2f}') if data else '{:.2f}')
        ttk.Entry(self, textvariable=self.format_var, width=50).grid(row=9, column=1, sticky=tk.W, pady=5)
        
        # Bits configuration for bit_indicator
        ttk.Label(self, text="Биты (JSON):").grid(row=10, column=0, sticky=tk.W, pady=5, padx=10)
        self.bits_text = tk.Text(self, height=5, width=50)
        self.bits_text.grid(row=10, column=1, sticky=tk.W, pady=5)
        if data and data.get('type') == 'bit_indicator' and 'bits' in data:
            self.bits_text.insert(tk.END, json.dumps(data['bits'], indent=2))
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=11, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="OK", command=self.ok).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.cancel).grid(row=0, column=1, padx=10)
        
        self.grab_set()
    
    def ok(self):
        """Save and close"""
        try:
            result = {
                'type': self.type_var.get(),
                'register': self.register_var.get(),
                'title': self.title_var.get(),
                'position': {
                    'row': self.row_var.get(),
                    'column': self.col_var.get(),
                    'colspan': self.colspan_var.get()
                }
            }
            
            if self.type_var.get() == 'gauge':
                result['min_value'] = self.min_var.get()
                result['max_value'] = self.max_var.get()
                result['unit'] = self.unit_var.get()
            elif self.type_var.get() == 'numeric_display':
                result['format'] = self.format_var.get()
                result['unit'] = self.unit_var.get()
            elif self.type_var.get() == 'bit_indicator':
                bits_str = self.bits_text.get(1.0, tk.END).strip()
                if bits_str:
                    result['bits'] = json.loads(bits_str)
            
            self.result = result
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Проверьте введенные данные:\n{str(e)}")
    
    def cancel(self):
        """Close without saving"""
        self.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ConfigEditorApp(root)
    
    # Try to open config.json from same directory if exists
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_config = os.path.join(script_dir, 'config.json')
    
    if os.path.exists(default_config):
        try:
            with open(default_config, 'r', encoding='utf-8') as f:
                app.config_data = json.load(f)
            app.config_path = default_config
            app.file_label.config(text=os.path.basename(default_config))
            app.load_data_to_ui()
            app.update_json_view()
        except Exception:
            pass
    
    root.mainloop()


if __name__ == "__main__":
    main()
