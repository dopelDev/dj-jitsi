#!/usr/bin/env python3
"""
Test de WebSocket con Selenium para pytest
Detecta el error: wss://http//localhost:8080/xmpp-websocket
"""

import os
import sys
import time
import re
import json
import logging
import pytest
from datetime import datetime
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.service import Service as FirefoxService
except ImportError as e:
    pytest.skip(f"Dependencias de Selenium no encontradas: {e}", allow_module_level=True)

# Configuración desde variables de entorno
JITSI_URL = os.getenv('JITSI_URL', 'http://localhost:8080')
TEST_ROOM = os.getenv('TEST_ROOM', 'test-websocket-error')
HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
TIMEOUT = int(os.getenv('TEST_TIMEOUT', '30'))
BROWSER = os.getenv('BROWSER', 'chrome').lower()
SCREENSHOT_DIR = os.getenv('SCREENSHOT_DIR', './test-results/screenshots')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

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

class WebSocketSeleniumTest:
    def __init__(self):
        self.driver = None
        self.errors_found = []
        self.warnings_found = []
        self.console_logs = []
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'jitsi_url': JITSI_URL,
            'test_room': TEST_ROOM,
            'browser': BROWSER,
            'headless': HEADLESS,
            'errors': [],
            'warnings': [],
            'console_logs': [],
            'screenshots': []
        }
        
        # Configurar logging
        logging.basicConfig(level=getattr(logging, LOG_LEVEL))
        self.logger = logging.getLogger(__name__)
        
        # Crear directorio de screenshots
        Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)

    def setup_driver(self):
        """Configurar Chrome/Firefox con opciones necesarias"""
        try:
            if BROWSER == 'chrome':
                options = Options()
                if HEADLESS:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--window-size=1920,1080')
                options.add_argument('--disable-web-security')
                options.add_argument('--allow-running-insecure-content')
                
                # Habilitar captura de logs
                options.add_argument('--enable-logging')
                options.add_argument('--log-level=0')
                
                # Configurar capacidades para capturar logs
                caps = DesiredCapabilities.CHROME
                caps['goog:loggingPrefs'] = {'browser': 'ALL', 'driver': 'ALL'}
                
                # Usar webdriver-manager para gestionar ChromeDriver
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options, desired_capabilities=caps)
                
            elif BROWSER == 'firefox':
                options = FirefoxOptions()
                if HEADLESS:
                    options.add_argument('--headless')
                options.add_argument('--width=1920')
                options.add_argument('--height=1080')
                
                # Configurar capacidades para capturar logs
                caps = DesiredCapabilities.FIREFOX
                caps['loggingPrefs'] = {'browser': 'ALL', 'driver': 'ALL'}
                
                # Usar webdriver-manager para gestionar GeckoDriver
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options, desired_capabilities=caps)
                
            else:
                raise ValueError(f"Navegador no soportado: {BROWSER}")
                
            self.driver.set_page_load_timeout(TIMEOUT)
            self.logger.info(f"✅ Driver {BROWSER} configurado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error configurando driver: {e}")
            return False

    def open_jitsi_room(self, room_name):
        """Abrir sala de Jitsi Meet"""
        try:
            room_url = f"{JITSI_URL}/{room_name}"
            self.logger.info(f"🌐 Abriendo sala: {room_url}")
            
            self.driver.get(room_url)
            
            # Esperar a que la página cargue
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self.logger.info("✅ Sala de Jitsi Meet abierta correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error abriendo sala: {e}")
            return False

    def get_console_logs(self):
        """Obtener logs de consola del navegador"""
        try:
            logs = self.driver.get_log('browser')
            self.console_logs.extend(logs)
            
            # Procesar logs
            for log in logs:
                log_entry = {
                    'timestamp': log['timestamp'],
                    'level': log['level'],
                    'message': log['message'],
                    'source': log['source']
                }
                self.test_results['console_logs'].append(log_entry)
                
            self.logger.info(f"📋 Capturados {len(logs)} logs de consola")
            return logs
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo logs: {e}")
            return []

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

    def take_screenshot(self, name):
        """Capturar screenshot para debugging"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = os.path.join(SCREENSHOT_DIR, filename)
            
            self.driver.save_screenshot(filepath)
            self.test_results['screenshots'].append(filepath)
            self.logger.info(f"📸 Screenshot guardado: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ Error tomando screenshot: {e}")
            return None

    def wait_for_errors(self, duration=10):
        """Esperar y monitorear errores durante un tiempo específico"""
        self.logger.info(f"⏳ Monitoreando errores durante {duration} segundos...")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            # Obtener logs actuales
            current_logs = self.get_console_logs()
            
            # Detectar errores
            self.detect_websocket_errors(current_logs)
            self.detect_malformed_urls(current_logs)
            
            time.sleep(1)  # Esperar 1 segundo entre verificaciones

    def generate_report(self):
        """Generar reporte JSON con resultados"""
        try:
            # Actualizar resultados
            self.test_results['errors'] = self.errors_found
            self.test_results['warnings'] = self.warnings_found
            self.test_results['total_errors'] = len(self.errors_found)
            self.test_results['total_warnings'] = len(self.warnings_found)
            
            # Guardar reporte
            report_file = f"./test-results/websocket-test-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            Path("./test-results").mkdir(exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"📊 Reporte generado: {report_file}")
            return report_file
            
        except Exception as e:
            self.logger.error(f"❌ Error generando reporte: {e}")
            return None

    def cleanup(self):
        """Limpiar recursos"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("🧹 Driver cerrado correctamente")
            except Exception as e:
                self.logger.error(f"❌ Error cerrando driver: {e}")

    def run(self):
        """Ejecutar test completo"""
        self.logger.info("🚀 Iniciando test de WebSocket con Selenium")
        self.logger.info(f"📋 Configuración: {BROWSER}, headless={HEADLESS}, timeout={TIMEOUT}s")
        
        try:
            # 1. Configurar driver
            if not self.setup_driver():
                return False
            
            # 2. Abrir sala de Jitsi Meet
            if not self.open_jitsi_room(TEST_ROOM):
                return False
            
            # 3. Esperar un poco para que cargue
            time.sleep(5)
            
            # 4. Obtener logs iniciales
            self.get_console_logs()
            
            # 5. Monitorear errores
            self.wait_for_errors(15)  # Monitorear por 15 segundos
            
            # 6. Tomar screenshot si hay errores
            if self.errors_found:
                self.take_screenshot("websocket_error")
            
            # 7. Generar reporte
            report_file = self.generate_report()
            
            # 8. Mostrar resultados
            self.print_results()
            
            return len(self.errors_found) == 0
            
        except Exception as e:
            self.logger.error(f"❌ Error durante el test: {e}")
            self.take_screenshot("test_error")
            return False
            
        finally:
            self.cleanup()

    def print_results(self):
        """Imprimir resultados del test"""
        print("\n" + "="*60)
        print("📊 RESULTADOS DEL TEST DE WEBSOCKET CON SELENIUM")
        print("="*60)
        
        print(f"🌐 URL: {JITSI_URL}")
        print(f"🏠 Sala: {TEST_ROOM}")
        print(f"🌍 Navegador: {BROWSER}")
        print(f"👻 Headless: {HEADLESS}")
        print(f"⏱️  Timeout: {TIMEOUT}s")
        
        print(f"\n📋 Logs capturados: {len(self.console_logs)}")
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
            print(f"\n📸 Screenshots: {len(self.test_results['screenshots'])}")
            for screenshot in self.test_results['screenshots']:
                print(f"  - {screenshot}")
        
        print("\n" + "="*60)
        
        if self.errors_found:
            print("❌ TEST FALLÓ - Se detectaron errores de WebSocket")
            return False
        else:
            print("✅ TEST EXITOSO - No se detectaron errores de WebSocket")
            return True

