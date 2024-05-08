import json
import requests
from api_setup import RS_BASE_URL, SINGLE_PART_UOMMESSAGE

def rs_components_scraper(url):
    res = requests.get(url)
    content = res.content.decode()
    data = {}
    first_line = None
    if content.find("__NEXT_DATA__") != -1:
        first_line = content.index("__NEXT_DATA__")
    if first_line:
        line = content[first_line:]
        startsubindex = line.find("__NEXT_DATA__")
        new_str = line[startsubindex+39:]
        endsubindex = new_str.find("</script>")
        new_str = new_str[:endsubindex]
        try:
            data = json.loads(new_str)
        except Exception:
            print("Could not load scraped string as json.")
    return data


def rs_compontents_scrape_search_results(part_number: str) -> list:
    url = f"{RS_BASE_URL}web/c/?searchTerm={part_number}"
    data = rs_components_scraper(url)
    return data.get("props",{}).get("pageProps",{}).get("searchFilterResultsData", {}).get("groupBySearchResults", {}).get("resultsList", {}).get("records", [])
    
            
def rs_components_scrape_product_page(rs_part:dict) -> dict:
    id = rs_part.get("id")
    category = rs_part.get("category")
    url = f"{RS_BASE_URL}web/p/{category.lower()}/{id}"
    data = rs_components_scraper(url)
    return data.get("props", {}).get("pageProps", {}).get("articleResult", {}).get("data", {}).get("article",{})
    

def rs_components_get_single_part(part_number):
    data = rs_compontents_scrape_search_results(part_number)
    single_part = [part for part in data if SINGLE_PART_UOMMESSAGE in part.get("uomMessage")]
    if single_part:
        return rs_components_scrape_product_page(single_part[0])
    return {}

