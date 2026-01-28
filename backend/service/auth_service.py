from core.supabase_client import supabase

def register_user(email, password):
    # 後端使用 Service Role Client 進行操作
    response = supabase.auth.admin.create_user(
        email=email,
        password=password,
        user_metadata={"role": "premium"}
    )
    return response