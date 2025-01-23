# Test Radar

Sistema inteligente de análisis y ejecución de pruebas con integración de AWS Bedrock (Claude) para proporcionar análisis avanzado y sugerencias de mejora.

## Características Principales

- Escaneo automático de tests en el proyecto
- Ejecución paralela de tests
- Análisis inteligente usando AWS Bedrock (Claude)
- Generación de reportes detallados
- Sistema de análisis local como respaldo
- Integración con VSCode Test Explorer
- Soporte para múltiples frameworks de prueba
- Dockerizado para fácil instalación y ejecución

## Requisitos

- Docker 20.10 o superior
- Docker Compose 2.0 o superior
- Cuenta AWS con acceso a Bedrock
- Credenciales AWS configuradas

## Instalación Rápida

1. Clonar el repositorio:
```bash
git clone https://github.com/jivagrisma/script-test-radar.git
cd script-test-radar
```

2. Dar permisos de ejecución al script de instalación:
```bash
chmod +x install_and_run.sh
```

3. Ejecutar el script de instalación:
```bash
./install_and_run.sh
```

## Configuración

### Variables de Entorno

Crear archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

Variables principales:
- `AWS_ACCESS_KEY_ID`: ID de clave de acceso AWS
- `AWS_SECRET_ACCESS_KEY`: Clave secreta AWS
- `AWS_REGION`: Región AWS (default: us-east-1)
- `TEST_PARALLEL_JOBS`: Número de jobs paralelos (default: 2)
- `TEST_TIMEOUT`: Timeout en segundos (default: 300)
- `TEST_COVERAGE_TARGET`: Objetivo de cobertura (default: 95.0)
- `LOG_LEVEL`: Nivel de logging (default: INFO)

### Configuración de AWS Bedrock

1. Crear un perfil de inferencia para el modelo `us.anthropic.claude-3-5-sonnet-20241022-v2:0`
2. Actualizar `test_config.json` con las credenciales AWS
3. Configurar variables de entorno en `.env`

## Uso

### Escanear Tests

```bash
./install_and_run.sh scan /path/to/tests
```

Opciones:
- `--pattern`: Patrón para encontrar tests (default: test_*.py)

### Ejecutar Tests

```bash
./install_and_run.sh run /path/to/tests
```

Opciones:
- `--parallel/--no-parallel`: Ejecutar tests en paralelo (default: true)
- `--coverage/--no-coverage`: Recolectar datos de cobertura (default: true)
- `--report`: Guardar reporte en archivo

### Analizar Tests

```bash
./install_and_run.sh analyze /path/to/tests
```

Opciones:
- `--fix/--no-fix`: Aplicar correcciones automáticamente (default: false)

## Estructura del Proyecto

```
test-radar/
├── src/                # Código fuente
│   ├── analyzer/      # Análisis con AWS Bedrock
│   ├── core/          # Funcionalidad core
│   ├── executor/      # Ejecución de tests
│   ├── reporter/      # Generación de reportes
│   └── scanner/       # Detección de tests
├── tests/             # Tests del proyecto
├── Dockerfile         # Configuración de Docker
├── docker-compose.yml # Orquestación de servicios
├── install_and_run.sh # Script de instalación y ejecución
├── pyproject.toml     # Configuración del proyecto
├── requirements.txt   # Dependencias
└── test_config.json  # Configuración principal
```

## Desarrollo con Docker

### Construir la imagen

```bash
docker-compose build
```

### Ejecutar tests en contenedor

```bash
docker-compose run --rm test-radar run /path/to/tests
```

### Ver logs

```bash
docker-compose logs -f
```

### Limpiar contenedores y volúmenes

```bash
docker-compose down -v
```

## Troubleshooting

### Problemas Comunes con Docker

1. Error de permisos:
```
Got permission denied while trying to connect to the Docker daemon socket
```
Solución:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

2. Error de memoria:
```
Killed
```
Solución: Aumentar memoria en Docker Desktop settings

### Problemas con AWS Bedrock

1. Error de autenticación:
```
BedRockError: Access denied
```
Solución:
- Verificar credenciales en .env
- Confirmar permisos IAM
- Verificar región AWS

2. Error de modelo:
```
BedRockError: Model not found
```
Solución:
- Verificar ID del modelo
- Confirmar acceso al modelo en Bedrock

## Contribuir

1. Fork el repositorio
2. Crear rama para feature (`git checkout -b feature/amazing-feature`)
3. Commit cambios (`git commit -m 'feat: add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abrir Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.
