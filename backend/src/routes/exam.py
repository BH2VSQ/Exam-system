from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from src.models.user import User, db
from src.models.exam import Exam, Application, Score, Certificate, FormConfig

exam_bp = Blueprint('exam', __name__)

def admin_required():
    """检查是否为管理员"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return user and user.role == 'admin'

@exam_bp.route('/exams', methods=['GET'])
def get_exams():
    """获取考试列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        query = Exam.query
        
        if status:
            query = query.filter_by(status=status)
        
        exams = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'exams': [exam.to_dict() for exam in exams.items],
            'total': exams.total,
            'pages': exams.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exam_bp.route('/exams/<int:exam_id>', methods=['GET'])
def get_exam(exam_id):
    """获取考试详情"""
    try:
        exam = Exam.query.get_or_404(exam_id)
        return jsonify(exam.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exam_bp.route('/exams', methods=['POST'])
@jwt_required()
def create_exam():
    """创建考试（仅管理员）"""
    try:
        if not admin_required():
            return jsonify({'error': '权限不足'}), 403
        
        data = request.json
        
        # 验证必填字段
        required_fields = ['name', 'start_time', 'end_time', 'registration_start', 'registration_end']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} 为必填项'}), 400
        
        # 解析时间
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        registration_start = datetime.fromisoformat(data['registration_start'].replace('Z', '+00:00'))
        registration_end = datetime.fromisoformat(data['registration_end'].replace('Z', '+00:00'))
        
        exam = Exam(
            name=data['name'],
            start_time=start_time,
            end_time=end_time,
            registration_start=registration_start,
            registration_end=registration_end,
            location=data.get('location'),
            exam_type=data.get('exam_type'),
            organizer=data.get('organizer'),
            description=data.get('description'),
            status=data.get('status', 'draft'),
            max_applicants=data.get('max_applicants', 0),
            contact_phone=data.get('contact_phone'),
            contact_email=data.get('contact_email')
        )
        
        db.session.add(exam)
        db.session.commit()
        
        return jsonify({
            'message': '考试创建成功',
            'exam': exam.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exam_bp.route('/exams/<int:exam_id>', methods=['PUT'])
@jwt_required()
def update_exam(exam_id):
    """更新考试信息（仅管理员）"""
    try:
        if not admin_required():
            return jsonify({'error': '权限不足'}), 403
        
        exam = Exam.query.get_or_404(exam_id)
        data = request.json
        
        # 更新字段
        if 'name' in data:
            exam.name = data['name']
        if 'start_time' in data:
            exam.start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        if 'end_time' in data:
            exam.end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        if 'registration_start' in data:
            exam.registration_start = datetime.fromisoformat(data['registration_start'].replace('Z', '+00:00'))
        if 'registration_end' in data:
            exam.registration_end = datetime.fromisoformat(data['registration_end'].replace('Z', '+00:00'))
        if 'location' in data:
            exam.location = data['location']
        if 'exam_type' in data:
            exam.exam_type = data['exam_type']
        if 'organizer' in data:
            exam.organizer = data['organizer']
        if 'description' in data:
            exam.description = data['description']
        if 'status' in data:
            exam.status = data['status']
        if 'max_applicants' in data:
            exam.max_applicants = data['max_applicants']
        if 'contact_phone' in data:
            exam.contact_phone = data['contact_phone']
        if 'contact_email' in data:
            exam.contact_email = data['contact_email']
        
        db.session.commit()
        
        return jsonify({
            'message': '考试信息更新成功',
            'exam': exam.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exam_bp.route('/exams/<int:exam_id>', methods=['DELETE'])
@jwt_required()
def delete_exam(exam_id):
    """删除考试（仅管理员）"""
    try:
        if not admin_required():
            return jsonify({'error': '权限不足'}), 403
        
        exam = Exam.query.get_or_404(exam_id)
        db.session.delete(exam)
        db.session.commit()
        
        return jsonify({'message': '考试删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exam_bp.route('/exams/<int:exam_id>/applications', methods=['GET'])
@jwt_required()
def get_exam_applications(exam_id):
    """获取考试报名列表（仅管理员）"""
    try:
        if not admin_required():
            return jsonify({'error': '权限不足'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        query = Application.query.filter_by(exam_id=exam_id)
        
        if status:
            query = query.filter_by(status=status)
        
        applications = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'applications': [app.to_dict() for app in applications.items],
            'total': applications.total,
            'pages': applications.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exam_bp.route('/applications/<int:application_id>/approve', methods=['POST'])
@jwt_required()
def approve_application(application_id):
    """审核通过报名申请（仅管理员）"""
    try:
        if not admin_required():
            return jsonify({'error': '权限不足'}), 403
        
        application = Application.query.get_or_404(application_id)
        application.status = 'approved'
        application.approved_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': '报名申请审核通过',
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exam_bp.route('/applications/<int:application_id>/reject', methods=['POST'])
@jwt_required()
def reject_application(application_id):
    """拒绝报名申请（仅管理员）"""
    try:
        if not admin_required():
            return jsonify({'error': '权限不足'}), 403
        
        data = request.json
        application = Application.query.get_or_404(application_id)
        application.status = 'rejected'
        application.rejected_reason = data.get('reason', '')
        
        db.session.commit()
        
        return jsonify({
            'message': '报名申请已拒绝',
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

