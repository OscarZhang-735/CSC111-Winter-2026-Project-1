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

        self.inventory = []
        self.flags = set()
        self.score = 0

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
                item_data['start_position'],
                item_data['target_position'],
                item_data['target_points'],
                item_data.get('fixed', False),
                item_data.get('locked', False),
                item_data.get('messages', None),
                item_data.get('reveals_flag', None)
            )
            items.append(item_obj)

        return locations, items

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the current location.
        """

        if loc_id is None:
            return self._locations[self.current_location_id]
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


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    # })

    game_log = EventList()  # This is REQUIRED as one of the baseline requirements
    game = AdventureGame('game_data.json', 1)  # load data, setting initial location ID to 1
    menu = ["look", "inventory", "score", "log", "quit"]  # Regular menu options available at each location
    choice = None

    # Note: You may modify the code below as needed; the following starter code is just a suggestion
    while game.ongoing:
        # Note: If the loop body is getting too long, you should split the body up into helper functions
        # for better organization. Part of your mark will be based on how well-organized your code is.

        location = game.get_location()

        # Add new Event to game log (record current location)
        event = Event(location.id_num, location.brief_description)
        game_log.add_event(event, choice)

        if not location.visited:
            print(location.long_description)
            location.visited = True
        else:
            print(location.brief_description)


        # 显示可拿取/查看物品
        pickup_items = []
        for item_name in location.items:
            item = game.get_item_by_name(item_name)
            if item is not None and not item.fixed:
                pickup_items.append(item_name)

        if pickup_items:
            print("You see the following items:")
            for name in pickup_items:
                print("-", name)

        # Display possible actions at this location
        print("What to do? Choose from: look, inventory, take <item>, check<item>, score, log, quit")

        print("At this location, you can also:")
        for action in location.available_commands:
            print("-", action)

        # Validate choice
        choice = input("\nEnter action: ").lower().strip()
        while choice not in location.available_commands and choice not in menu and not choice.startswith("take ") and not choice.startswith("check ") and not choice.startswith("drop "):   #这里我最后加了检查take check drop 不知道可不可以  原版是 while choice not in location.available_commands and choice not in menu:

            print("That was an invalid option; try again.")
            choice = input("\nEnter action: ").lower().strip()

        print("========")
        print("You decided to:", choice)

        if choice in menu:
            if choice == "log":
                game_log.display_events()
            # ENTER YOUR CODE BELOW to handle other menu commands (remember to use helper functions as appropriate)
            elif choice == "inventory":
                if not game.inventory:
                    print("Your inventory is empty.")
                else:
                    print("You are carrying:")
                    for it in game.inventory:
                        print("-", it.name)
                    print("! You can:")
                    print("- check <item>")
                    print("- drop <item>")

            elif choice == "score":
                print("Current score:", game.score)

            elif choice == "look":
                print(location.long_description)
                location.visited = True

            elif choice == "quit":
                print("You quit the game.")
                game.ongoing = False

        elif choice.startswith("take "):
            item_name = choice[5:]
            if item_name in location.items:
                item = game.get_item_by_name(item_name)
                if item is None:
                    print("That item does not exist.")
                elif item.fixed:
                    print("You can't take that.")
                elif item.locked:
                    print("It's locked.")
                else:
                    location.items.remove(item_name)
                    game.inventory.append(item)
                    print(f"You picked up the {item_name}.")
            else:
                print("That item is not here.")

        elif choice.startswith("check "):  # 查看物品
            item_name = choice[6:].strip()
            # 背包
            item = None
            for it in game.inventory:
                if it.name == item_name:
                    item = it
                    break
            # 2) 背包里没有 检查当前地点是否有
            if item is None:
                if item_name in location.items:
                    item = game.get_item_by_name(item_name)
                else:
                    print("You don't see that here.")
                    item = None
            if item is None:
                pass
            elif item.name == "locker":
                print(item.description)
                print("You try to remember the password... but your mind goes blank.")

                if "forgot_password" not in game.flags:
                    game.flags.add("forgot_password")
                    print("You realize you must have written it down somewhere....Under the friend's carpet?")

                    note = game.get_item_by_name("password note")
                    if note is not None:
                        note.fixed = False

            elif item.name == "password note":
                print(item.description)

                if "forgot_password" in game.flags:
                    if "saw_password_hint" not in game.flags:
                        game.flags.add("saw_password_hint")
                        print("Something clicks. This must be the password hint.")

            elif item.name == "photo album":   # 是否找到密码
                if "saw_password_hint" not in game.flags:
                    # 没看过纸条：显示普通描述
                    print(item.description)
                else:
                    # 看过纸条
                    print("You flip through the album carefully.")
                    print("You find a photo of you with your mom and dad in front of the University of Toronto gate.")
                    print("It was your first time here. Little you made a wish to study here one day.")
                    print("You gently take the photo out. On the back, it says: 2009-08-20.")
                    if "knows_password" not in game.flags:
                        game.flags.add("knows_password")
                        print("\nYou suddenly remember the locker password.")
            else:
                # 描述
                print(item.description)
                # 显示手机信息
                if hasattr(item, "messages") and item.messages:
                    print("\nYou see the following:")
                    for msg in item.messages:
                        print("-", msg)
                # 解锁 flag
                if hasattr(item, "reveals_flag") and item.reveals_flag:
                    if item.reveals_flag not in game.flags:
                        game.flags.add(item.reveals_flag)
                        print("You feel like you learned something important.")

        elif choice.startswith("drop "):
            item_name = choice[5:].strip()

            drop_item = None
            for it in game.inventory:
                if it.name == item_name:
                    drop_item = it
                    break

            if drop_item is None:
                print("You are not carrying that.")
            else:
                game.inventory.remove(drop_item)
                location.items.append(drop_item.name)
                print(f"You dropped the {item_name} here.")

        else:
            # Handle non-menu actions
            result = location.available_commands[choice]
            game.current_location_id = result

            # TODO: Add in code to deal with actions which do not change the location (e.g. taking or using an item)
            # TODO: Add in code to deal with special locations (e.g. puzzles) as needed for your game


# move, win condition, deposite还没写
