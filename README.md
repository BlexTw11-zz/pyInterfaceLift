# pyInterfaceLift - A InterfaceLIFT Downloader
Downloader for InterfaceLift wallpapers

### Preparation

To run this software you need the [Requests](http://docs.python-requests.org/en/) package.
For installing over [pip](https://pip.pypa.io/en/stable/) enter:

    pip install requests
    
### Usage

Just run it with the python interpreter. Without the directory parameter, the wallpaper will be stored in your current folder.

    pyhton pyInterfacelift.py [-h] [-s {date,downloads,comments,rating,random}]
                          [-n MAX-WALLPAPER] [-c]
                          resolution [/path/to/your/directory]

For example:
    
    python pyInterfacelift.py -s comments -n 10 3840x2160 /home/pictures

### Options

###### Required arguments

* Resolution of the wallpaper. Possible options are e.g.: 1920x1080, 1280x1024, 360x240, ...

###### Optional arguments

* `[Path]` To your directory. Standard is the current directory.
* `[-s PARAM]` Sorts the wallpaper by "date", "rating", "downloads", "comments" or "random". Standard is "date".
* `[-n PARAM]` Defines the maximum of downloaded wallpaper. Standard is download all.
* `[-c]` Cron job mode. Downloads on every call just new wallpaper. If you using this option for the first time,
             call pyInterfaceLift with `-n N>0`.

Tested with Python 2.7.6.

### Licence

This software is licensed under the [MIT license](http://opensource.org/licenses/mit-license.php).
