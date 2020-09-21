# TO DO:
# 1. Proper data validation
# 2. Album image changable @@done
# 3. Make GUI look cleaner
# 3. Make it executable + keep the last opened folder list in cache

import PySimpleGUI as sg
import eyed3
import os.path
import shutil
import io
import time
import threading
import requests
import json
from google_images_download import google_images_download


# Class
class Song:
    def __init__(self, path, artist, title, album):
        self.path = path
        self.artist = artist
        self.title = title
        self.album = album
        self.file = eyed3.load(self.path)

    def reset_tags(self):
        self.file.initTag()

    def get_artist(self):
        return self.file.tag.artist

    def get_album(self):
        return self.file.tag.album

    def get_title(self):
        return self.file.tag.title

    def change_artist(self, change_value):
        self.file.tag.artist = change_value
        self.file.tag.save()

    def change_album(self, change_value):
        self.file.tag.album = change_value
        self.file.tag.save()

    def change_title(self, change_value):
        self.file.tag.title = change_value
        self.file.tag.save()

    def change_album_image(self, change_value):
        self.file.tag.images.set(3,
                                 open(change_value, 'rb').read(), 'image/jpeg')
        self.file.tag.save(version=eyed3.id3.ID3_V2_3)


# Functions
def clear_info():
    window['-INFO-'].update('')


def clear_input_fields():
    window['-TITLE-'].update('')
    window['-ARTIST-'].update('')
    window['-ALBUM-'].update('')


def get_image_from_google(query):
    response = google_images_download.googleimagesdownload(
    )  #class instantiation

    arguments = {
        "keywords": "{}".format(query),
        "limit": 1,
        "print_urls": True
    }  #creating list of arguments
    paths = response.download(
        arguments)  #passing the arguments to the function
    keyword = query
    return paths[0][keyword][0]


def delete_downloaded_image(file_path):
    formatted_path = r'%s' % file_path
    download_folder = os.path.dirname(formatted_path)
    shutil.rmtree(download_folder)


# ----- Full layout -----
sg.theme('LightBlue1')
label_col = [
    [sg.Text('Title:')],
    [sg.Text('Artist:')],
    [sg.Text('Album:')],
]

input_col = [
    [sg.Input(key='-TITLE-')],
    [sg.Input(key='-ARTIST-')],
    [sg.Input(key='-ALBUM-')],
]

left_col = [
    [
        sg.Text('Folder'),
        sg.In(size=(25, 1), enable_events=True, key='-FOLDER-'),
        sg.FolderBrowse()
    ],
    [
        sg.Listbox(values=[],
                   enable_events=True,
                   size=(40, 20),
                   key='-FILE LIST-')
    ],
]

right_col = [[sg.Column(label_col), sg.Column(input_col)],
             [sg.Button('Submit Changes', key='-CHANGE-')],
             [
                 sg.Text(text='              ',
                         key='-INFO-',
                         enable_events=True)
             ]]

layout = [[
    sg.Column(left_col, element_justification='c'),
    sg.VSeperator(),
    sg.Column(right_col, element_justification='c')
]]

# --------------------------------- Create Window ---------------------------------
window = sg.Window('Song Metadata Changer', layout, resizable=True)
FILE_PATH = ''
CURRENT_SONG = ''
# pylint: disable=E1101

# ----- Program loop -----
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == '-FOLDER-':  # Folder name was filled in, make a list of files in the folder
        folder = values['-FOLDER-']
        try:
            file_list = os.listdir(folder)  # get list of files in folder
        except:
            file_list = []
        fnames = [
            f for f in file_list
            if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith((
                ".mp3"))
        ]
        window['-FILE LIST-'].update(fnames)
    elif event == '-FILE LIST-':  # A file was chosen from the listbox
        try:
            # Clear input fields
            clear_input_fields()
            # Get filepath from listbox
            filename = os.path.join(values['-FOLDER-'],
                                    values['-FILE LIST-'][0])
            # Pass current path to global scope
            FILE_PATH = filename
            # Instantiate object
            song = Song(filename, values['-ARTIST-'], values['-TITLE-'],
                        values['-ALBUM-'])
            # Pass current object to global scope
            CURRENT_SONG = song
            # Set input fields after clicking on the song from list
            window['-TITLE-'].update(song.get_title())
            window['-ARTIST-'].update(song.get_artist())
            window['-ALBUM-'].update(song.get_album())
        except Exception as E:
            print(f'** Error {E} **')
            pass
    elif event == '-CHANGE-':
        # Set query for web scrapper for album IMG
        query = values['-TITLE-'] + ' ' + values['-ARTIST-']
        image_location = get_image_from_google(query)
        # Set new data
        CURRENT_SONG.reset_tags()
        CURRENT_SONG.change_title(values['-TITLE-'])
        CURRENT_SONG.change_artist(values['-ARTIST-'])
        CURRENT_SONG.change_album(values['-ALBUM-'])
        CURRENT_SONG.change_album_image(image_location)
        # Confirmation that the operation has been performed sucessfuly
        window['-INFO-'].update('Updated!')
        # Clear input fields
        clear_input_fields()
        # Wait 1 second and erase the confirmation
        threading.Timer(1, clear_info).start()
        # Delete downloaded album image
        delete_downloaded_image(image_location)

# --------------------------------- Close & Exit ---------------------------------
window.close()