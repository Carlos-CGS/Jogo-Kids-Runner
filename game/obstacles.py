import os
import random
import pygame

from game.assets_loader import (
    load_image,
    find_first_image_in_folder,
    find_image_by_name,
    find_first_sound_in_folder,
    load_sound,
)
from game.settings import HEIGHT


class Obstacle(pygame.sprite.Sprite):
    """
    Obstacle sprite que carrega uma imagem e possui um tipo:
    - 'need_jump' : deve ser evitado pulando
    - 'must_avoid': deve ser evitado desviando (troca de lane)
    Cada obstáculo conhece a lane index onde nasceu (self.lane).
    """

    def __init__(self, lane_x, lane_idx, image_path=None, w=48, h=48):
        super().__init__()
        self.lane = lane_idx
        self.ob_type = "must_avoid"  # default
        self.image = None

        # tentar carregar imagem específica
        if image_path:
            try:
                img = load_image(image_path, size=(w, h), use_alpha=True)
                if img:
                    self.image = img
            except Exception:
                self.image = None

        # se não carregou, tentar encontrar por nome padrão na pasta assets/obstacles
        if not self.image:
            # tenta encontrar qualquer imagem na pasta obstacles
            cand = os.path.join(os.path.dirname(__file__), "..", "assets", "obstacles")
            imgp = None
            try:
                imgp = find_first_image_in_folder(cand)
            except Exception:
                imgp = None
            if imgp:
                try:
                    self.image = load_image(imgp, size=(w, h), use_alpha=True)
                except Exception:
                    self.image = None

        # fallback: superfície simples
        if not self.image:
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (255, 60, 60), (0, 0, w, h), border_radius=8)

        # determinar tipo pelo nome do arquivo se possível
        try:
            src_name = ""
            if image_path:
                src_name = os.path.basename(image_path).lower()
            elif "imgp" in locals() and imgp:
                src_name = os.path.basename(imgp).lower()
            # mapear substrings para tipo
            if "barra" in src_name or "buraco" in src_name or "buraco" in src_name:
                self.ob_type = "need_jump"
            elif "bola" in src_name or "cometa" in src_name or "cone" in src_name:
                self.ob_type = "must_avoid"
            # se não for possível inferir, manter default must_avoid
        except Exception:
            pass

        # rect - posicionado acima da tela inicialmente
        self.rect = self.image.get_rect()
        self.rect.centerx = lane_x
        self.rect.top = -self.rect.height - random.randint(0, 80)

        # flags para evitar dupla contagem
        self._hit_counted = False
        self._evaded_counted = False

    def update(self, dt, speed=180):
        # mover verticalmente para baixo
        self.rect.y += int(speed * dt)


