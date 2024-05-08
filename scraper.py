import json
import os
from api_setup import RS_BASE_URL, SINGLE_PART_UOMMESSAGE

def rs_components_scraper(url):
    os.system(f"curl --output rs_scraped_data.html {url}")
    data = {}
    with open("./rs_scraped_data.html", "r") as fp:
        lines = fp.readlines()
        first_line = None
        for line in lines:
            if line.find("__NEXT_DATA__") != -1:
                first_line = lines.index(line)
                break
        if first_line:
            line = lines[first_line:][0]
            startsubindex = line.find("__NEXT_DATA__")
            new_str = line[startsubindex+39:]
            endsubindex = new_str.find("</script>")
            new_str = new_str[:endsubindex]
            try:
                data = json.loads(new_str)
            except Exception:
                print("Could not load scraped string as json.")
    os.remove("./rs_scraped_data.html")
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
        single_part = rs_components_scrape_product_page(single_part[0])
    return single_part

