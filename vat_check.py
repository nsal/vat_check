"""
This app is intended to check UK/EU^ business registered details:
- VAT number
- registration name
- registration address
- registration postcode
on European Commission website
(https://ec.europa.eu/taxation_customs/vies/vatResponse.html)

^EU functionality hasn't been tested.
"""

import sys
import asyncio
from os import path
import pandas as pd
from suds.client import Client


def get_dataframe_from_file(filename: str) -> pd.DataFrame:
    if not path.exists(filename):
        sys.exit('File not found!')
    if filename.endswith('.xlsx') or filename.endswith('.xls'):
        df = pd.read_excel(filename)
    elif filename.endswith('.csv'):
        df = pd.read_csv(filename)
    else:
        sys.exit('file type is not supported. Operation cancelled.')
    return df


def get_unique_VAT_numbers(df: pd.DataFrame,
                           column_index: int) -> pd.Series:

    vat_numbers = pd.Series(df.iloc[:, column_index])
    vat_numbers = vat_numbers.dropna().drop_duplicates().astype(int)

    return vat_numbers


async def get_vat_registration(vat_number: int, country_code: str,
                               suds_client: Client) -> dict:

    retailer = {}
    retailer['VAT'] = vat_number

    try:
        result = suds_client.service.checkVat(country_code, vat_number)

        if result['valid'] is True:
            retailer['name'] = result['name'].title()
            address = result['address'].title().split('\n')[:-1]
            clean_address = [item.replace('\n', '') for item in address if
                             item != '']
            retailer['address'] = ', '.join(clean_address)
            retailer['postcode'] = result['address'].split('\n')[-1]
            retailer['status'] = 'valid'
        else:
            retailer['status'] = 'VAT is not Valid'

    except Exception:
        retailer['status'] = 'connection failed'

    return retailer


if __name__ == "__main__":

    FILE_NAME = 'example.csv'  # MODIFY THIS
    RESULT_FILE_NAME = 'result.xlsx'  # MODIFY THIS IF NEEDED
    VAT_COLUMN_INDEX = 0  # MODIFY THIS IF VAT NUMBERS NOT IN 1st COLUMN
    COUNTRY_CODE = 'GB'  # MODIFY THIS IF COUNTRY IS NOT GB
    SUDS_CLIENT = Client(
        'http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl')

    df = get_dataframe_from_file(FILE_NAME)
    vat_numbers = get_unique_VAT_numbers(df, VAT_COLUMN_INDEX)

    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(get_vat_registration(number,
                                                   COUNTRY_CODE,
                                                   SUDS_CLIENT))
             for number in vat_numbers]
    done, pending = loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    result = [item.result() for item in done]
    result_df = pd.DataFrame(result)
    result_df.to_excel(RESULT_FILE_NAME, index=False)
