# CSC111-Winter-2026-Project-1
For this project, you are to write a small-scale text adventure game that takes place at your campus at the University of Toronto.


##  Overview

The player wakes up in their dorm room on campus and realizes that three important items are missing:

- USB drive (project submission)
- Laptop charger
- Lucky mug

The goal is to **find all three items and return them to the dorm room** before the deadline.

Progression is driven by:
- Exploring locations
- Checking objects
- Remembering clues from messages and memories

---

##  Locations (Current)

- Dorm Room
- Study Lounge
- Friend’s Condo
- Robarts Research Library
- Coffee Shop


---

## Items & Interactions (Implemented)

### Commands currently supported:
- `look` – show full location description
- `inventory` – view items in backpack
- `take <item>` – pick up movable items
- `check <item>` – examine items (both in inventory or at current location)
- `drop <item>` – drop an item at current location
- `log` – show movement history
- `score` – show current score (placeholder)
- `quit` – exit game

---

## Story & Puzzle Mechanics (Partially Implemented)

- The **phone** provides messages and Instagram-style hints
- The **locker** is locked and requires remembering a password
- The **password note** provides a memory hint
- The **photo album** reveals a hidden memory *only after the note is discovered*
- Memory progression is handled using internal flags

---

## Features In Progress

- Unlocking the locker with a password
- Full lucky mug retrieval
- Score calculation when items are returned
- Win condition (all items returned to dorm)


