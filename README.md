# Movie Logger

A python application built in Tkinter that allows users to search for movies, view general information about the movies, add them to a list of their favorites, and write reviews for movies. 

This application serves as my first forray into API calls via python and GUI development. It was developed as part of the Boot.dev Personal Project course. Learn more about [Boot.dev](https://boot.dev).

## Features

- Search for movies via OMDB API
- Mark movies as your favorite and view them separately
- Write reviews for movies, give them a score, and save them
- Persistent local storage via JSON

## Getting Started

Movie Logger requires an OMDB API key. Please visit https://www.omdbapi.com/ and obtain an API key.

### Installation

1. Create a new virtual environment (optional)
```
python -m venv venv
source venv/bin/activate #on windows use: venv\Scripts\activate
```
2. Clone this repository
```
git clone https://github.com/ROFLBOB/MovieLogger
```
3. Install dependecies with
```pip install -r requirements.txt
```
4. Obtain an OMDB API key from omdbapi.com 
5. Run the app. Navigate to the directory and type:
```
python src/movielogger.py
```
6. Click on File -> Set API Key and put your OMDB API key in. Click save.
7. You're ready to search and write reviews.
