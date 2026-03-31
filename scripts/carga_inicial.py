"""
Script de carga inicial — popula o banco com 1000 médicos realistas.
Executar o com: uv run python ../scripts/carga_inicial.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from random import choice, randint

from faker import Faker

from app.models.medico import Medico
from app.repositories.hospital_repository import HospitalRepository

fake = Faker("pt_BR")

ESPECIALIDADES = [
    "Cardiologia", "Pediatria", "Ortopedia", "Neurologia",
    "Dermatologia", "Ginecologia", "Oftalmologia", "Psiquiatria",
    "Endocrinologia", "Urologia", "Clínica Geral", "Oncologia",
    "Reumatologia", "Pneumologia", "Gastroenterologia",
]

UFS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
    "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]


def main() -> None:
    repo = HospitalRepository(Medico, "data/medicos")

    print("🏥 Iniciando carga inicial de médicos...\n")

    for i in range(1, 1001):
        uf = choice(UFS)
        medico = Medico(
            nome=fake.name(),
            crm=f"CRM/{uf} {randint(10000, 99999)}",
            especialidade=choice(ESPECIALIDADES),
            telefone=fake.phone_number(),
            email=fake.email() if randint(0, 1) else None,
            cidade=fake.city(),
            uf=uf,
            ativo=choice([True, True, True, False]),
        )
        repo.insert(medico)

        if i % 100 == 0:
            print(f"  {i} médicos inseridos...")

    print(f"\n✅ Carga concluída! Total: {repo.count()} médicos.")


if __name__ == "__main__":
    main()