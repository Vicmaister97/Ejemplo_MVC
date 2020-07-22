# MODIFICADO POR: Víctor García: victor.garciacarrera@estudiante.uam.es,
#                 Carlos Isasa: carlos.isasa@estudiante.uam.es

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class GameStatus(models.Model):
    CREATED = 0
    ACTIVE = 1
    FINISHED = 2


class Game(models.Model):

    # ID DE PARTIDA UNICO auto-incrementable
    # ID = models.AutoField(primary_key=True)

    # Usuario Jugador1(Gatos) NO PUEDE SER NULL
    # TIENE QUE HABER UN JUGADOR GATO
    cat_user = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name="games_as_cat", null=False)
    # Usuario Jugador2(Raton)
    # Acepta que se cree sin jugador raton con blank=True
    mouse_user = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name="games_as_mouse",
                                   null=True, blank=True)

    cat1 = models.IntegerField(default=0, null=False)    # Posición Gato1
    cat2 = models.IntegerField(default=2, null=False)    # Posición Gato2
    cat3 = models.IntegerField(default=4, null=False)    # Posición Gato3
    cat4 = models.IntegerField(default=6, null=False)    # Posición Gato4
    mouse = models.IntegerField(default=59, null=False)  # Posicion Raton

    cat_turn = models.BooleanField(default=True, null=False)
    # True si turnoGato, False si turnoRaton

    status = models.IntegerField(default=GameStatus.CREATED, null=False)
    MIN_CELL = 0
    MAX_CELL = 63

    valid_pos = []          # Lista con las casillas validas de juego
    BOARD = 8               # numero de casillas por fila y columna
    for i in range(BOARD):          # recorremos por filas
        for j in range(BOARD):      # recorremos por columnas
            casilla = BOARD*i + j   # codificacion de la casilla
            if (i % 2) == 1:        # filas impares
                if (j % 2) == 1:
                    valid_pos.append(casilla)

            else:   # fila par
                if (j % 2 == 0):
                    valid_pos.append(casilla)

    def pos_gatos(self):
        return [int(self.cat1), int(self.cat2), int(self.cat3), int(self.cat4)]

    def pos_raton(self):
        return [int(self.mouse)]

    def save(self, *args, **kwargs):

        # Una vez tenemos la lista con las posiciones validas,
        # comprobamos antes de salvar la partida que las casillas
        # donde se encuentran los personajes son validas
        if self.cat_user and ((self.cat1 in self.valid_pos)
                              and (self.cat2 in self.valid_pos)
                              and (self.cat3 in self.valid_pos)
                              and (self.cat4 in self.valid_pos)
                              and (self.mouse in self.valid_pos)):
            # Si acabamos de crear la partida y ya hay un jugador raton
            if self.mouse_user and self.status == GameStatus.CREATED:
                self.status = GameStatus.ACTIVE

            # Si el raton no puede moverse finaliza la partida
            derecha_arriba = self.mouse - 7
            izquierda_arriba = self.mouse - 9
            derecha_abajo = self.mouse + 9
            izquierda_abajo = self.mouse + 7

            movs_raton = [derecha_arriba, izquierda_arriba,
                          derecha_abajo, izquierda_abajo]

            finish = False
            for pos in movs_raton:
                if ((pos in self.pos_gatos()) or (pos < self.MIN_CELL)
                        or (pos > self.MAX_CELL)):
                    finish = True
                else:
                    finish = False
                    break

            if (finish is True):
                self.status = GameStatus.FINISHED

            # Salvamos la partida
            super().save(*args, **kwargs)
        else:
            raise ValidationError("Invalid cell for a cat or the mouse")

    def full_clean(self):
        # Comprobamos que haya jugador gato y las posiciones sean correctas
        try:
            if self.cat_user and ((self.cat1 in self.valid_pos)
                                  and (self.cat2 in self.valid_pos)
                                  and (self.cat3 in self.valid_pos)
                                  and (self.cat4 in self.valid_pos)
                                  and (self.mouse in self.valid_pos)):
                super().full_clean()
            else:
                raise ValidationError("Invalid cell for a cat or the mouse")

        except AttributeError:
            raise ValidationError("Invalid cell for a cat or the mouse")

    def __str__(self):
        # Bloque con el ESTADO de la partida
        if (self.status == 0):
            block0 = "Created"
        if (self.status == 1):
            block0 = "Active"
        if (self.status == 2):
            block0 = "Finished"

        # Bloque de texto con (id, Estado) del juego
        block1 = "(" + str(self.id) + ", " + block0 + ")" + "\t"
        # Si tenemos al Jugador1 Gato
        if (self.cat_user):
            # Bloque de texto con la info del gato
            block2 = "Cat ["
            if (self.cat_turn is True):
                # Marcamos con una X si es el turno de Jugador1 Gato
                block2 += "X"
            else:
                block2 += " "

            # Mostramos las posiciones de los 4 gatos
            block2 += "] cat_user_test(" + str(self.cat1)
            block2 += ", " + str(self.cat2)
            block2 += ", " + str(self.cat3)
            block2 += ", " + str(self.cat4) + ")"

            # Si tenemos al Jugador2 Raton
            if (self.mouse_user):
                # Bloque de texto con la info del gato
                block3 = " --- Mouse ["
                if (self.cat_turn is False):
                    # Marcamos con una X si es el turno de Jugador2 Raton
                    block3 += "X"
                else:
                    block3 += " "
                block3 += "] mouse_user_test(" + str(self.mouse) + ")"

                return block1+block2+block3
            else:
                return block1+block2
        else:
            return block1


