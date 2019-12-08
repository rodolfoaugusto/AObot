# AObot
Albion Online MMORPG item trading clicker bot.
*Disclaimer: Use of this application is against Albion Online Terms of Service. Use it only for education purposes.*
## What does it do?
Aplication written in Python.
1. Uses ```Optical Character Recognition (OCR)``` and ```OpenCV``` library to read prices from Black Market. Uses ```pyautogui``` for scrolling through the list.
1. Saves them into the memory.
1. Goes into the Marketplace by using clicker ```pyautogui``` functions.
1. Types in search-bar scanned item names and compares their prices using Windows Clipboard thanks to ```win32gui```.
1. Buys items which price gives atleast 10% profit.
1. Goes back to Black Market and sells them by pasting in bought item names.
1. Pick next item category from Black Market dropdown.
1. Repeat process.

## Requirements
* OCR
* OpenCV lib
* Python 3
* Windows 7 (tested) with pywin32 package

## Instructions
The in-game position and HUD setup is necessary to for clicker to work correctly (even though window position is determined by ```win32gui```). Due to it's negative gameplay contribution, instructions are not provided.

## Usage
```python text.py go```
