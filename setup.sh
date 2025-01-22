#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Configurando Test Radar...${NC}"

# Verificar Python 3.11
echo -e "\n${BLUE}📋 Verificando versión de Python...${NC}"
if command -v python3.11 &>/dev/null; then
    echo -e "${GREEN}✓ Python 3.11 encontrado${NC}"
else
    echo -e "${RED}✗ Python 3.11 no encontrado. Por favor, instálalo primero.${NC}"
    exit 1
fi

# Verificar Poetry
echo -e "\n${BLUE}📋 Verificando Poetry...${NC}"
if command -v poetry &>/dev/null; then
    echo -e "${GREEN}✓ Poetry encontrado${NC}"
else
    echo -e "${BLUE}⚙️ Instalando Poetry...${NC}"
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Crear entorno virtual y instalar dependencias
echo -e "\n${BLUE}📦 Instalando dependencias...${NC}"
poetry install

# Crear directorios necesarios
echo -e "\n${BLUE}📁 Creando directorios...${NC}"
mkdir -p .cache reports

# Verificar credenciales AWS
echo -e "\n${BLUE}🔑 Verificando credenciales AWS...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ Archivo .env encontrado${NC}"
else
    echo -e "${BLUE}⚙️ Creando archivo .env...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Archivo .env creado. Por favor, configura tus credenciales.${NC}"
fi

# Verificar configuración
echo -e "\n${BLUE}⚙️ Verificando configuración...${NC}"
if [ -f "test_config.json" ]; then
    echo -e "${GREEN}✓ Archivo de configuración encontrado${NC}"
else
    echo -e "${RED}✗ Archivo test_config.json no encontrado${NC}"
    exit 1
fi

echo -e "\n${GREEN}✨ Configuración completada${NC}"
echo -e "\n${BLUE}Para ejecutar la prueba:${NC}"
echo -e "poetry run python test_run.py"