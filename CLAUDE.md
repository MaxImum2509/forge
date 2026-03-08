# Forge — Instructions Claude Code

## Projet

Forge est un écosystème de bibliothèques, d'outils et d'applications, développé
en collaboration avec des LLM (Claude, ...). Le répertoire `.claude/` héberge
les skills, settings et conventions locales du projet.

## Structure

```
forge/
├── CLAUDE.md
├── README.md
├── .gitignore
├── .claude/           # Écosystème IA local
│   ├── settings.json
│   └── skills/
├── _dev/              # Documentation de développement
│   └── PROGRESS.md
├── docs/              # Documentation projet
├── scripts/           # Scripts utilitaires
├── src/               # Code source des applications et bibliothèques
├── tests/             # Tests
└── _work/             # Zone de travail locale (hors git)
    ├── 00-inbox/      # Éléments entrants non classés
    ├── 10-projects/   # Projets actifs
    ├── 20-areas/      # Responsabilités continues
    ├── 30-resources/  # Références et ressources
    └── 40-archives/   # Éléments inactifs
```

`_work/` suit la méthode **IPARA** (PARA + Inbox). Les indices
multiples de 10 permettent d'insérer des catégories intermédiaires.

## Philosophie de développement

### scripts/ — Tooling utilitaire

- Langage libre (Python, VBA, C#, F#, Java, etc.) selon le besoin
- Deux vocations :
  1. Manipuler les fichiers de `_work/`
  2. Créer des outils et applications destinés à `src/`
- Développés rapidement, à la demande (pas de sur-ingénierie)
- **Pattern DRY** : quand un pattern se répète, on extrait vers
  une application dédiée ou une bibliothèque dans `src/`

### src/ — Code de production

- Applications et bibliothèques pérennes
- Émergent des patterns identifiés dans `scripts/`
- Conçus pour sous-tendre les futurs développements

### Principes généraux

**Clean Code** (appliqué strictement) :

- SRP — une seule responsabilité par module/fonction
- DRY — pas de duplication ; abstraire dès qu'un pattern se répète
- KISS — solution la plus simple possible
- YAGNI — ne pas développer ce qui n'est pas nécessaire maintenant
- SOLID — principes d'architecture orientée objet

**Test-Driven Development** (appliqué strictement) :

- Rouge → Vert → Refactor (cycle TDD sans exception)
- Écrire le test avant le code de production
- Couverture de tests élevée sur `src/` ; tests pertinents sur
  `scripts/` selon la criticité

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

## Langue

- **Communications** : français
- **Code, identifiants, commits** : anglais (Conventional Commits)

## Conventions

### Markdown

- Longueur de ligne : viser **75–85 caractères**, maximum **100**
- S'applique aussi aux tableaux : gérer la largeur de chaque colonne
  pour que la largeur totale du tableau reste dans cette plage
- Les textes en français doivent intégrer les accents (é, è, ê, à,
  ù, ç, œ, etc.) — ne jamais les omettre

### Git

- Conventional Commits : `type(scope): description`
- Messages de commit en **anglais**
- Toujours co-signer : `Co-Authored-By: Claude <noreply@anthropic.com>`
- Remote HTTPS : `https://github.com/MaxImum2509/forge.git`

## Contraintes (MANDATORY)

- **skills** : UNIQUEMENT locales au projet (`.claude/skills/`)
- **settings** : UNIQUEMENT locaux au projet (`.claude/settings.json`)
- **Python** : Poetry uniquement (`pip` interdit), docstrings Sphinx, tests pytest suivant standards `python-development-rules`
- **VBA** : modules dans `src/vba/`, encodage Windows-1252 suivant standards `excel-development-rules`
- **Exécution** : `poetry run python scripts/...`
