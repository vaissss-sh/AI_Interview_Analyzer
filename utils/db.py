import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from utils.config import DB_PATH

Base = declarative_base()

class Candidate(Base):
    __tablename__ = 'candidates'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    role = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    sessions = relationship("Session", back_populates="candidate", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    overall_score = Column(Float, nullable=True)
    grade = Column(String(10), nullable=True)
    
    candidate = relationship("Candidate", back_populates="sessions")
    questions = relationship("Question", back_populates="session", cascade="all, delete-orphan")
    emotions = relationship("EmotionLog", back_populates="session", cascade="all, delete-orphan")
    score_breakdown = relationship("ScoreBreakdown", uselist=False, back_populates="session", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    text = Column(Text, nullable=False)
    answer_transcript = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("Session", back_populates="questions")

class EmotionLog(Base):
    __tablename__ = 'emotion_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    emotion = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    
    session = relationship("Session", back_populates="emotions")

class ScoreBreakdown(Base):
    __tablename__ = 'score_breakdowns'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    communication = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    technical = Column(Float, nullable=False)
    emotional_iq = Column(Float, nullable=False)
    engagement = Column(Float, nullable=False)
    professionalism = Column(Float, nullable=False)
    
    session = relationship("Session", back_populates="score_breakdown")

# Database initialization and Session maker
engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(bind=engine)

def create_tables() -> None:
    """Creates all tables in the SQLite database if they don't exist."""
    Base.metadata.create_all(engine)

def save_session(session_data: dict) -> int:
    """
    Saves a completed session from Streamlit state to the DB.
    session_data should contain candidate info, scores, etc.
    Returns the created session ID.
    """
    db = SessionLocal()
    try:
        # Check if candidate exists, or create new
        email = session_data.get('email', 'unknown@example.com')
        candidate = db.query(Candidate).filter(Candidate.email == email).first()
        if not candidate:
            candidate = Candidate(
                name=session_data.get('name', 'Unknown'),
                email=email,
                role=session_data.get('role', 'Unknown')
            )
            db.add(candidate)
            db.flush()

        # Create Session
        new_session = Session(
            candidate_id=candidate.id,
            start_time=session_data.get('start_time', datetime.utcnow()),
            end_time=datetime.utcnow(),
            overall_score=session_data.get('overall_score', 0.0),
            grade=session_data.get('grade', 'F')
        )
        db.add(new_session)
        db.flush()

        # Save Score Breakdown
        sb_data = session_data.get('score_breakdown', {})
        sb = ScoreBreakdown(
            session_id=new_session.id,
            communication=sb_data.get('communication', 0.0),
            confidence_score=sb_data.get('confidence', 0.0),
            technical=sb_data.get('technical', 0.0),
            emotional_iq=sb_data.get('emotional_iq', 0.0),
            engagement=sb_data.get('engagement', 0.0),
            professionalism=sb_data.get('professionalism', 0.0)
        )
        db.add(sb)

        # Save Questions/Answers
        questions_list = session_data.get('questions', [])
        for q in questions_list:
            db_q = Question(
                session_id=new_session.id,
                text=q.get('text', ''),
                answer_transcript=q.get('answer_transcript', ''),
                score=q.get('score', 0.0)
            )
            db.add(db_q)

        # Optional: Save emotion logs if provided
        emotion_logs = session_data.get('emotions', [])
        for e in emotion_logs:
            db_e = EmotionLog(
                session_id=new_session.id,
                emotion=e.get('emotion', 'neutral'),
                confidence=e.get('confidence', 0.0),
                timestamp=e.get('timestamp', datetime.utcnow())
            )
            db.add(db_e)

        db.commit()
        return new_session.id
    except Exception as e:
        db.rollback()
        print(f"Error saving session: {e}")
        return -1
    finally:
        db.close()

def get_all_sessions() -> list:
    """Returns a list of all sessions with basic details."""
    db = SessionLocal()
    try:
        sessions = db.query(Session).order_by(Session.start_time.desc()).all()
        return [{
            "id": s.id,
            "candidate_name": s.candidate.name,
            "role": s.candidate.role,
            "date": s.start_time.strftime("%Y-%m-%d %H:%M"),
            "score": s.overall_score,
            "grade": s.grade
        } for s in sessions]
    finally:
        db.close()

def get_session_by_id(session_id: int) -> dict:
    """Gets detailed info for a single session."""
    db = SessionLocal()
    try:
        s = db.query(Session).filter(Session.id == session_id).first()
        if not s:
            return {}
        return {
            "id": s.id,
            "candidate": {
                "name": s.candidate.name,
                "email": s.candidate.email,
                "role": s.candidate.role
            },
            "metrics": {
                "overall_score": s.overall_score,
                "grade": s.grade,
                "start_time": s.start_time,
                "end_time": s.end_time
            },
            "breakdown": {
                "communication": s.score_breakdown.communication,
                "confidence": s.score_breakdown.confidence_score,
                "technical": s.score_breakdown.technical,
                "emotional_iq": s.score_breakdown.emotional_iq,
                "engagement": s.score_breakdown.engagement,
                "professionalism": s.score_breakdown.professionalism
            } if s.score_breakdown else {},
            "questions": [
                {"text": q.text, "transcript": q.answer_transcript, "score": q.score}
                for q in s.questions
            ]
        }
    finally:
        db.close()

def delete_session(session_id: int) -> bool:
    """Deletes a session and its associated data."""
    db = SessionLocal()
    try:
        s = db.query(Session).filter(Session.id == session_id).first()
        if s:
            db.delete(s)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting session: {e}")
        return False
    finally:
        db.close()
