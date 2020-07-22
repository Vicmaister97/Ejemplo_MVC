import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'ratonGato.settings')
import django
django.setup()
from django.contrib.auth.models import User
from datamodel.models import Game, Move
from operator import attrgetter


def populate():
    try:
        user1 = User.objects.get(id=10)
    except User.DoesNotExist:
        user1 = User.objects.create_user(id=10, username="test1")

    try:
        user2 = User.objects.get(id=11)
    except User.DoesNotExist:
        user2 = User.objects.create_user(id=11, username="test2")

    game = Game(cat_user=user1)
    game.full_clean()
    game.save()

    gamelist = []
    gamelisttemp = Game.objects.all()
    for game in gamelisttemp:
        if (game.mouse_user is None):
            gamelist.append(game)
    print(gamelist)

    playedgame = min(gamelist, key=attrgetter('id'))
    playedgame.mouse_user = user2
    game.full_clean()
    game.save()
    print(playedgame)

    Move.objects.create(game=playedgame, player=user1, origin=2, target=11)
    print(playedgame)

    Move.objects.create(game=playedgame, player=user2,
                        origin=59, target=52)
    print(playedgame)


if __name__ == '__main__':
    print('Starting ratonGato population script...')
    populate()
