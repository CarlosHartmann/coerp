'''
scout_corpus: Check out all of COERP corpus for statistics / overviews over its content.
'''


import os
from lxml import etree as ET


corpus_path = "/Users/chartman/Library/CloudStorage/GoogleDrive-smogshaik.uni@gmail.com/.shortcut-targets-by-id/1xXrtqarel363zcD11O0OzfvTnzROT6mb/Uni-Ablage/03 Assistance Work/COERP"


def get_unique_child_element_names(element, unique_elements=set()) -> list:
    '''
    Returns a list of unique elements found in a document.
    Used for scouting the documents before script development.
    '''
    # Add the name of the current element to the set
    unique_elements.add(element.tag)

    # Recursively call this function for each child element
    for child in element:
        get_unique_child_element_names(child, unique_elements)

    return unique_elements


def scout(file_path):
    parser = ET.XMLParser(remove_blank_text=False) # setting remove_blank_text to True would make things easier, but it would also introduce unfixable bugs in the export in the form of erroneously removed spaces between words
    tree = ET.parse(file_path, parser)
    root = tree.getroot()
    # Skip teiHeader and immediately access the body element (I believe always inside a <text> element)
    text_body = root[1][0]

    return get_unique_child_element_names(text_body)


def iterate_through_path(path):
    for root, _, files in os.walk(path):
        for file in files:
            # Check if the file has no extension
            if '.' not in file:
                print(file)
                file_path = os.path.join(root, file)
                yield scout(file_path)


def main():
    elements = list()
    for itemlist in iterate_through_path(corpus_path):
        for elem in itemlist:
            elements.append(elem)
        elements = list(set(elements))   

    for elem in elements:
        print(elem)     


if __name__ == "__main__":
    main()