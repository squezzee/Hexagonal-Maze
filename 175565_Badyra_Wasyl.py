import numpy as np
from random import *
from math import *
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Co się udało zrobić:
# generowanie labiryntu z hexagonalnymi komórkami

# Nie udało się zaimplementować algorytmu rozwiązującego labirynt


# generowanie środków sześciokątów
def generate_points(width, height):
    list_of_x = []
    list_of_y = []
    x = 1  # długość boku hexagonu
    for i in range(0, height):
        for j in range(0, width):
            if i % 2 == 1:
                displacement = 0.5 * x * sqrt(3)
            else:
                displacement = 0
            point_x = displacement + 0.5 * x * sqrt(3) + j * x * sqrt(3)
            point_y = x + i * 1.5 * x
            list_of_x.append(point_x)
            list_of_y.append(point_y)

    return list_of_x, list_of_y


# obliczanie wierzchołków szeciokątów
def hexagons_tops(list_x, list_y, wall):
    list_of_hexagons = []
    for i in range(0, len(list_x)):
        px = list_x[i]
        py = list_y[i]
        hexagon = []
        # wektory do obliczania wierzchołków gdy dany jest środek
        vec_point = [[px, py - wall], [px + 0.5 * wall * sqrt(3), py - 0.5 * wall],
                     [px + 0.5 * wall * sqrt(3), py + 0.5 * wall], [px, py + wall],
                     [px - 0.5 * wall * sqrt(3), py + 0.5 * wall], [px - 0.5 * wall * sqrt(3), py - 0.5 * wall]]
        for vec in vec_point:
            hexagon.append(vec)
        list_of_hexagons.append(hexagon)

    return list_of_hexagons


# sprawdzam czy pomiędzy wierzchołkami sześciokąta ma być narysowana krawędź
def draw_walls(figure, tab_walls, iterator):
    list_x = [figure[0, 0]]
    list_y = [figure[0, 1]]
    px = int(iterator / size)
    py = int(iterator % size)
    for i in range(0, len(figure) - 1):
        if tab_walls[px, py, i] == 1:
            list_x.append(figure[i + 1, 0])
            list_y.append(figure[i + 1, 1])
        else:
            line = Line2D(list_x, list_y)
            ax.add_line(line)
            list_x = [figure[i + 1, 0]]
            list_y = [figure[i + 1, 1]]
    if len(list_x) > 1:
        line = Line2D(list_x, list_y)
        ax.add_line(line)


def draw_maze(hexagons, hexagon_walls):
    count = 0
    for hexagon in hexagons:
        array = np.hstack(hexagon)
        array = np.append(array, array[0])
        array = np.append(array, array[1])
        array = array.reshape(7, 2)
        draw_walls(array, hexagon_walls, count)
        count = count + 1


def neighbour_available(been, px, py, offset):
    px = px + 1
    py = py + 1
    if (been[px + 1, py + offset] == 0 or been[px, py + 1] == 0 or been[px - 1, py + offset] == 0
            or been[px - 1, py - 1 + offset] == 0 or been[px, py - 1] == 0
            or been[px + 1, py - 1 + offset] == 0):
        return True
    else:
        return False


def new_start_point(row, col, been, offset):
    pos_x = 0
    pos_y = 0
    for i in range(row - 1, -1, -1):
        for j in range(0, col):
            if neighbour_available(been, i, j, offset) and been[i + 1, j + 1] == 1:
                pos_x = i
                pos_y = j
    return pos_x, pos_y


# definiowanie ilości hexagonów we wierszach i kolumnach
size = 15

# dzieki tym tablicom wiem, w którą stronę mogę się poruszyć
prawo = np.ones((size, size))
prawo_gora = np.ones((size, size))
lewo_gora = np.ones((size, size))
lewo = np.ones((size, size))
lewo_dol = np.ones((size, size))
prawo_dol = np.ones((size, size))

prawo[:, size - 1] = np.zeros((1, size))
prawo_gora[0, :] = np.zeros((1, size))
lewo_gora[0, :] = np.zeros((1, size))
lewo[:, 0] = np.zeros((1, size))
lewo_dol[size - 1, :] = np.zeros((1, size))
prawo_dol[size - 1, :] = np.zeros((1, size))
for i in range(0, size):
    for j in range(0, size):
        if i % 2 == 1 and j == size - 1:
            prawo_dol[i, j] = 0
            prawo_gora[i, j] = 0
        elif i % 2 == 0 and j == 0:
            lewo_dol[i, j] = 0
            lewo_gora[i, j] = 0

# tablica która informuje mnie o tym, gdzie są ściany
hexagon_walls = np.ones(shape=(size, size, 6))

# otworzenie wejścia i wyjścia z labiryntu
hexagon_walls[0, 0, 5] = 0
hexagon_walls[size - 1, size - 1, 2] = 0

fig = plt.figure()
ax = fig.add_subplot(111)

punkty_x, punkty_y = generate_points(size, size)
hexagons = hexagons_tops(punkty_x, punkty_y, 1)

