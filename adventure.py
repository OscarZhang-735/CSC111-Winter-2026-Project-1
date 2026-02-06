"""CSC111 Project 1: Text Adventure Game - Game Manager

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Project 1. Please consult
the project handout for instructions and details.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2026 CSC111 Teaching Team
"""
from __future__ import annotations
import json
from typing import Optional

from game_entities import Location, Item
from event_logger import Event, EventList


# Note: You may add in other import statements here as needed

# Note: You may add helper functions, classes, etc. below as needed


class AdventureGame:
    """A text adventure game class storing all location, item and map data.

    Instance Attributes:
        - current_location_id: The id of the player's current location.
        - ongoing: Whether the game is still running (False means the game ends).


    Representation Invariants:
        - self.current_location_id in self._locations
        - all(loc_id == self._locations[loc_id].id_num for loc_id in self._locations)

    """

    # Private Instance Attributes (do NOT remove these two attributes):
    #   - _locations: a mapping from location id to Location object.
    #                       This represents all the locations in the game.
    #   - _items: a list of Item objects, representing all items in the game.

    _locations: dict[int, Location]
    _items: list[Item]
    current_location_id: int  # Suggested attribute, can be removed
    ongoing: bool  # Suggested attribute, can be removed
    inventory: list[Item]
    flags: set[str]
    score: int

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        """
        Initialize a new text adventure game, based on the data in the given file, setting starting location of game
        at the given initial location ID.
        (note: you are allowed to modify the format of the file as you see fit)

        Preconditions:
        - game_data_file is the filename of a valid game data JSON file
        """

        # NOTES:
        # You may add parameters/attributes/methods to this class as you see fit.

        # Requirements:
        # 1. Make sure the Location class is used to represent each location.
        # 2. Make sure the Item class is used to represent each item.

        # Suggested helper method (you can remove and load these differently if you wish to do so):
        self._locations, self._items = self._load_game_data(game_data_file)

        # Suggested attributes (you can remove and track these differently if you wish to do so):
        self.current_location_id = initial_location_id  # game begins at this location
        self.ongoing = True  # whether the game is ongoing

        self.inventory: list = []
        self.flags: set = set()
        self.score: int = 0
        self.move: int = 0
        self.targets: list = ["lucky mug", "usb drive", "laptop charger"]
        self.flags.add("none")

    @staticmethod
    def _load_game_data(filename: str) -> tuple[dict[int, Location], list[Item]]:
        """Load locations and items from a JSON file with the given filename and
        return a tuple consisting of (1) a dictionary of locations mapping each game location's ID to a Location object,
        and (2) a list of all Item objects."""

        with open(filename, 'r') as f:
            data = json.load(f)  # This loads all the data from the JSON file

        locations = {}
        for loc_data in data['locations']:  # Go through each element associated with the 'locations' key in the file
            location_obj = Location(loc_data['id'], loc_data['brief_description'], loc_data['long_description'],
                                    loc_data['available_commands'], loc_data['items'])
            locations[loc_data['id']] = location_obj

        items = []
        for item_data in data['items']:
            item_obj = Item(
                item_data['name'],
                item_data['description'],
                item_data['fixed'],
                item_data['reveals_flag']
            )
            items.append(item_obj)

        return locations, items

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the current location.
        """

        if loc_id is None:
            return self.get_current_location()
        else:
            return self._locations[loc_id]

    def get_item_by_name(self, name: str) -> Optional[Item]:
        """Return the Item with the given name, or None if not found."""
        for it in self._items:
            if it.name == name:
                return it
        return None

    def get_current_location(self) -> Location:
        """Return the current Location."""
        return self._locations[self.current_location_id]

    def has_item(self, name: str) -> bool:
        """Return whether the player currently has an item with the given name."""
        return any(it.name == name for it in self.inventory)

    def display_inventory(self) -> None:
        """Display the items in the inventory."""
        if not self.inventory:
            print("Your inventory is empty.")
        else:
            print("You are carrying:")
            for it in self.inventory:
                print("-", it.name)

    def take_item(self, item_name: str) -> None:
        """Take an item by name from the inventory or current location."""
        location = self.get_current_location()
        if item_name in location.items:
            item = self.get_item_by_name(item_name)
            if item is None:
                print("That item does not exist.")
            elif item.fixed:
                print("You can't take that.")
            else:
                location.items.remove(item_name)
                self.inventory.append(item)
                print(f"You picked up the {item_name}.")
        else:
            print("That item is not here.")

    def check_item(self, item_name: str) -> None:
        """Check the information of an item by name from the inventory or current location."""
        location = self.get_current_location()
        item = None
        for it in self.inventory:
            if it.name == item_name:
                item = it
                break
        if item is None:
            print("It's not in your inventory.")
            if item_name in location.items:
                item = self.get_item_by_name(item_name)
            else:
                print("You don't see the item here.")
                return

        if item is not None:
            print(item.description)
            # Special items
            if item.name == "locker":
                if "locker_opened" in self.flags:
                    print("The locker has already been opened.")
                elif "forgot_password" not in self.flags:
                    print("You try to remember the password... but your mind goes blank.")
                    print("You realize you must have written it down somewhere....Under the friend's carpet?")
                    self.flags.add("forgot_password")
                    self.score += 10
                else:
                    self.flags.add("locker_opened")
                    print("The locker is opened and the lucky mug is available to be picked up at this location.")
                    if "lucky mug" not in location.items:
                        location.items.append("lucky mug")
                        self.score += 10

            elif item.name == "password note":
                if "forgot_password" in self.flags and "saw_password_hint" not in self.flags:
                    self.score += 10
                    self.flags.add("saw_password_hint")
                    print("Something clicks. This must be the password hint.")

            elif item.name == "photo album":
                if "saw_password_hint" in self.flags and "forgot_password" in self.flags and "knows_password" not in self.flags:
                    self.score += 10
                    self.flags.add("knows_password")
                    print("You flip through the album carefully.")
                    print("You find a photo of you with your mom and dad in front of the University of Toronto gate.")
                    print("It was your first time here. Little you made a wish to study here one day.")
                    print("You gently take the photo out. On the back, it says a 2009-08-20")

            elif item.name == "phone":
                if "read_phone" not in self.flags:
                    self.flags.add("read_phone")
                    self.score += 10

    def display_pickup_items(self) -> None:
        """Display all items which are available to be picked up at current location."""
        location = self.get_current_location()
        pickup_items = []
        print("You see the following items:")
        for item_name in location.items:
            item = self.get_item_by_name(item_name)
            if item is not None and item.reveals_flag in self.flags:
                pickup_items.append(item_name)
                print("-", item_name)
        if not pickup_items:
            print("You can't find any item here.")

    def drop_item(self, item_name: str) -> None:
        """Drop an item by name at current location."""
        location = self.get_current_location()
        drop_item = None
        for it in self.inventory:
            if it.name == item_name:
                drop_item = it
                break

        if drop_item is None:
            print("You are not carrying that.")
        else:
            self.inventory.remove(drop_item)
            location.items.append(drop_item.name)
            print(f"You dropped the {item_name} here.")
            if item_name in self.targets and self.current_location_id == 1:
                print(f"You successfully dropped an target item <{item_name}> here.")
                self.score += 30  # 20 pts for dropping target items
                self.targets.remove(item_name)
                self.get_item_by_name(item_name).fixed = True

    def save_game(self) -> None:
        """Save the current game state to a file. Log will not be saved."""
        with open("save.json", "w") as f:
            data = {
                "current_location_id": self.current_location_id,
                "inventory": [item.name for item in self.inventory],
                "score": self.score,
                "flags": list(self.flags)
            }
            json.dump(data, f)

    def read_game(self) -> None:
        """Read saved game state from a file."""
        with open("save.json", 'r') as f:
            data = json.load(f)

        self.current_location_id = int(data["current_location_id"])
        self.score = int(data["score"])
        self.flags = set(data["flags"])

        self.inventory = []
        for name in data["inventory"]:
            item = self.get_item_by_name(name)
            if item is not None:
                self.inventory.append(item)


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    #
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    # })
    game_log = EventList()  # This is REQUIRED as one of the baseline requirements
    game = AdventureGame('game_data.json', 1)  # load data, setting initial location ID to 1
    try:
        game.read_game()
    except FileNotFoundError:
        pass
    menu = ["look", "inventory", "score", "log", "quit"]  # Regular menu options available at each location
    choice = None
    print("""
    Welcome to the Text Adventure Game!

    Your goal is to find the missing items and return them to your dorm room
    before you run out of 20 moves.

    How to play:
    - Move between locations using commands like:
      go north, go south, go east, go west
    - Interact with items using:
      check <item>, take <item>, drop <item>
    - View your inventory with:
      inventory
    - Check your current score with:
      score
    - Review past actions with:
      log
    - Quit the game at any time with:
      quit

    Hints:
    - Some items are hidden and only appear after you discover clues.
    - Checking objects may unlock new information or progress the story.
    - Returning important items to your dorm increases your score.

    Good luck!
    ==================================
    """)

    # Note: You may modify the code below as needed; the following starter code is just a suggestion
    while game.ongoing:
        # Note: If the loop body is getting too long, you should split the body up into helper functions
        # for better organization. Part of your mark will be based on how well-organized your code is.

        curr_location = game.get_location()

        if not curr_location.visited:
            print(f"LOCATION {curr_location.id_num}:\n{curr_location.long_description}")
            curr_location.visited = True
        else:
            print(f"LOCATION {curr_location.id_num}:\n{curr_location.brief_description}")

        game.display_pickup_items()
        print("What to do? Choose from: look, inventory, take <item>, check <item>, drop, score, log, quit")
        print("At this location, you can also:")
        for action in curr_location.available_commands:
            print("-", action)

        # Validate choice
        choice = input("\nEnter action: ").lower().strip()
        while choice not in curr_location.available_commands and choice not in menu and not choice.startswith(
                "take ") and not choice.startswith("check ") and not choice.startswith("drop "):
            print("That was an invalid option; try again.")
            choice = input("\nEnter action: ").lower().strip()
        print("=====================")
        print("You decided to:", choice)

        if choice not in curr_location.available_commands:
            # Choices don't change location
            if choice == "log":
                # Display all commands you have input.
                game_log.display_events()

            elif choice == "inventory":
                game.display_inventory()

            elif choice == "score":
                print("Current score:", game.score)

            elif choice == "look":
                # Check the long description of current location.
                print(curr_location.long_description)
                curr_location.visited = True

            elif choice == "quit":
                game.save_game()
                print("You save and quit the game.")
                game.ongoing = False

            elif choice.startswith("take "):
                game.take_item(choice[5:])

            elif choice.startswith("check "):
                game.check_item(choice[6:].strip())

            elif choice.startswith("drop "):
                game.drop_item(choice[5:].strip())

        else:
            # Choices change location
            game.move += 1
            result = curr_location.available_commands[choice]
            game.current_location_id = result
            game.score += 5

        # Generate new event (record current location)
        curr_location = game.get_current_location()
        event_desc = f"LOCATION: {curr_location.id_num}\nCommand: {choice}"
        event = Event(curr_location.id_num, event_desc)
        game_log.add_event(event, choice)

        # Win condition
        if not game.targets:
            print("You win.")
            print("Score:", game.score)
            print("Choices made:")
            game_log.display_events()
            game.ongoing = False

        # Check max move (Lose condition)
        if game.move >= 20:
            print("You lost.")
            print("Score:", game.score)
            print("Choices made:")
            game_log.display_events()
            game.ongoing = False
    print("-----------------------------------------------------------")
