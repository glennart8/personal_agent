from firecrawl import Firecrawl
from dotenv import load_dotenv
import pandas as pd
import os
from datetime import datetime, timedelta
from rag_agent import news_agent
import asyncio
import requests

load_dotenv()

BACKEND_BASE_URL = os.getenv("BACKEND_URL")


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
    print(f"crawl from page {page_name} finished")

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
            
            if date is not None and date > str(datetime.today() - timedelta(days=4)):
                relevant_crawls.append(item)
                
            json_data =[item.model_dump() for item in relevant_crawls]
    print(f"\n{len(relevant_crawls)} relevant crawls was found.\n")

    return json_data


def save_crawl_to_json(json_data: list, page_name: str):
    """
    Save relevant crawls to a json file for reading into vectorDB later. 
    """
    data = requests.get(f"{BACKEND_BASE_URL}/news/cleaned")
    
    old_df = pd.DataFrame(data.json())
    
    json_data_df = pd.DataFrame([item["metadata"] for item in json_data]) #skapa df från dictionary'n metadata, där allt roligt finns!

    df = json_data_df.drop_duplicates(subset="title", keep="first")

    df_cleaned = df[["title", "description","article:section","published_time", "og:image:alt", "og:image"]] #hämta ut de relevanta kolumnerna

    df_cleaned = df_cleaned.rename(columns={ #renama till snyggare
        "description": "teaser_text",
        "published_time": "date",
        "article:section": "news_section",
        "og:image:alt": "image_description",
        "og:image": "image_url",
    })
    df_cleaned["date"] = pd.to_datetime(df_cleaned["date"]).dt.strftime('%Y-%m-%d') #konvertera till datetime, ta bara date
    
    for image in df_cleaned["image_description"]: 
        if type(image) == list:
            
            image = str(image[0])

    df_cleaned["image_description"] = df_cleaned["image_description"].astype(str)

    df_cleaned = pd.concat([old_df, df_cleaned], ignore_index=True) #slå ihop den gamla df med den som skapades nu
    df_cleaned = df_cleaned.drop_duplicates(subset="title", keep="first") #ta bort dubletter
    
    json_str = df_cleaned.to_json(indent=4, force_ascii=False, orient="records", date_format="iso") #spara den rena df:n till json

    data_to_send = {
        "page_name": f"{page_name}_cleaned.json",
        "data": json_str
    }
    requests.post(f"{BACKEND_BASE_URL}/news/post_news", json=data_to_send)
    print(f"{page_name} crawl with {len(df_cleaned)} results was written to json-file")
    
    return json_data_df

async def add_keywords_with_agent(new_data): 
    """
    Adds mood and keywords for new data that hasn't been processed.
    """
    output_list = []

    data = requests.get(f"{BACKEND_BASE_URL}/news")
    titles_already_processed = {row["title"] for row in data.json()}
    
    old_df = pd.DataFrame(data.json())
    old_df["date"] = pd.to_datetime(old_df["date"]).dt.strftime('%Y-%m-%d') #konvertera till datetime, ta bara date
    
    df_to_process = new_data[~new_data["title"].isin(titles_already_processed)].copy() #om den nya data inte innehåller de gamla titlarna, skicka in det till agenten

    df_for_agent = pd.DataFrame(df_to_process)[["title", "description"]]
    
    batch_size = 30
    for i in range(0, len(df_for_agent), batch_size):
        batch_df = df_for_agent.iloc[i:i + batch_size]
    
        print("Agent is analyzing..")
        result = await news_agent.run(f"Analysera dessa artiklar: {batch_df.to_json(orient="records")}")
        output_list.append(result.output) # dessa är nya rader med keyword och mode. dom ska fyllas på i den json_fil som inte har det. 

    keywords = []
    moods = []

    for batch in output_list: 
        for article in batch.articles:
            moods.append(article.mood)
            keywords.append(article.keywords)

    df_to_process["mood"] = moods
    df_to_process["keywords"] = keywords

    df_to_process = df_to_process[["title", "description","article:section","published_time", "og:image:alt", "og:image", "mood", "keywords"]] #hämta ut de relevanta kolumnerna

    df_to_process = df_to_process.rename(columns={ #renama till snyggare
        "description": "teaser_text",
        "published_time": "date",
        "article:section": "news_section",
        "og:image:alt": "image_description",
        "og:image": "image_url",
    })
    
    df_to_process["date"] = pd.to_datetime(df_to_process["date"]).dt.strftime('%Y-%m-%d') #konvertera till datetime, ta bara date
    
    merged_df = pd.concat([old_df, df_to_process], ignore_index=True)
    
    merged_df["mood"] = merged_df["mood"].str.capitalize()
    
    for image in merged_df["image_description"]: 
        if type(image) == list:
            
            image = str(image[0])

    merged_df["image_description"] = merged_df["image_description"].astype(str)
    
    merged_df["mood"] = merged_df["mood"].str.capitalize()
    merged_df["date"] = pd.to_datetime(merged_df["date"]).dt.strftime('%Y-%m-%d')
    merged_df['keywords'] = merged_df['keywords'].apply(lambda x: ", ".join([w[0].upper() + w[1:] for w in x.split(", ")]))
    
    merged_df_json = merged_df.to_json(indent=4, orient="records", force_ascii=False, date_format="iso")
    page_name = "omni"
    data_to_send = {
        "page_name": f"{page_name}_cleaned_with_keywords.json",
        "data": merged_df_json
    }
    requests.post(f"{BACKEND_BASE_URL}/news/post_news", json=data_to_send)

    print(f"\n\n{len(df_to_process)} articles was processed")

if __name__ == "__main__":
    
    url = "https://omni.se" #Lägg till vilken länk den ska crawla
    limit = 250 #ange hur många sidor den ska ta
    print("Your limit is: ", limit)
    crawl_list, page_name = crawl(url, limit)
    json_data = sort_crawl(crawl_list)
    json_data_df = save_crawl_to_json(json_data, page_name) # din fil kommer sparas till json i /data i länknamnet
    
    asyncio.run(add_keywords_with_agent(json_data_df))
    
    
    

