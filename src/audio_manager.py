#====================================================
#              SISTEMA DE AUDIO 
#====================================================

"""
AudioManager – Versão Mobile/PC 2025 (Ultra Otimizada)
-------------------------------------------------------
Melhorias:
- Busca inteligente: Procura músicas tanto na pasta 'musica' quanto 'efeitos'.
- Suporte a WAV loops curtos na tabela de música.
"""

import os
import json
import pygame
from typing import Optional


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
MUSIC_DIR = os.path.join(ASSETS_DIR, "sounds", "musica")
SFX_DIR = os.path.join(ASSETS_DIR, "sounds", "efeitos")
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")


class _AudioManager:
    def __init__(self, default_music_vol=0.5, default_sfx_vol=1.0):
        
        # ==========================================================
        # Mixer seguro para MOBILE/PC
        # ==========================================================
        if not pygame.mixer.get_init():
            try:
                # 44100Hz é o padrão seguro para evitar distorção em loops WAV
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except Exception:
                pass
        
        self.fade_speed = 650

        # ==========================================================
        # TABELA DE MÚSICAS
        # ==========================================================
        self.music_table = {
            # Agora apontando para os arquivos WAV
            "loop_start": "loop_start.ogg",  
            "musica_final": "musica_final.ogg",

            # minigames
            "musica_show_do_bilhao": "musica_show_do_bilhao.ogg",
            "musica_batalha_naval": "musica_batalha_naval.ogg",
            "musica_maleta_certa": "musica_maleta_certa.ogg",
            "musica_rodada_bonus": "musica_rodada_bonus.ogg",
            "musica_perseguicao": "musica_perseguicao.ogg",
            "musica_stop": "musica_stop.ogg",

            # cutscenes
            "cutscene_intro": "musica_cutscene_intro.ogg",
            "cutscene_final": "musica_cutscene_final.ogg",

            # menu
            "menu": "music_menu.ogg",
        }

        # Efeitos
        self.sfx_table = {
            "click": "clique.wav",
            "correto": "correto.wav",
            "errado": "errado.wav",
            "explosion": "explosion.wav",
            "roleta": "roleta.wav",
        }

        self.sfx_cache = {}

        # Volumes
        settings = self._load_settings()
        self.music_volume = settings.get("music_volume", default_music_vol)
        self.sfx_volume = settings.get("fx_volume", default_sfx_vol)

        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except:
            pass

        self.current_music_key = None


    # ==========================================================
    # INTERNOS
    # ==========================================================

    def _load_settings(self):
        try:
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data
        except:
            pass
        return {"music_volume": 0.5, "fx_volume": 1.0}

    def _music_path(self, key):
        """
        Retorna o caminho do arquivo de música.
        Modificado para procurar em 'efeitos' se não achar em 'musica'.
        """
        filename = self.music_table.get(key)
        if not filename:
            return None
        
        # 1. Tenta encontrar na pasta padrão de MÚSICA
        path_music = os.path.join(MUSIC_DIR, filename)
        if os.path.exists(path_music):
            return path_music

        # 2. Se não achar, tenta na pasta de EFEITOS (para loops wav curtos)
        path_sfx = os.path.join(SFX_DIR, filename)
        if os.path.exists(path_sfx):
            return path_sfx
        
        # Se não achar em lugar nenhum, retorna None (ou o caminho original para falhar log)
        return path_music

    def _sfx_path(self, key):
        f = self.sfx_table.get(key)
        if not f:
            return None
        return os.path.join(SFX_DIR, f)


    # ==========================================================
    # MÚSICA
    # ==========================================================

    def play_music_if_exists(self, key, loops=-1):
        """Toca música somente se existir."""
        path = self._music_path(key)
        if not path or not os.path.exists(path):
            print(f"AVISO: Música '{key}' não encontrada nos caminhos.")
            return False

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops)
            self.current_music_key = key
            return True
        except Exception as e:
            print(f"ERRO ao tocar música {key}: {e}")
            return False


    def fade_to_music_if_exists(self, key, fade_ms=None):
        """Crossfade otimizado."""
        path = self._music_path(key)
        if not path or not os.path.exists(path):
            return False

        fade_ms = fade_ms or self.fade_speed

        try:
            pygame.mixer.music.fadeout(fade_ms)
        except:
            pass

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1, fade_ms=fade_ms)
            self.current_music_key = key
            return True
        except:
            return False
    
    # Alias para compatibilidade
    def fade_to_music(self, key, fade_ms=None):
        return self.fade_to_music_if_exists(key, fade_ms)


    # ==========================================================
    # SFX
    # ==========================================================

    def _load_sfx(self, key):
        if key in self.sfx_cache:
            return self.sfx_cache[key]

        path = self._sfx_path(key)
        if not path or not os.path.exists(path):
            return None

        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(self.sfx_volume)
            self.sfx_cache[key] = snd
            return snd
        except:
            return None

    def play_sfx_if_exists(self, key):
        snd = self._load_sfx(key)
        if not snd:
            return False
        try:
            snd.play()
            return True
        except:
            return False


    # ==========================================================
    # VOLUMES
    # ==========================================================

    def set_music_volume(self, v):
        v = max(0, min(1, float(v)))
        self.music_volume = v
        try:
            pygame.mixer.music.set_volume(v)
        except:
            pass
        self._save_settings()

    def set_sfx_volume(self, v):
        v = max(0, min(1, float(v)))
        self.sfx_volume = v

        for snd in self.sfx_cache.values():
            try:
                snd.set_volume(v)
            except:
                pass

        self._save_settings()

    def _save_settings(self):
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump({"music_volume": self.music_volume,
                           "fx_volume": self.sfx_volume}, f, indent=2)
        except:
            pass


# Singleton
AudioManager = _AudioManager()
audio_manager = AudioManager # Alias minúsculo para compatibilidade