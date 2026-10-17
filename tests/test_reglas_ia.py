"""Los textos reales de la IA cumplen todas las reglas (meta del día 8: 15 de 15).

No llama a la IA: lee docs/textos_ia.json, que escribe scripts/probar_ia.py con tu llave.
Cada texto se guardó junto con su estado, así que aquí se revisa otra vez con las reglas
y el validador de HOY. Si mañana se endurece una regla, esta prueba lo nota sin gastar crédito.

Mientras docs/textos_ia.json no exista (antes de la primera corrida), las pruebas se saltan:
el CI queda en verde y en la salida de pytest aparecen como "skipped".
"""
import json

import pytest

from config import RAIZ
from ia.reglas import revisar
from ia.validador import cifras_inventadas

RUTA_TEXTOS = RAIZ / "docs" / "textos_ia.json"
CASOS_ESPERADOS = 15

if not RUTA_TEXTOS.exists():
    pytest.skip("aún no hay docs/textos_ia.json: correr scripts/probar_ia.py", allow_module_level=True)

RESULTADOS = json.loads(RUTA_TEXTOS.read_text(encoding="utf-8"))
POR_ID = {r["id"]: r for r in RESULTADOS}


def test_estan_los_15_casos():
    assert len(RESULTADOS) == CASOS_ESPERADOS


@pytest.mark.parametrize("caso", RESULTADOS, ids=[r["id"] for r in RESULTADOS])
def test_la_ia_respondio(caso):
    assert caso["texto"], f"{caso['id']} no tiene texto: {caso.get('error')}"


@pytest.mark.parametrize("caso", RESULTADOS, ids=[r["id"] for r in RESULTADOS])
def test_ninguna_cifra_inventada(caso):
    # El paso anterior también cuenta: "quedan 16 empresas, antes 22" (el 22 viene de G1).
    anterior = POR_ID[caso["anterior"]]["estado"] if caso.get("anterior") else None
    assert cifras_inventadas(caso["texto"], caso["estado"], anterior) == []


@pytest.mark.parametrize("caso", RESULTADOS, ids=[r["id"] for r in RESULTADOS])
def test_cumple_las_reglas_de_lenguaje(caso):
    # revisar() devuelve la lista de lo que falla: así pytest muestra QUÉ regla no se cumplió.
    assert revisar(caso["texto"], caso["estado"]) == []
