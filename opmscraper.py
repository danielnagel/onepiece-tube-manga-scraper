import requests
import urllib
import os
import argparse
from bs4 import BeautifulSoup
from PIL import Image


def save_image(url):
    mng_page = os.path.basename(url)
    mng_chpt = os.path.dirname(url)[os.path.dirname(url).rfind('/')+1:]
    picname = path2img + mng_chpt + "_" + mng_page
    urllib.urlretrieve(url, picname)
    print "saved", picname


def scrape(chapter):
    page = 1
    base_url = "http://onepiece-tube.com/kapitel/"
    isNextChapter = True

    while(isNextChapter):
        isNextPage = True
        while(isNextPage):
            url = base_url + str(chapter) + "/" + str(page)
            result = requests.get(url)

            if(result.status_code == 404):
                if(page == 1):
                    print "chapter", chapter, "not available, ending process..."
                    isNextChapter = False
                    return
                else:
                    print url, "not found"
                    isNextPage = False
                    continue

            c = result.content
            soup = BeautifulSoup(c, 'html.parser')
            img = soup.find("img", {"id": "p"})
            save_image(img['src'])
            page = page + 1

        page = 1
        img2pdf(chapter)
        chapter = chapter + 1


def img2pdf(chapter):
    current_chapter_list = []
    isNextPage = True
    page = 1
    fileType = ".jpg"

    while isNextPage:
        currentImgPath = path2img + \
            str(chapter) + "_" + str(page) + fileType
        if page < 10:
            currentImgPath = path2img + \
                str(chapter) + "_0" + str(page) + fileType
        try:
            img = Image.open(currentImgPath)
            # img with transparency or png has to be converted
            if img.mode == 'RGBA' or img.mode == 'LA':
                img = img.convert('RGB')

            if(page > 1):
                current_chapter_list.append(img)
            else:
                cover = img

            page = page + 1
        except IOError:
            if fileType == ".jpg":
                # since chapter 902 the not cover sites are in png format
                fileType = ".png"
            else:
                # page in chapter does not exist
                isNextPage = False

    if(len(current_chapter_list) > 1):
        pdfName = path2pdf + str(chapter) + ".pdf"
        cover.save(pdfName, "PDF", resolution=100.0, save_all=True,
                   append_images=current_chapter_list)
        print "saved", pdfName
        chapter = chapter + 1
    else:
        print "the chapter", chapter, "does not exist, stoping process..."
        return


print "One Piece Manga Scraper v0.1.0"

parser = argparse.ArgumentParser(
    description="script to scrape the one piece manga from 'onepiece-tube.com' and parse it into pdf format"
)

parser.add_argument(
    '-i', '--images',
    help="path to store images",
    type=str,
    default='.'
)

parser.add_argument(
    '-p', '--pdfs',
    help="path to store pdfs",
    type=str,
    default='.'
)

parser.add_argument(
    '-c', '--chapter',
    help="chapter where the scraper will start",
    type=int,
    default=925
)

arguments = parser.parse_args()

path2img = arguments.images
if not path2img.endswith("/"):
    path2img += "/"
path2pdf = arguments.pdfs
if not path2pdf.endswith("/"):
    path2pdf += "/"
chapter  = arguments.chapter

scrape(chapter)
