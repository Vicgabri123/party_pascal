# ===========================================================
#        MINIGAME RODADA BONUS - ROLETA DO RISCO (ASYNC)
# ===========================================================

import pygame
import random
import math
import sys
import os
import asyncio  # <--- IMPORTANTE PARA WEB/PYBAG
from src.utils import draw_question_container, draw_text_wrapped, draw_score_display, show_pause_screen, load_font, draw_text
from src.score_manager import ScoreManager
from src.audio_manager import AudioManager
import src.difficulty_manager as dm

# ===========================================================
#        PARTÍCULAS
# ===========================================================
class SparkParticle:
    def __init__(self, cx, cy):
        self.x = cx; self.y = cy
        ang = random.uniform(0, math.pi * 2); vel = random.uniform(3.5, 8.5)
        self.vx = math.cos(ang) * vel; self.vy = math.sin(ang) * vel
        self.life = random.randint(380, 620); self.alpha = 255; self.size = random.randint(3, 6)
    def update(self, dt_ms):
        dt = dt_ms / 1000.0; self.x += self.vx * dt; self.y += self.vy * dt
        self.vx *= 0.96; self.vy *= 0.96; self.life -= dt_ms; self.alpha = max(0, int(self.life / 3))
    def draw(self, surf):
        if self.alpha > 0:
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 60, 60, self.alpha), (self.size, self.size), self.size)
            surf.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class SparkGold:
    def __init__(self, x, y):
        self.x = x + random.uniform(-6, 6); self.y = y + random.uniform(-6, 6)
        self.angle = random.uniform(0, 2 * math.pi); self.speed = random.uniform(1.5, 3.0)
        self.size = random.randint(2, 5); self.life = random.randint(18, 28); self.alpha = 255
    def update(self):
        self.x += math.cos(self.angle) * self.speed; self.y += math.sin(self.angle) * self.speed * 0.75
        self.life -= 1; self.alpha = max(0, int(255 * (self.life / 28.0)))
    def draw(self, screen):
        if self.life > 0 and self.alpha > 0:
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 215, 80, self.alpha), (self.size, self.size), self.size)
            screen.blit(s, (int(self.x - self.size), int(self.y - self.size)))

# ===========================================================
#        VISUAIS: ORBIT SPARKS & BACKLIGHT
# ===========================================================

class OrbitSpark:
    """Fagulhas que orbitam suavemente ao redor da roleta"""
    def __init__(self, centro, raio):
        self.centro = centro
        self.base_raio = raio + 15
        self.raio = self.base_raio + random.uniform(-5, 5)
        self.ang = random.uniform(0, math.pi * 2)
        self.vel = random.uniform(0.015, 0.025) * (1 if random.random() > 0.5 else -1)
        self.size = random.randint(2, 4)
        self.alpha = random.randint(160, 230)

    def update(self):
        self.ang += self.vel
        if self.ang > math.pi * 2: self.ang -= math.pi * 2
        if self.ang < 0: self.ang += math.pi * 2

    def draw(self, screen):
        x = self.centro[0] + math.cos(self.ang) * self.raio
        y = self.centro[1] + math.sin(self.ang) * self.raio
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 160, self.alpha), (self.size, self.size), self.size)
        screen.blit(s, (int(x - self.size), int(y - self.size)))

