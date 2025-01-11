import random
from game_message import *
import heapq

class Bot:

    def __init__(self):
        self.state = {}
        self.role = {}

    def get_next_move(self, game_message: TeamGameState):
        actions = []
        for character in game_message.yourCharacters:
            index = game_message.yourCharacters.index(character)
            if character.id not in self.role :
                if index % 2 == 0 :
                    self.role[character.id] = "gatherer"
                else :
                    self.role[character.id] = "defender"
            if character.alive:
                if self.role[character.id] == "gatherer" :
                    action = self.gatherer(character, game_message)
                    if action:
                        actions.append(action)
                        print(f"Actions for {character.id}: {action}")  # Debugging output
                elif self.role[character.id] == "defender":
                    enemy = self.get_nearest_enemy_character(character, game_message)
                    if enemy is not None:
                        path = self.a_star(character.position, enemy.position, game_message.map, game_message.otherCharacters)
                        actions.append(self.get_move_action(character, path[1]))
                    continue
        return actions

    def gatherer(self, character, game_message):
        actions_gatherer = []

        # Check if the character is on the same position as any blitzium
        current_blitzium = next((item for item in game_message.items if
                                 item.type.startswith("blitzium") and item.position == character.position), None)
        if current_blitzium and character.numberOfCarriedItems < game_message.constants.maxNumberOfItemsCarriedPerCharacter:
            actions_gatherer.append(GrabAction(characterId=character.id))
            return actions_gatherer[0] if actions_gatherer else None
        else:
            path_to_blitzium = self.get_path_to_nearest_blitzium(character, game_message)
            if path_to_blitzium:
                actions_gatherer.append(self.get_move_action(character, path_to_blitzium[1]))
        if character.numberOfCarriedItems > 0 :
            path_to_drop_zone = self.get_path_to_nearest_drop_zone(character, game_message)
            if path_to_drop_zone:
                actions_gatherer.append(self.get_move_action(character, path_to_drop_zone[1]))

        return actions_gatherer[0] if actions_gatherer else None

    def get_path_to_nearest_blitzium(self, character, game_message):
        nearest_item = self.find_nearest_blitzium(character, game_message)
        if nearest_item is not None:
            return self.a_star(character.position, nearest_item.position, game_message.map,
                               game_message.otherCharacters)
        return None

    def get_path_to_nearest_drop_zone(self, character, game_message):
        drop_position = self.find_first_empty_position_in_team_zone(character, game_message)
        if drop_position is not None:
            return self.a_star(character.position, drop_position, game_message.map, game_message.otherCharacters)
        return None

    def find_nearest_blitzium(self, character, game_message):
        items = [
            item for item in game_message.items
            if item.type.startswith("blitzium") and
               0 <= item.position.y < len(game_message.teamZoneGrid) and
               0 <= item.position.x < len(game_message.teamZoneGrid[0]) and
               game_message.teamZoneGrid[item.position.y][item.position.x] != game_message.currentTeamId
        ]
        if items:
            return min(items, key=lambda item: self.manhattan_distance(character.position, item.position))
        return None

    def find_first_empty_position_in_team_zone(self, character, game_message):
        for y in range(len(game_message.teamZoneGrid)):
            for x in range(len(game_message.teamZoneGrid[0])):
                if game_message.teamZoneGrid[y][x] == game_message.currentTeamId:
                    if not any(item.position.x == x and item.position.y == y for item in game_message.items):
                        return Position(x, y)
        print("No empty position found in the team zone.")
        return None
    
    def get_nearest_enemy_character(self, character, game_message) :
        enemies = [
            enemy for enemy in game_message.otherCharacters
            if game_message.teamZoneGrid[enemy.position.x][enemy.position.y] == game_message.currentTeamId
        ]
        if not enemies:
            return None

        nearest_enemy = min(enemies, key=lambda enemy: self.manhattan_distance(character.position, enemy.position))
        return nearest_enemy   
    
    def get_nearest_enemy_tile(self, character, game_message) :
        nearest_dist = 10000
        nearest_position = None
        for x in range(len(game_message.teamZoneGrid)) :
            for y in range(len(game_message.teamZoneGrid[x])):
                if game_message.teamZoneGrid[x][y] != game_message.currentTeamId and game_message.teamZoneGrid[x][y] != '':
                    distance = self.manhattan_distance(character.position, Position(x, y))
                    if nearest_dist > distance:
                        nearest_dist = distance
                        nearest_position = Position(x, y)
        return nearest_position
    
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