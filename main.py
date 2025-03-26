import json
import models
import game_world
import game_ui
import utils

def run_game():
    with open('game_data.json', 'r') as f:
        data = json.load(f)
        if isinstance(data['world'], str):
            world_data = json.loads(data['world'])
        else:
            world_data = data['world']
        rooms = world_data['rooms']
        connections = world_data['connections']
        original_room_visit_order = world_data.get('original_room_visit_order', [])
        variables = utils.parse_variables(world_data.get('variables', []) )
    
    game = game_world.GameWorld(original_room_visit_order=original_room_visit_order, variables=variables)
    
    for room_data in rooms:
        room = models.Room(room_data["name"], room_data["description"], 
                         room_data["image_prompt"], room_data["canon_event"])
        game.add_room(room)
    
    for conn in connections:
        game.connect_rooms(conn["room1"], conn["room2"], models.Direction(conn["direction"]))
    
    game_ui_instance = game_ui.GameUI(game)
    game_ui_instance.run()


if __name__ == "__main__":
    # utils.generate_game_data()
    run_game()


