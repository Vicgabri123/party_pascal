"""
Teste rápido para verificar se todos os módulos podem ser importados.
Execute com:  python test_imports.py
"""

try:
    import pygame
    import sys
    from src.core import iniciar_jogo
    from src.game_loop import start_game_loop
    from src.menu import main_menu

    print("✅ Todos os módulos foram importados com sucesso!")
except ModuleNotFoundError as e:
    print("❌ ERRO de importação detectado:")
    print(e)
except Exception as e:
    print("⚠️ Outro erro ocorreu:")
    print(e)