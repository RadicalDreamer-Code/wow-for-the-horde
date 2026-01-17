"""
World of Warcraft Character Creator Automation Script
Automates the character creation process by detecting the WoW window
and clicking at specified coordinates.
"""

import json
import random
import time
from datetime import datetime
from typing import Optional, Tuple

import pyautogui
import win32con
import win32gui
from PIL import Image


class WoWCharacterCreator:
    def __init__(self, config_file: str = "config.json"):
        """Initialize the character creator with configuration."""
        self.window_handle = None
        self.window_rect = None
        self.config = self.load_config(config_file)

        # Safety settings
        pyautogui.PAUSE = self.config.get("pause_between_actions", 0.5)
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort

    def load_config(self, config_file: str) -> dict:
        """Load configuration from JSON file."""
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {config_file} not found. Using defaults.")
            return self.get_default_config()

    def get_default_config(self) -> dict:
        """Return default configuration."""
        return {
            "window_titles": ["World of Warcraft"],
            "pause_between_actions": 0.5,
            "coordinates": {
                "reconnect": {"x": 357, "y": 334},
                "realm_selection": {"x": 620, "y": 37},
                "spineshatter_selection": {"x": 206, "y": 163},
                "spineshatter_selection_confirm": {"x": 426, "y": 455},
                "spineshatter_selection_confirm_confirm": {"x": 307, "y": 338},
                "bloodelf_selection": {"x": 137, "y": 266},
                # "bloodelf_selection": {"x": 63, "y": 266},
                "open_create_new_character": {"x": 604, "y": 465},
                "creator_selection_back": {"x": 637, "y": 550},
                "character_selection_back": {"x": 684, "y": 552},
                "class_selection": {"x": 64, "y": 358},
                "accept": {"x": 631, "y": 520},
                "enter_world": {"x": 640, "y": 600},
                "final_confirm": {"x": 311, "y": 403},
            },
        }

    def find_window(self) -> bool:
        """Find the World of Warcraft window."""

        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                for search_title in self.config["window_titles"]:
                    if search_title.lower() in title.lower():
                        windows.append((hwnd, title))
            return True

        windows = []
        win32gui.EnumWindows(callback, windows)

        if not windows:
            print("World of Warcraft window not found!")
            print("Make sure the game is running.")
            return False

        # Use the first matching window
        self.window_handle, window_title = windows[0]
        print(f"Found window: {window_title}")

        # Get window position and size (using client area, not including borders/title)
        self.window_rect = win32gui.GetWindowRect(self.window_handle)

        # Get client rect to calculate offset for title bar and borders
        left, top, right, bottom = self.window_rect
        client_rect = win32gui.GetClientRect(self.window_handle)
        client_point = win32gui.ClientToScreen(self.window_handle, (0, 0))

        # Store the actual client area position
        self.client_left = client_point[0]
        self.client_top = client_point[1]
        self.client_width = client_rect[2]
        self.client_height = client_rect[3]

        print(
            f"Client area: ({self.client_left}, {self.client_top}) Size: {self.client_width}x{self.client_height}"
        )

        return True

    def bring_window_to_front(self):
        """Bring the WoW window to the foreground."""
        if self.window_handle:
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(0.5)
            print("Window brought to front")

    def get_absolute_coords(self, relative_x: int, relative_y: int) -> Tuple[int, int]:
        """Convert window-relative coordinates to absolute screen coordinates."""
        if not self.window_rect:
            raise ValueError("Window not found. Call find_window() first.")

        # Use client area coordinates (excludes title bar and borders)
        abs_x = self.client_left + relative_x
        abs_y = self.client_top + relative_y

        return abs_x, abs_y

    def click_at(
        self, relative_x: int, relative_y: int, clicks: int = 1, delay: float = None
    ):
        """Click at relative coordinates within the window."""
        abs_x, abs_y = self.get_absolute_coords(relative_x, relative_y)

        print(f"Moving to ({relative_x}, {relative_y}) -> Screen ({abs_x}, {abs_y})")
        pyautogui.moveTo(abs_x, abs_y, duration=0.3)

        if delay:
            time.sleep(delay)

        pyautogui.click(clicks=clicks)
        print(f"Clicked at ({relative_x}, {relative_y})")

    def click_coordinate(self, coord_name: str, clicks: int = 1, delay: float = None):
        """Click at a named coordinate from config."""
        if coord_name not in self.config["coordinates"]:
            print(f"Warning: Coordinate '{coord_name}' not found in config")
            return

        coord = self.config["coordinates"][coord_name]
        self.click_at(coord["x"], coord["y"], clicks, delay)

    def type_text(self, text: str, interval: float = 0.1):
        """Type text with a delay between characters."""
        pyautogui.write(text, interval=interval)
        print(f"Typed: {text}")

    def is_icon_clickable(
        self,
        relative_x: int,
        relative_y: int,
        width: int = 20,
        height: int = 20,
        threshold: int = 100,
    ) -> bool:
        """Check if an icon is clickable by detecting if it's grayed out.

        Args:
            relative_x: X coordinate relative to window
            relative_y: Y coordinate relative to window
            width: Width of area to sample
            height: Height of area to sample
            threshold: Color brightness threshold (0-255). Above = clickable, below = grayed out

        Returns:
            True if icon appears clickable (colorful), False if grayed out
        """
        abs_x, abs_y = self.get_absolute_coords(relative_x, relative_y)

        # Capture screenshot of the icon area
        screenshot = pyautogui.screenshot(
            region=(abs_x - width // 2, abs_y - height // 2, width, height)
        )

        # Calculate average saturation (grayed icons have low saturation)
        pixels = list(screenshot.getdata())
        avg_saturation = 0

        for r, g, b in pixels:
            # Calculate saturation: difference between max and min RGB values
            max_val = max(r, g, b)
            min_val = min(r, g, b)
            saturation = max_val - min_val
            avg_saturation += saturation

        avg_saturation = avg_saturation / len(pixels)

        is_clickable = avg_saturation > threshold
        print(
            f"Icon saturation: {avg_saturation:.1f} (threshold: {threshold}) - {'Clickable' if is_clickable else 'Grayed out'}"
        )

        return is_clickable

    def create_character(self, character_name: str):
        """Execute the character creation sequence."""
        # shutdown pc after 3am
        current_time = datetime.now().time()
        if current_time.hour >= 3:
            print("It's past 3 AM, shutting down the PC to save energy.")
            import subprocess

            subprocess.run(["shutdown", "/s", "/t", "60"], check=False)
            print("Shutdown scheduled. Run 'shutdown /a' to abort.")
            return False

        print("\n=== Starting Character Creation ===")
        print("You have 5 seconds to switch to WoW window...")
        time.sleep(5)

        if not self.find_window():
            return False

        self.bring_window_to_front()

        try:
            character_count = 0

            while True:
                character_count += 1
                print(f"\n=== Creating Character #{character_count} ===")

                print("1. Clicking reconnect...")
                self.click_coordinate("reconnect", delay=7)

                print("2. Selecting realm...")
                self.click_coordinate("realm_selection", delay=12)

                print("3. Selecting Spineshatter...")
                self.click_coordinate("spineshatter_selection", delay=7)

                print("4. Confirming Spineshatter...")
                self.click_coordinate("spineshatter_selection_confirm", delay=1)

                print("5. Confirming selection...")
                self.click_coordinate("spineshatter_selection_confirm_confirm", delay=1)

                # add delay to allow realm to load
                time.sleep(17)

                print("6. Checking if Blood Elf is selectable...")
                bloodelf_coord = self.config["coordinates"]["bloodelf_selection"]
                if not self.is_icon_clickable(
                    bloodelf_coord["x"], bloodelf_coord["y"], threshold=30
                ):
                    print("Blood Elf is grayed out - skipping character creation")
                    print("Going back to character selection...")
                    self.click_coordinate("character_selection_back", delay=2)

                    print("7. Going back from creator...")
                    self.click_coordinate("creator_selection_back", delay=2)

                    print("8. Going back again...")
                    self.click_coordinate("character_selection_back", delay=1)

                    print(f"\n=== Character #{character_count} Creation Failed! ===")
                    print("Starting next try in 2 seconds...")
                    continue

                print("Blood Elf is clickable - selecting...")
                self.click_coordinate("bloodelf_selection", delay=12)

                # TODO: Select class
                print("Selecting class...")
                self.click_coordinate("class_selection", delay=2)

                # Type character name
                print(f"9. Typing character name: {character_name}")
                self.type_text(character_name, interval=0.1)
                time.sleep(1)

                print("10. Accepting character creation...")
                self.click_coordinate("accept", delay=5)

                print("11. Final confirmation...")
                self.click_coordinate("final_confirm", delay=10)

                # Save completion log
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_message = f"[{now}] Character created successfully after {character_count} attempt(s)\n"
                with open("character_creation_log.txt", "a") as log_file:
                    log_file.write(log_message)

                # Schedule shutdown in 1 minute
                print("Scheduling system shutdown in 1 minute...")
                import subprocess

                subprocess.run(["shutdown", "/s", "/t", "60"], check=False)
                print("Shutdown scheduled. Run 'shutdown /a' to abort.")

                break

                time.sleep(2)

        except KeyboardInterrupt:
            print(f"\n\nScript interrupted! Created {character_count} character(s).")
            return False
        except Exception as e:
            print(f"\n\nError during creation: {e}")
            return False

    def quick_create_character(self, character_name: str):
        """Execute the character creation sequence."""
        print("\n=== Starting Character Creation ===")
        print("You have 5 seconds to switch to WoW window...")
        time.sleep(5)

        if not self.find_window():
            return False

        self.bring_window_to_front()

        try:
            character_count = 0

            while True:
                character_count += 1
                print(f"\n=== Creating Character #{character_count} ===")

                # add delay to allow realm to load
                time.sleep(2)

                print("1. Clicking to open create new character...")
                self.click_coordinate(
                    "open_create_new_character", delay=1 + random.uniform(1, 2)
                )

                time.sleep(3)

                print("2. Checking if Blood Elf is selectable...")
                bloodelf_coord = self.config["coordinates"]["bloodelf_selection"]
                if not self.is_icon_clickable(
                    bloodelf_coord["x"], bloodelf_coord["y"], threshold=30
                ):
                    print("Blood Elf is grayed out - skipping character creation")
                    print("7. Going back from creator...")
                    self.click_coordinate(
                        "creator_selection_back", delay=1 + random.uniform(1, 2)
                    )

                    # print("8. Going back again...")
                    # self.click_coordinate("character_selection_back", delay=1)

                    print(f"\n=== Character #{character_count} Creation Failed! ===")
                    print("Starting next try in 2 seconds...")
                    continue

                print("Blood Elf is clickable - selecting...")
                self.click_coordinate(
                    "bloodelf_selection", delay=4 + random.uniform(1, 2)
                )

                # TODO: Select class
                print("Selecting class...")
                self.click_coordinate("class_selection", delay=2 + random.uniform(1, 2))

                # Type character name
                print(f"9. Typing character name: {character_name}")
                self.type_text(character_name, interval=0.1)
                time.sleep(1)

                print("10. Accepting character creation...")
                self.click_coordinate("accept", delay=2 + random.uniform(1, 2))

                print("11. Final confirmation...")
                self.click_coordinate("final_confirm", delay=5 + random.uniform(1, 2))

                # Save completion log
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_message = f"[{now}] Character created successfully after {character_count} attempt(s)\n"
                with open("character_creation_log.txt", "a") as log_file:
                    log_file.write(log_message)

                # Schedule shutdown in 1 minute
                # print("Scheduling system shutdown in 1 minute...")
                # import subprocess

                # subprocess.run(["shutdown", "/s", "/t", "60"], check=False)
                # print("Shutdown scheduled. Run 'shutdown /a' to abort.")

                break

                time.sleep(2)

        except KeyboardInterrupt:
            print(f"\n\nScript interrupted! Created {character_count} character(s).")
            return False
        except Exception as e:
            print(f"\n\nError during creation: {e}")
            return False

    def get_mouse_position(self):
        """Helper function to show current mouse position when inside the WoW window."""
        if not self.find_window():
            return

        print("\nShowing mouse coordinates when inside WoW window.")
        print("Press Ctrl+C to exit.\n")

        try:
            while True:
                x, y = pyautogui.position()

                # Calculate relative position to client area
                rel_x = x - self.client_left
                rel_y = y - self.client_top

                # Only show coordinates if mouse is inside the client area
                if 0 <= rel_x <= self.client_width and 0 <= rel_y <= self.client_height:
                    print(
                        f"\rx={rel_x}, y={rel_y} [{self.client_width}x{self.client_height}]    ",
                        end="",
                    )
                else:
                    print(
                        f"\rOutside: x={rel_x}, y={rel_y} (bounds: {self.client_width}x{self.client_height})    ",
                        end="",
                    )

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n\nHelper mode exited.")


def main():
    """Main execution function."""
    print("=== WoW Character Creator ===\n")
    print("What would you like to do?")
    print("1. With logout and login")
    print("2. Try for a quick character create")
    print("3. Get mouse coordinates (helper mode)")

    choice = input("\nEnter choice (1, 2, or 3): ").strip()
    creator = WoWCharacterCreator()

    if choice == "1":
        char_name = input("Enter character name: ").strip()
        if not char_name:
            print("Character name required!")
            return

        creator.create_character(char_name)

    elif choice == "2":
        char_name = input("Enter character name: ").strip()
        if not char_name:
            print("Character name required!")
            return
        creator.quick_create_character(char_name)

    elif choice == "3":
        creator.get_mouse_position()

    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
