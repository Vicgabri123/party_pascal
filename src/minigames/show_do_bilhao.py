# ===========================================================
#           MINIGAME SHOW DO BILHÃO 
# ===========================================================

import asyncio  # <--- 1. IMPORT ESSENCIAL
import pygame
import sys
import os
import random
import math
import time
from src.utils import draw_text_wrapped, draw_score_display, load_font, show_pause_screen
from src.score_manager import ScoreManager
from src.audio_manager import AudioManager
import src.difficulty_manager as dm

# ===========================================================
#            BANCO DE PERGUNTAS (MANTIDO)
# ===========================================================
ALL_QUESTIONS = {
    "facil": [
        {
            "pergunta": "Qual é o principal objetivo da Governança de TI?",
            "opcoes": {"A": "Consertar computadores", "B": "Alinhar TI aos objetivos estratégicos", "C": "Criar jogos digitais", "D": "Instalar redes Wi-Fi"},
            "resposta": "B",
            "motivos": {"B": "A Governança garante que a tecnologia suporte e estenda as estratégias e objetivos da organização."}
        },
        {
            "pergunta": "O COBIT faz uma distinção clara entre dois conceitos. Quais são?",
            "opcoes": {"A": "Hardware e Software", "B": "Governança e Gestão", "C": "Lucro e Prejuízo", "D": "Diretores e Gerentes"},
            "resposta": "B",
            "motivos": {"B": "O COBIT separa claramente as atividades de Governança (avaliar/dirigir) das de Gestão (planejar/executar)."}
        },
        {
            "pergunta": "Quem é o principal responsável pela Governança Corporativa?",
            "opcoes": {"A": "O suporte técnico", "B": "O Conselho de Administração (Board)", "C": "O estagiário de TI", "D": "O fornecedor de internet"},
            "resposta": "B",
            "motivos": {"B": "A Governança é responsabilidade da alta direção/conselho, definindo a direção e monitorando resultados."}
        },
        {
            "pergunta": "O que significa a sigla 'I&T' no contexto do COBIT?",
            "opcoes": {"A": "Internet e Telefonia", "B": "Informação e Tecnologia", "C": "Instalação e Testes", "D": "Inovação e Trabalho"},
            "resposta": "B",
            "motivos": {"B": "O COBIT foca na governança e gestão de Informação e Tecnologia (I&T) em toda a empresa."}
        },
        {
            "pergunta": "Qual domínio cuida da 'Entrega e Suporte' dos serviços?",
            "opcoes": {"A": "EDM", "B": "BAI", "C": "DSS", "D": "APO"},
            "resposta": "C",
            "motivos": {"C": "DSS (Deliver, Service and Support) foca na entrega, serviço e suporte operacional de TI."}
        },
        {
            "pergunta": "O COBIT é um framework desenvolvido por qual organização?",
            "opcoes": {"A": "NASA", "B": "FIFA", "C": "ISACA", "D": "Google"},
            "resposta": "C",
            "motivos": {"C": "O COBIT é desenvolvido pela ISACA para apoiar a governança e gestão de TI."}
        }
    ],
    "normal": [
        {
            "pergunta": "Qual é o único domínio do COBIT focado exclusivamente em GOVERNANÇA?",
            "opcoes": {"A": "EDM (Evaluate, Direct, Monitor)", "B": "APO (Align, Plan, Organize)", "C": "BAI (Build, Acquire, Implement)", "D": "MEA (Monitor, Evaluate, Assess)"},
            "resposta": "A",
            "motivos": {"A": "EDM (Avaliar, Dirigir, Monitorar) é o domínio de Governança. Os outros 4 são de Gestão."}
        },
        {
            "pergunta": "Qual domínio trata da aquisição e implementação de soluções (projetos)?",
            "opcoes": {"A": "EDM", "B": "APO", "C": "BAI", "D": "DSS"},
            "resposta": "C",
            "motivos": {"C": "BAI (Build, Acquire, Implement) gerencia a definição, aquisição e implementação de soluções de TI."}
        },
        {
            "pergunta": "O princípio 'Holistic Approach' (Abordagem Holística) significa que:",
            "opcoes": {"A": "Foca apenas no software", "B": "Considera processos, pessoas e tecnologia", "C": "Ignora a cultura da empresa", "D": "Foca apenas no lucro"},
            "resposta": "B",
            "motivos": {"B": "Uma abordagem holística considera todos os componentes (processos, estruturas, cultura, info) interconectados."}
        },
        {
            "pergunta": "O domínio MEA (Monitor, Evaluate, Assess) é responsável por:",
            "opcoes": {"A": "Escrever códigos", "B": "Avaliação de desempenho e conformidade", "C": "Contratar funcionários", "D": "Comprar servidores"},
            "resposta": "B",
            "motivos": {"B": "MEA foca no monitoramento, avaliação e análise de conformidade e performance."}
        },
        {
            "pergunta": "Na distinção do COBIT, qual é o papel da GESTÃO?",
            "opcoes": {"A": "Avaliar e Dirigir", "B": "Planejar, Construir, Executar e Monitorar", "C": "Apenas Monitorar", "D": "Ignorar a estratégia"},
            "resposta": "B",
            "motivos": {"B": "A Gestão planeja, constrói, executa e monitora atividades alinhadas à direção da Governança."}
        },
        {
            "pergunta": "Qual princípio garante que o sistema de governança atenda às necessidades específicas?",
            "opcoes": {"A": "End-to-End System", "B": "Tailored to Enterprise Needs", "C": "Dynamic System", "D": "Open and Flexible"},
            "resposta": "B",
            "motivos": {"B": "'Tailored to Enterprise Needs' significa adaptar o sistema às necessidades específicas da empresa."}
        }
    ],
    "dificil": [
        {
            "pergunta": "Para 'Gestão de Serviços de TI', o COBIT se integra melhor com:",
            "opcoes": {"A": "PMBOK", "B": "ITIL", "C": "ISO 27001", "D": "Scrum"},
            "resposta": "B",
            "motivos": {"B": "ITIL é o padrão de mercado para Gestão de Serviços e se integra ao domínio DSS do COBIT."}
        },
        {
            "pergunta": "Para 'Segurança da Informação', qual padrão complementa o COBIT?",
            "opcoes": {"A": "ISO 9001", "B": "ISO 27001", "C": "PMBOK", "D": "Six Sigma"},
            "resposta": "B",
            "motivos": {"B": "A ISO 27001 é o padrão global para Segurança da Informação citado na integração com COBIT."}
        },
        {
            "pergunta": "O PMBOK se integra ao COBIT principalmente para apoiar:",
            "opcoes": {"A": "Operação de Service Desk", "B": "Gestão de Projetos", "C": "Auditoria Contábil", "D": "Segurança Física"},
            "resposta": "B",
            "motivos": {"B": "PMBOK fornece as melhores práticas para Gestão de Projetos dentro da governança."}
        },
        {
            "pergunta": "O uso de Modelos de Maturidade no COBIT serve para:",
            "opcoes": {"A": "Aumentar o salário", "B": "Análise de 'gap' (estado atual vs. desejado)", "C": "Eliminar a gerência", "D": "Criar logotipos"},
            "resposta": "B",
            "motivos": {"B": "A maturidade permite medir o desempenho atual e identificar o 'gap' para atingir o nível desejado."}
        },
        {
            "pergunta": "O domínio APO (Align, Plan, Organize) lida com:",
            "opcoes": {"A": "Organização, estratégia e portfólio", "B": "Suporte ao usuário final", "C": "Monitoramento de compliance", "D": "Codificação de software"},
            "resposta": "A",
            "motivos": {"A": "APO foca no alinhamento, planejamento e organização da estratégia e portfólio de TI."}
        },
        {
            "pergunta": "Um Sistema de Governança Dinâmico (Dynamic Governance System) significa:",
            "opcoes": {"A": "Mudar de regras todo dia", "B": "Adaptar-se a mudanças na estratégia/tecnologia", "C": "Não ter regras fixas", "D": "Usar apenas tecnologia nuvem"},
            "resposta": "B",
            "motivos": {"B": "Ser dinâmico significa que o sistema de governança evolui conforme as mudanças de estratégia e tecnologia."}
        }
    ]
}

