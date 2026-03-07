from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from core.supabase_client import supabase
from datetime import datetime, timezone

resume_bp = Blueprint('resume', __name__)




@resume_bp.route('/form', methods=['POST'])
@login_required
def create_resume():
    """
    C-02 建立原始履歷
    DB: RESUME — 存原始履歷
    """
    try:
        user_id = g.db_user_id
        if user_id is None:
            return jsonify({'error': 'User not found in DB'}), 403
        data = request.get_json(silent=True) or {}
        if not data.get('resume_name'):
            return jsonify({'error': 'Missing resume_name'}), 400
        if 'structured_data' not in data:
            return jsonify({'error': 'Missing structured_data'}), 400

        resume_type = data.get('resume_type')
        if resume_type not in ('uploaded', 'generic'):
            return jsonify({'error': "resume_type must be 'uploaded' or 'generic'"}), 400

        now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S+00')

        insert_payload = {
            "user_id": int(user_id),
            "resume_name": data['resume_name'],
            "resume_type": resume_type,
            "structured_data": data['structured_data'],
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
def create_opt_resume(id):
    """
    C-05 建立優化履歷
    每次 PUT 自動產生新版本 (optimization_version 遞增)
    DB: RESUME_OPTIMIZATION
    """
    try:
        user_id = g.db_user_id
        if user_id is None:
            return jsonify({'error': 'User not found in DB'}), 403

        owner_check = (
            supabase.table("resume")
            .select("resume_id, resume_name")
            .eq("resume_id", id)
            .eq("user_id", user_id)
            .execute()
        )
        if not owner_check.data:
            return jsonify({'error': 'Resume not found or not owned by user'}), 404
        base_resume_name = owner_check.data[0].get('resume_name') or str(id)
        opt_resume_name = f"{base_resume_name}_優化"

        data = request.get_json(silent=True) or {}
        if not data:
            return jsonify({'error': 'Missing request body'}), 400

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

        sd = data.get('structured_data', {})

        insert_payload = {
            "resume_id": id,
            "user_id": int(user_id),
            "resume_name": opt_resume_name,
            "optimization_version": next_ver,
            "professional_summary": data.get('professional_summary'), # 假設保留給自備
            "professional_experience": sd.get('work_experience') or data.get('professional_experience'),
            "core_skills": sd.get('skills') or data.get('core_skills'),
            "projects": sd.get('certificate_projects') or data.get('projects'),
            "education": sd.get('education') or data.get('education'),
            "autobiography": sd.get('autobiography') or data.get('autobiography'),
        }

        # template_color: JSON { template_id, style_color } 存入 DB
        style = data.get('style_settings', {})
        if isinstance(style, dict):
            template_color = {}
            if style.get('template_id') is not None:
                template_color['template_id'] = style['template_id']
            if style.get('style_color'):
                template_color['style_color'] = style['style_color']
            if template_color:
                insert_payload['template_color'] = template_color

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
            'resume_name': inserted.get('resume_name'),
            'optimization_version': inserted['optimization_version'],
            'template_color': inserted.get('template_color'),
            'created_at': inserted.get('created_at'),
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

