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
### Squashing Keynote file
```
python3 squash.py [Keynote file 1] [Keynote file 2] ...
```
Squashed file will be create with "*.squashed.key" extension under the same path as the input file. **Do not close the Keynote window that pops up!** 

**NOTE: When adding videos to your Keynote, ensure that they don't have the same names.** Otherwise, SquashNote may confuse the widths and heights of the videos.

### Squashing exported HTML folder 
First execute the following command to delete all pdfs in the HTML folder and extract pdf files from pdfp archives:
```
python3 squash-html.py extract [HTML folder] [temporary folder for pdfs]
```
Then, send the pdf files to some program/service for compression. **Not all program/services work.**
[PDF Compressor](https://pdfcompressor.com/) has been tested to be working.
Make sure to keep filenames unchanged!

Finally, put the compressed pdf files back into the folder and pack into pdfp archives:
```
python3 squash-html.py pack [PDF folder] [HTML folder]
```


## How does it work?
* For images, SquashNote uses optimize-image to shrink its file size, and limits it's width to 1280px maximum -- the default max width of Keynote presentations.
* For videos, SquashNote interfaces with Keynote to query the actual width and height used in the file, and downscales the video to that size.
* For exported HTML folders, SquashNote deletes the unesessary PDF files, and extracts all pdfp archives into pdfs for compression. After compression, the pdf files are packed back into the folder.

## Known problems
* Appscript might fail to interface with Keynote on macOS Mojave
* Currently does not support Python 2
