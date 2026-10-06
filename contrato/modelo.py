"""Validación del contrato JSON con pydantic. Dueño: Juanes."""

from typing import Literal, Optional

from pydantic import BaseModel


class Indicadores(BaseModel):
    rot_anual: float
    rot_temprana: Optional[float] = None
    ausentismo: Optional[float] = None


class Empresa(BaseModel):
    id: str
    plantilla_op: int
    palancas: dict[str, float]
    indicadores: Indicadores


class Cambio(BaseModel):
    palanca: str
    de: float
    a: float


class Grupo(BaseModel):
    n: int
    completado: bool
    ids: list[str]
    indicadores: Indicadores


class Resto(BaseModel):
    n: int
    ids: list[str]
    indicadores: Optional[Indicadores] = None  # vacío en el estado inicial


class Senal(BaseModel):
    etiqueta: Literal["clara", "débil", "no concluyente", "no aplica"]
    p: Optional[float] = None


class EnComun(BaseModel):
    texto: str
    grupo: str | float
    resto: str | float


class Pesos(BaseModel):
    costo_medida_anual: float
    costo_brecha_anual: float
    supuestos: dict[str, float]


class Explicacion(BaseModel):
    fuente: Literal["llm", "plantilla", "cache"]
    texto: str


class Meta(BaseModel):
    version: int


class Estado(BaseModel):
    meta: Meta
    empresa: Empresa
    cambio: Optional[Cambio] = None          # None en el estado inicial
    palancas_movidas: dict[str, float]
    grupo: Grupo
    resto: Resto
    senal: Senal
    en_comun: list[EnComun]
    pesos: Pesos
    explicacion: Optional[Explicacion] = None


def validar(datos : dict) -> Estado:
    """Devuelve el Estado si el JSON cumple el contrato; si no, lanza ValidationError."""
    return Estado.model_validate(datos)
