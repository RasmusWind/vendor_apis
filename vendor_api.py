import requests
import os
import digikey
from typing import List, Dict
from scraper import rs_components_get_single_part, RS_BASE_URL
from api_setup import API_KEYS, FARNELL_BASE_URL


def available_apis() -> List[dict]:
    return [("Farnell", farnell_api), ("Digikey", digikey_api), ("Mouser", mouser_api), ("Rscomponents", rscomponents_api)]


def farnell_api(part_number: str) -> dict:
    """
        Runs an API call.
        
        Parameters
        ----------
        part_number : str
            The part number the API should be called with.

        Returns
        -------
        dict
            a dict with the following format:\n
            {
                "pricebreaks": List[Dict[str, float]],
                "stock": int,
                "leadtime": int,
                "url": str,
            }
    """
    store = "dk.farnell.com" # Which store to query. Our case we query the danish store.
    offset = "0" # Mandatory for keyword search.
    requested_number_of_results = "10" # number of returned results from API. This is to insure the correct item is returned. Could be a mix of reels etc..
    response_group = "medium" # Type of response. 
    # Relevant response types available:
        # small - limited amount of data per item returned. Does not include stock and prices.
        # medium - Includes stock and pricing data.
        # large - Includes "medium" data and item attribute data.
        # prices - Includes all pricing data.
        # inventory - Includes all stock data.
    api_key = API_KEYS.get("farnell")
    
    if not api_key:
        print("Missing api key for Farnell")
        return {}
    
    part_number_request_url = f"https://api.element14.com/catalog/products?versionNumber=1.1&term=manuPartNum:{part_number}&storeInfo.id={store}&resultsSettings.offset={offset}&resultsSettings.numberOfResults={requested_number_of_results}&resultsSettings.responseGroup={response_group}&callInfo.omitXmlSchema=true&callInfo.responseDataFormat=json&callinfo.apiKey={api_key}"
    
    response = requests.get(part_number_request_url)
    if response.status_code != 200:
        return {}

    json_response = response.json()
    if not json_response:
        return {}
    products = json_response.get('manufacturerPartNumberSearchReturn', {}).get('products', [])
    
    filtered_products = list(filter(lambda x: x.get("translatedManufacturerPartNumber") == part_number, products))

    if not filtered_products:
        return {}
    
    part = filtered_products[0]
    pricebreaks = [{"from": pricebreak.get("from"), "cost": pricebreak.get("cost")} for pricebreak in part.get("prices")]

    return_data_dict = {
        "pricebreaks": pricebreaks,
        "stock": int(part.get("stock", {}).get("level")),
        "leadtime": int(part.get("stock", {}).get("leastLeadTime")),
        "url":f"{FARNELL_BASE_URL}search?st={part_number}"
    }

    return return_data_dict


def digikey_api(part_number: str) -> dict:
    """
        Runs an API call.
        
        Parameters
        ----------
        part_number : str
            The part number the API should be called with.

        Returns
        -------
        dict
            a dict with the following format:\n
            {
                "pricebreaks": List[Dict[str, float]],
                "stock": int,
                "leadtime": int,
                "url": str,
            }
    """
    api_key = API_KEYS.get("digikey")
    if not api_key:
        print("Missing api keys for DIGIKEY.")
        return {}
    
    os.environ['DIGIKEY_CLIENT_ID'] = api_key.get("clientid")
    os.environ['DIGIKEY_CLIENT_SECRET'] = api_key.get("clientsecret")
    os.environ['DIGIKEY_CLIENT_SANDBOX'] = 'False'
    os.environ['DIGIKEY_STORAGE_PATH'] = os.getcwd()
    
    part = digikey.product_details(part_number, x_digikey_locale_site='DK', x_digikey_locale_language='da', x_digikey_locale_currency='DKK')
    if not part:
        return {}
    leadtime = part.lead_status
    if leadtime == "Lead Status unavailable":
        manufacturer_lead_weeks = part.manufacturer_lead_weeks.split(" ")[0]
        if manufacturer_lead_weeks.isnumeric():
            mlw = int(manufacturer_lead_weeks)
            leadtime = mlw * 7

    pricing = part.standard_pricing
    pricebreaks = [{"from": pricebreak.break_quantity, "cost": pricebreak.unit_price} for pricebreak in pricing]
    
    return_data_dict = { 
        "pricebreaks": pricebreaks,
        "stock": int(part.quantity_available),
        "leadtime": (leadtime),
        "url": part.product_url
    }
    
    return return_data_dict


