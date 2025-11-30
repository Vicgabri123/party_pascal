#===============================================
#  CUTSCENE - INTRODUÇÃO DO JOGO (ASYNC/WEB)
#===============================================

import pygame
import os
import random
from math import sin
import asyncio  # <--- IMPORTANTE PARA WEB

from src.utils import (
    load_font,
    draw_text,
    draw_text_wrapped,
    draw_text_animated,
    draw_modern_container,
    fade_in,
    fade_out
)

from src.audio_manager import audio_manager


# ============================================================
# Pequeno blur eficiente
# ============================================================
def _blur(surface, amount=12):
    if amount <= 1:
        return surface
    w, h = surface.get_size()
    small = pygame.transform.smoothscale(surface, (w // amount, h // amount))
    return pygame.transform.smoothscale(small, (w, h))


# ============================================================
# Botão PULAR (Skip) - Animado
# ============================================================
class SkipButton:
    def __init__(self, screen_w, font):
        self.text = "PULAR"
        self.font = font
        self.base_color = (200, 50, 50)  # Vermelho Base
        self.hover_color = (230, 80, 80) # Vermelho Claro (Hover)
        self.text_color = (255, 255, 255) # Branco
        
        # Tamanho e Posição
        self.width = 110
        self.height = 45
        self.margin = 25
        
        # Retângulo lógico (sem escala)
        self.rect = pygame.Rect(
            screen_w - self.width - self.margin,
            self.margin,
            self.width,
            self.height
        )
        
        # Animação
        self.scale = 1.0
        self.target_scale = 1.0

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Lógica de animação (Efeito Mola Suave)
        self.target_scale = 1.1 if is_hovered else 1.0
        self.scale += (self.target_scale - self.scale) * 0.2

        # Calcula dimensões animadas
        anim_w = int(self.width * self.scale)
        anim_h = int(self.height * self.scale)
        
        # Cria retângulo centralizado na posição original
        anim_rect = pygame.Rect(0, 0, anim_w, anim_h)
        anim_rect.center = self.rect.center

        # Cor atual
        color = self.hover_color if is_hovered else self.base_color

        # Sombra (para profundidade)
        shadow_rect = anim_rect.copy()
        shadow_rect.move_ip(3, 3)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=12)

        # Desenha o botão
        pygame.draw.rect(screen, color, anim_rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), anim_rect, 2, border_radius=12) # Borda branca
        
        # Renderiza o texto centralizado
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=anim_rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def update_position(self, screen_w):
        # Garante que o botão fique no canto se a tela mudar de tamanho
        self.rect.topright = (screen_w - self.margin, self.margin)


