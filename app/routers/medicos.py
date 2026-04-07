from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from deltalake import DeltaTable
from zipstream.ng import ZipStream
from pathlib import Path

from app.models.medico import Medico as MedicoModel
from app.schemas.medico_schema import MedicoResponse, MedicoCreate
from app.repositories.hospital_repository import HospitalRepository
from app.routers.hasher import calcular_hash

router = APIRouter(prefix="/medicos", tags=["Médicos"])
repo = HospitalRepository(model=MedicoModel, caminho="data/medicos")

#Contagem (GET /count) 
@router.get("/count")
def contar_medicos():
    return {"total": repo.count()}

#POST - inserção, busca, atualização, deleção
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MedicoResponse)
def criar_medico(medico_in: MedicoCreate):
    novo_medico_model = MedicoModel(**medico_in.model_dump())
    return repo.insert(novo_medico_model)

@router.get("/{id}", response_model=MedicoResponse)
def buscar_por_id(id: int):
    medico = repo.get(id)
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    return medico

@router.put("/{id}", response_model=MedicoResponse)
def atualizar_medico(id: int, dados: MedicoCreate):
    novos_dados = MedicoModel(**dados.model_dump())
    resultado = repo.update(id, novos_dados)
    if not resultado:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    return resultado

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_medico(id: int):
    if not repo.delete(id):
        raise HTTPException(status_code=404, detail="Médico não encontrado")

#GET - listagem paginada
@router.get("/", response_model=list[MedicoResponse])
def listar_medicos(
    pagina: int = Query(1, ge=1), 
    tamanho: int = Query(10, ge=1, le=100)
):
    return repo.listar(pagina=pagina, tamanho=tamanho)


#Exportação CSV via Streaming
@router.get("/exportar/csv")
def exportar_csv_streaming():
    def gerador_csv():
        yield "id,nome,crm,especialidade,ativo\n"
        tabela = DeltaTable("data/medicos")
        
        # leitura em lotes (batches) para preservar a RAM
        # to_batches garante que não carregamos tudo de uma vez
        for batch in tabela.to_pyarrow_dataset().to_batches(batch_size=100):
            for linha in batch.to_pylist():
                yield f"{linha['id']},{linha['nome']},{linha['crm']},{linha['especialidade']},{linha['ativo']}\n"

    return StreamingResponse(
        gerador_csv(), 
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=medicos.csv"}
    )

#Compactação

@router.get("/exportar/zip")

def exportar_medicos_zip():

    

    def gerar_linhas_csv():

        yield b"id,nome,crm,especialidade,ativo\n"

        

        # 1. Verifica se a tabela já foi inicializada no disco

        if not Path("data/medicos/_delta_log").exists():

            return # Interrompe e retorna apenas um CSV vazio com cabeçalho

            

        tabela = DeltaTable("data/medicos")



        for batch in tabela.to_pyarrow_dataset().to_batches(batch_size=100):

            for linha in batch.to_pylist():

                linha_texto = f"{linha['id']},{linha['nome']},{linha['crm']},{linha['especialidade']},{linha['ativo']}\n"

                yield linha_texto.encode('utf-8')



    stream_zip = ZipStream()

    stream_zip.add(gerar_linhas_csv(), "medicos.csv")



    return StreamingResponse(

        stream_zip,

        media_type="application/zip",

        headers={"Content-Disposition": "attachment; filename=exportacao_medicos.zip"}

    )


#Hash
@router.get("/hash/{algoritmo}")
def rota_hash(algoritmo: str, valor: str):
    try:
        resultado = calcular_hash(algoritmo, valor)
        return {"algoritmo": algoritmo, "hash": resultado}
    except KeyError:
        raise HTTPException(status_code=400, detail="Algoritmo não suportado.")