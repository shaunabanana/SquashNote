#!/usr/bin/env python3
import sys
import os
import os.path
import shutil
import zipfile
import subprocess
import glob
import appscript
import time
from PIL import Image

# parameters
VIDEO_TYPES = ["*.mp4", "*.mov", "*.m4v"]
IMAGE_TYPES = ["*.png", "*.jpg", "*.jpeg"]
HANDBRAKE_PARAMETERS = ['-e', 'x264', '-q', '20', '-r', '25', '-2', '-T', '--keep-display-aspect', '--crop', '0:0:0:0']


def filename(path):
    return os.path.split(path)[1]


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def find_movie_path(movie):
    source_name = movie.file_name()[:-4]
    source_ext = movie.file_name()[-4:]
    for video_path in videos:
        video_name = os.path.split(video_path)[1]
        if source_name == video_name[:len(source_name)] and source_ext == video_name[-4:]:
            return video_path
    return None


def extract_zip(zip_path, extract_path):
    zipnote = zipfile.ZipFile(zip_path, 'r')
    for fileinfo in zipnote.infolist():
        _filename = fileinfo.filename.encode('cp437').decode('utf-8')
        pth = os.path.join(extract_path, os.path.split(_filename)[0])
        fin = zipnote.open(fileinfo.filename)
        if not os.path.isdir(pth):
            os.makedirs(pth)
        fout = open(os.path.join(extract_path, _filename), 'wb')
        fout.write(fin.read())
        fout.close()
        fin.close()
        
    zipnote.close()

def print_result(oldsize, newsize):
    print("      ✅ " + sizeof_fmt(oldsize) + " -> " + sizeof_fmt(newsize), " 🔻", end='')
    print("{0:.1f}%".format((oldsize - newsize) / oldsize * 100))


if len(sys.argv) < 2:
    print("Specify file name!")
    sys.exit(0)

if not shutil.which('optimize-images'):
    print("Can't find optimize-images. Try pip install optimize-images.")

if not shutil.which('HandBrakeCLI'):
    print("Can't find HandBrakeCLI. Try download your platform specific version and put it in your $PATH.")

ERROR_COUNT = 0
RESULTS = []
ERRORS = []
DEVNULL = open(os.devnull, 'wb')

for input_file in sys.argv[1:]:

    print("📥  Squashing", filename(input_file) + "...")

    FILE_NAME = os.path.split(input_file)[1]
    DIR_PATH = os.path.join("/tmp", FILE_NAME + ".tmp") 
    ZIP_PATH = os.path.join(DIR_PATH, FILE_NAME + ".zip")
    EXT_PATH = os.path.join(DIR_PATH, "extract")
    VIDEO_PATH = os.path.join(DIR_PATH, "videos")
    DATA_PATH = os.path.join(EXT_PATH, "Data")
    OUTPUT_PATH = input_file + ".squashed.key"

    if os.path.isdir(DIR_PATH):
        shutil.rmtree(DIR_PATH)

    os.mkdir(DIR_PATH)
    os.mkdir(VIDEO_PATH)
    shutil.copyfile(input_file, ZIP_PATH)

    extract_zip(ZIP_PATH, EXT_PATH)

    keynote = appscript.app('Keynote')
    keynote_file = appscript.mactypes.File(input_file)
    doc = keynote.open(keynote_file)

    images = []
    for itype in IMAGE_TYPES:
        images += glob.glob(os.path.join(DATA_PATH, itype))
    
    for image in images:
        old_size = os.path.getsize(image)
        print("   🏞  Squashing", filename(image) + '...')
        try:
            subprocess.check_output(['optimize-images', image, '-mw', '1280'])
            new_size = os.path.getsize(image)
            print_result(old_size, new_size)
        except:
            print("      ❌ Error while squashing!")
            ERRORS.append(("   🏞 ", filename(input_file), filename(image), "(Squash error)"))
            ERROR_COUNT += 1
    
    images = glob.glob(os.path.join(DATA_PATH, '*.tiff'))
    images += glob.glob(os.path.join(DATA_PATH, '*.tif'))
    for image in images:
        old_size = os.path.getsize(image)
        print("   🏞  Squashing", filename(image) + '...')
        try:
            itemp = Image.open(image)
            itemp.save(image, compression='tiff_lzw')
            new_size = os.path.getsize(image)
            print_result(old_size, new_size)
        except:
            print("      ❌ Error while squashing!")
            ERRORS.append(("   🏞 ", filename(input_file), filename(image), "(Squash error)"))
            ERROR_COUNT += 1
    
    # print("Optimizing videos...")
    videos = []
    for vtype in VIDEO_TYPES:
        videos += glob.glob(os.path.join(DATA_PATH, vtype))

    processed_videos = []
    for slide in doc.slides():
        for movie in slide.movies():
            print("   🎞  Squashing", movie.file_name() + '...')

            if movie.file_name() in processed_videos:
                print("      ❌ Possible duplicate")
                ERRORS.append(("   🎞 ", filename(input_file), filename(movie.file_name()), "(Duplicate)"))
                ERROR_COUNT += 1
                continue

            movie_path = find_movie_path(movie)
            if movie_path is None:
                print("      ❌ Can't find movie file!")
                ERRORS.append(("   🎞 ", filename(input_file), filename(movie.file_name()), "(Not found)"))
                ERROR_COUNT += 1
                continue

            old_size = os.path.getsize(movie_path)
            output_path = os.path.join(VIDEO_PATH, filename(movie_path))
            
            try:
                
                if "[FULLSCREEN]" in movie.file_name():
                    subprocess.check_output(['HandBrakeCLI', '-i', movie_path, '-o', output_path] + HANDBRAKE_PARAMETERS + ['-X', '1280'], stderr=DEVNULL)
                else:
                    subprocess.check_output(['HandBrakeCLI', '-i', movie_path, '-o', output_path] + HANDBRAKE_PARAMETERS + ['-w', str(movie.width()), '-l', str(movie.height())], stderr=DEVNULL)
                
                if os.path.getsize(output_path) < old_size:
                    shutil.copyfile(output_path, movie_path)
                
                new_size = os.path.getsize(movie_path)
                print_result(old_size, new_size)
                processed_videos.append(movie.file_name())
            except:
                print("      ❌ Error while squashing!")
                ERRORS.append(("   🎞 ", filename(input_file), filename(movie_path), "(Squash error)"))
                ERROR_COUNT += 1
    
    doc.close()

    print("   📦 Packing keynote file...")
    shutil.make_archive(OUTPUT_PATH, 'zip', EXT_PATH)
    shutil.move(OUTPUT_PATH + ".zip", OUTPUT_PATH)
    shutil.rmtree(DIR_PATH)

    old_size = os.path.getsize(input_file)
    new_size = os.path.getsize(OUTPUT_PATH)

    print_result(old_size, new_size)
    time.sleep(0.5)
    print("\n")

    RESULTS.append((filename(input_file), old_size, new_size))


if ERROR_COUNT > 0:
    print("❌ Command finished with", ERROR_COUNT, "errors:")

for error in ERRORS:
    print(error[0], error[1], ">", error[2], error[3])

print("")

print("✅ Overall result:")

for result in RESULTS:
    print("   📥 " + result[0] + ": " + sizeof_fmt(result[1]) + " -> " + sizeof_fmt(result[2]), " 🔻", end='')
    print("{0:.1f}%".format((result[1] - result[2]) / result[1] * 100))
