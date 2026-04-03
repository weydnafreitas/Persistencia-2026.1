from __future__ import annotations
from pathlib import Path
import pyarrow as pa
import pyarrow.compute as pc
from deltalake import DeltaTable, write_deltalake
from pydantic import BaseModel

class HospitalRepository[T: BaseModel]:
    def __init__(self, model: type[T], caminho: str) -> None:
        self._model = model
        self._caminho = caminho
        self._arquivo_seq = Path(f"{caminho}.seq")
        Path(caminho).mkdir(parents=True, exist_ok=True)

    def _proximo_id(self) -> int:
        #gerenciamento do autoincremento persistente no .seq
        atual = int(self._arquivo_seq.read_text()) if self._arquivo_seq.exists() else 0
        proximo = atual + 1
        self._arquivo_seq.write_text(str(proximo))
        return proximo

    def _para_tabela_arrow(self, obj: T) -> pa.Table:
        dados = obj.model_dump()
        arrays = {}
        for k, v in dados.items():
            if v is None:
                arrays[k] = pa.array([None], type=pa.string())
            elif isinstance(v, bool):
                arrays[k] = pa.array([v], type=pa.bool_())
            elif isinstance(v, int):
                arrays[k] = pa.array([v], type=pa.int64())
            elif isinstance(v, float):
                arrays[k] = pa.array([v], type=pa.float64())
            else:
                arrays[k] = pa.array([str(v)], type=pa.string())
        return pa.table(arrays)

    def _tabela_existe(self) -> bool:
        return (Path(self._caminho) / "_delta_log").exists()
    
    #operações f1-f4
    def insert(self, obj: T) -> T:
        #f1:inserção com id automatico
        obj = obj.model_copy(update={"id": self._proximo_id()})
        write_deltalake(self._caminho, self._para_tabela_arrow(obj), mode="append")
        return obj

    def get(self, id: int) -> T | None:
        #f3:recuperação de um registro por id usando batches para poupar ram
        if not self._tabela_existe():
            return None

        tabela = DeltaTable(self._caminho)
        for batch in tabela.to_pyarrow_dataset().to_batches():
            filtrado = batch.filter(pc.field("id") == id)
            if filtrado.num_rows > 0:
                return self._model(**filtrado.to_pylist()[0])
        return None

    def listar(self, pagina: int = 1, tamanho: int = 10) -> list[T]:
        #f2: listagem paginada via .to_batches()
        if not self._tabela_existe():
            return []

        inicio = (pagina - 1) * tamanho
        fim = inicio + tamanho
        vistos = 0
        resultado: list[T] = []

        tabela = DeltaTable(self._caminho)
        for batch in tabela.to_pyarrow_dataset().to_batches(batch_size=tamanho):
            batch_size = batch.num_rows

            if vistos + batch_size <= inicio:
                vistos += batch_size
                continue

            for row in batch.to_pylist():
                if vistos >= inicio and vistos < fim:
                    resultado.append(self._model(**row))
                vistos += 1
                if vistos >= fim:
                    return resultado
        return resultado

    def update(self, id: int, novos_dados: T) -> T | None:
        #f3: atualização direta no arq delta sem reescrita integral
        if not self._tabela_existe() or self.get(id) is None:
            return None

        tabela = DeltaTable(self._caminho)
        atualizados = novos_dados.model_dump(exclude={"id"})
        
        tabela.update(
            predicate=f"id = {id}",
            updates={k: f"'{v}'" if isinstance(v, str) else str(v) for k, v in atualizados.items()},
        )

        return self.get(id)

    def delete(self, id: int) -> bool:
        #remoção via log de transações
        if not self._tabela_existe() or self.get(id) is None:
            return False

        DeltaTable(self._caminho).delete(predicate=f"id = {id}")
        return True

    def count(self) -> int:
        #contagem total
        if not self._tabela_existe():
            return 0

        actions = DeltaTable(self._caminho).get_add_actions()
        valores = actions.column("num_records").to_pylist()
        return sum(v for v in valores if v is not None)

#regras de negocio
    def existe_por_crm(self, crm: str) -> bool:

        #verifica duplicatas sem carregar a tabela toda na ram
        if not self._tabela_existe():
            return False
        tabela = DeltaTable(self._caminho)

        for batch in tabela.to_pyarrow_dataset().to_batches():
            filtrado = batch.filter(pc.field("crm") == crm)
            if filtrado.num_rows > 0:
                return True
        return False

    def vacuum(self, horas_retencao: int = 168) -> list[str]:
        if not self._tabela_existe():
            return []

        return DeltaTable(self._caminho).vacuum(
            retention_hours=horas_retencao,
            enforce_retention_duration=False,
        )