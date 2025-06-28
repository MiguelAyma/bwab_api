from sqlalchemy import JSON, Boolean, Integer, String, DECIMAL, DateTime, ForeignKey, ARRAY, Text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
import datetime
from sqlalchemy.dialects.postgresql import JSONB

class Base(DeclarativeBase):
    pass
class User(Base):
    __tablename__ = 'bwab_user'
    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))
    

class Theme(Base):
    __tablename__ = 'bwab_theme'
    theme_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("bwab_user.user_id"))
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)#TEXT 
    progress:  Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=True)
    num_stages: Mapped[int] = mapped_column(Integer, nullable=True)
    keep_content: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))
    roadmap_stages = relationship("RoadmapStage", back_populates="theme")



class RoadmapStage(Base):
    __tablename__ = 'bwab_roadmap_stage'
    roadmap_stage_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    theme_id: Mapped[int] = mapped_column(ForeignKey("bwab_theme.theme_id"))
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    flashcards: Mapped[JSON] = mapped_column(JSON, nullable=False)
    concept_map: Mapped[JSON] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))
    icon: Mapped[str] = mapped_column(String(30), nullable=True)#campo para emoji
    progress:  Mapped[float] = mapped_column(DECIMAL(10, 2))##
    theme = relationship("Theme", back_populates="roadmap_stages")



class Evaluation(Base):
    __tablename__ = 'bwab_evaluation'
    evaluation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    theme_id: Mapped[int] = mapped_column(ForeignKey("bwab_theme.theme_id"))
    roadmap_stage_id: Mapped[int] = mapped_column(ForeignKey("bwab_roadmap_stage.roadmap_stage_id"), nullable=True)
    questions: Mapped[JSON] = mapped_column(JSON, nullable=False)
    answers: Mapped[JSON] = mapped_column(JSON, nullable=True)
    score: Mapped[float] = mapped_column(DECIMAL(5, 2))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))
    

    


    
    
    
    
    