def mouser_api(part_number: str) -> dict:
    """
        Runs an API call.
        
        Parameters
        ----------
        part_number : str
            The part number the API should be called with.

        Returns
        -------
        dict
            a dict with the following format:\n
            {
                "pricebreaks": List[Dict[str, float]],
                "stock": int,
                "leadtime": int,
                "url": str,
            }
    """
    mouser_api_key = API_KEYS.get("mouser")
    if not mouser_api_key:
        print("Missing api key for Mouser")
        return {}
    
    mouser_post_url = f'https://api.mouser.com/api/v1/search/keyword?apiKey={mouser_api_key}'
    
    mouser_postdata = {
        "SearchByKeywordRequest": {
            "keyword": f"{part_number}",
            "records": 1,
            "currencyCode": "DKK",
        }
    }

    response = requests.post(mouser_post_url, json=mouser_postdata)

    if response.status_code != 200:
        return {}
    
    json_response = response.json()
    if not json_response:
        return {}
    
    products = json_response.get("SearchResults", {}).get("Parts")

    filtered_products = list(filter(lambda x: x.get("ManufacturerPartNumber") == part_number, products))

    if not filtered_products:
        return {}
    
    part = filtered_products[0]
    eof = part.get("LifecycleStatus")
    if eof:
        return {}

    pricing = part.get("PriceBreaks")
    pricebreaks = [{"from": pricebreak.get("Quantity"), "cost":round(float(pricebreak.get("Price", "999999").split(" ")[0].replace(",",".")),2)} for pricebreak in pricing]
    
    leadtime = part.get("LeadTime")
    if leadtime:
        leadtime = leadtime.split(" ")[0]

    stock = part.get("Availability")
    if stock:
        stock = stock.split(" ")[0]

    return_data_dict = {
        "pricebreaks": pricebreaks,
        "stock": int(stock),
        "leadtime": int(leadtime),
        "url": part.get("ProductDetailUrl")
    }
    return return_data_dict


def rscomponents_api(part_number: str) -> dict:
    """
        Runs a GET request to scrape a product search page and download it as a file.\n
        From the file it gets the ID and Category of the item, if and item is found.\n
        Runs another GET request with a new link constructed from ID and Category.\n
        Deletes downloaded files after use.
        
        Parameters
        ----------
        part_number : str
            The part number the scraper should be called with.

        Returns
        -------
        dict
            a dict with the following format:
            {
                "pricebreaks": List[Dict[str, float]],
                "stock": int,
                "leadtime": int,
                "url": str,
            }
    """
    part = rs_components_get_single_part(part_number)
    if not part:
        return {}
    pricing = part.get("priceBreaks")
    pricebreaks = [{"from": pricebreak.get("quantity"), "cost": pricebreak.get("price")} for pricebreak in pricing]
    
    leadtime = None
    if leadtime:
        leadtime = leadtime.split(" ")[0]

    stock = part.get("productAvailability",{}).get("productPageStockVolume", '0')

    return_data_dict = {
        "pricebreaks": pricebreaks,
        "stock": int(stock),
        "leadtime": leadtime,
        "url": f"{RS_BASE_URL}web{part.get('productUrl')}"
    }
    return return_data_dict


