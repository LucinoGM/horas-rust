# 🎮 API Horas Rust

API que mostra automaticamente as horas de Rust do Steam no StreamElements.

## 🚀 Funcionalidades

- Comando `!horas` no StreamElements
- Site de status em tempo real
- Data automática (fuso Brasil UTC-3)
- Contador de pings
- Design com artes próprias (SVG/CSS)

## 📁 Estrutura

```
horas-rust/
├── rust_hours_server.py    # Servidor Flask
├── requirements.txt         # Dependências
├── static/
│   ├── css/
│   │   └── style.css       # Estilos com artes próprias
│   ├── js/
│   │   └── app.js          # JavaScript do site
│   └── images/             # (vazio - tudo é SVG/CSS)
└── templates/
    └── index.html          # Site de status
```

## 🔧 Configuração

1. Troque no `rust_hours_server.py`:
   - `STEAM_API_KEY` = Sua Steam API Key
   - `STEAM_ID` = Seu SteamID64

2. Deploy no Render:
   - Build: `pip install -r requirements.txt`
   - Start: `python rust_hours_server.py`

## 🔗 Endpoints

| Endpoint | Descrição |
|----------|-----------|
| `/` | Site de status |
| `/rust-hours` | Comando StreamElements |
| `/api/status` | Status em JSON |

## 📝 Comando StreamElements

```
$(customapi https://SEU-SITE.onrender.com/rust-hours)
```

---
Feito com 🔥 por [Seu Nome]
