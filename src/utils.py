#============================================================
#            SISTEMA DE UTILIZAÇÃO DO JOGO (WEB READY)
#============================================================
import asyncio # <--- 1. Import Asyncio
import pygame
import sys
import os
import random
from math import sin

# ... (MANTENHA AS FUNÇÕES DE FONTE, DRAW_TEXT e CONTAINERS IGUAIS) ...
# ... (NÃO ALTERE load_font, draw_text, draw_question_container, draw_modern_container, draw_score_display) ...
# ... (Cole aqui o código original dessas funções que não têm loop) ...

# VOU REESCREVER APENAS AS FUNÇÕES QUE MUDAM PARA ASYNC ABAIXO:

# ============================================================
# GERENCIAMENTO DE FONTES E TEXTO (MANTIDO IGUAL)
# ============================================================
_font_cache = {}
def load_font(size):
    size = int(size)
    if size in _font_cache: return _font_cache[size]
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_path = os.path.join(base_dir, "assets", "fonts", "NotoSans-Regular.ttf")
    try: font = pygame.font.Font(font_path, size)
    except: font = pygame.font.Font(None, size)
    _font_cache[size] = font
    return font

def draw_text(screen, text, font, color, center_pos, shadow=False):
    if shadow:
        sh = font.render(text, True, (0, 0, 0))
        rect = sh.get_rect(center=(center_pos[0] + 2, center_pos[1] + 2))
        screen.blit(sh, rect)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center_pos)
    screen.blit(surf, rect)
    return rect

def draw_text_animated(screen, text, font, color, rect, align="center"):
    return draw_text_wrapped(screen, text, font, color, rect, align=align)

def draw_text_wrapped(screen, text, font, color, rect, shadow_color=None, align="center"):
    words = text.split()
    lines, current_line = [], ""
    for word in words:
        test_line = f"{current_line}{word} "
        if font.size(test_line)[0] <= rect.width: current_line = test_line
        else: lines.append(current_line.strip()); current_line = word + " "
    if current_line: lines.append(current_line.strip())
    line_height = font.get_linesize()
    total_height = len(lines) * line_height
    y_start = rect.centery - (total_height / 2)
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        text_rect = text_surface.get_rect()
        if align == "left": text_rect.left = rect.left
        elif align == "right": text_rect.right = rect.right
        else: text_rect.centerx = rect.centerx
        text_rect.y = y_start + i * line_height
        if shadow_color:
            shadow_surface = font.render(line, True, shadow_color)
            screen.blit(shadow_surface, (text_rect.x + 2, text_rect.y + 2))
        screen.blit(text_surface, text_rect)

def draw_question_container(screen, rect, title_text=None, font_title=None, bg_color=(15, 15, 35, 180), border_color=(255, 255, 255), border_radius=16, padding=20):
    shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 80), shadow_surface.get_rect(), border_radius=border_radius)
    screen.blit(shadow_surface, (rect.x + 3, rect.y + 3))
    container_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(container_surface, bg_color, container_surface.get_rect(), border_radius=border_radius)
    pygame.draw.rect(container_surface, border_color, container_surface.get_rect(), 2, border_radius=border_radius)
    screen.blit(container_surface, rect.topleft)
    if title_text and font_title:
        title_surface = font_title.render(title_text, True, (255, 215, 0))
        title_shadow = font_title.render(title_text, True, (0, 0, 0))
        title_rect = title_surface.get_rect(midtop=(rect.centerx, rect.top - font_title.get_height() - 10))
        screen.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
        screen.blit(title_surface, title_rect)
    return rect.inflate(-padding * 2, -padding * 3)

def draw_modern_container(screen, rect, color=(22,22,35,210), border=2):
    shadow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0,0,0,90), shadow.get_rect(), border_radius=18)
    screen.blit(shadow, (rect.x + 4, rect.y + 4))
    surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, surf.get_rect(), border_radius=18)
    pygame.draw.rect(surf, (255,255,255,200), surf.get_rect(), border, border_radius=18)
    screen.blit(surf, rect)

