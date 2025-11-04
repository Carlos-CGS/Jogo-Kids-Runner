import os
import json
import pygame
from game.assets_loader import (
    find_first_image_in_folder,
    load_image,
    find_wallpaper_in_player_folder,
    find_image_by_name,
)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "data", "config.json")


def _load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_selected(name):
    cfg = _load_config()
    cfg["selected"] = name
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)


def _make_circular_preview_from_surface(img_surf, size, pad=8):
    """
    Retorna Surface size x size com img_surf centralizada e recortada em círculo.
    pad: espaço interno para borda
    """
    if img_surf is None:
        return None
    w, h = size
    target_w = max(1, w - pad * 2)
    target_h = max(1, h - pad * 2)
    # escalar preservando proporção para caber no target
    sw, sh = img_surf.get_size()
    scale = min(target_w / sw, target_h / sh)
    nw = max(1, int(sw * scale))
    nh = max(1, int(sh * scale))
    try:
        scaled = pygame.transform.smoothscale(img_surf, (nw, nh))
    except Exception:
        scaled = pygame.transform.scale(img_surf, (nw, nh))
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    x = (w - nw) // 2
    y = (h - nh) // 2
    surf.blit(scaled, (x, y))
    # máscara circular
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    radius = min(w, h) // 2
    pygame.draw.circle(mask, (255, 255, 255, 255), (w // 2, h // 2), radius)
    # aplica máscara (preserva apenas dentro do círculo)
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return surf


def _search_image_for_name(name, folder=None):
    """
    Procura de forma robusta por um arquivo de imagem que corresponda ao personagem.
    Retorna caminho completo ou None.
    """
    # 1) tentar usar folder configurado
    candidates = []
    if folder:
        candidates.append(os.path.join(os.path.dirname(__file__), folder))
        candidates.append(folder)
    # 2) procurar por arquivos cujo nome contenha o nome do personagem em assets
    base_assets = os.path.join(os.path.dirname(__file__), "assets")
    if os.path.isdir(base_assets):
        for root, _, files in os.walk(base_assets):
            for fname in files:
                fn = fname.lower()
                if fn.endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                    # preferência: nome exato (alegria.png), senão contém (minúsculo)
                    if fn.split(".")[0] == name.lower() or name.lower() in fn:
                        return os.path.join(root, fname)
    # 3) usar find_first_image_in_folder em candidatos comuns
    for cand in candidates:
        try:
            p = find_first_image_in_folder(cand)
            if p:
                # se o arquivo contém o nome do personagem, retorna
                if name.lower() in os.path.basename(p).lower():
                    return p
                # senão, ainda pode ser válido; retornar como fallback
                return p
        except Exception:
            continue
    # 4) busca recursiva no projeto (último recurso)
    root_proj = os.path.dirname(__file__)
    for root, _, files in os.walk(root_proj):
        for fname in files:
            fn = fname.lower()
            if (
                fn.endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif"))
                and name.lower() in fn
            ):
                return os.path.join(root, fname)
    return None


def show_menu(screen, clock, font=None):
    """
    Exibe menu inicial; retorna o nome do personagem escolhido (string) ou None se sair.
    """
    cfg = _load_config()
    chars = cfg.get("characters", {})
    options = list(chars.keys())

    # preparar previews (carregar imagens reais e transformar em circulares)
    small_sz = (120, 120)
    large_sz = (200, 200)
    scaled_small = {}
    scaled_large = {}

    for name in options:
        folder = chars.get(name)
        # primeiro tenta busca local/configurada
        img_path = _search_image_for_name(name, folder)
        # se nada encontrado, tenta busca por nome no assets (alegria.png, tristeza.png, raiva.png)
        if not img_path:
            try:
                img_path = find_image_by_name(name)
            except Exception:
                img_path = None

        img_surf_small = None
        img_surf_large = None
        if img_path:
            # tenta carregar imagens (tamanhos internos menores para padding)
            try:
                img_surf_small = load_image(
                    img_path, size=(small_sz[0] - 16, small_sz[1] - 16), use_alpha=True
                )
            except Exception:
                img_surf_small = None
            try:
                img_surf_large = load_image(
                    img_path, size=(large_sz[0] - 32, large_sz[1] - 32), use_alpha=True
                )
            except Exception:
                img_surf_large = None

        p_small = (
            _make_circular_preview_from_surface(img_surf_small, small_sz)
            if img_surf_small
            else None
        )
        p_large = (
            _make_circular_preview_from_surface(img_surf_large, large_sz)
            if img_surf_large
            else None
        )

        # fallback para placeholder circular com letra
        if p_small is None:
            p_small = pygame.Surface(small_sz, pygame.SRCALPHA)
            pygame.draw.circle(
                p_small,
                (140, 140, 140),
                (small_sz[0] // 2, small_sz[1] // 2),
                small_sz[0] // 2 - 6,
            )
            ftmp = pygame.font.SysFont(None, 28)
            letter = ftmp.render(name[:1].upper(), True, (240, 240, 240))
            p_small.blit(
                letter, letter.get_rect(center=(small_sz[0] // 2, small_sz[1] // 2))
            )
        if p_large is None:
            p_large = pygame.Surface(large_sz, pygame.SRCALPHA)
            pygame.draw.circle(
                p_large,
                (140, 140, 140),
                (large_sz[0] // 2, large_sz[1] // 2),
                large_sz[0] // 2 - 8,
            )
            ftmp = pygame.font.SysFont(None, 36)
            letter = ftmp.render(name[:1].upper(), True, (240, 240, 240))
            p_large.blit(
                letter, letter.get_rect(center=(large_sz[0] // 2, large_sz[1] // 2))
            )

        scaled_small[name] = p_small
        scaled_large[name] = p_large

    # carregar wallpaper (se houver)
    wallpaper_surf = None
    try:
        wp_path = find_wallpaper_in_player_folder()
        if wp_path:
            wp_img = load_image(wp_path, size=None, use_alpha=False)
            if wp_img:
                w, h = screen.get_size()
                sw, sh = wp_img.get_size()
                scale = max(w / sw, h / sh)
                nw, nh = int(sw * scale), int(sh * scale)
                wp_scaled = pygame.transform.smoothscale(wp_img, (nw, nh))
                x = (nw - w) // 2
                y = (nh - h) // 2
                try:
                    wallpaper_surf = wp_scaled.subsurface((x, y, w, h)).copy()
                except Exception:
                    wallpaper_surf = pygame.transform.smoothscale(wp_img, (w, h))
    except Exception:
        wallpaper_surf = None

    if font is None:
        font = pygame.font.SysFont(None, 28)

    selected = 0
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return None
            elif ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RIGHT, pygame.K_d):
                    selected = (selected + 1) % len(options)
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    selected = (selected - 1) % len(options)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    chosen = options[selected]
                    _save_selected(chosen)
                    return chosen
                elif ev.key == pygame.K_ESCAPE:
                    return None
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                w = screen.get_width()
                slot_w = w // len(options)
                idx = mx // slot_w
                if 0 <= idx < len(options):
                    selected = idx
                    chosen = options[selected]
                    _save_selected(chosen)
                    return chosen

        # desenho do fundo
        if wallpaper_surf:
            screen.blit(wallpaper_surf, (0, 0))
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill((25, 25, 40))

        # desenhar opções
        w = screen.get_width()
        h = screen.get_height()
        slot_w = w // len(options)
        for i, name in enumerate(options):
            cx = i * slot_w + slot_w // 2
            if i == selected:
                img = scaled_large[name]
                rect = img.get_rect(center=(cx, h // 2 - 20))
                # glow atrás do círculo selecionado
                glow = pygame.Surface(
                    (rect.width + 20, rect.height + 20), pygame.SRCALPHA
                )
                pygame.draw.circle(
                    glow,
                    (200, 200, 60, 60),
                    (glow.get_width() // 2, glow.get_height() // 2),
                    glow.get_width() // 2,
                )
                screen.blit(glow, (rect.left - 10, rect.top - 10))
                screen.blit(img, rect)
            else:
                img = scaled_small[name]
                rect = img.get_rect(center=(cx, h // 2 + 40))
                screen.blit(img, rect)

            label = font.render(
                name.capitalize(),
                True,
                (240, 240, 240) if i == selected else (180, 180, 180),
            )
            labrect = label.get_rect(
                center=(cx, h // 2 + 120) if i == selected else (cx, h // 2 + 100)
            )
            screen.blit(label, labrect)

        hint = font.render(
            "Use ← → ou clique. Enter para confirmar.", True, (200, 200, 200)
        )
        screen.blit(hint, (20, h - 40))

        pygame.display.flip()
        clock.tick(30)
