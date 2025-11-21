"""
Database models for the VenÃ¢ncio complaint system
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Complaint(Base):
    """Model for storing Reclame Aqui complaints"""
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)

    # Dados do scraping
    title = Column(String(500))
    text = Column(Text, nullable=False)
    user_name = Column(String(200))
    complaint_date = Column(DateTime, nullable=True)
    status = Column(String(100))  # Respondida, NÃ£o respondida, Resolvida
    category = Column(String(200), nullable=True)
    location = Column(String(200), nullable=True)
    external_id = Column(String(100), unique=True, nullable=True, index=True)  # ID do Reclame Aqui

    # Classificação loja física vs online (preenchido por IA)
    store_type = Column(String(50), nullable=True)  # physical, online, unknown

    # Tags inteligentes (preenchido por IA - distribuição média)
    tags = Column(JSON, nullable=True)  # Array de tags específicas

    # Resposta da empresa no Reclame Aqui (scraped)
    company_response_text = Column(Text, nullable=True)  # Texto da resposta da empresa
    company_response_date = Column(DateTime, nullable=True)  # Data da resposta
    customer_evaluation = Column(Text, nullable=True)  # Texto da avaliação do cliente
    evaluation_date = Column(DateTime, nullable=True)  # Data da avaliação pelo cliente

    # Análise (preenchido por Chat B)
    sentiment = Column(String(50), nullable=True)  # Negativo, Neutro, Positivo
    sentiment_score = Column(Float, nullable=True)  # 0-10
    classification = Column(JSON, nullable=True)  # Array de categorias
    entities = Column(JSON, nullable=True)  # Entidades extraÃ­das
    urgency_score = Column(Float, nullable=True)  # 0-10

    # Resposta (preenchido por Chat C)
    response_generated = Column(Text, nullable=True)
    response_edited = Column(Text, nullable=True)
    coupon_code = Column(String(50), nullable=True)
    coupon_discount = Column(Integer, nullable=True)  # Percentual
    response_sent = Column(Boolean, default=False)
    response_sent_at = Column(DateTime, nullable=True)

    # Metadata
    scraped_at = Column(DateTime, server_default=func.now(), nullable=False)
    analyzed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Complaint {self.id}: {self.title[:50] if self.title else 'N/A'}...>"


class Coupon(Base):
    """Model for discount coupons"""
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    discount_percent = Column(Integer, nullable=False)
    complaint_id = Column(Integer, ForeignKey('complaints.id'))

    valid_from = Column(DateTime, server_default=func.now())
    valid_until = Column(DateTime)  # 30 dias

    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    complaint = relationship("Complaint", backref="coupon")

    def __repr__(self):
        return f"<Coupon {self.code}: {self.discount_percent}% - {'Used' if self.is_used else 'Valid'}>"
