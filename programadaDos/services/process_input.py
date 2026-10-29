"""Lectura y validación completa del CSV antes de simular."""

import csv
from pathlib import Path

from models.process import Process


class InputError(ValueError):
    """Error comprensible en el archivo de entrada."""


def validate_processes(rows):
    processes, errors, identifiers = [], [], set()
    for number, row in rows:
        if len(row) != 3:
            errors.append(f"Fila {number}: se esperan 3 columnas (id,llegada,duracion).")
            continue
        identifier, arrival_text, duration_text = (value.strip() for value in row)
        valid = True
        if not identifier:
            errors.append(f"Fila {number}: el identificador está vacío.")
            valid = False
        elif identifier in identifiers:
            errors.append(f"Fila {number}: identificador duplicado '{identifier}'.")
            valid = False
        identifiers.add(identifier)
        values = []
        for name, value_text in (("llegada", arrival_text), ("duracion", duration_text)):
            try:
                value = int(value_text)
            except ValueError:
                errors.append(f"Fila {number}: {name} debe ser un entero; se recibió '{value_text}'.")
                values.append(None)
                valid = False
                continue
            values.append(value)
            if (name == "llegada" and value < 0) or (name == "duracion" and value <= 0):
                limit = "mayor o igual que cero" if name == "llegada" else "mayor que cero"
                errors.append(f"Fila {number}: {name} debe ser {limit}.")
                valid = False
        if valid:
            processes.append(Process(identifier, *values))
    if errors:
        raise InputError("\n".join(errors))
    if not processes:
        raise InputError("El archivo no contiene procesos.")
    return processes


def read_processes(path):
    """Acepta encabezados en español y los de la Tarea 1 en inglés."""
    try:
        with Path(path).open(encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file, strict=True)
            header = next(reader, None)
            if header is None:
                raise InputError("El archivo está vacío.")
            if [value.strip() for value in header] not in (
                ["id", "llegada", "duracion"], ["id", "arrival", "duration"]
            ):
                raise InputError("El encabezado debe ser id,llegada,duracion (o id,arrival,duration).")
            return validate_processes((reader.line_num, row) for row in reader)
    except FileNotFoundError as error:
        raise InputError(f"No existe el archivo '{path}'.") from error
    except (UnicodeError, csv.Error) as error:
        raise InputError(f"No se pudo interpretar el CSV UTF-8: {error}") from error
    except OSError as error:
        raise InputError(f"No se pudo leer '{path}': {error}") from error
