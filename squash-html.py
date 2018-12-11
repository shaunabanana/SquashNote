#!/usr/bin/env python3
import sys
from glob import glob
from os import remove, mkdir
from os.path import join, split
import base64
import json


if len(sys.argv) < 4:
    print("USAGE: squash-html.py [extract|pack] [in folder] [out folder]")


if sys.argv[1] == 'extract':

    def pdfp_extract(inpath, outpath):
        f = open(inpath)
        pdfp = f.read()
        f.close()

        pdfp = pdfp.replace("local_pdf(", "").replace(")", "")
        pdfp = json.loads(pdfp)

        pdf = base64.b64decode(pdfp['pdf'])

        f = open(join(outpath, pdfp['slide'] + ".pdf"), 'wb')
        f.write(pdf)
        f.close()


    pdfps = glob(join(sys.argv[2], "assets/**/*.pdfp"), recursive=True)
    pdfs = glob(join(sys.argv[2], "assets/**/*.pdf"), recursive=True)

    for pdf in pdfs:
        remove(pdf)
    
    curr_dir_id = 1
    curr_dir = ""
    for i, pdfp in enumerate(pdfps):
        if i % 20 == 0:
            curr_dir = join(sys.argv[3], "{}-{}".format((curr_dir_id - 1) * 20 + 1, curr_dir_id * 20))
            mkdir(curr_dir)
            curr_dir_id += 1
        pdfp_extract(pdfp, curr_dir)

elif sys.argv[1] == 'pack':

    def pdfp_pack(inpath, outpath):
        f = open(inpath, 'rb')
        pdf = f.read()
        f.close()

        pdfp = {}
        pdfp['slide'] = split(inpath)[1][:-4]
        pdfp['pdf'] = base64.b64encode(pdf).decode('utf-8')

        pdfp = json.dumps(pdfp).replace('/', '\\/')
        pdfp = "local_pdf( {} )".format(pdfp)

        f = open(join(outpath, "assets", split(inpath)[1][:-4], "assets", split(inpath)[1][:-4] + ".pdfp"), 'w')
        f.write(pdfp)
        f.close()

    pdfs = glob(join(sys.argv[2], "*.pdf"))
    
    for pdf in pdfs:
        pdfp_pack(pdf, sys.argv[3])