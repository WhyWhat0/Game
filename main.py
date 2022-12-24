# Какая то хрень в choice.
from random import randint, choice
import time
import os


class Ship:

    def __init__(self, length, tp=1, x=0, y=0):
        self.x = x
        self.y = y
        self.length = length
        self.tp = tp
        self.is_move = True
        self.cells = [1] * length
        self.is_broken = False

    def __repr__(self):
        return f'{(self.length, self.x, self.y, self.tp)}'

    def set_start_coords(self, x, y):
        self.x = x
        self.y = y

    def move(self, go):
        if self.is_move:
            if self.tp == 1:
                self.x += go
            else:
                self.y += go

    def is_collide(self, ship):
        a = b = c = d = 0
        for i in range(self.length):
            for j in range(ship.length):
                if ((self.x - ship.x + a - b) ** 2 + (self.y - ship.y + c - d) ** 2) ** 0.5 <= 2 ** 0.5:
                    return True
                if ship.tp == 1:
                    b += 1
                if ship.tp == 2:
                    d += 1
            if self.tp == 1:
                a += 1
            if self.tp == 2:
                c += 1
            b = 0
            d = 0

        return False

    def is_out_pole(self, size):
        if self.tp == 1:
            if self.x < 0 or self.y < 0 or self.x + self.length - 1 > size - 1 or self.y > size - 1:
                return True
        else:
            if self.x < 0 or self.y < 0 or self.x > size - 1 or self.y + self.length - 1 > size - 1:
                return True
        return False

    def __getitem__(self, item):
        return self.cells[item]

    def __setitem__(self, key, value):
        self.cells[key] = value


