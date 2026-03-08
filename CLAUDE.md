# Forge — Instructions Claude Code

## Projet

Forge est un écosystème de bibliothèques, d'outils et d'applications, développé
en collaboration avec des LLM (Claude, ...). Le répertoire `.claude/` héberge
les skills, settings et conventions locales du projet.

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

### Settings

- Les settings projet vont UNIQUEMENT dans `.claude/settings.json`

### Skills

- Toutes les skills sont locales au projet : `.claude/skills/`
