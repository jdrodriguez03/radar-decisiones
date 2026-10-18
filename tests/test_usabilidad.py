"""Revisa la tabla de fricciones de docs/usabilidad.md. Dueño: Juanes.

Para qué sirve: el "Listo cuando" del día 10 dice que cada fricción tiene dueño y que
la lista está ordenada de más grave a menos grave. Gaby (día 12) y Aleja corrigen en
ese orden, así que un renglón sin dueño o mal ordenado es trabajo que nadie hace.
Esta prueba lo revisa sola en el CI cada vez que alguien edita el documento.

Qué revisa de cada renglón entre <!-- fricciones:inicio --> y <!-- fricciones:fin -->:
- que tenga las 8 columnas;
- que la gravedad sea bloqueante, grave, moderada o leve;
- que el dueño sea Aleja, Gaby, Julian o Juanes;
- que "Qué pasó" no esté vacío;
- que los renglones vayan de más grave a menos grave.

Si la tabla todavía está vacía (antes de hacer la prueba con usuarios), la prueba se
SALTA en vez de fallar, para no poner el CI en rojo.

Cómo se corre (desde la raíz del repositorio):
    pytest tests/test_usabilidad.py -v
"""
import pytest

import config

RUTA = config.RAIZ / "docs" / "usabilidad.md"
GRAVEDADES = ["bloqueante", "grave", "moderada", "leve"]  # de más grave a menos grave
DUENOS = {"Aleja", "Gaby", "Julian", "Juanes"}
COLUMNAS = ["#", "Gravedad", "Tarea", "Dónde", "Qué pasó", "Quién", "Dueño", "Arreglo"]


def leer_fricciones(texto: str) -> list[dict]:
    """Devuelve un diccionario por renglón de la tabla de fricciones.

    Ejemplo de renglón en el .md:
    | 1 | bloqueante | T3 | ⚙ | No lo encontró en 2 min | P1, P2 | Juanes | Poner texto "Supuestos" |
    se convierte en:
    {"#": "1", "Gravedad": "bloqueante", ..., "Dueño": "Juanes", "Arreglo": "Poner texto..."}
    """
    inicio, fin = "<!-- fricciones:inicio -->", "<!-- fricciones:fin -->"
    assert inicio in texto and fin in texto, "No se encontraron las marcas de la tabla de fricciones"
    bloque = texto.split(inicio, 1)[1].split(fin, 1)[0]

    renglones = []
    for linea in bloque.strip().splitlines():
        linea = linea.strip()
        if not linea.startswith("|"):
            continue
        # "| a | b |" -> ["a", "b"]: se quitan los | de las orillas y se parte por los de en medio
        celdas = [c.strip() for c in linea.strip("|").split("|")]
        if celdas[0] == "#" or set(linea) <= set("|-: "):
            continue  # encabezado o línea separadora |---|---|
        renglones.append(dict(zip(COLUMNAS, celdas)) | {"_columnas": len(celdas), "_linea": linea})
    return renglones


@pytest.fixture(scope="module")
def fricciones():
    lista = leer_fricciones(RUTA.read_text(encoding="utf-8"))
    if not lista:
        pytest.skip("Todavía no hay fricciones anotadas en docs/usabilidad.md")
    return lista


def test_cada_renglon_tiene_las_columnas(fricciones):
    malos = [f["_linea"] for f in fricciones if f["_columnas"] != len(COLUMNAS)]
    assert not malos, f"Estos renglones no tienen {len(COLUMNAS)} columnas:\n" + "\n".join(malos)


def test_gravedad_valida(fricciones):
    malos = [f"#{f['#']}: '{f['Gravedad']}'" for f in fricciones if f["Gravedad"].lower() not in GRAVEDADES]
    assert not malos, f"Gravedad debe ser una de {GRAVEDADES}. Revisar: " + ", ".join(malos)


def test_cada_friccion_tiene_dueno(fricciones):
    malos = [f"#{f['#']}: '{f.get('Dueño', '')}'" for f in fricciones if f.get("Dueño") not in DUENOS]
    assert not malos, f"Dueño debe ser uno de {sorted(DUENOS)}. Revisar: " + ", ".join(malos)


def test_que_paso_no_esta_vacio(fricciones):
    malos = [f"#{f['#']}" for f in fricciones if not f.get("Qué pasó")]
    assert not malos, "Falta describir qué pasó en: " + ", ".join(malos)


def test_ordenadas_de_mas_grave_a_menos_grave(fricciones):
    # Cada gravedad se vuelve un número (bloqueante=0 ... leve=3); la lista debe ir de menor a mayor.
    # Los renglones con gravedad inválida se ignoran aquí: ya los reporta test_gravedad_valida.
    validas = [f["Gravedad"].lower() for f in fricciones if f["Gravedad"].lower() in GRAVEDADES]
    nivel = [GRAVEDADES.index(g) for g in validas]
    assert nivel == sorted(nivel), (
        "Las fricciones no están ordenadas de más grave a menos grave. Orden actual: "
        + ", ".join(validas)
    )