#!/bin/bash
# Hermes Configuration Backup Script
# Automated backup of Hermes Agent configuration files

set -euo pipefail

# Configuration
HERMES_HOME="${HOME}/.hermes"
BACKUP_BASE="~/ENV/temp"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/tmp/hermes_backup_${TIMESTAMP}"
BACKUP_FILE="${BACKUP_BASE}/hermes_config_${TIMESTAMP}.zip"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Error handling
cleanup() {
    if [[ -d "${BACKUP_DIR}" ]]; then
        log "Cleaning up temporary directory: ${BACKUP_DIR}"
        rm -rf "${BACKUP_DIR}"
    fi
}
trap cleanup EXIT

# Main backup procedure
main() {
    log "Starting Hermes configuration backup"
    
    # Verify Hermes home exists
    if [[ ! -d "${HERMES_HOME}" ]]; then
        log "ERROR: Hermes home directory not found: ${HERMES_HOME}"
        exit 1
    fi
    
    # Create backup directories
    log "Creating backup directories"
    mkdir -p "${BACKUP_BASE}"
    mkdir -p "${BACKUP_DIR}"
    
    # Copy configuration files
    log "Copying configuration files"
    cp "${HERMES_HOME}/config.yaml" "${BACKUP_DIR}/"
    cp "${HERMES_HOME}/.env" "${BACKUP_DIR}/"
    
    # Create zip archive
    log "Creating backup archive: ${BACKUP_FILE}"
    cd "${BACKUP_DIR}" && zip -r "${BACKUP_FILE}" config.yaml .env
    
    # Verify backup
    log "Verifying backup contents"
    unzip -l "${BACKUP_FILE}"
    
    log "Backup completed successfully: ${BACKUP_FILE}"
    log "Backup size: $(du -h "${BACKUP_FILE}" | cut -f1)"
}

# Run main procedure
main "$@"