site_name: str = "Books to Scrape"
site_url: str = "https://books.toscrape.com"
is_recheable: bool = True


def build_report(name: str, url: str) -> str:
    """Form string_report about site"""
    return f"Site '{name}' ({url}) is beginning to parsing"


if is_recheable:
    report = build_report(site_name, site_url)
else:
    report = "Site is unrecheable"


print(report)
