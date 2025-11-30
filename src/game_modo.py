# ========================================
#   TELA DE SELEÇÃO DE JOGO (WEB READY)
# ========================================

import pygame
import os
import math
import random
import sys
import asyncio  # <--- ESSENCIAL

from src.audio_manager import audio_manager
from src.utils import load_font

# ---------- util helpers ----------
def _blur_surface(surface, amount=10):
    if amount < 1:
        return surface
    w, h = surface.get_size()
    scale = 1.0 / amount
    small = (max(1, int(w * scale)), max(1, int(h * scale)))
    surf_small = pygame.transform.smoothscale(surface, small)
    return pygame.transform.smoothscale(surf_small, (w, h))

# ---------- Partículas ----------
class Particle:
    def __init__(self, w, h):
        self.reset(w, h)

    def reset(self, w, h):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.size = random.uniform(1.5, 5.0)
        self.color = random.choice([(255,215,0),(255,223,80),(255,191,0)])
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.6, -0.15)
        self.alpha = random.randint(120, 230)
        self.decay = random.uniform(0.4, 1.6)

    def update(self, dt, w, h):
        mul = dt * 0.06
        self.x += self.vx * mul
        self.y += self.vy * mul
        self.alpha -= self.decay * (mul * 0.5)
        self.size = max(0.2, self.size - 0.01 * mul)
        if self.y < -10 or self.alpha <= 0 or self.x < -50 or self.x > w + 50:
            self.reset(w, h)
            self.y = h + random.uniform(0, 40)

    def draw(self, screen):
        if self.alpha <= 0 or self.size <= 0:
            return
        surf = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
        col = (self.color[0], self.color[1], self.color[2], int(self.alpha))
        pygame.draw.circle(surf, col, (int(self.size), int(self.size)), int(self.size))
        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))


