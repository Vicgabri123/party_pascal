# ===========================================================
#                 MINIGAME STOP (ASYNC/WEB)
# ===========================================================

import pygame
import sys
import time
import os
import random
import math
import asyncio  # <--- ESSENCIAL PARA PYBAG
from src.utils import show_pause_screen, draw_text_wrapped, draw_question_container, draw_score_display, load_font
from src.score_manager import ScoreManager
from src.audio_manager import AudioManager
import src.difficulty_manager as dm


# ===========================================================
#            BANCO DE PERGUNTAS (6 POR NÍVEL)
# ===========================================================
ALL_QUESTIONS = {
    "facil": [
        {"categoria": "Domínio de Governança", "letra": "E", "dica": "Domínio focado em Avaliar, Dirigir e Monitorar.", "opcoes": ["EDM", "Entregar", "Executar", "Estratégia", "Engajar"], "correta": "EDM"},
        {"categoria": "Domínio de Gestão", "letra": "A", "dica": "Domínio focado em Alinhar, Planejar e Organizar.", "opcoes": ["APO", "Avaliar", "Adquirir", "Analisar", "Apoiar"], "correta": "APO"},
        {"categoria": "Domínio de Gestão", "letra": "B", "dica": "Domínio focado em Construir, Adquirir e Implementar.", "opcoes": ["BAI", "Buscar", "Balancear", "Benchmarking", "Basear"], "correta": "BAI"},
        {"categoria": "Domínio de Gestão", "letra": "D", "dica": "Domínio focado em Entregar, Servir e Suportar.", "opcoes": ["DSS", "Desenvolver", "Direcionar", "Diagnosticar", "Documentar"], "correta": "DSS"},
        {"categoria": "Domínio de Gestão", "letra": "M", "dica": "Domínio focado em Monitorar, Avaliar e Analisar.", "opcoes": ["MEA", "Manter", "Melhorar", "Mapear", "Medir"], "correta": "MEA"},
        {"categoria": "Princípio de Governança", "letra": "H", "dica": "Abordagem que considera todos os componentes interconectados.", "opcoes": ["Holística", "Hierárquica", "Humana", "Horizontal", "Homogênea"], "correta": "Holística"}
    ],
    "normal": [
        {"categoria": "Objetivo de Governança", "letra": "V", "dica": "Um dos principais objetivos da governança é a entrega de...", "opcoes": ["Valor", "Vendas", "Velocidade", "Visão", "Validação"], "correta": "Valor"},
        {"categoria": "Componente do Sistema", "letra": "P", "dica": "Componente que descreve as atividades e fluxos de trabalho.", "opcoes": ["Processos", "Pessoas", "Políticas", "Princípios", "Projetos"], "correta": "Processos"},
        {"categoria": "Componente do Sistema", "letra": "E", "dica": "Componente que define a organização e tomada de decisão.", "opcoes": ["Estruturas Organizacionais", "Estratégia", "Ética", "Eficiência", "Escopo"], "correta": "Estruturas Organizacionais"},
        {"categoria": "Fator de Desenho", "letra": "T", "dica": "Fator relacionado ao cenário de ameaças cibernéticas.", "opcoes": ["Threat Landscape", "Tecnologia", "Tempo", "Tamanho", "Transparência"], "correta": "Threat Landscape"},
        {"categoria": "Área de Foco", "letra": "S", "dica": "Área crítica que lida com proteção de dados e ativos.", "opcoes": ["Segurança Cibernética", "Serviços", "Sistemas", "Suporte", "Software"], "correta": "Segurança Cibernética"},
        {"categoria": "Papel de Gestão", "letra": "C", "dica": "Executivo responsável pela tecnologia (sigla).", "opcoes": ["CIO", "CEO", "CFO", "COO", "CTO"], "correta": "CIO"}
    ],
    "dificil": [
        {"categoria": "Conceito Avançado", "letra": "G", "dica": "Diferença fundamental entre Governança e...", "opcoes": ["Gestão", "Gasto", "Ganho", "Garantia", "Guia"], "correta": "Gestão"},
        {"categoria": "Objetivo de Gestão", "letra": "R", "dica": "APO12 foca na gestão de...", "opcoes": ["Risco", "Recursos", "Requisitos", "Relatórios", "Redes"], "correta": "Risco"},
        {"categoria": "Objetivo de Gestão", "letra": "Q", "dica": "APO11 foca na gestão da...", "opcoes": ["Qualidade", "Quantidade", "Questão", "Quadro", "Quota"], "correta": "Qualidade"},
        {"categoria": "Padrão Relacionado", "letra": "I", "dica": "Padrão para gestão de serviços de TI.", "opcoes": ["ITIL", "ISO", "IEEE", "ISACA", "IAM"], "correta": "ITIL"},
        {"categoria": "Padrão Relacionado", "letra": "P", "dica": "Guia de boas práticas para gestão de projetos.", "opcoes": ["PMBOK", "Prince2", "PDCA", "Padrão", "Plano"], "correta": "PMBOK"},
        {"categoria": "Conceito de Design", "letra": "D", "dica": "Sistema de governança que se adapta a mudanças.", "opcoes": ["Dinâmico", "Direto", "Digital", "Durável", "Definido"], "correta": "Dinâmico"}
    ]
}


