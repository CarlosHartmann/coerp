'''
normalization-extractor: Fetches all normalizations, adds a confidence score that the original is actually Latin and exports as CSV
'''


import os
import csv
import xml.etree.ElementTree as ET

from lingua import Language, LanguageDetectorBuilder

languages = [Language.ENGLISH, Language.FRENCH, Language.LATIN]
detector = LanguageDetectorBuilder.from_languages(*languages).build()

global ns
ns = "{http://www.tei-c.org/ns/1.0}"

def extract_normals(file):
    with open(file, "r", encoding="utf-8") as infile:
        doc = infile.read()

        filename = os.path.basename(file)

        with open(f"./output/normalizations_w_latin_conf-scores.csv", "a", encoding="utf-8") as outfile:

            writer = csv.writer(outfile, delimiter=';', quotechar='"', quoting = csv.QUOTE_MINIMAL)

            for elem in fetch_normals(doc, file):
                context_left_2 = elem['cont_l_2']
                context_left_1 = elem['cont_l_1']
                original = elem['orig']
                normalization = elem['norm']
                context_right_1 = elem['cont_r_1']
                context_right_2 = elem['cont_r_2']

                conf_val = detector.compute_language_confidence(original, Language.LATIN)

                writer.writerow([context_left_2, context_left_1, original, normalization, context_right_1, context_right_2])


def is_head(elem):
    return True if elem.tag == "{http://www.tei-c.org/ns/1.0}head" else False


def is_p(elem):
    return True if elem.tag == "{http://www.tei-c.org/ns/1.0}p" else False


def extracted(text):
    return ''.join([bit for bit in extract(text)])


def extract(elem):
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
    



def fetch_normals(xml_string) -> dict:
    ET.register_namespace('', "http://www.tei-c.org/ns/1.0")

    root = ET.fromstring(xml_string)
    body = root.find(ns + "text")[0] # 'body' was proven to be the child tag of text in all files
    # body usually only contains <div> objects except in one file where there is an empty page with only a page number in between the documents
    
    for element in body.iter():
        if is_head(element) or is_p(element):
            for norm in extract(element):
                yield norm


def main():
    data = "./data"
    genres = [elem for elem in os.listdir(data) if os.path.isdir(os.path.join(data, elem))]

    for genre in genres:
        dir = os.path.join(data, genre)
        files = [elem for elem in os.listdir(dir) if elem.startswith(genre)]
        for file in files:
            filedir = os.path.join(dir, file)
            extract_normals(filedir)


if __name__ == "__main__":
    main()