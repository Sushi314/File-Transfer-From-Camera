import os
import shutil
import datetime
import time
import subprocess
import win32gui
import win32con
import win32api
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import CENTER

#Note to future self it uses current year for "start_date" and "end_date"

screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

def on_closing(exitcode):
    sys.exit(exitcode)


def user_input_yes_no(prompt):
    result = messagebox.askyesnocancel("Confirmation", prompt)
    if result == None:
        on_closing(12)
    return result


def start_over_or_quit():
    if user_input_yes_no("Would you like to startover?"):
        return True
    else:
        on_closing(12)
    

def move_terminal_window():
    terminal_handle = win32gui.GetForegroundWindow()
    window_width = screen_width // 2  
    window_height = screen_height // 2  
    x = screen_width - window_width
    y = 0
    win32gui.MoveWindow(terminal_handle, x, y, window_width, window_height, True)

move_terminal_window()

def check_device_avaiablity():
    devices = [
        ("A7IV Pictures", "L:\\DCIM"),
        ("A7IV Videos", "K:\\PRIVATE\M4ROOT\CLIP"),
        ("SD card: A7 Pictures", "I:\\DCIM"),
        ("SD card: A7 Video", "I:\\PRIVATE\AVCHD\BDMV\STREAM"),
        ("MicroSD: Drone", "H:\\DCIM"),
        ("DJI Lav Mic 1", "N:\\"),
        ("DJI Lav Mic 2", "O:\\"),
    ]
    available_devices =[]

    for item, directoy_path in devices:
        if os.path.exists(directoy_path):
            available_devices.append((item, directoy_path))
            print("Avaiable device: " + item)
    
    choose_devices_to_transefer_from(available_devices)


def choose_devices_to_transefer_from(available_devices):
    def yes_no_to_add_drive_to_devices_selected(item):
        if user_input_yes_no("Transfer: " + item[0]):
            devices_selected.append(item)
            print("\nSelected: " + item[0] + "\n")

    devices_selected = []

    for item in available_devices:
        yes_no_to_add_drive_to_devices_selected(item)

    if len(devices_selected) == 0:
        if start_over_or_quit():
            choose_devices_to_transefer_from(available_devices)
        else:
            on_closing()

    #for device in devices_selected:
    #    open_file_explorer(device[1])
    #    print("foleder opened: ", device[0])
    
    get_start_end_dates(devices_selected)
   

#def open_file_explorer(folder_path):
#    folder_path = os.path.abspath(folder_path)
#    process = subprocess.Popen(f'explorer "{folder_path}"')
#    process.wait()
#    time.sleep(.1)
#    
#    file_explorer_handle = None
#    while not file_explorer_handle:
#        file_explorer_handle = win32gui.FindWindow("CabinetWClass", None)
#    
#    x_window_postion = 0
#    y_window_postion = 0
#    width = screen_width // 2  
#    height = screen_height // 1
#    win32gui.MoveWindow(file_explorer_handle, x_window_postion, y_window_postion, width, height, True)
#    details_view_message = win32con.WM_COMMAND
#    details_view_command = 41504
#    win32gui.SendMessage(file_explorer_handle, details_view_message, details_view_command, 0)


def get_start_end_dates(devices_selected):
    today = datetime.date.today()
    current_year = today.year
    start_date = None
    end_date = None

    print("\nTODAYS DATE IS: ", today, "\n")

    # Get the start date from the user
    while start_date is None:
        if user_input_yes_no("Use todays date for start date?"):
            start_date = today
        else:
            while True:
                start_date_input = input("Enter the start date (older) (MM DD): ")
                try:
                    start_date = datetime.datetime.strptime(f"{current_year} {start_date_input}", "%Y %m %d").date()
                    if start_date >= today:
                        print("Start date cannot be in the future.")
                    else:
                        break
                except ValueError:
                    print("Invalid date format. Please use the format: MM DD")
    print("Start date is", start_date)

    # Get the end date from the user
    while end_date is None:
        if user_input_yes_no("Use todays date for end date?"):
            end_date = today
        else:
            while True:
                end_date_input = input("Enter the end date (newer)(MM DD): ")
                try:
                    end_date = datetime.datetime.strptime(f"{current_year} {end_date_input}", "%Y %m %d").date()
                    if end_date <= today and end_date >= start_date:
                        break
                    elif end_date < start_date:
                        print("End date cannot be before the start date.")
                    elif end_date > today:
                        print("End date cannot be in the future.")
                except ValueError:
                    print("Invalid date format. Please use the format: MM DD")
            break
    print("End date is", end_date)

    sort_picture_video_audio_raw(start_date, end_date, devices_selected)


