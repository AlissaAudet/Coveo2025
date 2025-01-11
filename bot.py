import random
from game_message import *
import heapq

class Bot:
    def __init__(self):
        self.state = {}  #git add

    def get_next_move(self, game_message: TeamGameState):
        actions = []
        self.print_grid(game_message.map)  # Optionnel, pour débugger la grille

        # Mise à jour de l'état selon le score maximum actuel
        score_max = max(game_message.score.values())
        cles_max = [k for k, v in game_message.score.items() if v == score_max]

        if game_message.currentTeamId in cles_max and len(cles_max) == 1:
            global_state = "kill"
        else:
            global_state = "fetch"

        for character in game_message.yourCharacters:
            if character.id not in self.state:
                self.state[character.id] = global_state  # Initialise l'état par personnage

            if not character.alive:
                actions.append(MoveToAction(characterId=character.id, position=character.position))
                continue

            if self.state[character.id] == "fetch":
                # Vérifier si le personnage est déjà sur un item 'blitzium'
                items = [item for item in game_message.items if item.type.startswith("blitzium")]
                item_at_position = next((item for item in items if item.position == character.position), None)

                if item_at_position:
                    actions.append(GrabAction(characterId=character.id))  # Ramasser l'item
                    self.state[character.id] = "drop"
                    continue  # Passe au prochain caractère après avoir ramassé l'item
                target_item = self.find_nearest_blitzium(character, game_message)
                if target_item is not None:
                    path = self.a_star(character.position, target_item.position, game_message.map,
                                       game_message.otherCharacters)
                    if path and len(path) > 1:
                        move_action = self.get_move_action(character, path[1])
                        actions.append(move_action)
                    else:
                        actions.append(self.get_random_move(character))
                else:
                    actions.append(self.get_random_move(character))

            elif self.state[character.id] == "kill":
                # Ajoutez ici la logique pour 'kill' si nécessaire
                pass
            

        return actions

    def find_nearest_blitzium(self, character, game_message):
        items = [item for item in game_message.items if item.type.startswith("blitzium") and item.position != character.position]
        if not items:
            return None
        nearest_item = min(items, key=lambda item: self.manhattan_distance(character.position, item.position))
        return nearest_item

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

    def a_star(self, start, goal, game_map, enemies):
        grid = self.create_grid(game_map.tiles)

        def heuristic(pos1, pos2):
            return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

        def is_valid(pos):
            if not (0 <= pos.x < len(grid[0]) and 0 <= pos.y < len(grid)):
                return False
            if grid[pos.y][pos.x] == 1:
                return False
            if any(enemy.position == pos for enemy in enemies if enemy.alive):
                return False
            return True

        directions = [Position(0, -1), Position(0, 1), Position(-1, 0), Position(1, 0)]
        open_set = []
        start_tuple = (start.x, start.y)
        goal_tuple = (goal.x, goal.y)
        heapq.heappush(open_set, (0, start_tuple))
        came_from = {}
        g_score = {start_tuple: 0}
        f_score = {start_tuple: heuristic(start, goal)}

        while open_set:
            _, current_tuple = heapq.heappop(open_set)
            current = Position(*current_tuple)

            if current_tuple == goal_tuple:
                path = []
                while current_tuple in came_from:
                    path.append(Position(*current_tuple))
                    current_tuple = came_from[current_tuple]
                path.append(start)
                path.reverse()
                return path

            for direction in directions:
                neighbor = Position(current.x + direction.x, current.y + direction.y)
                neighbor_tuple = (neighbor.x, neighbor.y)
                if not is_valid(neighbor):
                    continue

                tentative_g_score = g_score[current_tuple] + 1

                if neighbor_tuple not in g_score or tentative_g_score < g_score[neighbor_tuple]:
                    came_from[neighbor_tuple] = current_tuple
                    g_score[neighbor_tuple] = tentative_g_score
                    f_score[neighbor_tuple] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor_tuple], neighbor_tuple))

        return None

    def get_move_action(self, character, next_step):
        dx = next_step.x - character.position.x
        dy = next_step.y - character.position.y

        if dx == 1:
            return MoveRightAction(characterId=character.id)
        elif dx == -1:
            return MoveLeftAction(characterId=character.id)
        elif dy == 1:
            return MoveDownAction(characterId=character.id)
        elif dy == -1:
            return MoveUpAction(characterId=character.id)
        else:
            return MoveToAction(characterId=character.id, position=character.position)

    def get_random_move(self, character):
        return random.choice([
            MoveUpAction(characterId=character.id),
            MoveDownAction(characterId=character.id),
            MoveLeftAction(characterId=character.id),
            MoveRightAction(characterId=character.id),
        ])

    def print_grid(self, game_map):
        grid = game_map.tiles
        for x in range(len(grid[0])):  # Parcourt les colonnes (axe x)
            print("".join(["#" if grid[y][x] == TileType.WALL else "." for y in range(len(grid))]))
        print("Grid printed successfully.")

    def create_grid(self, tiles):
        actual_height = len(tiles)
        actual_width = len(tiles[0]) if actual_height > 0 else 0
        grid = []
        for x in range(actual_width):
            grid_row = []
            for y in range(actual_height):
                tile = tiles[y][x]
                if tile == TileType.WALL:
                    grid_row.append(1)
                else:
                    grid_row.append(0)
            grid.append(grid_row)

        return grid
