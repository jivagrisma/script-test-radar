#!/usr/bin/env python3
"""
Script auxiliar para ejecutar el análisis de tests.
"""

import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from rich.console import Console

from src.analyzer.llm_analyzer import LLMAnalyzer
from src.core.config import load_config
from src.executor.executor import TestResult
from src.scanner.scanner import TestScanner

console = Console()


@dataclass
class DummyTestResult(TestResult):
    """Resultado de prueba simulado para análisis estático."""

    test_id: str
    status: str = "unknown"
    duration: float = 0.0
    coverage: Optional[float] = None
    stdout: str = ""
    stderr: str = ""


async def run_analysis():
    """Ejecutar análisis de tests."""
    try:
        # Cargar configuración
        config = load_config("test_config.json")

        # Inicializar componentes
        scanner = TestScanner(config.test)
        analyzer = LLMAnalyzer(config.llm)

        # Escanear tests
        test_path = Path("test_samples")
        if test_path.is_file():
            tests = scanner.scan_file(test_path)
        else:
            tests = list(scanner.scan_directory(test_path))

        if not tests:
            console.print("[red]No se encontraron tests[/red]")
            sys.exit(1)

        console.print(f"\nAnalizando {len(tests)} tests...")

        # Crear resultados dummy para análisis estático
        results = {
            test.id: DummyTestResult(
                test_id=test.id,
                status="unknown",
                duration=0.0,
                coverage=None,
                stdout="",
                stderr="",
            )
            for test in tests
        }

        # Analizar tests
        analyses = await analyzer.analyze_results(tests, results)

        # Imprimir resultados
        for test_id, analysis in analyses.items():
            console.print(f"\n[cyan]Test: {test_id}[/cyan]")

            if analysis.issues:
                console.print("\n[red]Issues:[/red]")
                for issue in analysis.issues:
                    console.print(f"  • {issue}")

            if analysis.suggestions:
                console.print("\n[green]Suggestions:[/green]")
                for suggestion in analysis.suggestions:
                    console.print(f"  • {suggestion}")

            if analysis.coverage_gaps:
                console.print("\n[yellow]Coverage Gaps:[/yellow]")
                for gap in analysis.coverage_gaps:
                    console.print(f"  • {gap}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_analysis())
