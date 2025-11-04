# 🧠 Jogo - Kids Runner

 🎮 Divertida Mente Runner (Projeto Educacional)

Este projeto foi desenvolvido por **Carlos Garcia** como parte de seus estudos em **Python, Pygame e Visão Computacional (MediaPipe)**.

Trata-se de um jogo no estilo *Subway Surfers*, onde o jogador controla o personagem com **movimentos corporais captados pela webcam**, simulando um *endless runner* divertido e interativo.

## 🚀 Tecnologias Utilizadas
- 🐍 **Python 3**
- 🎮 **Pygame** — motor de jogo 2D
- 👁️ **OpenCV + MediaPipe** — detecção de movimento e pose corporal
- 🎨 **Sprites e sons personalizados** (sem uso comercial)

## 🎯 Objetivo
Projeto criado **para fins de aprendizado**, explorando conceitos de:
- Lógica de jogos 2D
- Estrutura de pastas profissional
- Processamento de imagem em tempo real
- Integração de IA com jogos


- Jogo em Python + Pygame inspirado em "endless runner".
- Menu com seleção de personagem (alegria, tristeza, raiva) mostrando previews circulares.
- Player usa a imagem selecionada; obstáculos e sons carregados de `assets/`.
- Contagem de colisões/evitações, pontuação por desvio e popup de fim de jogo com imagem.

Como jogar

- Teclado: ← / A (esquerda), → / D (direita), ↑ (pular), ↓ (deslizar), Esc (sair).
- Se houver suporte de câmera, gestos mapeiam ações (LEFT/RIGHT/JUMP/DUCK).
- Objetivos: desviar/pular obstáculos; a cada 10 colisões o jogo termina (configurável).

Estrutura mínima de assets (recomendado)

- assets/
  - sprites/ ou sprits/
    - player/
      - alegria/ (ou alegria.png)
      - tristeza/ (ou tristeza.png)
      - raiva/ (ou raiva.png)
      - wallpaper.(jpg|png) (opcional)
    - obstacles/
      - obstaculo.barra.png
      - obstaculo.buraco.png
      - obstaculo.bola.png
      - obstaculo.cometa.png
      - obstaculo.cone.png
  - sounds/
    - musicGame.mp3
    - colisao.mp3
    - jump.mp3
    - gameOver.mp3

Configuração

- Arquivo: `data/config.json`
  - mapeia personagens para pastas (ex.: "alegria": "assets/sprits/player/alegria")
  - parâmetros:
    - selected: personagem padrão
    - max_collisions: número de colisões até fim de jogo
    - points_per_evade: pontos por desvio

Execução (desenvolvimento)

1. Criar ambiente virtual (opcional):
   - python -m venv venv
   - venv\Scripts\activate (Windows)
2. Instalar dependências:
   - pip install -r requirements.txt
3. Rodar:
   - python main.py

Build (gerar executável com PyInstaller)

1. Instalar PyInstaller:
   - pip install pyinstaller
2. Comando sugerido (onedir — recomendado para testes):
   - pyinstaller --noconfirm --onedir --windowed --add-data "assets;assets" --add-data "data;data" main.py
3. Para um único arquivo:
   - substitua `--onedir` por `--onefile`.
4. Observação:
   - O loader de assets já trata `sys._MEIPASS` para rodar dentro do executável.
   - Teste primeiro com `--onedir` para facilitar depuração.

Depuração rápida

- Se imagens não aparecem no menu:
  - Verifique nomes e pastas dentro de `assets/` (use apenas letras minúsculas sem espaços).
  - Verifique logs [DEBUG] no terminal.
- Se sons não tocam:
  - Confirme que `pygame.mixer` inicializou (ver mensagens no console).
  - Verifique formatos dos arquivos (mp3/wav/ogg).
- Se colisões não são detectadas:
  - Confirme que `game/player.py` define `rect` e que obstáculos são `pygame.sprite.Sprite`.

Boas práticas

- Use nomes consistentes (ex.: `alegria.png`, `tristeza.png`, `raiva.png`, `obstaculo.barra.png`).
- Mantém pastas `assets/` e `data/` junto ao executável ou inclua via `--add-data`.

Persistência de pontuação

- Pontuações salvas em `data/score.json` ao fim de cada partida (lista ordenada decrescente).

Créditos / Observações finais

- Projeto original e ajustes por você.
- Ferramentas: Python, Pygame, PyInstaller (opcional).
- Posso gerar um arquivo `build_exe.bat` e um `.spec` para PyInstaller se desejar automação do build.

