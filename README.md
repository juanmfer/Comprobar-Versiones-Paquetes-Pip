# Comprobar versiones de paquetes pip

Este script permite analizar un archivo `requirements.txt` y comprobar:

- Qué versión está instalada en tu entorno.
- La última versión disponible en PyPI.
- Si hay que actualizar la linea: pip install paquete

## Instalación

Clona el repositorio y crea un entorno virtual:

```bash
git clone https://github.com/juanmfer/Comprobar-Versiones-Paquetes-Pip.git
cd Comprobar-Versiones-Paquetes-Pip
python -m venv venv
venv\Scripts\activate

## Instalación de dependencias
Ejecuta:
```bash
pip install -r requirements.txt