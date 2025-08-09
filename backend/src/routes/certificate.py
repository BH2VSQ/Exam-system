from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from src.models.user import db, User
from src.models.exam import Exam
from src.models.certificate import Certificate, CertificateTemplate, CertificateRenewalApplication
from src.models.application import Application
import os
import uuid
from werkzeug.utils import secure_filename

certificate_bp = Blueprint('certificate', __name__)

# 获取我的证书列表
@certificate_bp.route('/my-certificates', methods=['GET'])
@jwt_required()
def get_my_certificates():
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        query = Certificate.query.filter_by(user_id=current_user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        certificates = query.order_by(Certificate.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'certificates': [cert.to_dict() for cert in certificates.items],
            'total': certificates.total,
            'pages': certificates.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 获取考试的证书列表（管理员）
@certificate_bp.route('/exams/<int:exam_id>/certificates', methods=['GET'])
@jwt_required()
def get_exam_certificates(exam_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.role != 'admin':
            return jsonify({'error': '权限不足'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        certificate_type = request.args.get('type')
        
        query = Certificate.query.filter_by(exam_id=exam_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if certificate_type:
            query = query.filter_by(certificate_type=certificate_type)
        
        certificates = query.order_by(Certificate.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'certificates': [cert.to_dict() for cert in certificates.items],
            'total': certificates.total,
            'pages': certificates.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 生成证书
@certificate_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_certificates():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.role != 'admin':
            return jsonify({'error': '权限不足'}), 403
        
        data = request.get_json()
        exam_id = data.get('exam_id')
        user_ids = data.get('user_ids', [])
        template_id = data.get('template_id')
        certificate_type = data.get('certificate_type', 'initial')
        expiry_months = data.get('expiry_months', 36)  # 默认3年有效期
        
        if not exam_id:
            return jsonify({'error': '考试ID不能为空'}), 400
        
        exam = Exam.query.get(exam_id)
        if not exam:
            return jsonify({'error': '考试不存在'}), 404
        
        generated_certificates = []
        
        for user_id in user_ids:
            # 检查是否已有有效证书
            existing_cert = Certificate.query.filter_by(
                user_id=user_id, 
                exam_id=exam_id, 
                status='active'
            ).first()
            
            if existing_cert and certificate_type == 'initial':
                continue  # 跳过已有证书的用户
            
            # 生成证书编号
            certificate_number = generate_certificate_number(exam, certificate_type)
            
            # 计算有效期
            expiry_date = datetime.utcnow() + timedelta(days=expiry_months * 30)
            
            certificate = Certificate(
                certificate_number=certificate_number,
                user_id=user_id,
                exam_id=exam_id,
                certificate_type=certificate_type,
                status='active',
                expiry_date=expiry_date,
                template_id=template_id,
                certificate_data={
                    'exam_name': exam.name,
                    'user_name': User.query.get(user_id).username,
                    'issue_date': datetime.utcnow().strftime('%Y-%m-%d'),
                    'expiry_date': expiry_date.strftime('%Y-%m-%d')
                }
            )
            
            db.session.add(certificate)
            generated_certificates.append(certificate)
        
        db.session.commit()
        
        return jsonify({
            'message': f'成功生成 {len(generated_certificates)} 张证书',
            'certificates': [cert.to_dict() for cert in generated_certificates]
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 导入证书编号
@certificate_bp.route('/import', methods=['POST'])
@jwt_required()
def import_certificates():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.role != 'admin':
            return jsonify({'error': '权限不足'}), 403
        
        data = request.get_json()
        certificates_data = data.get('certificates', [])
        
        imported_count = 0
        errors = []
        
        for cert_data in certificates_data:
            try:
                certificate_number = cert_data.get('certificate_number')
                user_id = cert_data.get('user_id')
                exam_id = cert_data.get('exam_id')
                
                if not all([certificate_number, user_id, exam_id]):
                    errors.append(f'证书编号 {certificate_number}: 缺少必要字段')
                    continue
                
                # 检查证书编号是否已存在
                existing_cert = Certificate.query.filter_by(
                    certificate_number=certificate_number
                ).first()
                
                if existing_cert:
                    errors.append(f'证书编号 {certificate_number}: 已存在')
                    continue
                
                certificate = Certificate(
                    certificate_number=certificate_number,
                    user_id=user_id,
                    exam_id=exam_id,
                    certificate_type=cert_data.get('certificate_type', 'initial'),
                    status=cert_data.get('status', 'active'),
                    issue_date=datetime.strptime(cert_data.get('issue_date'), '%Y-%m-%d') if cert_data.get('issue_date') else datetime.utcnow(),
                    expiry_date=datetime.strptime(cert_data.get('expiry_date'), '%Y-%m-%d') if cert_data.get('expiry_date') else None,
                    certificate_data=cert_data.get('certificate_data', {})
                )
                
                db.session.add(certificate)
                imported_count += 1
                
            except Exception as e:
                errors.append(f'证书编号 {cert_data.get("certificate_number", "未知")}: {str(e)}')
        
        db.session.commit()
        
        return jsonify({
            'message': f'成功导入 {imported_count} 张证书',
            'imported_count': imported_count,
            'errors': errors
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 申请证书更替（换证/补证）
@certificate_bp.route('/renewal-application', methods=['POST'])
@jwt_required()
def create_renewal_application():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        original_certificate_id = data.get('original_certificate_id')
        application_type = data.get('application_type')  # renewal 或 replacement
        reason = data.get('reason')
        
        if not all([original_certificate_id, application_type, reason]):
            return jsonify({'error': '缺少必要字段'}), 400
        
        # 验证原证书
        original_cert = Certificate.query.get(original_certificate_id)
        if not original_cert or original_cert.user_id != current_user_id:
            return jsonify({'error': '原证书不存在或无权限'}), 404
        
        # 检查是否已有待处理的申请
        existing_app = CertificateRenewalApplication.query.filter_by(
            user_id=current_user_id,
            original_certificate_id=original_certificate_id,
            status='pending'
        ).first()
        
        if existing_app:
            return jsonify({'error': '已有待处理的申请'}), 400
        
        application = CertificateRenewalApplication(
            user_id=current_user_id,
            original_certificate_id=original_certificate_id,
            application_type=application_type,
            reason=reason,
            supporting_documents=data.get('supporting_documents', {})
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify({
            'message': '申请提交成功',
            'application': application.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 获取证书更替申请列表
@certificate_bp.route('/renewal-applications', methods=['GET'])
@jwt_required()
def get_renewal_applications():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        if user.role == 'admin':
            # 管理员可以查看所有申请
            query = CertificateRenewalApplication.query
        else:
            # 普通用户只能查看自己的申请
            query = CertificateRenewalApplication.query.filter_by(user_id=current_user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        applications = query.order_by(CertificateRenewalApplication.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'applications': [app.to_dict() for app in applications.items],
            'total': applications.total,
            'pages': applications.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 审核证书更替申请
@certificate_bp.route('/renewal-applications/<int:application_id>/review', methods=['POST'])
@jwt_required()
def review_renewal_application(application_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.role != 'admin':
            return jsonify({'error': '权限不足'}), 403
        
        data = request.get_json()
        action = data.get('action')  # approve 或 reject
        comment = data.get('comment', '')
        
        application = CertificateRenewalApplication.query.get(application_id)
        if not application:
            return jsonify({'error': '申请不存在'}), 404
        
        if application.status != 'pending':
            return jsonify({'error': '申请已处理'}), 400
        
        application.reviewer_id = current_user_id
        application.review_comment = comment
        application.reviewed_at = datetime.utcnow()
        
        if action == 'approve':
            application.status = 'approved'
            
            # 如果批准，生成新证书
            original_cert = application.original_certificate
            new_cert_number = generate_certificate_number(
                original_cert.exam, 
                application.application_type
            )
            
            new_certificate = Certificate(
                certificate_number=new_cert_number,
                user_id=application.user_id,
                exam_id=original_cert.exam_id,
                certificate_type=application.application_type,
                status='active',
                original_certificate_id=original_cert.id,
                original_certificate_number=original_cert.certificate_number,
                renewal_reason=application.reason,
                template_id=original_cert.template_id,
                expiry_date=datetime.utcnow() + timedelta(days=36 * 30),  # 3年有效期
                certificate_data=original_cert.certificate_data
            )
            
            # 更新原证书状态
            original_cert.status = 'replaced'
            
            db.session.add(new_certificate)
            db.session.flush()  # 获取新证书ID
            
            application.new_certificate_id = new_certificate.id
            application.status = 'completed'
            
        elif action == 'reject':
            application.status = 'rejected'
        
        db.session.commit()
        
        return jsonify({
            'message': '审核完成',
            'application': application.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def generate_certificate_number(exam, certificate_type='initial'):
    """生成证书编号"""
    # 证书编号格式：考试代码-年份-类型-序号
    year = datetime.utcnow().year
    type_code = {
        'initial': 'I',
        'renewal': 'R',
        'replacement': 'P'
    }.get(certificate_type, 'I')
    
    # 获取当年该类型证书的最大序号
    prefix = f"{exam.exam_code}-{year}-{type_code}-"
    last_cert = Certificate.query.filter(
        Certificate.certificate_number.like(f"{prefix}%")
    ).order_by(Certificate.certificate_number.desc()).first()
    
    if last_cert:
        last_number = int(last_cert.certificate_number.split('-')[-1])
        new_number = last_number + 1
    else:
        new_number = 1
    
    return f"{prefix}{new_number:06d}"

# 获取证书模板列表
@certificate_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_certificate_templates():
    try:
        templates = CertificateTemplate.query.filter_by(is_active=True).all()
        return jsonify({
            'templates': [template.to_dict() for template in templates]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 创建证书模板（管理员）
@certificate_bp.route('/templates', methods=['POST'])
@jwt_required()
def create_certificate_template():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.role != 'admin':
            return jsonify({'error': '权限不足'}), 403
        
        data = request.get_json()
        
        template = CertificateTemplate(
            name=data.get('name'),
            description=data.get('description'),
            template_type=data.get('template_type', 'exam'),
            template_config=data.get('template_config', {}),
            is_default=data.get('is_default', False)
        )
        
        # 如果设置为默认模板，取消其他默认模板
        if template.is_default:
            CertificateTemplate.query.filter_by(
                template_type=template.template_type,
                is_default=True
            ).update({'is_default': False})
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'message': '模板创建成功',
            'template': template.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

