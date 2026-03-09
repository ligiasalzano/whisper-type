# 🎙️ WhisperType

Ditado por voz local com Whisper — segure **Ctrl+Space**, fale, solte e o texto é colado automaticamente onde o cursor estiver.

Funciona em qualquer campo de texto: Notion, navegadores, editores, apps de mensagem, etc.
Toda a transcrição é feita **localmente** — nenhum áudio é enviado para servidores externos.

| Sistema | Guia completo |
|---|---|
| Windows 10/11 | [README_windows.md](README_windows.md) |
| Ubuntu / Pop!_OS | [README_linux.md](README_linux.md) |

---

## Estrutura do projeto

```
whispertype/
├── whispertype/
│   ├── __main__.py        # ponto de entrada (detecta o OS automaticamente)
│   ├── config.py          # configurações (modelo, idioma, atalho)
│   ├── recorder.py        # lógica de gravação e transcrição (compartilhada)
│   ├── audio/
│   │   ├── windows.py     # detecção de microfone e ffmpeg via dshow
│   │   └── linux.py       # detecção de microfone e ffmpeg via pulse
│   └── paste/
│       ├── windows.py     # colagem via pyautogui
│       └── linux.py       # colagem via xdotool (X11) ou ydotool (Wayland)
├── requirements_windows.txt
├── requirements_linux.txt
├── pyproject.toml
├── LICENSE
└── .gitignore
```

---

## Instalação rápida

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/whispertype.git
cd whispertype
```

### 2. Crie e ative o ambiente virtual

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instale as dependências Python

```bash
# Windows
pip install -r requirements_windows.txt

# Linux
pip install -r requirements_linux.txt
```

### 4. Instale as dependências do sistema

```bash
# Windows — ffmpeg no PATH
# Baixe em https://ffmpeg.org e adicione a pasta bin ao PATH

# Linux
sudo apt install ffmpeg pulseaudio-utils xdotool   # X11
sudo apt install ffmpeg pulseaudio-utils ydotool   # Wayland
```

---

## Uso

```bash
python -m whispertype
```

O script detecta o sistema operacional automaticamente.

---

## Configuração

Edite `whispertype/config.py`:

| Variável | Padrão | Descrição |
|---|---|---|
| `MODEL_SIZE` | `base` | Tamanho do modelo Whisper |
| `LANGUAGE` | `pt` | Idioma (`None` para autodetectar) |
| `PASTE_DELAY_SECONDS` | `0.15` | Pausa antes de colar (em segundos) |

### Modelos disponíveis

| Modelo | Velocidade | Precisão | VRAM |
|---|---|---|---|
| `tiny` | ⚡⚡⚡⚡ | ★★☆☆ | ~1 GB |
| `base` | ⚡⚡⚡ | ★★★☆ | ~1 GB |
| `small` | ⚡⚡ | ★★★★ | ~2 GB |
| `medium` | ⚡ | ★★★★ | ~5 GB |
| `large` | 🐢 | ★★★★★ | ~10 GB |

---

## Dependências

| Pacote | Onde | Descrição |
|---|---|---|
| `openai-whisper` | ambos | Transcrição de áudio local |
| `pyperclip` | ambos | Área de transferência |
| `keyboard` | Windows | Captura de atalhos globais |
| `pyautogui` | Windows | Simula Ctrl+V |
| `pynput` | Linux | Captura de atalhos globais (X11 e Wayland) |
| `ffmpeg` | ambos | Captura de áudio do microfone |
| `xdotool` | Linux X11 | Simula Ctrl+V |
| `ydotool` | Linux Wayland | Simula Ctrl+V |

---

## Licença

MIT
