from functions import *
from whois import whois
import argparse


parser = argparse.ArgumentParser(description="ReconPie - Website Reconnaissance Tool")
parser.add_argument("website_link", type=str, help="Website link to scan (e.g. https://python.org)")
args = parser.parse_args()
website_link = args.website_link


print("Site map crawling...\n")
site_map = crawl_site(website_link, depth=2)
print('')
for i in site_map[:5]:
    print(i)
print(f"\nand {len(site_map[5:])} more links")


print("\ncollecting subdomains...")
subdomains = check_subdomains(website_link)

# get an item from dict by index
main_ip = (subdomains[list(subdomains.keys())[0]][2])
open_ports = get_ports(main_ip)


emails, phones = [], []
for subdomain in subdomains:
    info = get_information(f"https://{subdomain}")
    emails.extend(info["emails"])
    phones.extend(info["phones"])
print("information collected.")

whois_info = whois(website_link)
print("whois completed.")

generate_html_report(website_link, site_map, subdomains, open_ports, emails, phones, whois_info)