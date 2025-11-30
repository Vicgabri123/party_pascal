# ===========================================================
#       MENU DE CONFIGURAÇÕES (WEB READY)
# ===========================================================

import pygame
import os
import math
import random
import sys
import json
import asyncio  # <--- Importante
from src.utils import load_font, draw_text
from src.audio_manager import audio_manager

# ---------- Config paths ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
BG_PATH_DEFAULT = os.path.join(ASSETS_DIR, "background", "background_main.png")

# ---------- Paleta de Cores ----------
COLORS = {
    "text": (255, 255, 255),
    "shadow": (0, 0, 0),
    "panel_bg": (20, 25, 40, 230),
    "slider_bg": (60, 60, 80),
    "slider_fill": (100, 200, 255),
    # Dificuldades
    "btn_easy": (50, 120, 220),    # Azul
    "btn_normal": (220, 180, 40),  # Amarelo/Dourado
    "btn_hard": (200, 50, 50),     # Vermelho
    "btn_gray": (80, 80, 90),      # Cinza (Voltar/Salvar)
    "btn_hover_add": (40, 40, 40)  # Brilho ao passar o mouse
}

# ---------- Utility: load & save settings ----------
def load_settings():
    defaults = {
        "music_volume": 0.5,
        "fx_volume": 1.0,
        "fullscreen": False,
        "difficulty": "normal"
    }
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k, v in defaults.items():
                if k not in data:
                    data[k] = v
            return data
    except Exception:
        pass
    return defaults

def save_settings(s):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2)
        # Nota para Web: O salvamento ocorre num sistema de arquivos virtual (MEMFS).
        # Ele persiste enquanto a aba estiver aberta, mas pode sumir ao recarregar 
        # dependendo da configuração do Pygbag.
    except Exception as e:
        print("⚠ Erro ao salvar settings:", e)


# ---------- Partículas (Bolinhas coloridas de fundo) ----------
class Particle:
    def __init__(self, w, h):
        self.w, self.h = max(1, w), max(1, h)
        self.reset()

    def reset(self):
        self.x = random.uniform(0, self.w)
        self.y = random.uniform(0, self.h)
        self.r = random.uniform(2, 5)
        self.speed = random.uniform(0.2, 0.6)
        self.alpha = random.randint(50, 150)
        self.color = random.choice([(255, 255, 255), (100, 200, 255), (255, 100, 150)])

    def update(self, dt):
        self.y -= self.speed * dt * 0.06
        self.x += math.sin(self.y * 0.01) * 0.2
        if self.y < -10:
            self.reset()
            self.y = self.h + 10

    def draw(self, surf):
        s = pygame.Surface((int(self.r*2), int(self.r*2)), pygame.SRCALPHA)
        c = (*self.color, int(self.alpha))
        pygame.draw.circle(s, c, (int(self.r), int(self.r)), int(self.r))
        surf.blit(s, (int(self.x), int(self.y)))


# ---------- Slider (Controle de Volume) ----------
class Slider:
    def __init__(self, x, y, width, value=1.0):
        self.rect = pygame.Rect(x, y, width, 12)
        self.value = max(0.0, min(1.0, float(value)))
        self.dragging = False
        self.knob_radius = 12

    def draw(self, screen):
        # Barra fundo
        pygame.draw.rect(screen, COLORS["slider_bg"], self.rect, border_radius=6)
        
        # Barra preenchida
        fill_w = int(self.value * self.rect.width)
        if fill_w > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.height)
            pygame.draw.rect(screen, COLORS["slider_fill"], fill_rect, border_radius=6)
        
        # Knob (Bolinha)
        knob_x = self.rect.x + fill_w
        knob_y = self.rect.centery
        pygame.draw.circle(screen, (255, 255, 255), (knob_x, knob_y), self.knob_radius)
        pygame.draw.circle(screen, (200, 200, 200), (knob_x, knob_y), self.knob_radius - 3)

    def handle_event(self, event):
        """Retorna True se o valor mudou."""
        changed = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Check colisão expandida para facilitar o clique
            if self.rect.inflate(20, 20).collidepoint(mx, my):
                self.dragging = True
                self.update_value(mx)
                changed = True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return "released" 

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mx, my = event.pos
            self.update_value(mx)
            changed = True
            
        return changed

    def update_value(self, mouse_x):
        relative = mouse_x - self.rect.x
        self.value = max(0.0, min(1.0, relative / self.rect.width))


