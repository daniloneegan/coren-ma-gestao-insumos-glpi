"""Modelos SQLAlchemy para estoque e trilha de movimentações."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Insumo(Base):
    """Material de TI controlado pelo estoque."""

    __tablename__ = "insumos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    categoria: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    saldo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estoque_minimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unidade: Mapped[str] = mapped_column(String(20), nullable=False, default="un")
    movimentacoes: Mapped[list["Movimentacao"]] = relationship(back_populates="insumo")


class Movimentacao(Base):
    """Registro imutável da baixa vinculada ao chamado GLPI."""

    __tablename__ = "movimentacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chamado_glpi_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    insumo_id: Mapped[int] = mapped_column(ForeignKey("insumos.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    tecnico_responsavel: Mapped[str] = mapped_column(String(120), nullable=False)
    data_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    insumo: Mapped[Insumo] = relationship(back_populates="movimentacoes")
