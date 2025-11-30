#=======================================================
#               GAME LOOP PRINCIPAL (WEB READY)
#========================================================

"""
Loop principal e controle de estados do jogo Party Pascal.
Gerencia o menu, minigames e tela final com pontuação integrada e animada.
Adaptado para Pygbag/Web (Async/Await).
"""

import asyncio # <--- OBRIGATÓRIO
import pygame
import sys
import os
import random
import traceback
from math import sin

from src.utils import show_pause_screen, load_font
from src.score_manager import ScoreManager
from src.audio_manager import AudioManager

# Minigames
from src.minigames.show_do_bilhao import run_show_do_bilhao
from src.minigames.batalha_naval import run_batalha_naval
from src.minigames.maleta_certa import run_maleta_certa
from src.minigames.roleta_risco import roleta_risco
from src.minigames.perseguicao import run_perseguicao
from src.minigames.stop import run_stop

# Cutscene Final
from src.cutscene_final import run_cutscene_final

# BGs Globais
bg_start = None
bg_exit = None
bg_start_original = None
bg_exit_original = None


def resize_backgrounds(screen):
    global bg_start, bg_exit, bg_start_original, bg_exit_original
    if bg_start_original:
        bg_start = pygame.transform.scale(bg_start_original, screen.get_size())
    if bg_exit_original:
        bg_exit = pygame.transform.scale(bg_exit_original, screen.get_size())


