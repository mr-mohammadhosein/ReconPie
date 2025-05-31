from functions import *

website_link =  "https://mrbug.ir" # input("Enter website link: ")


print("Site map crawling...\n")
# site_map = crawl_site(website_link, depth=2)
# print('')
# for i in site_map[:5]:
#     print(i)
# print(f"\nand {len(site_map[5:])} more links")


# print("\ncollecting subdomains...")
subdomains = check_subdomains(website_link)

# get an item from dict by index
main_ip = (subdomains[list(subdomains.keys())[0]][2])
open_ports = get_ports(main_ip)
print(open_ports)