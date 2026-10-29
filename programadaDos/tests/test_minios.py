"""Pruebas de aceptación del enunciado, invariantes y errores de la CLI."""

from copy import deepcopy
import csv
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

from models.process import Process
from services.metrics import calculate_metrics
from services.process_input import InputError, read_processes
from services.scheduler import simulate, simulate_fifo, simulate_round_robin


ROOT = Path(__file__).resolve().parents[1]


def results(processes):
    return [(p.start, p.finish, p.wait, p.turnaround, p.response, p.preemptions) for p in processes]


class SchedulingTests(unittest.TestCase):
    def test_pdf_section_10(self):
        result = simulate_round_robin(read_processes(ROOT / "casos/desempate_quantum.csv"), 2)
        self.assertEqual(results(result.processes), [
            (0, 10, 5, 10, 0, 2), (2, 9, 4, 7, 0, 1), (6, 12, 5, 9, 3, 1)])
        m = calculate_metrics(result)
        self.assertEqual((m["total_time"], m["context_switches"]), (12, 6))
        self.assertAlmostEqual(m["average_wait"], 14 / 3)
        self.assertAlmostEqual(m["average_turnaround"], 26 / 3)
        self.assertEqual(m["average_response"], 1)
        self.assertEqual(m["longest_wait_process"], "P1")

    def test_pdf_section_18_with_rule_9_2_7(self):
        result = simulate_round_robin(read_processes(ROOT / "procesos.csv"), 3)
        # P3 renueva su último quantum solo: la regla 9.2.7 exige una expropiación,
        # aunque la tabla de la sección 18 indica dos por error.
        self.assertEqual(results(result.processes), [
            (0, 11, 6, 11, 0, 1), (3, 6, 1, 4, 1, 0),
            (6, 18, 7, 15, 3, 1), (11, 13, 5, 7, 5, 0)])
        m = calculate_metrics(result)
        self.assertEqual([m[k] for k in ("total_time", "average_wait", "average_turnaround",
                                        "average_response", "context_switches", "cpu_utilization")],
                         [18, 4.75, 9.25, 2.25, 5, 100])
        self.assertIn("[16] P3 renueva quantum sin expropiación; cola vacía", result.events)

    def test_fifo_matches_first_assignment(self):
        result = simulate_fifo(read_processes(ROOT / "procesos.csv"))
        self.assertEqual(results(result.processes), [
            (0, 5, 0, 5, 0, 0), (5, 8, 3, 6, 3, 0),
            (8, 16, 5, 13, 5, 0), (16, 18, 10, 12, 10, 0)])
        self.assertEqual(result.context_switches, 3)

    def test_single_process_never_preempted(self):
        for q in (1, 3, 100):
            with self.subTest(quantum=q):
                result = simulate_round_robin([Process("Solo", 4, 8)], q)
                self.assertEqual(results(result.processes), [(4, 12, 0, 8, 0, 0)])
                self.assertEqual(result.context_switches, 0)
                self.assertAlmostEqual(calculate_metrics(result)["cpu_utilization"], 800 / 12)

    def test_simultaneous_arrivals_preserve_file_order(self):
        result = simulate_round_robin(read_processes(ROOT / "casos/llegadas_simultaneas.csv"), 1)
        self.assertEqual([p.start for p in result.processes], [0, 1, 2])
        self.assertEqual([p.finish for p in result.processes], [7, 5, 3])

    def test_unsorted_input_and_output_order(self):
        result = simulate_fifo(read_processes(ROOT / "casos/orden_no_cronologico.csv"))
        self.assertEqual([p.identifier for p in result.processes], ["Tardio", "Primero", "Segundo"])
        self.assertEqual([p.start for p in result.processes], [5, 0, 3])

    def test_idle_gap_still_counts_switch_between_distinct_processes(self):
        result = simulate_round_robin(read_processes(ROOT / "casos/cpu_ocioso.csv"), 3)
        self.assertEqual((result.total_time, result.busy_time, result.context_switches), (13, 5, 1))
        self.assertEqual(sum("CPU ocioso" in event for event in result.events), 8)
        self.assertAlmostEqual(calculate_metrics(result)["cpu_utilization"], 500 / 13)

    def test_completion_at_quantum_is_not_preemption(self):
        result = simulate_round_robin([Process("A", 0, 2), Process("B", 2, 1)], 2)
        self.assertEqual(results(result.processes), [(0, 2, 0, 2, 0, 0), (2, 3, 0, 1, 0, 0)])

    def test_new_arrival_precedes_preempted_process(self):
        result = simulate_round_robin([Process("A", 0, 4), Process("B", 2, 1)], 2)
        self.assertEqual([p.finish for p in result.processes], [5, 3])
        self.assertLess(result.events.index("[2] B llega al sistema y entra a la cola (Listo)"),
                        result.events.index("[2] A vuelve a la cola (Listo)"))

    def test_large_quantum_equals_fifo_on_many_workloads(self):
        rng = random.Random(2026)
        for case in range(40):
            processes = [Process(f"P{i}", rng.randrange(12), rng.randrange(1, 10)) for i in range(8)]
            fifo = simulate_fifo(deepcopy(processes))
            rr = simulate_round_robin(deepcopy(processes), 9)
            with self.subTest(case=case):
                self.assertEqual(results(fifo.processes), results(rr.processes))
                self.assertEqual(fifo.context_switches, rr.context_switches)

    def test_wait_matches_independently_counted_queue_time(self):
        rng = random.Random(42)
        for case in range(40):
            processes = [Process(f"P{i}", rng.randrange(8), rng.randrange(1, 8)) for i in range(6)]
            for policy, quantum in (("fifo", 3), ("rr", 1), ("rr", 3)):
                result = simulate(deepcopy(processes), policy, quantum)
                # Se reconstruye quién usó cada tick desde la bitácora y se cuenta
                # cuánto esperó cada proceso ya llegado pero sin ejecutar.
                ticks = [e.split("] ", 1)[1].split(" ejecuta", 1)[0]
                         for e in result.events if " ejecuta [" in e or "CPU ocioso" in e]
                for p in result.processes:
                    with self.subTest(case=case, policy=policy, quantum=quantum, process=p.identifier):
                        waiting = sum(ticks[t] != p.identifier for t in range(p.arrival, p.finish))
                        self.assertEqual(p.wait, waiting)
                        self.assertEqual(sum(t == p.identifier for t in ticks), p.duration)
                        self.assertGreaterEqual(p.wait, p.response)
                        self.assertEqual(p.state, "Terminado")
                self.assertEqual(result.busy_time, sum(p.duration for p in processes))

    def test_reusing_processes_resets_all_state(self):
        processes = read_processes(ROOT / "procesos.csv")
        first = results(simulate_round_robin(processes, 1).processes)
        simulate_fifo(processes)
        self.assertEqual(results(simulate_round_robin(processes, 1).processes), first)

    def test_metric_ties_use_input_order(self):
        result = simulate_fifo([Process("PrimeroEnArchivo", 10, 1), Process("Segundo", 0, 1)])
        m = calculate_metrics(result)
        self.assertEqual(m["longest_wait_process"], "PrimeroEnArchivo")
        self.assertEqual(m["shortest_wait_process"], "PrimeroEnArchivo")

    def test_invalid_scheduler_arguments(self):
        for policy, quantum in (("otro", 1), ("rr", 0), ("rr", -1), ("rr", 1.5), ("rr", "3")):
            with self.subTest(policy=policy, quantum=quantum), self.assertRaises(ValueError):
                simulate([Process("A", 0, 1)], policy, quantum)
        with self.assertRaises(ValueError):
            simulate([])


