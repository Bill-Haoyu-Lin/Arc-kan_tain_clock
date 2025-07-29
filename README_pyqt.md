# Arc PyQt Version

This is a PyQt5 rewrite of the original CustomTkinter Arc application. The application maintains the same functionality as the original but uses PyQt5 for the GUI framework.

## Features

- **Kantai Clock**: Start/stop character voice announcements with hourly chimes
- **Character Rotation**: Cycle through different characters (Верный, Warspite, Kawakaze, Yura, Ark_Royal)
- **Anime Schedule**: Display today's anime and upcoming anime from MongoDB database
- **Web Integration**: Open anime search pages in browser
- **Dark/Light Theme**: Toggle between appearance modes
- **Real-time Clock**: Display current time with updates

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements_pyqt.txt
```

2. Ensure you have a `config.json` file with your MongoDB URI:
```json
{
    "mongodb_uri": "your_mongodb_connection_string"
}
```

3. Make sure you have the required directories and files:
   - `Characters/` - Character images
   - `Sounds/` - Audio files for characters
   - `test_images/` - UI images

## Usage

Run the application:
```bash
python Main_pyqt.py
```

## Key Changes from CustomTkinter Version

### GUI Framework
- **CustomTkinter** → **PyQt5**: Complete rewrite using PyQt5 widgets
- **Layout System**: Uses QVBoxLayout, QHBoxLayout, and QGridLayout instead of Tkinter's grid
- **Styling**: CSS-like stylesheets instead of CustomTkinter's built-in theming

### Widget Equivalents
- `customtkinter.CTk` → `QMainWindow`
- `customtkinter.CTkFrame` → `QFrame`
- `customtkinter.CTkButton` → `QPushButton`
- `customtkinter.CTkLabel` → `QLabel`
- `customtkinter.CTkScrollableFrame` → `QScrollArea`
- `customtkinter.CTkOptionMenu` → `QComboBox`

### Image Handling
- `customtkinter.CTkImage` → `QPixmap`
- Image scaling and display handled through QPixmap methods

### Web Integration
- **CEF Python** → **PyQtWebEngine**: Replaced CEF browser with QWebEngineView
- Web content now displayed within the application using Qt's web engine

### Threading
- Uses QThread for database operations instead of Python's threading module
- Signal/slot mechanism for thread communication

### Timer
- `after()` method → `QTimer` for periodic updates

## Architecture

### Main Components
1. **App Class**: Main application window inheriting from QMainWindow
2. **AnimeThread**: QThread subclass for loading anime data from MongoDB
3. **Navigation**: Sidebar with navigation buttons
4. **Content Pages**: Home, Playlist, and Add Person pages

### Data Flow
1. Application starts and loads MongoDB connection
2. AnimeThread loads anime data asynchronously
3. UI updates when data is received via signals
4. Timer updates clock and checks for hourly announcements

## Benefits of PyQt5

- **Better Performance**: More efficient rendering and event handling
- **Modern Look**: Native appearance on all platforms
- **Rich Widget Set**: More comprehensive widget library
- **Better Documentation**: Extensive Qt documentation and examples
- **Cross-platform**: Consistent behavior across Windows, macOS, and Linux

## Dependencies

- **PyQt5**: Main GUI framework
- **PyQtWebEngine**: Web content display
- **python-vlc**: Audio playback for character voices
- **requests**: HTTP requests for image loading
- **pymongo**: MongoDB database connectivity
- **pytz**: Timezone handling for anime schedules
- **Pillow**: Image processing (if needed for additional features)

## File Structure

```
Arc-kan_tain_clock/
├── Main_pyqt.py          # Main PyQt application
├── requirements_pyqt.txt  # PyQt dependencies
├── README_pyqt.md        # This file
├── Characters/           # Character images
├── Sounds/              # Audio files
├── test_images/         # UI images
└── config.json          # MongoDB configuration
```

## Troubleshooting

### Common Issues

1. **PyQtWebEngine not found**: Install with `pip install PyQtWebEngine`
2. **VLC not working**: Ensure VLC media player is installed on your system
3. **MongoDB connection**: Check your `config.json` file and network connectivity
4. **Missing images**: Ensure all image files are in the correct directories

### Platform-Specific Notes

- **Windows**: May need to install Visual C++ redistributables
- **macOS**: PyQt5 works well with Homebrew Python
- **Linux**: May need additional system packages for PyQtWebEngine

## Migration Notes

If migrating from the CustomTkinter version:

1. Replace `Main.py` with `Main_pyqt.py`
2. Update dependencies using `requirements_pyqt.txt`
3. The same data files (images, sounds, config) can be used
4. MongoDB schema remains the same
5. Character and anime functionality is preserved 