# ============================================================
# Cutscene Intro (ASYNC)
# ============================================================
async def run_cutscene_intro(screen):

    pygame.display.set_caption("Party Pascal — Introdução")
    clock = pygame.time.Clock()

    # Música da cutscene
    audio_manager.fade_to_music("cutscene_intro", fade_ms=1100)

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets = os.path.join(base, "assets")

    # Backgrounds e sprites
    bg_path = os.path.join(assets, "background", "curtcene.png")
    pascal_path = os.path.join(assets, "sprites", "pascal.png")
    click_path = os.path.join(assets, "sounds", "efeitos", "clique.wav")

    # ==================================================================
    # FONTES ESCALÁVEIS (Ajustadas para evitar overflow)
    # ==================================================================
    H = screen.get_height()
    
    # Reduzi levemente o título para garantir que caiba no container
    font_title = load_font(int(H * 0.048)) 
    font_body = load_font(int(H * 0.040))
    font_hint = load_font(int(H * 0.028))
    font_particle = load_font(int(H * 0.034))
    
    # Fonte para o botão Pular
    font_skip = load_font(int(H * 0.032))

    # ==================================================================
    # FUNDO COM BLUR
    # ==================================================================
    if os.path.exists(bg_path):
        raw = pygame.image.load(bg_path).convert()
        raw = pygame.transform.smoothscale(raw, screen.get_size())
        bg = _blur(raw, 10)
    else:
        bg = pygame.Surface(screen.get_size())
        bg.fill((15, 18, 30))

    # Pascal sprite
    pascal = None
    if os.path.exists(pascal_path):
        pascal = pygame.image.load(pascal_path).convert_alpha()

    # clique
    click_sfx = pygame.mixer.Sound("click") if os.path.exists("click") else None

    # ==================================================================
    # PARTÍCULAS ✦
    # ==================================================================
    particles = []
    for i in range(45):
        particles.append({
            "x": random.randint(0, screen.get_width()),
            "y": random.randint(0, screen.get_height()),
            "spd": random.uniform(0.3, 1.0),
            "alpha": random.randint(150, 255),
            "char": random.choice(["✦", "✧", "•", "⋆"])
        })

    # ==================================================================
    # SCRIPT — INTRO + LORE
    # ==================================================================
    script = [
        ("Antes da Jornada…",
        "Em um lugar muito além dos servidores e sistemas, existe o Reino da Governança. "
        "Um mundo onde decisões moldam destinos e cada ação pode criar valor… ou caos."),

        ("A Chegada do Guardião",
        "Eu sou Pascal, o seu guia nesta aventura! Fui criado para proteger este reino mantendo ordem, "
        "controle e sabedoria."),

        ("A Ameaça Invisível",
        "Mas algo está errado… riscos ignorados, decisões ruins e operações desorganizadas estão "
        "abalando todo o reino."),

        ("A Essência da Governança",
        "Para restaurar o equilíbrio, você precisará dominar a Governança de TI: "
        "alinhar objetivos, processos, pessoas e tecnologia."),

        ("Os Cinco Guardiões",
        "EDM a direção; APO o planejamento; BAI a construção; DSS a operação; MEA o monitoramento. "
        "Eles são os pilares que sustentam o Reino da Governança."),

        ("Seu Papel",
        "Você enfrentará desafios inspirados em situações reais de Governança, "
        "tomando decisões rápidas, estratégicas e responsáveis."),

        ("Preparado?",
        "O Reino da Governança depende de você. Vamos começar a Festa!")
    ]

    # ==================================================================
    # Variáveis de animação
    # ==================================================================
    index = 0
    body_text = script[0][1]

    char_index = 0
    char_speed = 18
    last_char = pygame.time.get_ticks()

    # entrada do Pascal
    pas_x = -500
    pas_alpha = 0
    
    # Instancia o Botão Pular
    skip_btn = SkipButton(screen.get_width(), font_skip)

    # CORRIGIDO: Adicionado await
    await fade_in(screen)

    running = True
    t = 0

    # ==================================================================
    # LOOP ASYNC
    # ==================================================================
    while running:
        dt = clock.tick(60)
        t += dt
        W, H = screen.get_size()

        # ---------------------------------------------------------
        # FUNDO + GLOW
        # ---------------------------------------------------------
        screen.blit(bg, (0, 0))

        glow = pygame.Surface((W, H), pygame.SRCALPHA)
        glow.fill((60, 90, 180, int(35 + 20 * sin(t * 0.004))))
        screen.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # ---------------------------------------------------------
        # PARTÍCULAS
        # ---------------------------------------------------------
        for p in particles:
            p["y"] -= p["spd"]
            p["alpha"] -= 1

            if p["alpha"] <= 0 or p["y"] < -30:
                p["x"] = random.randint(0, W)
                p["y"] = random.randint(H, H + 150)
                p["alpha"] = random.randint(150, 255)

            ps = font_particle.render(p["char"], True, (255, 230, 170))
            ps.set_alpha(p["alpha"])
            screen.blit(ps, (p["x"], p["y"]))

        # ---------------------------------------------------------
        # PASCAL ANIMADO
        # ---------------------------------------------------------
        if pascal:
            target_h = int(H * 0.86)
            ratio = pascal.get_width() / pascal.get_height()
            target_w = int(ratio * target_h)

            pas = pygame.transform.smoothscale(pascal, (target_w, target_h))

            # entrada suave
            target_x = int(W * 0.03)
            pas_x += (target_x - pas_x) * 0.12

            # respiração
            scale = 1.0 + 0.012 * sin(t * 0.005)
            pas = pygame.transform.rotozoom(pas, 0, scale)

            # fade
            pas_alpha = min(255, pas_alpha + 4)
            pas.set_alpha(pas_alpha)

            screen.blit(pas, (pas_x, H - pas.get_height()))

        # ---------------------------------------------------------
        # CAIXA DE DIÁLOGO (utils)
        # ---------------------------------------------------------
        d_w = int(W * 0.88)
        d_h = int(H * 0.28)
        d_rect = pygame.Rect((W - d_w)//2, int(H * 0.66), d_w, d_h)

        draw_modern_container(screen, d_rect)

        # Título
        # Ajustado o Y (+25) para descolar do topo da caixa
        draw_text(
            screen,
            script[index][0],
            font_title,
            (255, 230, 170),
            (d_rect.x + 30 + font_title.size(script[index][0])[0]/2, d_rect.y + 25)
        )

        # Typewriter
        now = pygame.time.get_ticks()
        if char_index < len(body_text) and now - last_char >= char_speed:
            char_index += 1
            last_char = now

        ta = d_rect.inflate(-40, -80)

        # Alinhamento justificado (simulado com 'left')
        draw_text_wrapped(
            screen,
            body_text[:char_index],
            font_body,
            (240,240,240),
            ta,
            align="left" 
        )

        # Hint
        if (t // 400) % 2 == 0:
            draw_text(screen, "Clique para avançar", font_hint,
                      (230,230,230), (W//2, int(H * 0.97)))
        
        # ---------------------------------------------------------
        # BOTÃO PULAR (ANIMADO)
        # ---------------------------------------------------------
        skip_btn.update_position(W) # Atualiza se a tela redimensionar
        skip_btn.draw(screen)

        # ---------------------------------------------------------
        # EVENTOS
        # ---------------------------------------------------------
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); exit()

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Verifica clique no botão PULAR
                if skip_btn.is_clicked(mouse_pos):
                    audio_manager.play_sfx_if_exists("click")
                    # CORRIGIDO: Adicionado await
                    await fade_out(screen)
                    return

                # Avança o texto
                audio_manager.play_sfx_if_exists("click")

                if char_index < len(body_text):
                    char_index = len(body_text)
                else:
                    index += 1
                    if index >= len(script):
                        # CORRIGIDO: Adicionado await
                        await fade_out(screen)
                        return

                    body_text = script[index][1]
                    char_index = 0
                    last_char = pygame.time.get_ticks()

        pygame.display.flip()
        
        # PONTO CRÍTICO PARA PYBAG:
        await asyncio.sleep(0)