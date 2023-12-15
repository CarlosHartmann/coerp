'''
export: This module shall one day export all the COERP data into the desired output format (../assets/output_format_example.txt)
'''


import re
import xml.etree.ElementTree as ET


testfile = "/Users/chartman/Library/CloudStorage/GoogleDrive-smogshaik.uni@gmail.com/.shortcut-targets-by-id/1xXrtqarel363zcD11O0OzfvTnzROT6mb/Uni-Ablage/03 Assistance Work/COERP/bio/bio_1510_More_R3"

def is_only_whitespace(text):
    return True if not re.search('\S', text) else False


def get_unique_child_element_names(element, unique_elements=set()):
    # Add the name of the current element to the set
    unique_elements.add(element.tag)

    # Recursively call this function for each child element
    for child in element:
        get_unique_child_element_names(child, unique_elements)

    return unique_elements


def extract_text(xml_file):
    # Define the namespace
    ns = '{http://www.tei-c.org/ns/1.0}'

    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Focus on the specific part of the document
    text_body = root[1][0]  # Adjust this index based on the structure of your XML

    # Initialize an empty list to hold the text content
    text_content = []

    # Define a function to recursively extract text
    def extract_text_recursive(element):
        if element.tag in [f'{ns}head', f'{ns}p', f'{ns}corr', f'{ns}quote', f'{ns}choice', f'{ns}join']:
            if element.text:
                text_content.append(element.text)

            for child in element:
                if child.tag in [f'{ns}normalised', f'{ns}hi', f'{ns}notvariant']:
                    if child.text:
                        text_content.append(child.text.lstrip())

                elif child.tag == f'{ns}lb' and not text_content[-1] == '\n':
                    text_content.append('\n')

                elif child.tag not in [f'{ns}sic', f'{ns}fw']:
                    extract_text_recursive(child)

                if child.tail and not is_only_whitespace(child.tail):
                    text_content.append(child.tail.replace('\n', ''))

            #if element.tag == f'{ns}head':
                #text_content.append('\n')

    # Iterate through the elements in a linear fashion within the specified part of the document
    for elem in text_body.iter():
        extract_text_recursive(elem)

    return ''.join(text_content)


def main():
    text = extract_text(testfile)

    with open("./test/export_test.txt", "w", encoding="utf-8") as outfile:
        outfile.write(text)


if __name__ == "__main__":
    main()