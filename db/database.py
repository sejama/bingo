import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from models.carton import Carton


if getattr(sys, "frozen", False):
    # Ejecutable empaquetado: guardar DB en AppData para que sea escribible
    _app_data = Path(os.environ.get("APPDATA", Path.home())) / "BingoEscolar"
    _app_data.mkdir(parents=True, exist_ok=True)
    DB_PATH = _app_data / "bingo.sqlite3"
else:
    DB_PATH = Path(__file__).resolve().parent / "bingo.sqlite3"


def get_connection():
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	return conn


def init_db():
	with get_connection() as conn:
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS partidas (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				fecha_creacion TEXT NOT NULL,
				cantidad_cartones INTEGER NOT NULL
			)
			"""
		)

		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS cartones (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				partida_id INTEGER NOT NULL,
				carton_numero INTEGER NOT NULL,
				numeros_json TEXT NOT NULL,
				hash_unico TEXT,
				FOREIGN KEY (partida_id) REFERENCES partidas(id)
			)
			"""
		)

		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS sorteos (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				partida_id INTEGER NOT NULL,
				numero_sorteo INTEGER NOT NULL,
				fecha_inicio TEXT NOT NULL,
				fecha_fin TEXT,
				UNIQUE (partida_id, numero_sorteo),
				FOREIGN KEY (partida_id) REFERENCES partidas(id)
			)
			"""
		)

		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS sorteo_ganadores (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				sorteo_id INTEGER NOT NULL,
				carton_numero INTEGER NOT NULL,
				premio TEXT NOT NULL,
				numero_disparo INTEGER,
				UNIQUE (sorteo_id, carton_numero, premio),
				FOREIGN KEY (sorteo_id) REFERENCES sorteos(id)
			)
			"""
		)

		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS sorteo_numeros (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				sorteo_id INTEGER NOT NULL,
				orden_salida INTEGER NOT NULL,
				numero INTEGER NOT NULL,
				UNIQUE (sorteo_id, orden_salida),
				UNIQUE (sorteo_id, numero),
				FOREIGN KEY (sorteo_id) REFERENCES sorteos(id)
			)
			"""
		)


def guardar_partida(cartones):
	if not cartones:
		raise ValueError("No hay cartones para guardar")

	fecha = datetime.now().isoformat(timespec="seconds")

	with get_connection() as conn:
		cursor = conn.execute(
			"INSERT INTO partidas (fecha_creacion, cantidad_cartones) VALUES (?, ?)",
			(fecha, len(cartones)),
		)
		partida_id = cursor.lastrowid

		rows = []
		for carton in cartones:
			rows.append(
				(
					partida_id,
					carton.id,
					json.dumps(carton.numeros),
					str(carton.get_hash()),
				)
			)

		conn.executemany(
			"""
			INSERT INTO cartones (partida_id, carton_numero, numeros_json, hash_unico)
			VALUES (?, ?, ?, ?)
			""",
			rows,
		)

	return partida_id


def listar_partidas(limit=100):
	with get_connection() as conn:
		rows = conn.execute(
			"""
			SELECT id, fecha_creacion, cantidad_cartones
			FROM partidas
			ORDER BY id DESC
			LIMIT ?
			""",
			(limit,),
		).fetchall()

	return [dict(row) for row in rows]


def cargar_cartones_de_partida(partida_id):
	with get_connection() as conn:
		rows = conn.execute(
			"""
			SELECT carton_numero, numeros_json
			FROM cartones
			WHERE partida_id = ?
			ORDER BY carton_numero ASC
			""",
			(partida_id,),
		).fetchall()

	cartones = []
	for row in rows:
		numeros = json.loads(row["numeros_json"])
		cartones.append(Carton(row["carton_numero"], numeros=numeros))

	return cartones


def obtener_proximo_numero_sorteo(partida_id):
	with get_connection() as conn:
		row = conn.execute(
			"""
			SELECT COALESCE(MAX(numero_sorteo), 0) + 1 AS proximo
			FROM sorteos
			WHERE partida_id = ?
			""",
			(partida_id,),
		).fetchone()

	return int(row["proximo"])


def crear_sorteo(partida_id, numero_sorteo):
	fecha_inicio = datetime.now().isoformat(timespec="seconds")

	with get_connection() as conn:
		cursor = conn.execute(
			"""
			INSERT INTO sorteos (partida_id, numero_sorteo, fecha_inicio)
			VALUES (?, ?, ?)
			""",
			(partida_id, numero_sorteo, fecha_inicio),
		)

	return cursor.lastrowid


def cerrar_sorteo(sorteo_id):
	fecha_fin = datetime.now().isoformat(timespec="seconds")

	with get_connection() as conn:
		conn.execute(
			"""
			UPDATE sorteos
			SET fecha_fin = ?
			WHERE id = ?
			""",
			(fecha_fin, sorteo_id),
		)


def guardar_ganadores_sorteo(sorteo_id, ganadores, numero_disparo=None):
	if not ganadores:
		return

	rows = [(sorteo_id, carton_numero, premio, numero_disparo) for carton_numero, premio in ganadores]

	with get_connection() as conn:
		conn.executemany(
			"""
			INSERT OR IGNORE INTO sorteo_ganadores (sorteo_id, carton_numero, premio, numero_disparo)
			VALUES (?, ?, ?, ?)
			""",
			rows,
		)


def guardar_numero_sorteo(sorteo_id, numero, orden_salida):
	with get_connection() as conn:
		conn.execute(
			"""
			INSERT OR IGNORE INTO sorteo_numeros (sorteo_id, orden_salida, numero)
			VALUES (?, ?, ?)
			""",
			(sorteo_id, orden_salida, numero),
		)


def obtener_historial_sorteos(partida_id, limit=50):
	with get_connection() as conn:
		sorteos = conn.execute(
			"""
			SELECT id, numero_sorteo, fecha_inicio, fecha_fin
			FROM sorteos
			WHERE partida_id = ?
			ORDER BY numero_sorteo DESC
			LIMIT ?
			""",
			(partida_id, limit),
		).fetchall()

		historial = []
		for sorteo in sorteos:
			numeros_rows = conn.execute(
				"""
				SELECT numero
				FROM sorteo_numeros
				WHERE sorteo_id = ?
				ORDER BY orden_salida ASC
				""",
				(sorteo["id"],),
			).fetchall()

			ganadores_rows = conn.execute(
				"""
				SELECT carton_numero, premio
				FROM sorteo_ganadores
				WHERE sorteo_id = ?
				ORDER BY carton_numero ASC
				""",
				(sorteo["id"],),
			).fetchall()

			historial.append(
				{
					"id": sorteo["id"],
					"numero_sorteo": sorteo["numero_sorteo"],
					"fecha_inicio": sorteo["fecha_inicio"],
					"fecha_fin": sorteo["fecha_fin"],
					"numeros": [row["numero"] for row in numeros_rows],
					"ganadores": [(row["carton_numero"], row["premio"]) for row in ganadores_rows],
				}
			)

	return historial
