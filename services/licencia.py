import hashlib
import json
import os
import platform
import sys
import uuid
from datetime import datetime
from pathlib import Path

import requests

# --- Configuración ---
URL_VALIDACION = "https://tu-servidor.com/validar.php"  # <-- cambiá esta URL
DIAS_GRACIA = 7
TIMEOUT_SEGUNDOS = 5
# ---------------------


def get_machine_id() -> str:
    raw = f"{uuid.getnode()}-{platform.node()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _get_cache_path() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(os.environ.get("APPDATA", Path.home())) / "BingoEscolar"
    else:
        base = Path(__file__).resolve().parent.parent / "db"
    base.mkdir(parents=True, exist_ok=True)
    return base / "licencia.json"


def _leer_cache() -> dict | None:
    try:
        with open(_get_cache_path()) as f:
            return json.load(f)
    except Exception:
        return None


def _guardar_cache(clave: str) -> None:
    data = {
        "clave": clave,
        "machine_id": get_machine_id(),
        "ultima_validacion": datetime.now().isoformat(),
    }
    with open(_get_cache_path(), "w") as f:
        json.dump(data, f)


def _validar_online(clave: str) -> tuple[bool, str]:
    resp = requests.post(
        URL_VALIDACION,
        json={"clave": clave.strip().upper(), "machine_id": get_machine_id()},
        timeout=TIMEOUT_SEGUNDOS,
    )
    data = resp.json()
    return bool(data.get("valida")), data.get("mensaje", "")


def verificar_inicio() -> tuple[bool, str, str | None]:
    """
    Verifica si el equipo tiene licencia válida al arrancar.

    Retorna (puede_arrancar, mensaje, clave_o_None).
    - puede_arrancar=True y clave: OK, la app puede iniciarse.
    - puede_arrancar=False y clave=None: necesita ingresar clave.
    """
    cache = _leer_cache()
    machine_id = get_machine_id()

    if cache and cache.get("machine_id") == machine_id:
        clave = cache["clave"]
        try:
            valida, msg = _validar_online(clave)
            if valida:
                _guardar_cache(clave)
                return True, "Licencia válida", clave
            else:
                return False, f"Licencia revocada: {msg}", None
        except Exception:
            # Sin internet: chequear período de gracia
            ultima = datetime.fromisoformat(cache["ultima_validacion"])
            dias_pasados = (datetime.now() - ultima).days
            if dias_pasados <= DIAS_GRACIA:
                restantes = DIAS_GRACIA - dias_pasados
                return True, f"Sin conexión. Días de gracia restantes: {restantes}", clave
            else:
                return False, "El período de gracia expiró. Conectate a internet para validar.", None

    return False, "Sin licencia registrada", None


def activar_clave(clave: str) -> tuple[bool, str]:
    """
    Intenta activar una clave nueva ingresada por el usuario.
    Requiere conexión a internet.

    Retorna (valida, mensaje).
    """
    try:
        valida, msg = _validar_online(clave)
        if valida:
            _guardar_cache(clave)
        return valida, msg or ("Licencia activada correctamente" if valida else "Clave inválida")
    except Exception:
        return False, "Sin conexión a internet. No se puede activar una clave nueva sin internet."
