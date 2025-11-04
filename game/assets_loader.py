import os
import pygame
import sys

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets")

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
SOUND_EXTS = (".mp3", ".wav", ".ogg", ".flac")


def _resolve_path(path):
    # se estiver rodando empacotado (PyInstaller), use o diretório temporário _MEIPASS
    try:
        if getattr(sys, "_MEIPASS", None):
            base_meipass = sys._MEIPASS
            cand_meipass = os.path.join(base_meipass, path)
            if os.path.exists(cand_meipass):
                return cand_meipass
            # tentar dentro de assets relativo ao _MEIPASS
            cand_meipass2 = os.path.join(base_meipass, "assets", path)
            if os.path.exists(cand_meipass2):
                return cand_meipass2
    except Exception:
        # se algo falhar, continua com resolução normal
        pass

    # se caminho for relativo, interpreta relativo à raiz do projeto (pasta acima de 'game')
    base = os.path.dirname(os.path.dirname(__file__))
    cand = os.path.join(base, path)
    if os.path.exists(cand):
        return cand
    # se for caminho absoluto ou já válido
    if os.path.exists(path):
        return path
    # fallback: tenta apenas o nome dentro assets
    cand2 = os.path.join(base, "assets", path)
    if os.path.exists(cand2):
        return cand2
    return None


def load_image(path, size=None, use_alpha=True):
    """
    Carrega imagem de forma robusta.
    - path: caminho relativo/absoluto ou diretório (se diretório, busca o primeiro arquivo de imagem)
    - size: tuple (w,h) opcional para escalar preservando proporção (encaixe)
    - use_alpha: tenta convert_alpha(), senão convert()
    Retorna Surface ou None.
    """
    if not path:
        return None

    # resolve caminho
    res = _resolve_path(path)
    if res is None:
        # se path aparenta ser pasta, tenta procurar dentro
        if os.path.isdir(path):
            res = find_first_image_in_folder(path)
        else:
            return None

    # se resultado for pasta, busca dentro
    if os.path.isdir(res):
        res = find_first_image_in_folder(res)
        if res is None:
            return None

    try:
        img = pygame.image.load(res)
    except Exception as e:
        print(f"[assets_loader] falha ao carregar imagem {res!r}: {e}")
        return None

    # tentar converter conforme display
    try:
        if use_alpha:
            img = img.convert_alpha()
        else:
            img = img.convert()
    except Exception:
        try:
            img = img.convert()
        except Exception:
            # manter original se não for possível converter
            pass

    # escalar mantendo proporção se solicitado
    if size:
        sw, sh = img.get_size()
        tw, th = size
        scale = min(tw / sw, th / sh)
        nw, nh = max(1, int(sw * scale)), max(1, int(sh * scale))
        try:
            img = pygame.transform.smoothscale(img, (nw, nh))
        except Exception:
            try:
                img = pygame.transform.scale(img, (nw, nh))
            except Exception:
                pass

    return img


def find_first_image_in_folder(folder):
    """
    Busca recursivamente o primeiro arquivo de imagem dentro de 'folder'.
    Retorna caminho completo ou None.
    """
    if not folder:
        return None
    # tenta resolver caminhos com mais tolerância
    res = _resolve_path(folder) or folder
    # se for arquivo explícito válido
    if os.path.isfile(res):
        fn = res.lower()
        if fn.endswith(IMAGE_EXTS):
            return res
        return None
    if not os.path.isdir(res):
        return None
    for root, _, files in os.walk(res):
        for fname in files:
            if fname.lower().endswith(IMAGE_EXTS):
                return os.path.join(root, fname)
    return None


