from flask import Flask, render_template, jsonify, request
import requests
import os
from datetime import datetime, timezone, timedelta

api_enabled = True


def set_api_enabled(enabled):
    global api_enabled
    api_enabled = enabled


def is_api_enabled():
    return api_enabled

app = Flask(__name__)

# ═══════════════════════════════════════════════════════════
# CONFIGURAÇÃO - TROQUE AQUI
# ═══════════════════════════════════════════════════════════
STEAM_API_KEY = "A53A2AEF21547138C92E69B702C5CE85"
STEAM_ID = "76561199738179203"
RUST_APPID = 252490

# Contador de pings (conta apenas os pings enviados pelo monitor/externo)
ping_count = 0
last_ping_timestamp = None
start_time = datetime.now(timezone(timedelta(hours=-3)))
# ═══════════════════════════════════════════════════════════

@app.route('/')
def home():
    """Página inicial com o site de status"""
    return render_template('index.html')

@app.route('/api/toggle-status', methods=['GET', 'POST'])
def toggle_status():
    """Alterna o estado da API entre ligada e desligada."""
    global api_enabled

    api_enabled = not api_enabled
    return jsonify({
        'enabled': api_enabled,
        'message': 'API ligada' if api_enabled else 'API desligada'
    })


@app.route('/api/status')
def api_status():
    """Endpoint que retorna o status da API em JSON"""
    global ping_count, last_ping_timestamp

    if not api_enabled:
        return jsonify({
            'online': False,
            'enabled': False,
            'error': 'API desligada manualmente.'
        }), 503

    now = datetime.now(timezone(timedelta(hours=-3)))
    accept_header = request.headers.get('Accept', '')
    is_monitor_ping = request.args.get('source') == 'monitor' or request.args.get('monitor') == '1' or 'application/json' not in accept_header

    if is_monitor_ping:
        ping_count += 1
        last_ping_timestamp = now

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
            return jsonify({
                'online': False,
                'error': 'Rust nao encontrado na biblioteca Steam.'
            })

        current_game_name = None
        current_game_hours = None
        profile_name = None
        profile_avatar = None
        profile_state = None
        try:
            summary_url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={STEAM_ID}"
            summary_response = requests.get(summary_url, timeout=10)
            summary_data = summary_response.json()
            player = summary_data.get('response', {}).get('players', [None])[0]
            if player:
                profile_name = player.get('personaname')
                profile_avatar = player.get('avatarfull')
                persona_state = player.get('personastate')
                profile_state = 'Offline' if persona_state == 0 else 'Online'
                current_game_name = player.get('gameextrainfo')
                current_game_id = player.get('gameid')
                if current_game_id:
                    for game in games:
                        if str(game.get('appid')) == str(current_game_id):
                            current_game_hours = game.get('playtime_forever', 0) // 60
                            break
                if current_game_name and current_game_hours is None:
                    for game in games:
                        if game.get('name') == current_game_name:
                            current_game_hours = game.get('playtime_forever', 0) // 60
                            break
        except Exception:
            current_game_name = None
            current_game_hours = None
            profile_name = None
            profile_avatar = None
            profile_state = None

        minutes = rust_game.get('playtime_forever', 0)
        hours = minutes // 60

        # Calcular uptime
        uptime_seconds = int((now - start_time).total_seconds())

        return jsonify({
            'online': True,
            'enabled': True,
            'hours': hours,
            'hours_formatted': f"{hours:,}".replace(",", "."),
            'date': now.strftime("%d/%m/%Y"),
            'uptime_seconds': uptime_seconds,
            'ping_count': ping_count,
            'profile_name': profile_name,
            'profile_avatar': profile_avatar,
            'profile_state': profile_state,
            'current_game': current_game_name,
            'current_game_hours': current_game_hours,
            'last_ping_timestamp': int(last_ping_timestamp.timestamp()) if last_ping_timestamp else None,
            'last_ping_at': last_ping_timestamp.strftime('%d/%m/%Y %H:%M:%S') if last_ping_timestamp else None,
            'message': f"No dia {now.strftime('%d/%m/%Y')} foi registrado {hours} horas de rust"
        })

    except Exception as e:
        return jsonify({
            'online': False,
            'error': str(e)
        })

@app.route('/rust-hours')
def get_rust_hours():
    """Endpoint para o StreamElements"""
    if not api_enabled:
        return "API desligada manualmente.", 503

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

        hoje = datetime.now(timezone(timedelta(hours=-3)))
        data_formatada = hoje.strftime("%d/%m/%Y")

        horas_formatadas = f"{hours:,}".replace(",", ".")

        return f"No dia {data_formatada} foi registrado {horas_formatadas} horas de rust"

    except Exception as e:
        return "Erro ao buscar horas de Rust. Tente novamente mais tarde."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
