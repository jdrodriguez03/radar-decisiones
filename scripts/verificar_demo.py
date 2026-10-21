"""Comprueba los requisitos locales de la demo antes del ensayo."""

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import anthropic

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import config
from ia.cache import buscar, llave
from ia.cache import cargar as cargar_cache
from motor import api
from motor.datos import cargar as cargar_empresas
from scripts.generar_cache import armar_secuencias, cargar_casos, poner_llave_api

LIMITE_MOTOR_MS = 50
TIMEOUT_API_SEG = 5
TIMEOUT_APP_SEG = 30


def _imprimir(esta_bien, mensaje):
    color = "\033[32m" if esta_bien else "\033[31m"
    marca = "OK" if esta_bien else "ERROR"
    print(f"{color}[{marca}]\033[0m {mensaje}")


def _ejecutar_revision(nombre, revision):
    try:
        detalle = revision()
    except Exception as error:  # noqa: BLE001 - registra el fallo y continúa las otras revisiones
        _imprimir(False, f"{nombre}: {type(error).__name__}: {error}")
        return False
    _imprimir(True, f"{nombre}: {detalle}")
    return True


def _cargar_secuencias(empresas):
    supuestos = json.loads(config.RUTA_SUPUESTOS.read_text(encoding="utf-8"))
    return armar_secuencias(cargar_casos(), empresas, supuestos)


def _revisar_parquet():
    empresas = cargar_empresas()
    return f"{len(empresas)} filas; carga y columnas requeridas válidas"


def _revisar_cache():
    empresas = cargar_empresas()
    secuencias = _cargar_secuencias(empresas)
    cache = cargar_cache()
    vistas = set()
    faltantes = []

    for secuencia in secuencias:
        anterior = None
        for estado in secuencia:
            clave = llave(estado, anterior)
            if clave not in vistas:
                vistas.add(clave)
                if buscar(estado, anterior, cache=cache) is None:
                    faltantes.append(clave)
            anterior = estado

    if faltantes:
        muestra = ", ".join(faltantes[:3])
        raise RuntimeError(f"faltan {len(faltantes)} estados; por ejemplo: {muestra}")
    return f"{len(vistas)} estados de guion y respaldo encontrados y válidos"


def _revisar_api():
    if not poner_llave_api():
        raise RuntimeError(
            "falta ANTHROPIC_API_KEY en el entorno o en .streamlit/secrets.toml"
        )

    cliente = anthropic.Anthropic(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        max_retries=0,
        timeout=TIMEOUT_API_SEG,
    )
    try:
        cliente.models.list(limit=1)
    except anthropic.APIConnectionError as error:
        raise RuntimeError("no se pudo conectar con Anthropic o se agotó el tiempo") from error
    except anthropic.APIStatusError as error:
        raise RuntimeError(f"Anthropic respondió con HTTP {error.status_code}") from error
    return "Anthropic respondió a la consulta de modelos (sin generar texto)"


def _entradas_motor(empresas):
    secuencias = _cargar_secuencias(empresas)
    entradas = {}
    for secuencia in secuencias:
        for estado in secuencia:
            datos = (
                estado["empresa"],
                estado["palancas_movidas"],
                estado["cambio"],
                estado["pesos"]["supuestos"],
            )
            clave = json.dumps(datos, ensure_ascii=False, sort_keys=True, allow_nan=False)
            entradas.setdefault(clave, datos)
    return list(entradas.values())


def _revisar_motor():
    empresas = cargar_empresas()
    secuencias = _cargar_secuencias(empresas)
    estado_guion = secuencias[0][0]
    respuesta = api.calcular_estado(
        empresas,
        estado_guion["empresa"],
        estado_guion["palancas_movidas"],
        estado_guion["cambio"],
        estado_guion["pesos"]["supuestos"],
    )
    if respuesta["empresa"]["id"] != estado_guion["empresa"]["id"]:
        raise RuntimeError("la API del motor devolvió otra empresa")
    return f"motor.api.calcular_estado respondió para {respuesta['empresa']['id']}"


