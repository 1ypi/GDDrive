# GDDrive
Cloud Storage Implemented in Geometry Dash

Video: https://youtu.be/oENqzFJ3TgI

## Linux and Windows

Requirements:
- Python 3
- `requests`

Install and run:

```bash
python3 -m pip install requests
python3 gddrive.py
```

Notes:
- The script now resolves `credentials.json`, `index.json`, and `Downloads/` relative to the project folder, so it works even if you launch it from another directory.
- Uploaded files can be selected with absolute paths, relative paths, or `~/...` home-directory paths on Linux.
- Now you can relogin from the menu.
- Now you can download other users files using the level id.
- The program automatically detects the file type.

# Cool links

gaxolotl's webserver panel: https://github.com/gaxolotl/GDDriveWS

ArcticWoof's web implementation: https://github.com/DumbCaveSpider/GDDriveWeb