# ===========================================================
#        SISTEMA DE PARTÍCULAS: MONEY RAIN (FUNDO)
# ===========================================================
class MoneyParticle:
    """Partículas financeiras que flutuam no fundo"""
    def __init__(self, w, h, font):
        self.w, self.h = w, h
        self.font = font
        self.reset(first_time=True)

    def reset(self, first_time=False):
        self.char = "$"
        self.x = random.randint(20, self.w - 20)
        
        if first_time:
            self.y = random.randint(0, self.h)
        else:
            self.y = random.randint(self.h, self.h + 100)
            
        self.speed = random.uniform(0.5, 2.5)
        self.base_alpha = random.randint(50, 150)
        self.scale = random.uniform(0.5, 1.2)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-1.5, 1.5)
        
        self.color = random.choice([
            (255, 215, 0),   # Gold
            (0, 255, 0),     # Green
            (0, 255, 255),   # Cyan
            (180, 180, 180)  # Platinum
        ])

    def update(self, dt):
        self.y -= self.speed * dt
        self.rotation += self.rot_speed * dt
        
        if self.y < -50:
            self.reset()

    def draw(self, screen):
        surf = self.font.render(self.char, True, self.color)
        w = int(surf.get_width() * self.scale)
        h = int(surf.get_height() * self.scale)
        if w <= 0 or h <= 0: return
        surf = pygame.transform.scale(surf, (w, h))
        surf = pygame.transform.rotate(surf, self.rotation)
        surf.set_alpha(self.base_alpha)
        
        rect = surf.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(surf, rect)


