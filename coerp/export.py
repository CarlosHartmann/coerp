'''
export: This module shall one day export all the COERP data into the desired output format (../assets/output_format_example.txt)
'''


import sys
import re
from lxml import etree as ET


testfile = "/Users/chartman/Documents/GitHub/coerp/test/bio_1510_More_R3"

ns = '{http://www.tei-c.org/ns/1.0}' #used in all TEI documents (which is all of the COERP documents)

def is_only_whitespace(text) -> bool:
    '''
    Removes chunks of only whitespace, ideally without catching legitimate cases like single spaces, linebreaks, or tabs.
    Initially, only chunks of the shape '\\n           ' were caught. For maximum precision, only this pattern is caught here.
    The function extract_text sometimes still catches blocks of whitespace meant for XML formatting that this function hopefully filters out.
    '''
    return True if re.search('^\n\s{4,}', text) and not re.search('\w', text) else False


def is_under_skippable_tag(element, skippables = [f'{ns}sic', f'{ns}fw']):
    '''
    Identifies if any given XML element is somewhere inside a tag I want to skip entirely.
    This is necessary because the extract_text() function is recursive so child elements of skipped elements will still get processed.
    Hence, this function always checks all ancestors until root to check for the to-be-skipped ones.
    Currently, this is not necessary as the script works as expected anyway.
    '''
    
    parent = element.getparent()
    while parent is not None:
        if parent.tag in skippables:
            return True
        parent = parent.getparent()
    return False


def remove_huge_spaces(text):
    return re.sub(' {14,}', '', text)


def extract_text(xml_file):
    # Parse the XML file
    parser = ET.XMLParser(remove_blank_text=False) # setting remove_blank_text to True would make things easier, but it would also introduce unfixable bugs in the export in the form of erroneously removed spaces between words
    tree = ET.parse(xml_file, parser)
    root = tree.getroot()

    # Skip teiHeader and immediately access the body element (I believe always inside a <text> element)
    text_body = root[1][0]

    # Initialize an empty list to hold the text content
    text_content = []

    # Define a function to recursively extract text
    def extract_text_recursive(element):
        if element.tag in [f'{ns}head', f'{ns}p', f'{ns}corr', f'{ns}quote', f'{ns}choice', f'{ns}join', f'{ns}opener',f'{ns}closer', f'{ns}variant', f'{ns}sp', f'{ns}l', f'{ns}note', f'{ns}writing']:
            # these mark the border between different texts within a document, marking by adding additional linebreak – might need to be handled differently at a later stage
            if element.tag in [f'{ns}p', f'{ns}sp', f'{ns}l']: # extra linebreak to keep text away from its title above
                if len(text_content) > 0:
                    text_content.append('\n')
            if element.tag == f'{ns}head': # adding a double linebreak to highlight a new incoming title
                if len(text_content) > 0:
                    text_content.append('\n\n')

            if element.text and not is_only_whitespace(element.text) and element.tag == f'{ns}head': # Just as a help for myself – titles might need to be handled differently at a later stage
                text_content.append(f'Title: {element.text}')

            elif element.text and not is_only_whitespace(element.text):
                text_content.append(remove_huge_spaces(element.text))

            for child in element: # this is mainly to catch all the elements within paragraphs such as linebreaks and simple normalisations
                if child.tag in [f'{ns}normalised', f'{ns}hi', f'{ns}notvariant']:
                    if child.text:
                        text_content.append(child.text)

                elif child.tag not in [f'{ns}sic', f'{ns}fw', f'{ns}l', f'{ns}p']: # sic always occurs before the corr element which contains what we actually want for the final corpus | similar problem with <l> which is used in <sp>
                    extract_text_recursive(child)

                if child.tail and not is_only_whitespace(child.tail): # the tails are most commonly text or simple spaces, but sometimes also chunks of formatting-whitespace
                    if child.tag in [f'{ns}lb', f'{ns}p', f'{ns}l'] and child.tail.startswith('\n    '): # trying to catch those formatting chunks of whitespace right after a linebreak
                        text_content.append(child.tail.strip())
                    elif re.search(' *\n {4,}', child.tail):
                        tail = re.sub('^ *\n','\n', child.tail)
                        tail = re.sub('\n {4,}', '\n', tail)
                        text_content.append(tail)
                    elif child.tag.startswith('\n    '):    
                        text_content.append(child.tail.replace('\n', ''))
                    else:
                        text_content.append(child.tail)

    # Iterate through the elements in a linear fashion within the specified part of the document
    for elem in text_body.iter():
        # the content of certain elements was doubled at the end of paragraphs without this line
        # why this fixed it and not filtering within the extract_text_recursive() function, I still do not know
        if elem.tag not in [f'{ns}normalised', f'{ns}corr', f'{ns}choice', f'{ns}join', f'{ns}sic']:
            extract_text_recursive(elem)

    return ''.join(text_content)


def main():
    if len(sys.argv) > 1:
        testfile = sys.argv[1]
    text = extract_text(testfile)

    with open("./test/export_test.txt", "w", encoding="utf-8") as outfile:
        outfile.write(text)


if __name__ == "__main__":
    main()