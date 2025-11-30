# ===========================================================
#                 MINIGAME MALETA CERTA (ASYNC/WEB)
# ===========================================================
# Arquivo: party_pascal/src/minigames/maleta_certa.py
#
# ✔ Visual: Estilo Cyber-Glass (Transparência + Neon)
# ✔ Correção: Título "PROBLEMA" em badge separado
# ✔ Animação: Flutuação suave
# ✔ Web: Suporte a Pybag (asyncio)
# ===========================================================

import pygame
import random
import sys
import os
import math
import asyncio  # <--- IMPORTANTE PARA PYBAG

from src.utils import show_pause_screen, draw_text_wrapped, draw_question_container, draw_score_display, load_font
from src.score_manager import ScoreManager
from src.audio_manager import AudioManager
import src.difficulty_manager as dm


# ===========================================================
#            BANCO DE DESAFIOS (6 POR NÍVEL)
# ===========================================================
ALL_CHALLENGES = {
    "facil": [
        {"problema": "A empresa sofre com decisões de TI desalinhadas aos objetivos de negócio.", "opcoes": ["Adotar COBIT 2019", "Trocar equipamentos", "Fazer backup"], "correta": "Adotar COBIT 2019"},
        {"problema": "Usuários continuam caindo em golpes de phishing.", "opcoes": ["Treinar Usuários", "Atualizar Servidor", "Comprar licenças"], "correta": "Treinar Usuários"},
        {"problema": "Há falhas frequentes na comunicação entre TI e negócios.", "opcoes": ["Criar Comitê de TI", "Aumentar orçamento", "Comprar ERP"], "correta": "Criar Comitê de TI"},
        {"problema": "Incidentes não são registrados formalmente.", "opcoes": ["Gestão de Incidentes", "Contratar analistas", "Aumentar data center"], "correta": "Gestão de Incidentes"},
        {"problema": "Auditorias mostram falhas recorrentes de compliance.", "opcoes": ["Reforçar Controles", "Reduzir políticas", "Migrar para nuvem"], "correta": "Reforçar Controles"},
        {"problema": "O time de TI está sobrecarregado com tarefas manuais.", "opcoes": ["Automatizar Processos", "Contratar estagiários", "Ignorar chamados"], "correta": "Automatizar Processos"}
    ],
    "normal": [
        {"problema": "A TI não consegue priorizar projetos estratégicos.", "opcoes": ["Gestão de Portfólio", "Cancelar projetos", "Focar no operacional"], "correta": "Gestão de Portfólio"},
        {"problema": "Riscos de segurança não são monitorados proativamente.", "opcoes": ["Gestão de Riscos", "Instalar antivírus grátis", "Esperar o ataque"], "correta": "Gestão de Riscos"},
        {"problema": "Não se sabe se o investimento em TI traz retorno.", "opcoes": ["Gestão de Valor", "Cortar custos", "Aumentar preços"], "correta": "Gestão de Valor"},
        {"problema": "Mudanças no sistema causam falhas constantes.", "opcoes": ["Gestão de Mudanças", "Proibir atualizações", "Testar em produção"], "correta": "Gestão de Mudanças"},
        {"problema": "Dados sensíveis estão sendo acessados indevidamente.", "opcoes": ["Gestão de Identidade", "Bloquear internet", "Confiar nos usuários"], "correta": "Gestão de Identidade"},
        {"problema": "A empresa não tem plano para desastres.", "opcoes": ["Plano de Continuidade", "Backup em fita", "Rezar"], "correta": "Plano de Continuidade"}
    ],
    "dificil": [
        {"problema": "Falta alinhamento entre Arquitetura de TI e Estratégia.", "opcoes": ["Arquitetura Corporativa", "Comprar servidores", "Trocar o CIO"], "correta": "Arquitetura Corporativa"},
        {"problema": "A TI não atende aos níveis de serviço acordados (SLA).", "opcoes": ["Gestão de Nível de Serviço", "Ignorar o contrato", "Culpar o usuário"], "correta": "Gestão de Nível de Serviço"},
        {"problema": "Custos de TI estão opacos e sem controle.", "opcoes": ["Gestão Financeira de TI", "Planilha Excel", "Pedir mais dinheiro"], "correta": "Gestão Financeira de TI"},
        {"problema": "Fornecedores não entregam o prometido.", "opcoes": ["Gestão de Fornecedores", "Trocar de fornecedor", "Aceitar o prejuízo"], "correta": "Gestão de Fornecedores"},
        {"problema": "A qualidade dos softwares entregues é baixa.", "opcoes": ["Gestão da Qualidade", "Testar menos", "Lançar rápido"], "correta": "Gestão da Qualidade"},
        {"problema": "Conhecimento crítico está retido em poucas pessoas.", "opcoes": ["Gestão do Conhecimento", "Aumentar salários", "Impedir demissões"], "correta": "Gestão do Conhecimento"}
    ]
}