# ===========================================================
#        SISTEMA DE PARTÍCULAS: CLICK EXPLOSION (NOVO)
# ===========================================================
class ExplosionParticle:
    """Partículas que explodem ao clicar no botão"""
    def __init__(self, x, y, font):
        self.x, self.y = x, y
        self.font = font
        self.char = "$"
        
        # Física de Explosão
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 9)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.life = 255
        self.decay = random.uniform(5, 12)
        self.size = random.uniform(0.4, 0.8)
        self.gravity = 0.2
        
        # Cores Dourado e Verde
        self.color = random.choice([(255, 215, 0), (50, 255, 50), (255, 255, 200)])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity # Cai um pouco
        self.life -= self.decay

    def draw(self, screen):
        if self.life <= 0: return
        
        surf = self.font.render(self.char, True, self.color)
        
        # Escala
        w = int(surf.get_width() * self.size)
        h = int(surf.get_height() * self.size)
        if w > 0 and h > 0:
            surf = pygame.transform.scale(surf, (w, h))
            surf.set_alpha(int(self.life))
            screen.blit(surf, (self.x, self.y))


# ===========================================================
#         FUNÇÕES DE DESENHO DE UI (CYBER-VAULT)
# ===========================================================
def draw_cyber_vault_container(surface, rect, title_idx, total):
    """Desenha a caixa da pergunta parecendo um cofre digital holográfico"""
    
    # 1. Fundo Glass (Vidro Escuro)
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    s.fill((10, 15, 30, 200)) # Azul/Preto muito escuro e transparente
    surface.blit(s, rect.topleft)
    
    # 2. Borda Principal (Dourado Neon Fino)
    pygame.draw.rect(surface, (180, 160, 50), rect, 1, border_radius=2)
    
    # 3. Detalhes Tech nos Cantos (Cantoneiras Grossas)
    corner_len = 20
    thick = 3
    color_tech = (255, 215, 0) # Gold
    
    # Cantos
    pygame.draw.line(surface, color_tech, rect.topleft, (rect.left + corner_len, rect.top), thick)
    pygame.draw.line(surface, color_tech, rect.topleft, (rect.left, rect.top + corner_len), thick)
    pygame.draw.line(surface, color_tech, rect.topright, (rect.right - corner_len, rect.top), thick)
    pygame.draw.line(surface, color_tech, rect.topright, (rect.right, rect.top + corner_len), thick)
    pygame.draw.line(surface, color_tech, rect.bottomleft, (rect.left + corner_len, rect.bottom), thick)
    pygame.draw.line(surface, color_tech, rect.bottomleft, (rect.left, rect.bottom - corner_len), thick)
    pygame.draw.line(surface, color_tech, rect.bottomright, (rect.right - corner_len, rect.bottom), thick)
    pygame.draw.line(surface, color_tech, rect.bottomright, (rect.right, rect.bottom - corner_len), thick)
    
    # 4. Header "PERGUNTA X/Y"
    header_h = 30
    header_rect = pygame.Rect(rect.left, rect.top - header_h, 160, header_h)
    pygame.draw.rect(surface, color_tech, header_rect, border_top_left_radius=5, border_top_right_radius=15)
    
    # Label
    font = load_font(18)
    lbl = font.render(f"PERGUNTA {title_idx}/{total}", True, (10, 10, 10))
    surface.blit(lbl, (rect.left + 10, rect.top - 25))

