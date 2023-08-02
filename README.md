# Transfer_Pic_Vid_Audio_From_SD-Cards

```
Moves Pictures, Videos, and Audio files from SD-Cards to C:\Pictures\"File_Date" or C:\Video\"File_Date" 

Transfer_Pic_Vid_Audio_From_SD-Cards.py takes in date range as start_date, end_date.
Checks for avaiable drives (Hard coded in var "devices")
Prompts y/n for each drive to be added to "devices_selected"
Asks for start and end date for files you want to move.
walks folders in all "devices_selected"
Creates folders named as the file date.
For non RAW pictures copys files to windows directory \pictures\"File_Date"
For RAW pictures copys files to windows \pictures\"File_Date"\ARW
For Video copys files to windows directory \video\"File_Date"
For Audio copys files to windows directory \video\"File_Date"\Audio


```
