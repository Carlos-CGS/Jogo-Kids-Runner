import sys
import os
import json
import pygame
import traceback
import time
from game.player import Player
from game.obstacles import ObstacleManager
from game.camera_control import CameraController
from game.settings import *
from start_menu import show_menu
from game.assets_loader import (
    find_first_image_in_folder,
    find_first_sound_in_folder,
    load_sound,
    load_image,
    find_image_by_name,
)


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "data", "config.json")
SCORE_PATH = os.path.join(os.path.dirname(__file__), "data", "score.json")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_scores():
    try:
        with open(SCORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_score_entry(entry):
    scores = load_scores()
    scores.append(entry)
    # opcional: manter apenas top N ou ordenar
    try:
        scores_sorted = sorted(scores, key=lambda e: e.get("score", 0), reverse=True)
    except Exception:
        scores_sorted = scores
    try:
        with open(SCORE_PATH, "w", encoding="utf-8") as f:
            json.dump(scores_sorted, f, indent=4, ensure_ascii=False)
    except Exception:
        pass


def show_game_over_popup(screen, clock, score):
    """
    Exibe popup de fim de jogo usando imagem 'vencedor' como fundo do box (se existir).
    Aguarda Enter ou clique para continuar.
    """
    # fontes maiores
    font_title = pygame.font.SysFont(None, 56)
    font_body = pygame.font.SysFont(None, 34)
    w, h = screen.get_size()

    # função auxiliar para desenhar texto com contorno (white outline, black fill)
    def draw_text_outline(
        surface,
        text,
        font,
        center,
        fg=(0, 0, 0),
        outline=(255, 255, 255),
        outline_width=2,
    ):
        # desenha contorno (várias posições ao redor)
        for ox in range(-outline_width, outline_width + 1):
            for oy in range(-outline_width, outline_width + 1):
                if ox == 0 and oy == 0:
                    continue
                s = font.render(text, True, outline)
                r = s.get_rect(center=(center[0] + ox, center[1] + oy))
                surface.blit(s, r)
        # desenha texto principal
        s_main = font.render(text, True, fg)
        r_main = s_main.get_rect(center=center)
        surface.blit(s_main, r_main)

    # tentar localizar imagem 'vencedor' no diretório assets (recursivo)
    winner_path = None
    try:
        assets_root = os.path.join(os.path.dirname(__file__), "assets")
        if os.path.isdir(assets_root):
            for root, _, files in os.walk(assets_root):
                for fname in files:
                    if ("vencedor" in fname.lower()) or ("winner" in fname.lower()):
                        if fname.lower().endswith(
                            (".png", ".jpg", ".jpeg", ".bmp", ".gif")
                        ):
                            winner_path = os.path.join(root, fname)
                            break
                if winner_path:
                    break
    except Exception:
        winner_path = None

    # preparar overlay para escurecer o fundo da tela
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))

    # texto
    msg_title = font_title.render("Fim de Jogo!", True, (255, 255, 255))
    msg_score = font_body.render(f"Pontuação: {score}", True, (255, 255, 255))
    msg_hint = font_body.render(
        "Pressione Enter para voltar ao menu", True, (200, 200, 200)
    )

    # criar box
    box_w, box_h = 420, 220
    box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)

    # se encontrou imagem, carregar e inserir como fundo do box
    winner_img = None
    if winner_path:
        try:
            from game.assets_loader import load_image

            winner_img = load_image(winner_path, size=(box_w, box_h), use_alpha=True)
        except Exception:
            winner_img = None

    if winner_img:
        try:
            box.blit(winner_img, (0, 0))
        except Exception:
            pygame.draw.rect(box, (30, 30, 40), box.get_rect(), border_radius=12)
    else:
        pygame.draw.rect(box, (30, 30, 40), box.get_rect(), border_radius=12)

    # borda do box
    pygame.draw.rect(box, (200, 200, 60), box.get_rect(), 3, border_radius=12)

    # desenhar textos sobre o box usando contorno branco e texto preto
    draw_text_outline(
        box,
        "Fim de Jogo!",
        font_title,
        (box_w // 2, 50),
        fg=(0, 0, 0),
        outline=(255, 255, 255),
        outline_width=2,
    )
    draw_text_outline(
        box,
        f"Pontuação: {score}",
        font_body,
        (box_w // 2, 110),
        fg=(0, 0, 0),
        outline=(255, 255, 255),
        outline_width=2,
    )
    draw_text_outline(
        box,
        "Pressione Enter para voltar ao menu",
        font_body,
        (box_w // 2, 170),
        fg=(0, 0, 0),
        outline=(255, 255, 255),
        outline_width=1,
    )

    # loop do popup
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    return
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                return

        screen.blit(overlay, (0, 0))
        screen.blit(box, ((w - box_w) // 2, (h - box_h) // 2))
        pygame.display.flip()
        clock.tick(30)


def find_sprite_for(selected_name):
    # tenta obter via configuração primeiro
    cfg = load_config()
    chars = cfg.get("characters", {})
    folder = chars.get(selected_name)

    candidates = []
    if folder:
        candidates.append(os.path.join(os.path.dirname(__file__), folder))
        candidates.append(folder)
    # caminhos padrão
    candidates.append(
        os.path.join(
            os.path.dirname(__file__), "assets", "sprits", "player", selected_name
        )
    )
    candidates.append(
        os.path.join(
            os.path.dirname(__file__), "assets", "sprites", "player", selected_name
        )
    )
    candidates.append(
        os.path.join(os.path.dirname(__file__), "assets", "sprits", selected_name)
    )
    candidates.append(
        os.path.join(os.path.dirname(__file__), "assets", "sprites", selected_name)
    )

    # tentar localizar primeira imagem em cada candidato
    for cand in candidates:
        try:
            p = find_first_image_in_folder(cand)
            if p:
                # se o nome do arquivo contém o nome do personagem, preferir
                if selected_name.lower() in os.path.basename(p).lower():
                    return p
                # senão, ainda é um bom candidato — retornar como fallback
                return p
        except Exception:
            continue

    # usar busca por nome específico em assets (mais agressiva)
    try:
        pn = find_image_by_name(selected_name)
        if pn:
            return pn
    except Exception:
        pass

    # fallback: procurar recursivamente em assets por pastas contendo o nome do personagem
    base_assets = os.path.join(os.path.dirname(__file__), "assets")
    if os.path.isdir(base_assets):
        for root, _, files in os.walk(base_assets):
            if selected_name.lower() in root.lower():
                for fname in files:
                    if fname.lower().endswith(
                        (".png", ".jpg", ".jpeg", ".bmp", ".gif")
                    ):
                        return os.path.join(root, fname)

    # tentativa final: busca recursiva no projeto
    root_proj = os.path.dirname(__file__)
    for root, _, files in os.walk(root_proj):
        if selected_name.lower() in root.lower():
            for fname in files:
                if fname.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                    return os.path.join(root, fname)

    return None


def _extract_obstacle_counters(obstacles):
    """
    Tenta extrair contadores úteis de ObstacleManager.
    Retorna (collisions_count, evaded_count) ou (None, None) se não encontrar.
    """
    # possíveis nomes para colisões
    collision_names = (
        "collisions",
        "collision_count",
        "collisions_count",
        "hits",
        "hit_count",
    )
    # possíveis nomes para evitações/passagens
    evade_names = (
        "evaded",
        "evaded_count",
        "passed",
        "passed_count",
        "passed_obstacles",
        "avoided",
    )

    coll = None
    evd = None

    for name in collision_names:
        if hasattr(obstacles, name):
            try:
                coll = int(getattr(obstacles, name))
                break
            except Exception:
                continue

    for name in evade_names:
        if hasattr(obstacles, name):
            try:
                evd = int(getattr(obstacles, name))
                break
            except Exception:
                continue

    return coll, evd


def _safe_cleanup_obstacles(obstacles):
    """Tenta limpar ou encerrar o ObstacleManager sem lançar erro se métodos não existirem."""
    # tenta métodos comuns
    for meth in ("clear", "empty", "kill", "stop", "shutdown", "dispose"):
        fn = getattr(obstacles, meth, None)
        if callable(fn):
            try:
                fn()
            except Exception:
                # ignora falhas de cleanup
                pass
    # também tenta apagar grupos internos, se houver
    try:
        for grp in ("_obstacle_sprites", "_passed_sprites"):
            objs = getattr(obstacles, grp, None)
            if objs:
                try:
                    objs.empty()
                except Exception:
                    pass
    except Exception:
        pass


def _find_obstacle_group(obstacles):
    """
    Tenta localizar um pygame.sprite.Group dentro do ObstacleManager.
    Retorna o primeiro grupo encontrado ou None.
    """
    possible = (
        "obstacles",
        "obstacle_sprites",
        "_obstacle_sprites",
        "sprites",
        "group",
        "all_sprites",
        "obstacle_group",
    )
    for name in possible:
        grp = getattr(obstacles, name, None)
        if isinstance(grp, pygame.sprite.Group):
            return grp
    # fallback: procura por qualquer atributo do tipo Group
    for name in dir(obstacles):
        attr = getattr(obstacles, name)
        if isinstance(attr, pygame.sprite.Group):
            return attr
    return None


def main():
    pygame.init()
    # inicializa mixer (safe)
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
    except Exception:
        # se falhar, continua sem áudio
        print("[WARN] falha ao inicializar mixer pygame (áudio pode não funcionar)")

    print("[DEBUG] pygame iniciado")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Kids Runner 🎮")
    clock = pygame.time.Clock()

    cfg = load_config()
    max_collisions = cfg.get("max_collisions", 10)
    points_per_evade = cfg.get("points_per_evade", 10)
    print(
        f"[DEBUG] config: max_collisions={max_collisions}, points_per_evade={points_per_evade}"
    )

    # Loop principal que permite voltar ao menu ao fim da partida
    while True:
        try:
            # mostrar menu inicial e obter personagem selecionado
            print("[DEBUG] exibindo menu de seleção")
            chosen = show_menu(screen, clock)
            print(f"[DEBUG] retorno do menu: {chosen!r}")
            if chosen is None:
                print("[DEBUG] usuário saiu no menu. Encerrando.")
                pygame.quit()
                return

            sprite_path = find_sprite_for(chosen)
            print(f"[DEBUG] sprite selecionado: {sprite_path}")

            # criar objetos do jogo com captura de exceção para expor erros silenciosos
            try:
                player = Player(sprite_path)
                obstacles = ObstacleManager()
                camera = CameraController()
            except Exception:
                print("[ERROR] falha ao criar Player/ObstacleManager/Camera:")
                traceback.print_exc()
                # se falhar na criação, volta ao menu
                continue

            print("[DEBUG] Player/ObstacleManager/Camera criados com sucesso")

            # tenta iniciar música de fundo para a rodada
            try:
                music_path = None
                candidates = [
                    os.path.join(
                        os.path.dirname(__file__), "assets", "sounds", "musicGame.mp3"
                    ),
                    os.path.join(
                        os.path.dirname(__file__), "assets", "sounds", "musicGame.mp3"
                    ),
                    os.path.join(
                        os.path.dirname(__file__), "assets", "sounds", "music.mp3"
                    ),
                    os.path.join(os.path.dirname(__file__), "assets", "sounds"),
                ]
                for c in candidates:
                    p = find_first_sound_in_folder(c)
                    if p:
                        music_path = p
                        break
                if music_path and pygame.mixer.get_init():
                    try:
                        pygame.mixer.music.load(music_path)
                        pygame.mixer.music.set_volume(0.6)
                        pygame.mixer.music.play(-1)
                        print(f"[DEBUG] música de fundo tocando: {music_path}")
                    except Exception:
                        print("[WARN] falha ao tocar música de fundo")
            except Exception:
                pass

            # carregar som de pulo (jump) para usar durante a rodada
            jump_sound = None
            try:
                js_candidates = [
                    os.path.join(
                        os.path.dirname(__file__), "assets", "sounds", "jump.mp3"
                    ),
                    os.path.join(
                        os.path.dirname(__file__), "assets", "sounds", "jump.wav"
                    ),
                    os.path.join(os.path.dirname(__file__), "assets", "sounds"),
                ]
                for c in js_candidates:
                    p = find_first_sound_in_folder(c)
                    if p and (
                        "jump" in os.path.basename(p).lower() or c.endswith("sounds")
                    ):
                        # tenta carregar o primeiro arquivo 'jump' ou qualquer som na pasta (fallback)
                        s = load_sound(p)
                        if s:
                            jump_sound = s
                            break
            except Exception:
                jump_sound = None

            # --- carregar imagem de fundo "estrada" ---
            road_surf = None
            try:
                assets_root = os.path.join(os.path.dirname(__file__), "assets")
                road_path = None
                if os.path.isdir(assets_root):
                    for root, _, files in os.walk(assets_root):
                        for fname in files:
                            if "estrada" in fname.lower() and fname.lower().endswith(
                                (".png", ".jpg", ".jpeg", ".bmp", ".gif")
                            ):
                                road_path = os.path.join(root, fname)
                                break
                        if road_path:
                            break
                # fallback: usar find_first_image_in_folder em locais prováveis
                if not road_path:
                    for cand in (
                        os.path.join(os.path.dirname(__file__), "assets", "sprites"),
                        os.path.join(os.path.dirname(__file__), "assets", "sprits"),
                        os.path.join(os.path.dirname(__file__), "assets"),
                    ):
                        try:
                            p = find_first_image_in_folder(cand)
                            if p and "estrada" in os.path.basename(p).lower():
                                road_path = p
                                break
                        except Exception:
                            continue
                if road_path:
                    # carrega e escala para o tamanho da tela
                    road_surf = load_image(
                        road_path, size=(WIDTH, HEIGHT), use_alpha=False
                    )
            except Exception:
                road_surf = None
            # --- fim carregar estrada ---

            collisions = 0
            score = 0

            # inicializar prev a partir dos contadores do manager (agora sempre presentes)
            prev_coll_count = getattr(obstacles, "collision_count", 0) or 0
            prev_evade_count = getattr(obstacles, "evaded_count", 0) or 0

            running = True
            # criação de player/obstacles/camera e loop da rodada
            try:
                while running:
                    dt = clock.tick(FPS) / 1000
                    # Eventos (fechar janela ou apertar ESC)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        elif (
                            event.type == pygame.KEYDOWN
                            and event.key == pygame.K_ESCAPE
                        ):
                            running = False

                    # Controles por teclado (fallback)
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT]:
                        player.switch_lane(-1)
                    if keys[pygame.K_RIGHT]:
                        player.switch_lane(+1)
                    if keys[pygame.K_UP]:
                        player.jump()
                        if jump_sound:
                            try:
                                jump_sound.play()
                            except Exception:
                                pass
                    if keys[pygame.K_DOWN]:
                        player.slide()

                    # Controles por câmera
                    action = camera.get_action()
                    if action == "LEFT":
                        player.switch_lane(-1)
                    elif action == "RIGHT":
                        player.switch_lane(+1)
                    elif action == "JUMP":
                        player.jump()
                        if jump_sound:
                            try:
                                jump_sound.play()
                            except Exception:
                                pass
                    elif action == "DUCK":
                        player.slide()

                    # Atualizações
                    player.update(dt)
                    obstacles.update(dt)

                    # checa colisões/evitações via método do manager
                    try:
                        res = obstacles.check_collision(player)
                    except Exception:
                        res = None

                    # interpretar retorno direto (compatibilidade)
                    if res == "hit":
                        # manager já incrementou collision_count; we'll read delta below
                        pass
                    elif isinstance(res, int) and res > 0:
                        # evadidos retornados diretamente; atualizar score
                        score += points_per_evade * res

                    # ler contadores do ObstacleManager e aplicar deltas
                    curr_coll = getattr(obstacles, "collision_count", None)
                    curr_evade = getattr(obstacles, "evaded_count", None)

                    if curr_coll is not None:
                        delta = curr_coll - prev_coll_count
                        if delta > 0:
                            collisions += delta
                        prev_coll_count = curr_coll

                    if curr_evade is not None:
                        delta_ev = curr_evade - prev_evade_count
                        if delta_ev > 0:
                            score += points_per_evade * delta_ev
                        prev_evade_count = curr_evade

                    # Renderização e HUD
                    # desenha fundo estrada se disponível, senão cor sólida
                    if road_surf:
                        try:
                            screen.blit(road_surf, (0, 0))
                        except Exception:
                            screen.fill(BG_COLOR)
                    else:
                        screen.fill(BG_COLOR)
                    obstacles.draw(screen)
                    player.draw(screen)

                    hud_font = pygame.font.SysFont(None, 26)
                    hud_score = hud_font.render(
                        f"Pontuação: {score}", True, (255, 255, 255)
                    )
                    remaining = max(0, max_collisions - collisions)
                    hud_lives = hud_font.render(
                        f"Colisões: {collisions}/{max_collisions} (restam {remaining})",
                        True,
                        (255, 200, 60),
                    )
                    screen.blit(hud_score, (16, 16))
                    screen.blit(hud_lives, (16, 46))

                    pygame.display.flip()

                    # fim de jogo
                    if collisions >= max_collisions:
                        # parar música de fundo
                        try:
                            if pygame.mixer.get_init():
                                pygame.mixer.music.stop()
                        except Exception:
                            pass

                        # tocar som de game over (se encontrado)
                        gameover_sound = None
                        try:
                            candidates = [
                                os.path.join(
                                    os.path.dirname(__file__),
                                    "assets",
                                    "sounds",
                                    "gameOver.mp3",
                                ),
                                os.path.join(
                                    os.path.dirname(__file__),
                                    "assets",
                                    "sounds",
                                    "gameover.mp3",
                                ),
                                os.path.join(
                                    os.path.dirname(__file__), "assets", "sounds"
                                ),
                            ]
                            for c in candidates:
                                p = find_first_sound_in_folder(c)
                                if p:
                                    s = load_sound(p)
                                    if s:
                                        gameover_sound = s
                                        break
                            if gameover_sound and pygame.mixer.get_init():
                                try:
                                    gameover_sound.set_volume(0.9)
                                    gameover_sound.play()
                                except Exception:
                                    pass
                        except Exception:
                            pass

                        # exibir popup (som será reproduzido durante o popup)
                        show_game_over_popup(screen, clock, score)

                        # parar som de game over após o popup
                        try:
                            if gameover_sound:
                                gameover_sound.stop()
                        except Exception:
                            pass

                        # salvar pontuação
                        entry = {
                            "score": score,
                            "player": chosen,
                            "time": int(time.time()),
                        }
                        save_score_entry(entry)
                        running = False

            finally:
                # Finalização segura da rodada (sempre executa)
                try:
                    camera.close()
                except Exception:
                    pass
                try:
                    player.kill()
                except Exception:
                    pass
                # usar clear() implementado no manager
                try:
                    obstacles.clear()
                except Exception:
                    _safe_cleanup_obstacles(obstacles)
                # parar música de fundo ao final da rodada
                try:
                    if pygame.mixer.get_init():
                        pygame.mixer.music.stop()
                except Exception:
                    pass
                print("[DEBUG] limpeza da rodada concluída, voltando ao menu")

        except Exception:
            # trata erros não previstos na rotina da rodada e volta ao menu
            print("[ERROR] exceção na rodada principal:")
            traceback.print_exc()
            # continue para mostrar o menu novamente
            continue


if __name__ == "__main__":
    main()
