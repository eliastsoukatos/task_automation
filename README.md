# Task Automation GUI

**Task Automation GUI** is a desktop application for building and running simple automation macros. Through an intuitive interface you can record mouse clicks, define waiting times and combine them into repeatable cycles. It is ideal for automating repetitive tasks in marketing, sales or any workflow that requires consistent user interaction.

![screenshot](docs/screenshot_placeholder.png)

## Key Features

- **Point-and-click action builder** – capture screen coordinates and insert sleep steps from the GUI.
- **Cycle management** – save, rename and reuse groups of actions.
- **Looped execution** – run sequences for a configurable number of cycles.
- **Debug mode** – overlay markers show exactly where each click occurs.
- **JSON-based storage** – action cycles are stored in a local JSON file for portability.

## Possible Use Cases

- Creating marketing demos that replay the same steps.
- Automating data entry or simple form submissions.
- Replaying tedious configuration flows in test environments.
- Any scenario where a lightweight macro saves time.

## Tech Stack

- **Python 3**
- **PyQt5** for the graphical user interface
- **pyautogui** for controlling the mouse

## Installation

```bash
pip install -r requirements.txt
python automation_gui.py
```

The application runs on Windows, macOS and Linux where PyQt5 and pyautogui are supported.

## Project Structure

```
automation_gui.py   # main application
requirements.txt    # Python dependencies
LICENSE             # project license (MIT)
docs/               # extended documentation
examples/           # usage examples and snippets
data/               # placeholder for sample datasets
```

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the terms of the MIT License. See [LICENSE](LICENSE) for details.
