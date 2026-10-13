"""Cifras de negocio calculadas en código, que la IA puede usar. Dueño: Julian.

Una sola lista, que usan dos lugares:
- ia/prompts.py se la manda a la IA ya calculada, con qué es y cuándo usarla.
- ia/validador.py la agrega a las cifras permitidas.
Si una métrica no está aquí, la IA no puede escribirla: el validador la rechaza.

Reglas para agregar una métrica nueva:
- Sale solo de cifras del contrato (no de la base ni de supuestos nuevos).
- Nunca divide el costo de la medida entre la diferencia en pesos: eso insinúa
  un retorno, y el documento del proyecto lo prohíbe.
- Si en un estado no tiene sentido, no se incluye (mejor ausente que engañosa).
"""


def _dato(estado, *ruta):
    """Busca un valor siguiendo la ruta de llaves; None si falta alguna."""
    for clave in ruta:
        if not isinstance(estado, dict):
            return None
        estado = estado.get(clave)
    return estado


def cifras_derivadas(estado):
    """{nombre: {"valor": número, "que_es": texto}} con las métricas que aplican a este estado."""
    plantilla = _dato(estado, "empresa", "plantilla_op")
    salario = _dato(estado, "empresa", "palancas", "sal_dia_ini")
    rot_empresa = _dato(estado, "empresa", "indicadores", "rot_anual")
    rot_temprana = _dato(estado, "empresa", "indicadores", "rot_temprana")
    rot_grupo = _dato(estado, "grupo", "indicadores", "rot_anual")
    n_grupo = _dato(estado, "grupo", "n")
    n_resto = _dato(estado, "resto", "n")
    completado = _dato(estado, "grupo", "completado")
    medida = _dato(estado, "pesos", "costo_medida_anual")
    hay_cambio = bool(estado.get("cambio"))

    derivadas = {}

    # 1. El tamaño del problema en gente: 52% es abstracto, 742 personas es operativo.
    if plantilla and rot_empresa is not None:
        personas = plantilla * rot_empresa
        derivadas["personas_que_pierde_al_año"] = {
            "valor": round(personas),
            "que_es": "cuántas personas pierde hoy su empresa al año",
        }
        # 3. La rotación más cara: se van antes de ser productivas.
        if rot_temprana is not None:
            derivadas["personas_que_se_van_antes_de_3_meses"] = {
                "valor": round(personas * rot_temprana),
                "que_es": "de esas personas, cuántas se van antes de cumplir 3 meses",
            }

    # 4. Qué tan común es la medida en el mercado. No aplica sin palancas movidas
    #    (daría "39 de 39") ni con grupo completado (ya no es una proporción real).
    if hay_cambio and n_grupo and n_resto is not None and not completado:
        comparables = n_grupo + n_resto
        derivadas["empresas_comparables"] = {
            "valor": comparables,
            "que_es": "cuántas empresas se compararon en total (las que ya lo hacen más las demás)",
        }
        derivadas["porcentaje_que_ya_lo_hace"] = {
            "valor": round(100 * n_grupo / comparables),
            "que_es": "qué porcentaje de las empresas comparables ya aplica todo lo que movió el usuario",
        }

    # 5. El costo en el idioma de finanzas. "Base" porque usa el salario inicial,
    #    igual que el costo de la medida.
    if hay_cambio and medida and salario and plantilla:
        derivadas["porcentaje_de_la_nomina_base"] = {
            "valor": round(100 * medida / (salario * 365 * plantilla), 1),
            "que_es": "cuánto suma la medida a la nómina operativa base al año, en porcentaje",
        }

    # 6. Lo que está en juego, en personas. Sale de cifras observadas, no del costo
    #    por baja: si el juez cambia el supuesto, los pesos cambian y esto no.
    if plantilla and rot_empresa is not None and rot_grupo is not None and rot_empresa > rot_grupo:
        derivadas["personas_de_diferencia_al_año"] = {
            "valor": round(plantilla * (rot_empresa - rot_grupo)),
            "que_es": "con su plantilla, a cuántas personas al año equivale la diferencia frente a esas empresas",
        }

    return derivadas
