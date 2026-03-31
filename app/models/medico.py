from __future__ import annotations
 
from pydantic import BaseModel, field_validator
 
 
class Medico(BaseModel):
    id: int | None = None
    nome: str
    crm: str
    especialidade: str
    telefone: str
    email: str | None = None
    cidade: str
    uf: str
    ativo: bool = True
 
    @field_validator("crm")
    @classmethod
    def crm_nao_pode_ser_vazio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("CRM não pode ser vazio")
        return v.upper()
 
    @field_validator("uf")
    @classmethod
    def uf_deve_ter_dois_caracteres(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) != 2:
            raise ValueError("UF deve ter 2 caracteres")
        return v