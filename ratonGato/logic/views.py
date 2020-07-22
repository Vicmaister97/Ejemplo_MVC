from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from datamodel import constants
from datamodel.models import Counter, Game, GameStatus, Move
from logic.forms import MoveForm, SignupForm, UserLoginForm
from operator import attrgetter
from django.http import HttpResponseNotFound
from django.core.exceptions import ValidationError


def anonymous_required(f):
    def wrapped(request):
        if request.user.is_authenticated:
            return HttpResponseForbidden(
                errorHTTP(request,
                          exception="Action restricted to anonymous users"))
        else:
            print('Good request')
            return f(request)
    return wrapped


def errorHTTP(request, exception=None):
    context_dict = {}
    context_dict[constants.ERROR_MESSAGE_ID] = exception
    return render(request, "mouse_cat/error.html", context_dict)


def index(request):
    return render(request, 'mouse_cat/index.html')


@anonymous_required
def login_service(request):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        user_form = UserLoginForm(data=request.POST)
        if user_form.is_valid():
            user = authenticate(username=user_form.cleaned_data['username'],
                                password=user_form.cleaned_data['password'])
            if user:
                request.session["counter_session"] = 0
                login(request, user)
                return redirect(reverse('index'))
        else:
            print(user_form.errors)
    else:
        user_form = UserLoginForm()

    return render(request, 'mouse_cat/login.html', {'user_form': user_form})


@login_required
def logout_service(request):
    request.session["counter_session"] = 0
    logout(request)
    return redirect(reverse('index'))


@anonymous_required
def signup_service(request):
    if request.method == 'POST':
        user_form = SignupForm(data=request.POST)

        if user_form.is_valid():
            user_form.save()
            return render(request, 'mouse_cat/signup.html')
    else:
        user_form = SignupForm()

    return render(request, 'mouse_cat/signup.html', {'user_form': user_form})


def counter_service(request):
    # get the session counter
    if "counter_session" in request.session:
        counter = request.session["counter_session"] + 1
    else:
        counter = 1

    # set the session counter
    request.session["counter_session"] = counter

    # set the global counter
    counter_global = Counter.objects.inc()

    return render(request, 'mouse_cat/counter.html',
                  {'counter_session': request.session["counter_session"],
                   'counter_global': counter_global})


@login_required
def create_game_service(request):
    game = Game(cat_user=request.user)
    game.full_clean()
    game.save()
    return render(request, 'mouse_cat/new_game.html', {'game': game})


@login_required
def join_game_service(request):
    gamelist = []
    gamelisttemp = Game.objects.all()
    for game in gamelisttemp:
        if (game.mouse_user is None) and (game.cat_user != request.user):
            gamelist.append(game)

    if not gamelist:
        return render(request, 'mouse_cat/join_game.html',
                      {'msg_error': "There is no available games"})

    readygame = max(gamelist, key=attrgetter('id'))
    readygame.mouse_user = request.user
    readygame.full_clean()
    readygame.save()
    return render(request, 'mouse_cat/join_game.html', {'game': readygame})


@login_required
def select_game_service(request, game_id=-1):
    as_mouse = []
    as_cat = []

    gamelist = Game.objects.all()
    for game in gamelist:
        if game.status == GameStatus.ACTIVE:
            if (game.mouse_user == request.user):
                as_mouse.append(game)
            elif (game.cat_user == request.user):
                as_cat.append(game)

    if game_id != -1:
        for game in gamelist:
            if game.id == game_id:
                if game.status == GameStatus.ACTIVE:
                    if (game.mouse_user == request.user):
                        tag = constants.GAME_SELECTED_SESSION_ID
                        request.session[tag] = game_id
                        return redirect(reverse('index'))
                    elif (game.cat_user == request.user):
                        tag = constants.GAME_SELECTED_SESSION_ID
                        request.session[tag] = game_id
                        return redirect(reverse('index'))	
                    else:
                        return HttpResponseNotFound("Not Found")
                else:
                    return HttpResponseNotFound("Not Found")
        return HttpResponseNotFound("Not Found")

    return render(request, 'mouse_cat/select_game.html',
                  {'as_cat': as_cat, 'as_mouse': as_mouse})


@login_required
def show_game_service(request):
    if constants.GAME_SELECTED_SESSION_ID not in request.session:
        print('Error')
        return HttpResponseNotFound("Not Found")
    else:
        game_id = request.session[constants.GAME_SELECTED_SESSION_ID]
        game = Game.objects.get(id=game_id)
        board = [0]*64
        cats = game.pos_gatos()

        for c in cats:
            board[c] = 1
        board[game.pos_raton()[0]] = -1
        moveform = MoveForm()
        return render(request, 'mouse_cat/game.html',
                      {'game': game, 'board': board,
                       'move_form': moveform})


@login_required
def move_service(request):
    if request.method == 'POST':
        if constants.GAME_SELECTED_SESSION_ID not in request.session:
            return HttpResponseNotFound("Not Found")
        else:
            moveform = MoveForm(data=request.POST)

            if moveform.is_valid():
                game_id = request.session[constants.GAME_SELECTED_SESSION_ID]
                game = Game.objects.get(id=game_id)
                try:
                    Move.objects.create(game=game, player=request.user,
                                        origin=moveform.cleaned_data['origin'],
                                        target=moveform.cleaned_data['target'])
                except ValidationError:
                    print('Error en el movimiento')
                finally:
                    return redirect(reverse('show_game'))

    return HttpResponseNotFound("Forbidden Get")
