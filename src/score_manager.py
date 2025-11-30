#===================================================
#  SISTEMA DE PONTUAÇÃO DO JOGO
#===================================================

class ScoreManager:
    _score = 0
    _displayed_score = 0  # para animação suave

    @classmethod
    def reset(cls):
        cls._score = 0
        cls._displayed_score = 0

    @classmethod
    def add_points(cls, amount):
        cls._score += amount

    @classmethod
    def get_score(cls):
        return cls._score

    @classmethod
    def update_displayed_score(cls, speed=0.3):
        """Anima o valor exibido para aproximar do valor real."""
        if abs(cls._displayed_score - cls._score) < 0.5:
            cls._displayed_score = cls._score
        else:
            cls._displayed_score += (cls._score - cls._displayed_score) * speed
        return int(cls._displayed_score)