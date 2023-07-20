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
        ("A7IV videos", "K:\\PRIVATE\M4ROOT\CLIP"),
        ("SD card: A7 Pictures", "I:\\DCIM"),
        ("SD card: A7 Video", "I:\\PRIVATE\AVCHD\BDMV\STREAM"),
        ("MicroSD: Drone", "H:\\DCIM"),
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
   

def open_file_explorer(folder_path):
    folder_path = os.path.abspath(folder_path)
    process = subprocess.Popen(f'explorer "{folder_path}"')
    process.wait()
    time.sleep(.1)
    
    file_explorer_handle = None
    while not file_explorer_handle:
        file_explorer_handle = win32gui.FindWindow("CabinetWClass", None)
    
    x_window_postion = 0
    y_window_postion = 0
    width = screen_width // 2  
    height = screen_height // 1
    win32gui.MoveWindow(file_explorer_handle, x_window_postion, y_window_postion, width, height, True)
    details_view_message = win32con.WM_COMMAND
    details_view_command = 41504
    win32gui.SendMessage(file_explorer_handle, details_view_message, details_view_command, 0)


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
    selected_picture_dates = []
    selected_video_dates = []
    selected_audio_dates = []
    selected_files = []

    def select_file_if_within_date_range(file, file_path):                     
        modified_date = datetime.date.fromtimestamp(os.path.getmtime(file_path))
        if start_date <= modified_date <= end_date:
            #selected_files.append((file_path, modified_date))
            formatted_date = modified_date.strftime("%Y-%m-%d")
            print("File selected: ", file, " - ", formatted_date)
            return True, formatted_date
            #if formatted_date not in selected_dates:
            #   selected_dates.append(formatted_date)
    
    def create_folder(directory, date):
        folder_path = os.path.join(directory, date)
        os.makedirs(folder_path, exist_ok=True)
        print("Created folder: ", folder_path)

    for selected_dir in devices_selected:
        for root, dirs, files in os.walk(selected_dir[1]):
            for file in files:
                if files:
                    file_path = os.path.join(root, file)
                    if file.lower().endswith(picture_formats):
                        true_false, formatted_date = select_file_if_within_date_range(file, file_path)
                        if true_false:
                            create_folder(pictures_directory, formatted_date)

                    elif file.lower().endswith(raw_picture_formats):
                        true_false, formatted_date = select_file_if_within_date_range(file, file_path)
                        if true_false:
                            raw_directory = os.path.join(pictures_directory, formatted_date)
                            create_folder(raw_directory, formatted_date)

                    elif file.lower().endswith(video_formats):
                        true_false, formatted_date = select_file_if_within_date_range(file, file_path)
                        if true_false:
                            create_folder(videos_directory, formatted_date)

                    elif file.lower().endswith(audio_formats):
                        true_false, formatted_date = select_file_if_within_date_range(file, file_path)
                        if true_false:
                            audio_directory = os.path.join(videos_directory, formatted_date)
                            create_folder(audio_directory, formatted_date)

                    else:
                        print(file, "is not picture, video, or audio file.")
    input("we made it here.")
#    if len(selected_files) == 0:
#        print("No files selected.")
#        if start_over_or_quit():
#            # I think this is broke
#            choose_devices_to_transefer_from()
#        else:
#            on_closing(12)
#    else:
#        if selected_picture_dates:
#            print("Picture Dates:")
#            for picture_date in selected_picture_dates:
#                print(picture_date)
#        if selected_video_dates:
#            print("\nVideo Dates:")
#            for video_date in selected_video_dates:
#                print(video_date)
#        if selected_audio_dates:
#            print("\nAudio Dates:")
#            for audio_date in selected_audio_dates:
#                print(audio_date)
#        #create_folders_by_date(selected_picture_dates, selected_video_dates, selected_audio_dates, selected_files)
#
#
#def create_folders_by_date(selected_picture_dates, selected_video_dates, selected_audio_dates, selected_files):
#
#    
#    #old code
#    if user_input_yes_no("Create folders at: " + target_directory_base):
#        open_file_explorer(target_directory_base)
#        for item in selected_dates:
#            folder_name = item
#            target_directory = os.path.join(target_directory_base, folder_name)
#            os.makedirs(target_directory, exist_ok=True)
#            
#            arw_folder_path = os.path.join(target_directory, "ARW")
#            os.makedirs(arw_folder_path, exist_ok=True)
#
#            print("Created folder:", target_directory)
#            print("Created folder:", arw_folder_path)
#
#    else:
#        while True:
#            input_target_directory = input("What directory would you like to use?").strip('"\'')
#            if not os.path.isdir(input_target_directory):
#                print("Not a valid directory. Please try again.")
#            else:
#                open_file_explorer(input_target_directory)
#                for item in selected_dates:
#                    folder_name = item
#                    target_directory = os.path.join(input_target_directory, folder_name)
#                    os.makedirs(target_directory, exist_ok=True)
#                    
#                    arw_folder_path = os.path.join(target_directory, "ARW")
#                    os.makedirs(arw_folder_path, exist_ok=True)
#
#                    print("Created folder:", target_directory)
#                    print("Created folder:", arw_folder_path)
#                break
#    # copy_files_to_folders(selected_files, target_directory_base)
#
#def copy_files_to_folders(selected_files, target_directory_base):
#    for item in selected_files:
#        file_path = item[0]
#        file_date = item[1]
#        destination_file_path = os.path.join(target_directory_base, str(file_date))
#
#        if item[0].lower().endswith("jpg" or "png"):
#            shutil.copy(file_path, destination_file_path)
#            print("Copied file:", file_path, "to", destination_file_path)
#        elif item[0].lower().endswith(".arw"):
#            arw_destination_file_path = os.path.join(destination_file_path, "ARW")
#            shutil.copy(file_path, arw_destination_file_path)
#            print("Copied file:", file_path, "to", arw_destination_file_path)
#        else:
#            print("File is not a .jpg .png or .arw", file_path)         
#
#    print("Files transferred successfully!")
#    input("Process completed. Press Enter to exit...")

check_device_avaiablity()