class Move(models.Model):
    origin = models.IntegerField(null=False)    # Casilla Origen de movimiento
    target = models.IntegerField(null=False)    # Casilla Destino de movimiento
    game = models.ForeignKey(Game, related_name="moves",
                             on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(null=False, default=timezone.now)

    def save(self, *args, **kwargs):
        derecha_arriba = self.origin - 7
        izquierda_arriba = self.origin - 9
        derecha_abajo = self.origin + 9
        izquierda_abajo = self.origin + 7

        mov_gato = [derecha_abajo, izquierda_abajo]
        mov_raton = [derecha_arriba, izquierda_arriba,
                     derecha_abajo, izquierda_abajo]

        # Si el juego no permite movimientos
        if ((self.game.status == GameStatus.CREATED)
                or (self.game.status == GameStatus.FINISHED)):
            raise ValidationError("Move not allowed")

        # print("ESTOS SON LOS GATOS" + str(self.game.pos_gatos()))
        # Comprobar si el movimieto va a una posicion OCUPADA
        if ((self.target in self.game.pos_gatos())
                or (self.target in self.game.pos_raton())):
            raise ValidationError("Move not allowed")

        # No puedes moverte mas alla de la primera y ultima fila
        if ((self.target <= self.game.MAX_CELL) and
           (self.target >= self.game.MIN_CELL)):
            if ((self.player == self.game.cat_user) and self.game.cat_turn):
                # Gatos no pueden moverse atras
                if ((self.origin % 8) == 0):
                    # Columna 0 no puede moverse izquierda
                    if (self.target == derecha_abajo):
                        if self.actualizarMove() is True:
                            # Si puede actualizar el movimiento del juego
                            super().save(*args, **kwargs)
                            # Añadimos el movimiento
                        else:
                            raise ValidationError("Move not allowed")
                    else:
                        raise ValidationError("Move not allowed")

                elif ((self.origin % 8) == 7):
                    # Columna 7 no puede moverse derecha
                    if (self.target == izquierda_abajo):
                        if self.actualizarMove() is True:
                            # Si puede actualizar el movimiento deljuego
                            super().save(*args, **kwargs)
                            # Añadimos el movimiento
                        else:
                            raise ValidationError("Move not allowed")
                    else:
                        raise ValidationError("Move not allowed")
                else:
                    if ((self.target in mov_gato)):
                        if self.actualizarMove() is True:
                            # Si puede actualizar el movimiento deljuego
                            super().save(*args, **kwargs)
                            # Añadimos el movimiento
                        else:
                            raise ValidationError("Move not allowed")
                    else:
                        raise ValidationError("Move not allowed")

            elif ((self.player == self.game.mouse_user)
                  and not(self.game.cat_turn)):
                if (self.origin % 8 == 0):
                    # Columna 0 no puede moverse izquierda
                    if ((self.target == derecha_abajo)
                            or (self.target == derecha_arriba)):
                        if self.actualizarMove() is True:
                            # Si puede actualizar el movimiento deljuego
                            super().save(*args, **kwargs)
                            # Añadimos el movimiento
                        else:
                            raise ValidationError("Move not allowed")
                    else:
                        raise ValidationError("Move not allowed")

                elif (self.origin % 8 == 7):
                    # Columna 7 no puede moverse derecha
                    if ((self.target == izquierda_abajo)
                            or (self.target == izquierda_arriba)):
                        if self.actualizarMove() is True:
                            # Si puede actualizar el movimiento deljuego
                            super().save(*args, **kwargs)
                            # Añadimos el movimiento
                        else:
                            raise ValidationError("Move not allowed")
                    else:
                        raise ValidationError("Move not allowed")

                else:
                    if ((self.target in mov_raton)):
                        if self.actualizarMove() is True:
                            # Si puede actualizar el movimiento deljuego
                            super().save(*args, **kwargs)
                            # Añadimos el movimiento
                        else:
                            raise ValidationError("Move not allowed")
                    else:
                        raise ValidationError("Move not allowed")
            else:
                raise ValidationError("Move not allowed")

        else:
            raise ValidationError("Move not allowed")

    def actualizarMove(self):
        # Comprobar si el movimieto parte de una posición actual del juego
        if ((self.origin not in self.game.pos_gatos())
                and (self.origin not in self.game.pos_raton())):
            return False

        # Movimiento de un gato
        if ((self.player == self.game.cat_user) and self.game.cat_turn):
            if self.origin not in self.game.pos_gatos():
                return False
            else:
                # Actualizamos el turno
                self.game.cat_turn = False

                if(self.origin == self.game.pos_gatos()[0]):
                    # Movimiento gato1
                    self.game.cat1 = self.target
                elif(self.origin == self.game.pos_gatos()[1]):
                    # Movimiento gato2
                    self.game.cat2 = self.target
                elif(self.origin == self.game.pos_gatos()[2]):
                    # Movimiento gato3
                    self.game.cat3 = self.target
                else:  # Movimiento gato4
                    self.game.cat4 = self.target

        # Movimiento de un raton
        if ((self.player == self.game.mouse_user)
                and (not self.game.cat_turn)):
            if self.origin not in self.game.pos_raton():
                return False
            else:
                # Actualizamos el turno
                self.game.cat_turn = True
                # Actualizamos la pos del raton
                self.game.mouse = self.target

        self.game.save()
        return True


# Implementa el controlador del Counter
class CounterManager(models.Manager):  # models.Manager

    @classmethod
    def inc(self):
        # Obtenemos todos los objetos que existen de la clase
        objects = Counter.objects.all()

        # No existe el contador
        if len(objects) == 0:
            counter = self.singleton()
        else:
            counter = objects[0]

        # Incrementamos el valor del contador
        counter.value += 1
        # Actualizamos el valor
        super(Counter, counter).save()
        return counter.value

    # Crea un unico contador siguiendo el diseño Singleton
    @classmethod
    def singleton(self):
        cont = Counter(value=0)
        # Actualizamos el valor
        super(Counter, cont).save()
        return cont

    @classmethod
    def get_current_value(self):
        # Obtenemos todos los objetos que existen de la clase
        objects = Counter.objects.all()

        # No existe el contador, valor inicial de 0
        if len(objects) == 0:
            return 0
        return objects[0].value


# Clase que implementa el registro de las peticiones recibidas
class Counter(models.Model):
    # Contador de peticiones inicializado a 0
    value = models.IntegerField(default=0, null=False)

    # Sobreescribimos el Manager de Counter
    objects = CounterManager()

    # Anulamos el save
    def save(self, *args, **kwargs):
        raise ValidationError("Insert not allowed")