def main():
    """Función principal"""
    print("🧪 Test de WebSocket con Selenium")
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
    
    # Ejecutar test
    test = WebSocketSeleniumTest()
    success = test.run()
    
    return 0 if success else 1

# Funciones de test para pytest
@pytest.mark.selenium
def test_websocket_selenium_basic(jitsi_url, test_room):
    """Test básico de WebSocket con Selenium"""
    test = WebSocketSeleniumTest()
    test.test_results['jitsi_url'] = jitsi_url
    test.test_results['test_room'] = test_room
    
    try:
        # Configurar driver
        if not test.setup_driver():
            pytest.fail("No se pudo configurar el driver de Selenium")
        
        # Abrir sala de Jitsi Meet
        if not test.open_jitsi_room(test_room):
            pytest.fail(f"No se pudo abrir la sala {test_room}")
        
        # Esperar un poco para que cargue
        time.sleep(5)
        
        # Obtener logs iniciales
        test.get_console_logs()
        
        # Monitorear errores
        test.wait_for_errors(10)  # Monitorear por 10 segundos
        
        # Verificar que no hay errores críticos
        assert len(test.errors_found) == 0, f"Se detectaron errores de WebSocket: {test.errors_found}"
        
    finally:
        test.cleanup()

@pytest.mark.selenium
def test_websocket_selenium_malformed_url_detection(jitsi_url, test_room):
    """Test específico para detectar URLs malformadas"""
    test = WebSocketSeleniumTest()
    test.test_results['jitsi_url'] = jitsi_url
    test.test_results['test_room'] = test_room
    
    try:
        # Configurar driver
        if not test.setup_driver():
            pytest.fail("No se pudo configurar el driver de Selenium")
        
        # Abrir sala de Jitsi Meet
        if not test.open_jitsi_room(test_room):
            pytest.fail(f"No se pudo abrir la sala {test_room}")
        
        # Esperar un poco para que cargue
        time.sleep(5)
        
        # Obtener logs y detectar URLs malformadas
        logs = test.get_console_logs()
        malformed_urls = test.detect_malformed_urls(logs)
        
        # Si se detectan URLs malformadas, el test debe fallar
        if malformed_urls:
            pytest.fail(f"URLs malformadas detectadas: {malformed_urls}")
        
        print("✅ No se detectaron URLs malformadas")
        
    finally:
        test.cleanup()

