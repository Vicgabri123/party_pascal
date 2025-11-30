# ===========================================================
#                MINIGAME BATALHA NAVAL (WEB READY)
# ===========================================================
#
# ✔ Versão: WEB READY (Async/Await)
# ✔ Visual: Mantido (Partículas de água, Splashes, Efeitos)
# ✔ Correção: Loop principal com await asyncio.sleep(0)
# ===========================================================

import asyncio  # <--- 1. IMPORT OBRIGATÓRIO
import pygame
import random
import sys
import os
import math
from src.utils import show_pause_screen, draw_score_display
from src.score_manager import ScoreManager
from src.audio_manager import AudioManager
import src.difficulty_manager as dm

# === SISTEMA DE PARTÍCULAS DE ÁGUA ===
class WaterParticle:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.x = random.uniform(0, screen_w)
        self.y = random.uniform(0, screen_h)
        self.radius = random.randint(2, 5)
        self.speed = random.uniform(0.15, 0.7)
        self.alpha = random.randint(30, 110)
        self.dir_x = random.uniform(-0.25, 0.25)
        self.dir_y = random.uniform(-0.05, 0.2)
        self.osc = random.uniform(0, 6.28)

    def update(self):
        self.x += self.dir_x + math.sin(self.osc) * 0.12
        self.y += self.dir_y
        self.osc += 0.04
        if self.x < -10: self.x = self.screen_w + 10
        if self.x > self.screen_w + 10: self.x = -10
        if self.y < -10: self.y = self.screen_h + 10
        if self.y > self.screen_h + 10: self.y = -10

    def draw(self, surface):
        water_color = (160, 200, 255, self.alpha)
        s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, water_color, (self.radius, self.radius), self.radius)
        surface.blit(s, (int(self.x - self.radius), int(self.y - self.radius)))

GRID_SIZE = 5
MARGIN = 10

# === BANCO DE AMEAÇAS EXPANDIDO ===
BANCO_AMEACAS = [
    ("Malware", "Antivírus Corporativo"),
    ("Phishing", "Autenticação Multifator (MFA)"),
    ("Ransomware", "Backup Offline"),
    ("DDoS", "Firewall de Borda"),
    ("Engenharia Social", "Treinamento de Conscientização"),
    ("Vazamento de Dados", "DLP (Data Loss Prevention)"),
    ("Acesso Não Autorizado", "Gestão de Identidade (IAM)"),
    ("Shadow IT", "Inventário de Ativos"),
    ("Falha de Hardware", "Redundância / HA"),
    ("Insider Threat", "Monitoramento de Logs"),
    ("SQL Injection", "WAF (Web App Firewall)"),
    ("Senha Fraca", "Política de Senhas Fortes"),
    ("Zero-Day Exploit", "Gestão de Patches"),
    ("Man-in-the-Middle", "VPN e Criptografia"),
    ("Dispositivo Perdido", "Criptografia de Disco"),
    ("Wi-Fi Inseguro", "WPA3 Enterprise"),
    ("Spyware", "EDR (Endpoint Detection)"),
    ("Botnet", "IPS (Intrusion Prevention)"),
    ("API Vulnerável", "API Gateway Seguro"),
    ("Bypass de Auth", "Testes de Intrusão (Pentest)")
]

