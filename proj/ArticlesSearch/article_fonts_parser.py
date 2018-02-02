"""
Module to split a list of fonts (journalistic fonts) from a CSV file into
new CSV rows for each font.

@author: Joao Hatum
@date: 03Jan2018
"""

import csv

class ArticleFontsParser:
    """Main class"""

    def __init__(self, file_path, output_path):
        self.file_path = file_path
        self.output_path = output_path
        self.final_data = []

    def __write_new_csv(self):
        with open(self.output_path, 'w', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter = ';',  \
                quotechar='"', quoting=csv.QUOTE_MINIMAL)

            for item in self.final_data:
                writer.writerow(item)

    def parse_articles_fonts(self):
        with open(self.file_path, encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, delimiter = ';',  \
                quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                if len(row) >= 6:
                    fonts = row[5].strip().split(',')
                    for font in fonts:
                        current_row = list(row)
                        current_row[5] = font.strip()
                        self.final_data.append(current_row)
                else:
                    self.final_data.append(row)

        self.__write_new_csv()

# Le Figaro
#fonts_parser = ArticleFontsParser('/home/jvhm/Documentos/Code/Python/LavaJatoSearch/le_figaro_fontes.csv', \
#    '/home/jvhm/Documentos/Code/Python/LavaJatoSearch/le_figaro_fontes_mod.csv')
#fonts_parser.parse_articles_fonts()

# Le Monde
#fonts_parser = ArticleFontsParser('/home/jvhm/Documentos/Code/Python/LavaJatoSearch/le_monde_fontes.csv', \
#    '/home/jvhm/Documentos/Code/Python/LavaJatoSearch/le_monde_fontes_mod.csv')
#fonts_parser.parse_articles_fonts()

# Liberation
fonts_parser = ArticleFontsParser('/home/jvhm/Documentos/Code/Python/LavaJatoSearch/liberation_fontes.csv', \
    '/home/jvhm/Documentos/Code/Python/LavaJatoSearch/liberation_fontes_mod.csv')
fonts_parser.parse_articles_fonts()