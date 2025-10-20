#!/usr/bin/env python3
"""
Script principal para ejecutar todos los tests de Jitsi Meet con pytest
"""
import sys
import pytest
import os
from pathlib import Path

def main():
    """Ejecutar pytest con configuración optimizada para Jitsi Meet"""
    
    # Configurar argumentos de pytest
    args = [
        '-v',                    # verbose
        '--tb=short',           # traceback corto
        '--color=yes',          # colores
        '--strict-markers',     # marcas estrictas
        '--disable-warnings',   # deshabilitar warnings
        '--timeout=60',         # timeout por test (60 segundos)
        '--durations=10',       # mostrar 10 tests más lentos
        '--junit-xml=test-results/junit.xml',  # reporte JUnit
        '--html=test-results/report.html',    # reporte HTML
        '--self-contained-html', # HTML autocontenido
    ]
    
    # Agregar argumentos pasados por línea de comandos
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])
    
    # Crear directorio de resultados
    Path('test-results').mkdir(exist_ok=True)
    
    print("🧪 Ejecutando Tests de Jitsi Meet con pytest")
    print("=" * 50)
    print(f"📁 Directorio de tests: {os.getcwd()}/tests")
    print(f"📊 Reportes en: test-results/")
    print("=" * 50)
    
    # Ejecutar pytest
    exit_code = pytest.main(args)
    
    if exit_code == 0:
        print("\n✅ Todos los tests pasaron exitosamente")
    else:
        print(f"\n❌ {exit_code} tests fallaron")
    
    return exit_code

if __name__ == '__main__':
    sys.exit(main())