def find_cheapest_parts(part_numbers: List[str]) -> Dict[str, dict]:    
    """ 
    Runs all vendor api calls with chosen part numbers.
    Finds the cheapest price breaks and least amount break.
    Sorts on these and returns a dictionary with the part numbers as keys, and vendors with part information as values. 
    Returns in the following format:
    {
        str[part_number as key]: {
            'cheapest': {
                'Mouser': {
                    "pricebreaks": List[Dict[str, float]],
                    "stock": Int[stock],
                    "leadtime": Int[leadtime],
                    "url": Str[url_to_part_page],
                    'filteredprices': {
                        'cheapest': {
                            'from': int, 
                            'cost': float
                        }, 
                        'least_amount': {
                            'from': int, 
                            'cost': float
                        }
                    }
                }
            }, 
            'least_amount': {
                'Mouser': {
                    "pricebreaks": List[Dict[str, float]],
                    "stock": int,
                    "leadtime": int,
                    "url": str,
                    'filteredprices': {
                        'cheapest': {
                            'from': int, 
                            'cost': float
                        }, 
                        'least_amount': {
                            'from': int, 
                            'cost': float
                        }
                    }
                }
            }
        }
    }
    """
    apis = available_apis()

    api_results = [(supplier_name, [{part_number: api(part_number)} for part_number in part_numbers]) for supplier_name, api in apis]

    cheapest_parts = {}
    for part_number in part_numbers:
        supplier_named_parts = []
        for supplier, api_result in api_results:
            part = [part for part in api_result if part_number in part]
            if not part:
                continue

            part = part[0]
            
            if not part[part_number]:
                continue

            pricebreaks = part[part_number]["pricebreaks"]
            prices_by_cheapest_price = sorted(pricebreaks, key=lambda x: float(x.get("cost")))
            prices_by_least_amount = sorted(pricebreaks, key=lambda x: int(x.get("from")))
            prices = {
                "cheapest": prices_by_cheapest_price[0] if prices_by_cheapest_price else {},
                "least_amount": prices_by_least_amount[0] if prices_by_least_amount else {}
            }
            part[part_number]["filteredprices"] = prices

            supplier_named_parts.append({supplier: part}) 

        cheapest = {}
        for snp in supplier_named_parts:
            if not cheapest:
                cheapest = snp
                continue
            last_part_cost = cheapest.get(list(cheapest.keys())[0]).get(part_number, {}).get("filteredprices", {}).get("cheapest", {}).get("cost")
            new_part_cost = snp.get(list(snp.keys())[0]).get(part_number, {}).get("filteredprices", {}).get("cheapest", {}).get("cost")
            if float(new_part_cost) < float(last_part_cost):
                cheapest = snp

        least_amount_cheapest = {}
        for snp in supplier_named_parts:
            if not least_amount_cheapest:
                least_amount_cheapest = snp
                continue
            last_part_cost = least_amount_cheapest.get(list(least_amount_cheapest.keys())[0]).get(part_number, {}).get("filteredprices").get("least_amount").get("cost")
            new_part_cost = snp.get(list(snp.keys())[0]).get(part_number, {}).get("filteredprices").get("least_amount").get("cost")
            if float(new_part_cost) < float(last_part_cost):
                least_amount_cheapest = snp
        
        cheapest_keys = list(cheapest.keys())
        cheapest_key = cheapest_keys[0] if cheapest_keys else None
        least_amount_cheapest_keys = list(least_amount_cheapest.keys())
        least_amount_cheapest_key = least_amount_cheapest_keys[0] if least_amount_cheapest_keys else None

        if part_number not in cheapest_parts:
            cheapest_parts[part_number] = {}
        if cheapest_key:
            cheapest_parts[part_number]["cheapest"] = {cheapest_key: cheapest.get(cheapest_key, {}).get(part_number)}
        if least_amount_cheapest_key:
            cheapest_parts[part_number]["least_amount"] = {least_amount_cheapest_key: least_amount_cheapest.get(least_amount_cheapest_key).get(part_number)}

    return cheapest_parts


def get_single_part_data(part_number: str) -> List[tuple]:
    """
        Runs API calls for all APIs listed in the available_apis function.

        Parameters
        ----------
        part_number: str
            The part number the API should be called with.
        
        Returns
        -------
        list
            a list of tuples containing (supplier, part dictionary):\n
            format: [
                ("supplier1_name", part_dictionary)
                ("supplier2_name", part_dictionary)
            ]
    """
    apis = available_apis()
    api_results = [(supplier_name, api(part_number)) for supplier_name, api in apis]
    return api_results

# EXAMPLE USAGES OF EACH FUNCTION. READ DOCSTRINGS.
# if __name__ == "__main__":
    # mpn = ["M80-8530442", "CLM-110-02-F-D", "INA195AIDBVT"]
    
    # digikey_call = digikey_api(mpn[0])
    # print(digikey_call, "\n")

    # farnell_call = farnell_api(mpn[0])
    # print(farnell_call, "\n")

    # mouser_call = mouser_api(mpn[0])
    # print(mouser_call, "\n")

    # rscomponents_call = rscomponents_api(mpn[0])
    # print(rscomponents_call, "\n")

    # cheapest_vendors = find_cheapest_parts(mpn)
    # print(cheapest_vendors, "\n")

    # part_data = get_single_part_data(mpn[0])
    # print(part_data, "\n")
