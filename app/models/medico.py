from __future__ import annotations
from pydantic import BaseModel, field_validator
from fastapi import APIRouter, Query, status

from app.schemas.medico_schema import MedicoCreate
from app.core.exceptions import RegraNegocioException, EntidadeNaoEncontradaException
from app.repositories.hospital_repository import HospitalRepository
from app.core.config import DATA_DIR
 
 
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

    # --- FILTROS ---

router = APIRouter(tags=["Médicos"])
repo = HospitalRepository(Medico, str(DATA_DIR / "medicos"))

@router.get("/busca/avancada", response_model=list[Medico], summary="Busca avançada de médicos com múltiplos filtros")
def buscar_medicos_avancado(
    especialidade: str | None = Query(None, description="Filtrar médicos pela especialidade (ex: Cardiologia)"),
    cidade: str | None = Query(None, description="Filtrar pela cidade de atuação"),
    uf: str | None = Query(None, description="Filtrar pelo estado (sigla com 2 letras)"),
    ativo: bool | None = Query(None, description="Filtrar por médicos ativos (true) ou inativos (false)")
):
    return repo.buscar_por_filtros(especialidade=especialidade, cidade=cidade, uf=uf, ativo=ativo)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Medico, summary="Cadastrar um novo médico")
def criar_medico(medico_in: MedicoCreate):
    if repo.existe_por_crm(medico_in.crm):
        raise RegraNegocioException(f"Já existe um médico cadastrado com o CRM {medico_in.crm}")
    novo_medico_model = Medico(**medico_in.model_dump())
    return repo.insert(novo_medico_model)

@router.get("/{id}", response_model=Medico, summary="Obter médico por ID")
def buscar_por_id(id: int):
    medico = repo.get(id)
    if not medico:
        raise EntidadeNaoEncontradaException(entidade="Médico", id_ou_parametro=id)
    return medico