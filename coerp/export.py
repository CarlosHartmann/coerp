'''
export: This module shall one day export all the COERP data into the desired output format (../assets/output_format_example.txt)
'''


import xml.etree.ElementTree as ET


testfile = "/Users/chartman/Library/CloudStorage/GoogleDrive-smogshaik.uni@gmail.com/.shortcut-targets-by-id/1xXrtqarel363zcD11O0OzfvTnzROT6mb/Uni-Ablage/03 Assistance Work/COERP/bio/bio_1510_More_R3"


def extract_text(xml_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Initialize an empty list to hold the text content
    text_content = []

    # Define a function to recursively extract text
    def extract_text_recursive(element):
        # Process text of the current element
        if element.text:
            text_content.append(element.text)

        # Process each child element
        for child in element:
            if child.tag in ['normalised', 'hi']:
                # For 'normalised' and 'hi', include only their text
                if child.text:
                    text_content.append(child.text)
            elif child.tag == 'lb':
                # Insert a line break for 'lb' tags
                text_content.append('\n')
            else:
                # Recursively process other elements
                extract_text_recursive(child)

            # Process tail text
            if child.tail:
                text_content.append(child.tail)

    # Extract text from 'head' and 'p' elements
    for elem in root.findall('.//head') + root.findall('.//p'):
        extract_text_recursive(elem)
        if elem.tag == 'head':
            # Add a line break at the end of 'head' elements
            text_content.append('\n')

    # Join and return the text content
    return ''.join(text_content)


def main():
    with open(testfile, "r", encoding="utf-8") as xmlfile:
        text = extract_text(xmlfile.read())
    
    with open("../output/export_test.txt", "w", encoding="utf-8") as outfile:
        _=outfile.write(text)


if __name__ == "__main__":
    main()