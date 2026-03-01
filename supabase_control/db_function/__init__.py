"""
db_function：資料庫連線與前端寫入函數

提供 connect_to_supabase 及各寫入 function，供後端或腳本 import。

使用方式:
    from db_function import connect_to_supabase
    from db_function.supabase_connection import connect_to_supabase
    from db_function.db_writes import insert_career_survey, upsert_user_profile, ...
"""

from .supabase_connection import connect_to_supabase

__all__ = ["connect_to_supabase"]
