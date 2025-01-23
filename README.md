# Test Radar

Test Radar es una herramienta de análisis inteligente de tests que utiliza AWS Bedrock y Claude 3.5 Sonnet para proporcionar sugerencias de mejora y detectar problemas potenciales en tus tests de Python.

## Características

- Análisis estático de código de tests
- Sugerencias de mejora basadas en IA
- Detección de patrones y anti-patrones
- Recomendaciones de cobertura
- Análisis de rendimiento
- Generación de informes detallados

## Requisitos

- Docker y Docker Compose
- Credenciales de AWS con acceso a Bedrock
- Python 3.9+ (para desarrollo local)

## Instalación Rápida

1. Clonar el repositorio:
```bash
git clone https://github.com/jivagrisma/script-test-radar.git
cd test-radar
```

2. Ejecutar el script de instalación:
```bash
chmod +x install_and_run.sh
./install_and_run.sh
```

El script realizará automáticamente:
- Verificación de requisitos
- Configuración de credenciales AWS a través del archivo .env
- Creación de directorios necesarios
- Construcción de la imagen Docker
- Configuración inicial

## Configuración

La configuración se realiza a través del archivo `.env`. Durante la instalación, el script te pedirá:

1. AWS Access Key ID
2. AWS Secret Access Key
3. AWS Region (por defecto: us-east-1)
4. Bedrock Model ID (por defecto: us.anthropic.claude-3-5-sonnet-20241022-v2:0)

También puedes editar el archivo `.env` manualmente:

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1

# Bedrock Configuration
BEDROCK_MODEL_ID=us.anthropic.claude-3-5-sonnet-20241022-v2:0
```

## Uso

### 1. Preparación de Tests

Coloca tus archivos de test en el directorio `test_samples/`. Por ejemplo:

```
test_samples/
├── test_calculator.py
└── test_api.py
```

### 2. Ejecución del Análisis

```bash
docker-compose up
```

### 3. Resultados

Los resultados se guardan en el directorio `reports/` en formato Markdown. Para cada test, se proporciona:

- Lista de problemas potenciales
- Sugerencias de mejora
- Ejemplos de código
- Recomendaciones de cobertura
- Métricas de rendimiento

## Ejemplos de Uso

### 1. Análisis de Tests Unitarios
```python
# test_samples/test_calculator.py
class TestCalculator(unittest.TestCase):
    def test_add(self):
        calc = Calculator()
        self.assertEqual(calc.add(2, 3), 5)
```

Test Radar analizará este código y sugerirá mejoras como:
- Agregar pruebas parametrizadas
- Implementar property-based testing
- Mejorar la documentación
- Agregar casos límite

### 2. Análisis de Tests de API
```python
# test_samples/test_api.py
class TestUserAPI(unittest.TestCase):
    def test_create_user(self):
        api = UserAPI()
        user = api.create_user("test", "test@example.com")
        self.assertEqual(user.username, "test")
```

Test Radar sugerirá mejoras como:
- Agregar validación de entrada
- Implementar pruebas de concurrencia
- Mejorar el manejo de errores
- Agregar pruebas de rendimiento

## Integración Continua

Puedes integrar Test Radar en tu pipeline de CI/CD:

```yaml
# .github/workflows/test-radar.yml
name: Test Analysis
on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Test Radar
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          docker-compose up
```

## Solución de Problemas

### Error de Credenciales AWS
```
Error: Failed to generate response: AccessDeniedException
```
Solución: Verifica tus credenciales AWS en el archivo .env y asegúrate de tener acceso a Bedrock.

### Error de Timeout
```
Error: Failed to generate response: ThrottlingException
```
Solución: Aumenta el valor de `timeout` en la configuración o reduce la cantidad de tests simultáneos.

## Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Push a la rama
5. Crea un Pull Request

## Licencia

MIT

## Soporte

- Abre un issue en GitHub
- Consulta la documentación
- Contacta al equipo de desarrollo
