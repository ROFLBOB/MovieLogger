from connect import Connect
from movie import Movie
from watchlist import Watchlist
from tkinter import ttk, DISABLED, NORMAL, PhotoImage, LEFT, font, Scale, DoubleVar, scrolledtext
from PIL import Image, ImageTk
import tkinter as tk
from format import WrappingLabel
import requests, json
from io import BytesIO
from requests.exceptions import ConnectionError, MissingSchema

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
        self.total_results = "0"
        self.current_page = 1
        self.total_pages = 1


        #load movies from watchlist if there are any saved
        self.watchlist = self.load_movies_from_file("watchlist.json")

        #load reviews doc
        self.movie_reviews = self.load_reviews_from_file("reviews.json")
        
        #favorites list
        self.favorites = self.load_movies_from_file("favorites.json")

        #print(self.watchlist)

        #add menu bar
        self.menubar = tk.Menu(root)
        root.config(menu=self.menubar)

        #File
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Set API Key", command=self.edit_api)
        self.file_menu.add_command(label="Exit", command=self.exit_program)
        
        #Watchlist
        self.watchlist_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Watchlist", menu=self.watchlist_menu)
        self.watchlist_menu.add_command(label="Toggle Watchlist", command = self.toggle_frame)
        self.watchlist_menu.add_command(label="Save Watchlist", command=lambda: self.save_movies_to_file(self.watchlist, "watchlist.json"))

        #Favorites
        self.favorites_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Favorites", menu=self.favorites_menu)
        self.favorites_menu.add_command(label="View Favorites", command=lambda: self.open_favorites_window())

        #Review
        self.review_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Review", menu=self.review_menu)
        self.review_menu.add_command(label="Add/Update Review")
        self.review_menu.add_command(label="Read Review")

        #Create custom fonts
        self.bold = font.Font(weight="bold")
    
        #create the frames
        self.watchlist_frame = tk.Frame(self.root)
        self.watchlist_frame.grid(row=4, column=0, columnspan=3, sticky="nsew")
        
        #Statuses
        self.STATUS = ["Error!","Awaiting Lookup", "Results fetched", "Type a Movie Name", "No movies found."]

        #create labels for interface & grid them
        self.search_label = tk.Label(self.root, text="Movie Search")
        self.search_label.grid(row=0, column=0, sticky="nsew")
        self.status_label = tk.Label(self.root, text=self.STATUS[1])
        self.status_label.grid(row=1, column=0, sticky="nsew")
        self.watchlist_label = tk.Label(self.watchlist_frame, text="Watchlist")
        self.watchlist_label.grid(row=0, column = 0, sticky="nsew")
        self.total_results_label = tk.Label(self.root, text=f"Search Results: {self.total_results}\nCurrent Page: {self.current_page}")
        self.total_results_label.grid(row=3, column=0, sticky="nsew")

        #create buttons for interface & grid them
        self.search_button = tk.Button(self.root, text="Search Now", command=self.search)
        self.search_button.grid(row=0, column=2, columnspan=2, sticky="nsew")
        self.prev_page_button = tk.Button(self.root, text="Previous Page", state=DISABLED)
        self.prev_page_button.grid(row=3, column=1, sticky="nsew")
        self.next_page_button = tk.Button(self.root, text="Next Page", state=DISABLED)
        self.next_page_button.grid(row=3, column=2, sticky="nsew")
        
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

        for entry in self.watchlist:
            self.add_movie_frame_to_watchlist(entry)

        self.favorites_panel = None

        
    #search button function
    def search(self, page=1):
        search_query = self.search_field.get()
        if len(search_query)<=0:
            self.set_status_label(3)
            return
        connection = Connect("http://www.omdbapi.com/")
        self.movies_query = connection.search(search_query, page)
        #print(f"Movies Query:{self.movies_query}")

        #for each movie in self.movies_query, use the movie info to create a new movies frame and pack it to the search frame
        num_movies = 0

        if self.movies_query == "No movies found.":
            #no movies found so setting status label and returning early
            self.set_status_label(4)
            return
        #there's at least one movie returned
        self.set_status_label(2)

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
            title_label = WrappingLabel(single_movie_frame, text=movie.get_title())
            year_label = tk.Label(single_movie_frame, text=movie.get_year())
            id_label = tk.Label(single_movie_frame, text=movie.get_id())
            if poster == None:
                thumbnail_label = tk.Label(single_movie_frame, text="Not Available")
            else:
                thumbnail_label = tk.Label(single_movie_frame, text="URL", image=poster)

            #make the buttons
            lookup_button = tk.Button(single_movie_frame, text="Lookup", command=lambda m=movie: self.lookup_movie(m))
            watchlist_button = tk.Button(single_movie_frame, text="Watchlist", command=lambda m=movie: self.add_to_watchlist(m))
            favorites_button = tk.Button(single_movie_frame, text="Favorite", command=lambda m=movie: self.add_to_favorites(m))
            review_button = tk.Button(single_movie_frame, text="Review", command=lambda m=movie: self.open_reviews(m))

            #grid the labels to the frame
            thumbnail_label.grid(row=0, column=0, rowspan=3, sticky="nsew")
            title_label.grid(row=0, column=1, sticky="nsew")
            year_label.grid(row=1, column=1, sticky="nsew")
            id_label.grid(row=2, column=1, sticky="nsew")

            #grid the buttons
            lookup_button.grid(row=0, column=2, rowspan=3, sticky="nsew")
            watchlist_button.grid(row=0, column=3, rowspan=3, sticky="nsew")
            favorites_button.grid(row=0, column=4, rowspan=3, sticky="nsew") 
            review_button.grid(row=0, column=5, rowspan=3, sticky="nsew")

            #grid the frame to self.movies_container
            single_movie_frame.grid(row = num_movies, column = 0, sticky="nsew")
            single_movie_frame.config(highlightbackground = "green", borderwidth=1, highlightthickness=1)

            #set the weights
            single_movie_frame.grid_columnconfigure(0, weight=1)
            single_movie_frame.grid_columnconfigure(1, weight=1)
            single_movie_frame.grid_rowconfigure(num_movies, weight=1)


            num_movies += 1


        #update pagination buttons
        self.update_pagination_controls(connection.total_results, page)

        self.search_results_canvas.update_idletasks()
        self.search_results_canvas.config(scrollregion=self.search_results_canvas.bbox("all"))
        #print(self.movies_query)

    def update_pagination_controls(self, total_results, current_page):
        self.current_page = current_page
        #calculate total pages
        total_pages = (int(total_results)+9)//10 

        #update results label
        self.total_results_label.config(
            text=f"Search Results: {total_results}\nPage: {current_page}/{total_pages}"
        )

        #update previous button
        if current_page <= 1:
            self.prev_page_button.config(state=DISABLED)
        else:
            self.prev_page_button.config(
                state=tk.NORMAL,
                command=lambda:self.search(page=current_page-1)
            )
        
        #update next button
        if current_page >= total_pages:
            self.next_page_button.config(state=tk.DISABLED)
        else:
            self.next_page_button.config(
                state=tk.NORMAL,
                command=lambda: self.search(page=current_page+1)
            )
        
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
        #print(f"Added {movie.get_title()} to self.watchlist")
        #create the frame and pack it to self.watchlist_container
        self.add_movie_frame_to_watchlist(movie)

    def add_movie_frame_to_watchlist(self, movie):
        watchlist_movie_frame = tk.Frame(self.watchlist_container)
        watchlist_movie_frame.movie = movie
        if movie.get_poster_image() == None:
            URL_label = tk.Label(watchlist_movie_frame,text="Not Available").grid(column=0,row=0)
        else:
            URL_label = tk.Label(watchlist_movie_frame,image=movie.get_poster_image()).grid(column=0,row=0)
        title_label = tk.Label(watchlist_movie_frame,text=movie.get_title(), font=self.bold).grid(column=0,row=2)
        lookup_button = tk.Button(watchlist_movie_frame, text="Lookup", command=lambda m=movie: self.lookup_movie(m)).grid(column=1, row=0)
        remove_from_watchlist_button = tk.Button(watchlist_movie_frame, text="-", command=lambda m=movie:self.remove_movie_from_watchlist(m)).grid(column=1,row=1)
        watchlist_movie_frame.pack(side=LEFT)

        #reset the scrollable region after updating the frame
        self.watchlist_canvas.update_idletasks()
        self.watchlist_canvas.config(scrollregion=self.watchlist_canvas.bbox("all"))

        
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
        if full_movie_info == None:
            #there's an error, return None
            print("error in lookup, connection error")
            tk.Label(lookup_window, text="Connection error.", font=self.bold, fg="red").grid(row=0, column=0, sticky="nsew")
            return None
        lookup_window.title(movie.get_title())

        #get string for metadata
        metadata = f"Released: {full_movie_info.get_released()}\nRating: {full_movie_info.get_rating()}\n"\
                    f"Director: {full_movie_info.get_director()}\nBox Office: {full_movie_info.get_boxoffice()}"
        
        #configure column weights
        lookup_window.columnconfigure(0,weight=1)
        lookup_window.columnconfigure(1, weight=2)
        review_score = None
        #check review score
        for each in self.movie_reviews:
            if lookup_window.movie.get_id() == each.get("imdbID"):
                review_score = each.get("Review Score")
        
        if review_score == None:
            review_score = "No Review Saved"

        #grid the labels to the lookup_window
        tk.Label(lookup_window, text="Movie Lookup:", justify="left", anchor="w").grid(column=0, row=0, sticky="nsew")
        if movie.get_poster_image()==None:
            tk.Label(lookup_window, text="Not Available", justify="left", anchor="w").grid(column=0,row=1, sticky="nsew")
        else:
            tk.Label(lookup_window, image=movie.get_poster_image(), justify="left", anchor="w").grid(column=0,row=1, sticky="nsew")    
        tk.Label(lookup_window, text=full_movie_info.get_title(), justify="left", anchor="w", font=self.bold).grid(column=1,row=0, sticky="nsew")
        tk.Label(lookup_window, text=metadata, justify="left", anchor="w").grid(column=1, row=1, sticky="nsew")
        WrappingLabel(lookup_window, text=f"Plot: {full_movie_info.get_plot()}", justify="left", anchor="w", wraplength=400).grid(column=0, row=2, columnspan=2, sticky="nsew")
        tk.Label(lookup_window, text=f"Score: {review_score}", justify="left", anchor="w").grid(column=0, row=3, sticky="nsew")
        if lookup_window.movie in self.watchlist:
            tk.Button(lookup_window, text="In Watchlist", state=tk.DISABLED).grid(column=0,row=4, sticky="nsew")    
        else:
            tk.Button(lookup_window, text="Add To Watchlist", command=lambda: self.add_to_watchlist(lookup_window.movie)).grid(column=0,row=4, sticky="nsew")
        if lookup_window.movie in self.favorites:
            tk.Button(lookup_window, text="In Favorites", state=tk.DISABLED).grid(column=1,row=4, sticky="nsew")
        else:
            tk.Button(lookup_window, text="Favorite", command=lambda : self.add_to_favorites(lookup_window.movie)).grid(column=1,row=4, sticky="nsew")
        tk.Button(lookup_window, text="Review", command=lambda : self.open_reviews(lookup_window.movie)).grid(column=2,row=4, sticky="nsew")
        

    #remove specific movie from the watchlist
    def remove_movie_from_watchlist(self,movie):
        for m in self.watchlist:
            if m == movie:
                self.watchlist.remove(m)
                #print(f"{m.get_title()} removed from the watchlist.")
        
        #loop through the frames in the watchlist window and check to see if the frame's movie is equal to the movie
        for element in self.watchlist_container.winfo_children():
            if element.movie == movie:
                element.destroy()
    
   

    #be a good programmer and swap out remove_from_watchlist and remove_from_favorites with function below
    def remove_movie_from_list(self, movie, list_of_movies):
        #remove movie from the list
        for m in list_of_movies:
            if m == movie:
                list_of_movies.remove(m)
                print(f"Removed {m} from list.")
        #remove movie frame from the window


    #remove specific movie from favorites
    def remove_movie_from_favorites(self, movie, frame):
        if movie in self.favorites:
            self.favorites.remove(movie)
            self.refresh_favorites_window()

    def refresh_favorites_window(self):
        #clear the current favorites window
        for widget in self.favorites_panel.winfo_children():
            widget.destroy()

        #rebuild the panel
        for each in self.favorites:
            favorite_movie_frame = tk.Frame(self.favorites_panel)
            favorite_movie_frame.movie = each.get_title()
            tk.Label(favorite_movie_frame, text=f"{each.get_title()}", font=self.bold).grid(row=0, column=0, sticky="nsew")
            tk.Button(favorite_movie_frame, text=f"Lookup", command=lambda m=each:self.lookup_movie(m)).grid(row=0, column=1, sticky="nsew")
            tk.Button(favorite_movie_frame, text=f"Remove from Favorites", command=lambda m=each: self.remove_movie_from_favorites(m,favorite_movie_frame)).grid(row=0, column=2, sticky="nsew")
            favorite_movie_frame.pack()
            

    #adds the movie to the favorites list
    def add_to_favorites(self, movie):
        if movie in self.favorites:
            return
        self.favorites.append(movie)
        #save to favorites.json
        self.save_movies_to_file(self.favorites, "favorites.json")
        print(f"Full favorites List: {self.favorites}")

    def open_favorites_window(self):
        self.favorites_panel = tk.Toplevel(self.root)
        self.favorites_panel.geometry("600x600")
        self.favorites_panel.title("Favorite Movies")
        self.refresh_favorites_window()
    
    #open the personal review for the specified movie
    def open_reviews(self, movie):
        reviews_panel = tk.Toplevel(self.root)
        reviews_panel.geometry("600x600")
        reviews_panel.title(f"Review for {movie.get_title()}")
        review_score = 3.0
        #check if movie has a review in the self.movie_reviews list
        #print(f"reviews list: {self.movie_reviews}")
        for review in self.movie_reviews:
            if review.get("imdbID") == movie.get_id():
                #movie has a review, set review text and score
                movie.set_review_text(review.get("Review"))
                movie.set_review_score(review.get("Review Score"))
                review_score = movie.get_review_score()

        review_scale = Scale(reviews_panel, variable=DoubleVar, from_=0.5, to=5.0, tickinterval=0.5, orient="horizontal", length=500, resolution=0.5)
        review_scale.set(review_score)
        
        #set_review_button = tk.Button(reviews_panel, text="Save Review", command=lambda m=movie:m.set_review_score(review_scale.get()))
        set_review_button = tk.Button(reviews_panel, text="Save Review", command=lambda m=movie:self.set_review(m, review_scale, written_review))

        written_review = scrolledtext.ScrolledText(reviews_panel, wrap=tk.WORD, width=80, height=20)
        #print(written_review)
        if movie.get_review_text() != None:
            written_review.insert(tk.END, movie.get_review_text())
        review_scale.pack()
        written_review.pack()
        set_review_button.pack()
        return
    
    def open_all_reviews_window(self):
        return
    
    def set_review(self, movie, scale, textbox):
        movie.set_review_score(scale.get())
        review_text = textbox.get("1.0", tk.END)
        movie.set_review_text(review_text)
        self.movie_reviews.append(movie.review_to_dictionary())
        #print(f"{movie.get_title()} now has a review: {movie.get_review_text()}")
        self.save_movie_review(movie, "reviews.json")
        return movie

    
    #takes a movie and returns a thumbnail image to be used in a label
    def download_movie_poster(self,movie):
        if movie.get_thumbnail_url() == None or movie.get_thumbnail_url() == 'N/A':
            return None
        url = movie.get_thumbnail_url()
        try:
            download = requests.get(url,stream=True)
        except (ConnectionError, MissingSchema) as e:
            print(f"poster unavailable: {e}")
            return
        if download.status_code != 200:
            return
        image_data = BytesIO(download.content)
        image = Image.open(image_data)
        image.thumbnail((150,150))
        thumbnail = ImageTk.PhotoImage(image)
        movie.set_poster_image(thumbnail)
        return thumbnail
    
    def save_movies_to_file(self, movies, filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([movie.to_dictionary() for movie in movies], f, indent=4)
            #print(f"added to file")

    #figure out how to save the reviews to a file
    #should be an xml file, movie_reviews [{"ttid": "12345", "Review Score": 3.0, "Review": "Movie Review Here"}]
    def save_movie_review(self, movie, filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.movie_reviews, f, indent=4)
            #print(f"reviews saved.")
    
    def load_movies_from_file(self,filename):
        movies = []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    movie = Movie()
                    movie = movie.load_from_dictionary(item)
                    thumbnail = self.download_movie_poster(movie)
                    movie.set_poster_image(thumbnail)
                    movies.append(movie)
        except FileNotFoundError:
            print(f"{filename} not found. Returning empty list.")
        except Exception:
            print("Error, returning empty list")
        return movies
    
    def load_reviews_from_file(self, filename):
        reviews = []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(data)
                for movie in data:
                    #print(movie)
                    reviews.append({"imdbID":movie["imdbID"],"Review Score":movie["Review Score"],"Review":movie["Review"]})
                return reviews
        except FileNotFoundError:
            print(f"{filename} not found, returning empty list")
            return reviews
        except Exception:
            print(f"Error. Returning empty list.")
            return reviews

    def edit_api(self):
        api_panel = tk.Toplevel(self.root)
        api_panel.geometry("300x300")
        api_panel.title(f"API Key")
        tk.Label(api_panel, text="Enter OMDB API Key:").pack()
        self.api_field = tk.Entry(api_panel)
        self.api_field.pack()
        save_api_button = tk.Button(api_panel,text="Save", command=self.save_api_key)
        save_api_button.pack()
        self.api_status=tk.Label(api_panel, text="")
        self.api_status.pack()


        #load existing key if possible
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if "API_KEY" in line:
                        key = line.split('=')[1].strip()
                        self.api_field.insert(0, key)
        except FileNotFoundError:
            pass

    def save_api_key(self):
        key = self.api_field.get().strip()
        if not key:
            self.api_status.config(text="Key cannot be empty!", fg="red")
            return
        try:
            #create or update .env file
            with open('.env', 'w') as f:
                f.write(f"API_KEY={key}")
            
            self.api_status.config(text="Key saved successfully.", fg="green")

            #update current session
            self.update_current_session_key(key)

        except Exception as e:
            self.api_status.config(text=f"Error: {str(e)}", fg="red")
    
    def update_current_session_key(self, key):
        connection = Connect("http://www.omdbapi.com/")
        connection.set_api_key(key)

        self.status_label.config(text="API Key Updated")




    #"imdbID": self.get_id(),
    #"Review Score": self.get_review_score(),
    #"Review": self.get_review_text()
                    


generateUI()

