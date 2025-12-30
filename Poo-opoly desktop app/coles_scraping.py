import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import FreeSimpleGUI as gui
import time
import json
import time
import unicodedata
from my_lists import error_popup

def scrape():
    with uc.Chrome() as driver:
        driver.get("https://www.coles.com.au")
        
        error_popup("Locate Catalogue", "Close this window when you have located the catalogue. " \
        "Do not close the browser window. It will close automatically when scraping is complete")

        try:                                                           #click the button until it disappears
            load_more_button = driver.find_element(By.ID, "show-more") #find the button
            while True:
                style = load_more_button.get_attribute("style")        #the style changes when the button is no longer available to click
                if "display: none" in style:  #reached the end of cata
                    break
                load_more_button.click()
                time.sleep(0.5)

            all_items = driver.find_element(By.CSS_SELECTOR, "div#sf-items-table") #hashtag for id of the table
            products = all_items.find_elements(By.CSS_SELECTOR, "a.sf-item.mid")
            half_off_products = all_items.find_elements(By.CSS_SELECTOR, "a.sf-item.mid.sf-halfspecial")
            output = []

            for product in products:      
                product_name = product.get_attribute("title")
                try:
                    amount = product.find_element(By.CSS_SELECTOR, "span.sf-saleoptiondesc").text
                    product_name = f"{product_name} {amount}"
                except:
                    product_name = product_name + ""
                nfkd_form = unicodedata.normalize("NFKD", product_name)       #fixes symbols like in nestle (with weird e)
                product_name = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
                product_name = product_name.encode('ascii', errors='ignore').decode('ascii') #remove non ascii chars
                product_name=product_name.lower()

                try:
                    product_price = product.find_element(By.CSS_SELECTOR, "span.sf-pricedisplay").text
                except: product_price = "0"

                try:
                    product_quantifier = product.find_element(By.CSS_SELECTOR, "span.sf-optionsuffix")
                    product_quantifier = product_quantifier.text.strip()
                    # if not product_quantifier:
                    #     product_quantifier = "N/A"
                except:
                    product_quantifier = "N/A"

                if(product in half_off_products): product_discount = "1/2 Price"
                else: 
                    try:
                        product_discount = product.find_element(By.CSS_SELECTOR, "span.sf-regoptiondesc").text
                        product_discount = product_discount.replace(", Save", "")
                    except: product_discount = "N/A"
                
                product_url = product.find_element(By.TAG_NAME, "img").get_attribute("src")
                
                item = [product_name, product_price, product_quantifier, product_discount, "Coles", product_url]
                output.append(item)
            
            print(f"scraped {len(output)} items")
            with open("coles_cata.json", "w", encoding="utf-8") as f: #'w' overwrites the file
                json.dump(output, f, ensure_ascii=False, indent=4)

        except Exception as e:
            error_popup("Error", "Error extracting catelogue")
            output = []                                         #wipe the json 
            with open("coles_cata.json", "w", encoding="utf-8") as f: #'w' overwrites the file
                json.dump(output, f, ensure_ascii=False, indent=4)
            return "failed"
    
    driver.quit()
    return "success"


    



