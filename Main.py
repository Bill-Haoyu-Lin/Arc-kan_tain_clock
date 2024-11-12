import customtkinter
import os
from PIL import Image
from cefpython3 import cefpython as cef
import requests
import datetime
import vlc
from random import *
from web_widget import *
import webbrowser
from threading import Thread
import logging as _logging
from pymongo import MongoClient
import json
import pytz

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Arc")
        self.geometry("800x450")

        self.browser_frame = None

        # Character list for kantai
        self.char_list = ['Верный', 'Warspite', 'Kawakaze', 'Yura', 'Ark_Royal']
        self.char_pos = 0
        self.kantai_is_start = False
        self.current_sound = None 
        self.mongodb_uri = self.load_mongodb_uri()

        # Set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.third_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        

        # Check day of week and import anime list
        self.day_of_week = datetime.date.today().weekday()
        self.anime_list = self.get_anime_list_from_db()  # Fetch anime list from DB
        self.anime_next = self.upcoming_anime()

        # Load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images")
        self.char_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Characters")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "CustomTkinter_logo_single.png")), size=(26, 26))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "logo.png")), size=(200, 200))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(100, 100))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.playlist_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "playlist_light.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "playlist_dark.png")), size=(20, 20))
        self.holder_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "holder.png")),
                                                   dark_image=Image.open(os.path.join(image_path, "holder.png")), size=(100, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))
        self.anime_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "anime.png")),
                                                  dark_image=Image.open(os.path.join(image_path, "anime.png")), size=(100, 100))

        # Create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Arc Demo", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Playlist",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.playlist_image, anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Add person",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w", command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # Create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.clock_label = customtkinter.CTkLabel(self.home_frame, font=("Courier New", 15, 'bold'), text='')
        self.clock_label.grid(row=0, column=0, columnspan=2, padx=2, pady=10)

        self.home_frame_large_image_label = customtkinter.CTkLabel(self.home_frame, text="", image=self.large_test_image)
        self.home_frame_large_image_label.grid(row=1, column=0, columnspan=2, padx=20, pady=10)

        self.home_button_1 = customtkinter.CTkButton(self.home_frame, text="Start Kantai",
                                                     command=self.start_kantai)
        self.home_button_1.grid(row=2, column=0, padx=10, pady=10)

        self.home_button_2 = customtkinter.CTkButton(self.home_frame, text="Next Character",
                                                     command=self.change_char)
        self.home_button_2.grid(row=2, column=1, padx=10, pady=10)

        self.home_buttons_frame = customtkinter.CTkScrollableFrame(self.home_frame, label_text="Anime List")
        self.home_buttons_frame.grid(row=0, column=2, rowspan=3, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.home_buttons_frame.grid_columnconfigure(0, weight=1)
        self.anime_next = self.upcoming_anime() if self.upcoming_anime() else {"name": "No upcoming anime", "image_url": ""}

        self.upcoming_anime_btn = customtkinter.CTkButton(
            self.home_frame,
            text=self.split_text(self.anime_next["name"]),
            image=self.get_img(self.anime_next["image_url"]) if self.anime_next["image_url"] else None,
            command=lambda: self.open_web(self.anime_next["name"])
        )
        self.upcoming_anime_btn.grid(row=3, column=2, padx=10, pady=10)
        thread1 = Thread(target=self.get_anime_list_display, args=())
        thread1.start()

        # Select default frame
        self.select_frame_by_name("home")
        self.check_time()
        
    def to_local_time(self, anime_time, anime_timezone):
        """Convert the anime's scheduled time to local time and adjust the day if needed."""
        # Parse the anime's time
        anime_hour, anime_minute = map(int, anime_time.split(':'))
        
        # Get the anime's timezone
        anime_tz = pytz.timezone(anime_timezone)
        
        # Create a datetime object for today with the anime's time in its timezone
        anime_datetime = datetime.datetime.now(anime_tz).replace(hour=anime_hour, minute=anime_minute, second=0, microsecond=0)
        
        # Convert to local timezone
        local_time = anime_datetime.astimezone()  # Convert to the system's local timezone
        
        if anime_datetime.day != local_time.day:
            if local_time < datetime.datetime.now(local_time.tzinfo).replace(hour=0, minute=0, second=0, microsecond=0):
                # If local time is in the previous day, adjust forward by one day
                local_time += datetime.timedelta(days=1)
            else:
                # If local time is in the next day, adjust back by one day
                local_time -= datetime.timedelta(days=1)

        return local_time



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

    def get_anime_list_from_db(self):
        """Fetch anime list from the database, converting scheduled times and days to local time."""
        client = MongoClient(self.mongodb_uri)
        db = client['anime_db']
        collection = db['anime_collection']
        
        anime_list = []
        for anime in collection.find({}):
            for lang in ["chs", "cht"]:
                details = anime.get("translations", {}).get(lang)
                if details:
                    # Convert anime time to local time
                    local_time = self.to_local_time(details.get("time", "00:00"), details.get("timezone", "UTC"))
                    
                    # Determine local day by comparing with anime's original day
                    local_day = details.get("day", 0)  # Default to 0 (Monday) if no day is specified
                    if local_time.date() > datetime.datetime.now().date():
                        # If the local time is the next day, increment the day (wrap around using % 7)
                        local_day = (local_day + 1) % 7
                    elif local_time.date() < datetime.datetime.now().date():
                        # If the local time is the previous day, decrement the day (wrap around using % 7)
                        local_day = (local_day - 1) % 7

                    anime_list.append({
                        "name": details.get("name", "Unnamed Anime"),
                        "day": local_day,
                        "local_time": local_time.strftime('%H:%M'),  # Store the local time as a string
                        "timezone": details.get("timezone"),
                        "image_url": details.get("image_url"),
                        "language": lang
                    })
       
        return anime_list


    def upcoming_anime(self):
        """Find the next upcoming anime scheduled for today or fallback to tomorrow, based on local time."""
        current_time = datetime.datetime.now().time()  # Current local time

        # Check for today's anime
        anime_today = [anime for anime in self.anime_list if anime['day'] == self.day_of_week]
        for anime in anime_today:
            anime_hour, anime_minute = map(int, anime['local_time'].split(':'))
            anime_time = datetime.time(anime_hour, anime_minute)
            
            # Compare the local times to find the next anime
            if anime_time > current_time:
                return anime
        
        # Fallback to the next day if no anime is left today
        next_day = (self.day_of_week + 1) % 7
        anime_next_day = [anime for anime in self.anime_list if anime['day'] == next_day]
        return anime_next_day[0] if anime_next_day else None

    def check_next_anime(self):
        temp = self.upcoming_anime()
        if temp and temp != self.anime_next:
            self.anime_next = temp
            self.upcoming_anime_btn.config(text=self.split_text(self.anime_next['name']), 
                                           image=self.get_img(self.anime_next['image_url']),
                                           command=lambda: self.open_web(self.anime_next['name']))

    def get_anime_list_display(self):
        count = 0
        self.anime_today = {}
        for anime in self.anime_list:
            if self.day_of_week == anime['day']:
                self.anime_today[count] = customtkinter.CTkButton(self.home_buttons_frame, text=self.split_text(anime['name']),
                                                                  image=self.get_img(anime['image_url']), compound="top",
                                                                  command=lambda a=anime['name']: self.open_web(a))
                self.anime_today[count].grid(row=count, column=0, padx=20, pady=10)
                count += 1

    def change_char(self):
        """Switch to the next character, stopping any currently playing sound first."""
        if self.current_sound:
            self.current_sound.stop()  # Stop any current sound before playing the new one

        # Cycle through characters
        self.char_pos = (self.char_pos + 1) % len(self.char_list)
        
        # Update character image
        old_image = Image.open(os.path.join(self.char_path, self.get_cur_char() + ".png"))
        im_size = old_image.size
        new_size = max(im_size)
        background = (new_size, new_size)
        location = ((new_size - im_size[0]) // 2, (new_size - im_size[1]) // 2)
        new_image = Image.new('RGBA', background, (0, 0, 0, 0))
        new_image.paste(old_image, location)
        
        # Display the updated character image
        image_char = customtkinter.CTkImage(new_image, size=(200, 200))
        self.home_frame_large_image_label.configure(image=image_char)

        # Play character intro sound if enabled
        if self.kantai_is_start:
            self.play_sound("_Intro")

    def switch_back_char(self):
         #get correct size of image to be a square   
        old_image = Image.open(os.path.join(self.char_path, self.get_cur_char()+".png" ))
        im_size = old_image.size
        if im_size[0]>im_size[1]:
            new_w = im_size[0]
            background = (new_w,new_w)
            location = (0,int((new_w-im_size[1])/2))
        else:
            new_h = im_size[1]
            background = (new_h,new_h)
            location = (int((new_h-im_size[0])/2),0)
        new_image = Image.new('RGBA', background, (0, 0, 0, 0))
        new_image.paste(old_image,location )

        #output image to update on home screen
        image_char = customtkinter.CTkImage(new_image, size=(200, 200))
        self.home_frame_large_image_label.configure(image=image_char)

    #Start or shut down kantain clock
    def start_kantai(self):
        """Start or stop Kantai mode. Stop all sounds if Kantai mode is turned off."""
        self.kantai_is_start = not self.kantai_is_start
        if self.kantai_is_start:
            # Play the start sound and update character image
            sound_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Sounds")
            self.current_sound = vlc.MediaPlayer(os.path.join(sound_path, "TitleCallA" + str(randint(1, 20)) + ".mp3"))
            self.current_sound.play()
            self.switch_back_char()
        else:
            # Stop all sounds if Kantai mode is turned off
            if self.current_sound:
                self.current_sound.stop()
                self.current_sound = None  # Clear the current sound reference
            self.home_frame_large_image_label.configure(image=self.large_test_image)  # Reset image if needed

        # Update the button text based on the mode
        self.home_button_1.configure(text="Start Kantai" if not self.kantai_is_start else "Close Kantai")


    #Get name of current character as string
    def get_cur_char(self):
        return  self.char_list[self.char_pos]
    
    #play sound
    def play_sound(self, keyword):
        """Play a sound for the current character, ensuring only one sound is played at a time."""
        sound_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Sounds")
        if self.kantai_is_start:
            if self.current_sound:
                self.current_sound.stop()  # Stop any currently playing sound
            self.current_sound = vlc.MediaPlayer(os.path.join(sound_path, self.get_cur_char() + keyword + ".mp3"))
            self.current_sound.play()
    
    #Update Time based on current PC time on home screen        
    def check_time(self):
        self.clock_label.configure(text=datetime.datetime.now().replace(microsecond=0))
        current_time = datetime.datetime.now()
        self.clock_label.after(1000, self.check_time)
        self.day_of_week = datetime.date.today().weekday()
        self.check_next_anime()
        if current_time.minute == 0 and current_time.second == 0:
            self.play_sound(str(current_time.hour))
            idle_times = [randint(5, 25),randint(35, 55)]
        else:
            pass
   

    #Open website on click for anime list
    def open_web(self,keyword):
        webbrowser.open_new("https://www.iyf.tv/search/"+keyword)

    #Get_img from URL
    def get_img(self,url,x=100,y =100):
        image = customtkinter.CTkImage(Image.open(requests.get(url, stream=True).raw), size=(x, y))
        return image
    
    def split_text(self,text):
        length = len(text)
        new_text ='\n'.join(text[i:i+10] for i in range(0, length, 10))
        return new_text
    
    #load anime frame into desired frame
    def load_anime_frame(self,frame):
        self.date_widget =dict()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.date_widget = self.list_to_widgets(days,frame,0)
        for day in range(0,7):
            list_anime = [sublist for sublist in self.anime_list if sublist[1] == day]
            thread3 = Thread(target = self.generate_anime_list,args=(list_anime,self.date_widget[day]))
            thread3.start()
    
    #generate a list of widgets and output as a dictionary
    def list_to_widgets(self,list,frame,row):
        col = 0
        list_widget = dict()
        for elements in list:
            #initialize the buttons and connect callback function to open relative webpage. 
            list_widget[col]=customtkinter.CTkScrollableFrame(frame, label_text=elements)
            list_widget[col].grid(row=row+int(col/3), column=col%3, padx=20, pady=10)
            col +=1
        return list_widget
    
    #generate a list of widgets in given tk frame by name from given list [name, day, time, img]
    def generate_anime_list(self,list,frame):
        count = 0
        self.list_buttons = dict()
        for elements in list:
            #initialize the buttons and connect callback function to open relative webpage. 
            self.list_buttons[count]=customtkinter.CTkButton(frame, text=self.split_text(elements[0])+ '\n' + elements[2], 
                                                           image=self.get_img(elements[3]), compound="top",
                                                           command=lambda a = elements[0]: self.open_web(a ))
            self.list_buttons[count].grid(row=count, column=0, padx=20, pady=10)
            count +=1

    #genearate button list for anime of the day !!!! NEED TO change to more general use
    def get_anime_list(self):
        count = 0
        self.anime_today = dict()
        for anime in self.anime_list:
            if self.day_of_week == anime[1]:
                #initialize the buttons and connect callback function to open relative webpage. 
                self.anime_today[count]=customtkinter.CTkButton(self.home_buttons_frame, text=self.split_text(anime[0]), 
                                                           image=self.get_img(anime[3]), compound="top",
                                                           command=lambda a = anime[0]: self.open_web(a ))
                self.anime_today[count].grid(row=count, column=0, padx=20, pady=10)
                count +=1
   
    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
            
        if name == "frame_2":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
            
        else:
            self.second_frame.grid_forget()
        if name == "frame_3":
            self.third_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.third_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")
        self.geometry("800x450")

    def frame_2_button_event(self):
        self.select_frame_by_name("frame_2")
        self.geometry("1000x850")
        thread2 = Thread(target = self.load_anime_frame,args=(self.second_frame,))
        thread2.start()

    def frame_3_button_event(self):
        self.select_frame_by_name("frame_3")
        self.geometry("960x640")
        
        

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)


if __name__ == "__main__":
    app = App()
    app.mainloop()
    logger.debug("Main loop exited")
    cef.Shutdown()