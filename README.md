# SquashNote
SquashNote compresses your Keynote files by squashing images and resizing videos to match actual sizes used in the Keynote file.

![Demo GIF](demo.gif)

## Requirements
* Python 3
* [appscript](http://appscript.sourceforge.net/) for interfacing with Keynote:
```
pip install appscript
```
* [optimize-images](https://github.com/victordomingos/optimize-images) for squashing images:
```
pip install pillow optimize-images
```
* [HandBrakeCLI](https://handbrake.fr/downloads2.php) for squashing videos: 
Download the Mac version and put in your $PATH.

## Usage
```
python squash.py [Keynote file 1] [Keynote file 2] ...
```
Squashed file will be create with "*.squashed.key" extension under the same path as the input file. 

## Known problems
* Appscript might fail to interface with Keynote on macOS Mojave
* Currently does not support Python 2