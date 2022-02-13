import csv
import logging
from typing import Dict, AnyStr


def load_data(csv_filename, key_row_name) -> Dict[AnyStr, Dict]:
    data = {}
    with open(csv_filename,  encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            data[row[key_row_name]] = row

    logging.info(f"Loaded {len(data.keys())} rows from {csv_filename}")
    return data


def auto_str(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )
    cls.__str__ = __str__
    return cls


def none2empty(s: str) -> str:
    return s if s else ""
