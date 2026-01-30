from firecrawl import Firecrawl
from dotenv import load_dotenv
import pandas as pd
import os
import time
from constants import DATA_PATH
from datetime import datetime, timedelta

load_dotenv()

def crawl(url: str, limit: int) -> list: 
    """
    Add url and limit for crawling. 
    e.g. if url is https://omni.se, firecrawl will crawl entire site that is generated on start, click one article and crawl it, then go back to url and continue on the next one.
    Don't have the limit higher than 1000. One article ~ one credit.
    """
    
    crawl_list = []
    firecrawl = Firecrawl(os.getenv("CRAWL_KEY")) 

    print("Starting crawl")
    full_crawl = firecrawl.crawl(url=url, 
                        limit=limit, # hur många sidor den ska crawla
                        crawl_entire_domain=True, #Behövs för att varje crawl ska bli ett eget objekt
                        max_discovery_depth=1, # ta bara en länk in från angiven url
                        scrape_options={"formats": ["markdown"]}, #format för datan
                        )
    crawl_list.append(full_crawl)
    page_name = url.replace("https://", "").split('.')[0]
    print(f"crawl nr.{len(crawl_list)} from page: {page_name} finished")

    return crawl_list, page_name


def sort_crawl(crawl_list) -> list:
    """
    Sort the crawls to only take actual articles with specified date. 
    """
    relevant_crawls = []
    for full_crawl in crawl_list: # för varje artikel från crawlingen
        for item in full_crawl.data: 
            metadata_dict = item.metadata.model_dump() #Hämta ut kolumen og:type från varje artikel i CrawlJob. 
            date = metadata_dict.get("published_time")
            # date = pd.to_datetime(date).dt.date
            
            if date is not None and date > str(datetime.today() - timedelta(days=2)):
                relevant_crawls.append(item)
                
            json_data =[item.model_dump() for item in relevant_crawls]
    print(f"\n{len(relevant_crawls)} relevant crawls was found.\n")

    return json_data


def save_crawl_to_json(json_data: list, page_name: str):
    """
    Save relevant crawls to a json file for reading into vectorDB later. 
    """
    df = pd.DataFrame([item["metadata"] for item in json_data]) #skapa df från dictionary'n metadata, där allt roligt finns!

    df = df.drop_duplicates(subset="title", keep="first")

    df_cleaned = df[["title", "description","article:section","published_time", "og:image:alt", "og:image"]] #hämta ut de relevanta kolumnerna

    df_cleaned = df_cleaned.rename(columns={ #renama till snyggare
        "description": "teaser_text",
        "published_time": "date",
        "article:section": "news_section",
        "og:image:alt": "image_description",
        "og:image": "image_url",
    })
    df_cleaned["date"] = pd.to_datetime(df_cleaned["date"]).dt.date #konvertera till datetime, ta bara date

    for image in df_cleaned["image_description"]: 
        if type(image) == list:
            
            image = str(image[0])

    df_cleaned["image_description"] = df_cleaned["image_description"].astype(str)

    json_str = df_cleaned.to_json(indent=4, force_ascii=False, orient="records", date_format="iso") #spara den rena df:n till json
    with open(f"{DATA_PATH}/{page_name}_{str(datetime.now().strftime("%d_%m_%Y_%H-%M-%S"))}.json", "w", encoding="utf-8") as file:
        file.write(json_str)
    
    print(f"{page_name} crawl with {len(df_cleaned)} results was written to json-file")

if __name__ == "__main__":
    
    url = "https://omni.se" #Lägg till vilken länk den ska crawla
    limit = 50 #ange hur många sidor den max ska ta i 2 omgångar
    
    crawl_list, page_name = crawl(url, limit)
    json_data = sort_crawl(crawl_list)
    save_crawl_to_json(json_data, page_name) # din fil kommer sparas till json i /data i länknamnet, 

