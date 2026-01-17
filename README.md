# WoW Character Creator Automation

Automates character creation in World of Warcraft by detecting the game window and performing mouse clicks at specific coordinates.

## Setup

1. **Set World of Warcraft resolution to 720x576 in window mode** (required for coordinates to work correctly)

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Getting Coordinates (Setup Mode)

Before creating characters, you need to find the correct coordinates for buttons in WoW:

1. Start World of Warcraft and navigate to the character creation screen
2. Run the script in coordinate helper mode:

```bash
python wow_character_creator.py
```

3. Select option `2` (Get mouse coordinates)
4. Move your mouse over each button you want to click (race, class, accept, etc.)
5. Press `Ctrl+C` when your mouse is positioned correctly
6. Copy the coordinates shown and update `config.json`

### Creating a Character

1. Start World of Warcraft and navigate to the character creation screen
2. Run the script:

```bash
python wow_character_creator.py
```

3. Select option `1` (Create a character)
4. Enter the character name when prompted
5. The script will automatically click through the creation process

## Configuration

Edit `config.json` to customize:

- **window_titles**: Window names to search for
- **pause_between_actions**: Delay between actions (seconds)
- **coordinates**: X/Y positions for each button (relative to window)

### Example Coordinate Configuration

```json
{
  "coordinates": {
    "race_selection": { "x": 100, "y": 200 },
    "class_selection": { "x": 100, "y": 300 }
  }
}
```

## Safety Features

- **Failsafe**: Move mouse to any screen corner to abort
- **5-second delay**: Time to switch to WoW window before execution
- **Configurable pauses**: Adjust timing between actions

## Tips

- Run in windowed or windowed fullscreen mode for best results
- Make sure WoW is visible (not minimized) when running the script
- Test coordinates one at a time using the helper mode
- Adjust `pause_between_actions` if clicks are too fast/slow

## For the Horde! 🔴
