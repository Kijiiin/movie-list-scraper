# config.py
# ============================================================
# DOMINIO CORRENTE DI STREAMINGCOMMUNITY
# ============================================================
# Quando il dominio cambia, modifica solo questa riga.
# Esempi:
#   streamingcommunityz.support
#   streamingcommunity.xyz
#   streamingcommunity.one
#   streamingcommunity.tv
# ============================================================

STREAMING_DOMAIN = "streamingcommunityz.jetzt"

# URL di base
BASE_URL = f"https://{STREAMING_DOMAIN}"

# Endpoint per film e serie TV
MOVIES_URL = f"{BASE_URL}/it/archive?type=movie"
TV_URL = f"{BASE_URL}/it/archive?sort=last_air_date&type=tv"
 
