#!/usr/bin/python
#This script rips all the existing locus tags from http://tuberculist.epfl.ch and gets all the information fields for these locusses as specified in the script

import urllib2 		#Module that provides an updated API for using internet resources identified by URLs, so allows easy communication with websites
import operator 	#For extracting multiple keys/indices in a specific order
import collections 	#For the defaultdict, generates a value for non existing keys
import re 			#Regular expressions library
import sys 			#Library that allows bett, in our case sys.stderr to print something, a line, when the format of that lyne is of different format than expected


locusTagDictionary={}	
locusTagList=[]			#All locus tags that are found will be stored in this list

#First get all locus tags from the website, read the website
html_file = urllib2.urlopen("http://tuberculist.epfl.ch/quicksearch.php?gene+name="+'Rv'+"&submit=Search") #Get website when you search for 'Rv', returns all locus tags
html_in = html_file.read() #The resulting html is one string not a file yet
html_file.close()

#Cut out the locus tags/RvXXXX from the 'html_in' and make a list of all the existing locus tags
for line in html_in.split('\n'): #Break up the html in to individual lines
	if "Search'>" in line:
		locusTag=line.split("Search'>")[-1].split("</td>")[0]
		locusTagList.append(locusTag)

		
column_names = ["Gene name","Rv number","Type", "Function", "Product", "Comments","Functional category" , "Proteomics","Mutation","Regulon"]
key_getter = operator.itemgetter(*column_names)
pattern = re.compile('<.+?>(.*?)</.+?>') #Patern compiled to replace html tags later on

#Get the info for each locusTag in the list from Tuberculist and add its information to the dictionary
print '"'+'"\t"'.join(column_names)+'"' # Join adds string between every ellement of whatever you put in join (list Tuple of strings)
total_number_of_locus = str(len(locusTagList))#string contaiing number of locus tags
length_str_length = len(total_number_of_locus)#length digits in number of locus tags

#Loop via enumerate over the list of locus tags
for locus_count, locusTag in enumerate(sorted(locusTagList), start=1):
	current_locus_count = str(locus_count).zfill(length_str_length) #zerofill the current locus tag number with 0
	printed_line = current_locus_count+"/"+total_number_of_locus+"\t"+locusTag+"\n"
	sys.stderr.write(printed_line) #write to stderr, so give back the line in case an error is caught so the problem can be easilly identified
	url=str("http://tuberculist.epfl.ch/quicksearch.php?gene+name=")+str(locusTag)+str("&submit=Search")
	html_file = urllib2.urlopen(url)
	html_in = html_file.read().decode()
	html_file.close()
	locusTagDictionary[locusTag]=collections.defaultdict(str)
	#locusTagDictionary[locusTag]["url"] = "=Hyperlink('"+url+"')" #add the url to the source page
	parts = html_in.split("<big>Coordinates</big")[0].split("<table")
	#Take the part of the tables we want
	for part in parts:
		parts2 = part.split("</table>")[0].replace("</TR>", "").split("<TR>")[1:]
		for part2 in parts2:
			try:
				part2 = part2.rstrip() #Remove all whitespace characters
				#print part2
				if part2:
					infoType = part2.split("<b>",1)[-1].split("</b>")[0]
					info = part2.split("</TD><TD>")[1].split("</TD>")[0]
					info=pattern.sub('\g<1>',info) #Remove all html tags, the '(' indicate this string must be remembered, g<1> referes back that anything between the tag must be kept/replace with g<1>
					infoType=pattern.sub('\g<1>',infoType) #Remove all html tags, \g<1> means, replace all tags with Whatever was between () in the patern, that what was between the html tag
					locusTagDictionary[locusTag][infoType] = info
			except: #In the case the part2 is only rubish, like below,skip and go on to see if another fragment of the table is interesting
				if part2 in ("<TH COLSPAN=3 align=left><a name=\"comments\"></a><big>General annotation</big></TH>", "<TH COLSPAN=4 align=left><a name=\"coordinates\"></a>"):
					continue
				print part2
				raw_input("next??")
		
	print '"'+'"\t"'.join(key_getter(locusTagDictionary[locusTag]))+'"\t=Hyperlink("'+url+'")' #Add the url to the source page