# ===========================================================
#              SISTEMA DE PARTÍCULAS
# ===========================================================
class MalaParticle:
    def __init__(self, screen_w, screen_h, icon):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.icon = icon
        self.x = random.randint(0, screen_w)
        self.y = random.randint(-screen_h, 0)
        self.speed = random.uniform(0.7, 1.7)
        base_size = random.randint(20, 36)
        self.icon_scaled = pygame.transform.smoothscale(self.icon, (base_size, base_size))
        self.alpha = random.randint(80, 150)

    def update(self, dt):
        self.y += self.speed * dt
        if self.y > self.screen_h + 10:
            self.x = random.randint(0, self.screen_w)
            self.y = random.randint(-200, -40)

    def draw(self, screen):
        icon = self.icon_scaled.copy()
        icon.set_alpha(self.alpha)
        screen.blit(icon, (self.x, self.y))

# ===========================================================
#   FUNÇÃO DE DESENHO: Maleta Cyber-Glass
# ===========================================================
def draw_briefcase_button(surface, base_rect, text, font, is_hovered, anim_offset_y):
    """
    Desenha uma maleta com estilo transparente, bordas neon e alça tecnológica.
    """
    # 1. Configuração de Cores (RGBA para transparência)
    if is_hovered:
        # Hover: Mais claro e menos transparente
        body_color = (40, 60, 120, 210) 
        border_color = (150, 220, 255) # Ciano Brilhante
        handle_color = (150, 220, 255)
        hover_lift = -6 # Sobe mais no hover
        shadow_alpha = 100
    else:
        # Normal: Mais escuro e transparente
        body_color = (20, 30, 60, 160)
        border_color = (0, 180, 255) # Azul Neon
        handle_color = (80, 120, 200)
        hover_lift = 0
        shadow_alpha = 80

    # Retângulo principal animado
    current_y = base_rect.y + anim_offset_y + hover_lift
    
    # Surface temporária para suportar transparência complexa
    # Criamos um pouco maior para caber a alça e o brilho
    draw_surf = pygame.Surface((base_rect.width, base_rect.height + 40), pygame.SRCALPHA)
    
    # Coordenadas relativas dentro da surface
    draw_w = base_rect.width
    draw_h = base_rect.height
    body_y_rel = 30 # Deixa espaço para a alça no topo

    # --- ALÇA (HANDLE) ---
    handle_w = int(draw_w * 0.3)
    handle_h = 25
    handle_x = (draw_w - handle_w) // 2
    handle_y = body_y_rel - 15 # Encaixa no topo da maleta

    # Desenha a alça (Arco ou Retângulo arredondado)
    handle_rect = pygame.Rect(handle_x, handle_y, handle_w, handle_h)
    pygame.draw.rect(draw_surf, (body_color[0], body_color[1], body_color[2], 100), handle_rect, border_top_left_radius=10, border_top_right_radius=10)
    pygame.draw.rect(draw_surf, handle_color, handle_rect, 3, border_top_left_radius=10, border_top_right_radius=10)

    # --- CORPO DA MALETA ---
    body_rect = pygame.Rect(0, body_y_rel, draw_w, draw_h)
    
    # Preenchimento Transparente
    pygame.draw.rect(draw_surf, body_color, body_rect, border_radius=15)
    
    # Borda Neon
    pygame.draw.rect(draw_surf, border_color, body_rect, 2 if not is_hovered else 3, border_radius=15)

    # Detalhes Tech (Cantos)
    corner_len = 15
    # Canto Superior Esquerdo
    pygame.draw.line(draw_surf, (255, 255, 255), (5, body_y_rel + corner_len), (5, body_y_rel + 5), 2)
    pygame.draw.line(draw_surf, (255, 255, 255), (5, body_y_rel + 5), (5 + corner_len, body_y_rel + 5), 2)
    # Canto Inferior Direito
    pygame.draw.line(draw_surf, (255, 255, 255), (draw_w - 5, body_y_rel + draw_h - corner_len), (draw_w - 5, body_y_rel + draw_h - 5), 2)
    pygame.draw.line(draw_surf, (255, 255, 255), (draw_w - corner_len - 5, body_y_rel + draw_h - 5), (draw_w - 5, body_y_rel + draw_h - 5), 2)

    # Fechaduras (Locks) - Detalhe visual
    lock_y = body_y_rel + 5
    pygame.draw.rect(draw_surf, handle_color, (handle_x - 10, lock_y, 8, 12), border_radius=2)
    pygame.draw.rect(draw_surf, handle_color, (handle_x + handle_w + 2, lock_y, 8, 12), border_radius=2)

    # --- TEXTO ---
    text_area = body_rect.inflate(-20, -20)
    # Precisamos desenhar o texto na surface temporária
    draw_text_wrapped(draw_surf, text, font, (255, 255, 255), text_area)

    # --- DESENHAR NA TELA ---
    # Sombra
    shadow_rect = pygame.Rect(base_rect.x + 5, current_y + 8, base_rect.width, base_rect.height)
    pygame.draw.rect(surface, (0, 0, 0, shadow_alpha), shadow_rect, border_radius=15)

    # Blita a maleta final
    final_pos = (base_rect.x, current_y - 30)
    surface.blit(draw_surf, final_pos)

    # Retorna o rect de colisão
    return pygame.Rect(base_rect.x, current_y, base_rect.width, base_rect.height)


