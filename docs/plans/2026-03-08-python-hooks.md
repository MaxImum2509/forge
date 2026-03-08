# Python Hooks Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans
> to implement this plan task-by-task.

**Goal:** Mettre en place les hooks Claude Code pour la qualité Python
automatique (ruff + mypy + bandit) sur Write/Edit, corriger le pattern
de l'hook scripts-index, et documenter les sous-agents dans CLAUDE.md.

**Architecture:** Deux scripts PostToolUse indépendants (SRP) — l'un
dédié à la qualité Python, l'autre à l'indexation scripts.db. Le
settings.json orchestre les déclencheurs. Pas de TDD pour les scripts
shell : vérification par exécution directe.

**Tech Stack:** bash, Claude Code hooks (PostToolUse), ruff, mypy,
bandit, poetry.

---

### Task 1 : Corriger `on-script-created.sh`

**Files:**
- Modify: `.claude/hooks/on-script-created.sh`

**Step 1 : Lire le fichier existant**

```bash
cat .claude/hooks/on-script-created.sh
```

**Step 2 : Corriger le pattern glob**

Remplacer les deux conditions :

```bash
# Avant
if [[ "$file_path" == *scripts/*.py ]] \
   || [[ "$file_path" == *scripts\\*.py ]]; then

# Après — couvre tous les niveaux de sous-répertoires
if [[ "$file_path" == */scripts/* ]]; then
```

**Step 3 : Vérifier le rendu**

```bash
cat .claude/hooks/on-script-created.sh
```

Expected : une seule condition `*/scripts/*`, pas de `*.py`
spécifique (le rappel s'applique à tout fichier sous scripts/).

---

### Task 2 : Créer `on-python-saved.sh`

**Files:**
- Create: `.claude/hooks/on-python-saved.sh`

**Step 1 : Créer le script**

```bash
#!/usr/bin/env bash
# Hook PostToolUse (Write + Edit) — qualite Python
# Lance ruff, mypy et bandit apres toute ecriture de fichier .py
# Sort avec le code d'erreur cumule (0 = tout OK)

input=$(cat)
file_path=$(echo "$input" | python -c \
  "import sys,json; \
   print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" \
  2>/dev/null)

if [[ "$file_path" != *.py ]]; then
  exit 0
fi

exit_code=0

echo "--- ruff: $file_path ---"
poetry run ruff check --fix "$file_path" 2>&1 || exit_code=1
poetry run ruff format "$file_path" 2>&1

echo "--- mypy: src/ ---"
poetry run mypy src/ 2>&1 || exit_code=1

echo "--- bandit: src/ ---"
poetry run bandit -r src/ -q 2>&1 || exit_code=1

exit $exit_code
```

**Step 2 : Rendre le script exécutable**

```bash
chmod +x .claude/hooks/on-python-saved.sh
```

**Step 3 : Vérifier l'exécution directe sur un fichier existant**

```bash
echo '{"tool_input": {"file_path": "src/tooling/scripts_index.py"}}' \
  | bash .claude/hooks/on-python-saved.sh
```

Expected : sortie ruff (All checks passed), mypy (Success), bandit
(No issues identified), exit code 0.

---

### Task 3 : Mettre à jour `settings.json`

**Files:**
- Modify: `.claude/settings.json`

**Step 1 : Lire le fichier existant**

```bash
cat .claude/settings.json
```

**Step 2 : Ajouter les deux nouveaux hooks**

Structure cible de `PostToolUse` :

```json
"PostToolUse": [
  {
    "matcher": "Write",
    "hooks": [
      {
        "type": "command",
        "command": ".claude/hooks/on-script-created.sh"
      },
      {
        "type": "command",
        "command": ".claude/hooks/on-python-saved.sh"
      }
    ]
  },
  {
    "matcher": "Edit",
    "hooks": [
      {
        "type": "command",
        "command": ".claude/hooks/on-python-saved.sh"
      }
    ]
  }
]
```

**Step 3 : Valider le JSON**

```bash
python -c "import json; json.load(open('.claude/settings.json')); \
  print('JSON valide')"
```

Expected : `JSON valide`

---

### Task 4 : Mettre à jour `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md`

**Step 1 : Ajouter une section `## Agents parallèles`**

Insérer avant la section `## Langue` :

```markdown
## Agents parallèles

Utiliser des sous-agents pour :

- **Tâches indépendantes** — analyses, recherches ou transformations
  sans état partagé qui peuvent s'exécuter en parallèle
- **Protection du contexte** — déléguer les tâches volumineuses
  (exploration de codebase, lecture de nombreux fichiers) pour
  préserver la fenêtre de contexte de l'agent principal

Skill à invoquer : `superpowers:dispatching-parallel-agents`

Exemples typiques :
- Analyser plusieurs fichiers en parallèle avant une refactorisation
- Lancer des recherches indépendantes (grep, glob) simultanément
- Isoler une tâche longue sans polluer le contexte principal
```

**Step 2 : Vérifier la longueur des lignes**

```bash
awk 'length > 100 {print NR": "length" chars: "$0}' CLAUDE.md
```

Expected : aucune ligne > 100 caractères.

---

### Task 5 : Commit final

**Step 1 : Vérifier l'état git**

```bash
git status
```

**Step 2 : Stager et commiter en deux commits**

Commit A — hooks :

```bash
git add .claude/hooks/on-python-saved.sh \
        .claude/hooks/on-script-created.sh \
        .claude/settings.json
git commit -m "feat(hooks): add Python quality hook and fix scripts-index pattern

Add on-python-saved.sh (ruff + mypy + bandit) triggered on Write and
Edit. Fix on-script-created.sh subdirectory pattern (*/scripts/* instead
of *scripts/*.py). Register both hooks in settings.json.

Co-Authored-By: Claude <noreply@anthropic.com>"
```

Commit B — CLAUDE.md :

```bash
git add CLAUDE.md
git commit -m "docs(claude): add parallel sub-agents section

Document when and how to use dispatching-parallel-agents skill to
run independent tasks concurrently and protect main agent context.

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Step 3 : Vérifier le log**

```bash
git log --oneline -5
```
