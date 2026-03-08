# Forge

Forge est un écosystème de bibliothèques, d'outils et d'applications, développé en collaboration avec Claude Code.

Il sert également de terrain d'apprentissage pour construire un écosystème IA local dans `.claude` : skills, mémoire persistante, et conventions de travail partagées.

## Structure

```
forge/
├── .claude/          # Écosystème IA local (skills, settings, mémoire)
└── _dev/             # Documentation de développement
```

## Philosophie

- Les skills sont **locales** à ce projet
- Les settings sont dans `settings.json` (pas `settings.local.json`)
- Chaque outil ou bibliothèque est un sous-projet autonome
