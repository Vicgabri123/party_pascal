#========================================================================
#                          MENU PRINCIPAL (WEB READY)
#========================================================================

import asyncio  # <--- 1. Import essencial para Web
import pygame
import sys
import os
import math
import random
import json

# Nota: As funções importadas abaixo também precisarão ser convertidas para 'async'
# nos seus respectivos arquivos para o await funcionar corretamente.
from src.game_loop import start_game_loop
from src.utils import load_font
from src.cutscene_intro import run_cutscene_intro
from src.settings_menu import run_settings_menu
from src.audio_manager import audio_manager

# --------------------------------------------------
# Config / paths
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")

def load_settings():
    defaults = {"music_volume": 0.5, "fx_volume": 1.0, "fullscreen": False}
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


# --------------------------------------------------
# Menu particle (leve e cheap)
# --------------------------------------------------
class MenuParticle:
    __slots__ = ("w","x","y","r","alpha","speed","dir")
    def __init__(self, w, h):
        self.w = max(1, w)
        self.reset(h)

    def reset(self, h):
        self.x = random.uniform(0, self.w)
        self.y = random.uniform(0, h)
        self.r = random.uniform(2, 4)
        self.alpha = random.randint(40, 130)
        self.speed = random.uniform(0.3, 0.9)
        self.dir = random.choice([-1, 1])

    def update(self, dt, w, h):
        # dt is ms from clock.tick
        self.y -= self.speed * dt * 0.05
        self.x += math.sin(self.y * 0.01) * 0.4 * self.dir
        if self.y < -10:
            self.reset(h)
            self.y = h + random.uniform(20, 80)

    def draw(self, surf):
        s = pygame.Surface((int(self.r*2), int(self.r*2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (255,255,255,int(self.alpha)), (int(self.r), int(self.r)), int(self.r))
        surf.blit(s, (int(self.x), int(self.y)))


# --------------------------------------------------
# Button class
# --------------------------------------------------
class Button:
    def __init__(self, text, target_center, font, base_color, hover_color, icon_path=None):
        self.text = text
        self.target_center = target_center
        self.center = (target_center[0], target_center[1] + 280)
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.icon = None

        if icon_path and os.path.exists(icon_path):
            try:
                img = pygame.image.load(icon_path).convert_alpha()
                img = pygame.transform.smoothscale(img, (44, 44))
                white = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                for x in range(img.get_width()):
                    for y in range(img.get_height()):
                        r,g,b,a = img.get_at((x,y))
                        white.set_at((x,y), (255,255,255,a))
                self.icon = white
            except Exception:
                self.icon = None

        self.scale = 1.0
        self.target_scale = 1.0
        self._create_surfaces()

    def _create_surfaces(self):
        self.text_surf = self.font.render(self.text, True, (255,255,255))
        tw, th = self.text_surf.get_size()
        icon_space = 54 if self.icon else 0
        self.width = tw + icon_space + 80
        self.height = th + 40
        self.rect = pygame.Rect(0,0,self.width,self.height)
        self.rect.center = (int(self.center[0]), int(self.center[1]))

    def update_layout(self, target_center, font):
        self.target_center = target_center
        self.font = font
        self._create_surfaces()

    def draw(self, screen, mouse_pos, dt):
        cx, cy = self.center
        tx, ty = self.target_center
        cx += (tx - cx) * 0.18
        cy += (ty - cy) * 0.18
        self.center = (cx, cy)
        self.rect.center = (int(cx), int(cy))

        hover = self.rect.collidepoint(mouse_pos)
        self.target_scale = 1.06 if hover else 1.0
        self.scale += (self.target_scale - self.scale) * 0.18

        cur_w = int(self.width * self.scale)
        cur_h = int(self.height * self.scale)
        r = pygame.Rect(0,0,cur_w,cur_h)
        r.center = (int(cx), int(cy))

        sombra = r.copy()
        sombra.move_ip(6, 6)
        pygame.draw.rect(screen, (0,0,0), sombra, border_radius=22)

        pygame.draw.rect(screen, self.hover_color if hover else self.base_color, r, border_radius=22)
        pygame.draw.rect(screen, (255,255,255), r, 3, border_radius=22)

        if self.icon:
            icon_rect = self.icon.get_rect(center=(r.left + 38, r.centery))
            screen.blit(self.icon, icon_rect)
            text_rect = self.text_surf.get_rect(midleft=(icon_rect.right + 12, r.centery))
        else:
            text_rect = self.text_surf.get_rect(center=r.center)

        screen.blit(self.text_surf, text_rect)

    def try_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                audio_manager.play_sfx_if_exists("click")
                return True
        return False


# --------------------------------------------------
# Asset loader
# --------------------------------------------------
def load_assets(screen, background_path, logo_path):
    W, H = screen.get_size()
    font_size = max(22, int(H * 0.048))
    try:
        font = load_font(font_size)
    except:
        font = pygame.font.Font(None, font_size)

    try:
        bg = pygame.image.load(background_path).convert()
        bg = pygame.transform.smoothscale(bg, (W, H))
    except Exception:
        bg = pygame.Surface((W,H))
        bg.fill((20,20,30))

    logo = None
    try:
        logo_img = pygame.image.load(logo_path).convert_alpha()
        lw = int(W * 0.35)
        ratio = logo_img.get_height() / logo_img.get_width()
        lh = int(lw * ratio)
        logo = pygame.transform.smoothscale(logo_img, (lw, lh))
    except Exception:
        logo = pygame.Surface((int(W*0.4), int(H*0.2)))
        logo.fill((80,80,80))

    return font, bg, logo


# --------------------------------------------------
# Main menu (ASYNC VERSION)
# --------------------------------------------------
async def main_menu(screen): # <--- 2. Definição Async
    settings = load_settings()

    background_path = os.path.join(BASE_DIR, "assets", "background", "background_main.png")
    logo_path = os.path.join(BASE_DIR, "assets", "party_pascal_logo.png")
    icons_dir = os.path.join(BASE_DIR, "assets", "icons")

    audio_manager.fade_to_music("menu", fade_ms=800)

    font, background, logo = load_assets(screen, background_path, logo_path)
    W, H = screen.get_size()

    particles = [MenuParticle(W, H) for _ in range(32)]

    base_y = int(H * 0.58)
    spacing = int(H * 0.15)
    cx = W // 2

    btn_specs = [
        ("Iniciar Jogo", (cx, base_y + 0 * spacing), (200,70,70), (240,110,110)),
        ("Configurações", (cx, base_y + 1 * spacing), (70,110,200), (120,160,250)),
        ("Sair", (cx, base_y + 2 * spacing), (80,80,80), (130,130,130)),
    ]

    buttons = []
    for text, target_center, base_c, hover_c in btn_specs:
        icon = "play" if "Iniciar" in text else "settings" if "Configura" in text else "exit"
        b = Button(text, target_center, font, base_c, hover_c,
                   icon_path=os.path.join(icons_dir, f"{icon}.png"))
        buttons.append(b)

    last_size = screen.get_size()
    needs_recalc = False

    clock = pygame.time.Clock()
    fading = True
    fade_alpha = 255

    while True:
        dt = clock.tick(60)

        mouse_pos = pygame.mouse.get_pos()
        W, H = screen.get_size()

        if (W, H) != last_size or needs_recalc:
            font, background, logo = load_assets(screen, background_path, logo_path)
            cx = W // 2
            base_y = int(H * 0.58)
            spacing = int(H * 0.15)
            for i, b in enumerate(buttons):
                b.update_layout((cx, base_y + i * spacing), font)
            particles = [MenuParticle(W, H) for _ in range(32)]
            last_size = (W, H)
            needs_recalc = False

        # DRAW
        screen.blit(background, (0,0))

        for p in particles:
            p.update(dt, W, H)
            p.draw(screen)

        logo_pulse = 1.0 + 0.03 * math.sin(pygame.time.get_ticks() * 0.002)
        logo_s = pygame.transform.rotozoom(logo, 0, logo_pulse)
        logo_rect = logo_s.get_rect(center=(W//2, int(H*0.28)))
        screen.blit(logo_s, logo_rect)

        for b in buttons:
            b.draw(screen, mouse_pos, dt)

        # Fade-in initial
        if fading:
            f = pygame.Surface((W,H))
            f.fill((0,0,0))
            f.set_alpha(fade_alpha)
            screen.blit(f, (0,0))
            fade_alpha = max(0, fade_alpha - 10)
            if fade_alpha == 0:
                fading = False

        # EVENTS
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if ev.key == pygame.K_F11:
                    is_full = screen.get_flags() & pygame.FULLSCREEN
                    if is_full:
                        screen = pygame.display.set_mode((1024, 600), pygame.RESIZABLE)
                    else:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    needs_recalc = True

            for b in buttons:
                if b.try_click(ev):
                    pygame.display.flip()
                    
                    # 4. Substituição do wait(300) por sleep async
                    # Isso evita que o navegador trave durante o delay do clique
                    await asyncio.sleep(0.3) 

                    # --- INICIAR JOGO ---
                    if b.text == "Iniciar Jogo":
                        f = pygame.Surface((W,H)); f.fill((0,0,0))
                        for a in range(0, 255, 20):
                            f.set_alpha(a)
                            screen.blit(f,(0,0))
                            pygame.display.flip()
                            # 4. Substituição do wait(10) no fade
                            await asyncio.sleep(0.01)

                        audio_manager.fade_to_music("cutscene_intro", fade_ms=700)
                        
                        # 5. CHAMADAS COM AWAIT
                        # Nota: Você deve converter esses arquivos para async também!
                        await run_cutscene_intro(screen)

                        from src.game_modo import escolher_modo, run_minigame_selector
                        # Assumindo que escolher_modo também será async
                        modo = await escolher_modo(screen)

                        if modo == "campanha":
                            await start_game_loop(screen)
                        elif modo == "livre":
                            await run_minigame_selector(screen)

                        audio_manager.fade_to_music("menu", fade_ms=800)
                        needs_recalc = True

                    # --- CONFIGURAÇÕES ---
                    elif b.text == "Configurações":
                        # 5. Call async
                        await run_settings_menu(screen)
                        needs_recalc = True

                    # --- SAIR ---
                    elif b.text == "Sair":
                        pygame.quit(); sys.exit()

        pygame.display.flip()
        
        # 3. LINHA MÁGICA: Devolve controle ao navegador
        await asyncio.sleep(0)