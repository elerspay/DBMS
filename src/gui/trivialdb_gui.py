#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrivialDB 图形用户界面
基于Python Tkinter的数据库管理GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import subprocess
import os
import json
from pathlib import Path

class TrivialDBGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TrivialDB 图形管理界面")
        self.root.geometry("1200x800")
        
        # 数据库配置
        self.current_db = None
        
        # 读取配置文件
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                self.trivial_db_path = config.get("db_path", "../../build-win/bin/trivial_db.exe")
            except:
                self.trivial_db_path = "../../build-win/bin/trivial_db.exe"
        else:
            self.trivial_db_path = "../../build-win/bin/trivial_db.exe"
        
        # 初始化界面
        self.setup_ui()
        
    def setup_ui(self):
        """设置主界面布局"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 左侧导航栏
        nav_frame = ttk.LabelFrame(main_frame, text="数据库操作", padding="10")
        nav_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.N, tk.S, tk.W), padx=(0, 10))
        
        # 数据库选择/创建
        ttk.Button(nav_frame, text="创建数据库", command=self.create_database).grid(row=0, column=0, pady=5, sticky=tk.EW)
        ttk.Button(nav_frame, text="选择数据库", command=self.select_database).grid(row=1, column=0, pady=5, sticky=tk.EW)
        
        # 表操作
        ttk.Separator(nav_frame, orient='horizontal').grid(row=2, column=0, pady=10, sticky=tk.EW)
        ttk.Label(nav_frame, text="表操作").grid(row=3, column=0, pady=5)
        
        ttk.Button(nav_frame, text="创建表", command=self.create_table).grid(row=4, column=0, pady=2, sticky=tk.EW)
        ttk.Button(nav_frame, text="显示表结构", command=self.show_table_structure).grid(row=5, column=0, pady=2, sticky=tk.EW)
        ttk.Button(nav_frame, text="重命名表", command=self.rename_table).grid(row=6, column=0, pady=2, sticky=tk.EW)
        ttk.Button(nav_frame, text="修改表结构", command=self.alter_table).grid(row=7, column=0, pady=2, sticky=tk.EW)
        ttk.Button(nav_frame, text="删除表", command=self.drop_table).grid(row=8, column=0, pady=2, sticky=tk.EW)
        
        # 数据操作
        ttk.Separator(nav_frame, orient='horizontal').grid(row=9, column=0, pady=10, sticky=tk.EW)
        ttk.Label(nav_frame, text="数据操作").grid(row=10, column=0, pady=5)
        
        ttk.Button(nav_frame, text="插入数据", command=self.insert_data).grid(row=11, column=0, pady=2, sticky=tk.EW)
        ttk.Button(nav_frame, text="查询数据", command=self.query_data).grid(row=12, column=0, pady=2, sticky=tk.EW)
        ttk.Button(nav_frame, text="更新数据", command=self.update_data).grid(row=13, column=0, pady=2, sticky=tk.EW)
        ttk.Button(nav_frame, text="删除数据", command=self.delete_data).grid(row=14, column=0, pady=2, sticky=tk.EW)
        
        # SQL命令行
        ttk.Separator(nav_frame, orient='horizontal').grid(row=15, column=0, pady=10, sticky=tk.EW)
        ttk.Button(nav_frame, text="SQL命令行", command=self.open_sql_console).grid(row=16, column=0, pady=5, sticky=tk.EW)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 主显示区域
        display_frame = ttk.Frame(main_frame)
        display_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # 结果显示区域
        self.result_text = scrolledtext.ScrolledText(display_frame, width=80, height=30)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 数据库信息显示
        self.db_info_var = tk.StringVar(value="未选择数据库")
        db_info_label = ttk.Label(main_frame, textvariable=self.db_info_var)
        db_info_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
    
    def execute_sql(self, sql_command, require_db=True):
        """执行SQL命令并返回结果"""
        if require_db and not self.current_db:
            messagebox.showerror("错误", "请先选择或创建数据库")
            return None
        
        try:
            # 构建完整的SQL命令
            if require_db:
                full_command = f"USE {self.current_db};\n{sql_command}\nEXIT;"
            else:
                full_command = f"{sql_command}\nEXIT;"
            
            # 执行命令
            process = subprocess.Popen(
                [self.trivial_db_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=full_command)
            
            if stderr:
                messagebox.showerror("执行错误", stderr)
                return None
                
            return stdout
            
        except Exception as e:
            messagebox.showerror("错误", f"执行命令时出错: {str(e)}")
            return None
    
    def create_database(self):
        """创建数据库对话框"""
        def on_create():
            db_name = name_entry.get().strip()
            if not db_name:
                messagebox.showerror("错误", "数据库名称不能为空")
                return
                
            sql = f"CREATE DATABASE {db_name};"
            result = self.execute_sql(sql, require_db=False)
            
            if result and "Error" not in result:
                self.current_db = db_name
                self.db_info_var.set(f"当前数据库: {db_name}")
                self.status_var.set(f"数据库 {db_name} 创建成功")
                dialog.destroy()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("创建数据库")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="数据库名称:").pack(pady=10)
        name_entry = ttk.Entry(dialog, width=20)
        name_entry.pack(pady=5)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="创建", command=on_create).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def select_database(self):
        """选择数据库对话框"""
        def on_select():
            db_name = name_entry.get().strip()
            if not db_name:
                messagebox.showerror("错误", "数据库名称不能为空")
                return
                
            # 检查数据库是否存在
            sql = f"SHOW DATABASE {db_name};"
            result = self.execute_sql(sql, require_db=False)
            
            if result and "Error" not in result:
                self.current_db = db_name
                self.db_info_var.set(f"当前数据库: {db_name}")
                self.status_var.set(f"已选择数据库: {db_name}")
                dialog.destroy()
            else:
                messagebox.showerror("错误", f"数据库 {db_name} 不存在")
        
        dialog = tk.Toplevel(self.root)
        dialog.title("选择数据库")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="数据库名称:").pack(pady=10)
        name_entry = ttk.Entry(dialog, width=20)
        name_entry.pack(pady=5)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="选择", command=on_select).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def create_table(self):
        """创建表对话框"""
        def on_create():
            table_name = name_entry.get().strip()
            columns = columns_text.get("1.0", tk.END).strip()
            
            if not table_name or not columns:
                messagebox.showerror("错误", "表名和列定义不能为空")
                return
                
            sql = f"CREATE TABLE {table_name} ({columns});"
            result = self.execute_sql(sql)
            
            if result and "Error" not in result:
                self.status_var.set(f"表 {table_name} 创建成功")
                dialog.destroy()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("创建表")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="表名:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="列定义 (用逗号分隔):").pack(pady=5)
        columns_text = scrolledtext.ScrolledText(dialog, width=40, height=8)
        columns_text.pack(pady=5)
        columns_text.insert("1.0", "id INT PRIMARY KEY, name VARCHAR(50), age INT")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="创建", command=on_create).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def show_table_structure(self):
        """显示表结构"""
        table_name = simpledialog.askstring("显示表结构", "请输入表名:")
        if table_name:
            sql = f"SHOW TABLE {table_name};"
            result = self.execute_sql(sql)
            if result:
                self.display_result(result)
    
    def rename_table(self):
        """重命名表"""
        def on_rename():
            old_name = old_entry.get().strip()
            new_name = new_entry.get().strip()
            
            if not old_name or not new_name:
                messagebox.showerror("错误", "表名不能为空")
                return
                
            sql = f"RENAME TABLE {old_name} TO {new_name};"
            result = self.execute_sql(sql)
            
            if result and "Error" not in result:
                self.status_var.set(f"表 {old_name} 重命名为 {new_name}")
                dialog.destroy()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("重命名表")
        dialog.geometry("300x200")
        
        ttk.Label(dialog, text="原表名:").pack(pady=5)
        old_entry = ttk.Entry(dialog, width=20)
        old_entry.pack(pady=5)
        
        ttk.Label(dialog, text="新表名:").pack(pady=5)
        new_entry = ttk.Entry(dialog, width=20)
        new_entry.pack(pady=5)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="重命名", command=on_rename).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def display_result(self, result):
        """在结果显示区域显示结果"""
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", result)
    
    # 其他方法需要继续实现...
    def alter_table(self):
        """修改表结构对话框"""
        self.alter_dialog = tk.Toplevel(self.root)
        self.alter_dialog.title("修改表结构")
        self.alter_dialog.geometry("400x400")
        
        # 表名输入
        ttk.Label(self.alter_dialog, text="表名:").pack(pady=5)
        table_entry = ttk.Entry(self.alter_dialog, width=30)
        table_entry.pack(pady=5)
        
        # 操作选择
        ttk.Label(self.alter_dialog, text="操作类型:").pack(pady=5)
        operation_var = tk.StringVar(value="ADD")
        op_frame = ttk.Frame(self.alter_dialog)
        op_frame.pack(pady=5)
        
        ttk.Radiobutton(op_frame, text="添加列", variable=operation_var, value="ADD").pack(side=tk.LEFT)
        ttk.Radiobutton(op_frame, text="删除列", variable=operation_var, value="DROP").pack(side=tk.LEFT)
        ttk.Radiobutton(op_frame, text="重命名列", variable=operation_var, value="RENAME").pack(side=tk.LEFT)
        ttk.Radiobutton(op_frame, text="修改类型", variable=operation_var, value="MODIFY").pack(side=tk.LEFT)
        
        # 列名输入
        ttk.Label(self.alter_dialog, text="列名:").pack(pady=5)
        column_entry = ttk.Entry(self.alter_dialog, width=30)
        column_entry.pack(pady=5)
        
        # 新列名输入（重命名时使用）
        ttk.Label(self.alter_dialog, text="新列名 (重命名时):").pack(pady=5)
        new_column_entry = ttk.Entry(self.alter_dialog, width=30)
        new_column_entry.pack(pady=5)
        
        # 类型输入（添加/修改时使用）
        ttk.Label(self.alter_dialog, text="数据类型 (添加/修改时):").pack(pady=5)
        type_entry = ttk.Entry(self.alter_dialog, width=30)
        type_entry.pack(pady=5)
        type_entry.insert(0, "INT")
        
        def on_alter():
            table_name = table_entry.get().strip()
            operation = operation_var.get()
            column_name = column_entry.get().strip()
            new_column_name = new_column_entry.get().strip()
            new_type = type_entry.get().strip()
            
            if not table_name:
                messagebox.showerror("错误", "表名不能为空")
                return
                
            sql = ""
            if operation == "ADD":
                if not column_name or not new_type:
                    messagebox.showerror("错误", "列名和类型不能为空")
                    return
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {new_type};"
            elif operation == "DROP":
                if not column_name:
                    messagebox.showerror("错误", "列名不能为空")
                    return
                sql = f"ALTER TABLE {table_name} DROP COLUMN {column_name};"
            elif operation == "RENAME":
                if not column_name or not new_column_name:
                    messagebox.showerror("错误", "原列名和新列名不能为空")
                    return
                sql = f"ALTER TABLE {table_name} RENAME COLUMN {column_name} TO {new_column_name};"
            elif operation == "MODIFY":
                if not column_name or not new_type:
                    messagebox.showerror("错误", "列名和类型不能为空")
                    return
                sql = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} {new_type};"
            
            try:
                result = self.execute_sql(sql)
                if result is None:
                    return  # execute_sql已经显示了错误信息
                
                if "Error" in result:
                    messagebox.showerror("错误", result)
                    return
                
                self.status_var.set(f"表 {table_name} 修改成功")
                # 直接关闭对话框，不再使用after方法
                self.alter_dialog.destroy()
            except Exception as e:
                messagebox.showerror("系统错误", f"执行命令时出错: {str(e)}")
                # 直接关闭对话框，不再使用after方法
                self.alter_dialog.destroy()
        
        btn_frame = ttk.Frame(self.alter_dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="执行", command=on_alter).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.alter_dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def drop_table(self):
        """删除表对话框"""
        def on_drop():
            table_name = name_entry.get().strip()
            if not table_name:
                messagebox.showerror("错误", "表名不能为空")
                return
                
            # 确认对话框
            if not messagebox.askyesno("确认", f"确定要删除表 {table_name} 吗？此操作不可恢复！"):
                return
                
            sql = f"DROP TABLE {table_name};"
            result = self.execute_sql(sql)
            
            if result and "Error" not in result:
                self.status_var.set(f"表 {table_name} 删除成功")
                dialog.destroy()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("删除表")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="表名:").pack(pady=10)
        name_entry = ttk.Entry(dialog, width=20)
        name_entry.pack(pady=5)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="删除", command=on_drop).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def insert_data(self):
        """插入数据对话框"""
        def on_insert():
            table_name = table_entry.get().strip()
            values = values_text.get("1.0", tk.END).strip()
            
            if not table_name or not values:
                messagebox.showerror("错误", "表名和值不能为空")
                return
            
            # 解析多行值
            value_lines = [v.strip() for v in values.split('\n') if v.strip()]
            
            for val_line in value_lines:
                sql = f"INSERT INTO {table_name} VALUES ({val_line});"
                result = self.execute_sql(sql)
                if result and "Error" in result:
                    messagebox.showerror("插入错误", f"插入失败: {result}")
                    return
            
            self.status_var.set(f"成功插入 {len(value_lines)} 条数据到表 {table_name}")
            dialog.destroy()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("插入数据")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="表名:").pack(pady=5)
        table_entry = ttk.Entry(dialog, width=30)
        table_entry.pack(pady=5)
        
        ttk.Label(dialog, text="值 (每行一条记录):").pack(pady=5)
        values_text = scrolledtext.ScrolledText(dialog, width=40, height=8)
        values_text.pack(pady=5)
        values_text.insert("1.0", "1, 'Alice', 25\n2, 'Bob', 30")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="插入", command=on_insert).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def query_data(self):
        """查询数据对话框"""
        def on_query():
            table_name = table_entry.get().strip()
            condition = condition_entry.get().strip()
            
            if not table_name:
                messagebox.showerror("错误", "表名不能为空")
                return
                
            sql = f"SELECT * FROM {table_name}"
            if condition:
                sql += f" WHERE {condition}"
            sql += ";"
            
            result = self.execute_sql(sql)
            if result:
                self.display_result(result)
                dialog.destroy()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("查询数据")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="表名:").pack(pady=5)
        table_entry = ttk.Entry(dialog, width=30)
        table_entry.pack(pady=5)
        
        ttk.Label(dialog, text="条件 (可选):").pack(pady=5)
        condition_entry = ttk.Entry(dialog, width=30)
        condition_entry.pack(pady=5)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="查询", command=on_query).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def update_data(self):
        """更新数据对话框"""
        def on_update():
            table_name = table_entry.get().strip()
            set_clause = set_entry.get().strip()
            condition = condition_entry.get().strip()
            
            if not table_name or not set_clause:
                messagebox.showerror("错误", "表名和SET子句不能为空")
                return
                
            sql = f"UPDATE {table_name} SET {set_clause}"
            if condition:
                sql += f" WHERE {condition}"
            sql += ";"
            
            result = self.execute_sql(sql)
            if result and "Error" not in result:
                self.status_var.set(f"表 {table_name} 数据更新成功")
                dialog.destroy()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("更新数据")
        dialog.geometry("400x250")
        
        ttk.Label(dialog, text="表名:").pack(pady=5)
        table_entry = ttk.Entry(dialog, width=30)
        table_entry.pack(pady=5)
        
        ttk.Label(dialog, text="SET子句 (例: age = 30):").pack(pady=5)
        set_entry = ttk.Entry(dialog, width=30)
        set_entry.pack(pady=5)
        
        ttk.Label(dialog, text="条件 (可选):").pack(pady=5)
        condition_entry = ttk.Entry(dialog, width=30)
        condition_entry.pack(pady=5)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="更新", command=on_update).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def delete_data(self):
        """删除数据对话框"""
        def on_delete():
            table_name = table_entry.get().strip()
            condition = condition_entry.get().strip()
            
            if not table_name:
                messagebox.showerror("错误", "表名不能为空")
                return
                
            if not condition:
                if not messagebox.askyesno("警告", "没有指定条件，将删除表中所有数据！确定要继续吗？"):
                    return
            
            sql = f"DELETE FROM {table_name}"
            if condition:
                sql += f" WHERE {condition}"
            sql += ";"
            
            result = self.execute_sql(sql)
            if result and "Error" not in result:
                self.status_var.set(f"表 {table_name} 数据删除成功")
                dialog.destroy()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("删除数据")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="表名:").pack(pady=5)
        table_entry = ttk.Entry(dialog, width=30)
        table_entry.pack(pady=5)
        
        ttk.Label(dialog, text="条件 (可选，为空则删除所有数据):").pack(pady=5)
        condition_entry = ttk.Entry(dialog, width=30)
        condition_entry.pack(pady=5)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="删除", command=on_delete).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def open_sql_console(self):
        """打开SQL命令行界面"""
        console = SQLConsole(self.root, self)
        console.grab_set()

class SQLConsole(tk.Toplevel):
    """SQL命令行控制台"""
    def __init__(self, parent, gui):
        super().__init__(parent)
        self.gui = gui
        self.title("SQL控制台")
        self.geometry("600x400")
        
        # SQL输入区域
        ttk.Label(self, text="输入SQL命令:").pack(pady=5)
        self.sql_text = scrolledtext.ScrolledText(self, height=10)
        self.sql_text.pack(pady=5, fill=tk.BOTH, expand=True)
        
        # 按钮区域
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="执行", command=self.execute).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清除", command=self.clear).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关闭", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def execute(self):
        """执行SQL命令"""
        sql = self.sql_text.get("1.0", tk.END).strip()
        if sql:
            result = self.gui.execute_sql(sql)
            if result:
                # 在新的对话框中显示结果
                result_dialog = tk.Toplevel(self)
                result_dialog.title("执行结果")
                result_dialog.geometry("500x300")
                
                result_text = scrolledtext.ScrolledText(result_dialog)
                result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                result_text.insert("1.0", result)
                
                ttk.Button(result_dialog, text="关闭", command=result_dialog.destroy).pack(pady=10)
    
    def clear(self):
        """清除输入"""
        self.sql_text.delete("1.0", tk.END)

def main():
    """主函数"""
    root = tk.Tk()
    app = TrivialDBGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()