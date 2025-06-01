from bs4 import BeautifulSoup
import requests
import dns.resolver
import socket
import re

def get_links(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Can't connect to: {url}.")
        return set()

    soup = BeautifulSoup(response.content, "html.parser")
    links = set()
    for link in soup.find_all("a", href=True):
        try:
            href = link.get("href")
            if href.startswith("http"):
                links.add(href)
        except:
            print("Can't connect to site")
    return links


def crawl_site(url, depth=2):
    visited = set()
    all_links = []

    def crawl(current_url, current_depth):
        if current_depth > depth or current_url in visited:
            return
        visited.add(current_url)
        links = get_links(current_url)
        # for i in list(links):
        #     all_links.append(i)
        all_links.extend(list(links))
        for link in links:
            crawl(link, current_depth + 1)

    crawl(url, 1)
    return all_links


def check_title_status(domain):
    try:
        response = requests.get(domain)
        status = response.status_code
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.title.string
        return [title, status]
    except Exception as e:
        return ['', '']

def get_ip(domain):
    return socket.gethostbyname(domain)


def check_subdomains(domain:str):
    domain = domain.replace("https://", "").replace("http://", "")
    found = {}
    with open("wordlist.txt", 'r', encoding='utf-8') as f:
        i = 0.0
        for line in f:
            if i == 50:
                break
            sub = line.strip()
            if not sub:
                continue
            full_domain = f"{sub}.{domain}"
            try:
                dns.resolver.resolve(full_domain, 'A')
                details = check_title_status(f"https://{full_domain}")
                ip_address = get_ip(full_domain)
                details.append(ip_address)
                found[full_domain] = details
                print(full_domain)
                # print(f"{full_domain}, title: {details[0]}, status: {details[1]}, ip address: {ip_address}")
                # i += 1
            except Exception as e:
                # i += 0.5
                continue
    return found



common_ports = [21, 22, 23, 25, 53, 80, 110, 119, 123, 143, 161, 194, 443, 445, 993, 995]
def get_ports(ip_address):
    open_ports = []
    for port in common_ports:  
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip_address, port))
        if result == 0:
            open_ports.append(port)
            print(f"Port {port} is open")
        sock.close()
    return open_ports

# get email and phone numbers in site using regex
def get_information(domain):
    try:
        response = requests.get(domain)
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()

        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        phones = re.findall(r"(?:\+?\d{1,3}[- ]?)?(?:0?\d{2,4}[- ]?)?\d{3}[- ]?\d{4}", text)

        return {"emails": emails, "phones": phones}
    except Exception as e:
        return {"emails": [], "phones": []}

def generate_html_report(
    website_link, site_map, subdomains, open_ports, emails, phones, whois_info, filename="reconpie_report.html"
):
    html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ReconPie Report for {website_link}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2 {{ color: #2c3e50; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 30px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; }}
        th {{ background-color: #f2f2f2; }}
        ul {{ list-style-type: disc; margin-left: 20px; }}
    </style>
</head>
<body>
    <h1>ReconPie Report</h1>
    <h2>Target: {website_link}</h2>

    <h2>Site Map (Top 5 Links)</h2>
    <ul>
        {''.join(f'<li>{link}</li>' for link in site_map[:5])}
    </ul>
    <p>And {len(site_map[5:])} more links found.</p>

    <h2>Subdomains</h2>
    <table>
        <tr>
            <th>Subdomain</th>
            <th>Status</th>
            <th>IP Address</th>
        </tr>
        {''.join(f"<tr><td>{sub}</td><td>{subdomains[sub][1]}</td><td>{subdomains[sub][2]}</td></tr>" for sub in subdomains)}
    </table>

    <h2>Main IP Open Ports</h2>
    <ul>
        {''.join(f'<li>{port}</li>' for port in open_ports)}
    </ul>

    <h2>Emails Found</h2>
    <ul>
        {''.join(f'<li>{email}</li>' for email in set(emails))}
    </ul>

    <h2>Phone Numbers Found</h2>
    <ul>
        {''.join(f'<li>{phone}</li>' for phone in set(phones))}
    </ul>

    <h2>WHOIS Information</h2>
    <pre>{whois_info}</pre>
</body>
</html>
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_report)
    print(f"HTML report generated: {filename}")