# ===========================================================
#             SISTEMA DE PARTÍCULAS (STOP 2.0)
# ===========================================================
class StopParticle:
    """Letras flutuantes com rotação e escala (Efeito 3D fake)"""
    def __init__(self, w, h, font):
        self.w, self.h = w, h
        self.font = font
        self.reset(first_time=True)

    def reset(self, first_time=False):
        self.char = random.choice(["S", "T", "O", "P", "?", "!", "$"])
        self.x = random.randint(20, self.w - 20)
        
        if first_time:
            self.y = random.randint(0, self.h)
        else:
            self.y = random.randint(self.h, self.h + 100)
            
        self.speed = random.uniform(0.5, 2.0)
        self.base_alpha = random.randint(40, 100)
        self.scale = random.uniform(0.6, 1.4)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-1, 1)
        
        # Cores Neon
        self.color = random.choice([
            (255, 80, 80),   # Vermelho Neon
            (80, 255, 255),  # Ciano Neon
            (255, 255, 80),  # Amarelo Neon
            (180, 80, 255)   # Roxo Neon
        ])

    def update(self, dt):
        self.y -= self.speed * dt
        self.rotation += self.rot_speed * dt
        
        if self.y < -50:
            self.reset()

    def draw(self, screen):
        # Renderiza texto
        surf = self.font.render(self.char, True, self.color)
        
        # Escala
        w = int(surf.get_width() * self.scale)
        h = int(surf.get_height() * self.scale)
        if w <= 0 or h <= 0: return # Evita crash
        surf = pygame.transform.scale(surf, (w, h))
        
        # Rotação
        surf = pygame.transform.rotate(surf, self.rotation)
        
        # Alpha
        surf.set_alpha(self.base_alpha)
        
        # Centraliza para desenhar
        rect = surf.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(surf, rect)


