# 🎙️ WhisperType

Ditado por voz local para Windows — segure **Ctrl+Space**, fale, solte e o texto é colado automaticamente onde o cursor estiver.

Funciona em qualquer campo de texto: Notion, navegadores, editores, apps de mensagem, etc.

Toda a transcrição é feita **localmente** via [OpenAI Whisper](https://github.com/openai/whisper) — nenhum áudio é enviado para servidores externos.

---

## Como funciona

1. Segure **Ctrl+Space** → a gravação inicia
2. Fale o que quiser
3. Solte **Ctrl+Space** → o áudio é transcrito e o texto é colado automaticamente

---

## Requisitos

- **Windows** 10 ou 11
- **Python** 3.10 ou superior
- **[ffmpeg](https://ffmpeg.org/download.html)** instalado e no PATH

> Para verificar se o ffmpeg está no PATH, rode `ffmpeg -version` no terminal. Se a versão for exibida, está correto.

---

## Instalação

### 1. Clone ou baixe o projeto

```bash
git clone https://github.com/ligiasalzano/whisper-type.git
cd whisper-type
```

*(Ou faça o download do código e extraia em uma pasta.)*

### 2. (Recomendado) Crie um ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate
```

No PowerShell, se aparecer erro de "execução de scripts desabilitada", use **CMD** ou rode antes:  
`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 3. Instale as dependências Python

**Se você tem GPU NVIDIA** e quer usar CUDA (transcrição mais rápida, sem aviso FP16):

```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```
*(Troque `cu121` por `cu118` ou outra versão conforme [pytorch.org](https://pytorch.org/get-started/locally/).)*

Depois instale o resto:

```bash
pip install -r requirements.txt
```

**Se você usa só CPU**, basta:

```bash
pip install -r requirements.txt
```

*Ou, manualmente:* `pip install openai-whisper pyperclip keyboard pyautogui`

### 4. Instale o ffmpeg

Baixe em [ffmpeg.org](https://ffmpeg.org/download.html), extraia e adicione a pasta `bin` ao PATH do Windows.

---

## Uso

1. Abra o **Terminal** ou **PowerShell** e vá até a pasta do projeto:
   ```bash
   cd caminho\para\whisper-type
   ```

2. **Se você criou um ambiente virtual (passo 2 da instalação), ative-o** — em cada nova janela de terminal é preciso ativar de novo:
   ```bash
   venv\Scripts\activate
   ```
   *(O prompt deve mostrar `(venv)` no início.)*

3. Execute o script:
   ```bash
   python whispertype.py
   ```

Mantenha o terminal aberto; o atalho **Ctrl+Space** funciona em qualquer aplicativo em foco. Para encerrar, pressione **Ctrl+C**.

> Se o atalho **Ctrl+Space** não responder em outros programas, tente abrir o terminal como **Administrador** (clique direito → *Executar como administrador*) e rodar o script de novo. Em alguns sistemas isso é necessário para atalhos globais.

Ao iniciar, você verá algo assim (a primeira linha indica se o PyTorch enxerga a GPU; a segunda mostra onde o modelo foi carregado):

```
[14:46:51] PyTorch 2.10.0+cu126 | CUDA disponível: True (versão: 12.6)
[14:46:51] Carregando modelo Whisper 'small'...
[14:46:53] Modelo carregado (dispositivo: cuda:0).
[14:46:53] Atalho: CTRL+SPACE | Idioma: pt
[14:46:53] Detectando microfone...
[14:46:53] Microfone: Microphone (2- HyperX SoloCast)
[14:46:53] Pronto! Segure CTRL+SPACE para ditar. Ctrl+C para sair.
```

Se aparecer **dispositivo: CPU**, a transcrição roda na CPU (mais lenta). Se aparecer **dispositivo: cuda:0**, está usando a GPU.

---

## Configuração

As opções ficam no topo do arquivo `whispertype.py`:

| Variável | Padrão | Descrição |
|---|---|---|
| `HOTKEY` | `ctrl+space` | Atalho de push-to-talk |
| `MODEL_SIZE` | `base` | Tamanho do modelo Whisper |
| `LANGUAGE` | `pt` | Idioma da transcrição (`None` para autodetectar) |
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

## Solução de problemas

**Microfone não detectado**  
Verifique se o ffmpeg está no PATH com `ffmpeg -version`. Para listar os dispositivos de áudio:
```bash
ffmpeg -list_devices true -f dshow -i dummy 2>&1
```

**Atalho não funciona**  
Tente executar o terminal como **Administrador** (clique direito no Terminal/PowerShell → *Executar como administrador*), depois ative o venv (se usar) e rode `python whispertype.py` de novo. Em alguns Windows o atalho global só funciona com privilégios elevados.

**Erro "No module named 'whisper'" (ou outro módulo)**  
Confirme que está na pasta do projeto e que ativou o ambiente virtual (se estiver usando). Rode `pip install -r requirements.txt` novamente.

**Texto colando no lugar errado**  
Clique no campo de destino *antes* de soltar o atalho. Se continuar, aumente `PASTE_DELAY_SECONDS` em `whispertype.py` (por exemplo, `0.3` ou `0.5`).

**Transcrição em inglês mesmo com `LANGUAGE="pt"`**  
Use um modelo maior: `small` ou `medium`. Modelos menores têm menos precisão em idiomas que não sejam inglês.

**Continua usando CPU mesmo com PyTorch+CUDA instalado?**  
Ao iniciar, confira a linha que mostra **CUDA disponível** e **Modelo carregado (dispositivo: ...)**. Se aparecer `dispositivo: CPU` e você tem GPU NVIDIA, o PyTorch do ambiente provavelmente está em versão só para CPU (por exemplo, foi sobrescrito ao instalar o `openai-whisper`). Reinstale o PyTorch com CUDA *depois* das outras dependências:
```bash
pip uninstall torch torchaudio -y
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```
*(Troque `cu121` por `cu118` ou pela versão indicada em [pytorch.org](https://pytorch.org/get-started/locally/) para o seu driver.)*

---

## Dependências

As dependências Python estão em `requirements.txt`. Resumo:

| Pacote | Descrição |
|--------|-----------|
| `openai-whisper` | Transcrição de áudio local |
| `keyboard` | Captura de atalhos globais de teclado |
| `pyautogui` | Simulação de Ctrl+V para colar o texto |
| `pyperclip` | Copia o texto transcrito para a área de transferência |
| `ffmpeg` *(sistema)* | Captura do áudio do microfone via DirectShow (dshow) |

---

## Licença

Este projeto está sob a licença **MIT**.
