# 🎙️ WhisperType — Linux (Ubuntu / Pop!_OS)

Ditado por voz local para Linux — segure **Ctrl+Space**, fale, solte e o texto é colado automaticamente onde o cursor estiver.

Funciona em qualquer campo de texto: Notion, navegadores, editores, apps de mensagem, etc.

Toda a transcrição é feita **localmente** via [OpenAI Whisper](https://github.com/openai/whisper) — nenhum áudio é enviado para servidores externos.

> Testado em **Ubuntu 22.04** e **Pop!_OS 22.04** com GNOME 42, nas sessões X11 e Wayland.

---

## Como funciona

1. Segure **Ctrl+Space** → gravação inicia
2. Fale o que quiser
3. Solte **Ctrl+Space** → o áudio é transcrito e o texto é colado automaticamente

---

## Pré-requisitos do sistema

### 1. Python 3.10+

Verifique com:
```bash
python3 --version
```

Se precisar instalar:
```bash
sudo apt install python3 python3-pip python3-venv
```

### 2. ffmpeg

```bash
sudo apt install ffmpeg
```

### 3. pulseaudio-utils (para detectar o microfone)

```bash
sudo apt install pulseaudio-utils
```

> Pop!_OS e Ubuntu 22.04 já usam PipeWire com compatibilidade PulseAudio — os comandos `pactl` funcionam normalmente.

### 4. Ferramenta de colagem (escolha conforme sua sessão)

Não sabe qual sessão usa? Rode:
```bash
echo $XDG_SESSION_TYPE
```

**X11:**
```bash
sudo apt install xdotool
```

**Wayland:**
```bash
sudo apt install ydotool
# Ative o serviço:
sudo systemctl enable --now ydotool
```

---

## Instalação com ambiente virtual (recomendado)

O ambiente virtual (`venv`) isola as dependências do WhisperType do restante do sistema, evitando conflitos de pacotes.

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/whispertype.git
cd whispertype
```

### 2. Crie e ative o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> O prompt do terminal vai mudar para `(.venv) ...` confirmando que está ativo.

### 3. Instale as dependências Python

```bash
pip install openai-whisper pyperclip pynput
```

> A primeira execução vai baixar o modelo Whisper escolhido (ex: `base` ≈ 140 MB).

### 4. Verifique se o ffmpeg está disponível dentro do venv

```bash
ffmpeg -version
```

---

## Uso

Com o ambiente virtual ativo:

```bash
source .venv/bin/activate   # se ainda não estiver ativo
python whispertype_linux.py
```

Ao iniciar, você verá algo assim:

```
[14:32:01] Sessão detectada: WAYLAND
[14:32:01] Carregando modelo Whisper 'base'...
[14:32:04] Modelo carregado. Idioma: pt
[14:32:04] Detectando microfone...
[14:32:04] Microfone: alsa_input.usb-Kingston_HyperX_SoloCast-00.mono-fallback
[14:32:04] Pronto! Segure CTRL+SPACE para ditar. Ctrl+C para sair.
```

Para encerrar, pressione **Ctrl+C** no terminal.

---

## Configuração

As opções ficam no topo do arquivo `whispertype_linux.py`:

| Variável | Padrão | Descrição |
|---|---|---|
| `HOTKEY` | `ctrl+space` | Combinação de teclas para push-to-talk |
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

Para português, `small` oferece um bom equilíbrio entre velocidade e precisão.

---

## Executar automaticamente ao iniciar o sistema (opcional)

### 1. Crie um script de inicialização

Crie o arquivo `~/.local/bin/whispertype.sh`:

```bash
mkdir -p ~/.local/bin
cat > ~/.local/bin/whispertype.sh << 'SH'
#!/bin/bash
source /caminho/para/whispertype/.venv/bin/activate
python /caminho/para/whispertype/whispertype_linux.py
SH
chmod +x ~/.local/bin/whispertype.sh
```

> Substitua `/caminho/para/whispertype` pelo caminho real do repositório.

### 2. Crie uma entrada no Autostart do GNOME

```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/whispertype.desktop << 'DESKTOP'
[Desktop Entry]
Type=Application
Name=WhisperType
Exec=/home/SEU_USUARIO/.local/bin/whispertype.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
DESKTOP
```

> Substitua `SEU_USUARIO` pelo seu nome de usuário.

---

## Desativar o ambiente virtual

Quando terminar de usar o terminal onde o venv está ativo:

```bash
deactivate
```

---

## Solução de problemas

**`pactl: command not found`**
```bash
sudo apt install pulseaudio-utils
```

**Microfone não detectado**

Liste os dispositivos disponíveis:
```bash
pactl list sources short
```
Copie o nome do microfone desejado e defina manualmente na função `get_default_mic_name()`, substituindo o retorno pelo nome copiado.

**Atalho não funciona no Wayland**

O `pynput` no Wayland pode exigir permissões extras. Tente adicionar seu usuário ao grupo `input`:
```bash
sudo usermod -aG input $USER
# Faça logout e login novamente
```

**Colagem não funciona no Wayland (`ydotool`)**

Verifique se o serviço está ativo:
```bash
sudo systemctl status ydotool
```
Se não estiver:
```bash
sudo systemctl enable --now ydotool
```

**Texto colando no lugar errado**

Aumente o `PASTE_DELAY_SECONDS` para `0.3` ou mais.

**Transcrição em inglês com `LANGUAGE="pt"`**

Use um modelo maior como `small` ou `medium`.

**Erro ao importar `whisper` com o venv ativo**

Confirme que o venv está ativo (`(.venv)` no prompt) e reinstale:
```bash
pip install --upgrade openai-whisper
```

---

## Por que venv e não Docker?

O WhisperType precisa de acesso direto a recursos do sistema: microfone, teclado global e área de transferência. Expor esses recursos para dentro de um container Docker adiciona complexidade significativa (`--device`, sockets, permissões) sem nenhuma vantagem prática para um script local. O `venv` resolve o isolamento de dependências de forma simples e sem fricção.

---

## Dependências

| Pacote | Descrição |
|---|---|
| `openai-whisper` | Transcrição de áudio local |
| `pynput` | Captura de atalhos globais de teclado (X11 e Wayland) |
| `pyperclip` | Copia o texto transcrito para a área de transferência |
| `ffmpeg` | Captura do áudio do microfone via PulseAudio |
| `xdotool` | Simula Ctrl+V no X11 |
| `ydotool` | Simula Ctrl+V no Wayland |

---

## Licença

MIT
