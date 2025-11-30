# ===========================================================
#                CUTSCENE FINAL (ASYNC/WEB)
# ===========================================================

import pygame
import sys
import os
import random
import math
from math import sin
import asyncio  # <--- IMPORTANTE PARA WEB

from src.utils import (
    load_font, draw_text, draw_text_wrapped, draw_modern_container, 
    fade_in, fade_out
)
from src.audio_manager import audio_manager
import src.difficulty_manager as dm


# ===========================================================
# CLASSES E UTILITÁRIOS LOCAIS
# ===========================================================

def _blur_surface(surface, amount=10):
    """Gera um blur rápido reduzindo e ampliando a imagem."""
    if amount <= 1: return surface
    w, h = surface.get_size()
    small = pygame.transform.smoothscale(surface, (max(1, w//amount), max(1, h//amount)))
    return pygame.transform.smoothscale(small, (w, h))

class StarParticle:
    """Partículas sutis para o fundo (Poeira Estelar)"""
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.reset(first_time=True)

    def reset(self, first_time=False):
        self.x = random.randint(0, self.w)
        if first_time: self.y = random.randint(0, self.h)
        else: self.y = self.h + 10
        self.speed = random.uniform(0.3, 0.9) # Velocidade lenta e calma
        self.size = random.randint(1, 2)      # Pequenas
        self.alpha = random.randint(80, 180)  # Transparência média
    
    def update(self):
        self.y -= self.speed
        if self.y < -10: self.reset()

    def draw(self, surface):
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, int(self.alpha)), (self.size, self.size), self.size)
        surface.blit(s, (int(self.x), int(self.y)))

def draw_glowing_text(screen, text, font, center_pos, time_val):
    """Texto com efeito neon pulsante para o Game Over"""
    glow_intensity = 100 + int(50 * sin(time_val * 0.005))
    glow_color = (200, 220, 255, max(0, min(255, glow_intensity)))
    
    # Glow (blur simulado)
    txt_surf = font.render(text, True, glow_color)
    rect = txt_surf.get_rect(center=center_pos)
    for off in [2, -2]:
        screen.blit(txt_surf, (rect.x + off, rect.y))
        screen.blit(txt_surf, (rect.x, rect.y + off))
        
    # Texto Sólido
    main_surf = font.render(text, True, (255, 255, 255))
    screen.blit(main_surf, rect)


# ===========================================================
#             FUNÇÃO PRINCIPAL (ASYNC)
# ===========================================================
async def run_cutscene_final(screen, final_score):
    clock = pygame.time.Clock()
    
    # Inicia música final
    audio_manager.fade_to_music("cutscene_final", fade_ms=1000)

    # --- CONFIGURAÇÃO DE FONTES ---
    H = screen.get_height()
    font_title = load_font(int(H * 0.055))
    font_body = load_font(int(H * 0.040))
    font_big = load_font(int(H * 0.08))
    font_huge = load_font(int(H * 0.12))
    font_small = load_font(int(H * 0.028))
    
    # ------------------------------------------------------------------
    # ATO 1: PASCAL (A LORE)
    # ------------------------------------------------------------------
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets = os.path.join(base, "assets")
    bg_path = os.path.join(assets, "background", "curtcene.png")
    pascal_path = os.path.join(assets, "sprites", "pascal.png")

    # Background
    if os.path.exists(bg_path):
        raw = pygame.image.load(bg_path).convert()
        raw = pygame.transform.smoothscale(raw, screen.get_size())
        bg = _blur_surface(raw, 8)
    else:
        bg = pygame.Surface(screen.get_size()); bg.fill((15, 18, 30))

    # Pascal
    pascal = None
    if os.path.exists(pascal_path):
        pascal = pygame.image.load(pascal_path).convert_alpha()

    # Texto do Pascal
    if final_score < 250:
        p_title = "esse é Apenas o inicio."
        p_body = "Os desafios foram grandes, mas a Governança é um processo de melhoria contínua. Não desanime! O reino precisa de persistência."
    elif final_score < 450:
        p_title = "Bom Trabalho, Guardião!"
        p_body = "Você mostrou competência e equilibrou bem as decisões. O reino está mais seguro graças à sua gestão. Continue evoluindo!"
    else:
        p_title = "Extraordinário!"
        p_body = "Sua gestão foi impecável! Os processos estão alinhados e o valor foi entregue. Você é um verdadeiro Mestre da Governança!"

    # Loop Ato 1
    # CORRIGIDO: Adicionado await
    await fade_in(screen)
    running_act1 = True
    char_idx = 0
    full_text = p_body
    
    while running_act1:
        clock.tick(60)
        screen.blit(bg, (0,0))
        
        # Pascal
        if pascal:
            h_target = int(H * 0.85)
            ratio = pascal.get_width() / pascal.get_height()
            pas_scaled = pygame.transform.smoothscale(pascal, (int(h_target*ratio), h_target))
            screen.blit(pas_scaled, (int(screen.get_width() * 0.05), H - h_target))

        # Caixa de Texto
        d_rect = pygame.Rect((screen.get_width() * 0.1), H * 0.65, screen.get_width() * 0.8, H * 0.3)
        draw_modern_container(screen, d_rect)
        
        # Título Pascal
        draw_text(screen, p_title, font_title, (255, 215, 0), (d_rect.centerx, d_rect.y + 30))
        
        # Typewriter
        if char_idx < len(full_text): char_idx += 1
        draw_text_wrapped(screen, full_text[:char_idx], font_body, (255,255,255), d_rect.inflate(-40, -80))

        # Input
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    audio_manager.play_sfx_if_exists("click")
                    running_act1 = False # Próximo ato

        pygame.display.flip()
        
        # PONTO CRÍTICO ATO 1:
        await asyncio.sleep(0)

    # CORRIGIDO: Adicionado await
    await fade_out(screen)

    # ------------------------------------------------------------------
    # ATO 2: O PLACAR (PONTUAÇÃO + PARTÍCULAS)
    # ------------------------------------------------------------------
    diff = dm.get_difficulty() # facil, normal, dificil
    
    frases = {
        "facil": "Um bom começo é a metade do sucesso.",
        "normal": "A consistência é a chave da excelência.",
        "dificil": "Apenas na maior adversidade provamos nosso valor."
    }
    motivacao = frases.get(diff, "Governança é o caminho.")

    # Partículas do Ato 2 (Poucas: ~25)
    particles_act2 = [StarParticle(screen.get_width(), screen.get_height()) for _ in range(25)]

    # Loop Ato 2
    # CORRIGIDO: Adicionado await
    await fade_in(screen)
    running_act2 = True
    while running_act2:
        clock.tick(60)
        screen.fill((10, 15, 25)) # Fundo sóbrio

        # Atualiza e desenha partículas AO FUNDO
        for p in particles_act2:
            p.update()
            p.draw(screen)

        cx, cy = screen.get_width()//2, screen.get_height()//2

        # Títulos
        draw_text(screen, "PONTUAÇÃO FINAL DO JOGADOR", font_title, (200, 200, 200), (cx, cy - 120))
        
        # Score Gigante
        draw_text(screen, str(final_score), font_huge, (255, 215, 0), (cx, cy), shadow=True)

        # Detalhes
        draw_text(screen, f"Dificuldade: {diff.upper()}", font_body, (100, 200, 255), (cx, cy + 80))
        draw_text(screen, f'"{motivacao}"', font_body, (150, 150, 150), (cx, cy + 140))

        # Aviso
        blink = abs(sin(pygame.time.get_ticks() * 0.005)) * 255
        btn_txt = font_small.render("Toque para continuar", True, (255, 255, 255))
        btn_txt.set_alpha(int(blink))
        screen.blit(btn_txt, btn_txt.get_rect(center=(cx, H - 50)))

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    audio_manager.play_sfx_if_exists("click")
                    running_act2 = False

        pygame.display.flip()
        
        # PONTO CRÍTICO ATO 2:
        await asyncio.sleep(0)
    
    # CORRIGIDO: Adicionado await
    await fade_out(screen)

    # ------------------------------------------------------------------
    # ATO 3: CRÉDITOS (EQUIPE REAL + PARTÍCULAS)
    # ------------------------------------------------------------------
    creditos = [
        ("PARTY PASCAL", "header"),
        ("", "space"),
        ("Game Design & Idealização", "role"),
        ("Marcelo Felipe Beckman", "name"),
        ("", "space"),
        ("UI / UX Design", "role"),
        ("Cleidison Raimundo dos Santos Lima", "name"),
        ("", "space"),
        ("Desenvolvimento & Plataformas", "role"),
        ("Victor Gabriel Cabral da Silva", "name"),
        ("", "space"),
        ("Música & Efeitos Sonoros", "role"),
        ("Marcos França Gino Gonçalves", "name"),
        ("", "space"),
        ("Suporte da Equipe", "role"),
        ("Fernando Luiz Jales Da Rocha", "name"),
        ("", "space"),
        ("Obrigado por jogar!", "header")
    ]

    scroll_y = H + 50
    running_act3 = True
    
    # Partículas do Ato 3 (Poucas: ~25, reaproveitando ou criando novas)
    particles_act3 = [StarParticle(screen.get_width(), screen.get_height()) for _ in range(25)]

    while running_act3:
        dt = clock.tick(60)
        screen.fill((0, 0, 0)) # Fundo Preto

        # Partículas no fundo dos créditos
        for p in particles_act3:
            p.update()
            p.draw(screen)

        # Renderiza texto subindo
        curr_y = scroll_y
        all_passed = True
        
        for linha, tipo in creditos:
            if tipo == "header":
                f, c, off = font_big, (255, 215, 0), 90
            elif tipo == "role":
                f, c, off = font_body, (150, 150, 150), 40
            elif tipo == "name":
                f, c, off = font_title, (255, 255, 255), 60
            else:
                f, c, off = font_body, (0,0,0), 40

            if -100 < curr_y < H + 100:
                draw_text(screen, linha, f, c, (screen.get_width()//2, curr_y))
            
            if curr_y > -50: all_passed = False
            curr_y += off

        scroll_y -= 1.5 # Velocidade de subida

        # Input
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                running_act3 = False # Pula direto

        if all_passed:
            running_act3 = False

        pygame.display.flip()
        
        # PONTO CRÍTICO ATO 3:
        await asyncio.sleep(0)
    
    # CORRIGIDO: Adicionado await
    await fade_out(screen)

    # ------------------------------------------------------------------
    # ATO 4: GAME OVER (LOOP FINAL)
    # ------------------------------------------------------------------
    # Mais partículas aqui para o final dramático (~40)
    particles_act4 = [StarParticle(screen.get_width(), H) for _ in range(40)]
    t = 0
    running_act4 = True
    
    while running_act4:
        dt = clock.tick(60)
        t += dt
        screen.fill((0, 0, 0))

        # Partículas
        for p in particles_act4:
            p.update()
            p.draw(screen)

        # Game Over Neon
        draw_glowing_text(screen, "GAME OVER", font_huge, (screen.get_width()//2, H//2 - 20), t)

        # Botão voltar
        if t > 1500: # Delay dramático
            blink = abs(sin(t * 0.003)) * 255
            back_surf = font_small.render("- Clique para voltar ao Menu -", True, (120, 120, 120))
            back_surf.set_alpha(int(blink))
            screen.blit(back_surf, back_surf.get_rect(center=(screen.get_width()//2, H - 60)))

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1 and t > 1500:
                    audio_manager.play_sfx_if_exists("click")
                    # CORRIGIDO: Adicionado await
                    await fade_out(screen)
                    return # FIM DO JOGO -> Volta pro Main Menu

        pygame.display.flip()
        
        # PONTO CRÍTICO ATO 4:
        await asyncio.sleep(0)