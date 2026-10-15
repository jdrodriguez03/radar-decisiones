"""Regenera los 5 fixtures con la salida REAL del motor. Dueño: Juanes.

Para qué sirve: en el bloque 1 escribimos los fixtures (contrato/fixtures/*.json)
a mano, con cifras del guion, para que Gaby y Julian pudieran trabajar sin esperar
al motor. Desde el día 6 el motor real (motor.api.calcular_estado) ya existe en main,
así que hoy (día 7) los reemplazamos por lo que el motor de verdad produce.

Reglas:
- Los nombres de archivo NO cambian (01_aguinaldo.json ... 05_inicial.json): otras
  piezas los abren por nombre (sandbox de Gaby, caché de Julian, pruebas).
- Cada fixture se valida contra contrato/modelo.py antes de guardarse.
- Cada fixture tiene una condición que debe seguir cumpliendo (por ejemplo, el 04
  debe tener brecha 0). Si el motor real ya no la cumple, el script se detiene.
- La explicación (texto de la IA) se conserva solo si las cifras no cambiaron; si
  cambiaron, se quita para que no diga números viejos (Julian la regenera).

Cómo se corre (desde la raíz del repositorio):
    python scripts/regenerar_fixtures.py            # regenera y guarda
    python scripts/regenerar_fixtures.py --revisar  # solo muestra qué cambiaría
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from config import RUTA_FIXTURES
from contrato.modelo import validar
from scripts.correr_combinaciones import (
    cambio_de,
    cargar_supuestos,
    pct,
    perfil_de_empresa,
    pesos,
)

# ---------------------------------------------------------------------------
# 1. Qué representa cada fixture
# ---------------------------------------------------------------------------
# El ORDEN de las palancas importa: la última es el "cambio" (lo que el usuario
# acaba de mover). Así el 02 dice "venía del aguinaldo y ahora movió la prima".
FIXTURES = [
    {
        "archivo": "01_aguinaldo.json",
        "empresa": "COMPAÑIA 36",
        "palancas": {"aguinaldo_op": 20},
        "condicion": "guion paso 1: 22 empresas en el grupo",
        "cumple": lambda e: e["grupo"]["n"] == 22,
    },
    {
        "archivo": "02_prima.json",
        "empresa": "COMPAÑIA 36",
        "palancas": {"aguinaldo_op": 20, "prima_vac_op": 0.50},
        "condicion": "guion paso 2: 16 empresas y señal débil",
        "cumple": lambda e: e["grupo"]["n"] == 16 and e["senal"]["etiqueta"] == "débil",
    },
    {
        "archivo": "03_salario.json",
        "empresa": "COMPAÑIA 36",
        "palancas": {"aguinaldo_op": 20, "prima_vac_op": 0.50, "sal_dia_ini": 350},
        "condicion": "guion paso 3: 5 empresas y señal no concluyente",
        "cumple": lambda e: (
            e["grupo"]["n"] == 5 and e["senal"]["etiqueta"] == "no concluyente"
        ),
    },
    {
        "archivo": "04_ya_rota_menos.json",
        "empresa": "COMPAÑIA 37",
        "palancas": {"vales_op": 0.12},
        "condicion": "la empresa ya rota menos que el grupo: brecha en 0",
        "cumple": lambda e: e["pesos"]["costo_brecha_anual"] == 0,
    },
    {
        "archivo": "05_inicial.json",
        "empresa": "COMPAÑIA 36",
        "palancas": {},
        "condicion": "estado inicial: sin palancas movidas, sin cambio y medida en 0",
        "cumple": lambda e: (
            e["cambio"] is None
            and e["palancas_movidas"] == {}
            and e["pesos"]["costo_medida_anual"] == 0
        ),
    },
]


# ---------------------------------------------------------------------------
# 2. Construir un fixture con el motor real
# ---------------------------------------------------------------------------
def construir(empresas, definicion, supuestos):
    """Llama al motor real y devuelve el contrato de un fixture, ya validado."""
    from motor.api import calcular_estado

    perfil = perfil_de_empresa(empresas, definicion["empresa"])
    movidas = dict(definicion["palancas"])
    estado = calcular_estado(empresas, perfil, movidas, cambio_de(perfil, movidas), supuestos)
    validar(estado)  # si falta un campo o un tipo no cuadra, aquí truena con un error claro
    if not definicion["cumple"](estado):
        raise AssertionError(
            f"{definicion['archivo']} ya no cumple su condición "
            f"({definicion['condicion']}). Revisar con Aleja antes de seguir."
        )
    return estado


# ---------------------------------------------------------------------------
# 3. Comparar el fixture viejo contra el nuevo
# ---------------------------------------------------------------------------
def cifras_clave(estado):
    """Las cifras que se ven en pantalla y que narra la IA."""
    grupo, resto = estado["grupo"], estado["resto"]
    return {
        "n grupo": grupo["n"],
        "n resto": resto["n"],
        "rot. grupo": round(grupo["indicadores"]["rot_anual"], 3),
        "rot. resto": None if not resto.get("indicadores") else round(
            resto["indicadores"]["rot_anual"], 3
        ),
        "señal": estado["senal"]["etiqueta"],
        "completado": grupo["completado"],
        "costo medida": round(estado["pesos"]["costo_medida_anual"]),
        "costo brecha": round(estado["pesos"]["costo_brecha_anual"]),
        "ids grupo": sorted(grupo["ids"]),
    }


def diferencias(viejo, nuevo):
    """Lista legible de lo que cambió entre dos fixtures. Vacía si no cambió nada."""
    if viejo is None:
        return ["(el archivo no existía)"]
    a, b = cifras_clave(viejo), cifras_clave(nuevo)
    cambios = []
    for clave in a:
        if a[clave] != b[clave]:
            if clave == "ids grupo":
                cambios.append(f"ids del grupo: {len(a[clave])} → {len(b[clave])} empresas")
            else:
                antes, despues = _bonito(clave, a[clave]), _bonito(clave, b[clave])
                cambios.append(f"{clave}: {antes} → {despues}")
    return cambios


def _bonito(clave, valor):
    if valor is None:
        return "—"
    if clave.startswith("rot"):
        return pct(valor)
    if clave.startswith("costo"):
        return pesos(valor)
    return str(valor)


def conservar_explicacion(viejo, nuevo):
    """Copia la explicación vieja al nuevo fixture solo si las cifras clave no cambiaron."""
    if viejo and viejo.get("explicacion") and not diferencias(viejo, nuevo):
        nuevo["explicacion"] = viejo["explicacion"]
    else:
        nuevo.pop("explicacion", None)
    return nuevo


# ---------------------------------------------------------------------------
# 4. Programa principal
# ---------------------------------------------------------------------------
def leer(ruta):
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else None


def main(empresas=None, carpeta=RUTA_FIXTURES, revisar=False):
    if empresas is None:
        from motor.datos import cargar

        empresas = cargar()
    supuestos = cargar_supuestos()
    carpeta.mkdir(parents=True, exist_ok=True)

    for definicion in FIXTURES:
        ruta = carpeta / definicion["archivo"]
        viejo = leer(ruta)
        nuevo = conservar_explicacion(viejo, construir(empresas, definicion, supuestos))
        cambios = diferencias(viejo, nuevo)

        print(f"\n{definicion['archivo']}  ✓ valida y cumple: {definicion['condicion']}")
        for linea in cambios or ["sin cambios en las cifras"]:
            print(f"   · {linea}")

        if not revisar:
            texto = json.dumps(nuevo, ensure_ascii=False, indent=2) + "\n"
            ruta.write_text(texto, encoding="utf-8")

    print("\nModo revisión: no se guardó nada." if revisar else "\nListo: 5 fixtures guardados.")


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    lector.add_argument("--revisar", action="store_true", help="mostrar cambios sin guardar")
    main(revisar=lector.parse_args().revisar)