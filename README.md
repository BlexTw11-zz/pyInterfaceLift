# pyInterfaceLift - A InterfaceLIFT Downloader
Downloader for InterfaceLift pictures

### Running

Just run it with the python interpreter. Without the directory parameter, the wallpaper will be stored in your current folder.

    python pyInterfacelift.py [-s SORTING-PARAM] [-n MAX-WALLPAPER] resolution [/path/to/your/directory]

For example:
    
    python pyInterfacelift.py -s comments -n 10 3840x2160 /home/pictures

### Options

###### Required arguments

* Resolution of the wallpaper. Possible options are e.g.: 1920x1080, 1280x1024, 360x240, ...

###### Optional arguments

* Path to your directory. Standard is the current directory.
* -s PARAM - Sorts the wallpaper by "date", "rating", "downloads", "comments" or "random". Standard is "date".
* -n PARAM - Defines the maximum of downloaded wallpaper. Standard is download all.

Tested with Python 2.7.6.