def draw_option_button(surface, rect, text, font, is_hover, feedback_color=None):
    """Desenha botão estilo barra de ouro digital ou vidro"""
    
    if feedback_color:
        # Feedback sólido (Verde ou Vermelho)
        bg_color = feedback_color
        border_color = (255, 255, 255)
        text_color = (255, 255, 255)
    elif is_hover:
        # Hover: Dourado translúcido
        bg_color = (255, 215, 0, 80) 
        border_color = (255, 255, 100)
        text_color = (255, 255, 255)
    else:
        # Normal: Vidro azulado escuro
        bg_color = (30, 30, 60, 180)
        border_color = (100, 100, 140)
        text_color = (200, 200, 220)

    # Draw Shadow
    shadow_rect = rect.move(4, 4)
    pygame.draw.rect(surface, (0, 0, 0, 150), shadow_rect, border_radius=10)

    # Draw Button Body
    surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(surf, bg_color, surf.get_rect(), border_radius=10)
    surface.blit(surf, rect.topleft)

    # Draw Border
    pygame.draw.rect(surface, border_color, rect, 2 if not is_hover else 3, border_radius=10)

    # Draw Tech Decors (Hexagono)
    hex_color = (255, 215, 0) if is_hover else (80, 80, 100)
    pygame.draw.circle(surface, hex_color, (rect.left + 25, rect.centery), 6)
    pygame.draw.circle(surface, border_color, (rect.left + 25, rect.centery), 10, 1)

    # Text Rendering
    txt_surf = font.render(text, True, text_color)
    
    # Ajuste de texto
    available_w = rect.width - 60
    if txt_surf.get_width() > available_w:
        scale = available_w / txt_surf.get_width()
        txt_surf = pygame.transform.smoothscale(txt_surf, (int(txt_surf.get_width() * scale), int(txt_surf.get_height() * scale)))
    
    text_rect = txt_surf.get_rect(midleft=(rect.left + 50, rect.centery))
    surface.blit(txt_surf, text_rect)

