# ===========================================================
#                MINIGAME PERSEGUIÇÃO (ASYNC/WEB)
# ===========================================================
import pygame
import random
import sys
import time
import os
import math
import asyncio  # <--- NECESSÁRIO PARA PYBAG/WEB

from src.utils import show_pause_screen, draw_text_wrapped, draw_question_container, draw_score_display, load_font
from src.score_manager import ScoreManager
from src.audio_manager import AudioManager
import src.difficulty_manager as dm

# ===========================================================
#            BANCO DE INCIDENTES (6 POR NÍVEL)
# ===========================================================
ALL_INCIDENTS = {
    "facil": [
        {"descricao": "Um e-mail suspeito foi aberto por um funcionário.", "opcoes": ["Acionar resposta a incidentes", "Ignorar o ocorrido"], "correta": "Acionar resposta a incidentes"},
        {"descricao": "Um servidor apresentou falhas repetidas.", "opcoes": ["Analisar causa raiz", "Reiniciar e ignorar"], "correta": "Analisar causa raiz"},
        {"descricao": "Senha compartilhada no chat da empresa.", "opcoes": ["Redefinir senha agora", "Deixar pra lá"], "correta": "Redefinir senha agora"},
        {"descricao": "Visitante estranho tirando fotos do servidor.", "opcoes": ["Chamar segurança", "Perguntar o nome"], "correta": "Chamar segurança"},
        {"descricao": "Antivírus detectou um arquivo malicioso.", "opcoes": ["Quarentena Imediata", "Abrir para ver"], "correta": "Quarentena Imediata"},
        {"descricao": "Notebook corporativo foi perdido.", "opcoes": ["Bloquear acesso remoto", "Esperar ele aparecer"], "correta": "Bloquear acesso remoto"}
    ],
    "normal": [
        {"descricao": "Tentativa de acesso não autorizado no financeiro.", "opcoes": ["Bloquear IP e notificar", "Monitorar em silêncio"], "correta": "Bloquear IP e notificar"},
        {"descricao": "Backup diário falhou por falta de espaço.", "opcoes": ["Liberar espaço e refazer", "Ignorar por hoje"], "correta": "Liberar espaço e refazer"},
        {"descricao": "Funcionário instalou software pirata.", "opcoes": ["Remover e advertir", "Deixar se funcionar"], "correta": "Remover e advertir"},
        {"descricao": "Firewall está bloqueando tráfego legítimo.", "opcoes": ["Ajustar regras", "Desativar firewall"], "correta": "Ajustar regras"},
        {"descricao": "Vazamento de dados de clientes detectado.", "opcoes": ["Acionar plano de crise", "Esconder o fato"], "correta": "Acionar plano de crise"},
        {"descricao": "Usuário com privilégio de admin sem necessidade.", "opcoes": ["Revogar privilégio", "Manter por facilidade"], "correta": "Revogar privilégio"}
    ],
    "dificil": [
        {"descricao": "Ransomware criptografou o servidor de arquivos.", "opcoes": ["Isolar rede e restaurar", "Pagar o resgate"], "correta": "Isolar rede e restaurar"},
        {"descricao": "Ataque DDoS massivo em andamento.", "opcoes": ["Ativar mitigação DDoS", "Desligar o servidor"], "correta": "Ativar mitigação DDoS"},
        {"descricao": "Zero-day exploit divulgado para seu sistema.", "opcoes": ["Aplicar patch/workaround", "Esperar o vendor"], "correta": "Aplicar patch/workaround"},
        {"descricao": "Insider copiando banco de dados para USB.", "opcoes": ["Bloquear porta e conta", "Pedir explicação"], "correta": "Bloquear porta e conta"},
        {"descricao": "Certificado SSL do site expirou.", "opcoes": ["Renovar imediatamente", "Esperar reclamação"], "correta": "Renovar imediatamente"},
        {"descricao": "Logs de auditoria foram apagados.", "opcoes": ["Investigar intrusão", "Restaurar logs"], "correta": "Investigar intrusão"}
    ]
}

