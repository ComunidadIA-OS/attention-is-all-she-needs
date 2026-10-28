#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Runner inteligente de pruebas unitarias para AIASN.

Detecta automáticamente el entorno de la máquina:
1. Si Docker está activo, ejecuta los tests dentro del contenedor backend aislado.
2. Si Docker no está disponible, conmuta automáticamente a 'uv run pytest'.
3. Si uv no está disponible, ejecuta con el Python activo y proporciona ayuda clara si faltan dependencias.
4. Si Node.js está disponible, ejecuta también los tests del frontend piloto.
"""

import shutil
import subprocess
import sys


def docker_ready() -> bool:
    """Verifica si docker está en PATH y el daemon responde."""
    if not shutil.which("docker"):
        return False
    try:
        r = subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3,
        )
        return r.returncode == 0
    except Exception:
        return False


def uv_ready() -> bool:
    """Verifica si el gestor uv está instalado."""
    return shutil.which("uv") is not None


def node_ready() -> bool:
    """Verifica si Node.js está instalado."""
    return shutil.which("node") is not None


def run_tests():
    extra_args = sys.argv[1:] or ["tests/", "-v"]
    backend_ok = False

    print("=" * 65)
    print("  AIASN -- Suite Unificada de Verificación y Calidad")
    print("=" * 65)

    if docker_ready():
        print("\n[AIASN] -> Docker detectado y activo. Ejecutando tests en contenedor...")
        cmd = ["docker", "compose", "run", "--rm", "backend", "pytest"] + extra_args
        ret = subprocess.call(cmd)
        backend_ok = (ret == 0)
    elif uv_ready():
        print("\n[AIASN] -> Docker no activo. Conmutando automáticamente a 'uv run pytest'...")
        cmd = ["uv", "run", "pytest"] + extra_args
        ret = subprocess.call(cmd)
        backend_ok = (ret == 0)
    else:
        print("\n[AIASN] -> Conmutando a ejecución con el Python activo...")
        cmd = [sys.executable, "-m", "pytest"] + extra_args
        ret = subprocess.call(cmd)
        backend_ok = (ret == 0)
        if not backend_ok:
            print("\n[AIASN Ayuda] Si faltan dependencias del entorno:")
            print("  1. Inicia Docker Desktop (para ejecución en contenedor sin configurar nada)")
            print("  2. O instala el entorno del proyecto: pip install -e \".[dev]\"")
            print("  3. O usa uv: uv sync && uv run pytest")

    # Tests de frontend piloto (si node está instalado)
    if node_ready():
        print("\n" + "-" * 65)
        print("[AIASN] -> Ejecutando tests de frontend-piloto (Node.js)...")
        node_cmd = ["node", "frontend-piloto/tests/run.mjs"]
        node_ret = subprocess.call(node_cmd)
        if node_ret == 0 and backend_ok:
            print("\n[AIASN] -> Todo verificado con éxito: Backend + Frontend 100% operativos.")
        return 0 if (backend_ok and node_ret == 0) else 1

    return 0 if backend_ok else 1


if __name__ == "__main__":
    sys.exit(run_tests())

