from connect import Connect
from movie import Movie
from watchlist import Watchlist
from tkinter import ttk, DISABLED, NORMAL, PhotoImage, LEFT, font, Scale, DoubleVar, scrolledtext
from PIL import Image, ImageTk
import tkinter as tk
from format import WrappingLabel
import requests
from io import BytesIO

def generateUI():
    root = tk.Tk()
    app = MovieLogger(root)
    root.mainloop()

class MovieLogger():
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Logger")
        self.root.geometry("800x800")

        self._OMDB_URL = "http://www.omdbapi.com/"

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
        self.file_menu.add_command(label="Exit", command=self.exit_program)
        
        #Watchlist
        self.watchlist_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Watchlist", menu=self.watchlist_menu)
        self.watchlist_menu.add_command(label="Toggle Watchlist", command = self.toggle_frame)
        self.watchlist_menu.add_command(label="Export")  

        #Review
        self.review_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Review", menu=self.review_menu)
        self.review_menu.add_command(label="Add/Update Review")
        self.review_menu.add_command(label="Read Review")

        #Create custom fonts
        self.bold = font.Font(weight="bold")

        #create the watchlist that holds the list of movie objects
        self.watchlist = []

        #load watchlist from file
        #to do
    
        #create the frames
        self.watchlist_frame = tk.Frame(self.root)
        self.watchlist_frame.grid(row=4, column=0, columnspan=3, sticky="nsew")
        
        #Statuses
        self.STATUS = ["Error!","Awaiting Lookup", "Results fetched", "Type a Movie Name"]

        #create labels for interface & grid them
        self.search_label = tk.Label(self.root, text="Movie Search")
        self.search_label.grid(row=0, column=0, sticky="nsew")
        self.status_label = tk.Label(self.root, text=self.STATUS[1])
        self.status_label.grid(row=1, column=0, sticky="nsew")
        self.watchlist_label = tk.Label(self.watchlist_frame, text="Watchlist")
        self.watchlist_label.grid(row=0, column = 0, sticky="nsew")

        #create buttons for interface & grid them
        self.search_button = tk.Button(self.root, text="Search Now", command=self.search)
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

        #set up the frame container for the search results
        self.movies_container = tk.Frame(self.search_results_canvas)
        self.movies_container.grid_columnconfigure(0, weight=1) #column 0 expands

        self.search_results_window = self.search_results_canvas.create_window((0,0), window=self.movies_container, anchor="nw")


        #add event bindings
        #this one sets the width of the search_results_window to be the width of the search_results_canvas
        self.search_results_canvas.bind(
            "<Configure>",
            lambda e: self.search_results_canvas.itemconfig(self.search_results_window, width=self.search_results_canvas.winfo_width())
        )

        #individual movie frame
        #col 1: thumbnail
        #col 2: Movie Info (TItle, Year, Rating)
        #col 3: Lookup Button
        #col 4: Watchlist button
        #col 5: Favorite
        #col 6: Review button

        #set weights for columns and rows (changes the size compared to other cells)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(4, weight=1)
        self.watchlist_frame.rowconfigure(1, weight=1)
        self.watchlist_frame.columnconfigure(0, weight=1)
        self.movies_container.grid_columnconfigure(0, weight=1)
        self.movies_container.grid_rowconfigure(0, weight=1)
        
        #List of movies from most recent Search
        self.movies_query = None

        self.watchlist_container = tk.Frame(self.watchlist_canvas)
        self.watchlist_window = self.watchlist_canvas.create_window((0,0), window=self.watchlist_container, anchor="nw")
        
    #search button function
    def search(self):
        search_query = self.search_field.get()
        if len(search_query)<=0:
            self.set_status_label(3)
            return
        connection = Connect("http://www.omdbapi.com/")
        self.movies_query = connection.search(search_query)
        if self.movies_query == None:
            self.set_status_label(0)
            print(self.movies_query)
            return
        self.set_status_label(2)

        #for each movie in self.movies_query, use the movie info to create a new movies frame and pack it to the search frame
        num_movies = 0

        #parent object of single movie frame must have weight so it expands
        self.movies_container.grid_columnconfigure(0,weight=1)

        for movie in self.movies_query:
            single_movie_frame = tk.Frame(self.movies_container)
            single_movie_frame.movie = movie
            if not (isinstance(movie, Movie)):
                raise TypeError("movie must be a Movie object")

            #download the poster
            poster = self.download_movie_poster(movie)

            #make the labels
            title_label = tk.Label(single_movie_frame, text=movie.get_title())
            year_label = tk.Label(single_movie_frame, text=movie.get_year())
            id_label = tk.Label(single_movie_frame, text=movie.get_id())
            thumbnail_label = tk.Label(single_movie_frame, text="URL", image=poster)

            #make the buttons
            lookup_button = tk.Button(single_movie_frame, text="Lookup", command=lambda m=movie: self.lookup_movie(m))
            watchlist_button = tk.Button(single_movie_frame, text="Watchlist", command=lambda m=movie: self.add_to_watchlist(m))
            favorites_button = tk.Button(single_movie_frame, text="Favorite")
            review_button = tk.Button(single_movie_frame, text="Review", command=lambda m=movie: self.open_reviews(m))

            #grid the labels to the frame
            thumbnail_label.grid(row=0, column=0, rowspan=3, sticky="nsew")
            title_label.grid(row=0, column=1, sticky="nsew")
            year_label.grid(row=1, column=1, sticky="nsew")
            id_label.grid(row=2, column=1, sticky="nsew")

            #grid the buttons
            lookup_button.grid(row=0, column=2, sticky="nsew")
            watchlist_button.grid(row=0, column=3, sticky="nsew")
            favorites_button.grid(row=0, column=4, sticky="nsew") 
            review_button.grid(row=0, column=5, sticky="nsew")

            #grid the frame to self.movies_container
            single_movie_frame.grid(row = num_movies, column = 0, sticky="nsew")
            single_movie_frame.config(highlightbackground = "green", borderwidth=1, highlightthickness=1)

            #set the weights
            single_movie_frame.grid_columnconfigure(0, weight=1)
            single_movie_frame.grid_columnconfigure(1, weight=1)
            single_movie_frame.grid_rowconfigure(num_movies, weight=1)


            num_movies += 1



        self.search_results_canvas.update_idletasks()
        self.search_results_canvas.config(scrollregion=self.search_results_canvas.bbox("all"))
        print(self.movies_query)

        
    #updated the status label on the main window
    def set_status_label(self,status):
        self.status_label.config(text=self.STATUS[status])

    def exit_program(self):
        self.root.destroy()
        self.root.quit()

    def toggle_frame(self):
        if self.watchlist_frame.winfo_ismapped():
            self.watchlist_frame.grid_forget()
            self.watchlist_scrollbar.grid_forget()
            self.root.rowconfigure(2, weight=5)
            self.root.rowconfigure(4, weight=0)
        else:
            self.watchlist_frame.grid(row=4, column=0, columnspan=3, sticky="nsew")
            self.watchlist_scrollbar.grid(row=5, column=0, columnspan=3, sticky="ew")
            self.root.rowconfigure(2, weight=1)
            self.root.rowconfigure(4, weight=1)
    
    #adds the movie to the watchlist
    #takes a movie object
    def add_to_watchlist(self, movie):
        if movie in self.watchlist:
            print(f"{movie.get_title()} already in watchlist!")
            return
        self.watchlist.append(movie)
        #create the frame and pack it to self.watchlist_container
        watchlist_movie_frame = tk.Frame(self.watchlist_container)
        watchlist_movie_frame.movie = movie
        URL_label = tk.Label(watchlist_movie_frame,image=movie.get_poster_image()).grid(column=0,row=0)
        title_label = tk.Label(watchlist_movie_frame,text=movie.get_title(), font=self.bold).grid(column=0,row=2)
        lookup_button = tk.Button(watchlist_movie_frame, text="Lookup", command=lambda m=movie: self.lookup_movie(m)).grid(column=1, row=0)
        remove_from_watchlist_button = tk.Button(watchlist_movie_frame, text="-", command=lambda m=movie:self.remove_movie_from_watchlist(m)).grid(column=1,row=1)
        watchlist_movie_frame.pack(side=LEFT)

        #reset the scrollable region after updating the frame
        self.watchlist_canvas.update_idletasks()
        self.watchlist_canvas.config(scrollregion=self.watchlist_canvas.bbox("all"))

        print(f"Added {movie.get_title()} to self.watchlist")
        return watchlist_movie_frame

    #opens a new top level window that has more information about the movie such as a bigger thumbnail, actors, plot, etc
    #takes a movie object
    def lookup_movie(self, movie=None):
        if movie is None:
            print("error, lookup button clicked and movie is None")
            return
        print(f"Looking up movie: {movie.get_title()}, {movie.get_id}")
        #find the name of the movie frame that was clicked
        lookup_window = tk.Toplevel(self.root)
        lookup_window.geometry("400x400")
        lookup_window.movie = movie

        #from here, connect to the API and search for the ttid. Then, gather the extra information and display it in a window
        movie_lookup = Connect(self._OMDB_URL)
        full_movie_info = movie_lookup.lookup(movie.get_id())
        lookup_window.title(movie.get_title())

        #get string for metadata
        metadata = f"Released: {full_movie_info.get_released()}\nRating: {full_movie_info.get_rating()}\n"\
                    f"Director: {full_movie_info.get_director()}\nBox Office: {full_movie_info.get_boxoffice()}"
        
        #configure column weights
        lookup_window.columnconfigure(0,weight=1)
        lookup_window.columnconfigure(1, weight=2)



        #grid the labels to the lookup_window
        tk.Label(lookup_window, text="Movie Lookup:", justify="left", anchor="w").grid(column=0, row=0, sticky="nsew")
        tk.Label(lookup_window, image=movie.get_poster_image(), justify="left", anchor="w").grid(column=0,row=1, sticky="nsew")
        tk.Label(lookup_window, text=full_movie_info.get_title(), justify="left", anchor="w", font=self.bold).grid(column=1,row=0, sticky="nsew")
        tk.Label(lookup_window, text=metadata, justify="left", anchor="w").grid(column=1, row=1, sticky="nsew")
        WrappingLabel(lookup_window, text=f"Plot: {full_movie_info.get_plot()}", justify="left", anchor="w", wraplength=400).grid(column=0, row=2, columnspan=2, sticky="nsew")

    #remove specific movie from the watchlist
    def remove_movie_from_watchlist(self,movie):
        for m in self.watchlist:
            if m == movie:
                self.watchlist.remove(m)
                print(f"{m.get_title()} removed from the watchlist.")
        
        #loop through the frames in the watchlist window and check to see if the frame's movie is equal to the movie
        for element in self.watchlist_container.winfo_children():
            if element.movie == movie:
                element.destroy()



    #adds the movie to the favorites list
    def add_to_favorites(self, movie):
        return
    
    #open the personal review for the specified movie
    def open_reviews(self, movie):
        reviews_panel = tk.Toplevel(self.root)
        reviews_panel.geometry("600x600")
        reviews_panel.title(f"Review for {movie.get_title()}")

        review_scale = Scale(reviews_panel, variable=DoubleVar, from_=0.5, to=5.0, tickinterval=0.5, orient="horizontal", length=500, resolution=0.5)
        
        if movie.get_review_score() == None:
            review_scale.set(3.0)
        else:
            review_scale.set(movie.get_review_score())

        #set_review_button = tk.Button(reviews_panel, text="Save Review", command=lambda m=movie:m.set_review_score(review_scale.get()))
        set_review_button = tk.Button(reviews_panel, text="Save Review", command=lambda m=movie:self.set_review(m, review_scale, written_review))

        written_review = scrolledtext.ScrolledText(reviews_panel, wrap=tk.WORD, width=80, height=20)

        if movie.get_review_text() != None:
            written_review.insert(tk.END, movie.get_review_text())

        review_scale.pack()
        written_review.pack()
        set_review_button.pack()


        return
    
    def set_review(self, movie, scale, textbox):
        movie.set_review_score(scale.get())
        review_text = textbox.get("1.0", tk.END)
        movie.set_review_text(review_text)
        return movie

    
    #takes a movie and returns a thumbnail image to be used in a label
    def download_movie_poster(self,movie):
        url = movie.get_thumbnail_url()
        download = requests.get(url,stream=True)
        image_data = BytesIO(download.content)
        image = Image.open(image_data)
        image.thumbnail((150,150))
        thumbnail = ImageTk.PhotoImage(image)
        movie.set_poster_image(thumbnail)
        return thumbnail
            


generateUI()

