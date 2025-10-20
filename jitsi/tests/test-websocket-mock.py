#!/usr/bin/env python3
"""
Test Mock de WebSocket con Selenium
Simula el comportamiento del test de Selenium sin necesidad de navegador
"""

import os
import sys
import time
import re
import json
import logging
from datetime import datetime
from pathlib import Path

# Configuración desde variables de entorno
JITSI_URL = os.getenv('JITSI_URL', 'http://localhost:8080')
TEST_ROOM = os.getenv('TEST_ROOM', 'test-websocket-error')
TIMEOUT = int(os.getenv('TEST_TIMEOUT', '30'))

# Patrones de error a detectar
ERROR_PATTERNS = {
    'websocket_malformed': r'wss://https?//[^/]+',
    'websocket_failed': r'WebSocket connection to .* failed',
    'strophe_error': r'Strophe: Websocket error',
    'strophe_closed': r'Strophe: Websocket closed',
    'connection_fail': r'connfail\[.*WebSocket.*\]',
    'websocket_timeout': r'WebSocket.*timeout',
    'xmpp_connection_failed': r'XMPP.*connection.*failed',
}

class WebSocketMockTest:
    def __init__(self):
        self.errors_found = []
        self.warnings_found = []
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'jitsi_url': JITSI_URL,
            'test_room': TEST_ROOM,
            'test_type': 'mock',
            'errors': [],
            'warnings': [],
            'simulated_logs': [],
            'screenshots': []
        }
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def simulate_browser_logs(self):
        """Simular logs de navegador que contienen el error específico"""
        simulated_logs = [
            {
                'timestamp': int(time.time() * 1000),
                'level': 'SEVERE',
                'message': 'WebSocket connection to \'wss://http//localhost:8080/xmpp-websocket?room=recentconcessionscrysure\' failed:',
                'source': 'console'
            },
            {
                'timestamp': int(time.time() * 1000) + 100,
                'level': 'SEVERE',
                'message': 'Strophe: Websocket error {"isTrusted":true}',
                'source': 'console'
            },
            {
                'timestamp': int(time.time() * 1000) + 200,
                'level': 'SEVERE',
                'message': 'Strophe: Websocket closed unexcectedly',
                'source': 'console'
            },
            {
                'timestamp': int(time.time() * 1000) + 300,
                'level': 'INFO',
                'message': 'Strophe connfail[The WebSocket connection could not be established or was disconnected.]: 1720.3000000044703',
                'source': 'console'
            },
            {
                'timestamp': int(time.time() * 1000) + 400,
                'level': 'INFO',
                'message': 'The conference will be reloaded after 30 seconds.',
                'source': 'console'
            }
        ]
        
        self.test_results['simulated_logs'] = simulated_logs
        return simulated_logs

    def detect_websocket_errors(self, logs):
        """Detectar errores específicos de WebSocket"""
        errors_detected = []
        
        for log in logs:
            message = log.get('message', '')
            
            # Buscar patrones de error
            for error_type, pattern in ERROR_PATTERNS.items():
                if re.search(pattern, message, re.IGNORECASE):
                    error_info = {
                        'type': error_type,
                        'pattern': pattern,
                        'message': message,
                        'timestamp': log.get('timestamp', 0),
                        'level': log.get('level', 'UNKNOWN')
                    }
                    errors_detected.append(error_info)
                    self.errors_found.append(error_info)
                    self.logger.error(f"🚨 Error detectado [{error_type}]: {message}")
        
        return errors_detected

    def detect_malformed_urls(self, logs):
        """Detectar URLs malformadas en logs"""
        malformed_urls = []
        
        for log in logs:
            message = log.get('message', '')
            
            # Buscar URLs malformadas específicas
            if 'wss://http//' in message or 'ws://http//' in message:
                malformed_urls.append({
                    'url': message,
                    'timestamp': log.get('timestamp', 0),
                    'level': log.get('level', 'UNKNOWN')
                })
                self.logger.error(f"🚨 URL malformada detectada: {message}")
        
        return malformed_urls

    def simulate_screenshot(self, name):
        """Simular captura de screenshot"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = f"./test-results/screenshots/{filename}"
            
            # Crear directorio si no existe
            Path("./test-results/screenshots").mkdir(parents=True, exist_ok=True)
            
            # Simular screenshot (crear archivo vacío)
            with open(filepath, 'w') as f:
                f.write("# Mock screenshot - Error WebSocket detectado\n")
            
            self.test_results['screenshots'].append(filepath)
            self.logger.info(f"📸 Screenshot simulado guardado: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ Error simulando screenshot: {e}")
            return None

    def generate_report(self):
        """Generar reporte JSON con resultados"""
        try:
            # Actualizar resultados
            self.test_results['errors'] = self.errors_found
            self.test_results['warnings'] = self.warnings_found
            self.test_results['total_errors'] = len(self.errors_found)
            self.test_results['total_warnings'] = len(self.warnings_found)
            
            # Guardar reporte
            report_file = f"./test-results/websocket-mock-test-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            Path("./test-results").mkdir(exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"📊 Reporte generado: {report_file}")
            return report_file
            
        except Exception as e:
            self.logger.error(f"❌ Error generando reporte: {e}")
            return None

    def run(self):
        """Ejecutar test mock completo"""
        self.logger.info("🚀 Iniciando test mock de WebSocket con Selenium")
        self.logger.info(f"📋 Configuración: mock, timeout={TIMEOUT}s")
        
        try:
            # 1. Simular logs de navegador
            self.logger.info("📋 Simulando logs de navegador...")
            logs = self.simulate_browser_logs()
            
            # 2. Detectar errores
            self.logger.info("🔍 Detectando errores de WebSocket...")
            self.detect_websocket_errors(logs)
            self.detect_malformed_urls(logs)
            
            # 3. Simular screenshot si hay errores
            if self.errors_found:
                self.simulate_screenshot("websocket_error")
            
            # 4. Generar reporte
            report_file = self.generate_report()
            
            # 5. Mostrar resultados
            self.print_results()
            
            return len(self.errors_found) == 0
            
        except Exception as e:
            self.logger.error(f"❌ Error durante el test: {e}")
            return False

    def print_results(self):
        """Imprimir resultados del test"""
        print("\n" + "="*60)
        print("📊 RESULTADOS DEL TEST MOCK DE WEBSOCKET")
        print("="*60)
        
        print(f"🌐 URL: {JITSI_URL}")
        print(f"🏠 Sala: {TEST_ROOM}")
        print(f"🧪 Tipo: Mock (sin navegador)")
        print(f"⏱️  Timeout: {TIMEOUT}s")
        
        print(f"\n📋 Logs simulados: {len(self.test_results['simulated_logs'])}")
        print(f"🚨 Errores encontrados: {len(self.errors_found)}")
        print(f"⚠️  Advertencias: {len(self.warnings_found)}")
        
        if self.errors_found:
            print("\n🚨 ERRORES DETECTADOS:")
            for i, error in enumerate(self.errors_found, 1):
                print(f"  {i}. [{error['type']}] {error['message']}")
        
        if self.warnings_found:
            print("\n⚠️  ADVERTENCIAS:")
            for i, warning in enumerate(self.warnings_found, 1):
                print(f"  {i}. {warning}")
        
        if self.test_results['screenshots']:
            print(f"\n📸 Screenshots simulados: {len(self.test_results['screenshots'])}")
            for screenshot in self.test_results['screenshots']:
                print(f"  - {screenshot}")
        
        print("\n" + "="*60)
        
        if self.errors_found:
            print("❌ TEST MOCK EXITOSO - Se detectaron errores de WebSocket (como se esperaba)")
            return False
        else:
            print("✅ TEST MOCK EXITOSO - No se detectaron errores de WebSocket")
            return True

def main():
    """Función principal"""
    print("🧪 Test Mock de WebSocket con Selenium")
    print("="*40)
    
    # Verificar que Jitsi esté ejecutándose
    try:
        import requests
        response = requests.get(JITSI_URL, timeout=5)
        if response.status_code != 200:
            print(f"❌ Error: Jitsi no está accesible en {JITSI_URL}")
            return False
    except Exception as e:
        print(f"❌ Error: No se puede conectar a Jitsi en {JITSI_URL}: {e}")
        return False
    
    # Ejecutar test mock
    test = WebSocketMockTest()
    success = test.run()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
