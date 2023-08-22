import os
import csv
from lxml import etree
import xml.etree.ElementTree as ET

from lingua import Language, LanguageDetectorBuilder

languages = [Language.ENGLISH, Language.FRENCH, Language.LATIN]
detector = LanguageDetectorBuilder.from_languages(*languages).build()

global ns
ns = "{http://www.tei-c.org/ns/1.0}"

def check_langs(file):
    with open(file, "r", encoding="utf-8") as infile:
        doc = infile.read()
        filename = os.path.basename(file) + "_latin-scores.csv"

        with open("./output/{filename}", "w", encoding="utf-8") as outfile:

            writer = csv.writer(outfile, delimiter=';', quotechar='"', quoting = csv.QUOTE_MINIMAL)
            writer.writerow(['line', 'Latin confidence value'])

            for line in extract_sentences(doc, file):
                if ' - ' in line:
                    content = line.split(' - ')[1]
                else:
                    content = line

                conf_val = detector.compute_language_confidence(content, Language.LATIN)
                writer.writerow([line, conf_val])

                



def is_head(elem):
    return True if elem.tag == "{http://www.tei-c.org/ns/1.0}head" else False


def is_p(elem):
    return True if elem.tag == "{http://www.tei-c.org/ns/1.0}p" else False


def extracted(text):
    return ''.join([bit for bit in extract(text, page=None)])


def extract(elem, page):
    out = elem.text if elem.text else ''
    for child in elem:
        if child.tag == ns+'normalised':
            out += child.attrib['orig']
            out += child.tail if child.tail else ''
        elif child.tag == ns+'join':
            out += child.attrib['original']
            out += child.tail if child.tail else ''
        elif child.tag == ns+'choice':
            corr = extracted(child[1])
            out += corr
            out += child.tail if child.tail else ''
        elif child.tag == ns+'fw':
            pass
        elif child.tag == ns+'lb':
            yield out
            out = page+' - ' if page is not None else ''
            out += child.tail.replace('\n', ' ') if child.tail else ''
        elif child.tag == ns+'pb':
            try:
                page = child.attrib['n']
            except:
                pass
        else: # can be hi(ghlight), variant, notvariant, foreign, quote
            out += extracted(child)
            out += child.tail if child.tail else ''
    out += elem.tail if elem.tail else ''
    yield out

def extract_sentences(xml_string, file):
    head_contents = []
    p_contents = []
    ET.register_namespace('', "http://www.tei-c.org/ns/1.0")
    root = ET.fromstring(xml_string)
    page = '1'
    body = root.find(ns + "text")[0] # 'body' was proven to be the child tag of text in all files
    # body usually only contains <div> objects except in one file where there is an empty page with only a page number in between the documents
    
    for element in body.iter():
        if element.tag == ns+'pb':
            try:
                page = element.attrib['n']
            except:
                pass
        elif is_head(element) or is_p(element):
            for line in extract(element, page):
                yield line


def main():
    data = "./data"
    genres = [elem for elem in os.listdir(data) if os.path.isdir(os.path.join(data, elem))]

    for genre in genres:
        dir = os.path.join(data, genre)
        files = [elem for elem in os.listdir(dir) if elem.startswith(genre)]
        for file in files:
            filedir = os.path.join(dir, file)
            check_langs(filedir)


if __name__ == "__main__":
    main()