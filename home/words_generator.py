import random
from django.apps import apps
from django.conf import settings
import os

_CACHED_WORDS = None


def _load_words():
    """Load words from the aliases file once and cache them."""
    global _CACHED_WORDS
    if _CACHED_WORDS is not None:
        return _CACHED_WORDS

    # Construct the absolute path to the file
    file_path = os.path.join(settings.BASE_DIR, 'home', 'alias_words_2025.txt')

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read the entire file content
            content = f.read()
            
            # Split by commas and clean up
            raw_words = [w.strip() for w in content.split(',') if w.strip()]
            
            # Remove duplicates while preserving order
            seen = set()
            unique_words = []
            for word in raw_words:
                if word not in seen:
                    seen.add(word)
                    unique_words.append(word)
            
            if unique_words:
                _CACHED_WORDS = unique_words
                return _CACHED_WORDS
                
    except FileNotFoundError as e:
        print(f"Words file not found: {e}")
    except Exception as e:
        print(f"Error loading words: {e}")

    return _CACHED_WORDS


def new_word(game_session=None):
    """Return a random Hebrew word for the game, avoiding duplicates if game_session is provided."""
    words = _load_words()
    if not words:
        return ''
    
    # If no game session provided, return random word (backward compatibility)
    if not game_session:
        return random.choice(words)
    
    # Get used words for this game session
    UsedWord = apps.get_model('home', 'UsedWord')
    used_words = set(UsedWord.objects.filter(game_session=game_session).values_list('word', flat=True))
    
    # Find available words (not used yet)
    available_words = [word for word in words if word not in used_words]
    
    # If all words have been used, reset the used words for this game session
    if not available_words:
        UsedWord.objects.filter(game_session=game_session).delete()
        available_words = words
    
    # Select a random word from available words
    selected_word = random.choice(available_words)
    
    # Record this word as used
    UsedWord.objects.create(game_session=game_session, word=selected_word)
    
    return selected_word


def reset_used_words(game_session):
    """Reset all used words for a specific game session."""
    UsedWord = apps.get_model('home', 'UsedWord')
    UsedWord.objects.filter(game_session=game_session).delete()


def clear_word_cache():
    """Clear the cached words to force reloading with new parsing logic."""
    global _CACHED_WORDS
    _CACHED_WORDS = None