async def show_intro_screen(screen, clock):
    resize_backgrounds(screen)
    font_big = load_font(60)

    AudioManager.play_music_if_exists("loop_start")

    start_time = pygame.time.get_ticks()
    duration = 4000 

    running = True
    while running:
        elapsed = pygame.time.get_ticks() - start_time
        if elapsed >= duration:
            running = False

        if bg_start:
            screen.blit(bg_start, (0, 0))
        else:
            screen.fill((10, 10, 30))

        alpha = abs(sin(elapsed * 0.005)) * 255
        surf = font_big.render("Preparando o Palco...", True, (255, 215, 0))
        surf.set_alpha(int(alpha))
        screen.blit(surf, surf.get_rect(center=(screen.get_width()//2, screen.get_height() - 80)))

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_F11:
                    is_full = pygame.display.get_surface().get_flags() & pygame.FULLSCREEN
                    if is_full:
                        screen = pygame.display.set_mode((1024, 600), pygame.RESIZABLE)
                    else:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    resize_backgrounds(screen)
                elif ev.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    running = False

        pygame.display.flip()
        
        # CORREÇÃO: AWAIT PARA NÃO TRAVAR
        await asyncio.sleep(0)
        clock.tick(60)


async def show_stage_transition(screen, stage_num, stage_name):
    clock = pygame.time.Clock()
    font_big = load_font(80)
    font_small = load_font(36)
    font_particle = load_font(24)

    start = pygame.time.get_ticks()
    duration = 3000

    styles = {
        "Show do Bilhão": {"bg": (10, 10, 30), "accent": (255, 215, 0), "type": "char", "content": ["$"], "color": (255, 215, 0)},
        "Batalha Naval": {"bg": (5, 20, 60), "accent": (80, 200, 255), "type": "circle", "color": (120, 180, 255)},
        "Maleta Certa": {"bg": (40, 0, 0), "accent": (255, 60, 60), "type": "char", "content": ["M"], "color": (255, 200, 100)},
        "Roleta de Risco": {"bg": (40, 0, 70), "accent": (255, 120, 255), "type": "char", "content": ["!", "?"], "color": (255, 120, 255)},
        "Perseguição": {"bg": (10, 10, 10), "accent": (255, 220, 50), "type": "char", "content": ["!"], "color": (255, 50, 50)},
        "STOP": {"bg": (0, 70, 0), "accent": (255, 255, 255), "type": "char", "content": ["S", "T", "O", "P"], "color": (255, 255, 255)},
    }

    style = styles.get(stage_name, styles["Show do Bilhão"])

    particles = []
    W, H = screen.get_size()
    for _ in range(45):
        p = {"x": random.randint(0, W), "y": random.randint(0, H), "r": random.randint(2, 6), "alpha": random.randint(130, 255), "speed": random.uniform(0.5, 2)}
        if style["type"] == "char": p["char"] = random.choice(style["content"])
        particles.append(p)

    running = True
    while running:
        elapsed = pygame.time.get_ticks() - start
        t = elapsed / duration
        if t >= 1: running = False

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
                is_full = pygame.display.get_surface().get_flags() & pygame.FULLSCREEN
                if is_full: screen = pygame.display.set_mode((1024, 600), pygame.RESIZABLE)
                else: screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                resize_backgrounds(screen)

        screen.fill(style["bg"])

        for p in particles:
            p["y"] -= p["speed"]; p["alpha"] -= 2
            if p["y"] < -10 or p["alpha"] <= 0:
                p["x"] = random.randint(0, W); p["y"] = random.randint(H, H + 80); p["alpha"] = random.randint(150, 255)
            
            base = style["color"]
            col = (base[0], base[1], base[2], int(p["alpha"]))

            if style["type"] == "char":
                surf = font_particle.render(p["char"], True, col); surf.set_alpha(col[3])
                screen.blit(surf, (int(p["x"]), int(p["y"])))
            else:
                surf = pygame.Surface((p["r"]*2, p["r"]*2), pygame.SRCALPHA)
                pygame.draw.circle(surf, col, (p["r"], p["r"]), p["r"])
                screen.blit(surf, (int(p["x"]), int(p["y"])))

        fade = int(255 * min(t * 1.5, 1))
        title = font_big.render(stage_name, True, style["accent"])
        title.set_alpha(fade)
        screen.blit(title, title.get_rect(center=(W//2, H//2 - 50)))

        try: sc = ScoreManager.update_displayed_score()
        except: sc = ScoreManager.get_score()
        score_surf = font_small.render(f"Pontuação total: {sc}", True, (240, 240, 240))
        score_surf.set_alpha(fade)
        screen.blit(score_surf, score_surf.get_rect(center=(W//2, H//2 + 60)))

        pygame.display.flip()
        
        # CORREÇÃO: AWAIT PARA NÃO TRAVAR
        await asyncio.sleep(0)
        clock.tick(60)
        
    # CORREÇÃO: TROCAR TIME.DELAY POR ASYNC SLEEP
    await asyncio.sleep(0.4)


async def start_game_loop(screen):
    global bg_start_original, bg_exit_original

    pygame.display.set_caption("Party Pascal - Fases")
    clock = pygame.time.Clock()

    ScoreManager.reset()
    current_stage = 0

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bg_dir = os.path.join(base_dir, "assets", "background")

    try: bg_start_original = pygame.image.load(os.path.join(bg_dir, "loop_start.png")).convert()
    except: bg_start_original = None
    try: bg_exit_original = pygame.image.load(os.path.join(bg_dir, "loop_exit.png")).convert()
    except: bg_exit_original = None

    resize_backgrounds(screen)
    
    # CORREÇÃO: CHAMADA COM AWAIT
    await show_intro_screen(screen, clock)

    fases = [
        ("Show do Bilhão", run_show_do_bilhao, "musica_show_do_bilhao"),
        ("Batalha Naval", run_batalha_naval, "musica_batalha_naval"),
        ("Maleta Certa", run_maleta_certa, "musica_maleta_certa"),
        ("Roleta de Risco", roleta_risco, "musica_rodada_bonus"),
        ("Perseguição", run_perseguicao, "musica_perseguicao"),
        ("STOP", run_stop, "musica_stop"),
    ]

    while True:
        if current_stage < len(fases):
            nome_fase, funcao, musica_key = fases[current_stage]

            AudioManager.play_music_if_exists(musica_key)
            
            # CORREÇÃO: CHAMADA COM AWAIT
            await show_stage_transition(screen, current_stage + 1, nome_fase)

            try:
                # CORREÇÃO CRÍTICA: CHAMAR O MINIGAME COM AWAIT
                # O minigame (funcao) deve ser 'async def'
                pontos = await funcao(screen)
            except Exception as e:
                print(f"\n========================================")
                print(f"ERRO CRÍTICO NO MINIGAME: {nome_fase}")
                print(f"Erro: {e}")
                traceback.print_exc() 
                print(f"========================================\n")
                pontos = 0
                
                # CORREÇÃO: PAUSA DE ERRO ASYNC
                await asyncio.sleep(2)

            if pontos is None: pontos = 0
            
            current_stage += 1

        else:
            final_score = ScoreManager.get_score()
            resize_backgrounds(screen)
            AudioManager.play_music_if_exists("musica_final")

            # CORREÇÃO: CHAMADA COM AWAIT
            await show_pause_screen(screen, clock, "Jogo Concluído!",
                              f"Pontuação Total: {final_score}",
                              "Pressione para continuar...", background=bg_exit)

            # CORREÇÃO: CHAMADA COM AWAIT
            await run_cutscene_final(screen, final_score)
            return

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_F11:
                    is_full = pygame.display.get_surface().get_flags() & pygame.FULLSCREEN
                    if is_full: screen = pygame.display.set_mode((1024, 600), pygame.RESIZABLE)
                    else: screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    resize_backgrounds(screen)
                elif ev.key == pygame.K_ESCAPE:
                    # Cancela o jogo e volta ao menu
                    return

        clock.tick(60)
        
        # CORREÇÃO: AWAIT NO LOOP PRINCIPAL DE FASES
        await asyncio.sleep(0)