# ===========================================================
#            CLASSE: Estrada em Movimento (Speed Lines)
# ===========================================================
class RoadLine:
    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h
        self.x = random.randint(0, screen_w)
        self.y = random.randint(-screen_h, 0)
        self.length = random.randint(20, 60)
        self.speed = random.uniform(10, 25) # Alta velocidade
        self.width = random.randint(2, 4)
        self.color = (40, 40, 60) # Cinza azulado escuro

    def update(self):
        self.y += self.speed
        if self.y > self.h:
            self.y = -self.length
            self.x = random.randint(0, self.w)

    def draw(self, surface):
        pygame.draw.line(surface, self.color, (self.x, self.y), (self.x, self.y + self.length), self.width)


# ===========================================================
#             FUNÇÃO PRINCIPAL (AGORA ASYNC)
# ===========================================================
async def run_perseguicao(screen):
    pygame.display.set_caption("🚨 Perseguição — Decisões Rápidas 🚨")
    clock = pygame.time.Clock()

    # === CARREGAMENTO DE ASSETS ===
    layout = {}
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    assets_dir = os.path.join(base_dir, "assets")
    
    # Paths
    bg_path = os.path.join(assets_dir, "background", "background_perseguicao.png")
    police_path = os.path.join(assets_dir, "icons", "police_car.png")
    hacker_path = os.path.join(assets_dir, "icons", "hacker.png")
    lock_path = os.path.join(assets_dir, "icons", "cadeado.png") 
    
    # Carregamento Inicial
    bg_original = None
    if os.path.exists(bg_path):
        bg_original = pygame.image.load(bg_path).convert()

    img_police = pygame.image.load(police_path).convert_alpha() if os.path.exists(police_path) else None
    img_hacker = pygame.image.load(hacker_path).convert_alpha() if os.path.exists(hacker_path) else None
    img_lock = pygame.image.load(lock_path).convert_alpha() if os.path.exists(lock_path) else None

    # === FUNÇÃO DE RESIZE ===
    def resize_assets(surface):
        w, h = surface.get_size()
        
        if bg_original:
            layout['background'] = pygame.transform.scale(bg_original, (w, h))
        else:
            layout['background'] = pygame.Surface((w, h))
            layout['background'].fill((10, 10, 15)) 

        # Fontes
        layout['font_title'] = load_font(max(48, int(h * 0.07)))
        layout['font_text'] = load_font(max(40, int(h * 0.06)))
        layout['font_small'] = load_font(max(28, int(h * 0.045)))
        layout['font_timer'] = load_font(max(24, int(h * 0.035)))

        icon_size = int(h * 0.06)
        
        if img_hacker:
            layout['icon_hacker'] = pygame.transform.smoothscale(img_hacker, (int(icon_size*1.2), int(icon_size*1.2)))
        else:
            s = pygame.Surface((icon_size, icon_size)); s.fill((255, 50, 50))
            layout['icon_hacker'] = s

        if img_lock:
            title_icon_size = int(h * 0.085) 
            layout['icon_title'] = pygame.transform.smoothscale(img_lock, (title_icon_size, title_icon_size))
        else:
            layout['icon_title'] = None

    resize_assets(screen)

    # === EFEITOS ===
    road_lines = [RoadLine(screen.get_width(), screen.get_height()) for _ in range(25)]
    shake_amount = 0

    # === LÓGICA DE JOGO ===
    diff_rules = dm.get_rules()
    q_type = dm.get_question_set_type()
    
    tempo_base = diff_rules.get("perseguicao_tempo", diff_rules.get("tempo_pergunta", 5))
    
    incidentes = ALL_INCIDENTS.get(q_type, ALL_INCIDENTS["normal"])
    random.shuffle(incidentes)
    
    pontos_acerto = 10 + diff_rules["bonus_acerto"]
    pontos_erro = -diff_rules["perda_pontos"]

    indice = 0
    feedback = None
    start_time = time.time()
    frame = 0
    pontos_desta_fase = 0
    jogo_ativo = True
    
    last_correct_pos = -1
    transitioning = False
    transition_start_time = 0
    TRANSITION_DURATION = 0.6 

    # Loop Principal
    while jogo_ativo:
        frame += 1
        dt = clock.tick(60) / 1000.0

        # Transição
        if transitioning:
            if time.time() - transition_start_time > TRANSITION_DURATION:
                transitioning = False
                feedback = None
                indice += 1
                start_time = time.time()
        
        # Shake Decay
        if shake_amount > 0:
            shake_amount -= 0.5
            if shake_amount < 0: shake_amount = 0
        
        shake_x = random.randint(-int(shake_amount), int(shake_amount))
        shake_y = random.randint(-int(shake_amount), int(shake_amount))
        
        # Desenho Background
        screen.blit(layout['background'], (0, 0))
        bg_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for line in road_lines:
            line.update()
            line.draw(bg_surface)
        screen.blit(bg_surface, (shake_x, shake_y))

        w, h = screen.get_size()

        # Vignette
        sirene_alpha = int(abs(math.sin(frame * 0.15)) * 120) 
        is_red_phase = (frame // 30) % 2 == 0
        sirene_color = (255, 0, 0) if is_red_phase else (0, 0, 255)
        
        top_rect = pygame.Surface((w, 30)); top_rect.fill(sirene_color); top_rect.set_alpha(sirene_alpha)
        bottom_rect = pygame.Surface((w, 30)); bottom_rect.fill(sirene_color); bottom_rect.set_alpha(sirene_alpha)
        screen.blit(top_rect, (0, 0))
        screen.blit(bottom_rect, (0, h - 30))
        
        # HUD Surface
        hud_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # --- TÍTULO CENTRAL ---
        float_offset = math.sin(frame * 0.05) * 5
        title_text = "ALERTA DE SEGURANÇA"
        title_color = (255, 215, 0) # Amarelo Ouro Neon
        
        title_surf = layout['font_title'].render(title_text, True, title_color)
        title_shadow = layout['font_title'].render(title_text, True, (0, 0, 0))
        
        title_rect = title_surf.get_rect(center=(w // 2, int(h * 0.10) + float_offset))
        
        # Desenha Título
        hud_surface.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
        hud_surface.blit(title_surf, title_rect)

        # --- ÍCONES CADEADO FLUTUANTES ---
        if layout['icon_title']:
            icon_y = title_rect.centery - (layout['icon_title'].get_height() // 2)
            glow_intensity = int((math.sin(pygame.time.get_ticks() * 0.008) + 1) * 127.5)
            
            icon_glow = layout['icon_title'].copy()
            icon_glow.set_alpha(glow_intensity)

            left_pos = (title_rect.left - layout['icon_title'].get_width() - 20, icon_y)
            right_pos = (title_rect.right + 20, icon_y)

            hud_surface.blit(layout['icon_title'], left_pos) 
            hud_surface.blit(icon_glow, left_pos, special_flags=pygame.BLEND_ADD)

            hud_surface.blit(layout['icon_title'], right_pos) 
            hud_surface.blit(icon_glow, right_pos, special_flags=pygame.BLEND_ADD)

        draw_score_display(hud_surface, ScoreManager.get_score(), layout['font_small'], position="topright")

        if indice < len(incidentes):
            inc = incidentes[indice]
            
            # Shuffling Logic
            if 'shuffled_opcoes' not in inc:
                opts = inc["opcoes"][:]
                correta = inc["correta"]
                attempts = 0
                while True:
                    random.shuffle(opts)
                    try:
                        new_pos = opts.index(correta)
                    except ValueError: new_pos = 0 
                    if new_pos != last_correct_pos or attempts > 5:
                        last_correct_pos = new_pos
                        break
                    attempts += 1
                inc['shuffled_opcoes'] = opts
            
            opcoes_display = inc['shuffled_opcoes']
            
            if not transitioning:
                tempo_restante = max(0, tempo_base - (time.time() - start_time))
            else:
                tempo_restante = max(0, tempo_base - (transition_start_time - start_time))

            # --- LAYOUT DINÂMICO ---
            container_x = 100
            container_w = w - 200
            text_margin = 30
            
            def get_text_height(text, font, max_width):
                words = text.split(' ')
                lines = []
                current_line = []
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    if font.size(test_line)[0] <= max_width:
                        current_line.append(word)
                    else:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                lines.append(' '.join(current_line))
                return len(lines) * font.get_linesize()

            text_h = get_text_height(inc["descricao"], layout['font_text'], container_w - (text_margin * 2))
            
            container_min_h = int(h * 0.18)
            container_calculated_h = 60 + text_h + 40
            container_h = max(container_min_h, container_calculated_h)
            
            container_y = int(h * 0.22) + float_offset
            container_rect = pygame.Rect(container_x, container_y, container_w, container_h)
            
            pygame.draw.rect(hud_surface, (0, 20, 10, 200), container_rect, border_radius=8) 
            pygame.draw.rect(hud_surface, (0, 255, 0), container_rect, 2, border_radius=8) 
            
            if frame % 40 < 20:
                warn = layout['font_small'].render("> INCIDENTE DETECTADO <", True, (255, 0, 0))
                warn_rect = warn.get_rect(midtop=(container_rect.centerx, container_rect.top + 10))
                hud_surface.blit(warn, warn_rect)

            text_area = pygame.Rect(container_rect.left + text_margin, container_rect.top + 60, container_rect.width - (text_margin * 2), text_h)
            draw_text_wrapped(hud_surface, inc["descricao"], layout['font_text'], (200, 255, 200), text_area)

            # --- BOTÕES ---
            botoes = []
            largura_botao = int(w * 0.40)
            altura_botao = int(h * 0.16)
            espaco = 60
            total_largura = (2 * largura_botao) + espaco
            btn_start_x = (w - total_largura) // 2
            
            y_base = container_rect.bottom + int(h * 0.05)

            mouse_pos = pygame.mouse.get_pos()
            adj_mouse = (mouse_pos[0] - shake_x, mouse_pos[1] - shake_y)

            for i, opcao in enumerate(opcoes_display):
                offset_anim = max(0, (20 - (time.time() - start_time)*40)) * (-1 if i==0 else 1) 
                rect = pygame.Rect(btn_start_x + i * (largura_botao + espaco) + offset_anim, y_base, largura_botao, altura_botao)
                botoes.append((rect, opcao))
                
                hover = rect.collidepoint(adj_mouse)
                cor_fundo = (20, 40, 90, 230)
                cor_borda = (0, 150, 255)

                if transitioning:
                    if opcao == inc["correta"]:
                        cor_fundo = (0, 180, 0, 230)
                        cor_borda = (255, 255, 255)
                else:
                    if hover:
                        cor_fundo = (40, 80, 160, 240)
                        cor_borda = (255, 255, 255)

                pygame.draw.rect(hud_surface, cor_fundo, rect, border_radius=10)
                pygame.draw.rect(hud_surface, cor_borda, rect, 2, border_radius=10)
                pygame.draw.line(hud_surface, cor_borda, (rect.right-15, rect.bottom-5), (rect.right-5, rect.bottom-15), 2)
                draw_text_wrapped(hud_surface, opcao, layout['font_small'], (255, 255, 255), rect.inflate(-20, -20))

            # --- HUD INFERIOR: BARRA UNIFICADA ---
            track_h = 16
            
            # AJUSTE 1: Empurrei a barra mais para baixo (de 0.08 para 0.12)
            track_y = y_base + altura_botao + int(h * 0.12) 
            
            track_x_start = w * 0.1
            track_x_end = w * 0.9
            track_width = track_x_end - track_x_start
            
            ratio = tempo_restante / tempo_base
            progress = 1.0 - ratio
            
            if progress < 0.5: bar_color = (0, 255, 0)
            elif progress < 0.8: bar_color = (255, 255, 0)
            else: bar_color = (255, 0, 0)

            pygame.draw.rect(hud_surface, (40, 40, 50), (track_x_start, track_y, track_width, track_h), border_radius=8)
            current_bar_width = int(track_width * progress)
            if current_bar_width > 0:
                pygame.draw.rect(hud_surface, bar_color, (track_x_start, track_y, current_bar_width, track_h), border_radius=8)

            h_icon = layout['icon_hacker']
            h_x = track_x_start + current_bar_width
            hud_surface.blit(h_icon, (h_x - h_icon.get_width()//2, track_y + track_h//2 - h_icon.get_height()//2))

            pygame.draw.circle(hud_surface, (50, 100, 255), (int(track_x_end), int(track_y + track_h//2)), 10)
            pygame.draw.circle(hud_surface, (255, 255, 255), (int(track_x_end), int(track_y + track_h//2)), 10, 2)

            color_timer = (255, 255, 255)
            if tempo_restante < 2: color_timer = (255, 50, 50)
            timer_surf = layout['font_timer'].render(f"IMPACTO EM: {tempo_restante:.2f}s", True, color_timer)
            
            # AJUSTE 2: Subi o texto do timer (de -35 para -60)
            hud_surface.blit(timer_surf, (w//2 - timer_surf.get_width()//2, track_y - 60))

            screen.blit(hud_surface, (shake_x, shake_y))

            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                        screen = pygame.display.get_surface()
                        resize_assets(screen)
                        road_lines = [RoadLine(screen.get_width(), screen.get_height()) for _ in range(25)]
                    elif event.key == pygame.K_ESCAPE:
                        if pygame.display.is_fullscreen():
                            pygame.display.toggle_fullscreen()
                            screen = pygame.display.get_surface()
                            resize_assets(screen)
                        else: return pontos_desta_fase

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not transitioning:
                    pos = pygame.mouse.get_pos()
                    adj_click = (pos[0] - shake_x, pos[1] - shake_y)
                    for rect, opcao in botoes:
                        if rect.collidepoint(adj_click):
                            transitioning = True
                            transition_start_time = time.time()
                            if opcao == inc["correta"]:
                                pontos_desta_fase += pontos_acerto
                                ScoreManager.add_points(pontos_acerto)
                                feedback = ("AMEAÇA NEUTRALIZADA", True)
                                AudioManager.play_sfx_if_exists("correto")
                                shake_amount = 0 
                            else:
                                pontos_desta_fase += pontos_erro
                                ScoreManager.add_points(pontos_erro)
                                feedback = ("FALHA NA RESPOSTA", False)
                                AudioManager.play_sfx_if_exists("errado")
                                shake_amount = 15 

            if tempo_restante <= 0 and not transitioning:
                transitioning = True
                transition_start_time = time.time()
                pontos_desta_fase += pontos_erro
                ScoreManager.add_points(pontos_erro)
                feedback = ("SISTEMA COMPROMETIDO", False)
                shake_amount = 20
                AudioManager.play_sfx_if_exists("errado")

        else:
            AudioManager.play_sfx_if_exists("roleta")
            # ATENÇÃO: show_pause_screen deve ser NON-BLOCKING ou ter seu próprio await
            await show_pause_screen(screen, clock, "Relatório de Incidente", f"Pontuação Final: {ScoreManager.get_score()}", theme="Perseguição")
            jogo_ativo = False

        if feedback and transitioning:
            msg, acerto = feedback
            bg_col = (0, 100, 0, 220) if acerto else (140, 0, 0, 220)
            fb_surf = pygame.Surface((w, 80), pygame.SRCALPHA)
            fb_surf.fill(bg_col)
            txt = layout['font_title'].render(msg, True, (255, 255, 255))
            if txt.get_height() > 60:
                scale = 60 / txt.get_height()
                txt = pygame.transform.scale(txt, (int(txt.get_width()*scale), int(txt.get_height()*scale)))
            fb_surf.blit(txt, txt.get_rect(center=(w//2, 40)))
            screen.blit(fb_surf, (0, h//2 - 40))

        pygame.display.flip()
        
        if shake_amount > 0 and shake_amount < 2: shake_amount = 0
        
        # PONTO CRÍTICO PARA PYBAG:
        await asyncio.sleep(0)

    return pontos_desta_fase