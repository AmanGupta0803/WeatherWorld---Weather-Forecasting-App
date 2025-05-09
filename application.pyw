
import sys
import random
import datetime
import tkinter as tk
from tkinter import PhotoImage, messagebox
from PIL import ImageTk, Image
import requests

# ========== CONFIG ==========
API_KEY = 'd0f4215f39312e5de368ee8edad554b8'

PRIMARY_BG = "#212A3E"
SECONDARY_BG = "#394867"
ACCENT_BG = "#F1F6F9"
TITLE_FG = "#21E6C1"
LABEL_FG = "#F1F6F9"

ICON_SIZE = (40, 40)  # Standardize icon size

# ========== UTILITY ==========
def load_icon(path, size=ICON_SIZE):
    img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)

# ========== CUSTOM WIDGETS ==========
class CustomFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bd=0, relief=tk.FLAT, bg=SECONDARY_BG)
class CustomLabel(tk.Label):
    def __init__(self, parent, **kwargs):
        font = kwargs.pop('font', ('Segoe UI', 13))
        bg = kwargs.pop('bg', SECONDARY_BG)
        fg = kwargs.pop('fg', LABEL_FG)
        super().__init__(parent, font=font, bg=bg, fg=fg, **kwargs)
class PrimaryButton(tk.Button):
    def __init__(self, parent, **kwargs):
        font = kwargs.pop('font', ('Segoe UI', 12, 'bold'))
        bg = kwargs.pop('bg', TITLE_FG)
        fg = kwargs.pop('fg', "#212A3E")
        super().__init__(parent, font=font, bg=bg, fg=fg, activebackground="#23d1a7",
                         bd=0, relief=tk.FLAT, padx=12, pady=6, cursor='hand2', **kwargs)

