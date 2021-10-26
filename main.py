#!/usr/bin/env python

import requests
import random
import html
import io
import toml
from PIL import Image

class Config:
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

    def load_config(self, fp):
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

def create_url(what):
    return "https://www.googleapis.com/books/v1/users/" + str(config.user_id) + "/" + what + "?key=" + str(config.api_key) + "&maxResults=" + str(config.max_results)

def get_images():
        url = create_url("bookshelves/" + str(config.shelve_id) + "/volumes")

        r = requests.get(url).json()

        images = []

        for book in r['items']:
            if 'imageLinks' in book['volumeInfo']:
                thumb_url = book['volumeInfo']['imageLinks']['thumbnail']
                img = requests.get(thumb_url)
                images.append(img.content)

        return images

def create_wallpaper():
        x = 0 + config.x_offset
        y = 0 + config.y_offset

        space_left = True

        while(space_left and len(images) > 0):
                randint = random.randint(0, len(images) - 1)

                # instead use frombuffer or frombytes?
                img = Image.open(io.BytesIO(images[randint]))

                del images[randint]

                # calculate new height for the cover based on the wanted cover width
                cover_dim_factor = (config.cover_width / float(img.width))
                cover_height = int((float(img.height) * float(cover_dim_factor)))

                img = img.resize((config.cover_width, cover_height), Image.ANTIALIAS)

                # add transparency to the cover
                img.putalpha(OPACITY)

                if (y + img.height) >= MAX_HEIGHT:
                        x += img.width
                        y = Y_OFFSET

                        if (x + img.width) > MAX_WIDTH:
                                space_left = False

                # paste the book cover to the wallpaper
                wallpaper.paste(img, (x, y), img)
                y += img.height

def main():
    config = Config()
    config.load_config("./live.config")

    images = get_images()

    current_wallpaper = Image.open(config.wallpaper)

    wallpaper = Image.new('RGBA', current_wallpaper.size)
    wallpaper.paste(current_wallpaper)

    current_wallpaper.close()

    MAX_WIDTH = wallpaper.width
    MAX_HEIGHT = wallpaper.height

    create_wallpaper()

    wallpaper.save(config.output)

main()
