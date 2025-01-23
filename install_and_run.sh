#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Iniciando instalación de Test Radar...${NC}"

# Verificar Docker
echo -e "\n${YELLOW}Verificando instalación de Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker no está instalado. Por favor, instale Docker primero.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose no está instalado. Por favor, instale Docker Compose primero.${NC}"
    exit 1
fi

# Crear directorios necesarios
echo -e "\n${YELLOW}Creando directorios...${NC}"
mkdir -p reports .cache test_samples

# Verificar credenciales de AWS
echo -e "\n${YELLOW}Verificando credenciales de AWS...${NC}"
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo -e "${YELLOW}No se encontraron credenciales de AWS en el entorno.${NC}"

    # Solicitar credenciales
    read -p "Ingrese AWS Access Key ID: " aws_access_key
    read -p "Ingrese AWS Secret Access Key: " aws_secret_key
    read -p "Ingrese AWS Region [us-east-1]: " aws_region
    aws_region=${aws_region:-us-east-1}

    # Crear archivo .env
    echo "AWS_ACCESS_KEY_ID=$aws_access_key" > .env
    echo "AWS_SECRET_ACCESS_KEY=$aws_secret_key" >> .env
    echo "AWS_REGION=$aws_region" >> .env

    echo -e "${GREEN}Credenciales guardadas en .env${NC}"
fi

# Verificar archivo de configuración
echo -e "\n${YELLOW}Verificando archivo de configuración...${NC}"
if [ ! -f "test_config.json" ]; then
    if [ -f "test_config.example.json" ]; then
        cp test_config.example.json test_config.json
        echo -e "${GREEN}Archivo de configuración creado desde ejemplo${NC}"
    else
        echo -e "${RED}No se encontró archivo de configuración ejemplo${NC}"
        exit 1
    fi
fi

# Construir imagen Docker
echo -e "\n${YELLOW}Construyendo imagen Docker...${NC}"
docker-compose build

# Verificar directorio de tests
echo -e "\n${YELLOW}Verificando directorio de tests...${NC}"
if [ ! -d "test_samples" ] || [ -z "$(ls -A test_samples)" ]; then
    echo -e "${YELLOW}No se encontraron archivos de test en test_samples.${NC}"
    echo -e "Por favor, coloque sus archivos de test en el directorio test_samples/"
    echo -e "Ejemplo de estructura:"
    echo -e "test_samples/"
    echo -e "  ├── test_calculator.py"
    echo -e "  └── test_api.py"
fi

# Instrucciones finales
echo -e "\n${GREEN}Instalación completada!${NC}"
echo -e "\nPara ejecutar el análisis:"
echo -e "1. Coloque sus archivos de test en el directorio test_samples/"
echo -e "2. Ejecute: ${YELLOW}docker-compose up${NC}"
echo -e "\nLos resultados se guardarán en el directorio reports/"

# Preguntar si desea ejecutar el análisis ahora
read -p "¿Desea ejecutar el análisis ahora? (s/N): " run_now
if [[ $run_now =~ ^[Ss]$ ]]; then
    echo -e "\n${YELLOW}Ejecutando análisis...${NC}"
    docker-compose up
fi
