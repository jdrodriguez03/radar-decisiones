"""Genera data/processed/cache.json con todas las explicaciones de la demo. Dueño: Julian.

Qué entra al caché (día 11 del plan):
  1. El guion de COMPAÑIA 36, en orden: aguinaldo -> prima -> salario -> costo por baja a $30,000.
  2. Las historias de respaldo: COMPAÑIA 29 (prima -> prima y rutas) y COMPAÑIA 15 ($340 -> $350).
  3. Los 20 casos de scripts/combinaciones.yaml, cada uno solo (primera comparación).

Por qué con el motor real y no con los fixtures: la app calcula cada estado con
motor.api.calcular_estado. Si el texto del caché se generó con otras cifras, el validador
lo descarta en vivo y sale la plantilla. Generándolo con el mismo motor, las cifras coinciden.

Correr desde la raíz del repo, con la llave en .streamlit/secrets.toml o en ANTHROPIC_API_KEY:
    python scripts/generar_cache.py --mostrar   # solo lista las llaves, sin llamar a la IA
    python scripts/generar_cache.py             # pide solo las que faltan
    python scripts/generar_cache.py --rehacer   # borra el caché y pide todas de nuevo
"""
import argparse
import json
import os
import sys
from pathlib import Path

import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # para poder importar config, motor, ia y ui

import yaml

import config
from ia.cache import cargar as cargar_cache
from ia.cache import llave
from ia.precalcular import precalcular
from motor.api import calcular_estado
from motor.datos import cargar as cargar_empresas
from ui.selector import perfil_demo

RUTA_CASOS = config.RAIZ / "scripts" / "combinaciones.yaml"

# Cada secuencia es lo que pasa en pantalla entre dos cambios de empresa, en orden.
# Cada paso se explica con el paso anterior de su secuencia como "anterior" (así dice
# "quedan 16 empresas, antes 22"). Al cambiar de empresa la app borra lo explicado,
# por eso cada secuencia empieza sin anterior.
#   "caso": id de combinaciones.yaml, o un paso escrito aquí con empresa y palancas.
#   "costo_por_baja": solo si el paso cambia el supuesto (si no, el de supuestos.json).
SECUENCIAS = {
    "guion COMPAÑIA 36": [
        {"caso": "G1"},
        {"caso": "G2"},
        {"caso": "G3"},
        {"caso": "G3", "costo_por_baja": 30000},  # 3:45 del guion: el juez abre ⚙
    ],
    "respaldo COMPAÑIA 29": [
        {"caso": "R29-1"},
        {"caso": "R29-3"},
    ],
    "respaldo COMPAÑIA 15": [
        # No está en combinaciones.yaml; Juanes lo pidió en docs/guion.md (paso 1 del respaldo 2)
        {"empresa": "COMPAÑIA 15", "palancas": {"sal_dia_ini": 340}},
        {"caso": "R15-3"},
    ],
}


def cargar_casos(ruta=RUTA_CASOS):
    """Los casos de combinaciones.yaml, por id: {"G1": {"empresa": ..., "palancas": {...}}, ...}."""
    return {c["id"]: c for c in yaml.safe_load(ruta.read_text(encoding="utf-8"))["casos"]}


def estado_de(paso, casos, empresas, supuestos):
    """El estado real de un paso, calculado igual que en la app.

    1. El perfil sale de ui.selector.perfil_demo, la misma función que usa el selector.
    2. El "cambio" es la última palanca del paso (el último clic), de su valor real al nuevo.
    3. Los supuestos son los de supuestos.json, salvo que el paso cambie el costo por baja.
    """
    base = casos[paso["caso"]] if "caso" in paso else paso
    perfil = perfil_demo(empresas, base["empresa"])
    palancas = dict(base["palancas"])
    ultima = list(palancas)[-1]
    cambio = {"palanca": ultima, "de": perfil["palancas"].get(ultima), "a": palancas[ultima]}
    ajustes = dict(supuestos)
    if "costo_por_baja" in paso:
        ajustes["costo_por_baja"] = paso["costo_por_baja"]
    return calcular_estado(empresas, perfil, palancas, cambio, ajustes)