# ===========================================================
#             FUNÇÃO PRINCIPAL (AGORA ASYNC)
# ===========================================================
async def run_maleta_certa(screen):
    pygame.display.set_caption("💼 Qual é a Maleta Certa?")
    clock = pygame.time.Clock()

    # Variáveis de layout e assets
    layout = {}
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    assets_dir = os.path.join(base_dir, "assets")
    bg_path = os.path.join(assets_dir, "background", "background_maleta_certa.png")
    icon_path = os.path.join(assets_dir, "icons", "mala.png")

    bg_original = None
    if os.path.exists(bg_path):
        bg_original = pygame.image.load(bg_path).convert()
    
    mala_icon_original = None
    if os.path.exists(icon_path):
        mala_icon_original = pygame.image.load(icon_path).convert_alpha()

    # === FUNÇÃO DE RESIZE ===
    def resize_assets(surface):
        w, h = surface.get_size()
        
        if bg_original:
            layout['background'] = pygame.transform.scale(bg_original, (w, h))
        else:
            layout['background'] = pygame.Surface((w, h))
            layout['background'].fill((40, 0, 0))

        # Ícones
        if mala_icon_original:
            layout['mala_icon'] = mala_icon_original
            layout['mala_big'] = pygame.transform.smoothscale(mala_icon_original, (int(h*0.09), int(h*0.09)))
        else:
            layout['mala_icon'] = None
            layout['mala_big'] = None

        # Fontes
        layout['font_title'] = load_font(min(int(h * 0.085), 70))
        layout['font_text'] = load_font(min(int(h * 0.065), 44))
        layout['font_small'] = load_font(min(int(h * 0.048), 34))

    resize_assets(screen)

    # Partículas
    particles = []
    if layout['mala_icon']:
        particles = [MalaParticle(screen.get_width(), screen.get_height(), layout['mala_icon']) for _ in range(12)]

    # === LÓGICA DE JOGO ===
    diff_rules = dm.get_rules()
    q_type = dm.get_question_set_type()
    
    desafios = ALL_CHALLENGES.get(q_type, ALL_CHALLENGES["normal"])
    random.shuffle(desafios)
    
    pontos_acerto = 10 + diff_rules["bonus_acerto"]
    pontos_erro = -diff_rules["perda_pontos"]

    indice = 0
    efeitos = []
    anim_timer = 0
    last_correct_pos = -1

    # Loop principal
    while True:
        dt = clock.tick(60) / 16.0
        anim_timer += 1
        sw, sh = screen.get_size()
        mouse_pos = pygame.mouse.get_pos()

        screen.blit(layout['background'], (0, 0))
        
        # Overlay Global
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 20, 100))
        screen.blit(overlay, (0, 0))

        for p in particles:
            p.update(dt)
            p.draw(screen)

        # -----------------------------------------------------------
        # TÍTULO (Com flutuação)
        # -----------------------------------------------------------
        float_offset_title = int(math.sin(anim_timer * 0.04) * 4)
        title_text = "Qual é a Maleta Certa?"
        title = layout['font_title'].render(title_text, True, (255, 215, 0))
        shadow = layout['font_title'].render(title_text, True, (0, 0, 0))
        
        title_rect = title.get_rect(center=(sw // 2, int(sh * 0.10) + float_offset_title))
        
        screen.blit(shadow, (title_rect.x + 4, title_rect.y + 4))
        screen.blit(title, title_rect)

        if layout['mala_big']:
            icon_float = int(math.sin(anim_timer * 0.06) * 3)
            screen.blit(layout['mala_big'], (title_rect.left - layout['mala_big'].get_width() - 15, title_rect.y + icon_float))
            screen.blit(layout['mala_big'], (title_rect.right + 15, title_rect.y + icon_float))

        # -----------------------------------------------------------
        # DESAFIOS E UI
        # -----------------------------------------------------------
        if indice < len(desafios):
            desafio = desafios[indice]

            if 'shuffled_opcoes' not in desafio:
                opcoes = desafio["opcoes"][:]
                correta = desafio["correta"]
                attempts = 0
                while True:
                    random.shuffle(opcoes)
                    new_pos = opcoes.index(correta)
                    if new_pos != last_correct_pos or attempts > 5:
                        last_correct_pos = new_pos
                        break
                    attempts += 1
                desafio['shuffled_opcoes'] = opcoes

            opcoes_display = desafio['shuffled_opcoes']

            # --- CONTAINER DE PERGUNTA (CYBER-GLASS) ---
            float_offset_box = int(math.sin(anim_timer * 0.03 + 1) * 3) 
            
            container_h = int(sh * 0.22)
            base_container_rect = pygame.Rect(80, int(sh * 0.22), sw - 160, container_h)
            
            # Posição Y final do container (flutuante)
            final_y_container = base_container_rect.y + float_offset_box
            
            # Surface para o Container
            glass_surf = pygame.Surface((base_container_rect.width, base_container_rect.height), pygame.SRCALPHA)
            
            # Fundo Transparente
            pygame.draw.rect(glass_surf, (20, 30, 60, 180), glass_surf.get_rect(), border_radius=15)
            # Borda Neon
            pygame.draw.rect(glass_surf, (80, 220, 255), glass_surf.get_rect(), 2, border_radius=15)
            
            # Detalhes Tech (Cantos)
            pygame.draw.circle(glass_surf, (80, 220, 255), (15, 15), 4)
            pygame.draw.circle(glass_surf, (80, 220, 255), (base_container_rect.width-15, 15), 4)
            pygame.draw.circle(glass_surf, (80, 220, 255), (15, base_container_rect.height-15), 4)
            pygame.draw.circle(glass_surf, (80, 220, 255), (base_container_rect.width-15, base_container_rect.height-15), 4)

            # Desenha Container na Tela
            screen.blit(glass_surf, (base_container_rect.x, final_y_container))

            # === CORREÇÃO DO PROBLEMA (BADGE E PADDING) ===
            
            # 1. Desenha a Badge "PROBLEMA" (Aba no topo)
            badge_color = (80, 220, 255) # Ciano
            badge_text_color = (20, 30, 60) # Azul Escuro
            
            lbl_surf = layout['font_small'].render("PROBLEMA", True, badge_text_color)
            
            # Posição da Badge (colada na borda superior esquerda, um pouco para dentro e para fora)
            lbl_x = base_container_rect.x + 20
            lbl_y = final_y_container - 15 
            
            lbl_rect = lbl_surf.get_rect(topleft=(lbl_x, lbl_y))
            # Fundo da badge (com padding)
            badge_bg_rect = lbl_rect.inflate(30, 12)
            
            pygame.draw.rect(screen, badge_color, badge_bg_rect, border_radius=8)
            # Texto da badge centralizado
            screen.blit(lbl_surf, lbl_surf.get_rect(center=badge_bg_rect.center))

            # 2. Desenha Texto da Pergunta (Com margem superior para não bater na badge)
            text_rect = base_container_rect.copy()
            text_rect.y = final_y_container 
            
            # Padding: Desce o topo em 35px para dar espaço à badge "PROBLEMA"
            text_rect.top += 35 
            text_rect.height -= 35 
            
            # Padding lateral
            text_rect = text_rect.inflate(-40, -10)
            
            draw_text_wrapped(screen, desafio["problema"], layout['font_text'], (255, 255, 255), text_rect)

            # -----------------------------------------------------------
            # BOTÕES DAS MALETAS
            # -----------------------------------------------------------
            largura = int(sw * 0.27)
            altura = int(sh * 0.17)
            esp = int(sw * 0.05)
            total = largura * 3 + esp * 2
            start_x = (sw - total) // 2
            base_y = int(sh * 0.58) 

            maletas_desenhadas = []

            for i, opcao in enumerate(opcoes_display):
                rect_base = pygame.Rect(start_x + i * (largura + esp), base_y, largura, altura)
                is_hovered = rect_base.collidepoint(mouse_pos)
                anim_offset_mala = int(math.sin(anim_timer * 0.05 + i * 0.8) * 5)

                final_rect = draw_briefcase_button(
                    screen, 
                    rect_base, 
                    opcao, 
                    layout['font_small'], 
                    is_hovered, 
                    anim_offset_mala
                )
                
                maletas_desenhadas.append((final_rect, opcao))

            # Efeitos de feedback
            for e in efeitos[:]:
                e["tempo"] += 1
                alpha = int(255 * (1 - e["tempo"] / e["max_tempo"]))
                c = (0, 255, 0, alpha) if e["tipo"] == "acerto" else (255, 50, 50, alpha)
                glow = pygame.Surface((e["rect"].width, e["rect"].height), pygame.SRCALPHA)
                glow.fill(c)
                screen.blit(glow, (e["rect"].x, e["rect"].y)) 
                if e["tempo"] >= e["max_tempo"]:
                    efeitos.remove(e)

            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        # Nota: Em navegadores, fullscreen pode exigir interação do usuário ou não funcionar
                        pygame.display.toggle_fullscreen()
                        screen = pygame.display.get_surface()
                        resize_assets(screen)
                        if layout['mala_icon']:
                            particles = [MalaParticle(screen.get_width(), screen.get_height(), layout['mala_icon']) for _ in range(12)]
                    elif event.key == pygame.K_ESCAPE:
                        if pygame.display.is_fullscreen():
                            pygame.display.toggle_fullscreen()
                            screen = pygame.display.get_surface()
                            resize_assets(screen)
                        else:
                            return ScoreManager.get_score()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for final_rect, opcao in maletas_desenhadas:
                        if final_rect.collidepoint(event.pos):
                            if opcao == desafio["correta"]:
                                ScoreManager.add_points(pontos_acerto)
                                efeitos.append({"tipo": "acerto", "rect": final_rect, "tempo": 0, "max_tempo": 16})
                                AudioManager.play_sfx_if_exists("correto")
                            else:
                                ScoreManager.add_points(pontos_erro)
                                efeitos.append({"tipo": "erro", "rect": final_rect, "tempo": 0, "max_tempo": 16})
                                AudioManager.play_sfx_if_exists("errado")
                            
                            indice += 1
                            break

        else:
            AudioManager.play_sfx_if_exists("roleta")
            # ATENÇÃO: Se show_pause_screen tiver um loop interno,
            # ele TAMBÉM precisa de await asyncio.sleep(0) lá dentro,
            # ou deve ser refatorado para não ser blocante.
            # Como não tenho acesso ao src.utils, mantenho a chamada padrão.
            await show_pause_screen(
                screen, clock,
                "Desafio Completo!",
                f"Pontuação Total: {ScoreManager.get_score()}",
                theme="Maleta Certa"
            )
            return ScoreManager.get_score()

        draw_score_display(screen, ScoreManager.get_score(), layout['font_small'], "topright")
        pygame.display.flip()
        
        # PONTO CRÍTICO PARA O PYBAG:
        await asyncio.sleep(0)  # Cede o controle ao navegador

    return ScoreManager.get_score()