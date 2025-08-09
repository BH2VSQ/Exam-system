from datetime import datetime
from src.database import db

class Certificate(db.Model):
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    certificate_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    
    # 证书类型：initial(初证), renewal(换证), replacement(补证)
    certificate_type = db.Column(db.String(20), nullable=False, default='initial')
    
    # 证书状态：active(有效), expired(过期), revoked(吊销), replaced(已更换)
    status = db.Column(db.String(20), nullable=False, default='active')
    
    # 证书有效期
    issue_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=True)
    
    # 原证书信息（用于换证和补证）
    original_certificate_id = db.Column(db.Integer, db.ForeignKey('certificates.id'), nullable=True)
    original_certificate_number = db.Column(db.String(100), nullable=True)
    
    # 换证原因
    renewal_reason = db.Column(db.Text, nullable=True)
    
    # 证书模板和生成信息
    template_id = db.Column(db.String(50), nullable=True)
    certificate_data = db.Column(db.JSON, nullable=True)  # 存储证书上的具体信息
    
    # 文件路径
    certificate_file_path = db.Column(db.String(500), nullable=True)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='certificates')
    exam = db.relationship('Exam', backref='certificates')
    original_certificate = db.relationship('Certificate', remote_side=[id], backref='replacement_certificates')
    
    def to_dict(self):
        return {
            'id': self.id,
            'certificate_number': self.certificate_number,
            'user_id': self.user_id,
            'exam_id': self.exam_id,
            'certificate_type': self.certificate_type,
            'status': self.status,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'original_certificate_id': self.original_certificate_id,
            'original_certificate_number': self.original_certificate_number,
            'renewal_reason': self.renewal_reason,
            'template_id': self.template_id,
            'certificate_data': self.certificate_data,
            'certificate_file_path': self.certificate_file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': self.user.to_dict() if self.user else None,
            'exam': self.exam.to_dict() if self.exam else None
        }

class CertificateTemplate(db.Model):
    __tablename__ = 'certificate_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # 模板类型：exam(考试证书), training(培训证书), professional(职业资格证书)
    template_type = db.Column(db.String(50), nullable=False, default='exam')
    
    # 模板配置（JSON格式存储布局、字段、样式等信息）
    template_config = db.Column(db.JSON, nullable=False)
    
    # 模板文件路径（如果使用文件模板）
    template_file_path = db.Column(db.String(500), nullable=True)
    
    # 是否为默认模板
    is_default = db.Column(db.Boolean, nullable=False, default=False)
    
    # 是否启用
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'template_type': self.template_type,
            'template_config': self.template_config,
            'template_file_path': self.template_file_path,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CertificateRenewalApplication(db.Model):
    __tablename__ = 'certificate_renewal_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_certificate_id = db.Column(db.Integer, db.ForeignKey('certificates.id'), nullable=False)
    
    # 申请类型：renewal(换证), replacement(补证)
    application_type = db.Column(db.String(20), nullable=False)
    
    # 申请原因
    reason = db.Column(db.Text, nullable=False)
    
    # 申请状态：pending(待审核), approved(已批准), rejected(已拒绝), completed(已完成)
    status = db.Column(db.String(20), nullable=False, default='pending')
    
    # 审核信息
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    review_comment = db.Column(db.Text, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    # 新证书ID（完成后填写）
    new_certificate_id = db.Column(db.Integer, db.ForeignKey('certificates.id'), nullable=True)
    
    # 申请材料（JSON格式存储文件路径等）
    supporting_documents = db.Column(db.JSON, nullable=True)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', foreign_keys=[user_id], backref='renewal_applications')
    original_certificate = db.relationship('Certificate', foreign_keys=[original_certificate_id])
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])
    new_certificate = db.relationship('Certificate', foreign_keys=[new_certificate_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_certificate_id': self.original_certificate_id,
            'application_type': self.application_type,
            'reason': self.reason,
            'status': self.status,
            'reviewer_id': self.reviewer_id,
            'review_comment': self.review_comment,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'new_certificate_id': self.new_certificate_id,
            'supporting_documents': self.supporting_documents,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': self.user.to_dict() if self.user else None,
            'original_certificate': self.original_certificate.to_dict() if self.original_certificate else None,
            'reviewer': self.reviewer.to_dict() if self.reviewer else None,
            'new_certificate': self.new_certificate.to_dict() if self.new_certificate else None
        }

