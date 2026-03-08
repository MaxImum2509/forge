#!/usr/bin/env bash
# Hook PostToolUse (Write) — rappelle d'enregistrer les nouveaux scripts dans scripts.db
# Lit le JSON stdin pour extraire tool_input.file_path
# Exit 0 dans tous les cas (ne bloque jamais)

input=$(cat)
file_path=$(echo "$input" | python -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)

if [[ "$file_path" == */scripts/* ]]; then
  echo "RAPPEL : le fichier '$file_path' est dans scripts/. Pensez à l'enregistrer dans scripts.db via scripts-index."
fi

exit 0
