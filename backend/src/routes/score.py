from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from src.models.user import User, db
from src.models.exam import Exam, Score, Certificate
import csv
import io

score_bp = Blueprint('score', __name__)

def admin_required():
    """检查是否为管理员"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return user and user.role == 'admin'

@score_bp.route('/scores/import', methods=['POST'])
@jwt_required()
def import_scores():
    """批量导入成绩（仅管理员）"""
    try:
        if not admin_required():
            return jsonify({'error': '权限不足'}), 403
        
        data = request.json
        exam_id = data.get('exam_id')
        scores_data = data.get('scores', [])
        
        if not exam_id:
            return jsonify({'error': '考试ID为必填项'}), 400
        
        exam = Exam.query.get_or_404(exam_id)
        
        imported_count = 0
        errors = []
        
        for score_data in scores_data:
            try:
                # 查找用户
                user = None
                if 'user_id' in score_data:
                    user = User.query.get(score_data['user_id'])
                elif 'username' in score_data:
                    user = User.query.filter_by(username=score_data['username']).first()
                elif 'email' in score_data:
                    user = User.query.filter_by(email=score_data['email']).first()
                
                if not user:
                    errors.append(f"用户未找到: {score_data}")
                    continue
                
                # 检查是否已存在成绩
                existing_score = Score.query.filter_by(
                    user_id=user.id,
                    exam_id=exam_id
                ).first()
                
                if existing_score:
                    # 更新现有成绩
                    existing_score.score = score_data.get('score')
                    existing_score.is_passed = score_data.get('is_passed', False)
                    existing_score.imported_at = datetime.utcnow()
                else:
                    # 创建新成绩
                    score = Score(
                        user_id=user.id,
                        exam_id=exam_id,
                        score=score_data.get('score'),
                        is_passed=score_data.get('is_passed', False)
                    )
                    db.session.add(score)
                
                imported_count += 1
                
            except Exception as e:
                errors.append(f"处理数据时出错: {score_data}, 错误: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'message': f'成绩导入完成，成功导入 {imported_count} 条记录',
            'imported_count': imported_count,
            'errors': errors
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@score_bp.route('/exams/<int:exam_id>/scores', methods=['GET'])
@jwt_required()
def get_exam_scores(exam_id):
    """获取考试成绩列表（仅管理员）"""
    try:
        if not admin_required():
            return jsonify({'error': '权限不足'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        scores = Score.query.filter_by(exam_id=exam_id).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'scores': [score.to_dict() for score in scores.items],
            'total': scores.total,
            'pages': scores.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@score_bp.route('/my-scores', methods=['GET'])
@jwt_required()
def get_my_scores():
    """获取我的成绩"""
    try:
        current_user_id = get_jwt_identity()
        
        scores = Score.query.filter_by(user_id=current_user_id).all()
        
        return jsonify([score.to_dict() for score in scores]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@score_bp.route('/scores/<int:score_id>', methods=['PUT'])
@jwt_required()
def update_score(score_id):
    """更新成绩（仅管理员）"""
    try:
        if not admin_required():
            return jsonify({'error': '权限不足'}), 403
        
        score = Score.query.get_or_404(score_id)
        data = request.json
        
        if 'score' in data:
            score.score = data['score']
        if 'is_passed' in data:
            score.is_passed = data['is_passed']
        
        db.session.commit()
        
        return jsonify({
            'message': '成绩更新成功',
            'score': score.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@score_bp.route('/scores/<int:score_id>', methods=['DELETE'])
@jwt_required()
def delete_score(score_id):
    """删除成绩（仅管理员）"""
    try:
        if not admin_required():
            return jsonify({'error': '权限不足'}), 403
        
        score = Score.query.get_or_404(score_id)
        db.session.delete(score)
        db.session.commit()
        
        return jsonify({'message': '成绩删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@score_bp.route('/certificates/generate', methods=['POST'])
@jwt_required()
def generate_certificates():
    """生成证书编号（仅管理员）"""
    try:
        if not admin_required():
            return jsonify({'error': '权限不足'}), 403
        
        data = request.json
        exam_id = data.get('exam_id')
        rule_type = data.get('rule_type', 'auto')  # auto, manual
        
        if not exam_id:
            return jsonify({'error': '考试ID为必填项'}), 400
        
        exam = Exam.query.get_or_404(exam_id)
        
        # 获取通过考试的成绩
        passed_scores = Score.query.filter_by(exam_id=exam_id, is_passed=True).all()
        
        generated_count = 0
        
        for score in passed_scores:
            # 检查是否已有证书
            existing_cert = Certificate.query.filter_by(
                user_id=score.user_id,
                exam_id=exam_id
            ).first()
            
            if existing_cert:
                continue
            
            # 生成证书编号
            if rule_type == 'auto':
                # 自动生成规则：年份 + 考试ID + 序号
                year = datetime.now().year
                cert_count = Certificate.query.filter_by(exam_id=exam_id).count()
                certificate_number = f"{year}{exam_id:04d}{cert_count+1:06d}"
            else:
                # 手动模式，暂时生成临时编号
                certificate_number = f"TEMP_{exam_id}_{score.user_id}"
            
            certificate = Certificate(
                user_id=score.user_id,
                exam_id=exam_id,
                certificate_number=certificate_number,
                status='issued' if rule_type == 'auto' else 'pending'
            )
            
            db.session.add(certificate)
            generated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'证书生成完成，共生成 {generated_count} 个证书',
            'generated_count': generated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@score_bp.route('/certificates/import', methods=['POST'])
@jwt_required()
def import_certificates():
    """批量导入证书编号（仅管理员）"""
    try:
        if not admin_required():
            return jsonify({'error': '权限不足'}), 403
        
        data = request.json
        certificates_data = data.get('certificates', [])
        
        updated_count = 0
        errors = []
        
        for cert_data in certificates_data:
            try:
                certificate_id = cert_data.get('certificate_id')
                certificate_number = cert_data.get('certificate_number')
                
                if not certificate_id or not certificate_number:
                    errors.append(f"证书ID和证书编号为必填项: {cert_data}")
                    continue
                
                certificate = Certificate.query.get(certificate_id)
                if not certificate:
                    errors.append(f"证书未找到: {certificate_id}")
                    continue
                
                certificate.certificate_number = certificate_number
                certificate.status = 'issued'
                updated_count += 1
                
            except Exception as e:
                errors.append(f"处理数据时出错: {cert_data}, 错误: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'message': f'证书编号导入完成，成功更新 {updated_count} 个证书',
            'updated_count': updated_count,
            'errors': errors
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@score_bp.route('/my-certificates', methods=['GET'])
@jwt_required()
def get_my_certificates():
    """获取我的证书"""
    try:
        current_user_id = get_jwt_identity()
        
        certificates = Certificate.query.filter_by(user_id=current_user_id).all()
        
        return jsonify([cert.to_dict() for cert in certificates]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@score_bp.route('/exams/<int:exam_id>/certificates', methods=['GET'])
@jwt_required()
def get_exam_certificates(exam_id):
    """获取考试证书列表（仅管理员）"""
    try:
        if not admin_required():
            return jsonify({'error': '权限不足'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        certificates = Certificate.query.filter_by(exam_id=exam_id).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'certificates': [cert.to_dict() for cert in certificates.items],
            'total': certificates.total,
            'pages': certificates.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