# ---------- Botão Animado ----------
class AnimButton:
    def __init__(self, text, center, font, base_color, hover_color, fixed_size=None):
        self.text = text
        self.center = center
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.scale = 1.0
        self.target_scale = 1.0
        self.fixed_size = fixed_size
        self._render()

    def _render(self):
        self.text_surf = self.font.render(self.text, True, (255, 255, 255))
        
        if self.fixed_size:
            self.width, self.height = self.fixed_size
        else:
            w, h = self.text_surf.get_size()
            self.width = w + 40
            self.height = h + 20
            
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.center

    def update_pos(self, center, fixed_size=None):
        self.center = center
        if fixed_size:
            self.fixed_size = fixed_size
            self._render()
        self.rect.center = center

    def draw(self, screen, mouse_pos):
        hover = self.rect.collidepoint(mouse_pos)
        self.target_scale = 1.05 if hover else 1.0
        self.scale += (self.target_scale - self.scale) * 0.2

        cur_w = int(self.width * self.scale)
        cur_h = int(self.height * self.scale)
        r = pygame.Rect(0, 0, cur_w, cur_h)
        r.center = self.center

        shadow = r.copy()
        shadow.move_ip(4, 4)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow, border_radius=12)

        color = self.hover_color if hover else self.base_color
        pygame.draw.rect(screen, color, r, border_radius=12)
        
        gloss = pygame.Surface((r.width, r.height // 2), pygame.SRCALPHA)
        gloss.fill((255, 255, 255, 20))
        screen.blit(gloss, (r.x, r.y))

        pygame.draw.rect(screen, (255, 255, 255), r, 2, border_radius=12)
        screen.blit(self.text_surf, self.text_surf.get_rect(center=r.center))

    def clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                audio_manager.play_sfx_if_exists("click")
                return True
        return False


# ---------- Classe de Layout do Modo Livre ----------
class FreeModeUI:
    def __init__(self, screen):
        self.screen = screen
        self.w, self.h = screen.get_size()
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.bg_path = os.path.join(base, "assets", "background", "game_livre.png")
        
        self._load_resources()
        
        try:
            from src.minigames.show_do_bilhao import run_show_do_bilhao
            from src.minigames.batalha_naval import run_batalha_naval
            from src.minigames.maleta_certa import run_maleta_certa
            from src.minigames.roleta_risco import roleta_risco
            from src.minigames.perseguicao import run_perseguicao
            from src.minigames.stop import run_stop
            
            self.minigames = [
                ("Show do Bilhão", run_show_do_bilhao, "musica_show_do_bilhao"),
                ("Batalha Naval", run_batalha_naval, "musica_batalha_naval"),
                ("Maleta Certa", run_maleta_certa, "musica_maleta_certa"),
                ("Perseguição", run_perseguicao, "musica_perseguicao"),
                ("STOP", run_stop, "musica_stop"),
            ]
        except Exception as e:
            print(f"Erro ao importar minigames: {e}")
            self.minigames = []

        self._create_buttons()

    def _load_resources(self):
        self.w, self.h = self.screen.get_size()
        try:
            if os.path.exists(self.bg_path):
                raw = pygame.image.load(self.bg_path).convert()
                self.bg = pygame.transform.smoothscale(raw, (self.w, self.h))
                self.bg = _blur_surface(self.bg, 8)
            else:
                raise FileNotFoundError
        except:
            self.bg = pygame.Surface((self.w, self.h))
            self.bg.fill((20, 20, 35))

        self.font_title = load_font(int(self.h * 0.08))
        self.font_btn = load_font(int(self.h * 0.035))
        self.particles = [Particle(self.w, self.h) for _ in range(25)]

    def _create_buttons(self):
        cx = self.w // 2
        btn_width = min(int(self.w * 0.5), 500)
        btn_height = int(self.h * 0.08)
        fixed_size = (btn_width, btn_height)
        
        num_games = len(self.minigames)
        spacing = 15
        total_block_height = (num_games * btn_height) + ((num_games - 1) * spacing)
        
        area_top = int(self.h * 0.15)
        area_bottom = int(self.h * 0.85)
        area_center = (area_top + area_bottom) // 2
        start_y = area_center - (total_block_height // 2) + (btn_height // 2)
        
        self.game_buttons = []
        for i, (name, func, music) in enumerate(self.minigames):
            y_pos = start_y + i * (btn_height + spacing)
            btn = AnimButton(name, (cx, y_pos), self.font_btn, (60, 60, 100), (100, 100, 180), fixed_size=fixed_size)
            btn.action = func
            btn.music_key = music
            self.game_buttons.append(btn)
            
        nav_y = self.h - int(self.h * 0.08)
        nav_w = int(btn_width * 0.45)
        nav_h = int(btn_height * 0.9)
        nav_size = (nav_w, nav_h)
        nav_spacing = int(nav_w * 1.2)
        
        self.btn_back_mode = AnimButton("VOLTAR", (cx - nav_spacing//2, nav_y), self.font_btn, (180, 50, 50), (220, 80, 80), fixed_size=nav_size)
        self.btn_menu = AnimButton("MENU PRINCIPAL", (cx + nav_spacing//2, nav_y), self.font_btn, (80, 80, 80), (120, 120, 120), fixed_size=nav_size)

    def resize(self, screen):
        self.screen = screen
        self._load_resources()
        self._create_buttons()

    def draw(self, dt, mouse_pos):
        self.screen.blit(self.bg, (0, 0))
        for p in self.particles:
            p.update(dt, self.w, self.h)
            p.draw(self.screen)
            
        title_surf = self.font_title.render("MODO LIVRE", True, (255, 215, 0))
        title_shad = self.font_title.render("MODO LIVRE", True, (0, 0, 0))
        tr = title_surf.get_rect(center=(self.w // 2, int(self.h * 0.08)))
        self.screen.blit(title_shad, (tr.x + 4, tr.y + 4))
        self.screen.blit(title_surf, tr)
        
        for btn in self.game_buttons:
            btn.draw(self.screen, mouse_pos)
        self.btn_back_mode.draw(self.screen, mouse_pos)
        self.btn_menu.draw(self.screen, mouse_pos)


# ---------- Função Pública: run_minigame_selector (ASYNC) ----------
async def run_minigame_selector(screen):
    ui = FreeModeUI(screen)
    clock = pygame.time.Clock()
    audio_manager.fade_to_music("menu")

    running = True
    while running:
        dt = clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        ui.draw(dt, mouse_pos)
        pygame.display.flip()
        
        # OBRIGATÓRIO NA WEB
        await asyncio.sleep(0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                    screen = pygame.display.get_surface()
                    ui.resize(screen)
                elif event.key == pygame.K_ESCAPE:
                    return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 1. Botões de Jogo
                for btn in ui.game_buttons:
                    if btn.clicked(event):
                        audio_manager.fade_to_music(btn.music_key, fade_ms=500)
                        
                        try:
                            # ATENÇÃO: CHAMADA ASYNC DO MINIGAME
                            await btn.action(screen)
                        except Exception as e:
                            print(f"Erro no minigame: {e}")
                        
                        screen = pygame.display.get_surface()
                        ui.resize(screen)
                        audio_manager.fade_to_music("menu", fade_ms=800)
                        
                # 2. Navegação
                if ui.btn_back_mode.clicked(event):
                    return
                
                if ui.btn_menu.clicked(event):
                    return "menu_principal" 
    return


# ---------- UI da Seleção de Modo (ASYNC) ----------
async def escolher_modo(screen):
    clock = pygame.time.Clock()
    w, h = screen.get_size()
    
    font_title = load_font(int(h * 0.08))
    font_btn = load_font(int(h * 0.05))
    
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        bg_path = os.path.join(base, "assets", "background", "game_modo.png")
        raw = pygame.image.load(bg_path).convert()
        bg = pygame.transform.smoothscale(raw, (w, h))
        bg = _blur_surface(bg, 10)
    except:
        bg = pygame.Surface((w, h))
        bg.fill((20, 20, 40))

    cx = w // 2
    cy = h // 2
    main_btn_size = (int(w * 0.4), int(h * 0.12))

    btn_campanha = AnimButton("Modo Campanha", (cx, cy - 60), font_btn, (200, 60, 60), (240, 100, 100), fixed_size=main_btn_size)
    btn_livre = AnimButton("Modo Livre", (cx, cy + 60), font_btn, (60, 100, 200), (100, 140, 240), fixed_size=main_btn_size)
    btn_voltar = AnimButton("RETORNAR AO MENU", (cx, h - 80), font_btn, (80, 80, 80), (120, 120, 120), fixed_size=(int(w * 0.3), int(h * 0.08)))

    running = True
    while running:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        
        screen.blit(bg, (0, 0))
        
        ts = font_title.render("ESCOLHA O MODO DE JOGO", True, (255, 255, 255))
        tr = ts.get_rect(center=(cx, int(h * 0.15)))
        screen.blit(ts, tr)
        
        btn_campanha.draw(screen, mouse_pos)
        btn_livre.draw(screen, mouse_pos)
        btn_voltar.draw(screen, mouse_pos)
        
        pygame.display.flip()
        
        # OBRIGATÓRIO NA WEB
        await asyncio.sleep(0)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
                screen = pygame.display.get_surface()
                w, h = screen.get_size()
                bg = pygame.transform.smoothscale(raw, (w, h))
                bg = _blur_surface(bg, 10)
                cx, cy = w // 2, h // 2
                main_btn_size = (int(w * 0.4), int(h * 0.12))
                btn_campanha.update_pos((cx, cy - 60), fixed_size=main_btn_size)
                btn_livre.update_pos((cx, cy + 60), fixed_size=main_btn_size)
                btn_voltar.update_pos((cx, h - 80), fixed_size=(int(w * 0.3), int(h * 0.08)))

            if btn_campanha.clicked(event):
                return "campanha"
            
            if btn_livre.clicked(event):
                # CHAMADA ASYNC
                result = await run_minigame_selector(screen)
                if result == "menu_principal":
                    return None
                screen = pygame.display.get_surface()
            
            if btn_voltar.clicked(event):
                return None

    return None