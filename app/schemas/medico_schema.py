'''Arquivo que garante a integridade dos dados de entrada'''

from pydantic import BaseModel, EmailStr, Field, ConfigDict

# Validação da entrada de dados 
class MedicoCreate(BaseModel):
    nome: str
    crm: str = Field(..., min_length=1) # Field para validação extra (tamanho)
    especialidade: str
    email: EmailStr | None = None # EmailStr ajuda na validação automática de e-mail
    telefone: str 
    cidade: str
    uf: str = Field(..., min_length=2, max_length=2)
    ativo: bool = True

# Retorno de dados
class MedicoResponse(MedicoCreate):
    id: int

    # Conversão dos dados brutos do delta lake em JSON
    model_config = ConfigDict(from_attributes=True)