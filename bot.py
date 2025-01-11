import random
from game_message import *
import heapq

class Bot:
    def __init__(self):
        print("Initializing your super mega duper bot")

    def get_next_move(self, game_message: TeamGameState):
        actions = []

        for character in game_message.yourCharacters:
            if not character.alive:
                actions.append(MoveToAction(characterId=character.id, position=character.position))
                continue

            target = self.find_nearest_safe_item(character, game_message)
            if target:
                path = self.a_star(character.position, target.position, game_message.map, game_message.otherCharacters)
                if path and len(path) > 1:
                    next_step = path[1]
                    if self.is_valid_position(next_step, game_message.map):
                        actions.append(self.get_move_action(character, next_step))
                    else:
                        print(f"Next step ({next_step.x}, {next_step.y}) is invalid, moving randomly.")
                        actions.append(self.get_random_move(character))
                else:
                    print(f"No valid path found for character {character.id}, moving randomly.")
                    actions.append(self.get_random_move(character))
            else:
                print(f"No target found for character {character.id}, moving randomly.")
                actions.append(self.get_random_move(character))

        return actions

    def find_nearest_safe_item(self, character, game_message):
        items = [item for item in game_message.items if item.type.startswith("blitzium")]
        if not items:
            return None
        return min(items, key=lambda item: self.manhattan_distance(character.position, item.position))

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

    def is_valid_position(self, pos, game_map):
        if not (0 <= pos.x < game_map.width and 0 <= pos.y < game_map.height):
            return False
        if game_map.tiles[pos.y][pos.x] == TileType.WALL:
            return False
        return True

    def a_star(self, start, goal, game_map, enemies):
        def heuristic(pos1, pos2):
            return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

        def is_valid(pos, game_map):
            if not (0 <= pos.x < game_map.width and 0 <= pos.y < game_map.height):
                return False
            if game_map.tiles[pos.y][pos.x] == TileType.WALL:
                return False
            if any(enemy.position.x == pos.x and enemy.position.y == pos.y for enemy in enemies if enemy.alive):
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
                if not is_valid(neighbor, game_map):
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

    def get_neighbors(self, pos: Position, grid):
        height = len(grid)
        width = len(grid[0]) if height > 0 else 0
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbors = []
        for dx, dy in directions:
            nx, ny = pos.x + dx, pos.y + dy
            if 0 <= ny < height and 0 <= nx < width:
                if grid[ny][nx] == 0:
                    neighbors.append(Position(x=nx, y=ny))
        return neighbors
