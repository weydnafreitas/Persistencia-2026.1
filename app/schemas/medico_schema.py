#Field para validação extra
#EmailStr ajuda na validação automática de e-mail
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# Validação da entrada de dados 
class MedicoCreate(BaseModel):
    nome: str
    crm: str = Field(..., min_length=1)
    especialidade: str
    email: EmailStr | None = None
    telefone: str 
    cidade: str
    uf: str = Field(..., min_length=2, max_length=2)
    ativo: bool = True

#Retorno de dados
class MedicoResponse(MedicoCreate):
    id: int 

    model_config = ConfigDict(from_attributes=True)