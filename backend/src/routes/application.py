from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from src.models.user import User, db
from src.models.exam import Exam, Application, FormConfig

application_bp = Blueprint('application', __name__)

@application_bp.route('/applications', methods=['POST'])
@jwt_required()
def create_application():
    """创建报名申请"""
    try:
        current_user_id = get_jwt_identity()
        data = request.json
        
        if not data.get('exam_id'):
            return jsonify({'error': '考试ID为必填项'}), 400
        
        exam = Exam.query.get_or_404(data['exam_id'])
        
        # 检查是否已经报名
        existing_application = Application.query.filter_by(
            user_id=current_user_id,
            exam_id=exam.id
        ).first()
        
        if existing_application:
            return jsonify({'error': '您已经报名过此考试'}), 400
        
        # 检查报名时间
        now = datetime.utcnow()
        if now < exam.registration_start:
            return jsonify({'error': '报名尚未开始'}), 400
        if now > exam.registration_end:
            return jsonify({'error': '报名已结束'}), 400
        
        # 检查报名人数限制
        if exam.max_applicants > 0:
            current_count = Application.query.filter_by(exam_id=exam.id).count()
            if current_count >= exam.max_applicants:
                return jsonify({'error': '报名人数已满'}), 400
        
        # 创建报名申请
        application = Application(
            user_id=current_user_id,
            exam_id=exam.id,
            application_data=data.get('application_data', {})
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify({
            'message': '报名申请提交成功',
            'application': application.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@application_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_my_applications():
    """获取我的报名申请列表"""
    try:
        current_user_id = get_jwt_identity()
        
        applications = Application.query.filter_by(user_id=current_user_id).all()
        
        return jsonify([app.to_dict() for app in applications]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@application_bp.route('/applications/<int:application_id>', methods=['GET'])
@jwt_required()
def get_application(application_id):
    """获取报名申请详情"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        application = Application.query.get_or_404(application_id)
        
        # 检查权限：只有申请者本人或管理员可以查看
        if application.user_id != current_user_id and user.role != 'admin':
            return jsonify({'error': '权限不足'}), 403
        
        return jsonify(application.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@application_bp.route('/applications/<int:application_id>', methods=['PUT'])
@jwt_required()
def update_application(application_id):
    """更新报名申请（仅在待审核状态下）"""
    try:
        current_user_id = get_jwt_identity()
        application = Application.query.get_or_404(application_id)
        
        # 检查权限
        if application.user_id != current_user_id:
            return jsonify({'error': '权限不足'}), 403
        
        # 检查状态
        if application.status != 'pending':
            return jsonify({'error': '只能修改待审核的报名申请'}), 400
        
        data = request.json
        
        if 'application_data' in data:
            application.application_data = data['application_data']
        
        db.session.commit()
        
        return jsonify({
            'message': '报名申请更新成功',
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@application_bp.route('/applications/<int:application_id>', methods=['DELETE'])
@jwt_required()
def delete_application(application_id):
    """删除报名申请（仅在待审核状态下）"""
    try:
        current_user_id = get_jwt_identity()
        application = Application.query.get_or_404(application_id)
        
        # 检查权限
        if application.user_id != current_user_id:
            return jsonify({'error': '权限不足'}), 403
        
        # 检查状态
        if application.status != 'pending':
            return jsonify({'error': '只能删除待审核的报名申请'}), 400
        
        db.session.delete(application)
        db.session.commit()
        
        return jsonify({'message': '报名申请删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@application_bp.route('/exams/<int:exam_id>/form-config', methods=['GET'])
def get_form_config(exam_id):
    """获取考试的表单配置"""
    try:
        exam = Exam.query.get_or_404(exam_id)
        form_config = FormConfig.query.filter_by(exam_id=exam_id).first()
        
        if not form_config:
            # 返回默认表单配置
            default_config = {
                'fields': [
                    {'name': 'name', 'label': '姓名', 'type': 'text', 'required': True},
                    {'name': 'gender', 'label': '性别', 'type': 'select', 'required': True, 'options': ['男', '女']},
                    {'name': 'phone', 'label': '联系电话', 'type': 'text', 'required': True},
                    {'name': 'email', 'label': '电子邮箱', 'type': 'email', 'required': True},
                    {'name': 'id_type', 'label': '身份证件类型', 'type': 'select', 'required': True, 'options': ['身份证', '护照', '其他']},
                    {'name': 'id_number', 'label': '身份证件号码', 'type': 'text', 'required': True},
                    {'name': 'address', 'label': '联系地址', 'type': 'text', 'required': False},
                    {'name': 'remarks', 'label': '备注', 'type': 'textarea', 'required': False}
                ]
            }
            return jsonify({
                'exam_id': exam_id,
                'config_json': default_config
            }), 200
        
        return jsonify(form_config.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@application_bp.route('/exams/<int:exam_id>/form-config', methods=['POST'])
@jwt_required()
def create_form_config(exam_id):
    """创建或更新考试的表单配置（仅管理员）"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.role != 'admin':
            return jsonify({'error': '权限不足'}), 403
        
        exam = Exam.query.get_or_404(exam_id)
        data = request.json
        
        form_config = FormConfig.query.filter_by(exam_id=exam_id).first()
        
        if form_config:
            # 更新现有配置
            form_config.config_json = data.get('config_json', {})
        else:
            # 创建新配置
            form_config = FormConfig(
                exam_id=exam_id,
                config_json=data.get('config_json', {})
            )
            db.session.add(form_config)
        
        db.session.commit()
        
        return jsonify({
            'message': '表单配置保存成功',
            'form_config': form_config.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

