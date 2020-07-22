# MODIFICADO POR: Víctor García: victor.garciacarrera@estudiante.uam.es,
#                 Carlos Isasa: carlos.isasa@estudiante.uam.es
from django.contrib import admin
from datamodel.models import Game
from datamodel.models import Move
from datamodel.models import Counter

admin.site.register(Move)
admin.site.register(Game)
admin.site.register(Counter)