def _medir_motor():
    empresas = cargar_empresas()
    entradas = _entradas_motor(empresas)
    if not entradas:
        raise RuntimeError("no se encontraron estados de demo para medir")

    tiempos_ms = []
    with api._ESTADOS_CACHE_LOCK:
        api._ESTADOS_CACHE.clear()

    for perfil, palancas, cambio, supuestos in entradas:
        inicio = time.perf_counter()
        api.calcular_estado(empresas, perfil, palancas, cambio, supuestos)
        tiempos_ms.append((time.perf_counter() - inicio) * 1000)

    maximo_ms = max(tiempos_ms)
    if maximo_ms >= LIMITE_MOTOR_MS:
        raise RuntimeError(
            f"máximo {maximo_ms:.2f} ms en {len(tiempos_ms)} estados; "
            f"el límite es menos de {LIMITE_MOTOR_MS} ms"
        )
    return (
        f"máximo {maximo_ms:.2f} ms en {len(tiempos_ms)} estados únicos "
        f"(límite < {LIMITE_MOTOR_MS} ms)"
    )


def _puerto_local():
    with socket.socket() as servidor:
        servidor.bind(("127.0.0.1", 0))
        return servidor.getsockname()[1]


def _comprobar_arranque_app():
    from streamlit.testing.v1 import AppTest

    modo_demo_previo = os.environ.get("MODO_DEMO")
    os.environ["MODO_DEMO"] = "1"
    try:
        aplicacion = AppTest.from_file(
            str(RAIZ / "app.py"), default_timeout=TIMEOUT_APP_SEG
        ).run()
        if aplicacion.exception:
            error = aplicacion.exception[0].value
            raise RuntimeError(f"app.py lanzó {type(error).__name__}: {error}")
    finally:
        if modo_demo_previo is None:
            os.environ.pop("MODO_DEMO", None)
        else:
            os.environ["MODO_DEMO"] = modo_demo_previo

    puerto = _puerto_local()
    url = f"http://127.0.0.1:{puerto}/_stcore/health"
    entorno = os.environ.copy()
    entorno["MODO_DEMO"] = "1"
    entorno["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    comando = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(RAIZ / "app.py"),
        "--server.headless=true",
        "--server.address=127.0.0.1",
        f"--server.port={puerto}",
        "--browser.gatherUsageStats=false",
        "--logger.level=error",
    ]

    with tempfile.TemporaryFile() as salida:
        proceso = subprocess.Popen(
            comando,
            cwd=RAIZ,
            env=entorno,
            stdin=subprocess.DEVNULL,
            stdout=salida,
            stderr=subprocess.STDOUT,
        )
        try:
            limite = time.monotonic() + TIMEOUT_APP_SEG
            while time.monotonic() < limite:
                if proceso.poll() is not None:
                    salida.seek(0)
                    detalle = salida.read().decode("utf-8", errors="replace")[-1200:].strip()
                    raise RuntimeError(
                        f"Streamlit terminó con código {proceso.returncode}. {detalle}"
                    )
                try:
                    with urlopen(url, timeout=1) as respuesta:
                        if respuesta.status == 200:
                            return "app.py ejecutó sin errores y Streamlit respondió en localhost"
                except (OSError, URLError):
                    time.sleep(0.25)
            raise RuntimeError(f"Streamlit no respondió en {TIMEOUT_APP_SEG} segundos")
        finally:
            if proceso.poll() is None:
                proceso.terminate()
                try:
                    proceso.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proceso.kill()
                    proceso.wait(timeout=5)


def main():
    revisiones = (
        ("Parquet de empresas", _revisar_parquet),
        ("Caché de la demo", _revisar_cache),
        ("API de Anthropic", _revisar_api),
        ("Respuesta de la API del motor", _revisar_motor),
        ("Rendimiento del motor", _medir_motor),
        ("Arranque de la app", _comprobar_arranque_app),
    )
    resultados = [_ejecutar_revision(nombre, revision) for nombre, revision in revisiones]
    correctas = sum(resultados)
    print(f"\n{correctas}/{len(resultados)} revisiones correctas.")
    return 0 if all(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
