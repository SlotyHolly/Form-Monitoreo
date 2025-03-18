from datetime import datetime, timedelta
from flask_login import UserMixin
from . import db  # asumiendo que tu __init__.py hace db = SQLAlchemy()

def utc_minus_3():
    return datetime.utcnow() - timedelta(hours=3)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    # Relación con HistoryReports (uno a muchos)
    history_reports = db.relationship('HistoryReports', back_populates='user')

    def __repr__(self):
        return f'<User {self.userName}>'

class HistoryReports(db.Model):
    __tablename__ = 'history_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_minus_3, nullable=False)

    # Relación inversa con User
    user = db.relationship('User', back_populates='history_reports')
    
    # Relación con QueueReports (1 a 1 o 1 a n, según tu requerimiento)
    queue_reports = db.relationship('QueueReports', back_populates='history_report', uselist=False)
      # Si esperas uno-a-uno, pones uselist=False
      # Si esperas varios records en la cola por cada history_report, omites uselist=False

    # Relaciones a las demás tablas que apuntan a id_history
    failed_connections = db.relationship('FailedConnection', back_populates='history')
    failed_ips = db.relationship('FailedIp', back_populates='history')
    created_users = db.relationship('CreatedUser', back_populates='history')
    blocked_users = db.relationship('BlockedUsers', back_populates='history')
    blocked_ips = db.relationship('BlockedIp', back_populates='history')

    def __repr__(self):
        return f'<HistoryReports {self.id} - user_id={self.user_id}>'

class QueueReports(db.Model):
    __tablename__ = 'queue_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('history_reports.id'), nullable=False)
    
    # Relación con HistoryReports
    history_report = db.relationship('HistoryReports', back_populates='queue_reports')
    
    def __repr__(self):
        return f'<QueueReports {self.id} - report_id={self.report_id}>'


class FailedConnection(db.Model):
    __tablename__ = 'failed_connection'
    
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), nullable=False)
    server = db.Column(db.String(50), nullable=False)
    count = db.Column(db.Integer, default=0)
    
    id_history = db.Column(db.Integer, db.ForeignKey('history_reports.id'), nullable=False)
    history = db.relationship('HistoryReports', back_populates='failed_connections')

    def __repr__(self):
        return f'<FailedConnection {self.id} - user={self.user}>'


class FailedIp(db.Model):
    __tablename__ = 'failed_ip'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50))
    server = db.Column(db.String(50))
    count = db.Column(db.Integer, default=0)
    
    id_history = db.Column(db.Integer, db.ForeignKey('history_reports.id'), nullable=False)
    history = db.relationship('HistoryReports', back_populates='failed_ips')

    def __repr__(self):
        return f'<FailedIp {self.id} - IP={self.ip_address}>'


class CreatedUser(db.Model):
    __tablename__ = 'created_user'
    
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), nullable=False)
    uid = db.Column(db.String(50))
    path = db.Column(db.String(255))
    shell = db.Column(db.String(50))
    server = db.Column(db.String(50))
    date = db.Column(db.String(50))  # o db.DateTime, según necesites
    
    id_history = db.Column(db.Integer, db.ForeignKey('history_reports.id'), nullable=False)
    history = db.relationship('HistoryReports', back_populates='created_users')

    def __repr__(self):
        return f'<CreatedUser {self.id} - user={self.user}>'


class BlockedUsers(db.Model):
    __tablename__ = 'blocked_users'
    
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), nullable=False)
    server = db.Column(db.String(50))
    date = db.Column(db.String(50))  # o db.DateTime
    
    id_history = db.Column(db.Integer, db.ForeignKey('history_reports.id'), nullable=False)
    history = db.relationship('HistoryReports', back_populates='blocked_users')

    def __repr__(self):
        return f'<BlockedUsers {self.id} - user={self.user}>'


class BlockedIp(db.Model):
    __tablename__ = 'blocked_ip'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50))
    server = db.Column(db.String(50))  # según tu diagrama
    date = db.Column(db.String(50))      # o db.DateTime
    
    id_history = db.Column(db.Integer, db.ForeignKey('history_reports.id'), nullable=False)
    history = db.relationship('HistoryReports', back_populates='blocked_ips')

    def __repr__(self):
        return f'<BlockedIp {self.id} - ip_address={self.ip_address}>'
