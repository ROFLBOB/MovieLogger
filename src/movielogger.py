from connect import Connect
from movie import Movie
from watchlist import Watchlist
from tkinter import ttk, DISABLED, NORMAL, PhotoImage
from PIL import Image, ImageTk
import tkinter as tk

class MovieLogger():
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Logger")
        self.root.geometry("800x800")

        #add menu bar
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        #File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit")
        
        #Watchlist
        watchlist_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Watchlist", menu=watchlist_menu)
        watchlist_menu.add_command(label="View Watchlist")
        watchlist_menu.add_command(label="Export")  

        #Review
        review_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Review", menu=review_menu)
        review_menu.add_command(label="Add/Update Review")
        review_menu.add_command(label="Read Review")

        #Movie
        movie_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Movie", menu=movie_menu)
        movie_menu.add_command(label="Lookup")
    


        #create labels for interface


        #create buttons for interface