def find_image_by_name(name):
    """
    Procura recursivamente por imagens no diretório assets cujo nome (sem extensão)
    seja exatamente 'name' (case-insensitive) ou que contenham 'name'.
    Retorna o primeiro caminho encontrado ou None.
    """
    if not name:
        return None

    # caminho da pasta assets (projeto)
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    assets_root = os.path.join(base, "assets")
    # 1) procura por nome exato (antes de extensão)
    if os.path.isdir(assets_root):
        for root, _, files in os.walk(assets_root):
            for fname in files:
                fn = fname.lower()
                if fn.endswith(IMAGE_EXTS):
                    if fn.split(".")[0] == name.lower():
                        return os.path.join(root, fname)
    # 2) procura por arquivos que contenham o nome
    if os.path.isdir(assets_root):
        for root, _, files in os.walk(assets_root):
            for fname in files:
                fn = fname.lower()
                if fn.endswith(IMAGE_EXTS) and name.lower() in fn:
                    return os.path.join(root, fname)
    # 3) fallback: procurar no projeto inteiro
    proj_root = os.path.dirname(__file__)
    for root, _, files in os.walk(proj_root):
        for fname in files:
            fn = fname.lower()
            if fn.endswith(IMAGE_EXTS) and name.lower() in fn:
                return os.path.join(root, fname)
    return None


def load_character_preview(folder, size=(120, 120), use_alpha=True):
    """
    Retorna Surface circular de preview (size) a partir da primeira imagem na pasta do personagem.
    Se não houver imagem, retorna None.
    """
    img_path = find_first_image_in_folder(folder)
    if not img_path:
        return None
    img = load_image(img_path, size=size, use_alpha=use_alpha)
    if not img:
        return None

    # criar máscara circular
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    # centralizar imagem se não tiver exatamente o size
    sw, sh = img.get_size()
    x = (w - sw) // 2
    y = (h - sh) // 2
    surf.blit(img, (x, y))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (w // 2, h // 2), min(w, h) // 2)
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return surf


def find_wallpaper_in_player_folder():
    """
    Procura por 'wallpaper' dentro de assets/sprits/player ou assets/sprites/player.
    Retorna caminho completo ou None.
    """
    base = os.path.dirname(os.path.dirname(__file__))
    candidates = [
        os.path.join(base, "assets", "sprits", "player"),
        os.path.join(base, "assets", "sprites", "player"),
        os.path.join(base, "assets", "sprits"),
        os.path.join(base, "assets", "sprites"),
    ]
    for folder in candidates:
        if not os.path.isdir(folder):
            continue
        # procura arquivo explicitamente chamado wallpaper.*
        for fname in os.listdir(folder):
            name, ext = os.path.splitext(fname)
            if name.lower() == "wallpaper" and ext.lower() in IMAGE_EXTS:
                return os.path.join(folder, fname)
        # procura arquivo que contenha 'wallpaper'
        for fname in os.listdir(folder):
            if "wallpaper" in fname.lower() and fname.lower().endswith(IMAGE_EXTS):
                return os.path.join(folder, fname)
    # não encontrou
    return None


def find_first_sound_in_folder(folder):
    """
    Busca recursivamente o primeiro arquivo de áudio dentro de 'folder'.
    Retorna caminho completo ou None.
    """
    if not folder:
        return None
    res = _resolve_path(folder) or folder
    if os.path.isdir(res):
        for root, _, files in os.walk(res):
            for fname in files:
                if fname.lower().endswith(SOUND_EXTS):
                    return os.path.join(root, fname)
    else:
        # se for arquivo direto e existe
        if os.path.isfile(res) and res.lower().endswith(SOUND_EXTS):
            return res
    return None


def load_sound(path):
    """
    Tenta carregar um pygame.mixer.Sound a partir de path (arquivo ou diretório).
    Retorna objeto Sound ou None.
    """
    if not path:
        return None
    # resolve se for pasta
    res = _resolve_path(path) or path
    if os.path.isdir(res):
        res = find_first_sound_in_folder(res)
    if not res or not os.path.isfile(res):
        return None
    try:
        snd = pygame.mixer.Sound(res)
        return snd
    except Exception as e:
        print(f"[assets_loader] falha ao carregar som {res!r}: {e}")
        return None