# ===========================================================
#               FUNÇÃO PRINCIPAL (ASYNC)
# ===========================================================
async def run_batalha_naval(screen):  # <--- 2. ASYNC DEF
    pygame.display.set_caption("⚓ Batalha Naval - Controles e Ameaças ⚓")
    clock = pygame.time.Clock()

    # === PATHS ===
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    assets_dir = os.path.join(base_dir, "assets")
    bg_path = os.path.join(assets_dir, "background", "background_batalha_naval.png")
    icon_path = os.path.join(assets_dir, "icons", "naval.png")
    
    bg_original = None
    if os.path.exists(bg_path):
        bg_original = pygame.image.load(bg_path).convert()
    
    icon_original = None
    if os.path.exists(icon_path):
        icon_original = pygame.image.load(icon_path).convert_alpha()

    # Variáveis de layout
    layout = {}

    # === FUNÇÃO DE RESIZE ===
    def resize_assets(surface):
        w, h = surface.get_size()
        
        if bg_original:
            layout['bg'] = pygame.transform.scale(bg_original, (w, h))
        else:
            layout['bg'] = pygame.Surface((w, h))
            layout['bg'].fill((5, 20, 40))
            
        if icon_original:
            size = int(h * 0.08)
            layout['icon'] = pygame.transform.smoothscale(icon_original, (size, size))
        else:
            layout['icon'] = None
            
        layout['CELL_SIZE'] = min(w, h) // (GRID_SIZE + 3)
        total_width = GRID_SIZE * layout['CELL_SIZE'] + (GRID_SIZE - 1) * MARGIN
        total_height = GRID_SIZE * layout['CELL_SIZE'] + (GRID_SIZE - 1) * MARGIN
        layout['offset_x'] = (w - total_width) // 2
        layout['offset_y'] = (h - total_height) // 2 + 40
        layout['total_height'] = total_height
        
        layout['font_title'] = pygame.font.Font(None, max(48, int(h * 0.09)))
        layout['font_text'] = pygame.font.Font(None, max(28, int(h * 0.05)))
        layout['font_small'] = pygame.font.Font(None, max(20, int(h * 0.04)))

    resize_assets(screen)
    
    water_particles = [WaterParticle(screen.get_width(), screen.get_height()) for _ in range(40)]
    splashes = [] 

    # === CONFIGURAÇÃO DE DIFICULDADE ===
    qtd_navios_solicitada = dm.get_batalha_naval_threats()
    max_possible = min(GRID_SIZE * GRID_SIZE, len(BANCO_AMEACAS))
    qtd_navios = min(qtd_navios_solicitada, max_possible)
    
    # Randomização
    ameacas_rodada = random.sample(BANCO_AMEACAS, qtd_navios)
    grid = [[" " for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    navios_indices = random.sample(range(GRID_SIZE * GRID_SIZE), qtd_navios)
    navios_pos = {pos: ameacas_rodada[i] for i, pos in enumerate(navios_indices)}

    reveladas = set()
    efeitos = []
    jogo_ativo = True
    frame = 0
    HOVER_COLOR = (80, 120, 200)

    def adicionar_efeito(tipo, pos):
        efeitos.append({"tipo": tipo, "pos": pos, "tempo": 0, "max_tempo": 22})

    def criar_splash(cx, cy):
        spl = {"x": cx, "y": cy, "r": 6, "alpha": 200, "life": 0, "max_life": 16, "spread": random.uniform(0.8, 1.6)}
        splashes.append(spl)
        for _ in range(6):
            wp = {"x": cx + random.uniform(-6, 6), "y": cy + random.uniform(-6, 6), "r": random.randint(1, 3),
                  "alpha": random.randint(160, 240), "dx": random.uniform(-1.6, 1.6), "dy": random.uniform(-0.8, -0.1),
                  "life": 0, "max_life": random.randint(18, 26), "dx": 0}
            splashes.append(wp)

    # ========================= LOOP PRINCIPAL ================================
    while jogo_ativo:
        frame += 1
        mouse_pos = pygame.mouse.get_pos()
        
        CELL_SIZE = layout['CELL_SIZE']
        offset_x = layout['offset_x']
        offset_y = layout['offset_y']

        for p in water_particles: p.update()

        new_splashes = []
        for s in splashes:
            if "dx" in s and s["dx"] != 0:
                s["x"] += s["dx"]; s["y"] += s["dy"]; s["dy"] += 0.06
                s["life"] += 1; s["alpha"] = max(0, s["alpha"] - (255 / s["max_life"]))
                if s["life"] < s["max_life"]: new_splashes.append(s)
            else:
                s["life"] += 1; s["r"] += 0.9 * s.get("spread", 1)
                s["alpha"] = max(0, s["alpha"] - (200 / s["max_life"]))
                if s["life"] < s["max_life"]: new_splashes.append(s)
        splashes = new_splashes

        screen.blit(layout['bg'], (0, 0))
        for p in water_particles: p.draw(screen)

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 50, 120))
        screen.blit(overlay, (0, 0))

        # Título Animado
        title_animation_time = frame
        float_offset = int(math.sin(title_animation_time * 0.05) * 4)
        slide_offset = max(0, 30 - title_animation_time * 0.7)
        alpha = min(255, max(0, title_animation_time * 10))

        title_surf = layout['font_title'].render("Batalha Naval", True, (255, 255, 255))
        title_shadow = layout['font_title'].render("Batalha Naval", True, (0, 0, 0))
        title_surf.set_alpha(alpha); title_shadow.set_alpha(alpha)
        
        title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 60 - slide_offset + float_offset))
        screen.blit(title_shadow, (title_rect.x+3, title_rect.y+3))
        screen.blit(title_surf, title_rect)

        if layout['icon']:
            screen.blit(layout['icon'], (title_rect.left - layout['icon'].get_width() - 15, title_rect.top))
            screen.blit(layout['icon'], (title_rect.right + 15, title_rect.top))

        # Tabuleiro
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = offset_x + col * (CELL_SIZE + MARGIN)
                y = offset_y + row * (CELL_SIZE + MARGIN)
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

                is_interactive = (row, col) not in reveladas and grid[row][col] != "X"
                is_hovered = rect.collidepoint(mouse_pos)
                
                color = (40, 80, 160)
                if (row, col) in reveladas: color = (200, 60, 60)
                elif grid[row][col] == "X": color = (80, 80, 100)
                elif is_hovered and is_interactive: color = HOVER_COLOR

                pygame.draw.rect(screen, (0, 0, 0, 100), (x+3, y+3, CELL_SIZE, CELL_SIZE), border_radius=6)
                pygame.draw.rect(screen, color, rect, border_radius=6)
                pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=6)

        # Efeitos
        for efeito in efeitos[:]:
            efeito["tempo"] += 1
            alpha_fx = int(255 * (1 - efeito["tempo"] / efeito["max_tempo"]))
            (erow, ecol) = efeito["pos"]
            x = offset_x + ecol * (CELL_SIZE + MARGIN)
            y = offset_y + erow * (CELL_SIZE + MARGIN)
            cor = (255, 200, 60, alpha_fx) if efeito["tipo"] == "acerto" else (60, 120, 255, alpha_fx)
            flash = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            flash.fill(cor)
            screen.blit(flash, (x, y))
            if efeito["tempo"] >= efeito["max_tempo"]: efeitos.remove(efeito)

        # Splashes
        for s in splashes:
            if "dx" in s and s["dx"] != 0:
                surf = pygame.Surface((s["r"]*2, s["r"]*2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (200, 230, 255, max(0, int(s.get("alpha", 180)))), (s["r"], s["r"]), s["r"])
                screen.blit(surf, (int(s["x"]-s["r"]), int(s["y"]-s["r"])))
            else:
                surf = pygame.Surface((int(s["r"]*2+4), int(s["r"]*2+4)), pygame.SRCALPHA)
                pygame.draw.circle(surf, (180, 220, 255, max(0, int(s["alpha"]))), (surf.get_width()//2, surf.get_height()//2), int(s["r"]), 2)
                screen.blit(surf, (int(s["x"]-surf.get_width()//2), int(s["y"]-surf.get_height()//2)))

        draw_score_display(screen, ScoreManager.get_score(), layout['font_small'], position="topright")

        # Instruções
        info_s = layout['font_small'].render("Clique nas células para encontrar Riscos (ESC para sair)", True, (255, 255, 255))
        screen.blit(info_s, info_s.get_rect(center=(screen.get_width()//2, offset_y + layout['total_height'] + 40)))

        # === EVENTOS ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                    screen = pygame.display.get_surface()
                    resize_assets(screen)
                    for p in water_particles:
                        p.screen_w = screen.get_width(); p.screen_h = screen.get_height()
                elif event.key == pygame.K_ESCAPE:
                    return ScoreManager.get_score()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                for row in range(GRID_SIZE):
                    for col in range(GRID_SIZE):
                        x = offset_x + col * (CELL_SIZE + MARGIN)
                        y = offset_y + row * (CELL_SIZE + MARGIN)
                        if pygame.Rect(x, y, CELL_SIZE, CELL_SIZE).collidepoint(mx, my) and (row, col) not in reveladas and grid[row][col] != "X":
                            pos = row * GRID_SIZE + col
                            if pos in navios_pos:
                                reveladas.add((row, col))
                                ameaca, controle = navios_pos[pos]
                                
                                ScoreManager.add_points(10)
                                AudioManager.play_sfx_if_exists("explosion") 
                                
                                adicionar_efeito("acerto", (row, col))
                                criar_splash(x + CELL_SIZE//2, y + CELL_SIZE//2)
                                
                                # CHAMADA ASYNC PARA PAUSE SCREEN
                                await show_pause_screen(screen, clock, "Risco Detectado!", f"Ameaça: {ameaca}", f"Solução: {controle}", theme="Batalha Naval")
                            else:
                                grid[row][col] = "X"
                                ScoreManager.add_points(-5)
                                AudioManager.play_sfx_if_exists("errado") 
                                adicionar_efeito("erro", (row, col))
                                
                                # CHAMADA ASYNC PARA PAUSE SCREEN
                                await show_pause_screen(screen, clock, "ERROU!", "Nenhum risco encontrado aqui.", theme="Batalha Naval")

        if len(reveladas) == len(navios_pos):
            AudioManager.play_sfx_if_exists("correto")
            # CHAMADA ASYNC
            await show_pause_screen(screen, clock, "Ambiente Seguro!", f"Pontuação Total: {ScoreManager.get_score()}", theme="Batalha Naval")
            jogo_ativo = False

        pygame.display.flip()
        
        # 3. LINHA MÁGICA OBRIGATÓRIA
        await asyncio.sleep(0) 
        
        clock.tick(60)

    return ScoreManager.get_score()