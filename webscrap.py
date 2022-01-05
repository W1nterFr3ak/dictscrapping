#!/usr/bin/env python3

# imports
from colorama import Fore, Style
from bs4 import BeautifulSoup
from collections import Counter
from pprint import pprint
import validators
import argparse, sys
import requests
import math
import nltk
import os

# screen size
rows, cols = os.popen('stty size', 'r').read().split()
# nltk.download('words')

# test url
url = "https://www.pesapal.com/"

def clean_wordlist(wordlist):
	"""
    Cleans a list of words.

    Parameters
    ----------
    wordlist : list
        The list to be cleaned.

	"""
	clean_word_list = []
	for word in wordlist:
		char = "!@#$%^&*()_-+={[}]|\;:\"<>?/.,© "

		for i in range(len(char)):
			word = word.replace(char[i], '')
		if word:
			clean_word_list.append(word)

	return clean_word_list


def get_wordcount(url):
	"""
    Downloads text from webpage and gets the word frequebcy.

    Parameters
    ----------
    url : string
        The page to be scraped.
  
    """
	wordlist = []
	try:
	    res = requests.get(url,timeout=10)
	except requests.exceptions.RequestException as e:  # This is the correct syntax
	    # raise SystemExit(e)
	    print(f"{Fore.RED}Please check if you have an active internet connection or if the web page exists {Fore.BLUE}{url}{Style.RESET_ALL}!")
	    sys.exit(1)
	
	html_page = res.content
	soup = BeautifulSoup(html_page, 'html.parser')
	text = soup.find_all(text=True)

	# checkptags = set([t.parent.name for t in text]) # view to know what to exclude
	excluded = ['header','html',
				 'noscript','[document]',
			     'meta','head', 
	             'input','script',]
	# print(checkptags)

	for t in text:
		if t.parent.name not in excluded:
			w = [n.lower() for n in t.strip('\n').split() if n]
			wordlist.extend(w)

	counts = Counter(clean_wordlist(wordlist))
	return counts


def get_nonenglish(word_dict):
	"""
    Takes a dictionary of words and their counts and returns a list of none 
    english words.

    Parameters
    ----------
    word_dict : dict
        dictionary of word count.
  
    """
	try:
		brown = nltk.corpus.brown.words()
	except LookupError:
		print(f"{Fore.RED}Downloading Brown english wordlist please wait -----")
		nltk.download('brown')
		brown = nltk.corpus.brown.words()
		print(f"\nThanks for the wait brown downloaded {Style.RESET_ALL}")
		
	eng_words = [i.lower() for i in set(brown)]
	words = list(word_dict.keys())

	c = [i for i in words if i not in eng_words ]

	return c

	

def validate_args(args):
	"""
	Compares words of two webpages.

	Parameters
	----------
	args : object
	    argparse object containing 
	    	url: string
	    		the url for the first web page.
	    	url2: string
	    		the url for the second web page.
	    	compare: boolean
	    		states wether to compare the two urls

	"""
	if not args.url:
		parser.print_help(sys.stderr)
		sys.exit(1)

	if not validators.url(args.url):
		print(F"{Fore.RED}Please use a valid url")
		sys.exit(1)

	if args.compare and args.url2:
		if not validators.url(args.url2):
			print(f"{Fore.RED}Please use a valid url")
			sys.exit(1)
	elif args.compare and not args.url2:
		print(f"{Fore.RED}To compare two pages use : --url2 to include the second url ")
		sys.exit(1)


def print_list(obj, cols=4, columnwise=True, gap=6):
	"""
	Print the given list in evenly-spaced columns.

	Parameters
	----------
	obj : list
	    The list to be printed.
	cols : int
	    The number of columns in which the list should be printed.
	columnwise : bool, default=True
	    If True, the items in the list will be printed column-wise.
	    If False the items in the list will be printed row-wise.
	gap : int
	    The number of spaces that should separate the longest column
	    item/s from the next column. This is the effective spacing
	    between columns based on the maximum len() of the list items.
	"""

	sobj = [str(item) for item in obj]
	if cols > len(sobj): cols = len(sobj)
	max_len = max([len(item) for item in sobj])
	if columnwise: cols = int(math.ceil(float(len(sobj)) / float(cols)))
	plist = [sobj[i: i+cols] for i in range(0, len(sobj), cols)]
	if columnwise:
	    if not len(plist[-1]) == cols:
	        plist[-1].extend(['']*(len(sobj) - len(plist[-1])))
	    plist = zip(*plist)
	printer = '\n'.join([
	    ''.join([c.ljust(max_len + gap) for c in p])
	    for p in plist])
	print(printer)

def print_word_list(url, verbose=False):
	"""
    Prints word count

    Parameters
    ----------
    url : string
        webpage to get words.
    verbose : boolean
    	True or False value to consider printing all the words
   """
	wc1 = get_wordcount(url)
	print(f"Word count dictionary for {Fore.BLUE}{url}{Style.RESET_ALL}")
	if verbose:
		pprint(wc1.most_common())
	else:
		pprint(wc1.most_common(10))

	print(f"None english words for {Fore.BLUE}{url}{Style.RESET_ALL}")
	nne = get_nonenglish(dict(wc1))
	print_list(nne)


def comp_pages(args):# redundant
	"""
    Compares words of two webpages.

    Parameters
    ----------
    args : object
        argparse object containing 
        	url: string
        		the url for the first web page.
        	url2: string
        		the url for the second web page.
  
    """
	wc1 = get_wordcount(args.url)
	wc2 = get_wordcount(args.url2)
	sm = wc1 & wc2
	per = round(len(dict(sm))/len(dict(wc1)) * 100, 2)
	per2 = round(len(dict(sm))/len(dict(wc2)) * 100, 2)

	# dif = wc1 - wc2
	print("#"*int(cols))
	print(f"Similar words between {Fore.BLUE}{args.url}{Style.RESET_ALL} and {args.url2}{Style.RESET_ALL}")
	print("_"*int(cols))
	print(f"{Fore.BLUE}{args.url}{Style.RESET_ALL} words are {Fore.MAGENTA}{per}%{Style.RESET_ALL} similar to {Fore.BLUE}{args.url2}{Style.RESET_ALL}")
	print(f"{Fore.BLUE}{args.url2}{Style.RESET_ALL} words are {Fore.MAGENTA}{per2}%{Style.RESET_ALL} similar to {Fore.BLUE}{args.url}{Style.RESET_ALL}")
	print("-"*int(cols))


	
	print_list(list(dict(sm).keys()))

def main():
	parser = argparse.ArgumentParser(description="Diction & dictionary scrapping.")
	parser.add_argument("-u", "--url", help = "url to scrape")
	parser.add_argument("-c", "--compare", help="compare two webpage output difference and intercection", action='store_true')
	parser.add_argument("-u2", "--url2", help="second url if comparing")
	parser.add_argument("-v", "--verbose", help="print all words else print most common", action="store_true")

	
	if len(sys.argv)==1:
	    parser.print_help(sys.stderr)
	    sys.exit(1)
	args = parser.parse_args()
	validate_args(args)

	# print(args.url)
	if args.compare:
		print_word_list(args.url, args.verbose)
		print("="*int(cols))
		print_word_list(args.url2, args.verbose)
		print("\n\n")
		comp_pages(args)
	else:
		print_word_list(args.url, args.verbose)

	 
		

if __name__ == '__main__':
	# get_nonenglish(get_wordcount(url))
	main()

