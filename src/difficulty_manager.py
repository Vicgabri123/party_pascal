#=============================================================
#        SISTEMA DE DIFICULDADE DO JOGO
#=============================================================

"""
#difficulty_manager.py
Gerencia a dificuldade global do jogo Party Pascal.
Carrega automaticamente do settings.json e fornece regras
padronizadas para todos os minigames.
"""

import json
import os


# -----------------------------
# Caminho seguro para settings.json
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")


# -----------------------------
# Carrega a dificuldade salva
# -----------------------------
def get_difficulty():
    """Retorna 'facil', 'normal' ou 'dificil' baseado no settings.json."""
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("difficulty", "normal").lower()
    except Exception:
        pass

    return "normal"


# -----------------------------
# Regras centrais por dificuldade
# -----------------------------
DIFFICULTY_RULES = {
    "facil": {
        "perda_pontos": 5,
        "tempo_pergunta": 12,
        "perseguicao_tempo": 4,
        "navio_qtd": 16,           # ATUALIZADO: 1 ameaças (muito denso, fácil de acertar)
        "pergunta_tipo": "facil",
        "bonus_acerto": 2,         # recompensa maior
        "multiplicador_final": 1,  # pontuação final comum
    },

    "normal": {
        "perda_pontos": 12,
        "tempo_pergunta": 8,
        "perseguicao_tempo": 2.5,
        "navio_qtd": 12,           # ATUALIZADO: 12 ameaças (equilibrado)
        "pergunta_tipo": "normal",
        "bonus_acerto": 0,
        "multiplicador_final": 1,
    },

    "dificil": {
        "perda_pontos": 25,
        "tempo_pergunta": 1,
        "perseguicao_tempo": 1,
        "navio_qtd": 6,            # Mantido baixo (difícil de encontrar no mar de água)
        "pergunta_tipo": "dificil",
        "bonus_acerto": -2,        # penalidade mesmo acertando
        "multiplicador_final": 1.3, # bônus final por jogar no hard
    }
}



# -----------------------------
# Acesso simplificado
# -----------------------------
def get_rules():
    """Retorna o bloco de regras completo conforme a dificuldade atual."""
    diff = get_difficulty()
    return DIFFICULTY_RULES.get(diff, DIFFICULTY_RULES["normal"])



# -----------------------------
# Funções utilitárias
# -----------------------------
def get_question_set_type():
    """Retorna o tipo de pergunta para carregar: facil / normal / dificil."""
    return get_rules()["pergunta_tipo"]


def get_penalty():
    """Quanto o jogador perde ao errar."""
    return get_rules()["perda_pontos"]


def get_bonus():
    """Bônus ou penalidade ao acertar."""
    return get_rules()["bonus_acerto"]


def get_time_limit():
    """Tempo para responder perguntas (para minigames como perseguição, quiz, etc)."""
    return get_rules()["tempo_pergunta"]


def get_perseguicao_time():
    """Retorna o tempo específico da fase Perseguição."""
    return get_rules()["perseguicao_tempo"]


def get_batalha_naval_threats():
    """Quantidade de ameaças no tabuleiro da Batalha Naval."""
    return get_rules()["navio_qtd"]


def get_final_multiplier():
    """Multiplicador da pontuação final baseado na dificuldade."""
    return get_rules()["multiplicador_final"]



# -----------------------------
# Debug opcional (desativado por padrão)
# -----------------------------
if __name__ == "__main__":
    print("\n=== DEBUG DO SISTEMA DE DIFICULDADE ===")
    print("Dificuldade atual:", get_difficulty())
    print("Regras carregadas:", get_rules())