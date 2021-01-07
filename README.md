# check-folder-size
A little project in python for checking folders and subfolders size. Useful when you are running low on disk space and want to identify heavy folders/files.

## Usage
First, ensure you have python 3 and tkinter installed.
For Linux users:
```
python3 ./checksizes.py
```
For Windows users:
```
python ./checksizes.py
```
If you want to check admin/superuser/root/protected folders, ensure you have enough permissions for such folders and files.

### Important: Tkinter must be installed in order to work

Made in Python 3.8.5.
Tested on Windows 10.
Tested on Ubuntu 20.04, however, it will only work in GUI environments.
Tested on WSL 2 using xrdp and remote desktop tool to have GUI desktop.

TO-DO tasks:
 - [ ] Support for symlinks, as it only works with directories.
 - [ ] Realtime showing directories in the GUI. At the present time, although the GUI won't freeze while loading directories, it won't show any folder until it's finished.
 - [ ] Command-line based alternative.

Don't be afraid to post any issue you see while using this tool.