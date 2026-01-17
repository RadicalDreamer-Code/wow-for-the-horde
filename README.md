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
2. Run the script:

```bash
python wow_character_creator.py
```

3. Select option `3` (Get mouse coordinates)
4. Move your mouse over each button you want to click (race, class, accept, etc.)
5. The coordinates will be displayed in real-time
6. Copy the coordinates and update `config.json` as needed

### Creating a Character

Run the script:

```bash
python wow_character_creator.py
```

#### Option 1: Full Creation (With Logout and Login)

1. Start World of Warcraft
2. Select option `1` (With logout and login)
3. Enter the character name when prompted
4. The script will:
   - Reconnect to the server
   - Select realm (Spineshatter)
   - Create the character
   - Automatically retry if Blood Elf is unavailable
   - Schedule system shutdown after 3 AM

#### Option 2: Quick Create (Already at Character Selection)

1. Navigate to the character selection screen in WoW
2. Select option `2` (Try for a quick character create)
3. Enter the character name when prompted
4. The script will:
   - Open the character creator
   - Check if Blood Elf is available
   - Automatically retry if unavailable
   - Create the character with randomized delays

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
- **Randomized delays**: Quick create adds 1-2 second random delays for human-like behavior
- **Automatic retries**: Script continues trying if Blood Elf race is unavailable
- **Configurable pauses**: Adjust timing between actions
- **Creation logging**: All successful creations are logged to `character_creation_log.txt`

## Tips

- Run in windowed or windowed fullscreen mode for best results
- Make sure WoW is visible (not minimized) when running the script
- Test coordinates one at a time using the helper mode
- Adjust `pause_between_actions` if clicks are too fast/slow

## For the Horde! 🔴