def draw_neon_backlight(screen, centro, raio, timer):
    """
    O efeito 'pisca-pisca' que fica ATRÁS da roleta.
    Alterna entre as cores Neon (Rosa/Azul) e pulsa a intensidade.
    """
    # Cores Neon Definidas
    c_rosa = (207, 46, 57)
    c_azul = (32, 18, 204)
    
    # Alterna cor baseado no tempo (Strobe lento)
    # Divide o tempo para trocar a cada X ms
    color_phase = (timer // 600) % 2
    base_color = c_rosa if color_phase == 0 else c_azul

    # Intensidade pulsante (Senoide)
    # Varia de 0.2 (escuro) a 1.0 (brilhante)
    pulse = (math.sin(timer * 0.005) + 1) / 2 
    max_alpha = 180
    alpha = int(40 + pulse * (max_alpha - 40))

    # Cria superfície para o brilho
    glow_radius = int(raio * 1.4) # Um pouco maior que a roleta
    s_size = glow_radius * 2
    s = pygame.Surface((s_size, s_size), pygame.SRCALPHA)
    
    # Desenha 2 camadas de brilho para ficar "suave" e "neon"
    # Camada 1: Halo externo difuso
    pygame.draw.circle(s, (*base_color, int(alpha * 0.4)), (glow_radius, glow_radius), glow_radius)
    # Camada 2: Núcleo mais forte (perto da borda da roleta)
    pygame.draw.circle(s, (*base_color, int(alpha * 0.8)), (glow_radius, glow_radius), int(raio * 1.1))
    
    # Blit centralizado atrás da roleta
    screen.blit(s, (centro[0] - glow_radius, centro[1] - glow_radius), special_flags=pygame.BLEND_RGBA_ADD)


# ===========================================================
#                    FUNÇÃO PRINCIPAL (ASYNC)
# ===========================================================
async def roleta_risco(screen):
    pygame.display.set_caption("Roleta do Risco - Rodada Bônus")
    clock = pygame.time.Clock()

    # Caminhos
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    assets_dir = os.path.join(base_dir, "assets")
    bg_path = os.path.join(assets_dir, "background", "background_roleta_risco.png")
    perigo_icon_path = os.path.join(assets_dir, "icons", "perigo.png")
    seta_path = os.path.join(assets_dir, "icons", "seta.png")

    bg_original = None
    if os.path.exists(bg_path):
        bg_original = pygame.image.load(bg_path).convert()

    # === CONFIGURAÇÃO DE DIFICULDADE ===
    diff = dm.get_difficulty()
    if diff == 'facil':
        penalidade_baixa = -15; penalidade_alta = -25; bonus_baixo = 25; bonus_alto = 40
    elif diff == 'normal':
        penalidade_baixa = -30; penalidade_alta = -50; bonus_baixo = 30; bonus_alto = 50
    else:
        penalidade_baixa = -50; penalidade_alta = -80; bonus_baixo = 60; bonus_alto = 100

    # === CORES NEON ===
    COLOR_ROSA = (207, 46, 57)  # #cf2e39
    COLOR_AZUL = (32, 18, 204)  # #2012cc

    # Dados da roleta
    eventos_raw = [
        {"nome": "Falha em Servidor", "efeito": penalidade_baixa, "descricao": "Servidor caiu!"},
        {"nome": "Treinamento", "efeito": bonus_baixo, "descricao": "Equipe capacitada!"},
        {"nome": "Ransomware", "efeito": penalidade_alta, "descricao": "Dados sequestrados!"},
        {"nome": "Auditoria capacitada", "efeito": bonus_alto, "descricao": "Compliance total!"},
        {"nome": "Erro Humano", "efeito": penalidade_baixa, "descricao": "Falha operacional!"},
        {"nome": "Automação de processos", "efeito": bonus_baixo, "descricao": "Processos rápidos!"},
        {"nome": "Comunicação pessima", "efeito": penalidade_baixa, "descricao": "Ruído na gestão!"},
        {"nome": "Nova Política", "efeito": bonus_baixo, "descricao": "Governança OK!"},
    ]

    eventos = []
    for i, ev in enumerate(eventos_raw):
        ev["cor"] = COLOR_AZUL if i % 2 == 0 else COLOR_ROSA
        eventos.append(ev)

    num_setores = len(eventos)
    angulo_por_setor = 360.0 / num_setores
    
    # Estados
    angulo_atual = 0.0
    velocidade = 0.0
    girando = False
    is_tension_phase = False
    tension_start_time = 0
    resultado = None
    
    pontos_desta_fase = 0
    sparks = []; gold_sparks = []
    orbit_sparks = [] 
    
    # Efeitos visuais
    result_fade_alpha = 0
    
    layout = {}

    # === RESIZE E LAYOUT ===
    def resize_layout(surface):
        w, h = surface.get_size()
        
        if bg_original:
            layout['bg'] = pygame.transform.scale(bg_original, (w, h))
        else:
            layout['bg'] = pygame.Surface((w, h)); layout['bg'].fill((12, 2, 10))

        title_size = min(int(h * 0.08), int(w * 0.045)) 
        layout['font_title'] = load_font(title_size)
        layout['font_text'] = load_font(max(24, int(h * 0.06)))
        layout['font_small'] = load_font(max(20, int(h * 0.04)))
        layout['font_roleta'] = load_font(max(14, int(h * 0.025))) 
        layout['font_btn'] = load_font(max(28, int(h * 0.05)))

        layout['centro'] = (w // 2, int(h * 0.55)) 
        layout['raio'] = min(w, h) // 3.2

        # Recria partículas orbitais
        nonlocal orbit_sparks
        orbit_sparks = [OrbitSpark(layout['centro'], layout['raio']) for _ in range(16)]

        icon_size = int(h * 0.11)
        layout['icon_warning'] = None
        if os.path.exists(perigo_icon_path):
            img = pygame.image.load(perigo_icon_path).convert_alpha()
            layout['icon_warning'] = pygame.transform.smoothscale(img, (icon_size, icon_size))

        layout['seta_indicador'] = None
        if os.path.exists(seta_path):
            img = pygame.image.load(seta_path).convert_alpha()
            layout['seta_indicador'] = pygame.transform.smoothscale(img, (int(h*0.06), int(h*0.08)))
            layout['seta_rect'] = layout['seta_indicador'].get_rect(midbottom=(layout['centro'][0], layout['centro'][1] - layout['raio']))
        else:
             c = layout['centro']; r = layout['raio']
             layout['indicador_poly'] = [(c[0], c[1] - r - 10), (c[0] - 15, c[1] - r - 35), (c[0] + 15, c[1] - r - 35)]

        btn_w, btn_h = int(w * 0.3), int(h * 0.1)
        layout['btn_girar'] = pygame.Rect((w - btn_w)//2, int(h * 0.85), btn_w, btn_h)

    resize_layout(screen)

    running = True
    float_timer = 0

    while running:
        dt_ms = clock.tick(60)
        dt = dt_ms / 1000.0
        float_timer += dt
        W, H = screen.get_size()
        current_ticks = pygame.time.get_ticks()

        # 1. Background
        screen.blit(layout['bg'], (0, 0))
        
        # === TÍTULO ===
        float_y = math.sin(float_timer * 2.5) * 6 
        titulo_texto = "RODADA BÔNUS   ►   ROLETA DO RISCO"
        t_surf = layout['font_title'].render(titulo_texto, True, (255, 215, 0))
        t_shadow = layout['font_title'].render(titulo_texto, True, (0, 0, 0))
        t_rect = t_surf.get_rect(center=(W // 2, int(H * 0.12) + float_y))
        screen.blit(t_shadow, (t_rect.x + 3, t_rect.y + 3))
        screen.blit(t_surf, t_rect)

        if layout['icon_warning']:
            screen.blit(layout['icon_warning'], (t_rect.left - layout['icon_warning'].get_width() - 20, t_rect.centery - layout['icon_warning'].get_height()//2))
            screen.blit(layout['icon_warning'], (t_rect.right + 20, t_rect.centery - layout['icon_warning'].get_height()//2))

        # === EFEITO PISCA-PISCA TRAS (BACKLIGHT NEON) ===
        draw_neon_backlight(screen, layout['centro'], layout['raio'], current_ticks)

        # === DESENHA A ROLETA (FRENTE) ===
        centro = layout['centro']; raio = layout['raio']
        pygame.draw.circle(screen, (0,0,0), centro, raio) # Fundo preto da pizza

        for i, ev in enumerate(eventos):
            a_i = math.radians(i * angulo_por_setor + angulo_atual)
            a_f = math.radians((i + 1) * angulo_por_setor + angulo_atual)
            p2 = (centro[0] + raio * math.cos(a_i), centro[1] + raio * math.sin(a_i))
            p3 = (centro[0] + raio * math.cos(a_f), centro[1] + raio * math.sin(a_f))
            
            pygame.draw.polygon(screen, ev["cor"], [centro, p2, p3])
            pygame.draw.polygon(screen, (0, 0, 0), [centro, p2, p3], 2) # Linha preta

            # Texto
            nome_split = ev["nome"].split(" ")
            ang_txt = math.radians(i * angulo_por_setor + angulo_atual + angulo_por_setor / 2)
            dist_txt = raio * 0.68
            
            for idx, palavra in enumerate(nome_split):
                offset = (idx - len(nome_split)/2) * 18
                tx = centro[0] + math.cos(ang_txt) * (dist_txt - offset)
                ty = centro[1] + math.sin(ang_txt) * (dist_txt - offset)

                txt_s = layout['font_roleta'].render(palavra, True, (255, 255, 255))
                for ox in [-1, 1]:
                    for oy in [-1, 1]:
                         screen.blit(layout['font_roleta'].render(palavra, True, (0,0,0)), (tx - txt_s.get_width()//2 + ox, ty - txt_s.get_height()//2 + oy))
                screen.blit(txt_s, (tx - txt_s.get_width()//2, ty - txt_s.get_height()//2))

        # Centro
        pygame.draw.circle(screen, (30, 30, 30), centro, raio * 0.15)
        pygame.draw.circle(screen, (255, 215, 0), centro, raio * 0.15, 4)

        # Orbit Sparks (Fagulhas girando em volta)
        for ospark in orbit_sparks:
            ospark.update()
            ospark.draw(screen)

        # Seta
        if layout['seta_indicador']:
            screen.blit(layout['seta_indicador'], layout['seta_rect'])
        else:
            pygame.draw.polygon(screen, (255, 255, 0), layout['indicador_poly'])
            pygame.draw.polygon(screen, (0, 0, 0), layout['indicador_poly'], 2)

        # === LÓGICA DE GIRO ===
        if girando:
            angulo_atual += velocidade
            velocidade *= 0.991 
            
            # PARADA -> INICIA SUSPENSE
            if abs(velocidade) < 0.1:
                girando = False
                is_tension_phase = True
                tension_start_time = current_ticks

        # === FASE DE TENSÃO (DELAY 1.5s) ===
        if is_tension_phase:
            if current_ticks - tension_start_time > 1500:
                is_tension_phase = False
                
                idx = int(((270 - angulo_atual) % 360) // angulo_por_setor)
                resultado = eventos[idx]
                pontos_desta_fase = resultado["efeito"]
                ScoreManager.add_points(pontos_desta_fase)
                
                result_fade_alpha = 0 
                
                ang_s = math.radians(idx * angulo_por_setor + angulo_por_setor / 2.0)
                sx = centro[0] + math.cos(ang_s) * (raio * 0.70)
                sy = centro[1] + math.sin(ang_s) * (raio * 0.70)
                
                if resultado["efeito"] < 0:
                    AudioManager.play_sfx_if_exists("errado")
                    for _ in range(30): sparks.append(SparkParticle(sx, sy))
                else:
                    AudioManager.play_sfx_if_exists("correto")
                    for _ in range(20): gold_sparks.append(SparkGold(sx, sy))

        # Atualiza Partículas de Resultado
        if sparks:
            for s in sparks[:]: s.update(dt_ms); s.draw(screen); 
            if s.life <= 0: sparks.remove(s)
        if gold_sparks:
            for g in gold_sparks[:]: g.update(); g.draw(screen); 
            if g.life <= 0: gold_sparks.remove(g)

        # === UI (Botão Girar) ===
        if not girando and not is_tension_phase and resultado is None:
            btn_rect = layout['btn_girar']
            pulse = math.sin(current_ticks * 0.005) * 5
            draw_rect = btn_rect.inflate(pulse, pulse)
            pygame.draw.rect(screen, (0, 0, 0, 180), draw_rect.move(4,4), border_radius=15)
            pygame.draw.rect(screen, (255, 0, 100), draw_rect, border_radius=15)
            pygame.draw.rect(screen, (255, 255, 255), draw_rect, 3, border_radius=15)
            draw_text(screen, "GIRAR!", layout['font_btn'], (255,255,255), draw_rect.center)

        # === RESULTADO (APARECE SUAVE) ===
        if resultado and not girando and not is_tension_phase:
            result_fade_alpha = min(255, result_fade_alpha + 15)
            glow_color = (255, 200, 100) if resultado["efeito"] > 0 else (255, 100, 100)

            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(result_fade_alpha * 0.7)))
            screen.blit(overlay, (0,0))
            
            rect = pygame.Rect(0, 0, min(W * 0.8, 600), min(H * 0.4, 300))
            rect.center = (W//2, H//2)
            
            draw_question_container(screen, rect, "Resultado", layout['font_small'], 
                                    bg_color=(30, 10, 40, result_fade_alpha), 
                                    border_color=(glow_color[0], glow_color[1], glow_color[2], result_fade_alpha))
            
            if result_fade_alpha > 200:
                glow_surf = pygame.Surface((rect.width+10, rect.height+10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*glow_color, 50), glow_surf.get_rect(), border_radius=20, width=4)
                screen.blit(glow_surf, (rect.x-5, rect.y-5), special_flags=pygame.BLEND_RGBA_ADD)

            sinal = "+" if resultado["efeito"] > 0 else ""
            texto = f"{resultado['nome']}\n\n{resultado['descricao']}\n\nImpacto: {sinal}{resultado['efeito']} Pontos"
            
            if result_fade_alpha > 100:
                draw_text_wrapped(screen, texto, layout['font_text'], (255, 255, 255), rect.inflate(-40,-60))
                blink = int(math.sin(current_ticks * 0.01) * 100 + 155)
                txt_cont = layout['font_small'].render("Toque para continuar", True, (200, 200, 200))
                txt_cont.set_alpha(blink)
                screen.blit(txt_cont, txt_cont.get_rect(center=(W//2, rect.bottom + 40)))

        # Score
        displayed = ScoreManager.update_displayed_score()
        draw_score_display(screen, displayed, layout['font_small'], position="topright")

        # === INPUTS ===
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
                screen = pygame.display.get_surface()
                resize_layout(screen)

            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1: 
                    if resultado and not girando and result_fade_alpha > 150:
                        await show_pause_screen(screen, clock, "Fim da Rodada Bônus", f"Pontuação Total: {ScoreManager.get_score()}", theme="Roleta de Risco")
                        return pontos_desta_fase
                    
                    if not girando and not is_tension_phase and resultado is None:
                        AudioManager.play_sfx_if_exists("roleta") 
                        velocidade = random.uniform(22.0, 28.0)
                        girando = True

        pygame.display.flip()
        
        # PONTO CRÍTICO PARA PYBAG:
        await asyncio.sleep(0) 

    return pontos_desta_fase