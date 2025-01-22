# Test Radar

Un sistema inteligente de pruebas unitarias con detección y corrección de errores, integrado con Claude a través de AWS Bedrock para análisis avanzado.

## Características

- 🔍 Detección automática de tests
- ⚡ Ejecución paralela de tests
- 📊 Análisis de cobertura
- 🤖 Análisis inteligente con Claude vía AWS Bedrock
- 🛠️ Sugerencias de corrección automática
- 📝 Reportes detallados
- 🎯 Integración con VSCode

## Requisitos

- Python 3.11.11 o superior
- Poetry para gestión de dependencias
- Cuenta AWS con acceso a Bedrock
- VSCode (opcional, para integración con el editor)

## Instalación

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd test-radar
```

2. Instalar dependencias con Poetry:
```bash
poetry install
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
```

Editar .env con tus configuraciones, especialmente las credenciales de AWS:
```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

## Configuración de AWS Bedrock

1. Asegúrate de tener una cuenta AWS con acceso a Bedrock

2. Verifica que tienes acceso al modelo Claude en tu región:
```bash
aws bedrock list-foundation-models --region us-east-1
```

3. Configura las credenciales de AWS:
   - Usa las variables de entorno mencionadas arriba, o
   - Configura el CLI de AWS: `aws configure`

4. (Opcional) Ajusta la configuración del modelo en `config.json`:
```json
{
  "llm": {
    "temperature": 0.7,
    "max_tokens": 2000,
    "context_window": 100000,
    "aws": {
      "region": "us-east-1",
      "bedrock_model_id": "anthropic.claude-3-sonnet-20240229-v1:0"
    }
  }
}
```

## Uso

### CLI

1. Escanear tests en un directorio:
```bash
poetry run python -m src.main scan ./tests
```

2. Ejecutar tests con análisis de Claude:
```bash
poetry run python -m src.main run ./tests --coverage
```

3. Analizar tests sin ejecutarlos:
```bash
poetry run python -m src.main analyze ./tests
```

### Opciones Comunes

- `--config/-c`: Especificar archivo de configuración
- `--parallel/--no-parallel`: Habilitar/deshabilitar ejecución paralela
- `--coverage/--no-coverage`: Habilitar/deshabilitar análisis de cobertura
- `--report/-r`: Guardar reporte en archivo
- `--fix/--no-fix`: Aplicar correcciones automáticamente

## Integración con VSCode

1. Instalar la extensión Test Radar desde el marketplace

2. Configurar la extensión:
   - Abrir configuración de VSCode
   - Buscar "Test Radar"
   - Ajustar configuraciones según necesidades

3. Usar las funcionalidades:
   - Ver tests en el explorador de tests
   - Ejecutar/debuggear tests
   - Ver resultados y análisis
   - Aplicar correcciones sugeridas

## Estructura del Proyecto

```
test-radar/
├── pyproject.toml         # Configuración del proyecto
├── requirements.txt       # Dependencias
├── src/
│   ├── core/             # Funcionalidad central
│   │   ├── config.py     # Configuración
│   │   ├── logger.py     # Sistema de logging
│   │   └── exceptions.py # Manejo de errores
│   ├── scanner/          # Sistema de escaneo
│   ├── executor/         # Ejecución de tests
│   ├── reporter/         # Generación de reportes
│   ├── analyzer/         # Análisis con Claude
│   └── vscode/          # Integración con VSCode
└── tests/               # Tests del propio script
```

## Desarrollo

1. Configurar entorno de desarrollo:
```bash
poetry install --with dev
pre-commit install
```

2. Ejecutar tests:
```bash
poetry run pytest
```

3. Verificar estilo:
```bash
poetry run black .
poetry run isort .
```

## Troubleshooting

### Problemas Comunes con AWS Bedrock

1. Error de autenticación:
   - Verifica tus credenciales de AWS
   - Asegúrate de tener los permisos necesarios
   - Comprueba la región configurada

2. Error de cuota excedida:
   - Revisa tus límites de uso en AWS Bedrock
   - Considera aumentar la cuota si es necesario

3. Error de modelo no disponible:
   - Verifica que el modelo esté disponible en tu región
   - Comprueba el ID del modelo en la configuración

## Contribuir

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/amazing-feature`)
3. Commit cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abrir Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.