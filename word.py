from functions import *

website_link = "https://mrbug.ir"
site_map = crawl_site(website_link)

for i, j in site_map.items():
    print(f"{i} ... {j}")