# ========== MAIN APPLICATION ==========
class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.configure(bg=PRIMARY_BG)
        self.pack(fill="both", expand=True)

        self.city = tk.StringVar()
        self.icon_images = {}

        self.load_images()
        self.create_widgets()
        self.current_time()

    def load_images(self):
        # Wallpaper
        bg_list = [f'wallpapers/bg{i}.png' for i in range(1, 7)]
        bg_img_path = random.choice(bg_list)
        bg_img = Image.open(bg_img_path).resize((800, 500),)
        self.bg_image = ImageTk.PhotoImage(bg_img)
        
        # Icons (use consistent sizing for crisp look)
        self.icon_images = {
            "search": load_icon('icons/search.png', (30, 30)),
            "clear": load_icon('icons/clear.png'),
            "clouds": load_icon('icons/clouds.png'),
            "high_temp": load_icon('icons/high_temp.png'),
            "low_temp": load_icon('icons/low_temp.png'),
            "humidity": load_icon('icons/humidity.png'),
            "pressure": load_icon('icons/pressure.png'),
            "wind": load_icon('icons/wind.png'),
            "thunderstorm": load_icon('icons/thunderstorm.png'),
            "snow": load_icon('icons/snow.png'),
            "drizzle": load_icon('icons/drizzle.png'),
            "mist": load_icon('icons/mist.png'),
            "hail": load_icon('icons/hail.png'),
        }

    def create_widgets(self):
        # Background wallpaper
        bg_label = tk.Label(self, image=self.bg_image, bd=0)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Main frame
        main_frame = tk.Frame(self, bg=PRIMARY_BG)
        main_frame.place(relwidth=0.95, relheight=0.95, relx=0.025, rely=0.025)

        # Title
        title_label = tk.Label(main_frame, text="☁️ WeatherWorld", font=("Segoe UI", 28, 'bold'),
                               bg=PRIMARY_BG, fg=TITLE_FG, pady=12)
        title_label.pack(anchor='n', pady=10)

        # Search Bar
        search_frame = tk.Frame(main_frame, bg=PRIMARY_BG)
        search_frame.pack(pady=10)
        tk.Label(search_frame, text="Search City:", font=("Segoe UI", 13, "bold"),
                 bg=PRIMARY_BG, fg=LABEL_FG).pack(side="left", padx=(0,6))
        self.entry = tk.Entry(search_frame, textvariable=self.city, font=("Segoe UI", 13),
                              bg=ACCENT_BG, fg="#222", width=20, relief=tk.FLAT)
        self.entry.pack(side="left", padx=(0,6))
        self.entry.focus_set()
        search_btn = PrimaryButton(search_frame, image=self.icon_images["search"], 
                                   borderwidth=0, command=self.weather_search)
        search_btn.pack(side="left")
        self.master.bind('<Return>', self.get_weather)
        
        # Info Frame
        self.info_frame = tk.Frame(main_frame, bg=SECONDARY_BG, bd=7, relief="ridge")
        self.info_frame.pack(fill="both", expand=True, pady=24, padx=15)

        # City Label
        self.city_label = CustomLabel(self.info_frame, text="", font=("Segoe UI",15,"bold"),
                                      bg=SECONDARY_BG, anchor="center")
        self.city_label.grid(row=0, column=0, columnspan=4, pady=(0, 18), sticky="ew")

        # Datetime
        self.date_label = CustomLabel(self.info_frame, text=self.current_date(),
                                      font=("Segoe UI",13), bg=SECONDARY_BG, anchor="w")
        self.date_label.grid(row=1, column=0, sticky="w", padx=8)
        self.time_label = CustomLabel(self.info_frame, text="", font=("Segoe UI",13), anchor="w")
        self.time_label.grid(row=1, column=1, sticky="w", padx=8)

        # Weather metrics grid
        # Icons and labels for each metric
        self.widgets = {
            "weather": {"icon": "clear", "row": 2, "column": 0, "text": "Weather"},
            "temperature": {"icon": "high_temp", "row": 2, "column": 1, "text": "Temp (°C)"},
            "humidity": {"icon": "humidity", "row": 2, "column": 2, "text": "Humidity (%)"},
            "windspeed": {"icon": "wind", "row": 2, "column": 3, "text": "Windspeed (m/s)"},
            "pressure": {"icon": "pressure", "row": 3, "column": 0, "text": "Pressure (hPa)"},
        }
        self.display_labels = {}
        for key, val in self.widgets.items():
            icon_lbl = tk.Label(self.info_frame, image=self.icon_images[val["icon"]],
                                bg=SECONDARY_BG)
            icon_lbl.grid(row=val["row"], column=val["column"], pady=(0,2))
            text_lbl = CustomLabel(self.info_frame, text=val["text"], font=("Segoe UI", 12, "bold"))
            text_lbl.grid(row=val["row"]+1, column=val["column"])
            data_lbl = CustomLabel(self.info_frame, text="--", font=("Segoe UI", 15, "bold"))
            data_lbl.grid(row=val["row"]+2, column=val["column"], pady=(0,12))
            self.display_labels[key] = data_lbl

    def current_time(self):
        dt = datetime.datetime.now()
        self.time_label['text'] = dt.strftime('%I:%M:%S %p')
        self.time_label.after(1000, self.current_time)

    def current_date(self):
        dt = datetime.datetime.today()
        return dt.strftime('%d %b, %Y')

    def weather_search(self):
        # Triggered by button
        self.get_weather()

    def get_weather(self, event=None):
        city = self.city.get()
        if len(city) > 2:
            url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}'
            try:
                r = requests.get(url, timeout=5)
                data = r.json()
                if data.get('cod') != 200:
                    raise KeyError("Invalid city")

                weather = data['weather'][0]['description'].capitalize()
                temp = round(data['main']['temp'] - 273.15, 1)
                windspeed = data['wind']['speed']
                humidity = data['main']['humidity']
                pressure = data['main']['pressure']

                # Update metrics on UI
                self.display_labels["weather"].config(text=weather)
                self.display_labels["temperature"].config(text=f"{temp}°C")
                self.display_labels["humidity"].config(text=f"{humidity}%")
                self.display_labels["windspeed"].config(text=f"{windspeed} m/s")
                self.display_labels["pressure"].config(text=f"{pressure} hPa")
                self.city_label.config(text=f"Weather in {city.title()}")

                # Icon logic for current weather
                weather_lower = weather.lower()
                icon_map = [
                    ("thunder", "thunderstorm"),
                    ("cloud", "clouds"),
                    ("snow", "snow"),
                    ("drizzle", "drizzle"),
                    ("rain", "drizzle"),
                    ("mist", "mist"),
                    ("haze", "mist"),
                    ("fog", "mist"),
                    ("smoke", "mist"),
                    ("hail", "hail"),
                ]
                icon_key = "clear"
                for w, k in icon_map:
                    if w in weather_lower:
                        icon_key = k
                        break
                self.info_frame.grid_slaves(row=self.widgets["weather"]["row"], column=self.widgets["weather"]["column"])[0].config(
                    image=self.icon_images[icon_key]
                )
                t_icon = "high_temp" if temp > 18 else "low_temp"
                self.info_frame.grid_slaves(row=self.widgets["temperature"]["row"], column=self.widgets["temperature"]["column"])[0].config(
                    image=self.icon_images[t_icon]
                )
            except KeyError:
                messagebox.showerror('WeatherWorld', 'No such city in database', parent=self)
            except Exception:
                messagebox.showerror('WeatherWorld', 'No Internet Connection', parent=self)
            self.entry.delete(0, tk.END)

# ========== RUN APP ==========
if __name__ == '__main__':
    root = tk.Tk()
    root.title('WeatherWorld')
    root.geometry("820x575")
    root.resizable(False, False)

    if not API_KEY:
        root.withdraw()
        messagebox.showerror('WeatherWorld', 'OpenWeatherMap API Key is required to use this app')
        sys.exit(0)

    app = Application(master=root)
    app.mainloop()