def draw_score_display(screen, score, font, position="topright"):
    text = f"Pontos: {score}"
    text_surface = font.render(text, True, (255, 255, 255))
    shadow_surface = font.render(text, True, (0, 0, 0, 180))
    rect = text_surface.get_rect()
    margin = 20
    positions = {
        "topright": rect.move(screen.get_width() - rect.width - margin, margin),
        "topleft": rect.move(margin, margin),
        "bottomright": rect.move(screen.get_width() - rect.width - margin, screen.get_height() - rect.height - margin),
        "bottomleft": rect.move(margin, screen.get_height() - rect.height - margin),
    }
    text_rect = positions.get(position, rect.move((screen.get_width() - rect.width) // 2, margin))
    screen.blit(shadow_surface, (text_rect.x + 2, text_rect.y + 2))
    screen.blit(text_surface, text_rect)

def draw_score(screen, score, font):
    draw_score_display(screen, score, font)

# ============================================================
# EFEITOS DE TRANSIÇÃO (AGORA ASYNC)
# ============================================================

async def fade_in(screen, duration=350):
    overlay = pygame.Surface(screen.get_size())
    overlay.fill((0,0,0))
    steps = 18
    delta = 255 // steps
    clock = pygame.time.Clock()

    for a in range(255, -1, -delta):
        overlay.set_alpha(a)
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        # await essencial no loop
        await asyncio.sleep(0) 
        clock.tick(60)

async def fade_out(screen, duration=350):
    overlay = pygame.Surface(screen.get_size())
    overlay.fill((0,0,0))
    steps = 18
    delta = 255 // steps
    clock = pygame.time.Clock()

    for a in range(0, 255, delta):
        overlay.set_alpha(a)
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        # await essencial no loop
        await asyncio.sleep(0)
        clock.tick(60)


# ============================================================
# TELA DE PAUSA / FINAL (AGORA ASYNC)
# ============================================================

async def show_pause_screen(screen, clock, title, score_text, subtitle="Toque para continuar", theme="default", background=None):
    w, h = screen.get_size()
    font_title = load_font(int(h * 0.12))
    font_score = load_font(int(h * 0.07))
    font_sub = load_font(int(h * 0.035))
    font_particle = load_font(int(h * 0.025))

    themes = {
        "default": {"color": (255,255,255), "accent": (255,190,70), "type": "circle"},
        "Show do Bilhão": {"color": (255,215,0), "accent": (255,215,0), "type": "char", "content": ["$"]},
        "Batalha Naval": {"color": (150,220,255), "accent": (80,200,255), "type": "circle"},
        "Maleta Certa": {"color": (255,100,100), "accent": (255,200,100), "type": "char", "content": ["M"]},
        "Roleta de Risco": {"color": (255,100,255), "accent": (255,120,255), "type": "char", "content": ["!", "?"]},
        "Perseguição": {"color": (255,200,50), "accent": (255,50,50), "type": "char", "content": ["!"]},
        "STOP": {"color": (255,255,255), "accent": (100,255,100), "type": "char", "content": ["A","B","C"]},
    }
    style = themes.get(theme, themes["default"])

    particles = []
    for _ in range(30):
        p = {"x": random.randint(0, w), "y": random.randint(0, h), "r": random.randint(2, 6), "alpha": random.randint(100, 255), "speed": random.uniform(0.5, 2)}
        if style.get("type") == "char": p["char"] = random.choice(style.get("content", ["*"]))
        particles.append(p)

    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 40, 200))
    
    running = True
    t = 0
    blink_timer = 0

    while running:
        t += 1
        
        if background:
            screen.blit(background, (0, 0))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill((15, 15, 30))

        for p in particles:
            p["y"] -= p["speed"]
            p["alpha"] -= 2
            if p["y"] < -10 or p["alpha"] <= 0:
                p["x"] = random.randint(0, w); p["y"] = random.randint(h, h + 50); p["alpha"] = random.randint(150, 255)

            base = style["color"]
            col = (base[0], base[1], base[2], int(p["alpha"]))
            
            if style.get("type") == "char":
                ps = font_particle.render(p["char"], True, col)
                ps.set_alpha(int(p["alpha"]))
                screen.blit(ps, (int(p["x"]), int(p["y"])))
            else:
                surf = pygame.Surface((p["r"]*2, p["r"]*2), pygame.SRCALPHA)
                pygame.draw.circle(surf, col, (p["r"], p["r"]), p["r"])
                screen.blit(surf, (int(p["x"]), int(p["y"])))

        draw_text(screen, title, font_title, style["accent"], (w//2, h*0.35), shadow=True)
        draw_text(screen, score_text, font_score, (255,255,255), (w//2, h*0.50))
        
        blink_timer += 1
        if int(sin(blink_timer * 0.1) * 255) > 0:
            draw_text(screen, subtitle, font_sub, (200,200,200), (w//2, h*0.70))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11: pygame.display.toggle_fullscreen()
                elif event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE]: running = False
            if event.type == pygame.MOUSEBUTTONDOWN: running = False

        pygame.display.flip()
        # OBRIGATÓRIO NA WEB
        await asyncio.sleep(0) 
        clock.tick(60)