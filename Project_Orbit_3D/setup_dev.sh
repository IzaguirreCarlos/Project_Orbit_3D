#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║   ProjectForge 3D — Setup & VSCode Dev Script               ║
# ║   Ejecutar en WSL Ubuntu:  bash setup_dev.sh                ║
# ╚══════════════════════════════════════════════════════════════╝

set -e  # salir ante cualquier error

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

echo ""
echo -e "${CYAN}${BOLD}"
echo "  ██████╗ ██████╗  ██████╗      ██╗███████╗ ██████╗████████╗"
echo "  ██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝██╔════╝╚══██╔══╝"
echo "  ██████╔╝██████╔╝██║   ██║     ██║█████╗  ██║        ██║   "
echo "  ██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝  ██║        ██║   "
echo "  ██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗╚██████╗   ██║   "
echo "  ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝  "
echo -e "${NC}"
echo -e "${BOLD}  ProjectForge 3D — Enterprise Project Management Platform${NC}"
echo -e "  ${BLUE}${PROJECT_DIR}${NC}"
echo ""

# ─── 1. Check Python ──────────────────────────────────────────
echo -e "${YELLOW}[1/8]${NC} Verificando Python..."
if ! command -v python3 &>/dev/null; then
  echo -e "${RED}❌ Python 3 no encontrado. Instala con: sudo apt install python3 python3-pip${NC}"
  exit 1
fi
PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "${GREEN}✓ Python ${PYTHON_VER} encontrado${NC}"

# ─── 2. Virtual Environment ───────────────────────────────────
echo -e "${YELLOW}[2/8]${NC} Configurando entorno virtual..."
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
  echo -e "${GREEN}✓ Virtualenv creado en .venv${NC}"
else
  echo -e "${GREEN}✓ Virtualenv ya existe${NC}"
fi
source "$VENV_DIR/bin/activate"

# ─── 3. Install Dependencies ──────────────────────────────────
echo -e "${YELLOW}[3/8]${NC} Instalando dependencias Python..."
pip install --quiet --upgrade pip
pip install --quiet -r "$PROJECT_DIR/requirements.txt"
echo -e "${GREEN}✓ Dependencias instaladas${NC}"

# ─── 4. .env file ─────────────────────────────────────────────
echo -e "${YELLOW}[4/8]${NC} Configurando variables de entorno..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
  cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
  # Generate a random secret key
  SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
  sed -i "s/your-super-secret-key-change-in-production/$SECRET/" "$PROJECT_DIR/.env"
  # Use SQLite for local dev (no Docker needed)
  sed -i "s|DATABASE_URL=postgres://.*|DATABASE_URL=sqlite:///db.sqlite3|" "$PROJECT_DIR/.env"
  echo -e "${GREEN}✓ .env creado (con SQLite para dev local)${NC}"
else
  echo -e "${GREEN}✓ .env ya existe${NC}"
fi

# ─── 5. Database Migrations ───────────────────────────────────
echo -e "${YELLOW}[5/8]${NC} Ejecutando migraciones..."
cd "$PROJECT_DIR"
python manage.py makemigrations --settings=config.settings.development 2>/dev/null || true
python manage.py migrate --settings=config.settings.development
echo -e "${GREEN}✓ Base de datos lista${NC}"

# ─── 6. Seed initial data ─────────────────────────────────────
echo -e "${YELLOW}[6/8]${NC} Cargando datos iniciales (roles)..."
python manage.py shell --settings=config.settings.development << 'EOF'
from apps.accounts.models import Role
roles = ['CEO','CTO','Project Manager','Scrum Master','Team Lead',
         'Backend Developer','Frontend Developer','QA Engineer',
         'UI/UX Designer','DevOps Engineer','Client']
for r in roles:
    Role.objects.get_or_create(name=r)
print(f"✓ {len(roles)} roles creados/verificados")
EOF
echo -e "${GREEN}✓ Roles iniciales creados${NC}"

# ─── 7. Create superuser ──────────────────────────────────────
echo -e "${YELLOW}[7/8]${NC} Creando superusuario admin..."
python manage.py shell --settings=config.settings.development << 'EOF'
from apps.accounts.models import User
if not User.objects.filter(email='admin@projectforge.dev').exists():
    u = User.objects.create_superuser(
        email='admin@projectforge.dev',
        password='Admin1234!',
        first_name='Admin',
        last_name='ProjectForge',
    )
    print(f"✓ Superusuario creado: admin@projectforge.dev / Admin1234!")
else:
    print("✓ Superusuario ya existe: admin@projectforge.dev")
EOF

# ─── 8. Static files ──────────────────────────────────────────
echo -e "${YELLOW}[8/8]${NC} Recopilando archivos estáticos..."
mkdir -p "$PROJECT_DIR/static" "$PROJECT_DIR/staticfiles" "$PROJECT_DIR/media"
python manage.py collectstatic --no-input --settings=config.settings.development 2>/dev/null || true
echo -e "${GREEN}✓ Archivos estáticos listos${NC}"

# ─── Summary ──────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║            ✅ SETUP COMPLETADO                       ║${NC}"
echo -e "${GREEN}${BOLD}╠══════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}${BOLD}║${NC}  Iniciar servidor:                                   ${GREEN}${BOLD}║${NC}"
echo -e "${GREEN}${BOLD}║${NC}    ${CYAN}source .venv/bin/activate${NC}                         ${GREEN}${BOLD}║${NC}"
echo -e "${GREEN}${BOLD}║${NC}    ${CYAN}python manage.py runserver 8008${NC}                        ${GREEN}${BOLD}║${NC}"
echo -e "${GREEN}${BOLD}║${NC}                                                      ${GREEN}${BOLD}║${NC}"
echo -e "${GREEN}${BOLD}║${NC}  URLs:                                               ${GREEN}${BOLD}║${NC}"
echo -e "${GREEN}${BOLD}║${NC}    App:    ${CYAN}http://localhost:8008${NC}                     ${GREEN}${BOLD}║${NC}"
echo -e "${GREEN}${BOLD}║${NC}    Admin:  ${CYAN}http://localhost:8008/admin${NC}               ${GREEN}${BOLD}║${NC}"
echo -e "${GREEN}${BOLD}║${NC}    Docs:   ${CYAN}http://localhost:8008/api/docs${NC}            ${GREEN}${BOLD}║${NC}"
echo -e "${GREEN}${BOLD}║${NC}                                                      ${GREEN}${BOLD}║${NC}"
echo -e "${GREEN}${BOLD}║${NC}  Credenciales:                                       ${GREEN}${BOLD}║${NC}"
echo -e "${GREEN}${BOLD}║${NC}    Email:    ${CYAN}admin@projectforge.dev${NC}                  ${GREEN}${BOLD}║${NC}"
echo -e "${GREEN}${BOLD}║${NC}    Password: ${CYAN}Admin1234!${NC}                              ${GREEN}${BOLD}║${NC}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${YELLOW}Para Docker completo (con Redis + Celery):${NC}"
echo -e "  ${CYAN}docker-compose up --build${NC}"
echo ""

# ─── Auto-open VSCode ─────────────────────────────────────────
if command -v code &>/dev/null; then
  echo -e "${BLUE}Abriendo en VSCode...${NC}"
  code "$PROJECT_DIR"
else
  echo -e "${YELLOW}VSCode CLI no encontrado. Abre manualmente:${NC}"
  echo -e "  ${CYAN}code $(wslpath -m "$PROJECT_DIR")${NC}"
fi
