#!/usr/bin/env python

from os.path import isfile
import requests
import random
import io
import sys
import toml
from PIL import Image

DEFAULT_CONF_PATH = "./config"

class Config:
    """
    Keeps the configuration of the application, includes a method for loading
    an arbitrary external config file. If none is loaded it has sane defaults.
    """

    # google-books
    api_key = 0
    user_id = 0
    shelve_id = 4
    max_results = 40

    # covers
    y_offset = 150
    x_offset = 150
    opacity = 150
    cover_width = 300

    # file
    wallpaper = "wallpaper.jpg"
    output = "wallpaper_new.png"
    max_height = 1920
    max_width = 1080

    def load_config(self, fp):
        """
        Loads the existing config file located at the filepath fp into the class.
        """

        config = toml.load(fp)

        if 'google-books' in config:
            books = config['google-books'] if 'google-books' in config else []

            self.api_key = books['api_key'] if 'api_key' in books else self.api_key
            self.user_id = books['user_id'] if 'user_id' in books else self.user_id
            self.shelve_id = books['shelve_id'] if 'shelve_id' in books else self.shelve_id
            self.max_results = books['max_results'] if 'max_results' in books else self.max_results

        if 'covers' in config:
            covers = config['covers'] if 'covers' in config else []

            self.y_offset = covers['y_offset'] if 'y_offset' in covers else self.y_offset
            self.x_offset = covers['x_offset'] if 'x_offset' in covers else self.x_offset
            self.opacity = covers['opacity'] if 'opacity' in covers else self.opacity
            self.cover_width = covers['width'] if 'width' in covers else self.cover_width

        if 'file' in config:
            covers = config['file'] if 'file' in config else []

            self.wallpaper = covers['wallpaper'] if 'wallpaper' in covers else self.wallpaper
            self.output = covers['output'] if 'output' in covers else self.output
            self.max_height = covers['max_height'] if 'max_height' in covers else self.max_height
            self.max_width = covers['max_width'] if 'max_width' in covers else self.max_width

    def check(self):
        """
        Makes sure necessary variables are set.

        returns 1 if everything seem good, otherwise returns 0
        """

        good_config = True

        if not self.api_key:
            print("Bad API key set:", self.api_key)
            good_config = False
        if not self.user_id:
            print("Bad user ID set:", self.user_id)
            good_config = False
        if not self.output:
            print("Bad output file set:", self.output)
            good_config = False
        if not isfile(self.wallpaper):
            print("Can't find wallpaper at:", self.wallpaper)
            good_config = False

        return good_config



class WallpaperMaker:
    """
    Has the methods for grabbing the book covers from google books and also apply it
    onto the given wallpaper.
    """

    config = None

    def __init__(self, config):
        """
        Initializes the class by applying the given config.
        """
        self.config = config

    def get_api_url(self, call):
        """
        Returns a string of the url for an api call to google books.
        """
        return "https://www.googleapis.com/books/v1/users/" + str(self.config.user_id) + "/" + call + "?key=" + str(self.config.api_key) + "&maxResults=" + str(self.config.max_results)

    def get_covers(self):
        """
        Returns the cover images of volumes in a shelve as an array of bytes.
        """

        url = self.get_api_url("bookshelves/" + str(self.config.shelve_id) + "/volumes")

        req = requests.get(url).json()

        covers = []

        for book in req['items']:
            if 'imageLinks' in book['volumeInfo']:
                thumb_url = book['volumeInfo']['imageLinks']['thumbnail']
                img = requests.get(thumb_url)
                covers.append(img.content)

        return covers

    def create_wallpaper(self, covers, wallpaper):
        """
        Pastes the book covers onto the wallpaper.
        """

        x = 0 + self.config.x_offset
        y = 0 + self.config.y_offset

        space_left = True

        while space_left and len(covers) > 0:
            rint = random.randint(0, len(covers) - 1)

            # instead use frombuffer or frombytes?
            img = Image.open(io.BytesIO(covers[rint]))

            del covers[rint]

            # calculate new height for the cover based on the wanted cover width
            cover_dim_factor = (self.config.cover_width / float(img.width))
            cover_height = int((float(img.height) * float(cover_dim_factor)))

            img = img.resize((self.config.cover_width, cover_height), Image.ANTIALIAS)

            # add transparency to the cover
            img.putalpha(self.config.opacity)

            if (y + img.height) >= self.config.max_height:
                x += img.width
                y = self.config.y_offset

                if (x + img.width) > self.config.max_width:
                    space_left = False

            # paste the book cover to the wallpaper
            wallpaper.paste(img, (x, y), img)
            y += img.height

    def create(self):
        """
        Performs the methods for creating the wallpaper and saves it into the output file.
        """

        covers = self.get_covers()

        current_wallpaper = Image.open(self.config.wallpaper)

        wallpaper = Image.new('RGBA', current_wallpaper.size)
        wallpaper.paste(current_wallpaper)

        current_wallpaper.close()

        self.config.max_width = wallpaper.width
        self.config.max_height = wallpaper.height

        self.create_wallpaper(covers, wallpaper)

        wallpaper.save(self.config.output)

def main():
    """
    Makes sure a config is in place then asks the class that creates wallpapers to create one.

    returns 1 if everything went as expected, else 0
    """

    config = Config()

    if sys.argv[1] == "--config" or sys.argv[1] == "-c":
        config.load_config(sys.argv[2])
    elif isfile(DEFAULT_CONF_PATH):
        config.load_config(DEFAULT_CONF_PATH)

    if not config.check():
        print("Bad config given.")
        return 0

    maker = WallpaperMaker(config)
    maker.create()

    return 1

main()
