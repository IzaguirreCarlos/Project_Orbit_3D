#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║   ProjectForge 3D — Abrir en VSCode desde WSL               ║
# ║   Ejecutar en WSL Ubuntu:  bash open_in_vscode.sh           ║
# ╚══════════════════════════════════════════════════════════════╝

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "🚀 ProjectForge 3D — Abriendo en VSCode..."
echo "📁 Ruta WSL: $PROJECT_DIR"

# Convertir ruta WSL a Windows para code.cmd
WIN_PATH=$(wslpath -m "$PROJECT_DIR")
echo "📁 Ruta Windows: $WIN_PATH"

# Intento 1: code directamente (si está en PATH)
if command -v code &>/dev/null; then
  echo "✓ Usando 'code' del PATH"
  code "$PROJECT_DIR"
  exit 0
fi

# Intento 2: code.cmd vía Windows
CODE_CMD="/mnt/c/Users/$USER/AppData/Local/Programs/Microsoft VS Code/bin/code"
if [ -f "$CODE_CMD" ]; then
  echo "✓ Usando VSCode de AppData"
  "$CODE_CMD" "$WIN_PATH"
  exit 0
fi

# Intento 3: buscar code.cmd en rutas comunes
for path in \
  "/mnt/c/Program Files/Microsoft VS Code/bin/code" \
  "/mnt/c/Program Files (x86)/Microsoft VS Code/bin/code"; do
  if [ -f "$path" ]; then
    echo "✓ Encontrado en: $path"
    "$path" "$WIN_PATH"
    exit 0
  fi
done

# Si nada funciona, imprimir instrucciones
echo ""
echo "⚠️  No se encontró VSCode en el PATH."
echo ""
echo "Opciones:"
echo "  1. Desde PowerShell/CMD de Windows:"
echo "     code \\\\wsl.localhost\\ubuntu-24.04\\home\\$(whoami)\\Project_Orbit_3D\\Project_Orbit_3D"
echo ""
echo "  2. Desde VSCode: File → Open Folder → pegar la ruta:"
echo "     $WIN_PATH"
echo ""
echo "  3. Instala el WSL extension en VSCode y ejecuta:"
echo "     code $PROJECT_DIR"
