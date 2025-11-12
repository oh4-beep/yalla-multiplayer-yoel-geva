from django.test import TestCase
from .models import GameSession, Player

class GameSessionTestCase(TestCase):
    def setUp(self):
        # Create a test game session with players
        self.player_names = ['Alice', 'Bob', 'Charlie']
        self.game_session = GameSession.new_game(self.player_names)

    def test_game_session_creation(self):
        """Test that game session is created with correct players"""
        self.assertIsNotNone(self.game_session.session_id)
        self.assertEqual(self.game_session.current_player_order, None)
        
        # Check players were created
        players = self.game_session.players.all().order_by('order')
        self.assertEqual(players.count(), len(self.player_names))
        
        # Verify player names and order
        for i, player in enumerate(players):
            self.assertEqual(player.name, self.player_names[i])
            self.assertEqual(player.order, i)
            self.assertEqual(player.score, 0)

    def test_next_turn(self):
        """Test next_turn rotation logic"""
        # Get initial player order
        initial_player = self.game_session.next_turn()
        self.assertEqual(initial_player.order, 0)
        next_player = self.game_session.next_turn()
        self.assertEqual(next_player.order, 1)
        

    def test_empty_game_session(self):
        """Test next_turn behavior with no players"""
        empty_session = GameSession.objects.create(session_id='test123')
        self.assertIsNone(empty_session.next_turn())

class PlayerTestCase(TestCase):
    def setUp(self):
        self.game_session = GameSession.objects.create(session_id='test123')
        self.player = Player.objects.create(
            player_id='player123',
            name='Test Player',
            game_session=self.game_session,
            order=0
        )

    def test_player_creation(self):
        """Test player model creation and defaults"""
        self.assertEqual(self.player.name, 'Test Player')
        self.assertEqual(self.player.score, 0)
        self.assertEqual(self.player.order, 0)
        self.assertEqual(str(self.player), 'Test Player')

    def test_player_score_update(self):
        """Test updating player score"""
        self.player.score = 42
        self.player.save()
        
        # Refresh from db and verify
        updated_player = Player.objects.get(pk=self.player.pk)
        self.assertEqual(updated_player.score, 42)
