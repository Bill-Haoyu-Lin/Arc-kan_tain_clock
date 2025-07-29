import sys
import os
import datetime
import requests
import json
import pytz
import vlc
from random import randint
import webbrowser
from threading import Thread
import logging as _logging
from pymongo import MongoClient
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QPushButton, QLabel, QFrame, QScrollArea,
                              QGridLayout, QComboBox, QSplitter, QSizePolicy)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap, QFont, QIcon, QPalette, QColor

class AnimeCard(QFrame):
    """Custom widget for displaying anime information with full-image background"""
    def __init__(self, anime_data, parent=None):
        super().__init__(parent)
        self.anime_data = anime_data
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the anime card UI with Material Design principles"""
        self.setFixedSize(200, 200)  # Changed to 1:1 ratio
        self.setFrameStyle(QFrame.NoFrame)
        # Initial Material Design elevation
        self.setStyleSheet("""
            QFrame {
                border-radius: 8px;
                margin: 8px;
                background: white;
                border: none;
            }
        """)
        
        # Main layout with overlay
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Background image container
        self.bg_label = QLabel()
        self.bg_label.setFixedSize(200, 200)  # Changed to 1:1 ratio
        self.bg_label.setScaledContents(True)
        self.bg_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.bg_label)
        
        # Overlay for text information
        self.overlay_widget = QWidget()
        self.overlay_widget.setFixedSize(200, 200)  # Changed to 1:1 ratio
        self.overlay_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0,0,0,0.2), stop:0.4 rgba(0,0,0,0.4), stop:1 rgba(0,0,0,0.7));
                border-radius: 8px;
            }
        """)
        
        overlay_layout = QVBoxLayout(self.overlay_widget)
        overlay_layout.setContentsMargins(12, 8, 12, 8)
        overlay_layout.setSpacing(4)
        
        # Title
        self.title_label = QLabel(self.anime_data.get('name', 'Unknown Anime'))
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("""
            QLabel {
                font-weight: 500;
                font-size: 18px;
                color: white;
                background: transparent;
                line-height: 1.3;
                font-family: 'Roboto', sans-serif;
            }
        """)
        overlay_layout.addWidget(self.title_label)
        
        # Time and language info
        info_layout = QHBoxLayout()
        
        # Time
        time_text = f"{self.anime_data.get('local_time', '00:00')}"
        self.time_label = QLabel(time_text)
        self.time_label.setStyleSheet("""
            QLabel {
                color: #FFD700;
                font-size: 16px;
                font-weight: 500;
                background: transparent;
                font-family: 'Roboto', sans-serif;
            }
        """)
        info_layout.addWidget(self.time_label)
        
        info_layout.addStretch()
        
        # Language
        lang_text = f"{self.anime_data.get('language', 'Unknown').upper()}"
        self.lang_label = QLabel(lang_text)
        self.lang_label.setStyleSheet("""
            QLabel {
                color: #87CEEB;
                font-size: 14px;
                font-weight: 500;
                background: transparent;
                font-family: 'Roboto', sans-serif;
            }
        """)
        info_layout.addWidget(self.lang_label)
        
        overlay_layout.addLayout(info_layout)
        overlay_layout.addStretch()
        
        # Add overlay to main layout
        layout.addWidget(self.overlay_widget)
        
        # Make the card clickable
        self.setCursor(Qt.PointingHandCursor)
        self.mousePressEvent = self.on_click
        
        # Load the background image
        self.load_background_image()
        
        # Setup animations
        self.setup_animations()
        
    def load_background_image(self):
        """Load the anime background image"""
        image_url = self.anime_data.get('image_url', '')
        if image_url:
            try:
                # Download and display the image
                response = requests.get(image_url, timeout=5)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    if not pixmap.isNull():
                        pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                        self.bg_label.setPixmap(pixmap)
                        return
            except Exception:
                pass
        
        # Fallback: show a Material Design gradient background
        self.bg_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
                border-radius: 8px;
            }
        """)
        self.bg_label.setText("ANIME")
        self.bg_label.setStyleSheet(self.bg_label.styleSheet() + """
            QLabel {
                font-size: 24px;
                color: white;
                font-weight: 500;
                font-family: 'Roboto', sans-serif;
            }
        """)
    
    def setup_animations(self):
        """Setup hover and click animations for the card following Material Design"""
        # Elevation animation for Material Design shadow effect
        self.elevation_animation = QPropertyAnimation(self, b"geometry")
        self.elevation_animation.setDuration(200)
        self.elevation_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Store original geometry and style
        self.original_geometry = self.geometry()
        self.original_style = self.styleSheet()
        
        # Material Design elevation levels (PyQt5 compatible)
        self.elevation_1 = """
            QFrame {
                border-radius: 8px;
                margin: 8px;
                background: white;
                border: none;
            }
        """
        
        self.elevation_4 = """
            QFrame {
                border-radius: 8px;
                margin: 8px;
                background: white;
                border: none;
            }
        """
        
        self.elevation_8 = """
            QFrame {
                border-radius: 8px;
                margin: 8px;
                background: white;
                border: none;
            }
        """
        
    def enterEvent(self, event):
        """Handle mouse enter event with Material Design elevation"""
        try:
            # Apply higher elevation without changing geometry
            self.setStyleSheet(self.elevation_8)
            
            # Create shadow effect using PyQt5 graphics effects
            from PyQt5.QtWidgets import QGraphicsDropShadowEffect
            from PyQt5.QtGui import QColor
            
            # Create shadow effect for elevation
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 80))
            shadow.setOffset(0, 6)
            self.setGraphicsEffect(shadow)
            
        except Exception:
            pass
        
    def leaveEvent(self, event):
        """Handle mouse leave event with Material Design elevation"""
        try:
            # Return to normal elevation
            self.setStyleSheet(self.elevation_1)
            self.setGraphicsEffect(None)
        except Exception:
            pass
    
    def on_click(self, event):
        """Handle card click with Material Design ripple effect"""
        if event.button() == Qt.LeftButton:
            try:
                # Material Design ripple effect with shadow
                self.setStyleSheet(self.elevation_4)  # Medium elevation on click
                
                # Create click shadow effect
                from PyQt5.QtWidgets import QGraphicsDropShadowEffect
                from PyQt5.QtGui import QColor
                
                click_shadow = QGraphicsDropShadowEffect()
                click_shadow.setBlurRadius(10)
                click_shadow.setColor(QColor(0, 0, 0, 100))
                click_shadow.setOffset(0, 3)
                self.setGraphicsEffect(click_shadow)
                
                # Quick feedback animation
                QTimer.singleShot(150, lambda: self.setStyleSheet(self.elevation_8))
                QTimer.singleShot(300, lambda: self.setStyleSheet(self.elevation_1))
                QTimer.singleShot(300, lambda: self.setGraphicsEffect(None))
                
                # Open web after brief delay
                QTimer.singleShot(100, self.open_anime_web)
                
            except Exception:
                # Fallback if animation fails
                self.open_anime_web()
    
    def open_anime_web(self):
        """Open anime search page"""
        anime_name = self.anime_data.get('name', '')
        if anime_name:
            webbrowser.open_new(f"https://www.iyf.tv/search/{anime_name}")

# Initialize VLC with proper settings for Windows
def init_vlc():
    """Initialize VLC with Windows-compatible settings"""
    try:
        # Set VLC plugin path if not already set
        if not os.environ.get('VLC_PLUGIN_PATH'):
            # Try to find VLC installation
            possible_paths = [
                r"C:\Program Files\VideoLAN\VLC",
                r"C:\Program Files (x86)\VideoLAN\VLC",
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "vlc")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    os.environ['VLC_PLUGIN_PATH'] = path
                    break
        
        # Create VLC instance with specific parameters for Windows
        vlc_args = [
            '--no-video',      # Disable video output
            '--quiet',         # Suppress console output
            '--intf', 'dummy', # Use dummy interface
            '--no-qt-privacy-ask', # Don't ask for privacy
        ]
        
        # Create VLC instance
        vlc_instance = vlc.Instance(vlc_args)
        return vlc_instance
    except Exception:
        return None

# Alternative audio player using pygame (supports MP3)
def play_audio_file(file_path):
    """Play audio file using pygame (supports MP3)"""
    try:
        import pygame
        if os.path.exists(file_path):
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            return True
        else:
            return False
    except ImportError:
        # Fallback to winsound for WAV files only
        try:
            import winsound
            if file_path.lower().endswith('.wav'):
                winsound.PlaySound(file_path, winsound.SND_FILENAME)
                return True
            else:
                return False
        except ImportError:
            return False
        except Exception:
            return False
    except Exception:
        return False



class AnimeThread(QThread):
    """Thread for loading anime data from database with prioritized loading"""
    anime_loaded = pyqtSignal(list)
    all_anime_loaded = pyqtSignal(list)
    
    def __init__(self, mongodb_uri):
        super().__init__()
        self.mongodb_uri = mongodb_uri
        
    def run(self):
        try:
            client = MongoClient(self.mongodb_uri, serverSelectionTimeoutMS=5000)
            db = client['anime_db']
            collection = db['anime_collection']
            
            # Get current day of week for prioritized loading
            current_day = datetime.date.today().weekday()
            
            anime_list = []
            today_anime = []
            # Cache timezone conversions to avoid repeated calculations
            timezone_cache = {}
            
            # Only fetch necessary fields to speed up the query
            for anime in collection.find({}, {"translations": 1}):
                for lang in ["chs", "cht"]:
                    details = anime.get("translations", {}).get(lang)
                    if details:
                        # Use cached timezone conversion
                        timezone_key = f"{details.get('timezone', 'UTC')}_{details.get('day', 0)}"
                        if timezone_key not in timezone_cache:
                            local_day, local_time = self.to_local_time(
                                details.get("time", "00:00"),
                                details.get("timezone", "UTC"),
                                details.get("day", 0)
                            )
                            timezone_cache[timezone_key] = (local_day, local_time)
                        else:
                            local_day, local_time = timezone_cache[timezone_key]
                        
                        anime_entry = {
                            "name": details.get("name", "Unnamed Anime"),
                            "day": local_day,
                            "local_time": local_time,
                            "timezone": details.get("timezone"),
                            "image_url": details.get("image_url"),
                            "language": lang
                        }
                        
                        anime_list.append(anime_entry)
                        
                        # Prioritize today's anime
                        if local_day == current_day:
                            today_anime.append(anime_entry)
            
            # Sort today's anime by time and emit immediately
            today_anime.sort(key=lambda x: x["local_time"])
            self.anime_loaded.emit(today_anime)
            
            # Sort all anime and emit in background
            anime_list.sort(key=lambda x: (x["day"], x["local_time"]))
            self.all_anime_loaded.emit(anime_list)
            
        except Exception as e:
            print(f"Error loading anime: {e}")
            # Return empty list if database is not available
            self.anime_loaded.emit([])
            self.all_anime_loaded.emit([])
    
    def to_local_time(self, anime_time, anime_timezone, date_of_week):
        """Convert the anime's scheduled time and day to local time and day."""
        anime_hour, anime_minute = map(int, anime_time.split(':'))
        anime_tz = pytz.timezone(anime_timezone)
        
        anime_datetime = datetime.datetime.now(anime_tz).replace(
            hour=anime_hour, minute=anime_minute, second=0, microsecond=0
        )
        anime_datetime += datetime.timedelta(days=abs(date_of_week - anime_datetime.weekday()) % 7)
        
        local_time = anime_datetime.astimezone()
        local_day = (date_of_week + (local_time.date() - anime_datetime.date()).days) % 7
        
        return local_day, local_time.strftime('%H:%M')

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Arc")
        self.setGeometry(100, 100, 800, 450)
        
        # Character list for kantai
        self.char_list = ['Верный', 'Warspite', 'Kawakaze', 'Yura', 'Ark_Royal']
        self.char_pos = 0
        self.kantai_is_start = False
        self.current_sound = None
        self.mongodb_uri = self.load_mongodb_uri()
        self.is_closing = False
        
        # Initialize audio systems
        self.init_audio_systems()
        
        # Check day of week and import anime list
        self.day_of_week = datetime.date.today().weekday()
        self.anime_list = []
        self.anime_next = None
        
        # Load images
        self.load_images()
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Create navigation frame
        self.create_navigation_frame()
        
        # Create main content area
        self.content_stack = QWidget()
        self.content_layout = QVBoxLayout(self.content_stack)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.main_layout.addWidget(self.content_stack, 1)
        
        # Create only the home page initially
        self.create_home_page()
        
        # Initialize other pages as None (will be created on-demand)
        self.playlist_page = None
        self.add_person_page = None
        
        # Start timer for clock updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_time)
        self.timer.start(1000)
        
        # Load anime data
        self.load_anime_data()
        
        # Set default page after everything is initialized
        self.ensure_widgets_initialized()
        
        # Set initial active page
        self.current_active_page = "home"
        
        # Show home page and ensure it's properly displayed
        self.show_home_page()
        
    def load_mongodb_uri(self):
        """Load MongoDB URI from config.json."""
        try:
            with open("config.json", "r") as file:
                config = json.load(file)
                return config.get("mongodb_uri")
        except FileNotFoundError:
            print("Error: config.json file not found.")
        except json.JSONDecodeError:
            print("Error: config.json contains invalid JSON.")
        return None
    
    def load_images(self):
        """Load all images used in the application"""
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images")
        self.char_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Characters")
        
        # Load images with error handling
        try:
            self.logo_pixmap = QPixmap(os.path.join(image_path, "CustomTkinter_logo_single.png"))
            if self.logo_pixmap.isNull():
                self.logo_pixmap = QPixmap(26, 26)
                self.logo_pixmap.fill(Qt.transparent)
        except Exception as e:
            print(f"Error loading logo: {e}")
            self.logo_pixmap = QPixmap(26, 26)
            self.logo_pixmap.fill(Qt.transparent)
            
        try:
            self.large_test_pixmap = QPixmap(os.path.join(image_path, "logo.png"))
            if self.large_test_pixmap.isNull():
                self.large_test_pixmap = QPixmap(200, 200)
                self.large_test_pixmap.fill(Qt.gray)
        except Exception as e:
            print(f"Error loading large test image: {e}")
            self.large_test_pixmap = QPixmap(200, 200)
            self.large_test_pixmap.fill(Qt.gray)
            
        try:
            self.home_pixmap = QPixmap(os.path.join(image_path, "home_dark.png"))
            if self.home_pixmap.isNull():
                self.home_pixmap = QPixmap(20, 20)
                self.home_pixmap.fill(Qt.white)
        except Exception as e:
            print(f"Error loading home image: {e}")
            self.home_pixmap = QPixmap(20, 20)
            self.home_pixmap.fill(Qt.white)
            
        try:
            self.playlist_pixmap = QPixmap(os.path.join(image_path, "playlist_dark.png"))
            if self.playlist_pixmap.isNull():
                self.playlist_pixmap = QPixmap(20, 20)
                self.playlist_pixmap.fill(Qt.white)
        except Exception as e:
            print(f"Error loading playlist image: {e}")
            self.playlist_pixmap = QPixmap(20, 20)
            self.playlist_pixmap.fill(Qt.white)
            
        try:
            self.add_user_pixmap = QPixmap(os.path.join(image_path, "add_user_dark.png"))
            if self.add_user_pixmap.isNull():
                self.add_user_pixmap = QPixmap(20, 20)
                self.add_user_pixmap.fill(Qt.white)
        except Exception as e:
            print(f"Error loading add user image: {e}")
            self.add_user_pixmap = QPixmap(20, 20)
            self.add_user_pixmap.fill(Qt.white)
        
    def create_navigation_frame(self):
        """Create the navigation sidebar"""
        self.nav_frame = QFrame()
        self.nav_frame.setMaximumWidth(200)
        self.nav_frame.setMinimumWidth(200)
        self.nav_frame.setStyleSheet("QFrame { background-color: #2b2b2b; }")
        
        nav_layout = QVBoxLayout(self.nav_frame)
        
        # Logo and title
        logo_label = QLabel()
        logo_label.setPixmap(self.logo_pixmap.scaled(26, 26, Qt.KeepAspectRatio))
        title_label = QLabel("  Arc Demo")
        title_label.setFont(QFont("Arial", 15, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        
        title_layout = QHBoxLayout()
        title_layout.addWidget(logo_label)
        title_layout.addWidget(title_label)
        nav_layout.addLayout(title_layout)
        
        # Navigation buttons
        self.home_button = QPushButton("Home")
        self.home_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                text-align: left;
                padding: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #404040;
            }
            QPushButton:pressed {
                background-color: #505050;
            }
        """)
        self.home_button.clicked.connect(self.show_home_page)
        nav_layout.addWidget(self.home_button)
        
        self.playlist_button = QPushButton("Playlist")
        self.playlist_button.setStyleSheet(self.home_button.styleSheet())
        self.playlist_button.clicked.connect(self.show_playlist_page)
        nav_layout.addWidget(self.playlist_button)
        
        self.add_person_button = QPushButton("Add person")
        self.add_person_button.setStyleSheet(self.home_button.styleSheet())
        self.add_person_button.clicked.connect(self.show_add_person_page)
        nav_layout.addWidget(self.add_person_button)
        
        # Appearance mode selector
        self.appearance_combo = QComboBox()
        self.appearance_combo.addItems(["Light", "Dark", "System"])
        self.appearance_combo.setCurrentText("Dark")
        self.appearance_combo.currentTextChanged.connect(self.change_appearance_mode)
        nav_layout.addWidget(self.appearance_combo)
        
        nav_layout.addStretch()
        self.main_layout.addWidget(self.nav_frame)
        
    def create_home_page(self):
        """Create the home page"""
        self.home_page = QWidget()
        self.home_page.setObjectName("home_page")
        self.home_page.setParent(self.content_stack)  # Set proper parent
        home_layout = QVBoxLayout(self.home_page)
        home_layout.setContentsMargins(10, 10, 10, 10)
        home_layout.setSpacing(10)
        
        # Clock label
        self.clock_label = QLabel()
        self.clock_label.setObjectName("clock_label")
        self.clock_label.setFont(QFont("Courier New", 15, QFont.Bold))
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setText("Loading...")
        self.clock_label.setStyleSheet("""
            QLabel {
                color: #333;
                background-color: #f0f0f0;
                padding: 10px;
                border-radius: 5px;
                margin: 5px;
            }
        """)
        home_layout.addWidget(self.clock_label)
        
        # Set initial time
        current_time = datetime.datetime.now()
        self.clock_label.setText(str(current_time.replace(microsecond=0)))
        
        # Create main content area with left and right sections
        main_content_layout = QHBoxLayout()
        main_content_layout.setSpacing(20)
        
        # Left section (character and buttons)
        left_section = QVBoxLayout()
        left_section.setSpacing(15)
        
        # Character image
        self.character_label = QLabel()
        self.character_label.setObjectName("character_label")
        self.character_label.setPixmap(self.large_test_pixmap.scaled(500, 500, Qt.KeepAspectRatio))
        self.character_label.setAlignment(Qt.AlignCenter)
        self.character_label.setStyleSheet("""
            QLabel {
                border: 2px solid #ddd;
                border-radius: 20px;
                padding: 20px;
                background-color: white;
                min-width: 540px;
                min-height: 540px;
            }
        """)
        left_section.addWidget(self.character_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.start_kantai_button = QPushButton("Start Kantai")
        self.start_kantai_button.setObjectName("start_kantai_button")
        self.start_kantai_button.clicked.connect(self.start_kantai)
        self.start_kantai_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(self.start_kantai_button)
        
        self.next_char_button = QPushButton("Next Character")
        self.next_char_button.setObjectName("next_char_button")
        self.next_char_button.clicked.connect(self.change_char)
        self.next_char_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        button_layout.addWidget(self.next_char_button)
        
        left_section.addLayout(button_layout)
        left_section.addStretch()  # Push content to top
        
        main_content_layout.addLayout(left_section)
        
        # Right section (anime list)
        right_section = QVBoxLayout()
        right_section.setSpacing(15)
        
        # Section title
        title_label = QLabel("Today's Anime")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #333;
                padding: 5px;
                background-color: #f8f9fa;
                border-radius: 5px;
                border-left: 4px solid #007bff;
            }
        """)
        right_section.addWidget(title_label)
        
        # Today's anime list
        self.anime_scroll = QScrollArea()
        self.anime_scroll.setObjectName("anime_scroll")
        self.anime_scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid #ddd;
                border-radius: 10px;
                background-color: white;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
        """)
        
        self.anime_widget = QWidget()
        self.anime_widget.setObjectName("anime_widget")
        self.anime_layout = QVBoxLayout(self.anime_widget)
        self.anime_layout.setSpacing(8)
        self.anime_layout.setContentsMargins(12, 12, 12, 12)
        
        # Add loading indicator
        self.loading_label = QLabel("Loading anime...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: gray;
                font-style: italic;
                padding: 20px;
                background-color: #f9f9f9;
                border-radius: 8px;
                margin: 10px;
            }
        """)
        self.anime_layout.addWidget(self.loading_label)
        
        self.anime_scroll.setWidget(self.anime_widget)
        self.anime_scroll.setWidgetResizable(True)
        self.anime_scroll.setMinimumWidth(450)  # Wider to accommodate square cards
        self.anime_scroll.setMaximumWidth(480)
        right_section.addWidget(self.anime_scroll)
        
        # Upcoming anime button
        self.upcoming_anime_btn = QPushButton("No upcoming anime")
        self.upcoming_anime_btn.setObjectName("upcoming_anime_btn")
        self.upcoming_anime_btn.clicked.connect(lambda: self.open_web(""))
        self.upcoming_anime_btn.setStyleSheet("""
            QPushButton {
                padding: 12px;
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        right_section.addWidget(self.upcoming_anime_btn)
        
        main_content_layout.addLayout(right_section)
        
        home_layout.addLayout(main_content_layout)
        
    def create_playlist_page(self):
        """Create the playlist page"""
        self.playlist_page = QWidget()
        self.playlist_page.setObjectName("playlist_page")
        self.playlist_page.setParent(self.content_stack)  # Set proper parent
        self.playlist_layout = QGridLayout(self.playlist_page)
        
        # Days of the week
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.day_widgets = {}
        
        for i, day in enumerate(days):
            scroll_area = QScrollArea()
            scroll_area.setObjectName(f"scroll_area_{i}")
            scroll_widget = QWidget()
            scroll_widget.setObjectName(f"scroll_widget_{i}")
            scroll_layout = QVBoxLayout(scroll_widget)
            
            day_label = QLabel(day)
            day_label.setObjectName(f"day_label_{i}")
            day_label.setFont(QFont("Arial", 12, QFont.Bold))
            scroll_layout.addWidget(day_label)
            
            self.day_widgets[i] = scroll_layout
            scroll_area.setWidget(scroll_widget)
            scroll_area.setWidgetResizable(True)
            
            self.playlist_layout.addWidget(scroll_area, i // 3, i % 3)
            
    def create_add_person_page(self):
        """Create the add person page"""
        self.add_person_page = QWidget()
        self.add_person_page.setObjectName("add_person_page")
        self.add_person_page.setParent(self.content_stack)  # Set proper parent
        layout = QVBoxLayout(self.add_person_page)
        
        # Simple placeholder for add person functionality
        placeholder_label = QLabel("Add Person Page")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #333;
                padding: 50px;
            }
        """)
        layout.addWidget(placeholder_label)
        
    def show_home_page(self):
        """Show the home page"""
        try:
            self.set_page_active("home")
            self.clear_content_layout()
            
            # Ensure home_page exists and is valid
            if hasattr(self, 'home_page') and self.home_page is not None:
                # Check if home_page is still valid
                try:
                    if self.home_page.parent() is None:
                        # Home page was deleted, recreate it
                        self.create_home_page()
                except RuntimeError:
                    # Home page was deleted, recreate it
                    self.create_home_page()
                
                self.content_layout.addWidget(self.home_page)
                self.resize(800, 450)
                
                # Force update the display
                self.home_page.show()
                self.home_page.update()
                
                # Refresh anime display if we have today's anime data
                if hasattr(self, 'today_anime'):
                    self.update_anime_display()
            else:
                print("Error: home_page is not properly initialized")
        except RuntimeError as e:
            print(f"Error showing home page: {e}")
        except Exception as e:
            print(f"Unexpected error in show_home_page: {e}")
        
    def show_playlist_page(self):
        """Show the playlist page"""
        try:
            self.set_page_active("playlist")
            self.clear_content_layout()
            
            # Create playlist page if it doesn't exist
            if self.playlist_page is None:
                self.create_playlist_page()
            
            if hasattr(self, 'playlist_page') and self.playlist_page is not None:
                self.content_layout.addWidget(self.playlist_page)
                self.resize(1000, 850)
                self.load_anime_playlist()
            else:
                print("Error: playlist_page is not properly initialized")
        except RuntimeError as e:
            print(f"Error showing playlist page: {e}")
        except Exception as e:
            print(f"Unexpected error in show_playlist_page: {e}")
        
    def show_add_person_page(self):
        """Show the add person page"""
        try:
            self.set_page_active("add_person")
            self.clear_content_layout()
            
            # Create add person page if it doesn't exist
            if self.add_person_page is None:
                self.create_add_person_page()
            
            if hasattr(self, 'add_person_page') and self.add_person_page is not None:
                self.content_layout.addWidget(self.add_person_page)
                self.resize(960, 640)
            else:
                print("Error: add_person_page is not properly initialized")
        except RuntimeError as e:
            print(f"Error showing add person page: {e}")
        except Exception as e:
            print(f"Unexpected error in show_add_person_page: {e}")
    
    def clear_content_layout(self):
        """Clear all widgets from content layout"""
        try:
            # Store widgets to delete later to avoid modification during iteration
            widgets_to_delete = []
            while self.content_layout.count():
                child = self.content_layout.takeAt(0)
                if child and child.widget():
                    widget = child.widget()
                    if widget:
                        widgets_to_delete.append(widget)
            
            # Delete widgets after clearing the layout
            for widget in widgets_to_delete:
                try:
                    if widget and not widget.isHidden():
                        # Hide widget first to prevent any operations
                        widget.hide()
                        widget.setParent(None)
                        widget.deleteLater()
                except RuntimeError:
                    # Widget already deleted, skip
                    pass
                except Exception:
                    # Any other error, skip this widget
                    pass
        except RuntimeError as e:
            print(f"Error clearing content layout: {e}")
        except Exception as e:
            print(f"Unexpected error in clear_content_layout: {e}")
        
    def set_page_active(self, active_page):
        """Set the active page and update button styles"""
        buttons = {
            "home": self.home_button,
            "playlist": self.playlist_button,
            "add_person": self.add_person_button
        }
        
        for page, button in buttons.items():
            if page == active_page:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #505050;
                        color: white;
                        text-align: left;
                        padding: 10px;
                        border: none;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: white;
                        text-align: left;
                        padding: 10px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #404040;
                    }
                """)
        
        # Store current active page for timer management
        self.current_active_page = active_page
    
    def load_anime_data(self):
        """Load anime data from database with prioritized loading"""
        if self.mongodb_uri:
            self.anime_thread = AnimeThread(self.mongodb_uri)
            self.anime_thread.anime_loaded.connect(self.on_today_anime_loaded)
            self.anime_thread.all_anime_loaded.connect(self.on_all_anime_loaded)
            self.anime_thread.start()
    
    def on_today_anime_loaded(self, today_anime):
        """Handle today's anime data (prioritized loading)"""
        try:
            self.today_anime = today_anime
            print(f"Loaded {len(today_anime)} today's anime entries")
            self.update_anime_display()
            self.check_next_anime()
        except RuntimeError as e:
            print(f"Error handling today's anime data: {e}")
        except Exception as e:
            print(f"Unexpected error in today's anime loading: {e}")
    
    def on_all_anime_loaded(self, all_anime):
        """Handle all anime data (background loading)"""
        try:
            self.anime_list = all_anime
            print(f"Loaded {len(all_anime)} total anime entries")
            # Update playlist page if it's currently visible
            if hasattr(self, 'playlist_page') and self.playlist_page.isVisible():
                self.load_anime_playlist()
        except RuntimeError as e:
            print(f"Error handling all anime data: {e}")
        except Exception as e:
            print(f"Unexpected error in all anime loading: {e}")
    
    def update_anime_display(self):
        """Update the anime display on home page"""
        try:
            # Check if anime_layout exists and is valid
            if not hasattr(self, 'anime_layout') or self.anime_layout is None:
                return
                
            # Check if we're on the home page
            if not hasattr(self, 'current_active_page') or self.current_active_page != "home":
                return
                
            # Clear existing anime cards and loading indicator
            for i in reversed(range(self.anime_layout.count())):
                child = self.anime_layout.itemAt(i).widget()
                if child:
                    try:
                        child.hide()  # Hide first to prevent operations
                        child.deleteLater()
                    except RuntimeError:
                        # Widget already deleted, skip
                        pass
                    except Exception:
                        # Any other error, skip this widget
                        pass
            
            # Add today's anime as cards (using today_anime from signal)
            count = 0
            if hasattr(self, 'today_anime'):
                for i, anime in enumerate(self.today_anime):
                    try:
                        anime_card = AnimeCard(anime)
                        self.anime_layout.addWidget(anime_card)
                        
                        # Add staggered fade-in animation
                        self.add_card_animation(anime_card, i * 100)  # 100ms delay between cards
                        count += 1
                    except Exception:
                        # Skip this anime card if there's an error
                        pass
            
            # If no anime today, show a message
            if count == 0:
                try:
                    no_anime_label = QLabel("No anime scheduled for today")
                    no_anime_label.setAlignment(Qt.AlignCenter)
                    no_anime_label.setStyleSheet("""
                        QLabel {
                            color: gray;
                            font-style: italic;
                            padding: 20px;
                            background-color: #f9f9f9;
                            border-radius: 8px;
                            margin: 10px;
                        }
                    """)
                    self.anime_layout.addWidget(no_anime_label)
                except Exception:
                    # Skip if there's an error creating the label
                    pass
        except RuntimeError as e:
            print(f"Error updating anime display: {e}")
        except Exception as e:
            print(f"Unexpected error in anime display: {e}")
    
    def add_card_animation(self, card, delay=0):
        """Add fade-in animation to anime card"""
        try:
            # Start with 0 opacity
            card.setGraphicsEffect(None)  # Remove any existing effects
            
            # Create opacity animation
            opacity_animation = QPropertyAnimation(card, b"windowOpacity")
            opacity_animation.setDuration(300)
            opacity_animation.setStartValue(0.0)
            opacity_animation.setEndValue(1.0)
            opacity_animation.setEasingCurve(QEasingCurve.OutCubic)
            
            # Start animation after delay
            QTimer.singleShot(delay, opacity_animation.start)
            
        except Exception:
            # If animation fails, just show the card normally
            pass
    
    def check_next_anime(self):
        """Find the next upcoming anime"""
        try:
            current_time = datetime.datetime.now().time()
            
            # Check if upcoming_anime_btn exists and is valid
            if (not hasattr(self, 'upcoming_anime_btn') or 
                self.upcoming_anime_btn is None or 
                self.upcoming_anime_btn.isHidden()):
                return
            
            # Use today_anime if available, otherwise fall back to anime_list
            anime_to_check = getattr(self, 'today_anime', []) if hasattr(self, 'today_anime') else self.anime_list
            
            # Check for today's anime
            anime_today = [anime for anime in anime_to_check if anime['day'] == self.day_of_week]
            for anime in anime_today:
                anime_hour, anime_minute = map(int, anime['local_time'].split(':'))
                anime_time = datetime.time(anime_hour, anime_minute)
                
                if anime_time > current_time:
                    self.anime_next = anime
                    try:
                        self.upcoming_anime_btn.setText(self.split_text(anime['name']))
                        # Disconnect all existing connections to avoid duplicates
                        try:
                            self.upcoming_anime_btn.clicked.disconnect()
                        except TypeError:
                            pass  # No connections to disconnect
                        self.upcoming_anime_btn.clicked.connect(lambda: self.open_web(anime['name']))
                    except RuntimeError:
                        # Widget was deleted, skip this update
                        pass
                    return
            
            # Fallback to next day
            next_day = (self.day_of_week + 1) % 7
            anime_next_day = [anime for anime in anime_to_check if anime['day'] == next_day]
            if anime_next_day:
                self.anime_next = anime_next_day[0]
                try:
                    self.upcoming_anime_btn.setText(self.split_text(anime_next_day[0]['name']))
                    # Disconnect all existing connections to avoid duplicates
                    try:
                        self.upcoming_anime_btn.clicked.disconnect()
                    except TypeError:
                        pass  # No connections to disconnect
                    self.upcoming_anime_btn.clicked.connect(lambda: self.open_web(anime_next_day[0]['name']))
                except RuntimeError:
                    # Widget was deleted, skip this update
                    pass
        except RuntimeError as e:
            print(f"Error checking next anime: {e}")
        except Exception as e:
            print(f"Unexpected error in check_next_anime: {e}")
    
    def load_anime_playlist(self):
        """Load anime playlist for the playlist page"""
        for day in range(7):
            layout = self.day_widgets[day]
            
            # Clear existing cards
            for i in reversed(range(layout.count())):
                child = layout.itemAt(i).widget()
                if child:
                    child.deleteLater()
            
            # Add anime for this day
            day_anime = [anime for anime in self.anime_list if anime['day'] == day]
            for anime in day_anime:
                anime_card = AnimeCard(anime)
                layout.addWidget(anime_card)
    
    def change_char(self):
        """Switch to the next character"""
        if self.current_sound:
            self.current_sound.stop()
        
        self.char_pos = (self.char_pos + 1) % len(self.char_list)
        
        # Update character image
        char_image_path = os.path.join(self.char_path, self.get_cur_char() + ".png")
        try:
            if os.path.exists(char_image_path):
                char_pixmap = QPixmap(char_image_path)
                if not char_pixmap.isNull():
                    char_pixmap = char_pixmap.scaled(500, 500, Qt.KeepAspectRatio)
                    self.character_label.setPixmap(char_pixmap)
                else:
                    print(f"Failed to load character image: {char_image_path}")
            else:
                print(f"Character image not found: {char_image_path}")
        except Exception as e:
            print(f"Error loading character image: {e}")
        
        if self.kantai_is_start:
            self.play_sound("_Intro")
    
    def get_cur_char(self):
        """Get name of current character as string"""
        return self.char_list[self.char_pos]
    
    def start_kantai(self):
        """Start or stop Kantai mode"""
        self.kantai_is_start = not self.kantai_is_start
        
        if self.kantai_is_start:
            # Play start sound
            sound_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Sounds")
            sound_file = os.path.join(sound_path, f"TitleCallA{randint(1, 20)}.mp3")
            try:
                if os.path.exists(sound_file):
                    # Try VLC first
                    if self.vlc_instance is not None:
                        try:
                            media = self.vlc_instance.media_new(sound_file)
                            self.current_sound = self.vlc_instance.media_player_new()
                            self.current_sound.set_media(media)
                            self.current_sound.play()
                            return
                        except Exception:
                            pass
                    
                    # Try pygame
                    if hasattr(self, 'pygame_available') and self.pygame_available:
                        try:
                            import pygame
                            pygame.mixer.music.load(sound_file)
                            pygame.mixer.music.play()
                            return
                        except Exception:
                            pass
                    
                    # Fallback to generic audio function
                    play_audio_file(sound_file)
            except Exception:
                pass
            
            # Update character image
            char_image_path = os.path.join(self.char_path, self.get_cur_char() + ".png")
            try:
                if os.path.exists(char_image_path):
                    char_pixmap = QPixmap(char_image_path)
                    if not char_pixmap.isNull():
                        char_pixmap = char_pixmap.scaled(500, 500, Qt.KeepAspectRatio)
                        self.character_label.setPixmap(char_pixmap)
                    else:
                        print(f"Failed to load character image: {char_image_path}")
                else:
                    print(f"Character image not found: {char_image_path}")
            except Exception as e:
                print(f"Error loading character image: {e}")
        else:
            if self.current_sound:
                self.current_sound.stop()
                self.current_sound = None
            self.character_label.setPixmap(self.large_test_pixmap.scaled(500, 500, Qt.KeepAspectRatio))
        
        self.start_kantai_button.setText("Start Kantai" if not self.kantai_is_start else "Close Kantai")
    
    def play_sound(self, keyword):
        """Play a sound for the current character"""
        if self.kantai_is_start:
            sound_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Sounds")
            sound_file = os.path.join(sound_path, self.get_cur_char() + keyword + ".mp3")
            try:
                if os.path.exists(sound_file):
                    # Stop any currently playing sound
                    if self.current_sound:
                        self.current_sound.stop()
                    
                    # Try VLC first
                    if self.vlc_instance is not None:
                        try:
                            media = self.vlc_instance.media_new(sound_file)
                            self.current_sound = self.vlc_instance.media_player_new()
                            self.current_sound.set_media(media)
                            self.current_sound.play()
                            return
                        except Exception:
                            pass
                    
                    # Try pygame
                    if hasattr(self, 'pygame_available') and self.pygame_available:
                        try:
                            import pygame
                            pygame.mixer.music.load(sound_file)
                            pygame.mixer.music.play()
                            return
                        except Exception:
                            pass
                    
                    # Fallback to generic audio function
                    play_audio_file(sound_file)
            except Exception:
                pass
    
    def check_time(self):
        """Update time display and check for hourly sounds"""
        # Don't update if application is closing
        if hasattr(self, 'is_closing') and self.is_closing:
            return
            
        try:
            current_time = datetime.datetime.now()
            
            # Only update clock if we're on the home page and clock_label exists and is valid
            if (hasattr(self, 'current_active_page') and 
                self.current_active_page == "home" and
                hasattr(self, 'clock_label') and 
                self.clock_label is not None and 
                not self.clock_label.isHidden() and
                not self.clock_label.parent() is None):
                try:
                    self.clock_label.setText(str(current_time.replace(microsecond=0)))
                except RuntimeError:
                    # Widget was deleted, skip this update
                    pass
                except Exception:
                    # Any other error, skip this update
                    pass
            
            self.day_of_week = current_time.weekday()
            
            # Only check next anime if we're on the home page
            if hasattr(self, 'current_active_page') and self.current_active_page == "home":
                self.check_next_anime()
            
            if current_time.minute == 0 and current_time.second == 0:
                self.play_sound(str(current_time.hour))
        except RuntimeError as e:
            print(f"Error updating clock: {e}")
            # Don't stop the timer, just skip this update
        except Exception as e:
            print(f"Unexpected error in check_time: {e}")
    
    def open_web(self, keyword):
        """Open website for anime"""
        if keyword:
            webbrowser.open_new(f"https://www.iyf.tv/search/{keyword}")
    
    def split_text(self, text):
        """Split text for display"""
        length = len(text)
        new_text = '\n'.join(text[i:i+10] for i in range(0, length, 10))
        return new_text
    
    def change_appearance_mode(self, mode):
        """Change appearance mode"""
        if mode == "Dark":
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: white;
                }
            """)
        elif mode == "Light":
            self.setStyleSheet("")
        # System mode would require detecting system theme
    
    def closeEvent(self, event):
        """Handle application close event"""
        try:
            # Set closing flag to prevent timer updates
            self.is_closing = True
            
            # Stop the timer first
            if hasattr(self, 'timer'):
                self.timer.stop()
            
            # Stop any playing sound
            if hasattr(self, 'current_sound') and self.current_sound:
                try:
                    self.current_sound.stop()
                except Exception:
                    pass
            
            # Clean up any threads
            if hasattr(self, 'anime_thread') and self.anime_thread:
                try:
                    self.anime_thread.quit()
                    self.anime_thread.wait()
                except Exception:
                    pass
                
        except Exception as e:
            print(f"Error during cleanup: {e}")
        
        event.accept()
    
    def ensure_widgets_initialized(self):
        """Ensure all widgets are properly initialized"""
        try:
            # Check if all required widgets exist
            required_widgets = [
                'home_page', 'clock_label', 'character_label', 'start_kantai_button',
                'next_char_button', 'anime_scroll', 'anime_widget',
                'anime_layout', 'upcoming_anime_btn'
            ]
            
            for widget_name in required_widgets:
                if not hasattr(self, widget_name):
                    print(f"Warning: {widget_name} not found")
                elif getattr(self, widget_name) is None:
                    print(f"Warning: {widget_name} is None")
                    
            # Check other pages (may be None initially)
            if not hasattr(self, 'playlist_page'):
                print("Warning: playlist_page not found")
            if not hasattr(self, 'add_person_page'):
                print("Warning: add_person_page not found")
                    
        except Exception as e:
            print(f"Error checking widget initialization: {e}")
    
    def init_audio_systems(self):
        """Initialize all available audio systems"""
        # Initialize VLC
        self.vlc_instance = init_vlc()
        
        # Initialize pygame
        try:
            import pygame
            pygame.mixer.init()
            self.pygame_available = True
        except ImportError:
            self.pygame_available = False
        except Exception:
            self.pygame_available = False
        
        # Initialize winsound
        try:
            import winsound
            self.winsound_available = True
        except ImportError:
            self.winsound_available = False
    

    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_()) 