import unittest
import asyncio
from suds.client import Client
import pandas as pd
from vat_check import get_dataframe_from_file, get_unique_VAT_numbers
from vat_check import get_vat_registration


class Test_vat_check(unittest.TestCase):
    excel_file = './test_examples/example.xlsx'
    csv_file = './test_examples/example.csv'
    not_supported_file = './test_examples/example.txt'
    missing_file = './test_examples/404.file'
    COUNTRY_CODE = 'GB'
    SUDS_CLIENT = Client(
            'http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl')

    def test_get_dataframe_from_file(self):
        df = get_dataframe_from_file(self.excel_file)
        df_csv = get_dataframe_from_file(self.csv_file)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertIsInstance(df_csv, pd.DataFrame)
        with self.assertRaises(SystemExit) as cm:
            get_dataframe_from_file(self.missing_file)
            self.assertEqual(cm.exception, 'File not found!')
        with self.assertRaises(SystemExit) as cm:
            get_dataframe_from_file(self.not_supported_file)
            self.assertEqual(cm.exception,
                        'file type is not supported. Operation cancelled.')  # noqa

    def test_get_unique_VAT_numbers(self):
        df = pd.read_excel(self.excel_file)
        column_index = 0
        series = get_unique_VAT_numbers(df, column_index)

        self.assertIsInstance(series, pd.Series)
        self.assertEqual(len(series), 19)
        self.assertEqual(series[10], 297150384)

    def test_get_vat_registration_success(self):
        VALID_VAT_NUMBER = 297150384

        loop = asyncio.get_event_loop()
        success_result = loop.run_until_complete(get_vat_registration(
                                                     VALID_VAT_NUMBER,
                                                     self.COUNTRY_CODE,
                                                     self.SUDS_CLIENT))
        loop.close()
        self.assertIsInstance(success_result, dict)
        self.assertEqual(success_result['status'], 'valid')
        self.assertEqual(success_result['VAT'], VALID_VAT_NUMBER)
        self.assertEqual(success_result['name'], 'Cardiff Food Store Limited')
        self.assertEqual(success_result['address'],
                'Unit 3 Hosking Industrial, Dumballs Road, Butetown, Cardiff')  # noqa
        self.assertEqual(success_result['postcode'], 'CF10 5FG')

    def test_get_vat_registration_invalid(self):
        INVALID_VAT_NUMBER = 1111111

        loop = asyncio.new_event_loop()
        invalid_result = loop.run_until_complete(get_vat_registration(
                                                     INVALID_VAT_NUMBER,
                                                     self.COUNTRY_CODE,
                                                     self.SUDS_CLIENT))
        loop.close()
        self.assertIsInstance(invalid_result, dict)
        self.assertEqual(invalid_result['status'], 'VAT is not Valid')


if __name__ == "__main__":
    unittest.main()
