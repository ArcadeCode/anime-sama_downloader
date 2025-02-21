import sys
from collections.abc import Callable
from typing import List, TypeVar

from rich import print

T = TypeVar("T")


def safe_input(
    text: str, transform: Callable[[str], T], exceptions=(ValueError, IndexError)
) -> T:
    while True:
        try:
            print(text, end="")
            output = input()
            return transform(output)
        except exceptions:
            pass


def print_selection(choices: list, print_choices=True) -> None:
    if len(choices) == 0:
        print("[red]No result")
        sys.exit()
    if len(choices) == 1:
        print(f"-> \033[0;34m{choices[0]}")
        return
    if not print_choices:
        return

    for index, choice in enumerate(choices, start=1):
        line_colors = "yellow" if index % 2 == 0 else "white"
        print(
            f"[green][{index:{len(str(len(choices)))}}]",
            f"[{line_colors}]{choice}",
        )


def select_one(choices: list[T], msg="Choose a number", **_) -> T:
    print_selection(choices)
    if len(choices) == 1:
        return choices[0]

    return safe_input(f"{msg}: \033[0;34m", lambda string: choices[int(string) - 1])


def select_range(choices: List[T], msg: str = "Choose a range", print_choices: bool = True) -> List[T]:
    if print_choices:
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice}")

    print(f"\n{msg}")
    selection = input("Enter your choice(s), separated by commas (or '*' to select all): ")

    # If user write '*', select all choices
    if selection.strip() == "*":
        return choices  # Return the entire list

    # Otherwise, we assume the user enters indices separated by hyphens
    selected_indices = []
    for item in selection.split("-"):
        item = item.strip()
        if item.isdigit():
            index = int(item) - 1  # Convertir en index 0-basé
            if 0 <= index < len(choices):
                selected_indices.append(index)
            else:
                print(f"Invalid index: {item}")
        else:
            print(f"Invalid input: {item}")

    # Returns the selected items
    return [choices[i] for i in selected_indices]



def keyboard_inter():
    print("\n[red]Exiting...")
    sys.exit()