# ---------- Button (Colorido e Neon) ----------
class Button:
    def __init__(self, text, center, font, base_color):
        self.text = text
        self.font = font
        self.base_color = base_color
        self.center = center
        self.hovering = False
        self.scale = 1.0
        self._render()

    def _render(self):
        self.text_surf = self.font.render(self.text, True, COLORS["text"])
        self.shadow_surf = self.font.render(self.text, True, (0,0,0))
        
        w, h = self.text_surf.get_size()
        self.rect = pygame.Rect(0, 0, w + 40, h + 20)
        self.rect.center = self.center

    def update_pos(self, center):
        self.center = center
        self.rect.center = center

    def draw(self, screen, is_selected=False):
        mouse = pygame.mouse.get_pos()
        self.hovering = self.rect.collidepoint(mouse)
        
        target_scale = 1.05 if self.hovering else 1.0
        self.scale += (target_scale - self.scale) * 0.2

        r, g, b = self.base_color
        if self.hovering:
            r = min(255, r + 30)
            g = min(255, g + 30)
            b = min(255, b + 30)
        
        color = (r, g, b)
        
        w = int(self.rect.width * self.scale)
        h = int(self.rect.height * self.scale)
        draw_rect = pygame.Rect(0, 0, w, h)
        draw_rect.center = self.center

        # Sombra do botão
        shadow_rect = draw_rect.copy()
        shadow_rect.move_ip(4, 4)
        pygame.draw.rect(screen, (0, 0, 0, 150), shadow_rect, border_radius=15)

        # Botão
        pygame.draw.rect(screen, color, draw_rect, border_radius=15)
        
        # Borda
        border_col = (255, 255, 255) if is_selected else (30, 30, 30)
        border_width = 3 if is_selected else 1
        pygame.draw.rect(screen, border_col, draw_rect, border_width, border_radius=15)

        # Texto e Sombra
        screen.blit(self.shadow_surf, self.shadow_surf.get_rect(center=(draw_rect.centerx+1, draw_rect.centery+1)))
        screen.blit(self.text_surf, self.text_surf.get_rect(center=draw_rect.center))

    def clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                audio_manager.play_sfx_if_exists("click")
                return True
        return False


