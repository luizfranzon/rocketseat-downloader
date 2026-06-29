## ⚠️ Aviso Legal

Este script foi criado para uso pessoal e facilitar o acesso offline a conteúdos que você **já possui legalmente**. O download e a distribuição de conteúdo protegido por direitos autorais sem autorização é ilegal. Use por sua conta e risco, respeitando os **Termos de Serviço** da Rocketseat. Não nos responsabilizamos pelo uso indevido desta ferramenta.

## Como usar

### 1. Pré-requisitos

Antes de começar, instale as dependências abaixo e certifique-se de que estão disponíveis no PATH do sistema:

- **FFmpeg**: https://ffmpeg.org/download.html
- **yt-dlp**: https://github.com/yt-dlp/yt-dlp
- **Python 3.x**: https://www.python.org/downloads/

### 2. Clone o repositório

```bash
git clone https://github.com/luizfranzon/rocketseat-downloader.git
cd rocketseat-downloader
```

### 3. Crie e ative um ambiente virtual Python

```bash
python -m venv .venv
```

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 4. Instale as dependências Python

```bash
pip install -r requirements.txt
```

### 5. Configure o ambiente

Copie o arquivo de exemplo e ajuste se necessário:

```bash
cp .env.example .env
```

O arquivo `.env` possui as seguintes variáveis (os valores padrão já funcionam sem alteração):

| Variável | Padrão | Descrição |
|---|---|---|
| `BASE_API_URL` | `https://skylab-api.rocketseat.com.br` | URL da API da Rocketseat |
| `BASE_APP_URL` | `https://app.rocketseat.com.br` | URL do app da Rocketseat |
| `SESSION_DIR` | `.` (pasta atual) | Diretório onde o arquivo de sessão é salvo |

> **Atenção:** nunca commite o arquivo `.session.json` — ele contém seu token de autenticação. Ele já está no `.gitignore` por padrão.

### 6. Execute o script

```bash
python main.py
```

### 7. Login

No primeiro uso, o script solicitará seu **e-mail e senha da Rocketseat**. Após o login, a sessão é salva localmente e não será necessário autenticar novamente.

### 8. Selecione a formação

Uma lista das suas formações disponíveis será exibida. Digite o número correspondente e pressione `Enter`.

### 9. Selecione os módulos

Com a formação escolhida, o script listará todos os módulos disponíveis. Você pode:

- Digitar `0` para baixar **todos os módulos**
- Digitar os números desejados separados por vírgula (ex: `1, 3, 5`) para baixar apenas os selecionados

### 10. Aguarde o download

Os arquivos serão salvos na pasta `Cursos/`, organizados por formação e módulo. O progresso geral é exibido no formato `[aula atual/total de aulas]` durante o download.
