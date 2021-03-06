#!/usr/bin/python3

from scholarly import scholarly
import json
import sys
import argparse

scholarly.set_logger(True)
def fetch_citations(author, filesave="citations.json", proxy="",  proxy_list=""):
    if proxy != "":
        print("Setting up proxy ", proxy)
        scholarly.use_proxy(scholarly.SingleProxy(http=proxy, https=proxy))
    if proxy_list != "":
        lproxies = open(proxy_list, 'r').readlines() 
        def proxy_gen():
            if proxy_gen.counter >= len(lproxies):
                raise IndexError("We ran out of proxies...")
            proxy = lproxies[proxy_gen.counter]
            if not proxy.startswith("http"):
                proxy = "http://"+proxy
            proxy_gen.counter += 1
            return proxy
        proxy_gen.counter = 0
        scholarly.use_proxy(proxy_gen)

    print("Looking up "+author)
    search = scholarly.search_author(author)    
    author = scholarly.fill(next(search))
    publications = []

    for i, pub in enumerate(author['publications']):
        cites = pub['num_citations']       # often this gets messed up upon .fill()
        if "pub_year" in pub['bib']:
            pubyear = pub['bib']["pub_year"]  # also this gets messed up upon .fill()
            pub = scholarly.fill(pub)
            pub['bib']["pub_year"] = pubyear
        else:
            pub = scholarly.fill(pub)
            if not "pub_year" in pub.bib: 
                # skip publications that really don't have a year, 
                # they probably are crap that was picked up by the search robot
                continue
        
        pub['num_citations'] = cites
        print("Fetching: "+str(i)+"/"+str(len(author['publications']))+": "+pub['bib']["title"]+" ("+str(pub['bib']["pub_year"])+")")
        pub['bib'].pop("abstract", None)
        pub.pop("source", None)
        publications.append(pub)
    f = open(filesave,"w")
    f.write(json.dumps(publications))
    f.close()


description="""
Usage: 
    python fetch_citations.py "author name" -o data.json
    
    Looks up citation data for the selected author on Google Scholar,
    saving to the specified file a JSON string containing all of the info. 
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("author", type=str, help="Name of the author to look up.")
    parser.add_argument("-o", "--output", type=str, default="citations.json", help="Filename to store the citation JSON.")
    parser.add_argument("--proxy", type=str, default="", help="Address of a proxy.")
    parser.add_argument("--proxy-list", type=str, default="", help="Filename containing a list of proxy, one item per line, with format url (including port, e.g. 127.0.0.1:80)")    
    args = parser.parse_args()
    fetch_citations(args.author, args.output, args.proxy, args.proxy_list )

