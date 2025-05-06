from connect import Connect
from movie import Movie
from watchlist import Watchlist
from tkinter import ttk, DISABLED, NORMAL, PhotoImage
from PIL import Image, ImageTk
import tkinter as tk

def generateUI():
    root = tk.Tk()
    app = MovieLogger(root)
    root.mainloop()

class MovieLogger():
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Logger")
        self.root.geometry("800x800")

        #get default background color
        bg_color = root.cget("background")
        rgb = root.winfo_rgb(bg_color)
        self.bg_color_code = "#%x%x%x" % rgb

        #add menu bar
        self.menubar = tk.Menu(root)
        root.config(menu=self.menubar)

        #File
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Exit")
        
        #Watchlist
        self.watchlist_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Watchlist", menu=self.watchlist_menu)
        self.watchlist_menu.add_command(label="View Watchlist")
        self.watchlist_menu.add_command(label="Export")  

        #Review
        self.review_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Review", menu=self.review_menu)
        self.review_menu.add_command(label="Add/Update Review")
        self.review_menu.add_command(label="Read Review")

        #Movie
        self.movie_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Movie", menu=self.movie_menu)
        self.movie_menu.add_command(label="Lookup")
    
        #create the frames
        self.watchlist_frame = tk.Frame(self.root)
        self.watchlist_frame.grid(row=4, column=0, columnspan=3, sticky="nsew")

        #create labels for interface & grid them
        self.search_label = tk.Label(self.root, text="Movie Search")
        self.search_label.grid(row=0, column=0, sticky="nsew")
        self.status_label = tk.Label(self.root, text="Awaiting lookup")
        self.status_label.grid(row=1, column=0, sticky="nsew")
        self.watchlist_label = tk.Label(self.watchlist_frame, text="Watchlist")
        self.watchlist_label.grid(row=0, column = 0, sticky="nsew")

        #create buttons for interface & grid them
        self.search_button = tk.Button(self.root, text="Search Now")
        self.search_button.grid(row=0, column=2, columnspan=2, sticky="nsew")
        
        #create text input for interface & grid them
        self.search_field = tk.Entry(self.root)
        self.search_field.grid(row=0, column=1, sticky="nsew")
        
        #create the canvases & grid it
        self.search_results_canvas = tk.Canvas(self.root, bg=bg_color, highlightbackground="blue")
        self.search_results_canvas.grid(row=2, column=0, columnspan=3, sticky="nsew")
        self.watchlist_canvas = tk.Canvas(self.watchlist_frame, bg=bg_color, highlightbackground="blue")
        self.watchlist_canvas.grid(row=1, column=0, columnspan=3, sticky="nsew")
    

        #create scrollbar within the search_results canvas
        self.search_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.search_results_canvas.yview)
        self.search_results_canvas.config(yscrollcommand=self.search_scrollbar.set)
        self.search_scrollbar.grid(row=2, column=3, sticky="ns")

        #create scrollbar for the watchlist_canvas
        self.watchlist_scrollbar = ttk.Scrollbar(self.root, orient="horizontal", command=self.watchlist_canvas.xview)
        self.watchlist_canvas.config(xscrollcommand=self.watchlist_scrollbar.set)
        self.watchlist_scrollbar.grid(row=5, column=0, columnspan=3, sticky="ew")


        #set weights for columns and rows (changes the size compared to other cells)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(4, weight=1)
        self.watchlist_frame.rowconfigure(1, weight=1)
        self.watchlist_frame.columnconfigure(0, weight=1)


generateUI()
