from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class DigitalFootprintScan(db.Model):
    __tablename__ = 'digital_footprint_scans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # twitter, linkedin, youtube, etc.
    username = db.Column(db.String(100), nullable=False)
    scan_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    raw_data = db.Column(db.Text)  # JSON string of scraped data
    analysis_results = db.Column(db.Text)  # JSON string of AI analysis
    risk_score = db.Column(db.Float, default=0.0)  # 0-100 risk score
    
    def __repr__(self):
        return f'<DigitalFootprintScan {self.platform}:{self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'platform': self.platform,
            'username': self.username,
            'scan_date': self.scan_date.isoformat() if self.scan_date else None,
            'status': self.status,
            'raw_data': json.loads(self.raw_data) if self.raw_data else None,
            'analysis_results': json.loads(self.analysis_results) if self.analysis_results else None,
            'risk_score': self.risk_score
        }
    
    def set_raw_data(self, data):
        """Set raw data as JSON string"""
        self.raw_data = json.dumps(data) if data else None
    
    def set_analysis_results(self, results):
        """Set analysis results as JSON string"""
        self.analysis_results = json.dumps(results) if results else None

class PlatformConfig(db.Model):
    __tablename__ = 'platform_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    scan_frequency = db.Column(db.Integer, default=24)  # hours between scans
    last_scan = db.Column(db.DateTime)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PlatformConfig {self.platform}:{self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'platform': self.platform,
            'username': self.username,
            'enabled': self.enabled,
            'scan_frequency': self.scan_frequency,
            'last_scan': self.last_scan.isoformat() if self.last_scan else None,
            'created_date': self.created_date.isoformat() if self.created_date else None
        }

class RiskAlert(db.Model):
    __tablename__ = 'risk_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('digital_footprint_scans.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # content_risk, privacy_risk, professional_risk
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    recommendation = db.Column(db.Text)
    acknowledged = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RiskAlert {self.alert_type}:{self.severity}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'recommendation': self.recommendation,
            'acknowledged': self.acknowledged,
            'created_date': self.created_date.isoformat() if self.created_date else None
        }

