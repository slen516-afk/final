"""
向後相容：連線模組已移至 db_function 資料夾。

請改用:
    from db_function.supabase_connection import connect_to_supabase
    或
    from db_function import connect_to_supabase
"""
from db_function.supabase_connection import connect_to_supabase

__all__ = ["connect_to_supabase"]