def sort_picture_video_audio_raw(start_date, end_date, devices_selected):
    picture_formats = (".jpg",".png",".gif",".bmp",".tiff",".webp",".svg",".ico",".eps",".raw")
    raw_picture_formats = (".arw",".cr2",".nef",".raf",".dng",".orf",".rw2",".srw",".pef",".3fr",".mos",".x3f",".fff",".mef",".arq",)
    video_formats = (".mp4",".mov",".avi",".mkv",".wmv",".flv",".webm",".m4v",".mpeg",".3gp")
    audio_formats = (".mp3",".wav",".flac",".aac",".ogg",".wma",".m4a",".ape",".alac",".opus")
    pictures_directory = os.path.join(os.environ['USERPROFILE'], 'Pictures')
    videos_directory = os.path.join(os.environ['USERPROFILE'], 'Videos')
    folders_created = []
    
    def select_file_if_within_date_range(file, file_path):
        modified_date = datetime.date.fromtimestamp(os.path.getmtime(file_path))
        if start_date <= modified_date <= end_date:
            formatted_date = modified_date.strftime("%Y-%m-%d")
            print("File selected: ", file, " - ", formatted_date)
            return True, formatted_date
        else:
            return False, "_" 
        
    def create_folder(file_path, root_target_directory, file_name, date, subfolder_name, tr_fa):
        folder_path = os.path.join(root_target_directory, date)
        folder_path_file_name = os.path.join(folder_path, file_name)
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            folders_created.append(folder_path)
            print("Created folder: ", folder_path)
            if not os.path.exists(folder_path_file_name):
                copy_file(file_name, file_path, folder_path)
            else:
                create_folder(file_path, root_target_directory, file_name, date, "Duplicate Files", True)
        elif tr_fa:
            subfolder_path = os.path.join(folder_path, subfolder_name)
            subfolder_path_file_name = os.path.join(subfolder_path, file_name)
            if not os.path.exists(subfolder_path):
                os.makedirs(subfolder_path)
                folders_created.append(subfolder_path)
                print("Created folder: ", subfolder_path)
            if not os.path.exists(subfolder_path_file_name):
                copy_file(file_name, file_path, subfolder_path_file_name)
            else:
                create_folder(file_path, root_target_directory, file_name, date, "Duplicate Files", True )
        else:
            folder_path_file_name = os.path.join(folder_path, file_name)
            if not os.path.exists(folder_path_file_name):
                copy_file(file_name, file_path, folder_path)
            else:
                create_folder(file_path, root_target_directory, file_name, date, "Duplicate Files", True )


    def copy_file(file_name, source_directory, destination_file_path):
        print("Copying ", file_name)
        shutil.copy(source_directory, destination_file_path)
        print("Copied file:", file_name, "to", destination_file_path)

    for selected_dir in devices_selected:
        for root, dirs, files in os.walk(selected_dir[1]):
            for file in files:
                if files:            
                    file_path = os.path.join(root, file)

                    if file.lower().endswith(picture_formats):
                        true_false, formatted_date = select_file_if_within_date_range(file, file_path)
                        if true_false:
                            create_folder(file_path, pictures_directory, file, formatted_date, "_", False)

                    elif file.lower().endswith(raw_picture_formats):
                        true_false, formatted_date = select_file_if_within_date_range(file, file_path)
                        if true_false:
                            create_folder(file_path, pictures_directory, file, formatted_date, "RAW", True)

                    elif file.lower().endswith(video_formats):
                        true_false, formatted_date = select_file_if_within_date_range(file, file_path)
                        if true_false:
                            create_folder(file_path, videos_directory, file, formatted_date, "_", False)


                    elif file.lower().endswith(audio_formats):
                        true_false, formatted_date = select_file_if_within_date_range(file, file_path)
                        if true_false:
                            create_folder(file_path, videos_directory, file, formatted_date, "Audio", True)

                    else:
                        print(file, "is not picture, video, or audio file.")

    print("Folders created: ")
    for item in folders_created:
        print(item)


    input("Yay! I think this is working? Bugs? I am sure!")


def rename_folder():
    user_input_yes_no()




check_device_avaiablity()
