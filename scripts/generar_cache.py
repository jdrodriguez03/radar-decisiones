"""Ejecuta ia/precalcular.py y guarda data/processed/cache.json. Dueño: Julian.

Correr desde la raíz del repo, con la llave en .streamlit/secrets.toml o en ANTHROPIC_API_KEY:
    python scripts/generar_cache.py            # solo pide los que faltan
    python scripts/generar_cache.py --rehacer  # vuelve a pedir todos
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # para poder importar config e ia

import config
from ia.precalcular import precalcular

# El guion en orden: cada paso se explica comparado con el anterior (así dice "antes 22").
GUION = ["05_inicial", "01_aguinaldo", "02_prima", "03_salario"]
# Además, cada fixture solo, por si en vivo se llega a él por otro camino.
SUELTOS = ["01_aguinaldo", "02_prima", "03_salario", "04_ya_rota_menos", "05_inicial"]


def cargar(nombre):
    return json.loads((config.RUTA_FIXTURES / f"{nombre}.json").read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Genera data/processed/cache.json con la IA.")
    parser.add_argument("--rehacer", action="store_true", help="vuelve a pedir también los que ya están")
    args = parser.parse_args()

    if args.rehacer:
        # Se borra y se arma de cero: así un estado que aparece en el guion y suelto
        # (01 tiene la misma llave en los dos) se pide una sola vez.
        config.RUTA_CACHE.unlink(missing_ok=True)

    total = {"guardadas": [], "ya_estaban": [], "fallidas": []}
    secuencias = [[cargar(n) for n in GUION]] + [[cargar(n)] for n in SUELTOS]
    for secuencia in secuencias:
        resumen = precalcular(secuencia)
        for clave, llaves in resumen.items():
            total[clave] += [x for x in llaves if x not in total[clave]]

    # 01 se guarda en el guion y después aparece como "ya estaba" al pedirlo suelto: se muestra una vez
    total["ya_estaban"] = [x for x in total["ya_estaban"] if x not in total["guardadas"]]
    for clave in ("guardadas", "ya_estaban", "fallidas"):
        print(f"\n{clave} ({len(total[clave])}):")
        for x in total[clave]:
            print(f"  {x}")
    print(f"\nCaché en {config.RUTA_CACHE.relative_to(config.RAIZ)}")
    return 1 if total["fallidas"] else 0  # código de salida 1 = algo falló, para verlo en la terminal


if __name__ == "__main__":
    sys.exit(main())