# ===========================================================
#        ANIMAÇÃO DE ROLETA (ESTILO CASSINO) - ASYNC
# ===========================================================
async def animar_roleta(screen, letra_alvo, layout, clock):
    """Gira letras rapidamente e para na letra alvo com impacto"""
    letras_random = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    w, h = screen.get_size()
    
    # 1. Aceleração inicial
    velocidade = 50 # ms por frame
    total_giros = 20
    
    for i in range(total_giros):
        screen.fill((15, 15, 30)) # Limpa tela
        
        # Desenha Fundo Estático (Grade)
        grid_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for x in range(0, w, 40):
            pygame.draw.line(grid_surf, (255, 255, 255, 10), (x, 0), (x, h))
        screen.blit(grid_surf, (0,0))
        
        # Texto "Sorteando..."
        txt_sorteio = layout['font_text'].render("Sorteando Letra...", True, (200, 200, 200))
        screen.blit(txt_sorteio, txt_sorteio.get_rect(center=(w//2, h*0.3)))
        
        # Letra Atual (Aleatória)
        if i < total_giros - 1:
            char_atual = random.choice(letras_random)
            cor = (150, 150, 150)
            scale = 1.0
        else:
            char_atual = letra_alvo # Último giro é a certa
            cor = (255, 215, 0)
            scale = 1.5

        # Renderiza letra gigante
        font_big = layout['font_letra']
        letra_surf = font_big.render(char_atual, True, cor)
        
        # Se for a última, aplica escala
        if scale != 1.0:
            nw = int(letra_surf.get_width() * scale)
            nh = int(letra_surf.get_height() * scale)
            letra_surf = pygame.transform.scale(letra_surf, (nw, nh))

        rect = letra_surf.get_rect(center=(w//2, h//2))
        
        # Sombra
        sombra = font_big.render(char_atual, True, (0,0,0))
        if scale != 1.0: sombra = pygame.transform.scale(sombra, (nw, nh))
        screen.blit(sombra, (rect.x+5, rect.y+5))
        screen.blit(letra_surf, rect)
        
        pygame.display.flip()
        
        # Controle de tempo (Desacelera no final)
        if i > total_giros - 8:
            velocidade += 40 # Fica mais lento
        
        await asyncio.sleep(velocidade / 1000.0)

    # 2. Impacto Final (Screen Flash)
    flash = pygame.Surface((w, h))
    flash.fill((255, 255, 255))
    screen.blit(flash, (0,0))
    pygame.display.flip()
    
    await asyncio.sleep(0.05) # Delay do flash
    
    AudioManager.play_sfx_if_exists("explosion") # Som de impacto ao parar


# ===========================================================
#             FUNÇÃO PRINCIPAL (ASYNC)
# ===========================================================
async def run_stop(screen):
    pygame.display.set_caption("STOP - Governança de TI")
    clock = pygame.time.Clock()

    # Variáveis de layout
    layout = {}
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    assets_dir = os.path.join(base_dir, "assets")
    bg_path = os.path.join(assets_dir, "background", "background_stop.png")
    
    bg_original = None
    if os.path.exists(bg_path):
        bg_original = pygame.image.load(bg_path).convert()

    # === FUNÇÃO DE RESIZE ===
    def resize_assets(surface):
        w, h = surface.get_size()
        
        if bg_original:
            layout['background'] = pygame.transform.scale(bg_original, (w, h))
        else:
            layout['background'] = pygame.Surface((w, h))
            layout['background'].fill((15, 15, 35))

        # Fontes
        layout['font_title'] = load_font(max(32, int(h * 0.07)))
        layout['font_text'] = load_font(max(24, int(h * 0.05)))
        layout['font_small'] = load_font(max(20, int(h * 0.04)))
        layout['font_letra'] = load_font(max(180, int(h * 0.35))) # Para Roleta
        layout['font_particle'] = load_font(max(40, int(h * 0.08)))

    resize_assets(screen)

    # === PARTÍCULAS ===
    particles = [StopParticle(screen.get_width(), screen.get_height(), layout['font_particle']) for _ in range(30)]

    # === LÓGICA DE JOGO ===
    diff_rules = dm.get_rules()
    q_type = dm.get_question_set_type()
    
    perguntas = ALL_QUESTIONS.get(q_type, ALL_QUESTIONS["normal"])
    random.shuffle(perguntas)
    
    pontos_acerto = 10 + diff_rules["bonus_acerto"]
    pontos_erro = -diff_rules["perda_pontos"]
    
    pontos_desta_fase = 0
    
    # Efeito de Shake
    shake_amount = 0

    # === Loop de Perguntas ===
    for pergunta in perguntas:
        letra = pergunta["letra"]
        categoria = pergunta["categoria"]
        dica = pergunta["dica"]
        opcoes = pergunta["opcoes"][:]
        correta = pergunta["correta"]
        
        random.shuffle(opcoes)

        # 1. Animação de Entrada (Roleta)
        await animar_roleta(screen, letra, layout, clock)

        # Inicia rodada
        rodada_ativa = True
        selecionada_rect = None
        start_time = time.time()
        feedback_color = None

        while rodada_ativa:
            dt = clock.tick(60) / 16.0
            w, h = screen.get_size()
            
            # Shake Decay
            if shake_amount > 0:
                shake_amount -= 0.5
                if shake_amount < 0: shake_amount = 0
            
            shake_x = random.randint(-int(shake_amount), int(shake_amount))
            shake_y = random.randint(-int(shake_amount), int(shake_amount))

            # Desenha Fundo
            screen.blit(layout['background'], (0, 0))
            
            # Partículas
            for p in particles:
                p.update(dt)
                p.draw(screen)

            # Overlay Escuro
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((10, 10, 20, 140))
            screen.blit(overlay, (0, 0))
            
            # Surface do Jogo com Shake
            game_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            
            # Cálculo de Flutuação (Senoide do Tempo)
            float_offset = math.sin(pygame.time.get_ticks() * 0.003) * 6
            
            # Título
            title = layout['font_title'].render("STOP - Governança de TI", True, (255, 215, 0))
            glow_val = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 255
            title_glow = layout['font_title'].render("STOP - Governança de TI", True, (255, 215, 0))
            title_glow.set_alpha(int(glow_val * 0.6))
            
            rect_title = title.get_rect(center=(w // 2, int(h * 0.07)))
            game_surf.blit(title_glow, (rect_title.x-2, rect_title.y-2))
            game_surf.blit(title, rect_title)

            draw_score_display(game_surf, ScoreManager.get_score(), layout['font_text'], position="topright")

            # --- CONTAINER PRINCIPAL FLUTUANTE ---
            base_container_y = int(h * 0.16)
            container_y = base_container_y + float_offset
            container_rect = pygame.Rect(int(w * 0.1), container_y, int(w * 0.8), int(h * 0.24))
            
            # Estilo Cyber
            pygame.draw.rect(game_surf, (20, 30, 60, 180), container_rect, border_radius=15)
            pygame.draw.rect(game_surf, (80, 220, 255), container_rect, 2, border_radius=15)
            
            cx = container_rect.left + 25
            cy = container_rect.top + 20
            
            # Letra em Destaque
            letra_surf = layout['font_title'].render(letra, True, (255, 215, 0))
            pygame.draw.circle(game_surf, (255, 215, 0), (cx + 30, cy + 30), 40, 3)
            letra_rect = letra_surf.get_rect(center=(cx + 30, cy + 30))
            game_surf.blit(letra_surf, letra_rect)
            
            # Textos
            text_x = cx + 90
            cat_surf = layout['font_text'].render(f"Categoria: {categoria}", True, (230, 230, 255))
            game_surf.blit(cat_surf, (text_x, cy))
            
            dica_rect = pygame.Rect(text_x, cy + 40, container_rect.width - 120, container_rect.height - 60)
            draw_text_wrapped(game_surf, f"Dica: {dica}", layout['font_small'], (180, 200, 220), dica_rect, align="left")

            # --- BOTÕES ---
            num_colunas = 3
            botoes = []
            mouse_pos = pygame.mouse.get_pos()
            
            btn_w = int(min(w * 0.25, 340))
            btn_h = int(min(h * 0.12, 110))
            spacing = int(min(w * 0.04, 30))
            linha_y = int(h * 0.50) + float_offset
            grid_w = num_colunas * btn_w + (num_colunas - 1) * spacing
            start_x = (w - grid_w) // 2

            for i, opcao in enumerate(opcoes):
                linha = i // num_colunas
                coluna = i % num_colunas
                bx = start_x + coluna * (btn_w + spacing)
                by = linha_y + linha * (btn_h + spacing)
                rect_base = pygame.Rect(bx, by, btn_w, btn_h)
                
                is_hover = rect_base.collidepoint(mouse_pos)
                
                draw_rect = rect_base.copy()
                if is_hover: draw_rect = rect_base.inflate(10, 10)
                
                botoes.append((rect_base, opcao)) 

                if feedback_color and selecionada_rect == rect_base:
                    bg_color = feedback_color 
                    border_color = (255, 255, 255)
                elif is_hover:
                    bg_color = (100, 120, 220, 200) 
                    border_color = (255, 255, 255)
                else:
                    bg_color = (40, 50, 90, 160)
                    border_color = (100, 150, 200)

                pygame.draw.rect(game_surf, (0, 0, 0, 100), draw_rect.move(4, 6), border_radius=12)
                pygame.draw.rect(game_surf, bg_color, draw_rect, border_radius=12)
                pygame.draw.rect(game_surf, border_color, draw_rect, 2 if not is_hover else 3, border_radius=12)
                draw_text_wrapped(game_surf, opcao, layout['font_small'], (255, 255, 255), draw_rect.inflate(-16, -16))

            screen.blit(game_surf, (shake_x, shake_y))
            
            if feedback_color:
                flash_surf = pygame.Surface((w, h), pygame.SRCALPHA)
                flash_surf.fill(feedback_color + (50,)) 
                screen.blit(flash_surf, (0,0))

            pygame.display.flip()
            await asyncio.sleep(0)

            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                        screen = pygame.display.get_surface()
                        resize_assets(screen)
                        particles = [StopParticle(screen.get_width(), screen.get_height(), layout['font_particle']) for _ in range(30)]
                    elif event.key == pygame.K_ESCAPE:
                        return pontos_desta_fase

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not selecionada_rect:
                    pos = pygame.mouse.get_pos()
                    
                    for rect, opcao in botoes:
                        if rect.collidepoint(pos):
                            selecionada_rect = rect
                            tempo_total = round(time.time() - start_time, 2)
                            pontos_ganhos = 0

                            if opcao == correta:
                                pontos_ganhos = pontos_acerto
                                feedback_msg = "Resposta correta!"
                                feedback_color = (50, 255, 50) 
                                AudioManager.play_sfx_if_exists("correto")
                            else:
                                pontos_ganhos = pontos_erro
                                feedback_msg = "Resposta incorreta!"
                                feedback_color = (255, 50, 50) 
                                AudioManager.play_sfx_if_exists("errado")
                                shake_amount = 15
                            
                            pontos_desta_fase += pontos_ganhos
                            ScoreManager.add_points(pontos_ganhos)
                            
                            # Pequena pausa visual no botão (Async)
                            await asyncio.sleep(0.5)

                            # --- VOLTANDO A USAR show_pause_screen (COM AWAIT) ---
                            # Isso restaura o feedback visual completo que você queria
                            await show_pause_screen(
                                screen, clock,
                                feedback_msg,
                                f"Pontuação total: {ScoreManager.get_score()} | Tempo: {tempo_total}s",
                                f"Categoria: {categoria}",
                                theme="STOP"
                            )
                            
                            rodada_ativa = False
                            break

    # Tela Final (Async Loop via show_pause_screen)
    AudioManager.play_sfx_if_exists("roleta")
    await show_pause_screen(screen, clock, "Fim do Desafio STOP!", f"Pontuação Final: {ScoreManager.get_score()}", theme="STOP")
    
    return pontos_desta_fase