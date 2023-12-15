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

            for elem in fetch_normals(doc):
                context_left = elem['cont_l']
                original = elem['orig']
                normalization = elem['norm']
                context_right = elem['cont_r']

                whole_sent = f'{context_left}{original}{context_right}'

                conf_val_word = detector.compute_language_confidence(original, Language.LATIN)
                conf_val_sent = detector.compute_language_confidence(whole_sent, Language.LATIN)
                conf_val_total = conf_val_word + conf_val_sent

                if conf_val_word > 0.3 and conf_val_total > 0.6:
                    writer.writerow([context_left, original, normalization, context_right, conf_val_word, conf_val_sent, conf_val_total])


def is_head(elem):
    return True if elem.tag == "{http://www.tei-c.org/ns/1.0}head" else False


def is_p(elem):
    return True if elem.tag == "{http://www.tei-c.org/ns/1.0}p" else False


def extracted(text):
    content = extract(text)
    return (''.join([bit[0] for bit in content]), [elem for bit[1] in content for elem in bit[1]])


def extract(elem):
    normals = list()
    out = elem.text if elem.text else ''
    for child in elem:
        if child.tag == ns+'normalised':
            orig = child.attrib['orig']
            reg = child.text
            i = len(out)
            normals.append({'index': i, 'original': orig, 'regularized': reg})

            out += orig
            out += child.tail if child.tail else ''
        elif child.tag == ns+'join':
            content = extracted(child) if len(child) else child.attrib['original']
            if type(content) == tuple:
                out += content[0]
                normals.extend(content[1])
            elif type(content) == str:
                out += content
            #out += child.tail if child.tail else ''
        elif child.tag == ns+'choice':
            corr = extracted(child[1])
            out += corr[0]
            normals.extend(corr[1])
            out += child.tail if child.tail else ''
        elif child.tag == ns+'fw':
            pass
        elif child.tag == ns+'lb':
            out += child.tail.replace('\n', ' ') if child.tail else ''
        elif child.tag == ns+'pb':
            yield (out, normals)
            out, normals = '', list()
        else: # can be hi(ghlight), variant, notvariant, foreign, quote
            content = extracted(child)
            out += content[0]
            normals.extend(content[1])
            #out += child.tail if child.tail else ''
    out += elem.tail if elem.tail else ''
    yield (out, normals)


def fetch_normals(xml_string) -> dict:
    ET.register_namespace('', "http://www.tei-c.org/ns/1.0")

    root = ET.fromstring(xml_string)
    body = root.find(ns + "text")[0] # 'body' was proven to be the child tag of text in all files
    # body usually only contains <div> objects except in one file where there is an empty page with only a page number in between the documents
    
    for element in body.iter():
        if is_head(element) or is_p(element):
            for page, normals in extract(element):
                for norm in normals:
                    i = norm['index']
                    original = norm['original']
                    i2 = i + len(original)

                    con_size = 50

                    context_left = page[:i] if len(page[:i]) < con_size else page[:i][-con_size:]
                    context_right = page[i2:] if len(page[i2:]) < con_size else page[i2:][:con_size+1]
                    yield {'cont_l': context_left, 'cont_r': context_right, 'orig': original, 'norm': norm['regularized']}


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