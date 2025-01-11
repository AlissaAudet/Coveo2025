import random
from game_message import *


class Bot:
    tiles = []
    characters = []
    def __init__(self):
        print("Initializing your super mega duper bot")

    def get_next_move(self, game_message: TeamGameState):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        tiles = getattr(Bot, "tiles")
        characters = getattr(Bot, "characters")
        if len(tiles) == 0:
            setattr(Bot, "tiles", game_message.map.tiles)
        if len(characters) == 0:
            setattr(Bot, "characters", game_message.yourCharacters)
        actions = []

        for character in game_message.yourCharacters:
            map_tile = game_message.map.tiles[character.position.x][character.position.y]
            bla = 1
            actions.append(
                random.choice(
                    [
                        MoveUpAction(characterId=character.id),
                        MoveRightAction(characterId=character.id),
                        MoveDownAction(characterId=character.id),
                        MoveLeftAction(characterId=character.id),
                        GrabAction(characterId=character.id),
                        DropAction(characterId=character.id),
                    ]
                )
            )

        # You can clearly do better than the random actions above! Have fun!
        return actions
    
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