# ===========================================================
#               FUNÇÃO PRINCIPAL DO MINIGAME (ASYNC)
# ===========================================================
async def run_show_do_bilhao(screen): # <--- 2. ASYNC DEF
    pygame.display.set_caption("Show do Bilhão - Cyber Edition")
    clock = pygame.time.Clock()

    layout = {}
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    assets = os.path.join(base, "assets")
    bg_path = os.path.join(assets, "background", "background_show_do_bilhao.jpg") 
    icon_path = os.path.join(assets, "icons", "money.png")
    
    bg_original = None
    if os.path.exists(bg_path):
        bg_original = pygame.image.load(bg_path).convert()

    # Carrega o ícone original
    icon_original = None
    if os.path.exists(icon_path):
        icon_original = pygame.image.load(icon_path).convert_alpha()

    # === FUNÇÃO DE RESIZE ===
    def resize_assets(surface):
        w, h = surface.get_size()
        
        # Gera um background cyber
        if bg_original:
            layout['background'] = pygame.transform.scale(bg_original, (w, h))
            # Escurecer para destacar o neon
            dark = pygame.Surface((w, h))
            dark.fill((0, 0, 0))
            dark.set_alpha(100)
            layout['background'].blit(dark, (0,0))
        else:
            layout['background'] = pygame.Surface((w, h))
            for y in range(h):
                c = int(20 * (1 - y/h))
                pygame.draw.line(layout['background'], (c, c, c+10), (0, y), (w, y))

        # Configura ícone e Efeito Glow
        if icon_original:
            icon_size = int(h * 0.12)
            icon_surf = pygame.transform.smoothscale(icon_original, (icon_size, icon_size))
            layout['icon_money'] = icon_surf
            
            # CRIAÇÃO DO GLOW (MÁSCARA DOURADA)
            try:
                mask = pygame.mask.from_surface(icon_surf)
                glow_surf = mask.to_surface(setcolor=(255, 215, 0, 255), unsetcolor=(0, 0, 0, 0))
                layout['icon_glow'] = glow_surf
            except:
                layout['icon_glow'] = None
        else:
            layout['icon_money'] = None
            layout['icon_glow'] = None

        layout['font_titulo'] = load_font(int(h * 0.09))
        layout['font_pergunta'] = load_font(int(h * 0.045))
        layout['font_opcao'] = load_font(int(h * 0.035))
        layout['font_particle'] = load_font(int(h * 0.06))
        layout['font_ui'] = load_font(int(h * 0.03))

    resize_assets(screen)
    
    # Listas de Partículas
    bg_particles = [MoneyParticle(screen.get_width(), screen.get_height(), layout['font_particle']) for _ in range(35)]
    explosion_particles = [] # Lista para as explosões de clique

    # === CONFIGURAÇÃO DE DIFICULDADE ===
    diff_rules = dm.get_rules()
    questions_type = dm.get_question_set_type() 
    raw_questions = ALL_QUESTIONS.get(questions_type, ALL_QUESTIONS["normal"])
    
    # Prepara perguntas
    perguntas = []
    for q in raw_questions:
        opcoes_texto = list(q["opcoes"].values())
        key_correta = q["resposta"]
        texto_correto = q["opcoes"][key_correta]
        motivo_correto = q["motivos"][key_correta]
        random.shuffle(opcoes_texto)
        perguntas.append({
            "pergunta": q["pergunta"],
            "opcoes_embaralhadas": opcoes_texto,
            "texto_correto": texto_correto,
            "motivo_correto": motivo_correto
        })
    random.shuffle(perguntas)

    pontos_acerto = 10 + diff_rules["bonus_acerto"]
    pontos_erro = -diff_rules["perda_pontos"]
    
    pergunta_idx = 0
    feedback = None
    FEEDBACK_DURATION = 2500
    
    shake_amount = 0

    while True:
        dt = clock.tick(60) / 16.0
        w, h = screen.get_size()

        # Shake Decay
        if shake_amount > 0:
            shake_amount -= 0.5
            if shake_amount < 0: shake_amount = 0
        
        shake_x = random.randint(-int(shake_amount), int(shake_amount))
        shake_y = random.randint(-int(shake_amount), int(shake_amount))

        # 1. Background
        screen.blit(layout['background'], (0, 0))
        
        # 2. Partículas de Fundo
        for p in bg_particles:
            p.update(dt)
            p.draw(screen)

        if pergunta_idx >= len(perguntas):
            AudioManager.play_sfx_if_exists("roleta")
            # CHAMADA ASYNC
            await show_pause_screen(screen, clock, "Fim do Show!", f"Saldo Final: {ScoreManager.get_score()}", theme="Show do Bilhão")
            return 0

        pergunta_atual = perguntas[pergunta_idx]

        # === INTERFACE FLUTUANTE ===
        float_y = math.sin(pygame.time.get_ticks() * 0.003) * 5
        game_surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Cabeçalho
        title_txt = "SHOW DO BILHÃO"
        title_surf = layout['font_titulo'].render(title_txt, True, (255, 255, 255))
        
        # Efeito Neon
        neon_color = (255, 215, 0)
        current_ticks = pygame.time.get_ticks()
        glow_alpha = 150 + int(50 * math.sin(current_ticks * 0.01))
        
        glow_title = layout['font_titulo'].render(title_txt, True, neon_color)
        glow_title.set_alpha(glow_alpha)
        
        title_rect = title_surf.get_rect(center=(w // 2, int(h * 0.08)))
        
        game_surf.blit(glow_title, (title_rect.x - 2, title_rect.y - 2))
        game_surf.blit(glow_title, (title_rect.x + 2, title_rect.y + 2))
        game_surf.blit(title_surf, title_rect)

        # Ícones com Glow
        if layout['icon_money']:
            icon = layout['icon_money']
            icon_glow = layout.get('icon_glow')
            
            pos_left = (title_rect.left - icon.get_width() - 20, title_rect.centery - icon.get_height() // 2)
            pos_right = (title_rect.right + 20, title_rect.centery - icon.get_height() // 2)

            if icon_glow:
                icon_glow.set_alpha(glow_alpha)
                game_surf.blit(icon_glow, (pos_left[0]-2, pos_left[1]-2))
                game_surf.blit(icon_glow, (pos_left[0]+2, pos_left[1]+2))
            game_surf.blit(icon, pos_left)

            if icon_glow:
                game_surf.blit(icon_glow, (pos_right[0]-2, pos_right[1]-2))
                game_surf.blit(icon_glow, (pos_right[0]+2, pos_right[1]+2))
            game_surf.blit(icon, pos_right)

        # Score
        draw_score_display(game_surf, ScoreManager.get_score(), layout['font_ui'], position="topright")

        # Container da Pergunta
        c_width = w * 0.85
        c_height = h * 0.22
        c_x = (w - c_width) // 2
        c_y = (title_rect.bottom + 60) + float_y
        
        container_rect = pygame.Rect(c_x, c_y, c_width, c_height)
        
        draw_cyber_vault_container(game_surf, container_rect, pergunta_idx + 1, len(perguntas))
        
        padding = 30
        text_area = container_rect.inflate(-padding*2, -padding*1.5)
        text_area.y += 10
        draw_text_wrapped(game_surf, pergunta_atual["pergunta"], layout['font_pergunta'], (255, 255, 255), text_area)

        # Botões
        btn_start_y = container_rect.bottom + 30
        btn_h = min(80, int(h * 0.10))
        btn_spacing = 15
        
        mouse_pos = pygame.mouse.get_pos()
        buttons = []
        
        for i, texto_opcao in enumerate(pergunta_atual["opcoes_embaralhadas"]):
            btn_w = w * 0.7
            btn_x = (w - btn_w) // 2
            btn_float = math.sin(current_ticks * 0.003 + i) * 3
            btn_rect = pygame.Rect(btn_x, btn_start_y + i * (btn_h + btn_spacing) + btn_float, btn_w, btn_h)
            
            is_hover = btn_rect.collidepoint(mouse_pos) and feedback is None
            
            f_color = None
            if feedback:
                if texto_opcao == feedback["correct_text"]:
                    f_color = (0, 180, 0)
                elif texto_opcao == feedback["selected_text"] and not feedback["correto"]:
                    f_color = (180, 0, 0)

            draw_option_button(game_surf, btn_rect, texto_opcao, layout['font_opcao'], is_hover, f_color)
            buttons.append((btn_rect, texto_opcao))

        # Desenha Interface com Shake
        screen.blit(game_surf, (shake_x, shake_y))

        # === DESENHA EXPLOSÃO DE PARTÍCULAS ===
        # (Desenhamos aqui para ficar por cima dos botões)
        for ep in explosion_particles[:]:
            ep.update()
            ep.draw(screen)
            if ep.life <= 0:
                explosion_particles.remove(ep)

        # Overlay de Feedback
        if feedback:
            overlay_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay_surf.fill((0, 0, 0, 180))
            screen.blit(overlay_surf, (0,0))
            
            msg_w, msg_h = w * 0.6, h * 0.4
            msg_rect = pygame.Rect((w-msg_w)//2, (h-msg_h)//2, msg_w, msg_h)
            
            color_res = (50, 255, 50) if feedback["correto"] else (255, 50, 50)
            pygame.draw.rect(screen, (20, 20, 30), msg_rect, border_radius=20)
            pygame.draw.rect(screen, color_res, msg_rect, 3, border_radius=20)
            
            res_txt = "EXCELENTE!" if feedback["correto"] else "ACESSO NEGADO!"
            txt_surf = layout['font_titulo'].render(res_txt, True, color_res)
            screen.blit(txt_surf, txt_surf.get_rect(center=(w//2, msg_rect.top + 50)))
            
            reason_rect = msg_rect.inflate(-60, -100)
            reason_rect.top += 60
            
            motivo_full = ""
            if not feedback["correto"]:
                motivo_full += f"Resposta certa: {feedback['correct_text']}\n\n"
            motivo_full += feedback["correct_reason"]
            
            draw_text_wrapped(screen, motivo_full, layout['font_opcao'], (220, 220, 220), reason_rect)

            elapsed = pygame.time.get_ticks() - feedback["start"]
            if elapsed >= feedback["dur"]:
                pergunta_idx += 1
                feedback = None

        pygame.display.flip()
        
        # 3. LINHA MÁGICA: Devolve controle ao navegador
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
                    bg_particles = [MoneyParticle(screen.get_width(), screen.get_height(), layout['font_particle']) for _ in range(35)]
                elif event.key == pygame.K_ESCAPE:
                    return 0

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and feedback is None:
                mx, my = pygame.mouse.get_pos()
                for rect, texto_clicado in buttons:
                    if rect.collidepoint(mx, my):
                        
                        # --- TRIGGER DO EFEITO DE EXPLOSÃO ---
                        for _ in range(25): # Cria 25 partículas no ponto do clique
                            explosion_particles.append(ExplosionParticle(mx, my, layout['font_particle']))
                        # -------------------------------------

                        correta_str = pergunta_atual["texto_correto"]
                        acertou = (texto_clicado == correta_str)
                        
                        if acertou:
                            ScoreManager.add_points(pontos_acerto)
                            AudioManager.play_sfx_if_exists("correto")
                        else:
                            ScoreManager.add_points(pontos_erro)
                            AudioManager.play_sfx_if_exists("errado")
                            shake_amount = 20

                        feedback = {
                            "start": pygame.time.get_ticks(),
                            "dur": FEEDBACK_DURATION,
                            "correto": acertou,
                            "correct_text": correta_str,
                            "selected_text": texto_clicado,
                            "correct_reason": pergunta_atual["motivo_correto"],
                        }
                        break
    return 0