from flask import Flask
import requests
import os
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

# ═══════════════════════════════════════════════════════════
# TROQUE AQUI: Cole sua Steam API Key (Passo 1 do tutorial)
# Exemplo: STEAM_API_KEY = "A53A2AEF21547138C92E69B702C5CE85"
STEAM_API_KEY = "COLE_SUA_API_KEY_AQUI"

# TROQUE AQUI: Cole seu SteamID64 (Passo 2 do tutorial)
# Exemplo: STEAM_ID = "76561199738179203"
STEAM_ID = "COLE_SEU_STEAMID64_AQUI"
# ═══════════════════════════════════════════════════════════

RUST_APPID = 252490

@app.route('/rust-hours')
def get_rust_hours():
    try:
        url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid={STEAM_ID}&include_appinfo=true&format=json"

        response = requests.get(url, timeout=10)
        data = response.json()

        games = data.get('response', {}).get('games', [])

        rust_game = None
        for game in games:
            if game.get('appid') == RUST_APPID:
                rust_game = game
                break

        if not rust_game:
            return "Rust nao encontrado na biblioteca Steam."

        minutes = rust_game.get('playtime_forever', 0)
        hours = minutes // 60

        # Fuso horário do Brasil (UTC-3)
        brasil_tz = timezone(timedelta(hours=-3))
        hoje = datetime.now(brasil_tz)
        data_formatada = hoje.strftime("%d/%m/%Y")

        horas_formatadas = f"{hours:,}".replace(",", ".")

        return f"No dia {data_formatada} foi registrado {horas_formatadas} horas de rust"

    except Exception as e:
        return "Erro ao buscar horas de Rust. Tente novamente mais tarde."

@app.route('/')
def home():
    return "API de Horas de Rust - Use /rust-hours para ver as horas!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
