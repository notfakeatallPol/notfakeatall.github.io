from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json
from cryptography.fernet import Fernet
import base64

class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    submissions = db.relationship('Submission', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class SystemConfig(db.Model):
    __tablename__ = "system_config"
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    
    @classmethod
    def get(cls, key, default=None):
        config = cls.query.filter_by(key=key).first()
        return config.value if config else default
    
    @classmethod
    def set(cls, key, value):
        config = cls.query.filter_by(key=key).first()
        if config:
            config.value = value
        else:
            config = cls(key=key, value=value)
            db.session.add(config)
        db.session.commit()
        return config

class EncryptedData:
    @staticmethod
    def get_key():
        key = SystemConfig.get('encryption_key')
        if not key:
            # Generate a new key if it doesn't exist
            key = Fernet.generate_key().decode()
            SystemConfig.set('encryption_key', key)
        return key.encode()
    
    @staticmethod
    def encrypt(data):
        if data is None:
            return None
        
        # Convert data to string if it's not already
        if not isinstance(data, str):
            data = json.dumps(data)
            
        # Encrypt the data
        f = Fernet(EncryptedData.get_key())
        return f.encrypt(data.encode()).decode()
    
    @staticmethod
    def decrypt(encrypted_data):
        if encrypted_data is None:
            return None
            
        # Decrypt the data
        f = Fernet(EncryptedData.get_key())
        decrypted = f.decrypt(encrypted_data.encode()).decode()
        
        # Try to parse JSON, return as string if it fails
        try:
            return json.loads(decrypted)
        except:
            return decrypted

class Submission(db.Model):
    __tablename__ = "submissions"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    caption = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(256), nullable=True)
    _encrypted_caption = db.Column('encrypted_caption', db.Text, nullable=True)
    status = db.Column(db.String(20), default="pending")  # 'pending', 'accepted', 'rejected', 'needs_edits'
    admin_comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Encrypted caption property
    @property
    def encrypted_caption(self):
        return EncryptedData.decrypt(self._encrypted_caption)
    
    @encrypted_caption.setter
    def encrypted_caption(self, value):
        self._encrypted_caption = EncryptedData.encrypt(value)
    
    def __repr__(self):
        return f'<Submission {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'caption': self.caption,
            'image_path': self.image_path,
            'status': self.status,
            'admin_comment': self.admin_comment,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
