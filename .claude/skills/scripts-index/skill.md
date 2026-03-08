---
name: scripts-index
description: Use when creating, modifying, deleting, or searching for scripts in the FRV project. Required before closing any task that touches a script file in scripts/.
---

# scripts-index

## Overview

`scripts/scripts.db` est la source de vérité pour tous les scripts du projet FRV.
**Règle absolue : toute tâche qui crée, modifie ou supprime un script doit mettre à jour la base avant d'être close.**

CLI : `poetry run scripts-index <cmd>` (depuis la racine du repo).

## When to Use

- Création d'un nouveau script Python ou VBA dans `scripts/`
- Modification de la description ou de l'usage d'un script existant
- Suppression d'un script
- Recherche de scripts par logiciel, tag ou mot-clé

**Ne pas utiliser pour** les modules dans `src/` (bibliothèques, pas scripts).

## Règle de maintenance

> Avant de clore une tâche : exécuter l'INSERT/UPDATE correspondant.

| Action         | Opération                                            |
| -------------- | ---------------------------------------------------- |
| Nouveau script | `INSERT INTO scripts` + liaisons software/tags       |
| Modification   | `UPDATE scripts SET description=..., updated_at=...` |
| Suppression    | `DELETE FROM scripts WHERE path=...` (CASCADE auto)  |

## Schéma de référence

```sql
scripts       (id, path UNIQUE, name, description, usage, created_at, updated_at)
software      (id, name UNIQUE)          -- Excel, Outlook, Word...
tags          (id, label UNIQUE)         -- vba, com, encoding, waterfall...
script_software (script_id, software_id) -- liaison N-N avec CASCADE
script_tags     (script_id, tag_id)      -- liaison N-N avec CASCADE
```

## Quick Reference — Requêtes types

```bash
# Tous les scripts d'un logiciel
poetry run scripts-index exec "SELECT s.path, s.description FROM scripts s JOIN script_software ss ON ss.script_id=s.id JOIN software sw ON sw.id=ss.software_id WHERE sw.name='Outlook'"

# Tous les scripts avec un tag
poetry run scripts-index exec "SELECT s.path FROM scripts s JOIN script_tags st ON st.script_id=s.id JOIN tags t ON t.id=st.tag_id WHERE t.label='vba'"

# Vue complète
poetry run scripts-index exec "SELECT * FROM scripts"

# Référentiels
poetry run scripts-index exec "SELECT * FROM software"
poetry run scripts-index exec "SELECT * FROM tags ORDER BY label"
```

## Règles de tagging

| Tag        | Usage                                                              | Condition                                                                 |
| ---------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| `com`      | Appels **pywin32 directs** (`import win32com`, `import pythoncom`) | Uniquement si le script utilise pywin32 sans passer par xlmanage/olmanage |
| `xlmanage` | Script utilisant la bibliothèque `xlmanage`                        | Mutuellement exclusif avec `com`                                          |
| `olmanage` | Script utilisant la bibliothèque `olmanage`                        | Mutuellement exclusif avec `com`                                          |

**Règle clé** : ne jamais combiner `com` avec `xlmanage` ou `olmanage`. Si un script passe par une bibliothèque d'encapsulation COM, c'est le tag de la bibliothèque qui s'applique, pas `com`.

## Templates CRUD

### Ajouter un script

**Procédure complète :**

1. **Lister les logiciels existants** :

```bash
poetry run scripts-index exec "SELECT * FROM software ORDER BY name"
```

2. **Lister les tags existants** :

```bash
poetry run scripts-index exec "SELECT * FROM tags ORDER BY label"
```

3. **Ajouter le script dans la table principale** :

```bash
poetry run scripts-index exec "INSERT INTO scripts(path,name,description,usage,created_at,updated_at) VALUES('scripts/<dossier>/<fichier>.py','<nom>','<description>','poetry run python scripts/<dossier>/<fichier>.py <args>','<YYYY-MM-DD>','<YYYY-MM-DD>')"
```

4. **Ajouter un logiciel si nécessaire (idempotent)** :

```bash
poetry run scripts-index exec "INSERT OR IGNORE INTO software(name) VALUES('<NomLogiciel>')"
```

5. **Créer la liaison entre le script et le logiciel** :

```bash
poetry run scripts-index exec "INSERT OR IGNORE INTO script_software(script_id,software_id) VALUES((SELECT id FROM scripts WHERE path='scripts/<dossier>/<fichier>.py'),(SELECT id FROM software WHERE name='<NomLogiciel>'))"
```

6. **Ajouter un tag si nécessaire (idempotent)** :

```bash
poetry run scripts-index exec "INSERT OR IGNORE INTO tags(label) VALUES('<tag>')"
```

7. **Créer la liaison entre le script et le tag** :

```bash
poetry run scripts-index exec "INSERT OR IGNORE INTO script_tags(script_id,tag_id) VALUES((SELECT id FROM scripts WHERE path='scripts/<dossier>/<fichier>.py'),(SELECT id FROM tags WHERE label='<tag>'))"
```

### Mettre à jour un script

```bash
poetry run scripts-index exec "UPDATE scripts SET description='<desc>',usage='<cmd>',updated_at='<YYYY-MM-DD>' WHERE path='scripts/<dossier>/<fichier>.py'"
```

### Supprimer un script

```bash
poetry run scripts-index exec "DELETE FROM scripts WHERE path='scripts/<dossier>/<fichier>.py'"
```

## Initialisation

```bash
poetry run scripts-index init        # crée scripts/scripts.db (idempotent)
poetry run scripts-index --help      # aide complète
```
