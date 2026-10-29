"""MiniOS: simulador FIFO y Round Robin, solo con la biblioteca estándar."""

import argparse
from pathlib import Path

from controllers.simulation_controller import run_simulation


def read_parameters(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archivo", default=str(Path(__file__).with_name("procesos.csv")),
                        help="CSV de entrada (por defecto, procesos.csv junto a minios.py)")
    parser.add_argument("--politica", choices=("fifo", "rr"), default="rr",
                        help="política de planificación (por defecto rr)")
    parser.add_argument("--quantum", default="3", help="entero positivo para rr; se ignora con fifo")
    parser.add_argument("--salida", "--output", default=".", help="directorio de los archivos generados")
    parser.add_argument("--comparar", action="store_true", help="muestra FIFO y RR lado a lado")
    args = parser.parse_args(argv)
    if args.politica == "rr" or args.comparar:
        try:
            args.quantum = int(args.quantum)
        except ValueError:
            parser.error("el quantum debe ser un número entero mayor que cero para Round Robin")
        if args.quantum <= 0:
            parser.error("el quantum debe ser un número entero mayor que cero para Round Robin")
    else:
        args.quantum = None
    return args


def main(argv=None):
    args = read_parameters(argv)
    return run_simulation(args.archivo, args.politica, args.quantum, args.salida, args.comparar)


if __name__ == "__main__":
    raise SystemExit(main())
