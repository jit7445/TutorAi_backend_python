import firecrawl
client = firecrawl.FirecrawlApp(api_key="fc-9da27046b0a44ce5a02e19e1fcb4fbb5")
doc = client.scrape("https://example.com", formats=["markdown"])
print(type(doc), doc)
