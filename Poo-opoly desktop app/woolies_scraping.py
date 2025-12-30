from playwright.sync_api import sync_playwright
import sys
import json
import unicodedata
from my_lists import error_popup

POSTCODE = "3186"  # hard coded values
LOCATION_NAME = "Woolworths Middle Brighton, 3186"
LOCATION_ID = "5382"
products = [] 
number_of_products = 0

def start_browser(p):
    try:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        context.add_cookies([
            {"name": "sf-postcode", "value": POSTCODE, "domain": "www.woolworths.com.au", "path": "/"},
            {"name": "sf-locationName", "value": LOCATION_NAME, "domain": "www.woolworths.com.au", "path": "/"},
            {"name": "sf-locationId", "value": LOCATION_ID, "domain": "www.woolworths.com.au", "path": "/"},
        ])
        return context.new_page()
    
    except Exception as e:
        print("Error, maybe wi-fi is off? ", e)
        return None

def scrape(url):
    global number_of_products
    with sync_playwright() as p:
        try:
            page = start_browser(p)        
            if not page:
                sys.exit() #stop script
            
            page.goto(url)
            page.wait_for_selector("span.sf-item-heading")

            while True:
                for element in page.query_selector_all("div.shelfProductStamp-mainContainer"): #scraping
                    
                    product_name = element.query_selector("span.sf-item-heading")                               #inner_text() gives visiable text of element
                    product_name= product_name.inner_text().lstrip("\ufeff").strip() if product_name else "N/A" #get rid of weird chars
                    nfkd_form = unicodedata.normalize("NFKD", product_name)       #fixes symbols like in nestle (with weird e)
                    product_name = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
                    product_name = product_name.encode('ascii', errors='ignore').decode('ascii') #remove non ascii chars
                    product_name=product_name.lower()

                    product_price= element.query_selector("span.sf-pricedisplay")
                    product_price= product_price.inner_text().strip() if product_price else "N/A"
                    
                    product_quantifier= element.query_selector("span.sf-nowprice > span.sf-optionsuffix")
                    product_quantifier= product_quantifier.inner_text().strip() if product_quantifier else "N/A"
                    
                    product_discount = element.query_selector("span.sf-regoptiondesc")
                    product_discount = product_discount.inner_text().replace(", Save", "").strip() if product_discount else "N/A"
                    if product_discount in ["Range was", "Was", "Save"]:
                        previous_price = element.query_selector("span.sf-regprice")
                        previous_price = previous_price.inner_text().strip() if previous_price else ""
                        product_discount = f"{product_discount} {previous_price}"

                    product_img = element.query_selector("img")
                    product_url = product_img.get_attribute("src") 
                
                    item = [product_name, product_price, product_quantifier, product_discount, "Woolworths", product_url]
                        
                    products.append(item)
                    number_of_products += 1

                next_button = page.query_selector('a[aria-label="Next page"]') # try to find the "Next" button
                if not next_button:
                    break

                first_product_name = page.query_selector("span.sf-item-heading").inner_text().strip() #remember first product name to detect change
                page.click('a[aria-label="Next page"]')                                              #go to next page

                page.wait_for_function(  # wait for new products to load (different first product) by comparing string
                    f'document.querySelector("span.sf-item-heading").innerText !== "{first_product_name}"'
                )
            
            with open("woolies_cata.json", "w", encoding="utf-8") as f: #'w' overwrites the file
                json.dump(products, f, ensure_ascii=False, indent=4)
        
        except:
            error_popup("Error", "Error extracting catelogue")
            output = []                                         #wipe the json 
            with open("woolies_cata.json", "w", encoding="utf-8") as f: #'w' overwrites the file
                json.dump(output, f, ensure_ascii=False, indent=4)
            return "failed"
    
    return "success"
    
    

    
    

