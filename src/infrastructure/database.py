
import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()

# MODELS
class PriorAuthRequest(Base):
    __tablename__ = 'prior_auth_requests'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, index=True)
    payer_id = Column(String)
    procedure_code = Column(String)
    diagnosis_code = Column(String)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    payload = Column(JSON) # Store full request payload
    agent_response = Column(JSON, nullable=True) # Store FHIR/EDI response
    decision_reason = Column(Text, nullable=True)
    risk_score = Column(Integer, nullable=True) # Stored as int (0-100) or float? let's user float
    
class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow)
    action = Column(String)
    agent = Column(String)
    details = Column(Text)

# REPOSITORY
class Repository:
    def __init__(self, db_url=None):
        if not db_url:
            # Default to SQLite for local dev
            db_url = os.getenv("DATABASE_URL", "sqlite:///app.db")
        
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_request(self, data):
        session = self.Session()
        try:
            req = PriorAuthRequest(
                patient_id=data.get('patient_id'),
                payer_id=data.get('payer_id'),
                procedure_code=data.get('procedure_code'),
                diagnosis_code=data.get('diagnosis_code'),
                payload=data
            )
            session.add(req)
            session.commit()
            return req.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_status(self, request_id, status, reason=None, risk_score=None, agent_response=None):
        session = self.Session()
        try:
            req = session.query(PriorAuthRequest).filter_by(id=request_id).first()
            if req:
                req.status = status
                if reason:
                    req.decision_reason = reason
                if risk_score is not None:
                    req.risk_score = risk_score
                if agent_response:
                    req.agent_response = agent_response
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_status_details(self, request_id):
        session = self.Session()
        try:
            req = session.query(PriorAuthRequest).filter_by(id=request_id).first()
            if req:
                return {
                    "status": req.status,
                    "risk_score": req.risk_score,
                    "reason": req.decision_reason,
                    "agent_response": req.agent_response
                }
            return None
        finally:
            session.close()

    def get_status(self, request_id):
        session = self.Session()
        try:
            req = session.query(PriorAuthRequest).filter_by(id=request_id).first()
            return req.status if req else "UNKNOWN"
        finally:
            session.close()
            
    def log_audit(self, agent, action, details):
        session = self.Session()
        try:
            log = AuditLog(agent=agent, action=action, details=details)
            session.add(log)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
