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

# Configurar archivos base
echo -e "\n${YELLOW}Configurando archivos base...${NC}"
if [ ! -f "test_config.json" ]; then
    if [ -f "test_config.example.json" ]; then
        cp test_config.example.json test_config.json
        echo -e "${GREEN}Archivo de configuración base creado${NC}"
    else
        echo -e "${RED}No se encontró archivo de configuración ejemplo${NC}"
        exit 1
    fi
fi

# Configurar variables de entorno
echo -e "\n${YELLOW}Configurando variables de entorno...${NC}"
if [ ! -f ".env" ]; then
    if [ ! -f ".env.example" ]; then
        echo -e "${RED}No se encontró archivo .env.example${NC}"
        exit 1
    fi

    cp .env.example .env
    echo -e "${GREEN}Archivo .env creado desde plantilla${NC}"

    # Solicitar credenciales de AWS
    read -p "Ingrese AWS Access Key ID: " aws_access_key
    read -p "Ingrese AWS Secret Access Key: " aws_secret_key
    read -p "Ingrese AWS Region [us-east-1]: " aws_region
    aws_region=${aws_region:-us-east-1}
    read -p "Ingrese Bedrock Model ID [us.anthropic.claude-3-5-sonnet-20241022-v2:0]: " bedrock_model
    bedrock_model=${bedrock_model:-us.anthropic.claude-3-5-sonnet-20241022-v2:0}

    # Actualizar archivo .env
    sed -i "s|your_access_key_here|$aws_access_key|g" .env
    sed -i "s|your_secret_key_here|$aws_secret_key|g" .env
    sed -i "s|us-east-1|$aws_region|g" .env
    sed -i "s|us.anthropic.claude-3-5-sonnet-20241022-v2:0|$bedrock_model|g" .env

    echo -e "${GREEN}Credenciales configuradas en .env${NC}"
fi

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

# Construir imagen Docker
echo -e "\n${YELLOW}Construyendo imagen Docker...${NC}"
docker-compose build

# Instrucciones finales
echo -e "\n${GREEN}Instalación completada!${NC}"
echo -e "\nPara ejecutar el análisis:"
echo -e "1. Asegúrese de tener archivos de test en el directorio test_samples/"
echo -e "2. Ejecute: ${YELLOW}docker-compose up${NC}"
echo -e "\nLos resultados se guardarán en el directorio reports/"

# Preguntar si desea ejecutar el análisis ahora
read -p "¿Desea ejecutar el análisis ahora? (s/N): " run_now
if [[ $run_now =~ ^[Ss]$ ]]; then
    echo -e "\n${YELLOW}Ejecutando análisis...${NC}"
    docker-compose up
fi
