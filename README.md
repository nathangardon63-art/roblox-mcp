# Connecteur Roblox pour Claude

Serveur MCP basé sur l'API Roblox Open Cloud. **Non testé** : je n'avais pas
accès au réseau pour l'essayer, donc certains endpoints peuvent demander un
petit ajustement.

## 1. Créer la clé API Roblox
1. Va sur https://create.roblox.com/dashboard/credentials
2. Crée une clé API (Open Cloud) avec le **minimum** de permissions :
   - `universe:read` (infos de l'expérience)
   - `universe.datastore.objects:read` et `...:list` (lecture des data stores)
   - Écriture (`create`, `update`, `delete`, `universe-messaging-service:publish`) : **uniquement si tu en as besoin**
3. Ajoute l'expérience concernée et, si possible, restreins par adresse IP.
4. Ne colle jamais la clé dans le chat : elle va seulement dans la variable d'environnement du serveur.

## 2. Lancer le serveur
```bash
pip install -r requirements.txt
ROBLOX_API_KEY=ta_cle python server.py
```
Le serveur écoute sur `http://localhost:8000/mcp`.

Variables :
- `ROBLOX_API_KEY` : ta clé Open Cloud
- `ROBLOX_ALLOW_WRITE=1` : active les outils d'écriture (désactivés par défaut)
- `PORT` : port d'écoute (8000 par défaut)

## 3. L'héberger en HTTPS
Claude a besoin d'une URL publique en HTTPS. Render, Railway ou Fly.io
conviennent : déploie ce dossier, commande de démarrage `python server.py`,
puis renseigne `ROBLOX_API_KEY` dans les variables d'environnement.

## 4. Le brancher à Claude
Dans les paramètres de Claude, section Connecteurs → ajouter un connecteur
personnalisé, avec l'URL `https://ton-domaine/mcp`.

## Sécurité
- Ce serveur n'a pas d'authentification : quiconque connaît l'URL peut
  l'utiliser avec les droits de ta clé. Garde l'URL privée, laisse l'écriture
  désactivée si possible, et supprime la clé dans le tableau de bord Roblox au
  moindre doute.
- Les clés Open Cloud donnent accès à tes expériences, pas à ton compte
  entier (pas de Robux, ni de mot de passe, etc.).

## Outils disponibles
Lecture : `find_user`, `get_user`, `get_user_games`, `get_universe`,
`list_data_stores`, `list_data_store_entries`, `get_data_store_entry`.
Écriture (si activée) : `set_data_store_entry`, `delete_data_store_entry`,
`publish_message`.
