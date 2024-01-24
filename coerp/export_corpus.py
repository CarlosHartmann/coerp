'''
export_corpus: Takes the COERP corpus dir as input and writes the exported version into a neighboring dir that it creates.
'''

import os
import sys
import shutil

from export import *

def main():
    input_dir = sys.argv[1]
    output_dir = f'{input_dir}_exported'
    
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    
    for root, _, files in os.walk(input_dir):
        for file in files:
            in_path = os.path.join(root, file)
            out_path = in_path.replace(input_dir, output_dir)
            if not os.path.isfile(out_path):
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
            
            if '.' not in in_path: # exclude non-content files
                print(f'Processing {file}')
                exported_text = extract_text(in_path)

                with open(out_path, "w", encoding="utf-8") as outfile:
                    _=outfile.write(exported_text)
            
            elif not file.startswith('.'): # copy the rest that isn't a system file
                shutil.copyfile(in_path, out_path)


if __name__ == "__main__":
    main()