import os
import pygame
from game.assets_loader import load_image
from game.settings import LANES


class Player(pygame.sprite.Sprite):
    def __init__(self, image_path=None, pos=None, *args, **kwargs):
        """
        image_path: caminho para a imagem do personagem (pode ser None)
        pos: opcional (topleft) — se None, posiciona na lane central e no chão (GROUND_Y)
        """
        super().__init__(*args, **kwargs)

        # tamanho do jogador
        w, h = 48, 48

        # tenta carregar a imagem escolhida pelo menu e usá-la diretamente
        loaded = None
        if image_path:
            try:
                loaded = load_image(image_path, size=(w, h), use_alpha=True)
            except Exception:
                loaded = None

        if loaded:
            sw, sh = loaded.get_size()
            if (sw, sh) != (w, h):
                try:
                    loaded = pygame.transform.smoothscale(loaded, (w, h))
                except Exception:
                    loaded = pygame.transform.scale(loaded, (w, h))
            self.image = loaded
        else:
            # fallback: quadrado vermelho
            base = pygame.Surface((w, h), pygame.SRCALPHA)
            base.fill((200, 50, 50))
            self.image = base

        # determinar posição vertical do chão (GROUND_Y) se existir em settings
        try:
            from game.settings import GROUND_Y

            ground_y = GROUND_Y
        except Exception:
            ground_y = 500  # fallback

        # determinar lane inicial (centro) e posicao x via LANES
        try:
            self.current_lane = 1 if len(LANES) > 1 else 0
            start_x = LANES[self.current_lane]
        except Exception:
            # fallback: usar posição fornecida ou 100
            self.current_lane = 0
            start_x = pos[0] if pos else 100

        # posiciona o player com bottom no ground_y
        self.rect = self.image.get_rect()
        self.rect.centerx = start_x
        self.rect.bottom = ground_y

        # estado de movimento
        self._vel_y = 0
        self.is_jumping = False
        self.is_sliding = False

        # parâmetros de física (podem ser ajustados)
        try:
            from game.settings import JUMP_VELOCITY, GRAVITY

            self._jump_velocity = JUMP_VELOCITY
            self._gravity = GRAVITY
        except Exception:
            self._jump_velocity = -16  # pixels por frame inicial
            self._gravity = 1.0  # incremento por frame

    def switch_lane(self, direction):
        new_lane = self.current_lane + direction
        try:
            if 0 <= new_lane < len(LANES):
                self.current_lane = new_lane
                self.rect.centerx = LANES[self.current_lane]
        except Exception:
            # fallback: ajustar em pixels
            self.rect.x += direction * 100

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self._vel_y = self._jump_velocity

    def slide(self):
        # ...existing code...
        pass

    def update(self, dt):
        # atualiza pulo por frame (mantém compatibilidade com update simples)
        if self.is_jumping:
            # aplica velocidade vertical
            self.rect.y += int(self._vel_y)
            # aplica "gravidade"
            self._vel_y += self._gravity
            # aterrissagem: detectar chão (GROUND_Y)
            try:
                from game.settings import GROUND_Y

                ground_y = GROUND_Y
            except Exception:
                ground_y = 500
            if self.rect.bottom >= ground_y:
                self.rect.bottom = ground_y
                self.is_jumping = False
                self._vel_y = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)
