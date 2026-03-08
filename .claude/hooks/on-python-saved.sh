#!/usr/bin/env bash
# Hook PostToolUse (Write + Edit) — qualité Python
# Lance ruff, mypy et bandit après toute écriture de fichier .py
# Sort avec le code d'erreur cumulé (0 = tout OK)

input=$(cat)
file_path=$(echo "$input" | python -c \
  "import sys,json; \
   print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" \
  2>/dev/null)

if [[ -z "$file_path" ]]; then
  exit 0
fi

if [[ "$file_path" != *.py ]]; then
  exit 0
fi

exit_code=0

echo "--- ruff: $file_path ---"
poetry run ruff check --fix "$file_path" 2>&1 || exit_code=1
poetry run ruff format "$file_path" 2>&1 || exit_code=1

if [[ -d "src/" ]]; then
  echo "--- mypy: src/ ---"
  poetry run mypy src/ 2>&1 || exit_code=1

  echo "--- bandit: src/ ---"
  poetry run bandit -r src/ -q 2>&1 || exit_code=1
fi

exit $exit_code