class InputAndCliTests(unittest.TestCase):
    def read_text(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "entrada.csv"
            path.write_text(text, encoding="utf-8")
            return read_processes(path)

    def test_all_required_invalid_inputs(self):
        cases = [
            ("", "vacío"), ("id,llegada,duracion\n", "no contiene"),
            ("id,llegada,duracion\n,0,1\n", "vacío"),
            ("id,llegada,duracion\nA,0,1\nA,1,1\n", "duplicado"),
            ("id,llegada,duracion\nA,-1,1\n", "mayor o igual"),
            ("id,llegada,duracion\nA,0,0\n", "mayor que cero"),
            ("id,llegada,duracion\nA,0,-2\n", "mayor que cero"),
            ("id,llegada,duracion\nA,x,1\n", "entero"),
            ("id,llegada,duracion\nA,0,1.5\n", "entero"),
            ("id,llegada,duracion\nA,0\n", "3 columnas"),
            ("id,llegada,duracion\nA,0,1,extra\n", "3 columnas"),
            ("nombre,tiempo,uso\nA,0,1\n", "encabezado"),
            ('id,llegada,duracion\n"A,0,1\n', "interpretar"),
        ]
        for text, message in cases:
            with self.subTest(text=text), self.assertRaisesRegex(InputError, message):
                self.read_text(text)

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(InputError, "No existe"):
                read_processes(Path(directory) / "no_existe.csv")

    def test_english_header_bom_and_spaces(self):
        p = self.read_text("\ufeffid,arrival,duration\n A , 0 , 2 \n")[0]
        self.assertEqual((p.identifier, p.arrival, p.duration), ("A", 0, 2))

    def cli(self, directory, *args):
        return subprocess.run([sys.executable, str(ROOT / "minios.py"), *args], cwd=directory,
                              capture_output=True, text=True, encoding="utf-8")

    def test_default_execution_and_spanish_output_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            completed = self.cli(directory)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("Round Robin (quantum = 3)", completed.stdout)
            with (Path(directory) / "resultados.csv").open() as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(list(rows[0]), ["id", "llegada", "duracion", "inicio", "fin", "espera",
                                             "retorno", "respuesta", "expropiaciones"])
            self.assertEqual([row["id"] for row in rows], ["P1", "P2", "P3", "P4"])
            self.assertEqual(rows[0]["fin"], "11")
            self.assertIn("[18] P3 termina", (Path(directory) / "eventos.txt").read_text())

    def test_cli_invalid_options_create_no_output(self):
        for args in [("--politica", "otro"), ("--quantum", "0"), ("--quantum", "-2"),
                     ("--quantum", "1.5"), ("--quantum", "abc"),
                     ("--archivo", str(ROOT / "casos/invalidos/duplicados.csv"))]:
            with self.subTest(args=args), tempfile.TemporaryDirectory() as directory:
                completed = self.cli(directory, *args)
                self.assertNotEqual(completed.returncode, 0)
                self.assertTrue(completed.stderr)
                self.assertEqual(list(Path(directory).iterdir()), [])

    def test_fifo_ignores_quantum(self):
        with tempfile.TemporaryDirectory() as directory:
            completed = self.cli(directory, "--politica", "fifo", "--quantum", "ignorado")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("Espera promedio: 4.50", completed.stdout)

    def test_comparison_keeps_selected_policy_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            completed = self.cli(directory, "--politica", "fifo", "--comparar", "--quantum", "1")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("COMPARACIÓN DE POLÍTICAS", completed.stdout)
            with (Path(directory) / "resultados.csv").open() as file:
                row = next(csv.DictReader(file))
            self.assertEqual(row["fin"], "5")

    def test_input_is_never_overwritten_by_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "resultados.csv"
            original = "id,llegada,duracion\nA,0,2\n"
            path.write_text(original)
            completed = self.cli(directory, "--archivo", str(path))
            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(path.read_text(), original)
            self.assertFalse((Path(directory) / "eventos.txt").exists())


if __name__ == "__main__":
    unittest.main()
