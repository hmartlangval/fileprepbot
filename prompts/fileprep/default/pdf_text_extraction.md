Extract following data strictly from given text extract from PDF only:
Property Owner Name:
Owner Address:
County: *dynamically retrieve the county using property Address, just the name. Example: pasco, brevard, putnam*
Property Address:
Parcel ID or Account ID:
Year: 2024

*INSTRUCTIONS*
- Always capture completed address and use one line
- All other values aside x_county, strictly return an empty string where data is unavailable

Output format should be in JSON exactly like below. Fill all using Property Address ONLY:
{
    "order_number": "[order_number]",
    "s_data": {
        'x_county':,
        'x_property_address':,
        'x_account_number': 'account number',
        'x_parcel_id': 'parcel id',
        'x_house_number': '12459',
        'x_street_name': '51ST TER',
        'x_city': 'LAKE BUTLER',
        'x_zip_code': '32054'
    }
}