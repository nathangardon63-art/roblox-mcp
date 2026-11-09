"""Serveur MCP pour Roblox (API Open Cloud + API publiques).

Lecture seule par défaut. Les outils d'écriture (data stores, messages)
ne sont activés que si ROBLOX_ALLOW_WRITE=1.
"""
import os
from urllib.parse import quote

import httpx
from mcp.server.fastmcp import FastMCP

API_KEY = os.environ.get("ROBLOX_API_KEY", "")
ALLOW_WRITE = os.environ.get("ROBLOX_ALLOW_WRITE", "0") == "1"
CLOUD = "https://apis.roblox.com"

mcp = FastMCP(
    "roblox",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "8000")),
)


async def _request(method: str, url: str, *, auth: bool = False, **kwargs):
    headers = kwargs.pop("headers", {})
    if auth:
        if not API_KEY:
            return {"erreur": "ROBLOX_API_KEY n'est pas définie sur le serveur."}
        headers["x-api-key"] = API_KEY
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.request(method, url, headers=headers, **kwargs)
    if r.status_code >= 400:
        return {"erreur": r.status_code, "détail": r.text[:500]}
    if not r.content:
        return {"ok": True}
    try:
        return r.json()
    except ValueError:
        return {"texte": r.text[:2000]}


def _q(value: str) -> str:
    return quote(str(value), safe="")


# ---------- Outils en lecture (API publiques, sans clé) ----------

@mcp.tool()
async def find_user(username: str) -> dict:
    """Trouve un utilisateur Roblox par son pseudo et renvoie son ID."""
    return await _request(
        "POST",
        "https://users.roblox.com/v1/usernames/users",
        json={"usernames": [username], "excludeBannedUsers": False},
    )


@mcp.tool()
async def get_user(user_id: int) -> dict:
    """Infos publiques d'un utilisateur (pseudo, description, date de création)."""
    return await _request("GET", f"https://users.roblox.com/v1/users/{user_id}")


@mcp.tool()
async def get_user_games(user_id: int, limit: int = 25) -> dict:
    """Liste les expériences publiques créées par un utilisateur."""
    return await _request(
        "GET",
        f"https://games.roblox.com/v2/users/{user_id}/games",
        params={"limit": limit, "sortOrder": "Desc"},
    )


# ---------- Outils en lecture (Open Cloud, clé API requise) ----------

@mcp.tool()
async def get_universe(universe_id: int) -> dict:
    """Détails d'une expérience (univers) : nom, description, visibilité..."""
    return await _request(
        "GET", f"{CLOUD}/cloud/v2/universes/{universe_id}", auth=True
    )


@mcp.tool()
async def list_data_stores(universe_id: int, max_page_size: int = 50) -> dict:
    """Liste les data stores d'une expérience."""
    return await _request(
        "GET",
        f"{CLOUD}/cloud/v2/universes/{universe_id}/data-stores",
        auth=True,
        params={"maxPageSize": max_page_size},
    )


@mcp.tool()
async def list_data_store_entries(
    universe_id: int,
    data_store_id: str,
    scope: str = "global",
    max_page_size: int = 50,
) -> dict:
    """Liste les entrées d'un data store pour un scope donné."""
    return await _request(
        "GET",
        f"{CLOUD}/cloud/v2/universes/{universe_id}/data-stores/{_q(data_store_id)}"
        f"/scopes/{_q(scope)}/entries",
        auth=True,
        params={"maxPageSize": max_page_size},
    )


@mcp.tool()
async def get_data_store_entry(
    universe_id: int, data_store_id: str, entry_id: str, scope: str = "global"
) -> dict:
    """Lit la valeur d'une entrée d'un data store."""
    return await _request(
        "GET",
        f"{CLOUD}/cloud/v2/universes/{universe_id}/data-stores/{_q(data_store_id)}"
        f"/scopes/{_q(scope)}/entries/{_q(entry_id)}",
        auth=True,
    )


# ---------- Outils en écriture (désactivés par défaut) ----------

if ALLOW_WRITE:

    @mcp.tool()
    async def set_data_store_entry(
        universe_id: int,
        data_store_id: str,
        entry_id: str,
        value: str,
        scope: str = "global",
    ) -> dict:
        """Crée une entrée dans un data store. `value` est du JSON sous forme de texte.
        ATTENTION : modifie les données réelles du jeu."""
        import json

        try:
            parsed = json.loads(value)
        except ValueError:
            parsed = value
        return await _request(
            "POST",
            f"{CLOUD}/cloud/v2/universes/{universe_id}/data-stores/{_q(data_store_id)}"
            f"/scopes/{_q(scope)}/entries",
            auth=True,
            params={"id": entry_id},
            json={"value": parsed},
        )

    @mcp.tool()
    async def delete_data_store_entry(
        universe_id: int, data_store_id: str, entry_id: str, scope: str = "global"
    ) -> dict:
        """Supprime une entrée d'un data store. ATTENTION : irréversible."""
        return await _request(
            "DELETE",
            f"{CLOUD}/cloud/v2/universes/{universe_id}/data-stores/{_q(data_store_id)}"
            f"/scopes/{_q(scope)}/entries/{_q(entry_id)}",
            auth=True,
        )

    @mcp.tool()
    async def publish_message(universe_id: int, topic: str, message: str) -> dict:
        """Envoie un message aux serveurs en cours de l'expérience (Messaging Service)."""
        return await _request(
            "POST",
            f"{CLOUD}/messaging-service/v1/universes/{universe_id}/topics/{_q(topic)}",
            auth=True,
            json={"message": message},
        )


if __name__ == "__main__":
    # Point d'accès MCP : http://<hôte>:<port>/mcp
    mcp.run(transport="streamable-http")
