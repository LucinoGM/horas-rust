from flask import Flask
import requests
import os
from datetime import datetime

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
            return "Rust nao encontrado na biblioteca Steam."

        # Pegar horas inteiras (sem minutos)
        minutes = rust_game.get('playtime_forever', 0)
        hours = minutes // 60

        # Pegar data de hoje
        hoje = datetime.now()
        data_formatada = hoje.strftime("%d/%m/%Y")

        # Formatar horas com ponto como separador de milhar
        horas_formatadas = f"{hours:,}".replace(",", ".")

        # Mensagem final
        return f"No dia {data_formatada} foi registrado {horas_formatadas} horas de rust"

    except Exception as e:
        return "Erro ao buscar horas de Rust. Tente novamente mais tarde."

@app.route('/')
def home():
    return "API de Horas de Rust - Use /rust-hours para ver as horas!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
