'''
export: This module shall one day export all the COERP data into the desired output format (../assets/output_format_example.txt)
'''


import xml.etree.ElementTree as ET


testfile = "/Users/chartman/Library/CloudStorage/GoogleDrive-smogshaik.uni@gmail.com/.shortcut-targets-by-id/1xXrtqarel363zcD11O0OzfvTnzROT6mb/Uni-Ablage/03 Assistance Work/COERP/bio/bio_1510_More_R3"


def extract_text_from_div(xml_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Find the <div> elements in the file
    div_elements = root.findall('.//div')
    
    for div in div_elements:
        # Extract text line by line
        for element in div.iter():
            if element.tag == 'lb':
                print("\n", end='')  # New line for <lb/> tags
            elif element.text:
                print(element.text, end='')
            if element.tail:
                print(element.tail, end='')


def main():
    with open(testfile, "r", encoding="utf-8") as xmlfile:
        extract_text_from_div(xmlfile.read())


if __name__ == "__main__":
    main()