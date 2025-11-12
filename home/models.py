from django.db import models
from django.utils.crypto import get_random_string
import random

class GameSession(models.Model):

    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    current_player_order = models.IntegerField(null=True, blank=True)  # Made nullable
    code = models.CharField(max_length=6, unique=True, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True)


    @classmethod
    def new_game(cls, player_names):
        game_session = GameSession.objects.create(
            session_id=get_random_string(32),
            current_player_order=0, # Start with no current player
            code=get_random_string(6, allowed_chars='0123456789')
        )
        order = 0
        for name in player_names:
            Player.objects.create(
                player_id=get_random_string(16),
                name=name,
                game_session=game_session,
                order=order,
            )
            order += 1
        return game_session

    def current_player(self):

        player = Player.objects.get(game_session=self, order=self.current_player_order)
        return player
    
    def next_turn(self):
        players = self.players.order_by('order')
        if not players.exists():
            return None

        # If no current player, start with first player
        if self.current_player_order is None:
            self.current_player_order = 0
            self.save()
            return players[0]

        # Move to next player
        self.current_player_order = (self.current_player_order + 1) % players.count()
        self.save()
        return players[self.current_player_order]

    def winning_player(self):
        return self.players.filter(score__gte=36).first()
    
    def reset_used_words(self):
        """Reset all used words for this game session."""
        self.used_words.all().delete()
    
    def get_available_words_count(self):
        """Get the number of words that haven't been used yet in this game session."""
        from .words_generator import _load_words
        all_words = _load_words()
        used_words_count = self.used_words.count()
        return len(all_words) - used_words_count if all_words else 0

    def __str__(self):
        return f"{self.session_id} - {self.created_at}"
    

class Player(models.Model):
    player_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    score = models.IntegerField(default=0)
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='players')
    order = models.IntegerField(default=0)  # New field for player order

    @classmethod
    def new_player(cls, player_name, game_session):
        order = game_session.players.count()
        return Player.objects.create(
            player_id=get_random_string(16),
            name=player_name,
            game_session=game_session,
            order=order,
        )

    def handle_answer(self, result):
        if result == 'correct':
            self.score += 1
        elif result == 'incorrect':
            self.score = max(self.score - 1, 0)
        self.save()
        return self.score

    def __str__(self):
        return self.name


class UsedWord(models.Model):
    """Track words that have been used in each game session to avoid duplicates."""
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='used_words')
    word = models.CharField(max_length=100)
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['game_session', 'word']
        
    def __str__(self):
        return f"{self.word} in {self.game_session.session_id}"