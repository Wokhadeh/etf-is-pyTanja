import pygame
import os
import config
import math


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, row, col, file_name, transparent_color=None):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (col * config.TILE_SIZE, row * config.TILE_SIZE)
        self.row = row
        self.col = col

    @staticmethod
    def get_neighbours(game_map, row, col):
        north = game_map[row - 1][col] if row > 0 else None
        west = game_map[row][col - 1] if col > 0 else None
        south = game_map[row + 1][col] if row < len(game_map) - 1 else None
        east = game_map[row][col + 1] if col < len(game_map[0]) - 1 else None
        neighbours = [north, east, south, west]
        return list(filter(None, neighbours))


class Agent(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Agent, self).__init__(row, col, file_name, config.DARK_GREEN)

    def move_towards(self, row, col):
        row = row - self.row
        col = col - self.col
        self.rect.x += col
        self.rect.y += row

    def place_to(self, row, col):
        self.row = row
        self.col = col
        self.rect.x = col * config.TILE_SIZE
        self.rect.y = row * config.TILE_SIZE

    # game_map - list of lists of elements of type Tile
    # goal - (row, col)
    # return value - list of elements of type Tile
    def get_agent_path(self, game_map, goal):
        pass


class ExampleAgent(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]

        row = self.row
        col = self.col
        while True:
            if row != goal[0]:
                row = row + 1 if row < goal[0] else row - 1
            elif col != goal[1]:
                col = col + 1 if col < goal[1] else col - 1
            else:
                break
            path.append(game_map[row][col])
        return path


class Aki(Agent):

    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = []
        fields_to_visit = [(game_map[self.row][self.col], None)]
        visited_fields = []

        row = self.row
        col = self.col
        current_field = (game_map[row][col], None)

        while fields_to_visit:
            current_field = fields_to_visit[0]
            if current_field[0].row == goal[0] and current_field[0].col == goal[1]:
                visited_fields.append(current_field)
                break
            visited_fields.append(fields_to_visit.pop(0))
            fields_and_costs = []
            neighbours = BaseSprite.get_neighbours(game_map, current_field[0].row, current_field[0].col)

            for field in neighbours:
                fields_and_costs.append((field, field.cost()))
            visited_fields_fields = [elem[0] for elem in visited_fields]
            fields_and_costs = list(filter(lambda node: node[0] not in visited_fields_fields,
                                           fields_and_costs))
            fields_and_costs.sort(key=lambda field_and_cost: field_and_cost[1])
            for field_and_cost in reversed(fields_and_costs)  :
                fields_to_visit.insert(0,(field_and_cost[0], current_field[0]))


        path.append(visited_fields[-1][0])
        next_field_in_path = visited_fields[-1][1]
        while next_field_in_path:
            path.append(next_field_in_path)
            for field in reversed(visited_fields):
                if field[0] == next_field_in_path:
                    next_field_in_path = field[1]
                    break
        path.reverse()
        return path


class Jocke(Agent):

    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = []
        fields_to_visit = [(game_map[self.row][self.col], None)]
        visited_fields = []

        row = self.row
        col = self.col
        current_field = (game_map[row][col], None)

        while True:

            if current_field[0].row == goal[0] and current_field[0].col == goal[1]:
                visited_fields.append(current_field)
                break
            fields_and_costs = []
            neighbours = BaseSprite.get_neighbours(game_map, current_field[0].row, current_field[0].col)

            for field in neighbours:
                neighbours_of_neighbour = BaseSprite.get_neighbours(game_map, field.row, field.col)
                neighbours_of_neighbour = list(filter(lambda field: field != current_field[0], neighbours_of_neighbour))
                cost = sum(field.cost() for field in neighbours_of_neighbour) / len(neighbours_of_neighbour)
                fields_and_costs.append((field, cost))
            visited_fields_fields = [elem[0] for elem in visited_fields]
            fields_and_costs = list(filter(lambda node: node[0] not in visited_fields_fields,
                                           fields_and_costs))
            fields_and_costs.sort(key=lambda field_and_cost: field_and_cost[1])
            for field_and_cost in fields_and_costs:
                fields_to_visit.append((field_and_cost[0], current_field[0]))
            visited_fields.append(fields_to_visit.pop(0))
            current_field = fields_to_visit[0]
        path.append(visited_fields[-1][0])
        next_field_in_path = visited_fields[-1][1]
        while next_field_in_path:
            path.append(next_field_in_path)
            for field in visited_fields:
                if field[0] == next_field_in_path:
                    next_field_in_path = field[1]
                    break
        path.reverse()
        return path