@pytest.mark.selenium
def test_websocket_selenium_error_patterns(jitsi_url, test_room):
    """Test para detectar patrones de error específicos"""
    test = WebSocketSeleniumTest()
    test.test_results['jitsi_url'] = jitsi_url
    test.test_results['test_room'] = test_room
    
    try:
        # Configurar driver
        if not test.setup_driver():
            pytest.fail("No se pudo configurar el driver de Selenium")
        
        # Abrir sala de Jitsi Meet
        if not test.open_jitsi_room(test_room):
            pytest.fail(f"No se pudo abrir la sala {test_room}")
        
        # Esperar un poco para que cargue
        time.sleep(5)
        
        # Obtener logs y detectar errores
        logs = test.get_console_logs()
        errors = test.detect_websocket_errors(logs)
        
        # Verificar que no hay errores críticos
        critical_errors = [e for e in errors if e['type'] in ['websocket_malformed', 'websocket_failed']]
        assert len(critical_errors) == 0, f"Errores críticos detectados: {critical_errors}"
        
        print("✅ No se detectaron errores críticos de WebSocket")
        
    finally:
        test.cleanup()

@pytest.mark.selenium
def test_websocket_selenium_screenshot_on_error(jitsi_url, test_room):
    """Test que toma screenshot si hay errores"""
    test = WebSocketSeleniumTest()
    test.test_results['jitsi_url'] = jitsi_url
    test.test_results['test_room'] = test_room
    
    try:
        # Configurar driver
        if not test.setup_driver():
            pytest.fail("No se pudo configurar el driver de Selenium")
        
        # Abrir sala de Jitsi Meet
        if not test.open_jitsi_room(test_room):
            pytest.fail(f"No se pudo abrir la sala {test_room}")
        
        # Esperar un poco para que cargue
        time.sleep(5)
        
        # Obtener logs y detectar errores
        logs = test.get_console_logs()
        errors = test.detect_websocket_errors(logs)
        
        # Si hay errores, tomar screenshot
        if errors:
            screenshot_path = test.take_screenshot("websocket_error")
            assert screenshot_path is not None, "No se pudo tomar screenshot"
            assert os.path.exists(screenshot_path), f"Screenshot no encontrado: {screenshot_path}"
            print(f"✅ Screenshot tomado: {screenshot_path}")
        
        print("✅ Test de screenshot completado")
        
    finally:
        test.cleanup()

if __name__ == "__main__":
    sys.exit(main())
