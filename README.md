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

## Como jogar

- Teclado: ← / A (esquerda), → / D (direita), ↑ (pular), ↓ (deslizar), Esc (sair).
- Se houver suporte de câmera, gestos mapeiam ações (LEFT/RIGHT/JUMP/DUCK).
- Objetivos: desviar/pular obstáculos; a cada 10 colisões o jogo termina (configurável).

## Estrutura mínima de assets (recomendado)

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

## Configuração

- Arquivo: `data/config.json`
  - mapeia personagens para pastas (ex.: "alegria": "assets/sprits/player/alegria")
  - parâmetros:
    - selected: personagem padrão
    - max_collisions: número de colisões até fim de jogo
    - points_per_evade: pontos por desvio

## Execução (desenvolvimento)

1. Criar ambiente virtual (opcional):
   - python -m venv venv
   - venv\Scripts\activate (Windows)
2. Instalar dependências:
   - pip install -r requirements.txt
3. Rodar:
   - python main.py


## Persistência de pontuação

- Pontuações salvas em `data/score.json` ao fim de cada partida (lista ordenada decrescente).



## ⚠️ Aviso:
> Este projeto é apenas para aprendizado e não possui fins comerciais.
> Todos os personagens e elementos originais de *Divertida Mente* pertencem à Disney/Pixar.
> Nenhum material oficial foi utilizado nesta versão pública.



