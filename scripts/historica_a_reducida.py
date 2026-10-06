"""Reconstruye BASE_REDUCIDA_v2 a partir de BASE_HISTORICA.

Uso:
    python scripts/historica_a_reducida.py
    python scripts/historica_a_reducida.py --entrada data/raw/BASE_HISTORICA.xlsx \
        --salida data/processed/reducida_reconstruida.xlsx --comparar data/raw/BASE_REDUCIDA_v2.xlsx

Las columnas de la histórica se localizan por el TEXTO del encabezado (pregunta +
sub-etiqueta), nunca por posición: las hojas tienen 1142, 1158 y 1169 columnas.
Cada variable debe coincidir con exactamente una columna por hoja; si no, el script
se detiene (así se detecta un cambio de cuestionario).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HOJAS = ["JUL-AGO_2024", "SEP-OCT_2024", "NOV-DIC_2024", "ENE-FEB_2025",
         "MAR-ABR_2025", "MAY-JUN_2025", "JUL-AGO_2025"]

# ---------------------------------------------------------------------------
# Tabla de variables: nombre v2 -> (regex de la pregunta, regex de la sub-etiqueta)
# ---------------------------------------------------------------------------
SPEC: dict[str, tuple[str, str]] = {
    "plantilla_op": (r"^Número de Empleados Actual de Personal Operativo", r".*"),
    "plantilla_adm": (r"^Número de Empleados Personal Administrativo", r".*"),
    "sindicato": (r"^¿Su compañía cuenta con alguna Confederación Sindical", r"^Response$"),
    "traslado_op": (r"se trasladan desde otros Estados", r"^Personal Operativo - Porcentaje$"),
    "rot_vol_op": (r"^¿Cuál es el promedio de rotación mensual", r"^Personal Operativo - Rotación Voluntaria$"),
    "rot_inv_op": (r"^¿Cuál es el promedio de rotación mensual", r"^Personal Operativo - Rotación Involuntaria$"),
    "aus_inj_op": (r"^Por favor, capture el PROMEDIO MENSUAL DE AUSENTISMO", r"^Operativos - Promedio de Ausentismo Injustificado$"),
    "dias_contratar_op": (r"¿Cuántos días hábiles", r"^Operativos"),
    "bajas_op": (r"^Del total de bajas bimestral", r"^Bajas de Personal Operativo$"),
    "contrat_total": (r"^Por favor, capture el TOTAL DE CONTRATACIONES", r".*"),
    "contrat_reemplazo": (r"^De la contrataciones de la pregunta anterior", r"^Contrataciones para cubrir"),
    "faltas_inj_op": (r"^FALTAS DE PERSONAL OPERATIVO", r"^Injustificado - Personal Operativo$"),
    "inc_sal_op": (r"^Por favor, comparta el porcentaje de incrementos de SALARIOS Y BENEFICIOS", r"en SALARIO - Personal Operativo$"),
    "vales_op": (r"^Por favor, especifique el porcentaje de VALES DE DESPENSA", r"^Vales de Despensa - Personal Operativo"),
    "fondo_op": (r"^Por favor, especifique el porcentaje de VALES DE DESPENSA", r"^Fondo de Ahorro - Personal Operativo"),
    "bono_asist": (r"^Por favor, especifique el porcentaje de BONO DE ASISTENCIA", r"^Bono de Asistencia"),
    "transporte": (r"^¿Otorga Servicio de Transporte de Personal", r"^Response$"),
    "rutas": (r"^Transporte - ¿Cuántas rutas de transporte", r"Cantidad de rutas"),
    "costo_transp": (r"^Transporte - ¿Cuál es costo promedio mensual", r".*"),
    "escolar_op": (r"^Por favor, seleccione algún o algunos otros beneficios que su perso", r"^Permisos para asistir a eventos escolares - PersonalOperativo$"),
    "bono_perm": (r"^¿Otorga algún bono de permanencia", r"^Response$"),
    "sal_dia_ini": (r"^Por favor, capture el Salario Diario Inicial", r".*"),
    "sal_dia_ib": (r"^Por favor, capture el Salario Diario Intermedio - Bajo", r".*"),
    "sal_dia_ia": (r"^Por favor, capture el Salario Diario Intermedio - Alto", r".*"),
    "sal_dia_max": (r"^Por favor, capture el Salario Diario Máximo", r".*"),
    "aguinaldo_op": (r"^Por favor, especifique los días de AGUINALDO", r"^PersonalOPERATIVO - 1° Año$"),
    "prima_vac_op": (r"^Por favor, especifique el porcentaje de PRIMA VACACIONAL", r"^Personal Operativo - % Prima Vacacional$"),
    "comedor": (r"^¿Otorga el servicio de comedor", r"^Response$"),
    "comedor_empresa": (r"^Comedor - ¿Cuál es costo promedio por platillo", r"PAGA LA EMPRESA"),
    "jornada_12h": (r"^¿Su compañía maneja jornadas de 12 horas", r"^Response$"),
    "rota_turno": (r"^¿Su personal operativo tiene la opción de Rotar", r"^Response$"),
}

MOTIVOS = {
    "m_sueldo": "Otro empleo - mejor sueldo", "m_prest": "Otro empleo - mejores prestaciones",
    "m_ruta": "Otro empleo - mejor ruta de transporte", "m_cerca": "Otro empleo - más cerca de su casa",
    "m_horario": "Otro empleo - mejor horario", "m_horcomp": "Horario complicado",
    "m_companeros": "Problemas con compañeros", "m_jefe": "Problemas con jefe supervisor",
    "m_rendimiento": "Bajo rendimiento", "m_fin_contrato": "Fin de contrato",
    "m_residencia": "Cambio de residencia", "m_familia": "Conflictos con pareja - familia",
    "m_enfermedad": "Enfermedad general", "m_estudios": "Estudios - Impedimento para seguir estudiando",
    "m_negocio": "Independizarse - Poner un negocio propio", "m_inseguridad": "Inseguridad en la zona",
    "m_cuidados": "No tenía quien cuidara hijos / familiares", "m_personales": "Motivos personales sin especificar",
}
for k, v in MOTIVOS.items():
    SPEC[k] = (r"^Por favor, clasifique los siguientes motivos de baja", "^" + re.escape(v) + "$")

BAJAS = {"bajas_renuncia": "Renuncia Voluntaria", "bajas_abandono": "Abandono de Trabajo",
         "bajas_faltas": "Acumulación de Faltas", "bajas_rescision": "Rescisión de Contrato"}
for k, v in BAJAS.items():
    SPEC[k] = (r"^Del total de bajas del bimestre, .*Desglose el número de bajas", "^" + v + "$")

ANTIG = {"bajas_0_1m": "0 a 1 Mes", "bajas_1_3m": "1 a 3 Meses", "bajas_3_12m": "3 a 12 Meses",
         "bajas_1_3a": "1 a 3 Años", "bajas_mas3a": "Más de 3 Años"}
for k, v in ANTIG.items():
    SPEC[k] = (r"^¿Qué antigüedad tenían los empleados que fueron bajas", "^" + v + " - Porcentaje$")

TIER_Q = r"^En caso de ser proveedor automotriz, seleccione su Nivel de Proveeduría"
ESCALA = {"nunca": 0, "muy poco común": 1, "poco común": 2, "común": 3, "casi siempre": 4, "siempre": 5}

ORDEN_COLUMNAS = [
    "empresa", "periodo", "orden_periodo", "plantilla_op", "plantilla_adm", "tier_grupo", "sindicato",
    "traslado_op", "rot_vol_op", "aus_inj_op", "aus_inj_cens", "dias_contratar_op", "rot_inv_op",
    "rot_inv_cens", "bajas_op", "tasa_bajas_op_bim", "contrat_total", "contrat_reemplazo", "faltas_inj_op",
    "tasa_faltas_inj_op_bim", "inc_sal_op", "vales_op", "fondo_op", "bono_asist", "bono_asist_cens",
    "transporte", "rutas", "rutas_cens", "rutas_x100", "costo_transp", "escolar_op", "bono_perm",
    "sal_dia_ini", "sal_dia_ib", "sal_dia_ia", "sal_dia_max", "aguinaldo_op", "prima_vac_op", "comedor",
    "comedor_empresa", "jornada_12h", "rota_turno", "transp_uso", *MOTIVOS, *BAJAS,
    "bajas_0_1m", "bajas_1_3m", "bajas_menos3m", "bajas_3_12m", "bajas_1_3a", "bajas_mas3a",
]


# ---------------------------------------------------------------------------
# Lectura y localización de columnas
# ---------------------------------------------------------------------------
def etiquetas(hoja: pd.DataFrame) -> list[tuple[int, str, str]]:
    """(posición, pregunta, sub-etiqueta). Fila 0 = pregunta (las continuaciones dicen
    'Unnamed: N' y heredan la pregunta anterior); fila 1 = sub-etiqueta."""
    out, ultima = [], ""
    for i in range(hoja.shape[1]):
        q, s = hoja.iat[0, i], hoja.iat[1, i]
        q = "" if pd.isna(q) else str(q).strip()
        s = "" if pd.isna(s) else str(s).strip()
        if q and not q.startswith("Unnamed:"):
            ultima = q
        out.append((i, ultima, s))
    return out


def buscar(et, q, s) -> list[int]:
    return [i for i, qq, ss in et if qq and re.search(q, qq) and re.search(s, ss)]


def columna(hoja_nombre, et, var, q, s) -> int:
    m = buscar(et, q, s)
    if len(m) != 1:
        sys.exit(f"[{hoja_nombre}] '{var}' coincide con {len(m)} columnas (se esperaba 1): {m}")
    return m[0]


def vacio(v) -> bool:
    return v is None or (isinstance(v, float) and np.isnan(v)) or str(v).strip() in ("", "-", "nan")


def num(v):
    if vacio(v):
        return np.nan
    try:
        return float(str(v).replace(",", "").strip())
    except ValueError:
        return np.nan


def txt(v):
    return None if vacio(v) else str(v).strip()


# ---------------------------------------------------------------------------
# Reglas por variable
# ---------------------------------------------------------------------------
def tier_grupo(vals: dict[str, object]) -> str:
    marcadas = {t for t in ("Tier 1", "Tier 2", "Tier 3") if not vacio(vals.get(t))}
    if len(marcadas) == 0:
        return "Sin Tier"
    if len(marcadas) == 1:
        return "Solo " + next(iter(marcadas))
    return "Mixto"


def procesar_fila(r: dict) -> dict:
    o: dict = {}
    for v in ("plantilla_op", "plantilla_adm"):
        o[v] = num(r[v])
    o["sindicato"] = txt(r["sindicato"])
    # proporciones con "Desconocido" -> vacío
    o["traslado_op"] = num(r["traslado_op"])

    # rotación voluntaria: "más del 15%" sin bandera -> vacío (decisión v2)
    o["rot_vol_op"] = num(r["rot_vol_op"])
    # ausentismo injustificado: "más del 15%" -> 0.15 + bandera
    t = txt(r["aus_inj_op"])
    o["aus_inj_cens"] = 1 if t and t.lower().startswith("más del") else 0
    o["aus_inj_op"] = 0.15 if o["aus_inj_cens"] else num(r["aus_inj_op"])
    t = txt(r["rot_inv_op"])
    o["rot_inv_cens"] = 1 if t and t.lower().startswith("más del") else 0
    o["rot_inv_op"] = 0.15 if o["rot_inv_cens"] else num(r["rot_inv_op"])

    d = num(r["dias_contratar_op"])
    o["dias_contratar_op"] = np.nan if d == 0 else d
    for v in ("bajas_op", "contrat_total", "contrat_reemplazo", "faltas_inj_op"):
        o[v] = num(r[v])
    o["inc_sal_op"] = num(r["inc_sal_op"])          # "Más de 20%" -> vacío
    o["vales_op"] = num(r["vales_op"])
    o["fondo_op"] = num(r["fondo_op"])              # "Menos del 0.50%" -> vacío

    t = txt(r["bono_asist"])
    if t and t.lower().startswith("menos del"):
        o["bono_asist"], o["bono_asist_cens"] = 0.005, 1
    elif t and t.lower().startswith("más del"):
        o["bono_asist"], o["bono_asist_cens"] = 0.20, 1
    else:
        o["bono_asist"], o["bono_asist_cens"] = num(r["bono_asist"]), 0

    o["transporte"] = txt(r["transporte"])
    t = txt(r["rutas"])
    if t and t.lower().startswith("más de 40"):
        o["rutas"], o["rutas_cens"] = 41, 1
    else:
        o["rutas"], o["rutas_cens"] = num(r["rutas"]), 0
    if o["transporte"] == "No":
        o["rutas"] = 0
    o["costo_transp"] = num(r["costo_transp"])
    esc = txt(r["escolar_op"])
    o["escolar_op"] = None if esc in (None, "No aplica") else esc
    o["bono_perm"] = txt(r["bono_perm"])
    for v in ("sal_dia_ini", "sal_dia_ib", "sal_dia_ia", "sal_dia_max", "aguinaldo_op", "prima_vac_op"):
        o[v] = num(r[v])
    o["comedor"] = txt(r["comedor"])
    o["comedor_empresa"] = num(r["comedor_empresa"]) if o["comedor"] == "Sí" else np.nan
    o["jornada_12h"] = txt(r["jornada_12h"])
    rt = txt(r["rota_turno"])
    if rt is None or rt in ("No aplica", "Otro (especifique)"):
        o["rota_turno"] = None
    elif rt.startswith("Sí"):
        o["rota_turno"] = "Sí"
    else:
        o["rota_turno"] = "No"
    tu = num(r["transp_uso"])
    o["transp_uso"] = tu / 100 if o["transporte"] == "Sí" else np.nan

    for k in MOTIVOS:
        t = txt(r[k])
        o[k] = ESCALA.get(t.lower(), np.nan) if t else np.nan
    for k in BAJAS:
        o[k] = num(r[k])

    # antigüedad de bajas: si la empresa respondió al menos una categoría, las que quedaron
    # en blanco o como "NO APLICA" valen 0; si no respondió ninguna, todas quedan vacías.
    cats = list(ANTIG)
    brutos = {k: txt(r[k]) for k in cats}
    hay_dato = any(b is not None and b.upper() != "NO APLICA" for b in brutos.values())
    for k in cats:
        b = brutos[k]
        if b is not None and b.upper() != "NO APLICA":
            o[k] = num(b)
        else:
            o[k] = 0.0 if hay_dato else np.nan
    return o


def formulas(df: pd.DataFrame) -> pd.DataFrame:
    p = df["plantilla_op"].replace(0, np.nan)
    df["tasa_bajas_op_bim"] = df["bajas_op"] / p
    df["tasa_faltas_inj_op_bim"] = df["faltas_inj_op"] / p
    df["rutas_x100"] = df["rutas"] / p * 100
    df["bajas_menos3m"] = df["bajas_0_1m"] + df["bajas_1_3m"]
    return df


def construir(ruta_entrada: Path) -> pd.DataFrame:
    xl = pd.ExcelFile(ruta_entrada)
    filas = []
    for orden, nombre in enumerate(HOJAS, start=1):
        if nombre not in xl.sheet_names:
            sys.exit(f"Falta la hoja {nombre} en {ruta_entrada}")
        hoja = xl.parse(nombre, header=None, dtype=object)
        et = etiquetas(hoja)
        pos = {var: columna(nombre, et, var, q, s) for var, (q, s) in SPEC.items()}
        # transp_uso: la pregunta "¿Cuántos colaboradores hacen uso efectivo…" se repite
        # para cada prestación; es la primera que aparece después de la de Transporte.
        cand = [i for i in buscar(et, r"^¿Cuántos colaboradores hacen uso efectivo", r".*") if i > pos["transporte"]]
        if not cand:
            sys.exit(f"[{nombre}] no se encontró 'transp_uso'")
        pos["transp_uso"] = min(cand)
        tiers = {s_.replace("Tier ", "Tier "): i for i, qq, s_ in et
                 if qq and re.search(TIER_Q, qq) and s_ in ("Tier 1", "Tier 2", "Tier 3")}
        if len(tiers) != 3:
            sys.exit(f"[{nombre}] no se hallaron las 3 casillas de Tier")
        i_emp = [i for i, qq, ss in et if qq == "Compañía"]
        if len(i_emp) != 1:
            sys.exit(f"[{nombre}] columna Compañía: {i_emp}")
        for fila in range(2, hoja.shape[0]):
            emp = hoja.iat[fila, i_emp[0]]
            if vacio(emp):
                continue  # filas finales sin nombre de empresa
            r = {var: hoja.iat[fila, i] for var, i in pos.items()}
            o = procesar_fila(r)
            o["tier_grupo"] = tier_grupo({t: hoja.iat[fila, i] for t, i in tiers.items()})
            o.update(empresa=str(emp).strip(), periodo=nombre, orden_periodo=orden)
            filas.append(o)
    df = formulas(pd.DataFrame(filas))
    return df[ORDEN_COLUMNAS]


# ---------------------------------------------------------------------------
# Comparación contra la v2 entregada
# ---------------------------------------------------------------------------
def comparar(df: pd.DataFrame, ruta_v2: Path) -> int:
    v2 = pd.read_excel(ruta_v2, sheet_name="BASE_REDUCIDA")
    a = df.set_index(["empresa", "periodo"]).sort_index()
    b = v2.set_index(["empresa", "periodo"]).sort_index()
    if list(a.index) != list(b.index):
        print("ÍNDICES DISTINTOS:", len(a), len(b))
        return 1
    malas = 0
    for c in v2.columns:
        if c in ("empresa", "periodo"):
            continue
        x, y = a[c], b[c]
        if not (pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y)):
            ok = (x.fillna("∅").astype(str) == y.fillna("∅").astype(str))
        else:
            ok = (np.isclose(x.astype(float), y.astype(float), rtol=1e-9, atol=1e-9, equal_nan=True))
        if not ok.all():
            malas += 1
            print(f"  ✗ {c}: {(~ok).sum()} celdas distintas, p. ej. {list(zip(x[~ok].head(3), y[~ok].head(3)))}")
    print("columnas distintas:", malas, "de", len(v2.columns) - 2)
    return malas


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", default="data/raw/BASE_HISTORICA.xlsx")
    ap.add_argument("--salida", default="data/processed/reducida_reconstruida.xlsx")
    ap.add_argument("--comparar", default=None, help="ruta de BASE_REDUCIDA_v2.xlsx para verificar")
    a = ap.parse_args()
    df = construir(Path(a.entrada))
    print("filas:", len(df), "| columnas:", df.shape[1])
    if a.comparar:
        sys.exit(1 if comparar(df, Path(a.comparar)) else 0)
    Path(a.salida).parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(a.salida, index=False, sheet_name="BASE_REDUCIDA")
    print("escrito:", a.salida)


if __name__ == "__main__":
    main()
