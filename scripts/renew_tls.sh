#!/usr/bin/env bash
set -euo pipefail

# Automated TLS renewal helper for Lucy World
#
# This script wraps certbot renewal with a reload hook for Nginx (and the
# Gunicorn service if configured). It is designed to run from cron or a
# systemd timer. Usage:
#
#   sudo ./scripts/renew_tls.sh --domain lucy.world
#   sudo ./scripts/renew_tls.sh --domain lucy.world --dry-run
#
# Options can also be customised via environment variables:
#   CERTBOT_BIN - path to the certbot executable (default: /usr/bin/certbot)
#   NGINX_SERVICE - systemd unit to reload after renewal (default: nginx)
#   GUNICORN_SERVICE - systemd unit to reload after renewal (default: lucy-world-search)

CERTBOT_BIN="${CERTBOT_BIN:-/usr/bin/certbot}"
NGINX_SERVICE="${NGINX_SERVICE:-nginx}"
GUNICORN_SERVICE="${GUNICORN_SERVICE:-lucy-world-search}"
DOMAIN="lucy.world"
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: renew_tls.sh [options]

Options:
  --domain <domain>     Certificate name/domain to renew (default: lucy.world)
  --dry-run             Perform a certbot dry run
  --help                Show this message

Environment variables:
  CERTBOT_BIN           Path to certbot executable (default: /usr/bin/certbot)
  NGINX_SERVICE         systemd service to reload after renewal (default: nginx)
  GUNICORN_SERVICE      systemd service to reload after renewal (default: lucy-world-search)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domain)
      [[ $# -lt 2 ]] && { echo "Missing value for --domain" >&2; exit 1; }
      DOMAIN="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo is required to run certbot and reload services" >&2
  exit 1
fi

if [[ ! -x "$CERTBOT_BIN" ]]; then
  echo "certbot binary not found at $CERTBOT_BIN" >&2
  exit 1
fi

RELOAD_COMMANDS=("systemctl reload $NGINX_SERVICE")
if [[ -n "$GUNICORN_SERVICE" ]]; then
  RELOAD_COMMANDS+=("systemctl reload $GUNICORN_SERVICE")
fi

DEPLOY_HOOK=$(IFS='; '; echo "${RELOAD_COMMANDS[*]}")

CERTBOT_ARGS=(renew "--cert-name" "$DOMAIN" "--deploy-hook" "$DEPLOY_HOOK" "--quiet")
if (( DRY_RUN )); then
  CERTBOT_ARGS+=("--dry-run")
fi

sudo "$CERTBOT_BIN" "${CERTBOT_ARGS[@]}"

printf 'TLS renewal complete for %s (dry run: %s)\n' "$DOMAIN" "$DRY_RUN"
