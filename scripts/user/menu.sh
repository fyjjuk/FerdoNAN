#!/bin/bash
echo "=== Utilidades de FerdoNAN ==="
echo "1. Backup del proyecto"
echo "2. Ver logs en tiempo real"
echo "3. Health check"
echo "4. Buscar archivos duplicados"
echo "5. Mapear estructura del proyecto"
echo "6. Exportar proyecto completo a un solo archivo"
echo "0. Salir"
read -p "Opción: " opt

case $opt in
    1) python scripts/user/backup_cli.py crear ;;
    2) python scripts/user/logs_tail.py ;;
    3) python scripts/diagnostic/check_health.py ;;
    4) python scripts/diagnostic/find_duplicates.py ;;
    5) python scripts/diagnostic/audit_project.py ;;
    6) python scripts/user/export_project.py ;;
    0) exit ;;
    *) echo "Opción inválida" ;;
esac
