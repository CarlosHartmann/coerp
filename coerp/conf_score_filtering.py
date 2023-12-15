import csv

with open("/Users/chartman/Documents/GitHub/coerp/output/normalizations_w_latin_conf-scores.csv", "r", encoding="utf-8") as infile:
    with open("/Users/chartman/Documents/GitHub/coerp/output/normalizations_w_latin_conf-scores_over-45%.csv", "w", encoding="utf-8") as outfile:
        reader = csv.reader(infile, delimiter=';', quotechar='"', quoting = csv.QUOTE_MINIMAL)
        writer = csv.writer(outfile, delimiter=';', quotechar='"', quoting = csv.QUOTE_MINIMAL)
        for line in reader:
            if float(line[-1]) > 0.45:
                writer.writerow(line)