def armar_secuencias(casos, empresas, supuestos):
    """Todas las listas de estados que se mandan a precalcular, en orden.

    Primero las del guion y los respaldos (con su paso anterior); después cada uno de los
    20 casos solo. Los casos sueltos sirven si en vivo se llega a ellos por otro camino:
    ia/cache.py busca primero la llave con anterior y, si no está, la del estado solo.
    """
    secuencias = [
        [estado_de(paso, casos, empresas, supuestos) for paso in pasos] for pasos in SECUENCIAS.values()
    ]
    secuencias += [[estado_de({"caso": cid}, casos, empresas, supuestos)] for cid in casos]
    return secuencias


def llaves_de(secuencias):
    """Las llaves del caché que producirían las secuencias, sin repetir y en orden."""
    vistas = []
    for secuencia in secuencias:
        anterior = None
        for estado in secuencia:
            clave = llave(estado, anterior)
            if clave not in vistas:
                vistas.append(clave)
            anterior = estado
    return vistas


def poner_llave_api():
    """Si la llave no está en el entorno, la lee de .streamlit/secrets.toml.

    ia/explicar.py la busca en st.secrets, que solo existe dentro de Streamlit.
    Este script corre fuera de Streamlit, así que la pasamos al entorno nosotros.
    """
    if os.environ.get("ANTHROPIC_API_KEY"):
        return True
    ruta = config.RAIZ / ".streamlit" / "secrets.toml"
    if not ruta.exists():
        return False
    llave_api = tomllib.loads(ruta.read_text(encoding="utf-8")).get("ANTHROPIC_API_KEY")
    if llave_api:
        os.environ["ANTHROPIC_API_KEY"] = llave_api
    return bool(llave_api)


def generar(secuencias, cliente=None, ruta=None):
    """Manda cada secuencia a precalcular y junta los resúmenes sin repetir llaves."""
    total = {"guardadas": [], "ya_estaban": [], "fallidas": []}
    for secuencia in secuencias:
        resumen = precalcular(secuencia, cliente=cliente, ruta=ruta)
        for tipo, llaves in resumen.items():
            total[tipo] += [x for x in llaves if x not in total[tipo]]
    # Un estado que aparece en una secuencia y suelto (G1) se guarda una vez y luego "ya estaba"
    total["ya_estaban"] = [x for x in total["ya_estaban"] if x not in total["guardadas"]]
    return total


def main(argv=None, cliente=None):
    parser = argparse.ArgumentParser(description="Genera data/processed/cache.json con la IA.")
    parser.add_argument("--rehacer", action="store_true", help="borra el caché y vuelve a pedir todo")
    parser.add_argument("--mostrar", action="store_true", help="solo lista las llaves, sin llamar a la IA")
    args = parser.parse_args(argv)

    empresas = cargar_empresas()
    supuestos = json.loads(config.RUTA_SUPUESTOS.read_text(encoding="utf-8"))
    secuencias = armar_secuencias(cargar_casos(), empresas, supuestos)

    if args.mostrar:
        cache = cargar_cache()
        llaves = llaves_de(secuencias)
        for clave in llaves:
            print(f"  {'ya está ' if clave in cache else 'FALTA   '} {clave}")
        faltan = sum(1 for c in llaves if c not in cache)
        print(f"\n{len(llaves)} llaves, faltan {faltan}")
        return 0

    if cliente is None and not poner_llave_api():
        print("No encontré la llave: ponla en .streamlit/secrets.toml o en ANTHROPIC_API_KEY.")
        return 1

    if args.rehacer:
        config.RUTA_CACHE.unlink(missing_ok=True)

    total = generar(secuencias, cliente=cliente)
    for tipo in ("guardadas", "ya_estaban", "fallidas"):
        print(f"\n{tipo} ({len(total[tipo])}):")
        for clave in total[tipo]:
            print(f"  {clave}")
    print(f"\nCaché en {config.RUTA_CACHE.relative_to(config.RAIZ)}")
    return 1 if total["fallidas"] else 0  # código de salida 1 = algo falló, para verlo en la terminal


if __name__ == "__main__":
    sys.exit(main())
