#!/usr/bin/env bash
# Script para iniciar a aplicação TechCare com Gunicorn
# Uso: ./start_gunicorn.sh [opções]
#
# Opções:
#   --workers N      Define o número de workers (padrão: 2x núcleos + 1)
#   --host ADDR     Define o endereço para bind (padrão: 127.0.0.1)
#   --port PORT     Define a porta para bind (padrão: 8000)
#   --reload        Ativa o modo de reload automático (para desenvolvimento)
#   --daemon        Executa em modo daemon
#   --log FILE      Local do arquivo de log (padrão: gunicorn.log)
#   --help          Exibe esta ajuda

set -e

# Variáveis padrão
APP_DIR=$(dirname $(dirname $(readlink -f $0)))
WORKERS=$(python -c "import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)")
HOST="127.0.0.1"
PORT="8000"
LOG_FILE="${APP_DIR}/gunicorn.log"
RELOAD=false
DAEMON=false

# Função de ajuda
show_help() {
    grep "^#" "$0" | grep -v "!/usr/bin" | sed "s/^#//"
    exit 0
}

# Análise dos argumentos
while [[ $# -gt 0 ]]; do
    case "$1" in
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --reload)
            RELOAD=true
            shift 1
            ;;
        --daemon)
            DAEMON=true
            shift 1
            ;;
        --log)
            LOG_FILE="$2"
            shift 2
            ;;
        --help)
            show_help
            ;;
        *)
            echo "Opção inválida: $1"
            show_help
            ;;
    esac
done

# Verifica ambiente virtual
if [ -d "${APP_DIR}/venv" ]; then
    source "${APP_DIR}/venv/bin/activate"
elif [ -d "${APP_DIR}/.venv" ]; then
    source "${APP_DIR}/.venv/bin/activate"
else
    echo "Ambiente virtual não encontrado!"
    echo "Crie um ambiente virtual em ${APP_DIR}/venv ou ${APP_DIR}/.venv"
    exit 1
fi

# Verifica se o Gunicorn está instalado
if ! command -v gunicorn &> /dev/null; then
    echo "Gunicorn não está instalado. Instalando..."
    pip install gunicorn
fi

# Prepara opções do Gunicorn
OPTS="-w ${WORKERS} -b ${HOST}:${PORT} --access-logfile ${LOG_FILE}"

# Adiciona opções adicionais
if [ "$RELOAD" = true ]; then
    OPTS="${OPTS} --reload"
fi

if [ "$DAEMON" = true ]; then
    OPTS="${OPTS} --daemon"
fi

# Define variáveis de ambiente para produção
export FLASK_ENV=production
export FLASK_APP="${APP_DIR}/wsgi.py"

# Exibe configuração
echo "Iniciando TechCare com Gunicorn:"
echo " - App: ${APP_DIR}"
echo " - Workers: ${WORKERS}"
echo " - Bind: ${HOST}:${PORT}"
echo " - Log: ${LOG_FILE}"
if [ "$RELOAD" = true ]; then
    echo " - Reload ativado"
fi
if [ "$DAEMON" = true ]; then
    echo " - Modo daemon ativado"
fi

# Inicia o Gunicorn
cd ${APP_DIR}
echo "Comando: gunicorn ${OPTS} wsgi:app"
exec gunicorn ${OPTS} wsgi:app 