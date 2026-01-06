import sqlite3
import os
from langchain.tools import tool

# 建议定义一个专门存放数据库的文件夹，防止文件乱跑
DB_DIR = "databases"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

@tool
def run_sqlite_query(query: str, db_name: str = "company.db") -> str:
    """
    执行 SQLite SQL 查询。支持创建数据库、创建表、增删改查。
    参数：
    - query: 合法的 SQL 字符串。
    - db_name: 数据库文件名（如 'my_data.db'）。
    """
    # 1. 统一后缀和路径
    if not db_name.endswith(".db"):
        db_name += ".db"
    
    db_path = os.path.join(DB_DIR, db_name)
    
    # --- 核心修改：移除“文件不存在就报错”的逻辑 ---
    is_new_db = not os.path.exists(db_path)

    try:
        # sqlite3.connect 在文件不存在时会自动创建它
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 2. 执行 SQL
        cursor.execute(query)
        
        # 3. 处理返回结果
        query_upper = query.strip().upper()
        
        if query_upper.startswith("SELECT"):
            rows = cursor.fetchall()
            colnames = [description[0] for description in cursor.description]
            result = [dict(zip(colnames, row)) for row in rows]
            return str(result) if result else f"在 {db_name} 中查询成功，但返回为空。"
        
        # 4. 提交更改（CREATE, INSERT, UPDATE, DELETE）
        conn.commit()
        
        msg = f"操作成功！数据库: {db_name}"
        if is_new_db:
            msg = f"✅ 已成功创建新数据库文件 '{db_name}' 并执行指令。"
        if query_upper.startswith("CREATE"):
            msg += " 表结构已更新/创建。"
            
        return msg
        
    except sqlite3.Error as e:
        return f"数据库 {db_name} 操作出错: {str(e)}"
    finally:
        if 'conn' in locals() and conn:
            conn.close()