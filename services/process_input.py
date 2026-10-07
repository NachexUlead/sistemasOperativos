"""CSV loading and input validation."""

import csv
from pathlib import Path

from models.process import Process


class InputError(ValueError):
    """The process input file does not meet the required format."""


def validate_processes(rows):
    """Validate all rows and report input errors before simulation."""
    processes, errors, ids = [], [], set()
    for number, row in rows:
        if len(row) != 3:
            errors.append(f"Row {number}: expected 3 columns (id,arrival,duration).")
            continue
        identifier, arrival_text, duration_text = (value.strip() for value in row)
        valid = True
        if not identifier:
            errors.append(f"Row {number}: the identifier is empty.")
            valid = False
        elif identifier in ids:
            errors.append(f"Row {number}: duplicate identifier '{identifier}'.")
            valid = False
        ids.add(identifier)
        values = []
        for name, text in (("arrival", arrival_text), ("duration", duration_text)):
            try:
                value = int(text)
            except ValueError:
                errors.append(f"Row {number}: {name} must be an integer; received '{text}'.")
                valid = False
                values.append(None)
                continue
            values.append(value)
            if (name == "arrival" and value < 0) or (name == "duration" and value <= 0):
                limit = "greater than or equal to zero" if name == "arrival" else "greater than zero"
                errors.append(f"Row {number}: {name} must be {limit}.")
                valid = False
        if valid:
            processes.append(Process(identifier, *values))
    if errors:
        raise InputError("\n".join(errors))
    if not processes:
        raise InputError("The file contains no processes.")
    return processes


def read_processes(path):
    """Read a UTF-8 CSV with a required header, preserving row order."""
    try:
        with Path(path).open(encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file, strict=True)
            header = next(reader, None)
            if header is None:
                raise InputError("The file is empty.")
            if [value.strip() for value in header] not in (
                ["id", "arrival", "duration"], ["id", "llegada", "duracion"]
            ):
                raise InputError("The header must be: id,arrival,duration (or id,llegada,duracion).")
            rows = []
            for row in reader:
                rows.append((reader.line_num, row))
            return validate_processes(rows)
    except FileNotFoundError as error:
        raise InputError(f"File '{path}' does not exist.") from error
    except (UnicodeError, csv.Error) as error:
        raise InputError(f"Could not parse the UTF-8 CSV: {error}") from error
    except OSError as error:
        raise InputError(f"Could not read '{path}': {error}") from error


