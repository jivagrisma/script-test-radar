# Test Radar

Sistema automatizado de análisis y ejecución de pruebas con capacidades de análisis avanzado mediante AWS Bedrock.

## Características Implementadas

- Escaneo automático de tests en el proyecto
- Ejecución paralela de tests
- Generación de reportes detallados
- Sistema de análisis local como respaldo
- Manejo de errores robusto
- Reportes en formato HTML y JSON

## Resultados de la Prueba Inicial

- Se detectaron 12 tests en el proyecto API-H2H
- Se identificaron problemas en la ejecución de los tests
- Se generaron sugerencias de mejora básicas
- Se guardaron reportes en el directorio `reports/`

## Configuración

1. Clona el repositorio:
```bash
git clone https://github.com/jivagrisma/script-test-radar.git
cd script-test-radar
```

2. Copia el archivo de configuración de ejemplo:
```bash
cp test_config.example.json test_config.json
```

3. Instala las dependencias:
```bash
./setup.sh
```

## Configuración de AWS Bedrock

Para utilizar el análisis avanzado con Claude, necesitarás:

1. Acceder a la consola de AWS Bedrock
2. Crear un perfil de inferencia para el modelo `anthropic.claude-3-5-sonnet-20241022-v2:0`
3. Configurar el throughput según tus necesidades
4. Actualizar `test_config.json` con:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Region
   - ARN del perfil de inferencia

## Próximos Pasos

### Configuración de AWS Bedrock
- [ ] Crear un perfil de inferencia para el modelo Claude
- [ ] Configurar el throughput adecuado
- [ ] Actualizar la configuración con el ARN del perfil

### Mejoras en el Análisis
- [ ] Implementar análisis de cobertura detallado
- [ ] Mejorar el análisis local con más heurísticas
- [ ] Añadir detección de patrones comunes de error

### Integración con VSCode
- [ ] Implementar la extensión VSCode
- [ ] Añadir decoradores visuales
- [ ] Integrar con el debugger

### Documentación
- [ ] Crear guía de usuario detallada
- [ ] Documentar la API
- [ ] Añadir ejemplos de uso

## Uso

```bash
# Ejecutar análisis de tests
python test_run.py

# Ver reportes generados
open reports/test_report.html
```

## Estructura del Proyecto

```
test-radar/
├── src/
│   ├── analyzer/      # Análisis de tests
│   ├── scanner/       # Escaneo de tests
│   ├── executor/      # Ejecución de tests
│   ├── reporter/      # Generación de reportes
│   └── core/          # Funcionalidades core
├── reports/           # Reportes generados
└── test_config.json   # Configuración (no incluido en git)
```

## Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'feat: add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.