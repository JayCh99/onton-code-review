import os
import hashlib
from openai import OpenAI
from io import BytesIO
from typing import Dict, List, Optional, Tuple
from models import Action, Actions, Room, Direction, Event
from utils import generate_actions, generate_non_canon_event
from dotenv import load_dotenv

load_dotenv()

class GameWorld:
    """
    Contains game state for an instance of the game.
    """
    
    def __init__(self, original_room_visit_order: List[str] = None, variables: str = ""):
        """
        Initialize the game world based on the original room visit order
        and the variables.
        """
        self.rooms: Dict[str, Room] = {}
        self.current_room: Optional[Room] = None
        self.original_room_visit_order = original_room_visit_order or []
        self.openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        
        self.current_event: Optional[Event] = None
        self.visited_rooms = []
        self.seen_events = []
        self.variables = variables
        self.actions: Optional[Actions] = None

    def is_canon_route(self) -> bool:
        """ 
        Check if the current room visit order is the canon route. 
        """
        return self.visited_rooms == self.original_room_visit_order[:min(len(self.original_room_visit_order), len(self.visited_rooms))]

    def add_room(self, room: Room):
        """
        Add a room to the game world.
        """
        self.rooms[room.name] = room
        if not self.current_room:
            self.visited_rooms.append(room.name)
            self.current_room = room
            self.current_event = Event(event=room.canon_event, is_canon=True)
            self.generate_actions()

    def connect_rooms(self, room1_name: str, room2_name: str, direction: Direction):
        """
        Connect two rooms in the game world in the given direction.
        """
        if room1_name not in self.rooms or room2_name not in self.rooms:
            return
            
        opposite = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST
        }
        room1 = self.rooms[room1_name]
        room2 = self.rooms[room2_name]
        room1.connections[direction] = room2
        # room2.connections[opposite[direction]] = room1

    def generate_room_image(self, room: Room):
        """
        Generate an image for a room based on its description and image prompt.
        """
        try:
            # Create hash from room properties
            room_hash = hashlib.sha256(
                f"{room.name}{room.description}{room.image_prompt}".encode()
            ).hexdigest()
            
            # Check if image already exists
            image_path = f"room_images/{room_hash}.png"
            if os.path.exists(image_path):
                room.image_path = image_path
                return image_path
            
            # Generate new image if it doesn't exist
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=room.image_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            # Download the image
            image_url = response.data[0].url
            response = requests.get(image_url)
            img_data = BytesIO(response.content)
            
            # Save the image using hash
            os.makedirs("room_images", exist_ok=True)
            with open(image_path, "wb") as f:
                f.write(img_data.getbuffer())
            
            room.image_path = image_path
            return image_path
        except Exception as e:
            print(f"Error generating image for room {room.name}: {e}")
            return None
    
    def get_event(self, room: Room) -> Tuple[str, bool]:
        """
        Get the event for a room based on previous events
        """
        if self.is_canon_route():
            return room.canon_event, True
        else:
            return generate_non_canon_event(room, self.seen_events), False
    
    
    def generate_actions(self) -> None:
        """
        Generate the actions for the current room based on the current event
        and the variables.
        """
        self.actions = generate_actions(self.current_room, self.current_event, self.variables)
    
    def update_variables(self, action: Action):
        """
        Update the variables based on an action.
        """
        for variable in action.changed_variables:
            if variable in self.variables:
                print(f"Updating {variable}: {self.variables[variable]} -> {action.changed_variables[variable]}")
                self.variables[variable] = action.changed_variables[variable]

    def has_valid_variables(self, action: Action) -> bool:
        """
        Check if the variables changed by an action are valid.
        """
        return any(var in self.variables for var in action.changed_variables.keys())



