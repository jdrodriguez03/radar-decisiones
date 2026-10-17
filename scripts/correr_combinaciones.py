"""Corre las 20 combinaciones y escribe docs/resultados_combinaciones.md. Dueño: Juanes.

Para qué sirve: antes de la demo queremos saber qué pasa en las 20 jugadas más
probables (las del guion, cada palanca sola, extremos y empresas de respaldo).
Así sabemos de antemano si alguna da un resultado raro que un juez pueda provocar.

Día 7 (bloque 4): el script ya no arma el resultado a mano con comparar() y pesos.py.
Ahora le pide todo al motor real con una sola llamada, motor.api.calcular_estado(),
que devuelve el contrato JSON completo: exactamente lo que verá la pantalla y lo que
leerá la IA. Así, lo que probamos aquí es lo mismo que pasará en la demo.

Cómo se corre (desde la raíz del repositorio):
    python scripts/correr_combinaciones.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# Para poder importar config y motor aunque el script viva dentro de scripts/
RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from config import MIN_GRUPO, PALANCAS, RUTA_SUPUESTOS
from motor.api import calcular_estado

RUTA_CASOS = RAIZ / "scripts" / "combinaciones.yaml"
RUTA_SALIDA = RAIZ / "docs" / "resultados_combinaciones.md"


# ---------------------------------------------------------------------------
# 1. Leer los casos y los supuestos
# ---------------------------------------------------------------------------
def cargar_casos(ruta=RUTA_CASOS):
    """Lee combinaciones.yaml y revisa que cada caso esté bien escrito."""
    with open(ruta, encoding="utf-8") as f:
        casos = yaml.safe_load(f)["casos"]
    for caso in casos:
        validar_caso(caso)
    return casos


def validar_caso(caso):
    """Lanza un error claro si un caso tiene una palanca mal escrita o fuera de rango."""
    for campo in ("id", "empresa", "palancas"):
        if campo not in caso:
            raise ValueError(f"Al caso {caso.get('id', '?')} le falta el campo '{campo}'.")
    for palanca, valor in caso["palancas"].items():
        if palanca not in PALANCAS:
            raise ValueError(f"Caso {caso['id']}: la palanca '{palanca}' no existe.")
        minimo, maximo, _paso = PALANCAS[palanca]
        if not minimo <= valor <= maximo:
            raise ValueError(
                f"Caso {caso['id']}: {palanca}={valor} está fuera del rango {minimo} a {maximo}."
            )


def cargar_supuestos(ruta=RUTA_SUPUESTOS):
    """Lee el costo por baja y el costo mensual por ruta de supuestos.json."""
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# 2. Del DataFrame al perfil que pide calcular_estado
# ---------------------------------------------------------------------------
def fila_empresa(empresas, empresa_id):
    """Devuelve la fila de una empresa, tenga el DataFrame la empresa como índice o columna."""
    if "empresa" in empresas.columns:
        filas = empresas[empresas["empresa"] == empresa_id]
        if filas.empty:
            raise ValueError(f"No existe la empresa {empresa_id}.")
        return filas.iloc[0]
    return empresas.loc[empresa_id]

import math


def _o_none(valor):
    """Convierte NaN en None (el contrato usa None para 'sin dato')."""
    if valor is None:
        return None
    try:
        numero = float(valor)
    except (TypeError, ValueError):  # pd.NA o un texto no se pueden pasar a float
        return None
    return None if math.isnan(numero) else numero


def perfil_de_empresa(empresas, empresa_id):
    """Perfil con la misma forma que devuelve ui/selector.py: id, plantilla, palancas e indicadores.

    Los nombres de los indicadores son los del contrato (rot_temprana, ausentismo),
    no los de la base (bajas_menos3m, aus_inj_op).
    """
    fila = fila_empresa(empresas, empresa_id)
    return {
        "id": empresa_id,
        "plantilla_op": int(fila["plantilla_op"]),
        "banda": fila.get("banda"),
        "palancas": {p: float(fila[p]) for p in PALANCAS},
        "indicadores": {
            "rot_anual": float(fila["rot_anual"]),
            "rot_temprana": _o_none(fila.get("bajas_menos3m")),
            "ausentismo": _o_none(fila.get("aus_inj_op")),
        },
    }


def cambio_de(perfil, palancas_movidas):
    """El 'cambio' es la ÚLTIMA palanca movida: de su valor real al nuevo.

    En el YAML el orden importa: {aguinaldo_op: 20, prima_vac_op: 0.5} significa
    que primero se movió el aguinaldo y después la prima, así que el cambio es la prima.
    Sin palancas movidas (estado inicial) no hay cambio: None.
    """
    if not palancas_movidas:
        return None
    palanca, valor = list(palancas_movidas.items())[-1]
    return {"palanca": palanca, "de": perfil["palancas"][palanca], "a": valor}


def estado_de_caso(empresas, caso, supuestos):
    """Contrato JSON completo de un caso, tal cual lo entrega el motor real.

    También le sirve a Julian para generar los estados con los que prueba el prompt.
    """
    perfil = perfil_de_empresa(empresas, caso["empresa"])
    movidas = dict(caso["palancas"])
    return calcular_estado(
        empresas,
        perfil,
        movidas,
        cambio_de(perfil, movidas),
        supuestos,
        solo_tamano=bool(caso.get("solo_tamano", False)),
    )


# ---------------------------------------------------------------------------
# 3. Leer el contrato
# ---------------------------------------------------------------------------
def rotacion(bloque):
    """Rotación anual (mediana) de 'grupo' o 'resto' del contrato; None si no hay indicadores."""
    indicadores = bloque.get("indicadores") or {}
    return indicadores.get("rot_anual")


def fila_de_estado(caso, estado):
    """Resume un contrato en la fila de la tabla (solo lo que necesitamos revisar)."""
    salida = {
        "id": caso["id"],
        "tipo": caso.get("tipo", ""),
        "descripcion": caso.get("descripcion", ""),
        "empresa": caso["empresa"],
        "palancas": caso["palancas"],
        "n_grupo": estado["grupo"]["n"],
        "n_resto": estado["resto"]["n"],
        "rot_empresa": estado["empresa"]["indicadores"]["rot_anual"],
        "rot_grupo": rotacion(estado["grupo"]),
        "rot_resto": rotacion(estado["resto"]),
        "senal": estado["senal"]["etiqueta"],
        "p": estado["senal"].get("p"),
        "completado": bool(estado["grupo"]["completado"]),
        "costo_medida": estado["pesos"]["costo_medida_anual"],
        "costo_brecha": estado["pesos"]["costo_brecha_anual"],
    }
    salida["alertas"] = alertas(salida)
    salida["revision_guion"] = revisar_esperado(salida, caso.get("esperado"))
    return salida


def correr_caso(empresas, caso, supuestos):
    """Llama al motor real para un caso y devuelve su fila de resultados."""
    return fila_de_estado(caso, estado_de_caso(empresas, caso, supuestos))


def alertas(fila):
    """Las tres alertas que pide la guía: grupo vacío, resto chico y grupo que rota más."""
    lista = []
    if fila["n_grupo"] == 0:
        lista.append("grupo vacío")
    if fila["n_resto"] < MIN_GRUPO:
        lista.append(f"resto con menos de {MIN_GRUPO}")
    if (
        fila["rot_grupo"] is not None
        and fila["rot_resto"] is not None
        and fila["rot_grupo"] > fila["rot_resto"]
    ):
        lista.append("el grupo rota más que el resto")
    return lista


def revisar_esperado(fila, esperado):
    """Si el caso trae cifras esperadas (pasos del guion), dice si el motor las reproduce."""
    if not esperado:
        return ""
    fallas = []
    if fila["n_grupo"] != esperado["n_grupo"]:
        fallas.append(f"n grupo {fila['n_grupo']} ≠ {esperado['n_grupo']}")
    for clave in ("rot_grupo", "rot_resto"):
        valor = fila[clave]
        if valor is None or round(valor, 2) != esperado[clave]:
            fallas.append(f"{clave} {valor} ≠ {esperado[clave]}")
    return "coincide" if not fallas else "NO coincide: " + "; ".join(fallas)


# ---------------------------------------------------------------------------
# 4. Formato y archivo de salida
# ---------------------------------------------------------------------------
def pct(valor):
    return "—" if valor is None else f"{valor:.0%}"


def pesos(valor):
    """6341580 -> $6.3 M ; 650000 -> $650 mil ; negativos con signo."""
    signo = "−" if valor < 0 else ""
    valor = abs(valor)
    if valor >= 1_000_000:
        return f"{signo}${valor / 1_000_000:.1f} M"
    if valor >= 1_000:
        return f"{signo}${valor / 1_000:.0f} mil"
    return f"{signo}${valor:.0f}"


def texto_palancas(palancas):
    return ", ".join(f"{k}={v}" for k, v in palancas.items())


def a_markdown(filas, supuestos):
    con_alerta = [f for f in filas if f["alertas"]]
    guion = [f for f in filas if f["revision_guion"]]
    # Fecha local con zona horaria explícita (la regla DTZ de ruff no acepta date.today())
    hoy = datetime.now(timezone.utc).astimezone().date().isoformat()
    lineas = [
        "# Resultados de las 20 combinaciones",
        "",
        (
            f"Generado por scripts/correr_combinaciones.py el {hoy} con el motor real "
            f"(motor.api.calcular_estado). Costo por baja: ${supuestos['costo_por_baja']:,}; "
            f"costo mensual por ruta: ${supuestos['costo_ruta_mensual']:,}."
        ),
        "",
        (
            f"**Resumen:** {len(filas)} casos corridos, {len(con_alerta)} con alerta, "
            f"{sum(f['completado'] for f in filas)} con grupo completado. "
            "Las anomalías se explican en docs/anomalias.md."
        ),
        "",
        "## Tabla",
        "",
        (
            "| Caso | Empresa | Palancas movidas | n grupo | n resto | Rot. empresa "
            "| Rot. grupo | Rot. resto | Señal (p) | Completado | Costo medida "
            "| Costo brecha | Alertas |"
        ),
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for f in filas:
        p = "" if f["p"] is None else f" ({f['p']:.3f})"
        lineas.append(
            f"| {f['id']} | {f['empresa']} | {texto_palancas(f['palancas'])} "
            f"| {f['n_grupo']} | {f['n_resto']} | {pct(f['rot_empresa'])} "
            f"| {pct(f['rot_grupo'])} | {pct(f['rot_resto'])} | {f['senal']}{p} "
            f"| {'sí' if f['completado'] else 'no'} | {pesos(f['costo_medida'])} "
            f"| {pesos(f['costo_brecha'])} | {'; '.join(f['alertas']) or '—'} |"
        )

    lineas += ["", "## Revisión de los pasos del guion", ""]
    for f in guion:
        lineas.append(f"- **{f['id']}** ({f['descripcion']}): {f['revision_guion']}")

    lineas += ["", "## Casos con alerta", ""]
    if not con_alerta:
        lineas.append("Ninguno.")
    for f in con_alerta:
        lineas.append(
            f"- **{f['id']}** · {f['descripcion']}: {', '.join(f['alertas'])} "
            f"(grupo {pct(f['rot_grupo'])} contra resto {pct(f['rot_resto'])}, "
            f"n = {f['n_grupo']} vs {f['n_resto']})."
        )
    return "\n".join(lineas) + "\n"


def correr(empresas, casos, supuestos):
    """Corre todos los casos y devuelve la lista de filas (útil para pruebas)."""
    return [correr_caso(empresas, caso, supuestos) for caso in casos]


def main(empresas=None):
    if empresas is None:
        from motor.datos import cargar

        empresas = cargar()
    casos = cargar_casos()
    supuestos = cargar_supuestos()
    filas = correr(empresas, casos, supuestos)
    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    RUTA_SALIDA.write_text(a_markdown(filas, supuestos), encoding="utf-8")
    print(f"Listo: {len(filas)} casos -> {RUTA_SALIDA}")
    print(f"Con alerta: {sum(bool(f['alertas']) for f in filas)}")
    for f in filas:
        if f["revision_guion"] and f["revision_guion"] != "coincide":
            print(f"  ¡Ojo! {f['id']}: {f['revision_guion']}")


if __name__ == "__main__":
    main()