class SeaBattle:
    def __init__(self, size):
        self.active = True
        self.size = size
        self.pole_litter_collection = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        self.processed_attacks = []
        self.myprocessed_attacks = []
        self.ship_is_damaged = False
        self.count_my_broken_ships = 0
        self.count_opp_broken_ships = 0
        self.smart_attacks = SmartPlayer()
        self.active = False

        self.ships = [
            Ship(4, tp=randint(1, 2)),
            Ship(3, tp=randint(1, 2)),
            Ship(3, tp=randint(1, 2)),
            Ship(2, tp=randint(1, 2)),
            Ship(2, tp=randint(1, 2)),
            Ship(2, tp=randint(1, 2)),
            Ship(1, tp=randint(1, 2)),
            Ship(1, tp=randint(1, 2)),
            Ship(1, tp=randint(1, 2)),
            Ship(1, tp=randint(1, 2))
        ]

        self.myships = [
            Ship(4, tp=randint(1, 2)),
            Ship(3, tp=randint(1, 2)),
            Ship(3, tp=randint(1, 2)),
            Ship(2, tp=randint(1, 2)),
            Ship(2, tp=randint(1, 2)),
            Ship(2, tp=randint(1, 2)),
            Ship(1, tp=randint(1, 2)),
            Ship(1, tp=randint(1, 2)),
            Ship(1, tp=randint(1, 2)),
            Ship(1, tp=randint(1, 2))
        ]

    def move_ships(self, ships):
        for ship in ships:
            go = choice([-1, 1])
            ship.move(go)
            if ship.is_out_pole(self.size) or True in [ship.is_collide(s) for s in
                                                       list(filter(lambda x: x != ship, ships))]:
                ship.move((-go) * 2)
            if ship.is_out_pole(self.size) or True in [ship.is_collide(s) for s in
                                                       list(filter(lambda x: x != ship, ships))]:
                ship.move(go)

    def get_opp_ships(self):
        return self.ships

    def get_my_ships(self):
        return self.myships

    def init_pole_randomly_for_ships(self, ships):
        k = 0
        for ship in ships:
            if ship.tp == 1:
                ship.x = randint(0, self.size - ship.length)
                ship.y = randint(0, self.size)
            else:
                ship.x = randint(0, self.size)
                ship.y = randint(0, self.size - ship.length)
            while ship.is_out_pole(self.size) or True in [ship.is_collide(ships[i]) for i in range(0, k)]:
                if ship.tp == 1:
                    ship.x = randint(0, self.size - ship.length)
                    ship.y = randint(0, self.size)
                else:
                    ship.x = randint(0, self.size)
                    ship.y = randint(0, self.size - ship.length)
            k += 1

    def init_my_ships(self):
        for l in (4, 3, 3, 2, 2, 2, 1, 1, 1, 1):
            ship = Ship(*[l] + list(map(int, input(f'{l}: ').split())))
            self.myships.append(ship)

    def generate_my_pole(self):
        self.mypole = list(list(0 for _ in range(self.size)) for __ in range(self.size))
        for ship in self.myships:
            for i in range(ship.length):
                if ship.tp == 1:
                    self.mypole[ship.y][ship.x + i] = 'X' if ship.is_broken else ship[i]
                else:
                    self.mypole[ship.y + i][ship.x] = 'X' if ship.is_broken else ship[i]
        for p in self.processed_attacks:
            if 0 <= p[1] < self.size and 0 <= p[0] < self.size:
                if self.mypole[p[1]][p[0]] == 0:
                    self.mypole[p[1]][p[0]] = '*'

    def generate_opp_pole(self):
        self.pole = list(list(0 for _ in range(self.size)) for __ in range(self.size))
        for ship in self.ships:
            for i in range(ship.length):
                if ship.tp == 1:
                    self.pole[ship.y][ship.x + i] = 'X' if ship.is_broken else 2 if ship[i] == 2 else 0
                else:
                    self.pole[ship.y + i][ship.x] = 'X' if ship.is_broken else 2 if ship[i] == 2 else 0
            for p in self.myprocessed_attacks:
                if 0 <= p[1] < self.size and 0 <= p[0] < self.size:
                    if self.pole[p[1]][p[0]] == 0:
                        self.pole[p[1]][p[0]] = '*'

    def show_game(self):
        self.generate_opp_pole()
        self.generate_my_pole()
        print(*['#'] + [litter for litter in self.pole_litter_collection], '  ',
              *['#'] + [litter for litter in self.pole_litter_collection])
        for i in range(self.size):
            print(self.pole_litter_collection[i], *self.mypole[i], '  ', self.pole_litter_collection[i], *self.pole[i])
        print()

    def search_coors(self, x, y, l):
        for ship in l:
            if ship.tp == 1:
                if ship.y == y and ship.x <= x < ship.x + ship.length:
                    return ship
            else:
                if ship.x == x and ship.y <= y < ship.y + ship.length:
                    return ship
        return None

    def processed_cells_around_ship(self, ship):
        if ship in self.myships:
            if ship.tp == 1:
                self.processed_attacks.extend(
                    [(ship.x + i // 3 - 1, ship.y + i % 3 - 1) for i in range((ship.length + 2) * 3)])
            else:
                self.processed_attacks.extend(
                    [(ship.x + i % 3 - 1, ship.y + i // 3 - 1) for i in range((ship.length + 2) * 3)])
        else:
            if ship.tp == 1:
                self.myprocessed_attacks.extend(
                    [(ship.x + i // 3 - 1, ship.y + i % 3 - 1) for i in range((ship.length + 2) * 3)])
            else:
                self.myprocessed_attacks.extend(
                    [(ship.x + i % 3 - 1, ship.y + i // 3 - 1) for i in range((ship.length + 2) * 3)])

    def my_attack(self, a, b):
        self.active = True
        if a in self.pole_litter_collection + list(map(lambda l: l.lower(), self.pole_litter_collection)):
            x, y = self.pole_litter_collection.index(a.upper()), self.pole_litter_collection.index(b.upper())
        else:
            x, y = int(a) - 1, int(b) - 1
        ship = self.search_coors(x, y, self.ships)
        if ship:
            if ship.tp == 1:
                ship[x - ship.x] = 2
            else:
                ship[y - ship.y] = 2

            if 1 not in ship.cells:
                self.processed_cells_around_ship(ship)
                ship.is_broken = True
                self.count_opp_broken_ships += 1
        else:
            self.active = False
        self.myprocessed_attacks.append((x, y))

    def comp_attack(self):
        self.active = True
        if self.ship_is_damaged:
            if self.smart_attacks.attack():
                self.ship_is_damaged = False
                self.count_my_broken_ships += 1

        else:
            x = randint(0, self.size - 1)
            y = randint(0, self.size - 1)
            while (x, y) in self.processed_attacks:
                x = randint(0, self.size - 1)
                y = randint(0, self.size - 1)
            ship = self.search_coors(x, y, self.myships)
            if ship:
                if ship.tp == 1:
                    ship[x - ship.x] = 2
                else:
                    ship[y - ship.y] = 2
                self.ship_is_damaged = True
                self.smart_attacks.init(ship, self.processed_attacks, self.size)
                if 1 not in ship.cells:
                    self.processed_cells_around_ship(ship)
                    self.ship_is_damaged = False
                    ship.is_broken = True
                    self.count_my_broken_ships += 1
            else:
                self.active = False
            self.processed_attacks.append((x, y))


class SmartPlayer:
    def __init__(self):
        self.active = False

    def init(self, ship, processed, size):
        self.active = True
        self.ship = ship
        self.size = size
        self.processed = processed
        self.line = False
        self.push = None
        self.wrong = False
        if ship.tp == 1:
            self.x = ship.x + ship.cells.index(2)
            self.y = ship.y
        else:
            self.x = ship.x
            self.y = ship.y + ship.cells.index(2)

    def attack(self):
        self.active = True
        x = self.x
        y = self.y
        processed = self.processed
        f = [i for i in range(self.size)]
        if not self.line:
            vars = list(filter(lambda t: t not in processed and t[0] in f and t[1] in f,
                               [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]))
            self.push = choice(vars)
            processed.append(self.push)

        else:
            if not self.push:
                if self.ship.tp == 1:
                    self.rvars = [(x + i, y) for i in range(1, self.ship.length)]
                    self.lvars = [(x - i, y) for i in range(1, self.ship.length)]
                else:
                    self.rvars = [(x, y + i) for i in range(1, self.ship.length)]
                    self.lvars = [(x, y - i) for i in range(1, self.ship.length)]

                self.lvars = list(filter(lambda t: t not in processed and t[0] in f and t[1] in f, self.lvars))
                self.rvars = list(filter(lambda t: t not in processed and t[0] in f and t[1] in f, self.rvars))

                if self.lvars and self.rvars:
                    self.push = choice((self.lvars[0], self.rvars[0]))
                else:
                    self.push = self.lvars[0] if self.lvars else self.rvars[0]

            elif self.wrong:
                self.push = self.lvars[0] if self.push in self.rvars else self.rvars[0]
                self.wrong = False

            else:
                if self.push in self.lvars and self.push == self.lvars[-1] or self.push in self.rvars and self.push == \
                        self.rvars[-1]:
                    self.push = self.lvars[0] if self.push in self.rvars else self.rvars[0]
                else:
                    self.push = self.lvars[self.lvars.index(self.push) + 1] if self.push in self.lvars else self.rvars[
                        self.rvars.index(self.push) + 1]

            processed.append(self.push)

        if self.ship.tp == 1 and self.push[1] == self.ship.y and 0 <= self.push[0] - self.ship.x < self.ship.length or \
                self.ship.tp == 2 and self.push[0] == self.ship.x and 0 <= self.push[
            1] - self.ship.y < self.ship.length:

            if self.ship.tp == 1:
                self.ship[self.push[0] - self.ship.x] = 2
            else:
                self.ship[self.push[1] - self.ship.y] = 2
            self.push = self.push if self.line else None
            self.line = True

        elif self.line:
            self.wrong = True
        else:
            if self.line:
                self.wrong = True
            self.active = False

        if 1 not in self.ship.cells:
            self.ship.is_broken = True

            if self.ship.tp == 1:
                processed.extend(
                    [(self.ship.x + i // 3 - 1, self.ship.y + i % 3 - 1) for i in range((self.ship.length + 2) * 3)])

            else:
                processed.extend(
                    [(self.ship.x + i % 3 - 1, self.ship.y + i // 3 - 1) for i in range((self.ship.length + 2) * 3)])

            return True
        return


game = SeaBattle(10)
game.init_pole_randomly_for_ships(game.get_my_ships())
game.init_pole_randomly_for_ships(game.get_opp_ships())

a = 's'
if a == 's':
    game.show_game()
    while game.count_my_broken_ships < 10 and game.count_opp_broken_ships < 10:
        while True:
            game.my_attack(*input('print coords: ').split())
            if game.active:
                game.show_game()
            else:
                break

        while True:
            game.comp_attack()
            if game.active or game.smart_attacks.active:
                game.show_game()
                time.sleep(0.5)
            else:
                break



else:
    print('dt started \n', )
    game.show_game()
    for i in range(100):
        game.comp_attack()
        game.show_game()
        if game.count_my_broken_ships == 10:
            print('end')
            break

