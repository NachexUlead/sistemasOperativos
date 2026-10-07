"""MiniOS: a non-preemptive FIFO CPU simulator using the standard library."""

import argparse
import sys

from controllers.simulation_controller import run_simulation


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", default="procesos.csv",
                        help="Input CSV (procesos.csv by default)")
    parser.add_argument("--output", default=".",
                        help="Directory for resultados.csv and eventos.txt")
    args = parser.parse_args(argv)
    return run_simulation(args.file, args.output)


if __name__ == "__main__":
    sys.exit(main())
