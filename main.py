#--------------------------------------------------------------------
# INICIALIZAÇÃO DO JOGO - ADAPTADO PARA WEB (PYGBAG)
#--------------------------------------------------------------------
import asyncio  # <--- 1. IMPORT OBRIGATÓRIO PARA WEB
import pygame
import sys
import os

# Adiciona o diretório base ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core import main_menu
from src.performance import is_mobile_like

# 2. A FUNÇÃO PRINCIPAL AGORA É 'ASYNC'
async def main():
    # Inicializa o Pygame
    pygame.init()
    
    # Detecta o ambiente
    # Dica: No Pygbag (Web), o sistema muitas vezes é identificado como 'emscripten'
    mobile_mode = is_mobile_like()
    
    # Ajuste para Web: Se for Pygbag, forçamos um tamanho ou deixamos resizable
    if sys.platform == "emscripten":
        # Na web, geralmente deixamos a janela se ajustar ou definimos um fixo
        screen = pygame.display.set_mode((1280, 720)) 
        print("🌐 Modo Web (Pygbag) Detectado")
    elif mobile_mode:
        # --- MODO MOBILE NATIVO (APK) ---
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
        print(f"📱 Modo Mobile Detectado: Resolução {screen.get_size()}")
    else:
        # --- MODO PC ---
        default_size = (1024, 600)
        screen = pygame.display.set_mode(default_size, pygame.RESIZABLE)
        print(f"💻 Modo PC Detectado: Janela {default_size}")

    # ------------------------------------------------------------------
    # 3. CHAMADA DO MENU (O PONTO CRÍTICO)
    # Como o main_menu provavelmente tem um loop (while), ele também
    # precisa ser async ou você precisa garantir que o loop dele tenha
    # o await asyncio.sleep(0).
    # ------------------------------------------------------------------
    
    # Se você alterou o main_menu para ser 'async def main_menu...', use:
    await main_menu(screen)
    
    # Se o main_menu NÃO for async, o jogo vai rodar, mas pode travar
    # se não houver o asyncio.sleep(0) lá dentro.

if __name__ == "__main__":
    # 4. EXECUÇÃO COM ASYNCIO
    asyncio.run(main())