class ObstacleManager:
    def __init__(self, *args, **kwargs):
        # grupo principal de obstáculos (usado por main.py para detecção)
        self.obstacle_sprites = pygame.sprite.Group()
        # contadores públicos
        self.collision_count = 0
        self.evaded_count = 0
        # controle de spawn — aumenta espaçamento para dar tempo de desviar
        self._spawn_timer = 0.0
        # intervalo base maior; será usado para gerar _next_spawn aleatório
        self._spawn_interval = 1.2  # segundos base (aumentado)
        # intervalo real até o próximo spawn (varia entre _spawn_interval e 1.6x)
        self._next_spawn = random.uniform(
            self._spawn_interval, self._spawn_interval * 1.6
        )
        # evita spawn repetido na mesma lane
        self._last_lane = None
        self._speed = 220  # velocidade de deslocamento (pixels/seg)
        # lanes x - manter compatibilidade com seu layout
        self._lane_x = [300, 450, 600]

        # som de colisão
        self._collision_sound = None

    def _play_collision_sound(self):
        try:
            if not pygame.mixer.get_init():
                return
            if self._collision_sound is None:
                # procurar colisao.mp3 em assets/sounds
                s = find_first_sound_in_folder(
                    os.path.join(os.path.dirname(__file__), "..", "assets", "sounds")
                )
                if s:
                    self._collision_sound = load_sound(s)
            if self._collision_sound:
                self._collision_sound.play()
        except Exception:
            pass

    def update(self, dt):
        # spawn com espaçamento maior e variação aleatória
        self._spawn_timer += dt
        if self._spawn_timer >= self._next_spawn:
            self._spawn_timer = 0.0
            # recalcula próximo intervalo (variação)
            self._next_spawn = random.uniform(
                self._spawn_interval, self._spawn_interval * 1.6
            )
            # escolhe lane evitando repetir a mesma lane consecutiva quando possível
            lane_idx = random.randrange(len(self._lane_x))
            if self._last_lane is not None and len(self._lane_x) > 1:
                # com alta probabilidade força outra lane
                if lane_idx == self._last_lane:
                    alts = [i for i in range(len(self._lane_x)) if i != self._last_lane]
                    lane_idx = random.choice(alts)
            self._last_lane = lane_idx
            lx = self._lane_x[lane_idx]
            # escolher imagem aleatória entre as esperadas (preferir pasta obstacles)
            ob_folder = os.path.join(
                os.path.dirname(__file__), "..", "assets", "obstacles"
            )
            # lista de possíveis nomes preferidos
            candidates_names = [
                "obstaculo.barra",
                "obstaculo.buraco",
                "obstaculo.bola",
                "obstaculo.cometa",
                "obstaculo.cone",
            ]
            chosen_path = None
            # tenta encontrar por nome exato/contendo
            for nm in random.sample(candidates_names, len(candidates_names)):
                p = find_image_by_name(nm)
                if p:
                    chosen_path = p
                    break
            # se não encontrou, tenta qualquer imagem na pasta obstacles
            if not chosen_path:
                try:
                    p2 = find_first_image_in_folder(ob_folder)
                    if p2:
                        chosen_path = p2
                except Exception:
                    chosen_path = None
            obs = Obstacle(lx, lane_idx, image_path=chosen_path, w=64, h=64)
            self.obstacle_sprites.add(obs)

        # atualizar todos os sprites e remover evadidos que saíram da tela
        for spr in list(self.obstacle_sprites):
            try:
                spr.update(dt, speed=self._speed)
            except Exception:
                spr.rect.y += int(self._speed * dt)
            # remover quando fora da tela (passou)
            if spr.rect.top > HEIGHT + 100:
                if not getattr(spr, "_evaded_counted", False):
                    self.evaded_count += 1
                    spr._evaded_counted = True
                try:
                    spr.kill()
                except Exception:
                    pass

    def draw(self, screen):
        self.obstacle_sprites.draw(screen)

    def _get_obstacle_group(self):
        return self.obstacle_sprites

    def check_collision(self, player):
        """
        Verifica colisões com lógica diferenciada:
        - 'need_jump' : pode ser evitado pulando OU desviando para outra lane
        - 'must_avoid': deve ser evitado desviando (troca de lane)
        Atualiza collision_count e evaded_count.
        """
        grp = self._get_obstacle_group()
        if grp is None:
            return None

        hits = []
        evaded = 0
        collisions = 0

        # colisões por spritecollide (rect overlap)
        try:
            hits = pygame.sprite.spritecollide(player, grp, False)
        except Exception:
            hits = []

        if hits:
            for spr in hits:
                # se já contado, skip
                if getattr(spr, "_hit_counted", False) or getattr(
                    spr, "_evaded_counted", False
                ):
                    continue

                # lógica por tipo
                try:
                    if spr.ob_type == "need_jump":
                        # considerado evadido se:
                        #  - jogador está pulando e seus pés estão acima de um limiar (pulo),
                        #  OU
                        #  - jogador mudou de lane (está em lane diferente da do obstáculo)
                        evaded_by_jump = False
                        evaded_by_lane = False
                        try:
                            threshold = max(8, int(spr.rect.height * 0.25))
                            player_feet = player.rect.bottom
                            ob_top = spr.rect.top
                            if player.is_jumping and (
                                player_feet <= ob_top + threshold
                            ):
                                evaded_by_jump = True
                        except Exception:
                            evaded_by_jump = False

                        try:
                            if (
                                getattr(player, "current_lane", None) is not None
                                and getattr(spr, "lane", None) is not None
                            ):
                                if player.current_lane != spr.lane:
                                    evaded_by_lane = True
                        except Exception:
                            evaded_by_lane = False

                        if evaded_by_jump or evaded_by_lane:
                            self.evaded_count += 1
                            evaded += 1
                            spr._evaded_counted = True
                        else:
                            # contado como colisão
                            self.collision_count += 1
                            collisions += 1
                            spr._hit_counted = True
                            self._play_collision_sound()
                    else:
                        # must_avoid: se player não está na mesma lane -> evadiu, senão colisão
                        if getattr(
                            player, "current_lane", None
                        ) is not None and player.current_lane != getattr(
                            spr, "lane", None
                        ):
                            self.evaded_count += 1
                            evaded += 1
                            spr._evaded_counted = True
                        else:
                            self.collision_count += 1
                            collisions += 1
                            spr._hit_counted = True
                            self._play_collision_sound()
                except Exception:
                    # fallback: contar como colisão
                    if not getattr(spr, "_hit_counted", False):
                        self.collision_count += 1
                        collisions += 1
                        spr._hit_counted = True
                        self._play_collision_sound()

                # remover obstáculo da tela para evitar dupla contagem
                try:
                    spr.kill()
                except Exception:
                    pass

            # retornar sinais conforme antes
            if collisions > 0:
                return "hit"
            if evaded > 0:
                return evaded

        return None

    def clear(self):
        try:
            for spr in list(self.obstacle_sprites):
                try:
                    spr.kill()
                except Exception:
                    pass
            self.obstacle_sprites.empty()
        except Exception:
            pass
        self.collision_count = 0
        self.evaded_count = 0
