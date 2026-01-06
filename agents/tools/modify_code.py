# agents/tools/python_executor.py

import os
import sys
from io import StringIO
from langchain.tools import tool

@tool
def python_repl_tool(code: str, file_name: str = "task_code.py", save_path: str = "./") -> str:
    """
    编写 Python 代码并保存到指定位置运行。
    参数：
    - code: 合法的 Python 代码字符串。
    - file_name: 文件名（如 'snake.py'）。
    - save_path: 相对路径或绝对路径，默认为 './'（当前目录）。
    """
    
    # 1. 确定最终存储目录（处理相对路径）
    # os.path.abspath(save_path) 会把 "./" 转为当前运行命令的完整路径
    target_dir = os.path.abspath(save_path)
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    full_file_path = os.path.join(target_dir, file_name)

    try:
        # 2. 写入文件
        with open(full_file_path, "w", encoding="utf-8") as f:
            f.write(code)
        
        # 3. 捕获输出
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()
        
        # 4. 执行
        # 注意：对于贪吃蛇这种游戏，exec 会阻塞进程直到窗口关闭
        # 为了防止测试卡死，我们可以通过 globals 运行
        exec(code, globals())
        
        sys.stdout = old_stdout
        execution_result = redirected_output.getvalue()
        
        result_msg = execution_result if execution_result else "代码已执行（无控制台输出）。"
        return f"【成功】文件已保存至: {full_file_path}\n【执行结果】: {result_msg}"

    except Exception as e:
        if 'old_stdout' in locals():
            sys.stdout = old_stdout
        return f"执行出错: {str(e)}\n文件已保存至: {full_file_path}"