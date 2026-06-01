import json
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

LICENCIAS_FILE = os.path.join(os.path.dirname(__file__), "licencias.json")


def _cargar_licencias() -> dict:
    if not os.path.exists(LICENCIAS_FILE):
        return {}
    with open(LICENCIAS_FILE, encoding="utf-8") as f:
        return json.load(f)


@app.route("/api/validar", methods=["POST"])
def validar():
    data = request.get_json(silent=True) or {}
    clave = data.get("clave", "").strip().upper()
    machine_id = data.get("machine_id", "")

    if not clave:
        return jsonify({"valida": False, "mensaje": "Clave requerida"}), 400

    licencias = _cargar_licencias()

    if clave not in licencias:
        return jsonify({"valida": False, "mensaje": "Clave no encontrada"})

    licencia = licencias[clave]

    if not licencia.get("activa", True):
        return jsonify({"valida": False, "mensaje": "Licencia desactivada"})

    return jsonify({"valida": True, "mensaje": "OK"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
