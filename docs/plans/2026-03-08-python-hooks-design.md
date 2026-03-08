# Design — Hooks Claude Code et sous-agents

Date : 2026-03-08

## Contexte

Le projet Forge utilise des hooks Claude Code (PostToolUse) pour automatiser
des vérifications au fil du développement. Deux hooks existent déjà :

- `on-script-created.sh` — rappel d'indexation scripts.db
- `settings.json` — permissions et déclaration des hooks

Trois améliorations sont identifiées :

1. Créer un hook de qualité Python (ruff + mypy + bandit) sur Write et Edit
2. Corriger le pattern de `on-script-created.sh` (sous-répertoires ignorés)
3. Documenter l'usage des sous-agents parallèles dans `CLAUDE.md`

## Décisions de design

### Approche retenue : script partagé (SRP + DRY)

Un seul script `on-python-saved.sh`, enregistré sur les matchers `Write`
et `Edit`. Un script = une responsabilité (qualité Python).

`on-script-created.sh` reste dédié à la responsabilité scripts-index.

### Hook de qualité Python — `on-python-saved.sh`

**Déclencheur :** PostToolUse sur `Write` et `Edit`

**Condition :** `file_path` se termine par `.py`

**Chaîne d'outils (dans l'ordre) :**

| Outil | Cible | Rôle |
|-------|-------|------|
| `ruff check --fix` | fichier modifié | Lint + auto-fix |
| `ruff format` | fichier modifié | Formatage |
| `mypy src/` | `src/` entier | Typage (contexte complet) |
| `bandit -r src/` | `src/` entier | Sécurité |

Tous les outils s'exécutent même si l'un échoue. Le code de sortie est le
OU logique des codes de retour — Claude voit les problèmes résiduels.

### Fix `on-script-created.sh`

Pattern actuel : `*scripts/*.py` (ne couvre pas les sous-répertoires)
Pattern corrigé : `*/scripts/*` (couvre tous les niveaux, py et non-py)

### Déclaration dans `settings.json`

```
PostToolUse:
  Write  → on-script-created.sh
  Write  → on-python-saved.sh
  Edit   → on-python-saved.sh
```

### CLAUDE.md — section sous-agents parallèles

Nouvelle section documentant :

- Quand déléguer à un sous-agent (tâches indépendantes, protection
  du contexte principal)
- Skill à invoquer : `superpowers:dispatching-parallel-agents`
- Exemples de cas d'usage (analyse multi-fichiers, recherches parallèles)

## Fichiers impactés

| Fichier | Action |
|---------|--------|
| `.claude/hooks/on-python-saved.sh` | Créer |
| `.claude/hooks/on-script-created.sh` | Modifier (pattern) |
| `.claude/settings.json` | Modifier (nouveaux hooks) |
| `CLAUDE.md` | Modifier (section sous-agents) |