# ---------- UI Layout Controller ----------
class SettingsUI:
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        self.w, self.h = screen.get_size()
        
        self.particles = [Particle(self.w, self.h) for _ in range(25)]
        
        # Background
        try:
            raw_bg = pygame.image.load(BG_PATH_DEFAULT).convert()
            self.bg = pygame.transform.smoothscale(raw_bg, (self.w, self.h))
        except:
            self.bg = pygame.Surface((self.w, self.h))
            self.bg.fill((30, 30, 45))

        self._init_elements()

    def _init_elements(self):
        h = self.h
        cx = self.w // 2
        
        # Fontes via utils
        self.font_title = load_font(int(h * 0.08))
        self.font_label = load_font(int(h * 0.04))
        self.font_btn = load_font(int(h * 0.035))

        # Sliders
        slider_w = int(self.w * 0.5)
        self.slider_music = Slider(cx - slider_w//2, int(h * 0.35), slider_w, self.settings.get("music_volume", 0.5))
        self.slider_fx = Slider(cx - slider_w//2, int(h * 0.52), slider_w, self.settings.get("fx_volume", 1.0))

        # Botões de Dificuldade
        btn_y = int(h * 0.68)
        spacing = int(self.w * 0.22)
        
        self.btn_easy = Button("Fácil", (cx - spacing, btn_y), self.font_btn, COLORS["btn_easy"])
        self.btn_normal = Button("Normal", (cx, btn_y), self.font_btn, COLORS["btn_normal"])
        self.btn_hard = Button("Difícil", (cx + spacing, btn_y), self.font_btn, COLORS["btn_hard"])

        # Botão Fullscreen
        is_full = self.settings.get("fullscreen")
        txt = "Tela Cheia: DESATIVAR" if is_full else "Tela Cheia: ATIVAR"
        
        self.btn_full = Button(txt, (cx, int(h * 0.80)), self.font_btn, COLORS["btn_gray"])

        # Ações
        self.btn_save = Button("Salvar & Voltar", (cx, int(h * 0.92)), self.font_btn, (40, 150, 60))

    def resize(self, screen):
        self.screen = screen
        self.w, self.h = screen.get_size()
        try:
            raw_bg = pygame.image.load(BG_PATH_DEFAULT).convert()
            self.bg = pygame.transform.smoothscale(raw_bg, (self.w, self.h))
        except: pass
        self._init_elements()

    def draw(self):
        # BG e Overlay
        self.screen.blit(self.bg, (0, 0))
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill(COLORS["panel_bg"])
        self.screen.blit(overlay, (0, 0))

        # Partículas
        for p in self.particles:
            p.update(16)
            p.draw(self.screen)

        # Título
        title = self.font_title.render("CONFIGURAÇÕES", True, (255, 255, 255))
        shad = self.font_title.render("CONFIGURAÇÕES", True, (0,0,0))
        tr = title.get_rect(center=(self.w//2, int(self.h * 0.10)))
        self.screen.blit(shad, (tr.x+4, tr.y+4))
        self.screen.blit(title, tr)

        # Labels
        l1 = self.font_label.render("Música", True, (200, 200, 200))
        self.screen.blit(l1, (self.slider_music.rect.x, self.slider_music.rect.y - 45))
        self.slider_music.draw(self.screen)

        l2 = self.font_label.render("Efeitos Sonoros", True, (200, 200, 200))
        self.screen.blit(l2, (self.slider_fx.rect.x, self.slider_fx.rect.y - 45))
        self.slider_fx.draw(self.screen)

        # Dificuldade Label
        ld = self.font_label.render("Dificuldade", True, (255, 255, 255))
        self.screen.blit(ld, ld.get_rect(center=(self.w//2, int(self.h * 0.60))))

        # Botões
        curr_diff = self.settings.get("difficulty", "normal")
        self.btn_easy.draw(self.screen, is_selected=(curr_diff == "facil"))
        self.btn_normal.draw(self.screen, is_selected=(curr_diff == "normal"))
        self.btn_hard.draw(self.screen, is_selected=(curr_diff == "dificil"))

        self.btn_full.draw(self.screen)
        self.btn_save.draw(self.screen)


# ---------- Loop Principal (ASYNC) ----------
async def run_settings_menu(screen):
    clock = pygame.time.Clock()
    
    # Carrega config atual
    current_settings = load_settings()
    
    ui = SettingsUI(screen, current_settings)

    running = True
    while running:
        dt = clock.tick(60)

        ui.draw()
        pygame.display.flip()
        
        # ⚠️ CORREÇÃO CRÍTICA PARA WEB ⚠️
        await asyncio.sleep(0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(current_settings)
                pygame.quit(); sys.exit()
            
            # Sliders
            res_mus = ui.slider_music.handle_event(event)
            if res_mus:
                vol = ui.slider_music.value
                current_settings["music_volume"] = vol
                audio_manager.set_music_volume(vol)

            res_fx = ui.slider_fx.handle_event(event)
            if res_fx:
                vol = ui.slider_fx.value
                current_settings["fx_volume"] = vol
                audio_manager.set_sfx_volume(vol)
                if res_fx == "released":
                    audio_manager.play_sfx_if_exists("click")

            # Botões Dificuldade
            if ui.btn_easy.clicked(event):
                current_settings["difficulty"] = "facil"
            if ui.btn_normal.clicked(event):
                current_settings["difficulty"] = "normal"
            if ui.btn_hard.clicked(event):
                current_settings["difficulty"] = "dificil"

            # Botão Fullscreen
            if ui.btn_full.clicked(event):
                is_full = screen.get_flags() & pygame.FULLSCREEN
                if is_full:
                    # Estava em tela cheia -> Vai para janela
                    screen = pygame.display.set_mode((1024, 600), pygame.RESIZABLE)
                    current_settings["fullscreen"] = False
                else:
                    # Estava em janela -> Vai para tela cheia
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    current_settings["fullscreen"] = True
                
                ui.resize(screen)
                
                # Atualiza texto do botão
                txt = "Tela Cheia: DESATIVAR" if current_settings["fullscreen"] else "Tela Cheia: ATIVAR"
                ui.btn_full = Button(txt, ui.btn_full.center, ui.font_btn, COLORS["btn_gray"])

            # Botão Salvar/Sair
            if ui.btn_save.clicked(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                save_settings(current_settings)
                return

            # F11 Global
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                is_full = screen.get_flags() & pygame.FULLSCREEN
                if is_full:
                    screen = pygame.display.set_mode((1024, 600), pygame.RESIZABLE)
                    current_settings["fullscreen"] = False
                else:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    current_settings["fullscreen"] = True
                ui.resize(screen)