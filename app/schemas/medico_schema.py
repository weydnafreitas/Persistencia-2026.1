#Field para validação extra
#EmailStr ajuda na validação automática de e-mail
from pydantic import BaseModel, EmailStr, Field 

#POST - envio de dados para criar médico
class MedicoCreate(BaseModel):
    nome: str
    crm: str = Field(..., min_length=1)
    especialidade: str
    email: EmailStr | None = None
    telefone: str 
    cidade: str
    uf: str = Field(..., min_length=2, max_length=2)
    ativo: bool= True

#GET/PUT - quando a API devolver os dados
class MedicoResponse(MedicoCreate):
    id: int 

    class Config:
        from_attributes = True