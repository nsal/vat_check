https://ec.europa.eu is a European Commission website which hosts VAT Information Exchange System.
According to HMRC, this is a most reliable service to check validity of VAT registration number and its details.
Unfortunately, the service is designed for single requests. However, it offers WSDL interface. 

This python script brings automation functionality for the service. 
It can check .csv or .xls(x) file with VAT numbers and create a result file containing:
- VAT number status: valid\not valid
- VAT number registered name
- VAT number registered address, including postcode

The script has been tested on UK market only.
