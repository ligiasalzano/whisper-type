# 🎙️ WhisperType — Windows

Ditado por voz local para Windows — segure **Ctrl+Space**, fale, solte e o texto é colado automaticamente onde o cursor estiver.

Toda a transcrição é feita **localmente** via [OpenAI Whisper](https://github.com/openai/whisper) — nenhum áudio é enviado para servidores externos.

---

## Como funciona

1. Segure **Ctrl+Space** → gravação inicia
2. Fale o que quiser
3. Solte **Ctrl+Space** → o áudio é transcrito e o texto é colado automaticamente

---

## Pré-requisitos do sistema

### 1. Python 3.10+

Verifique com:
```
python --version
```

Baixe em [python.org](https://www.python.org/downloads/) se necessário.

### 2. ffmpeg no PATH

Baixe em [ffmpeg.org](https://ffmpeg.org/download.html), extraia e adicione a pasta `bin` ao PATH do Windows.

Verifique com:
```
ffmpeg -version
```

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/whispertype.git
cd whispertype
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv .venv
.venv\Scripts\activate
```

> O prompt mudará para `(.venv) ...` confirmando que está ativo.

### 3. Instale as dependências Python

```bash
pip install -r requirements_windows.txt
```

---

## Uso

Execute o terminal **como Administrador** (necessário para capturar atalhos globais):

```bash
.venv\Scripts\activate
python -m whispertype
```

Ao iniciar:

```
[14:32:01] Carregando modelo Whisper 'base'...
[14:32:04] Modelo carregado. Idioma: pt
[14:32:04] Detectando microfone...
[14:32:04] Microfone: Microphone (2- HyperX SoloCast)
[14:32:04] Pronto! Segure CTRL+SPACE para ditar. Ctrl+C para sair.
```

---

## Configuração

Edite `whispertype/config.py`:

| Variável | Padrão | Descrição |
|---|---|---|
| `MODEL_SIZE` | `base` | Tamanho do modelo Whisper |
| `LANGUAGE` | `pt` | Idioma (`None` para autodetectar) |
| `PASTE_DELAY_SECONDS` | `0.15` | Pausa antes de colar (em segundos) |

O atalho é configurado diretamente em `whispertype/__main__.py`, na função `_run_windows`:
```python
HOTKEY = "ctrl+space"
```

### Modelos disponíveis

| Modelo | Velocidade | Precisão | VRAM |
|---|---|---|---|
| `tiny` | ⚡⚡⚡⚡ | ★★☆☆ | ~1 GB |
| `base` | ⚡⚡⚡ | ★★★☆ | ~1 GB |
| `small` | ⚡⚡ | ★★★★ | ~2 GB |
| `medium` | ⚡ | ★★★★ | ~5 GB |
| `large` | 🐢 | ★★★★★ | ~10 GB |

---

## Executar ao iniciar o Windows (opcional)

1. Crie `whispertype.vbs` substituindo o caminho real:

```vbs
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c cd /d C:\caminho\para\whispertype && .venv\Scripts\activate && python -m whispertype", 0, False
```

2. Pressione **Win+R**, digite `shell:startup` e coloque um atalho para o `.vbs` nessa pasta.

---

## Desativar o ambiente virtual

```bash
deactivate
```

---

## Solução de problemas

**ffmpeg não encontrado**
Verifique se está no PATH: `ffmpeg -version`. Se falhar, revise a instalação.

**Microfone não detectado**
Liste os dispositivos:
```
ffmpeg -list_devices true -f dshow -i dummy 2>&1
```

**Atalho não funciona**
Execute o terminal como Administrador.

**Texto colando no lugar errado**
Aumente `PASTE_DELAY_SECONDS` para `0.3` ou mais em `config.py`.

**Transcrição em inglês com `LANGUAGE="pt"`**
Use um modelo maior como `small` ou `medium`.

---

## Licença

MIT
