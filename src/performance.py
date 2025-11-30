#=========================================================
#   SISTEMA DE PERFOMANCE PC/MOBILE DO JOGO
#=========================================================

"""
Módulo de detecção de dispositivo e otimizações automáticas
para performance mobile em Party Pascal.
"""

import pygame
import sys

# ---------------------------------------------------------
# DETECTAR SE É UM DISPOSITIVO MOBILE-LIKE
# ---------------------------------------------------------
def is_mobile_like():
    try:
        w, h = pygame.display.get_surface().get_size()
        if max(w, h) <= 1280:
            return True
    except:
        pass

    platform = sys.platform
    if platform.startswith("android") or platform.startswith("ios"):
        return True

    return False


# ---------------------------------------------------------
# PRESETS DE DESEMPENHO
# ---------------------------------------------------------
PRESETS = {
    "high": {
        "fps": 60,
        "particles": 64,
        "particle_spawn_ms": 30,
        "use_smoothscale": True,
        "use_rotozoom": True,
        "preload_sfx": True,
    },
    "medium": {
        "fps": 45,
        "particles": 36,
        "particle_spawn_ms": 60,
        "use_smoothscale": True,
        "use_rotozoom": False,
        "preload_sfx": False,
    },
    "low": {
        "fps": 30,
        "particles": 18,
        "particle_spawn_ms": 110,
        "use_smoothscale": False,
        "use_rotozoom": False,
        "preload_sfx": False,
    }
}

PRESET = None


# ---------------------------------------------------------
# ESCOLHE PRESET IDEAL
# ---------------------------------------------------------
def pick_preset():
    if is_mobile_like():
        return PRESETS["low"]

    try:
        w, h = pygame.display.get_surface().get_size()
        if max(w, h) >= 2000:
            return PRESETS["high"]
        elif max(w, h) >= 1400:
            return PRESETS["medium"]
        else:
            return PRESETS["medium"]
    except:
        return PRESETS["medium"]


def ensure_preset():
    global PRESET
    if PRESET is None:
        PRESET = pick_preset()
    return PRESET


# ---------------------------------------------------------
# ACESSORES
# ---------------------------------------------------------
def target_fps():
    return ensure_preset()["fps"]


def particle_settings():
    p = ensure_preset()
    return p["particles"], p["particle_spawn_ms"]


def supports_smoothscale():
    return ensure_preset()["use_smoothscale"]


def supports_rotozoom():
    return ensure_preset()["use_rotozoom"]


# ---------------------------------------------------------
# CACHE PARA SUPERFÍCIES ESCALADAS
# ---------------------------------------------------------
_scaled_cache = {}

def adapt_surface(surface, new_size):
    key = (id(surface), new_size)
    if key in _scaled_cache:
        return _scaled_cache[key]

    try:
        if supports_smoothscale():
            scaled = pygame.transform.smoothscale(surface, new_size)
        else:
            scaled = pygame.transform.scale(surface, new_size)
    except:
        scaled = pygame.transform.scale(surface, new_size)

    scaled = scaled.convert_alpha()
    _scaled_cache[key] = scaled
    return scaled


# Para testes
def force_preset(name):
    global PRESET
    if name in PRESETS:
        PRESET = PRESETS[name]