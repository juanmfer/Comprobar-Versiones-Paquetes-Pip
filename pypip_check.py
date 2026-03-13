"""
Script para comparar versiones de paquetes Python entre un archivo requirements
y la última versión disponible en PyPI, mostrando también la versión instalada.
Ejemplo Windows: python check_requirements.py C:\proyecto\requirements.txt
"""

import sys
import subprocess
import requests
import time
import random
from collections import namedtuple
import colorama
from colorama import Fore, Style
colorama.init(autoreset=True)  # autoreset evita tener que poner RESET cada vez


# primero packaging sino pkg_resources
try:
    from packaging.requirements import Requirement
    from packaging.version import parse as parse_version
    USA_PACKAGING = True
except ImportError:
    import pkg_resources
    USA_PACKAGING = False


# Definir colores (colorama)
COLOR_OK = Fore.GREEN
COLOR_WARNING = Fore.YELLOW
COLOR_ERROR = Fore.RED
COLOR_RESET = Style.RESET_ALL
COLOR_BOLD = Style.BRIGHT
COLOR_CYAN = Fore.CYAN

InfoPaquete = namedtuple('PackageInfo', ['nombre', 'requiere_spec', 'linea'])

def analizar_linea(linea):
    """Extrae nombre y especificación de una línea de requirements."""
    linea = linea.strip()
    if not linea or linea.startswith('#'):
        return None

    # Quitar comentarios al final
    if '#' in linea:
        linea = linea[:linea.index('#')].strip()

    if USA_PACKAGING:
        try:
            req = Requirement(linea)
            return InfoPaquete(req.nombre, str(req.specifier), linea)
        except Exception:
            # Fallback: línea no válida según packaging, intentar método simple
            pass

    # Método simple con pkg_resources o split manual
    try:
        if USA_PACKAGING:
            # Si packaging falla se usa pkg_resources
            req = pkg_resources.Requirement.parse(linea)
            especificaciones = ','.join(f"{op}{v}" for op, v in req.specs)
            return InfoPaquete(req.project_name, especificaciones, linea)
        else:
            req = pkg_resources.Requirement.parse(linea)
            especificaciones = ','.join(f"{op}{v}" for op, v in req.specs)
            return InfoPaquete(req.project_name, especificaciones, linea)
    except Exception:
        # Separar por operadores comunes
        import re
        operadores = r'==|>=|<=|>|<|~=|!='
        partes = re.split(f'({operadores})', linea, maxsplit=1)
        if len(partes) >= 2:
            nombre = partes[0].strip()
            op = partes[1].strip()
            version = partes[2].strip() if len(partes) > 2 else ''
            return InfoPaquete(nombre, f"{op}{version}", linea)
        else:
            # Sin especificador
            return InfoPaquete(nombre, '', linea)

def comprobar_version_instalada(package_name):
    """Devuelve la versión instalada del paquete o None."""
    try:
        if USA_PACKAGING:
            # Usar importlib.metadata si está disponible - Python 3.8+
            try:
                from importlib.metadata import version
                return version(package_name)
            except ImportError:
                # Fallback a pkg_resources
                return pkg_resources.get_distribution(package_name).version
        else:
            return pkg_resources.get_distribution(package_name).version
    except Exception:
        return None

def comprobar_paquete(package_info):
    """Consulta PyPI y muestra la información del paquete."""
    nombre = package_info.nombre
    requerida = package_info.requiere_spec
    instalado = comprobar_version_instalada(nombre)

    try:
        url = f"https://pypi.org/pypi/{nombre}/json"
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"{COLOR_ERROR} {nombre}: no encontrado en PyPI{COLOR_RESET}")
            return

        datos = resp.json()
        ultima = datos["info"]["version"]

        # Línea de salida
        salida = []
        salida.append(f"{COLOR_BOLD}{COLOR_CYAN}  {nombre}{COLOR_RESET}")

        if requerida:
            salida.append(f"  Requerida: {COLOR_WARNING}{requerida}{COLOR_RESET}")
        else:
            salida.append(f"  Requerida: {COLOR_WARNING}(sin versión específica){COLOR_RESET}")

        salida.append(f"  PyPI última: {COLOR_OK}{ultima}{COLOR_RESET}")

        if instalado:
            salida.append(f"  Instalada: {COLOR_OK if instalado == ultima else COLOR_WARNING}{instalado}{COLOR_RESET}")
        else:
            salida.append(f"  Instalada: {COLOR_ERROR}(no instalada){COLOR_RESET}")

        # Sugerencia según versión
        if instalado and ultima != instalado:
            salida.append(f"  Sugerencia: pip install --upgrade {nombre}")
        elif not instalado and requerida:
            salida.append(f"  Sugerencia: pip install {nombre}{requerida}")

        print('\n'.join(salida))
        print()

    except requests.exceptions.RequestException as e:
        print(f"{COLOR_ERROR}Error de red al consultar {nombre}: {e}{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_ERROR}Error procesando {nombre}: {e}{COLOR_RESET}")

def main():
    # Determinar archivo de requisitos
    if len(sys.argv) > 1:
        req_archivo = sys.argv[1]
    else:
        req_archivo = "requirements.txt"
        print(f"{COLOR_WARNING}No se especificó archivo, usando '{req_archivo}' por defecto.{COLOR_RESET}\n")

    try:
        with open(req_archivo, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"{COLOR_ERROR}Archivo no encontrado: {req_archivo}{COLOR_RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{COLOR_ERROR}Error al leer archivo: {e}{COLOR_RESET}")
        sys.exit(1)

    paquetes = []
    for line in lines:
        pkg_info = analizar_linea(line)
        if pkg_info:
            paquetes.append(pkg_info)

    if not paquetes:
        print(f"{COLOR_WARNING}  No se encontraron paquetes válidos en {req_archivo}{COLOR_RESET}")
        return

    print(f"{COLOR_BOLD}  Analizando {len(paquetes)} paquetes desde {req_archivo}...{COLOR_RESET}\n")

    for pkg in paquetes:
        comprobar_paquete(pkg)
        # comprobacion de 1 a 3 para saltar limiter
        time.sleep(random.uniform(1, 3))

if __name__ == "__main__":
    main()