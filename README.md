# Library Wallpaper

![Example of wallpaper with added images](example.png)

A simple script that downloads covers from a personal [google books](https://books.google.com/) shelve, adds them onto a given wallpaper and saves the result to a file. Because e-books also deserves a shelf.

## Configuration

See the file [./config](/blob/main/config) included in the repository for all available options, commented options gives sane defaults.

## Requirements

Following packages are required to be installed.

- requests
Used to create the request to the google books API.
- toml
Used to parse the configuration file.
- pillow
Used to manipulate the images.

Install with:

`pip3 install requests toml pillow`

## Usage

Make sure to add at least an API key and user id in the configuration file, as well as the wallpaper to the same folder as the script (expected with the name wallpaper.jpg by default). Then run the script with:

`> ./library-wallpaper.py`
