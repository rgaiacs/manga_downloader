#!/usr/bin/env python

######################

from xml.dom import minidom

######################

from parsers.thread import SiteParserThread
from util import fixFormatting, getText
import os
######################

class MangaXmlParser:
	def __init__(self, optDict):
		self.options = optDict
		for elem in vars(optDict):
			setattr(self, elem, getattr(optDict, elem))

	def downloadManga(self):
		print("Parsing XML File...")
		if (self.verbose_FLAG):
			print("XML Path = %s" % self.xmlfile_path)
 
		dom = minidom.parse(self.xmlfile_path)
		
		threadPool = []
		self.options.auto = True
		
		SetOutputPathToName_Flag = False
		# Default OutputDir is the ./MangaName
		if (self.options.outputDir == 'DEFAULT_VALUE'):
			SetOutputPathToName_Flag = True
			
		for node in dom.getElementsByTagName("MangaSeries"):
			name = getText(node.getElementsByTagName('name')[0])
			site = getText(node.getElementsByTagName('HostSite')[0])
			
			try:
				lastDownloaded = getText(node.getElementsByTagName('LastChapterDownloaded')[0])
			except IndexError:
				lastDownloaded = ""
			
			try:
				download_path =	getText(node.getElementsByTagName('downloadPath')[0])
			except IndexError:
				download_path = ('./' + fixFormatting(name))
			
			self.options.site = site
			self.options.manga = name
			self.options.downloadPath = download_path
			self.options.lastDownloaded = lastDownloaded
			if SetOutputPathToName_Flag:
				self.options.outputDir = download_path
			
			# Because the SiteParserThread constructor parses the site to retrieve which chapters to 
			# download the following code would be faster
			
			# thread = SiteParserThread(self.options, dom, node)
			# thread.start()
			# threadPool.append(thread)
			
			# Need to remove the loop which starts the thread's downloading. The disadvantage is that the 
			# the print statement would intermingle with the progress bar. It would be very difficult to 
			# understand what was happening. Do not believe this change is worth it.
			
			threadPool.append(SiteParserThread(self.options, dom, node))
		
		for thread in threadPool: 
			thread.start()
			thread.join()

		#print (dom.toxml())		
		#Backs up file
		backupFileName = self.xmlfile_path + "_bak"
		os.rename(self.xmlfile_path, backupFileName)
		f = open(self.xmlfile_path, 'w')
		outputStr = dom.toxml()
		outputStr = outputStr.encode('utf-8')
		f.write(outputStr) 
		
		# The file was succesfully saved and now remove backup
		os.remove(backupFileName)
