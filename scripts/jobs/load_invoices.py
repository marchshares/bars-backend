import logging
from pathlib import Path
from typing import List
from datetime import datetime

import config
from functions.entity import Product
from functions.services.moysklad_controller import MoySkladClient
import pandas as pd
import re

class InvoiceLoader:

    def __init__(self) -> None:
        self._ms_client = MoySkladClient(config.MOYSKLAD_LOGIN, config.MOYSKLAD_PASSWORD)

    def load_positions_from_excel(self, excel_file: Path) -> pd.DataFrame:
        logging.info(f"Load {excel_file}")

        df = None
        engine = "xlrd" if excel_file.suffix == ".xls" else "openpyxl"
        columns = ['№', 'Артикул', 'Товары (работы, услуги)', 'Количество', 'Цена', 'Сумма']
        try:
            df = pd.read_excel(excel_file, skiprows=22, engine=engine)[columns]
        except:
            df = pd.read_excel(excel_file, skiprows=19, engine=engine)[columns]

        df = df[df['Сумма'].notna()]
        total_sum = df.iloc[-1, -1]
        df_positions = df[df['Товары (работы, услуги)'].notna()]

        prod_total_sum = df_positions['Сумма'].sum()
        if total_sum != prod_total_sum:
            logging.warning(f"Diff in total_sum: file={total_sum} != prod={prod_total_sum}")

        df_positions = df_positions.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        logging.info(f"Loaded:\n {df_positions}")

        return df_positions

    def convert_to_products(self, df_positions: pd.DataFrame) -> List[Product]:
        products = []
        for idx, position_row in df_positions.iterrows():
            products.append(
                Product(
                    sku=position_row['Артикул'],
                    price=position_row['Цена'],
                    quantity=position_row['Количество']
                )
            )

        return products

    def get_invoice_details(self, excel_file: Path):
        groups = re.match(".*№ (.*) от (.*)\.", excel_file.name).groups()
        return groups[0], datetime.strptime(groups[1], "%d.%m.%Y")

    def load(self, excel_file: Path):
        df_positions = self.load_positions_from_excel(excel_file)
        products = self.convert_to_products(df_positions)

        invoice_num, invoice_date = self.get_invoice_details(excel_file)

        invoicein = self._ms_client.create_invoicein(products, invoice_num, invoice_date)
        self._ms_client.create_supply(invoicein_id=invoicein['id'], moment=invoice_date)


    def load_all(self):
        for f in Path("Z:\ИП\Drivix\Накладные\\2019-2020").iterdir():
            if f.is_file():
                try:
                    # self.load(f)
                    print(self.get_invoice_details(f))
                except Exception as e:
                    logging.error(f"Not loaded {f}. Cause: {e}")


InvoiceLoader().load(excel_file=Path("Z:\ИП\Drivix\Накладные\\Schet na oplatu № 136 от 18.02.2022.xlsx"))
# InvoiceLoader().load_all()