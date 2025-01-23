# Test Radar

Test Radar es una herramienta de análisis inteligente de tests que utiliza AWS Bedrock y Claude 3.5 Sonnet para proporcionar sugerencias de mejora y detectar problemas potenciales en tus tests de Python, ayudando a alcanzar y mantener una cobertura de pruebas superior al 95%.

## Características

- Análisis estático de código de tests
- Sugerencias de mejora basadas en IA
- Detección de patrones y anti-patrones
- Recomendaciones de cobertura
- Análisis de rendimiento
- Generación de informes detallados

## Beneficios para Alta Cobertura

1. Análisis Inteligente:
   - Identifica áreas sin cobertura suficiente
   - Sugiere casos de prueba específicos
   - Proporciona ejemplos de código listos para usar
   - Detecta casos límite y escenarios no probados

2. Tipos de Pruebas Recomendadas:
   ```python
   # Property-based testing
   @given(st.floats(), st.floats())
   def test_multiply_properties(self, a, b):
       result = self.calc.multiply(a, b)
       assert result == b * a  # Propiedad conmutativa

   # Pruebas parametrizadas
   @pytest.mark.parametrize("a,b,expected", [
       (2, 3, 6),
       (-2, 3, -6),
       (0, 5, 0)
   ])
   def test_multiply_parametrized(self, a, b, expected):
       assert self.calc.multiply(a, b) == expected

   # Pruebas de rendimiento
   def test_performance(self):
       start_time = time.time()
       for _ in range(1000):
           self.calc.multiply(2.5, 3.5)
       duration = time.time() - start_time
       assert duration < 1.0  # Debe completarse en menos de 1 segundo
   ```

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

2. Configurar credenciales:
```bash
cp .env.example .env
# Editar .env con las credenciales de AWS Bedrock:
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
# AWS_REGION=us-east-1
# BEDROCK_MODEL_ID=your_model_id
```

3. Ejecutar el script de instalación:
```bash
chmod +x install_and_run.sh
./install_and_run.sh
```

## Uso para Alta Cobertura

1. Preparación:
   - Coloca tus archivos de test en `test_samples/`
   - Asegúrate de que el archivo .env está configurado
   - Verifica que Docker está corriendo

2. Análisis Inicial:
```bash
docker-compose up
```

3. Implementar Mejoras:
   - Revisa el reporte en `reports/`
   - Implementa las sugerencias proporcionadas
   - Agrega los casos de prueba recomendados

4. Verificar Mejoras:
   - Ejecuta el análisis nuevamente
   - Revisa el nuevo reporte de cobertura
   - Repite el proceso hasta alcanzar >95%

## Ejemplos de Mejoras de Cobertura

### 1. Pruebas Básicas a Completas
```python
# Antes
def test_add(self):
    self.assertEqual(calc.add(2, 3), 5)

# Después
def test_add_comprehensive(self):
    # Casos básicos
    self.assertEqual(calc.add(2, 3), 5)

    # Casos límite
    self.assertEqual(calc.add(0, 0), 0)
    self.assertEqual(calc.add(-1, 1), 0)

    # Números grandes
    self.assertEqual(calc.add(sys.maxsize-1, 1), sys.maxsize)

    # Flotantes
    self.assertAlmostEqual(calc.add(0.1, 0.2), 0.3)
```

### 2. Property-Based Testing
```python
@given(st.floats(allow_nan=False, allow_infinity=False),
       st.floats(allow_nan=False, allow_infinity=False))
def test_multiply_properties(self, a, b):
    result = self.calc.multiply(a, b)
    # Propiedad conmutativa
    assert abs(result - self.calc.multiply(b, a)) < 1e-10
    # Propiedad con cero
    assert self.calc.multiply(a, 0) == 0
    # Propiedad con uno
    assert self.calc.multiply(a, 1) == a
```

### 3. Pruebas de Concurrencia
```python
def test_concurrent_access(self):
    """Test concurrent API access."""
    from concurrent.futures import ThreadPoolExecutor

    def create_user(i):
        return self.api.create_user(f"user{i}", f"user{i}@example.com")

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create_user, i) for i in range(100)]
        results = [f.result() for f in futures]

    self.assertEqual(len(self.api.list_users()), 100)
```

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
Solución: Verifica tus credenciales en el archivo .env y asegúrate de tener acceso a Bedrock.

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
