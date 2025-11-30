"""
Simple Mouse Sensitivity Converter

Concepts shown:
- try / except   (error handling)
- Class (OOP)    (Game, Profile)
- Decorator      (handle_errors)
- Context manager (ProfileStore)
- Generator      (profiles_for_player)
- String encoding (UTF-8 JSON file)
"""

import json
from dataclasses import dataclass, asdict
from functools import wraps
from typing import List, Iterable


# 1. OOP: Game and Profile

@dataclass
class Game:
    name: str
    cm_per_360_at_sens1: float  # how many cm for 360° at sens 1.0

    def cm_per_360(self, sensitivity: float) -> float:
        if sensitivity <= 0:
            raise ValueError("Sensitivity must be positive.")
        return self.cm_per_360_at_sens1 / sensitivity

    def sens_for_cm360(self, cm360: float) -> float:
        if cm360 <= 0:
            raise ValueError("cm/360 must be positive.")
        return self.cm_per_360_at_sens1 / cm360


@dataclass
class Profile:
    player: str
    game: str
    sensitivity: float


# Game list with example values
GAMES = {
    "cs2": Game("CS2", cm_per_360_at_sens1=50.0),
    "valorant": Game("Valorant", cm_per_360_at_sens1=52.0),
    "apex": Game("Apex Legends", cm_per_360_at_sens1=48.0),
    "overwatch": Game("Overwatch", cm_per_360_at_sens1=42.0),
}


def get_game(key: str) -> Game:
    key = key.strip().lower()
    if key not in GAMES:
        raise KeyError(f"{key} (valid: cs2, valorant, apex, overwatch)")
    return GAMES[key]


# 2. Decorator: handle_errors

def handle_errors(fn):
    """Decorator to catch common input errors."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValueError as e:
            print("[Input error]", e)
        except KeyError as e:
            print("[Game error] Unknown game:", e)
        except Exception as e:
            print("[Unexpected error]", e)

    return wrapper


# 3. Context Manager: ProfileStore
#    + UTF-8 string encoding

class ProfileStore:
    """
    Very simple context manager that:
    - loads profiles from a JSON file on enter
    - saves profiles back to the file on normal exit

    Demonstrates:
    - context manager (__enter__, __exit__)
    - string encoding (UTF-8)
    """

    def __init__(self, path: str):
        self.path = path
        self.profiles: List[Profile] = []

    def __enter__(self) -> List[Profile]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.profiles = [Profile(**item) for item in data]
        except FileNotFoundError:
            self.profiles = []
        except json.JSONDecodeError:
            print("Warning: profiles file is corrupted. Starting empty.")
            self.profiles = []
        return self.profiles

    def __exit__(self, exc_type, exc, tb) -> None:
        # Save when there is no error
        if exc_type is None:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(
                    [asdict(p) for p in self.profiles],
                    f,
                    indent=2,
                    ensure_ascii=False,  
                )
        else:
            print("An error occurred; profiles were NOT saved automatically.")
        

# 4. Generator: profiles_for_player

def profiles_for_player(player: str, profiles: List[Profile]) -> Iterable[Profile]:
    """
    Generator that yields all profiles for a given player.
    Shows how generators work with 'yield'.
    """
    player_norm = player.strip().lower()
    for p in profiles:
        if p.player.lower() == player_norm:
            yield p


# 5. Actions (using decorator)

@handle_errors
def convert_and_maybe_save(profiles: List[Profile]) -> None:
    print("\nAvailable games: cs2, valorant, apex, overwatch\n")

    player = input("Player name: ").strip()
    from_key = input("Convert FROM (cs2/valorant/apex/overwatch): ").strip()
    to_key = input("Convert TO   (cs2/valorant/apex/overwatch): ").strip()

    from_game = get_game(from_key)
    to_game = get_game(to_key)

    sens_str = input(f"Sensitivity in {from_game.name}: ").strip()
    sensitivity = float(sens_str)  # may raise ValueError

    # Convert sensitivity
    cm360 = from_game.cm_per_360(sensitivity)
    to_sens = to_game.sens_for_cm360(cm360)

    print(f"\n{from_game.name} sens {sensitivity} → {cm360:.2f} cm/360")
    print(f"Equivalent in {to_game.name}: {to_sens:.4f}\n")

    save = input("Save this profile? (yes/no): ").strip().lower()
    if save == "yes":
        # Add or update profile
        for p in profiles:
            if p.player == player and p.game == to_game.name:
                p.sensitivity = to_sens
                break
        else:
            profiles.append(Profile(player=player, game=to_game.name, sensitivity=to_sens))
        print("Profile saved.\n")


@handle_errors
def list_player_profiles(profiles: List[Profile]) -> None:
    player = input("Player name to list: ").strip()
    found_any = False
    print()
    for p in profiles_for_player(player, profiles):  # using generator
        print(f"- {p.player} | {p.game}: {p.sensitivity}")
        found_any = True

    if not found_any:
        print("No profiles found for that player.\n")
    else:
        print()


# 6. Main loop (with basic try/except)

def main() -> None:
    # Context manager handles loading/saving profiles
    with ProfileStore("profiles_simple.json") as profiles:
        while True:
            print(
                """
==== Simple Mouse Sens Converter ====
1) Convert sensitivity and optionally save
2) List profiles for a player
0) Exit
"""
            )
            choice = input("Choose an option: ").strip()

            # try/except for menu number
            try:
                choice_num = int(choice)
            except ValueError:
                print("Please enter a number (0, 1, or 2).\n")
                continue

            if choice_num == 0:
                print("Goodbye!")
                break
            elif choice_num == 1:
                convert_and_maybe_save(profiles)
            elif choice_num == 2:
                list_player_profiles(profiles)
            else:
                print("Unknown option.\n")


if __name__ == "__main__":
    main()