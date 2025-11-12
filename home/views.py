from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import GameSession, Player
import json
from .words_generator import new_word
from django.utils import timezone

@csrf_exempt
def hello(request):
    return render(request, 'index.html')


@csrf_exempt
def new_game(request):
    if request.method == 'GET':
        return render(request, "new_game.html")

    payload = json.loads(request.body.decode() or "{}")
    player_names = payload.get('players', [])
    if not player_names:
        return JsonResponse({'error': 'No players provided'}, status=400)
    print(player_names)
    from .models import GameSession
    game_session = GameSession.new_game(player_names)
    request.session['game_session_id'] = game_session.session_id
    request.session['player_id'] = game_session.players.first().player_id
    request.session.modified = True


    return JsonResponse({
        'redirect_url': f'/game/{game_session.session_id}'
    })


@csrf_exempt
def game_session(request, session_id):
    try:
        game_session = GameSession.objects.get(session_id=session_id)
    except GameSession.DoesNotExist:
        return HttpResponse("Game session not found", status=404)

    players = game_session.players.all()
    player_id = request.session.get('player_id')
    current_player = game_session.current_player()
    winning_player = game_session.winning_player()
    return render(request, "game_session.html", {
        'game_session': game_session,
        'players': players,
        'current_player': current_player,
        'my_turn': player_id == current_player.player_id,
        'winning_player': winning_player
    })


@csrf_exempt
def game_next_turn(request, session_id):
    try:
        game_session = GameSession.objects.get(session_id=session_id)
        next_player = game_session.next_turn()
        return redirect(f'/game/{session_id}/')
    except GameSession.DoesNotExist:
        return HttpResponse("Game session not found", status=404)

@csrf_exempt
def start_player_turn(request, session_id):
    try:
        game_session = GameSession.objects.get(session_id=session_id)
        current_player = game_session.current_player()
        player_id = request.session.get('player_id')
        if player_id != current_player.player_id:
            return HttpResponse("You are not the current player", status=403)
        return redirect(f'/game/{session_id}/player/{current_player.player_id}')
    except GameSession.DoesNotExist:
        return HttpResponse("Game session not found", status=404)
@csrf_exempt
def player_turn(request, session_id, player_id):
    try:
        game_session = GameSession.objects.get(session_id=session_id)
        player = Player.objects.get(player_id=player_id, game_session=game_session)
    except (GameSession.DoesNotExist, Player.DoesNotExist):
        return HttpResponse("Game session or player not found", status=404)

    if request.method == 'GET':
        return render(request, "player_turn.html", {
            'game_session': game_session,
            'player': player,
            'word': new_word(game_session),
        })
    
@csrf_exempt
def submit_result(request, session_id, player_id):
    try:
        game_session = GameSession.objects.get(session_id=session_id)
        player = Player.objects.get(player_id=player_id, game_session=game_session)
    except (GameSession.DoesNotExist, Player.DoesNotExist):
        return HttpResponse("Game session or player not found", status=404)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    payload = json.loads(request.body.decode() or "{}")
    result = payload.get('result')
    if result not in ['correct', 'incorrect']:
        return JsonResponse({'error': 'Invalid result'}, status=400)

    new_score = player.handle_answer(result)
    return JsonResponse({'new_score': new_score, 'word': new_word(game_session), 'won': new_score >= 36})


@csrf_exempt
def new_player(request):
    # Try to get code from JSON body first, then fallback to POST data
    payload = json.loads(request.body.decode() or "{}")
    print(payload)
    code = payload.get('code')
    try:
        game_session = GameSession.objects.get(code=code)
    except GameSession.DoesNotExist:
        return HttpResponse("Game session not found", status=404)

    player_name = payload.get('player_name')
    if not player_name:
        return JsonResponse({'error': 'No player name provided'}, status=400)

    new_player = Player.new_player(player_name, game_session)
    request.session['player_id'] = new_player.player_id
    request.session.modified = True
    game_session.modified_at = timezone.now()
    game_session.save()
    return redirect(f'/game/{game_session.session_id}/')



def game_status(request, session_id):
    try:
        game_session = GameSession.objects.get(session_id=session_id)
    except GameSession.DoesNotExist:
        return HttpResponse("Game session not found", status=404)
    return JsonResponse({'game_session':  {
        'session_id': game_session.session_id,
        'modified_at': game_session.modified_at,
    }})