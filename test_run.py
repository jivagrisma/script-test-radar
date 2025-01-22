"""
Script de prueba para ejecutar Test Radar en un caso real.
Analiza los tests del proyecto API-H2H.
"""

import asyncio
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from src.core.config import load_config
from src.core.logger import setup_logger
from src.scanner.scanner import TestScanner
from src.executor.executor import TestExecutor
from src.reporter.reporter import TestReporter
from src.analyzer.llm_analyzer import LLMAnalyzer

console = Console()
logger = setup_logger()

async def main():
    """Función principal de prueba"""
    try:
        # Cargar configuración
        config_path = Path("test_config.json")
        console.print(Panel("🔧 Cargando configuración...", title="Test Radar"))
        config = load_config(config_path)
        
        # Inicializar componentes
        scanner = TestScanner(config.test)
        executor = TestExecutor(config.test)
        reporter = TestReporter(config.test)
        analyzer = LLMAnalyzer(config.llm)
        
        # Escanear tests
        console.print("\n🔍 Escaneando tests en API-H2H...")
        all_tests = []
        for path in config.test.test_paths:
            path = Path(path)
            if path.is_file():
                tests = scanner.scan_file(path)
            else:
                tests = list(scanner.scan_directory(path))
            all_tests.extend(tests)
        
        console.print(f"✨ Encontrados {len(all_tests)} tests")
        for test in all_tests:
            console.print(f"  • {test.id}")
        
        # Ejecutar tests
        console.print("\n⚡ Ejecutando tests...")
        results = await executor.run_tests(all_tests)
        
        # Generar reporte
        console.print("\n📊 Generando reporte...")
        test_report = reporter.generate_report(all_tests, results)
        reporter.print_report(test_report)
        
        # Guardar reporte
        report_path = Path(config.report_dir) / "test_report.html"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        reporter.save_report(test_report, report_path)
        console.print(f"\n📝 Reporte guardado en {report_path}")
        
        # Analizar resultados con Claude
        console.print("\n🤖 Analizando tests con Claude...")
        analyses = await analyzer.analyze_results(all_tests, results)
        
        # Mostrar análisis
        console.print("\n🔬 Resultados del Análisis:")
        for test_id, analysis in analyses.items():
            console.print(f"\n[cyan]Test: {test_id}[/cyan]")
            
            if analysis.issues:
                console.print("\n[red]Problemas Detectados:[/red]")
                for issue in analysis.issues:
                    console.print(f"  • {issue}")
            
            if analysis.suggestions:
                console.print("\n[green]Sugerencias de Mejora:[/green]")
                for suggestion in analysis.suggestions:
                    console.print(f"  • {suggestion}")
            
            if analysis.coverage_gaps:
                console.print("\n[yellow]Gaps de Cobertura:[/yellow]")
                for gap in analysis.coverage_gaps:
                    console.print(f"  • {gap}")
            
            if analysis.fixes:
                console.print("\n[blue]Correcciones Sugeridas:[/blue]")
                for fix in analysis.fixes:
                    console.print(Panel(
                        f"[red]Original:[/red]\n{fix.original_code}\n\n" +
                        f"[green]Sugerido:[/green]\n{fix.suggested_code}",
                        title=f"Fix para {fix.file_path}"
                    ))
        
        # Guardar análisis
        analysis_path = Path(config.report_dir) / "analysis_report.json"
        with open(analysis_path, 'w') as f:
            json.dump(
                {
                    test_id: analysis.model_dump()
                    for test_id, analysis in analyses.items()
                },
                f,
                indent=2,
                default=str
            )
        console.print(f"\n💾 Análisis guardado en {analysis_path}")
        
        # Resumen final
        console.print("\n📈 Resumen Final:")
        console.print(f"  • Tests Totales: {test_report.total_tests}")
        console.print(f"  • Tests Pasados: [green]{test_report.passed_tests}[/green]")
        console.print(f"  • Tests Fallidos: [red]{test_report.failed_tests}[/red]")
        console.print(f"  • Tests con Error: [red]{test_report.error_tests}[/red]")
        console.print(f"  • Cobertura Promedio: {test_report.total_coverage:.2f}%")
        console.print(f"  • Duración Total: {test_report.total_duration:.2f}s")
        
    except Exception as e:
        console.print(f"\n[red]❌ Error: {str(e)}[/red]")
        raise

if __name__ == '__main__':
    asyncio.run(main())