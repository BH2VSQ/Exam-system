from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    registration_start = db.Column(db.DateTime, nullable=False)
    registration_end = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(500))
    exam_type = db.Column(db.String(50))
    organizer = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, published, closed
    max_applicants = db.Column(db.Integer, default=0)  # 0表示无限制
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    applications = db.relationship('Application', backref='exam', lazy=True, cascade='all, delete-orphan')
    scores = db.relationship('Score', backref='exam', lazy=True, cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='exam', lazy=True, cascade='all, delete-orphan')
    form_config = db.relationship('FormConfig', backref='exam', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Exam {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'registration_start': self.registration_start.isoformat() if self.registration_start else None,
            'registration_end': self.registration_end.isoformat() if self.registration_end else None,
            'location': self.location,
            'exam_type': self.exam_type,
            'organizer': self.organizer,
            'description': self.description,
            'status': self.status,
            'max_applicants': self.max_applicants,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'application_count': len(self.applications) if self.applications else 0
        }

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    application_data = db.Column(db.JSON)  # 存储自定义表单数据
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected
    admission_ticket_path = db.Column(db.String(500))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    rejected_reason = db.Column(db.Text)
    
    # 关联关系
    user = db.relationship('User', backref='applications')

    def __repr__(self):
        return f'<Application {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exam_id': self.exam_id,
            'application_data': self.application_data,
            'status': self.status,
            'admission_ticket_path': self.admission_ticket_path,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejected_reason': self.rejected_reason,
            'user': self.user.to_dict() if self.user else None,
            'exam': self.exam.to_dict() if self.exam else None
        }

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    score = db.Column(db.Float)
    is_passed = db.Column(db.Boolean, default=False)
    imported_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    user = db.relationship('User', backref='scores')

    def __repr__(self):
        return f'<Score {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exam_id': self.exam_id,
            'score': self.score,
            'is_passed': self.is_passed,
            'imported_at': self.imported_at.isoformat() if self.imported_at else None,
            'user': self.user.to_dict() if self.user else None,
            'exam': self.exam.to_dict() if self.exam else None
        }

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    certificate_number = db.Column(db.String(100), unique=True)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, issued
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    user = db.relationship('User', backref='certificates')

    def __repr__(self):
        return f'<Certificate {self.certificate_number}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exam_id': self.exam_id,
            'certificate_number': self.certificate_number,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': self.user.to_dict() if self.user else None,
            'exam': self.exam.to_dict() if self.exam else None
        }

class FormConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    config_json = db.Column(db.JSON)  # 存储表单字段配置
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<FormConfig {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'exam_id': self.exam_id,
            'config_json': self.config_json,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