# stworzenie tablicy do sprawdzania na jakich polach byłem, dodaję ramkę dookoła, że przy sprawdzaniu czy mam sąsiada
# nie wyjdę poza zakres tablicy
visited = np.zeros(shape=(size + 2, size + 2))
visited[:, 0] = np.ones((1, size + 2))
visited[:, size + 1] = np.ones((1, size + 2))
visited[0, :] = np.ones((1, size + 2))
visited[size + 1, :] = np.ones((1, size + 2))
unvisited = size * size

# tutaj generowanie labiryntu

# pozycja początkowa
pos_x = size - 1
pos_y = 0
found_new_point = True

# wykonuję pętlę dopóki wszystkie komórki nie będą ze sobą połączone
while unvisited > 0:

    # w zależności czy jestem we wierszu parzystym czy nieparzystym, to muszę uwzględnić zmianę przy poruszaniu się po
    # skosie, dla parzystego ruch w prawo do góry sprowadza się do zmniejszenia pozycji x o 1, y bez zmian,
    # dla nieparzystego wykonanie tego samego ruchu powoduje z mniejszenia pozycji x o 1, zwiększenie pozycji y o 1
    if pos_x % 2 == 0:
        offset = 0
    else:
        offset = 1

    # gdy wykona się pętla while i jestem w nowym punkcie to muszę zaznaczyć ją jako odwiedzoną,
    # oraz zmniejszyć liczbę komórek nieodwiedzonych
    if found_new_point:
        visited[pos_x + 1, pos_y + 1] = 1
        unvisited = unvisited - 1

    # jeżeli natomiast po iteracji nie jestem w nowej komórce to sprawdzam czy są nieodwiedzeni sąsiedzi,
    # do których mogę przejść, jeżeli tak to nic nie robię w kolejnych iteracjach zostaną oni znalezieni
    # jeżeli nie ma sąsiadów, to szukam odwiedzonego już punktu, który ma nieodwiedzonych sąsiadów
    elif neighbour_available(visited, pos_x, pos_y, offset) is False:
        pos_x, pos_y = new_start_point(size, size, visited, offset)

        # ustalam czy wystąpi przesunięcie dla nowych współrzędnych
        if pos_x % 2 == 0:
            offset = 0
        else:
            offset = 1

    # generacja jednego z 6 kierunków ruchów
    direction = randint(1, 6)
    found_new_point = False

    # w zależności od tego jaki kierunek ruchu został wygenerowany sprawdzam czy jest możliwy ruch w tamtą stronę,
    # oraz czy komórka do której mam się udać była już odwiedzona
    # dodatkowo wyburzając ściany współrzędna x jest postaci abs(pos_x - rows + 1), gdyż indeksowanie tablicy zaczyna
    # się od lewego górnego rogu, a wypisywanie hexagonów od lewego dolnego
    if direction == 1 and prawo_dol[pos_x, pos_y] == 1 and visited[pos_x + 2, pos_y + offset + 1] == 0:
        hexagon_walls[abs(pos_x - size + 1), pos_y, 0] = 0
        pos_x = pos_x + 1
        pos_y = pos_y + offset
        hexagon_walls[abs(pos_x - size + 1), pos_y, 3] = 0
        found_new_point = True
    elif direction == 2 and prawo[pos_x, pos_y] == 1 and visited[pos_x + 1, pos_y + 2] == 0:
        hexagon_walls[abs(pos_x - size + 1), pos_y, 1] = 0
        pos_y = pos_y + 1
        hexagon_walls[abs(pos_x - size + 1), pos_y, 4] = 0
        found_new_point = True
    elif direction == 3 and prawo_gora[pos_x, pos_y] == 1 and visited[pos_x, pos_y + offset + 1] == 0:
        hexagon_walls[abs(pos_x - size + 1), pos_y, 2] = 0
        pos_x = pos_x - 1
        pos_y = pos_y + offset
        hexagon_walls[abs(pos_x - size + 1), pos_y, 5] = 0
        found_new_point = True
    elif direction == 4 and lewo_gora[pos_x, pos_y] == 1 and visited[pos_x, pos_y + offset] == 0:
        hexagon_walls[abs(pos_x - size + 1), pos_y, 3] = 0
        pos_x = pos_x - 1
        pos_y = pos_y - 1 + offset
        hexagon_walls[abs(pos_x - size + 1), pos_y, 0] = 0
        found_new_point = True
    elif direction == 5 and lewo[pos_x, pos_y] == 1 and visited[pos_x + 1, pos_y] == 0:
        hexagon_walls[abs(pos_x - size + 1), pos_y, 4] = 0
        pos_y = pos_y - 1
        hexagon_walls[abs(pos_x - size + 1), pos_y, 1] = 0
        found_new_point = True
    elif direction == 6 and lewo_dol[pos_x, pos_y] == 1 and visited[pos_x + 2, pos_y + offset] == 0:
        hexagon_walls[abs(pos_x - size + 1), pos_y, 5] = 0
        pos_x = pos_x + 1
        pos_y = pos_y - 1 + offset
        hexagon_walls[abs(pos_x - size + 1), pos_y, 2] = 0
        found_new_point = True

axes = plt.gca()
axes.set_xlim([-1, sqrt(3)*(size + 1) + 1])
axes.set_ylim([-1, 1.5 * size + 2])
draw_maze(hexagons, hexagon_walls)
plt.show()