class Draza(Agent):

    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):

        row = self.row
        col = self.col
        current_field = game_map[row][col]
        partial_paths = []
        partial_paths.append(([current_field], current_field.cost()))  # (partial path,cost)
        while (partial_paths):
            current_partial_path = partial_paths.pop(0)
            neighbours = BaseSprite.get_neighbours(game_map, current_partial_path[0][-1].row,
                                                   current_partial_path[0][-1].col)
            neighbours = list(filter(lambda neighbour: neighbour not in current_partial_path[0], neighbours))
            for neighbour in neighbours:
                if (neighbour.col == goal[1] and neighbour.row == goal[0]):
                    path = current_partial_path[0].copy()
                    path.append(neighbour)
                    return path
                else:
                    new_partial_path = current_partial_path[0].copy()
                    new_partial_path.append(neighbour)
                    new_partial_path_cost = current_partial_path[1] + neighbour.cost()
                    partial_paths.append((new_partial_path, new_partial_path_cost))
            partial_paths.sort(key=lambda x: (x[1], len(x[0])))


class Bole(Agent):

    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        row = self.row
        col = self.col
        current_field = game_map[row][col]
        partial_paths = []
        partial_paths.append(([current_field], current_field.cost(),
                              current_field.cost() + Bole.calculate_distance(row, col,goal)))  # (partial path,cost, cost+heuristic)
        while (partial_paths):
            current_partial_path = partial_paths.pop(0)
            neighbours = BaseSprite.get_neighbours(game_map, current_partial_path[0][-1].row,
                                                   current_partial_path[0][-1].col)
            neighbours = list(filter(lambda neighbour: neighbour not in current_partial_path[0], neighbours))
            for neighbour in neighbours:
                if (neighbour.col == goal[1] and neighbour.row == goal[0]):
                    path = current_partial_path[0].copy()
                    path.append(neighbour)
                    return path
                else:
                    new_partial_path = current_partial_path[0].copy()
                    new_partial_path.append(neighbour)
                    new_partial_path_cost = current_partial_path[1] + neighbour.cost()
                    new_partial_path_cost_and_heuristic = new_partial_path_cost + Bole.calculate_distance(neighbour.row,
                                                                                                          neighbour.col,
                                                                                                          goal)
                    partial_paths.append((new_partial_path, new_partial_path_cost,new_partial_path_cost_and_heuristic ))
            partial_paths.sort(key=lambda x: x[2])

    @staticmethod
    def calculate_distance(row, col, goal):
        return math.sqrt((row - goal[0]) ** 2 + (col - goal[1]) ** 2)


class Tile(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Tile, self).__init__(row, col, file_name)

    def position(self):
        return self.row, self.col

    def cost(self):
        pass

    def kind(self):
        pass


class Stone(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'stone.png')

    def cost(self):
        return 1000

    def kind(self):
        return 's'


class Water(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'water.png')

    def cost(self):
        return 500

    def kind(self):
        return 'w'


class Road(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'road.png')

    def cost(self):
        return 2

    def kind(self):
        return 'r'


class Grass(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'grass.png')

    def cost(self):
        return 3

    def kind(self):
        return 'g'


class Mud(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'mud.png')

    def cost(self):
        return 5

    def kind(self):
        return 'm'


class Dune(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'dune.png')

    def cost(self):
        return 7

    def kind(self):
        return 's'


class Goal(BaseSprite):
    def __init__(self, row, col):
        super().__init__(row, col, 'x.png', config.DARK_GREEN)


class Trail(BaseSprite):
    def __init__(self, row, col, num):
        super().__init__(row, col, 'trail.png', config.DARK_GREEN)
        self.num = num

    def draw(self, screen):
        text = config.GAME_FONT.render(f'{self.num}', True, config.WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
