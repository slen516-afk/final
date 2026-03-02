from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from core.supabase_client import supabase
from datetime import datetime, timezone

resume_bp = Blueprint('resume', __name__)


@resume_bp.route('/form', methods=['POST'])
@login_required
def create_resume_form():
    """
    C-02 建立履歷 (表單填寫)
    DB: RESUME — 存原始履歷
    """
    try:
        user_id = g.db_user_id
        if user_id is None:
            return jsonify({'error': 'User not found in DB'}), 403
        data = request.json
        if 'structured_data' not in data:
            return jsonify({'error': 'Missing structured_data'}), 400

        template_id = data.get('template_id', 1)
        resume_type = data.get('resume_type', 'generic')

        now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S+00')

        insert_payload = {
            "user_id": int(user_id),
            "template_id": int(template_id),
            "resume_type": resume_type,
            "structured_data": data['structured_data'],
            "normalized_data": data.get('normalized_data', {}),
            "vector_id": None,
            "is_embedded": False,
            "is_primary": True,
            "created_at": now_str,
            "updated_at": now_str
        }

        response = supabase.table("resume").insert(insert_payload).execute()
        inserted = response.data[0]

        return jsonify({
            'resume_id': inserted['resume_id'],
            'status': 'completed',
            'last_updated': inserted.get('updated_at', now_str)
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_resume(id):
    """
    C-04 取得履歷詳情 (原始履歷)
    DB: RESUME
    """
    try:
        user_id = g.db_user_id
        if user_id is None:
            return jsonify({'error': 'User not found in DB'}), 403

        response = (
            supabase.table("resume")
            .select("*")
            .eq("resume_id", id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        resume_data = response.data
        if not resume_data:
            return jsonify({'error': 'Resume not found'}), 404

        return jsonify(resume_data), 200

    except Exception as e:
        if 'Row not found' in str(e) or '0 rows' in str(e):
            return jsonify({'error': 'Resume not found'}), 404
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_resume(id):
    """
    C-05 用戶更新/確認履歷內容 → 寫入 resume_optimization
    每次 PUT 自動產生新版本 (optimization_version 遞增)
    DB: RESUME_OPTIMIZATION
    """
    try:
        user_id = g.db_user_id
        if user_id is None:
            return jsonify({'error': 'User not found in DB'}), 403

        # 1. 驗證原始履歷存在且屬於該使用者
        owner_check = (
            supabase.table("resume")
            .select("resume_id")
            .eq("resume_id", id)
            .eq("user_id", user_id)
            .execute()
        )
        if not owner_check.data:
            return jsonify({'error': 'Resume not found or not owned by user'}), 404

        data = request.json
        if not data:
            return jsonify({'error': 'Missing request body'}), 400

        # 2. 查詢目前最大版本號
        ver_resp = (
            supabase.table("resume_optimization")
            .select("optimization_version")
            .eq("user_id", user_id)
            .order("optimization_version", desc=True)
            .limit(1)
            .execute()
        )

        if ver_resp.data:
            current_ver = ver_resp.data[0]['optimization_version']
            try:
                next_ver = str(int(float(current_ver)) + 1)
            except (ValueError, TypeError):
                next_ver = "1"
        else:
            next_ver = "1"

        # 3. 從 structured_data 或直接頂層欄位映射
        sd = data.get('structured_data', {})

        insert_payload = {
            "resume_id": id,
            "user_id": int(user_id),
            "optimization_version": next_ver,
            "professional_summary": sd.get('professional_summary')
                or data.get('professional_summary'),
            "professional_experience": sd.get('professional_experience')
                or sd.get('work_experience')
                or data.get('professional_experience'),
            "core_skills": sd.get('core_skills')
                or sd.get('skills')
                or data.get('core_skills'),
            "projects": sd.get('projects')
                or data.get('projects'),
            "education": sd.get('education')
                or data.get('education'),
            "autobiography": sd.get('autobiography')
                or data.get('autobiography'),
        }

        # 4. template_color (style_settings.color → varchar)
        style = data.get('style_settings', {})
        if isinstance(style, dict) and style.get('color'):
            insert_payload["template_color"] = style['color']
        elif isinstance(style, str):
            insert_payload["template_color"] = style

        # 5. version_id (optional FK to resume_version)
        if data.get('version_id'):
            insert_payload["version_id"] = int(data['version_id'])

        # 清除 None 值，讓 DB 用 DEFAULT
        insert_payload = {k: v for k, v in insert_payload.items() if v is not None}

        response = (
            supabase.table("resume_optimization")
            .insert(insert_payload)
            .execute()
        )

        inserted = response.data[0]

        return jsonify({
            'optimization_id': inserted['optimization_id'],
            'resume_id': inserted['resume_id'],
            'optimization_version': inserted['optimization_version'],
            'template_color': inserted.get('template_color'),
            'created_at': inserted.get('created_at'),
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─── 版本管理 ────────────────────────────────────────────────────────

@resume_bp.route('/<int:id>/versions', methods=['GET'])
@login_required
def list_resume_versions(id):
    """取得某份履歷的所有優化版本列表"""
    try:
        user_id = g.db_user_id
        if user_id is None:
            return jsonify({'error': 'User not found in DB'}), 403

        response = (
            supabase.table("resume_optimization")
            .select("optimization_id, optimization_version, template_color, created_at")
            .eq("resume_id", id)
            .eq("user_id", user_id)
            .order("optimization_version", desc=True)
            .execute()
        )

        return jsonify({
            'resume_id': id,
            'versions': response.data or []
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/<int:id>/versions/<version>', methods=['GET'])
@login_required
def get_resume_version(id, version):
    """取得特定版本的優化履歷內容"""
    try:
        user_id = g.db_user_id
        if user_id is None:
            return jsonify({'error': 'User not found in DB'}), 403

        response = (
            supabase.table("resume_optimization")
            .select("*")
            .eq("resume_id", id)
            .eq("user_id", user_id)
            .eq("optimization_version", version)
            .single()
            .execute()
        )

        opt_data = response.data
        if not opt_data:
            return jsonify({'error': 'Version not found'}), 404

        return jsonify(opt_data), 200

    except Exception as e:
        if 'Row not found' in str(e) or '0 rows' in str(e):
            return jsonify({'error': 'Version not found'}), 404
        return jsonify({'error': str(e)}), 500
