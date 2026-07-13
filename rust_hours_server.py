from flask import Flask
import requests
import os

app = Flask(__name__)

STEAM_API_KEY = "A53A2AEF21547138C92E69B702C5CE85"
STEAM_ID = "76561199738179203"
RUST_APPID = 252490

@app.route('/rust-hours')
def get_rust_hours():
    try:
        # Busca todos os jogos e filtra o Rust no Python
        url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid={STEAM_ID}&include_appinfo=true&format=json"

        response = requests.get(url, timeout=10)
        data = response.json()

        games = data.get('response', {}).get('games', [])

        # Procurar Rust
        rust_game = None
        for game in games:
            if game.get('appid') == RUST_APPID:
                rust_game = game
                break

        if not rust_game:
            return "❌ Rust não encontrado na biblioteca Steam."

        minutes = rust_game.get('playtime_forever', 0)
        hours = minutes // 60
        remaining_minutes = minutes % 60

        # Formatação bonita baseada nas horas
        if hours >= 1000:
            return f"🎮 O streamer tem {hours:,}h {remaining_minutes}m de Rust! É muita dedicação! 🔥"
        elif hours >= 500:
            return f"🎮 O streamer tem {hours}h {remaining_minutes}m de Rust! Já é veterano de guerra! 💪"
        elif hours >= 100:
            return f"🎮 O streamer tem {hours}h {remaining_minutes}m de Rust! Tá virando pro! 🚀"
        elif hours >= 10:
            return f"🎮 O streamer tem {hours}h {remaining_minutes}m de Rust! Tá evoluindo bem! ⭐"
        else:
            return f"🎮 O streamer tem {hours}h {remaining_minutes}m de Rust! Começando a jornada! 🌱"

    except Exception as e:
        return "❌ Erro ao buscar horas de Rust. Tente novamente mais tarde."

@app.route('/')
def home():
    return "🎮 API de Horas de Rust - Use /rust-hours para ver as horas!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
