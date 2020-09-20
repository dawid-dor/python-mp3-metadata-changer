# TO DO:
# 1. Proper data validation
# 2. Album image changable
# 3. Make GUI look cleaner
# 3. Make it executable + keep the last opened folder list in cache

import PySimpleGUI as sg
import eyed3
import os.path
import io
import time
import threading


# Class
class Song:
    def __init__(self, path, artist, title, album):
        self.path = path
        self.artist = artist
        self.title = title
        self.album = album
        self.file = eyed3.load(self.path)

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


# Functions
def clear_info():
    window['-INFO-'].update('')


def clear_input_fields():
    window['-TITLE-'].update('')
    window['-ARTIST-'].update('')
    window['-ALBUM-'].update('')


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
             [sg.Text(text='PLACEHOLDER', key='-INFO-', enable_events=True)]]

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
        # Set new data
        CURRENT_SONG.change_title(values['-TITLE-'])
        CURRENT_SONG.change_artist(values['-ARTIST-'])
        CURRENT_SONG.change_album(values['-ALBUM-'])
        # Clear input fields
        clear_input_fields()
        # Confirmation that the operation has been performed sucessfuly
        window['-INFO-'].update('Updated!')
        # Wait 1 second and erase the confirmation
        threading.Timer(1, clear_info).start()

# --------------------------------- Close & Exit ---------------------------------
window.close()