import json
import os

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
            data = json.loads(new_str)
    os.remove("./rs_scraped_data.html")
    return data

def rs_compontents_scrape_search_results(part_number):
    url = f"https://dk.rs-online.com/web/c/?searchTerm={part_number}"
    data = rs_components_scraper(url)
    return data.get("props",{}).get("pageProps",{}).get("searchFilterResultsData", {}).get("groupBySearchResults", {}).get("resultsList", {}).get("records", [])
    
            
def rs_components_scrape_product_page(rs_part:dict):
    id = rs_part.get("id")
    category = rs_part.get("category")
    print(id, category)
    url = f"https://dk.rs-online.com/web/p/{category.lower()}/{id}"
    data = rs_components_scraper(url)
    return data.get("props", {}).get("pageProps", {}).get("articleResult", {}).get("data", {}).get("article",{})
    

def rs_components_get_single_part(part_number):
    data = rs_compontents_scrape_search_results("M80-8530442")
    single_part = [part for part in data if "Leveres Pr. stk." in part.get("uomMessage")]
    if single_part:
        single_part = rs_components_scrape_product_page(single_part[0])
    return single_part

