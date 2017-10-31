
#-----Statement of Authorship----------------------------------------#
#
#  This is an individual assessment item.  By submitting this
#  code I agree that it represents my own work.  I am aware of
#  the University rule that a student must not act in a manner
#  which constitutes academic dishonesty as stated and explained
#  in QUT's Manual of Policies and Procedures, Section C/5.3
#  "Academic Integrity" and Section E/2.1 "Student Code of Conduct".
#
#    Student no: n10089675
#    Student name: Jordan Fischer
#
#  NB: Files submitted without a completed copy of this statement
#  will not be marked.  Submitted files will be subjected to
#  software plagiarism analysis using the MoSS system
#  (http://theory.stanford.edu/~aiken/moss/).
#
#--------------------------------------------------------------------#



#-----Task Description-----------------------------------------------#
#
#  News Archivist
#
#  In this task you will combine your knowledge of HTMl/XML mark-up
#  languages with your skills in Python scripting, pattern matching
#  and Graphical User Interface development to produce a useful
#  application for maintaining and displaying archived news or
#  current affairs stories on a topic of your own choice.  See the
#  instruction sheet accompanying this file for full details.
#
#--------------------------------------------------------------------#



#-----Imported Functions---------------------------------------------#
#
# Below are various import statements that were used in our sample
# solution.  You should be able to complete this assignment using
# these functions only.

# Import the function for opening a web document given its URL.
from urllib.request import urlopen

# Import the function for finding all occurrences of a pattern
# defined via a regular expression, as well as the "multiline"
# and "dotall" flags.
from re import findall, MULTILINE, DOTALL

# A function for opening an HTML document in your operating
# system's default web browser. We have called the function
# "webopen" so that it isn't confused with the "open" function
# for writing/reading local text files.
from webbrowser import open as webopen

# An operating system-specific function for getting the current
# working directory/folder.  Use this function to create the
# full path name to your HTML document.
from os import getcwd

# An operating system-specific function for 'normalising' a
# path to a file to the path-naming conventions used on this
# computer.  Apply this function to the full name of your
# HTML document so that your program will work on any
# operating system.
from os.path import normpath, isfile
    
# Import the standard Tkinter GUI functions.
from tkinter import *

# Import the SQLite functions.
from sqlite3 import *

# Import the date and time function.
from datetime import datetime

#import module to dynamically search directories
from glob import glob

#
#--------------------------------------------------------------------#



#-----Student's Solution---------------------------------------------#
#
# Put your solution at the end of this file.
#

# Name of the folder containing your archived web documents.  When
# you submit your solution you must include the web archive along with
# this Python program. The archive must contain one week's worth of
# downloaded HTML/XML documents. It must NOT include any other files,
# especially image files.
internet_archive = 'internetArchive'


################ PUT YOUR SOLUTION HERE #################

if __name__ == "__main__":
	eventLogging = False

	#create the function to toggle eventlogging
	def eventLoggingToggle(failure = False):
		#toggle the value of the eventLogging variable from true to false
		#and vice versa
		global eventLogging
		eventLogging = not eventLogging

		#check if a failure has been forced
		if failure == True:
			eventLogging = False

		#modify button colours and text based on current event logging status
		if eventLogging == True:
			status = "ENABLED"
			root.btnToggle['background'] = "#0BD900"
			root.btnToggle['activebackground'] = "#09BA00"
		else:
			status = "DISABLED"
			root.btnToggle['background'] = "#FF0000"
			root.btnToggle['activebackground'] = "#BD0000"
		
		#notify user of failure 
		if failure == True:
			#notify user and remove command for enabling toggle service
			root.btnToggle['text'] = "Catastrophic error encountered, logging disabled"
			root.btnToggle['command'] = ""
			return
		root.btnToggle['text'] = "EVENT LOGGING " + status
		logEvent("Event Logging has been " + status, forced = True)

	#create the function to log events
	def logEvent(event, forced = False):
		#do nothing if eventlogging is disabled
		if eventLogging == True or forced == True:
			#give a graceful error if database error occurrs 
			try:
				conn = connect(normpath(getcwd() + "/event_log.db"))
				c = conn.cursor()
				#execute a query to insert the logged event into the database
				param = (event,)
				c.execute("INSERT INTO Event_log VALUES (NULL, ?)", param)
				conn.commit()
				conn.close()
			except:
				#create a graceful error message
				root.objLogoStatusText.set("Event Logging database could not be found!")
				eventLoggingToggle(failure = True)

	#create global dictionary
	stories = {}

	def handle_extract():
		#get the selected archive from the listbox 
		selection = root.objArchiveVar.get()
		#display error if user tries to extract without selecting archive
		if selection == "Please Select A Date":
			root.objLogoStatusText.set("You must select an archive date!")
			return False

		#fetch the file path for the archive file from the list of archives
		if selection == "Latest":
			path = archives[len(archives) - 1]['path']
		else:
			for archive in archives:
				if archive['date'] == selection:
					path = archive['path']
		
		#open the archive file based on the selected archive date
		archive = open(path, 'r', encoding = "UTF-8")
		archive_content = archive.read()
		archive.close()

		#call function to handle the extraction of news stories from the archived file
		extract_data(archive_content)
		root.objLogoStatusText.set("Successfully extracted archive from: " + selection)
		logEvent("Archive has been successfully extracted!")

	def handle_display():
		#generate operating system specific file path
		path = normpath(getcwd() + '/extracted.html')
		#check if the file actually exists
		if(isfile(path)):
			#open the file in the default web browser
			webopen(normpath("file://" + path))
			root.objLogoStatusText.set("Opening extracted news archive in your browser")
			logEvent("News has been opened in web browser!")
		else:
			root.objLogoStatusText.set("You must extract the data before viewing it!")

	def handle_latest():
		#fetch the RSS feed data for the news stories
		url = "http://feeds.skynews.com/feeds/rss/politics.xml"
		document = urlopen(url)
		contents = document.read().decode("UTF-8")

		#fetch the current date and time and format it nicely
		todays_date = datetime.now()
		formatted_date = todays_date.strftime('%d, %b %Y')

		#create the full path for the file to be created
		path = normpath(getcwd() + '/' + internet_archive + '/' + formatted_date + '.xhtml')

		#fetch current latest(before new insertion)
		if len(archives) != 0:
			oldLatest = archives[len(archives) - 1]['date']
		else:
			oldLatest = None

		#ensure no duplicates created
		if oldLatest != formatted_date:
			#create the file and insert the scraped data
			extracted_file = open(path, 'w', encoding = "UTF-8")
			extracted_file.write(contents)
			extracted_file.close()
			#notify the user of the successful operation
			root.objLogoStatusText.set("Archive Updated")
			
			#add updated archive to list as "Latest"
			root.objArchive["menu"].delete(END)
			if oldLatest is not None:
				insertItem(oldLatest)
			insertItem("Latest")

			#add new archive to list of archives
			archive = {
				"date": formatted_date,
				"path": path
			}
			archives.append(archive)

			#log the event of updating the database
			logEvent("Archive has been updated!")
		else:
			root.objLogoStatusText.set("The archive already includes todays news!")

	def extract_data(data):
		#find data for each news story
		day = findall("<lastBuildDate>(.+)</lastBuildDate>", data, MULTILINE)[0]
		stories = findall("<item>(?s:.)+?</item>", data, MULTILINE)

		#create an empty list and iterate through each news story
		news_stories = []
		for storyN in range(10):
			story = stories[storyN]

			#extract individual details about the news story
			title = findall("<title>(.+)</title>", story, MULTILINE)[0]
			title = str(storyN + 1) + ". " + title
			description = findall("<description>(.+)</description>", story, MULTILINE)[0]
			publication_date = findall("<pubDate>(.+)</pubDate>", story, MULTILINE)[0]
			full_story = findall("<link>(.+)</link>", story, MULTILINE)[0]
			image = findall('<enclosure url="(.+)?" length="', story, MULTILINE)[0]
			image = image.replace("70x70", "1096x616")

			#arrange extracted information into a dictionary and append it to a list
			news_story = {
				"title": title,
				"description": description,
				"publication_date": publication_date,
				"full_story": full_story,
				"image": image
			}
			news_stories.append(news_story)

			#create an elegant HTML page to view the extracted data
			create_viewable(news_stories, day)

	def create_viewable(news_stories, day):
		#create the variable which contains the html styling
		html_template = """
			<!DOCTYPE html>
			<html lang = "en">
				<head>
					<!-- Title for browser window / character encoding -->
					<title>News Archives</title>
					<meta charset = "UTF-8">
				</head>
				<body>
					<!-- Inline styles used for the basic layout of the page -->
					<style type="text/css">
						body {
							margin:0;
							font-family:arial;
							background:#454545;
						}
						section {
							width: 80%;
							background:#35B7E8;
							margin:0 auto;
							min-width:500px;
							max-width:1000px;
							padding:10px;
							box-shadow:0px 0px 10px rgba(0, 0, 0, 0.5);
							color:#eee;
							text-align:center;
							margin-bottom:15px;
						}
						section.header {
							border-bottom-left-radius:5px;
							border-bottom-right-radius:5px;
						}
						div.flex {
							display: flex;
							margin:10px 0px 0px 0px;
							justify-content: space-between;
							font-family: 'Trebuchet MS', sans-serif;
							flex-wrap:wrap;
						}
						div.flex a, p a {
							color:#ffffff;
						}
						span.bold {font-weight:bold;}
						section p {text-align:left;}
					</style>
					<!-- Header section detailing information about the archiver -->
					<section class="header">
						<h1>Sky News - Political Archives - US</h1>
						<h3>Latest 10 Political news stories from ***day***</h3>
						<h4>Date inconsistancies created by differing timezones</h4>
						<img width = "50%" src = "https://i.imgur.com/u0QPsnB.gif" />
						<div class="flex">
							<div><span class="bold">News Source:</span> <a href="http://feeds.skynews.com/feeds/rss/politics.xml">http://feeds.skynews.com/feeds/rss/politics.xml</a></div>
							<div><span class="bold">Archivist:</span> Jordan Fischer</div>
						</div>
					</section>
					<!-- Individual news stories displayed below -->
					***NEWS_STORIES***

					<!-- End news stories -->
				</body>
			</html>
		"""

		#create the variable which contains the template for individual news stories
		news_story_template = """
					<section>
						<h1>***TITLE***</h1>
						<img src = "***IMAGE***" title="Sorry this image could not be loaded" width = "100%" />
						<p>
							***DESCRIPTION***
						</p>
						<p>
							<span class="bold">Full story:</span> <a href="***FULL_STORY***">***FULL_STORY***</a> <br /><br />
							<span class="bold">Date published:</span> ***PUBLICATION_DATE***
						</p>
					</section>
		"""

		#create empty list of news stories and iterate current list of stories
		elegant_stories = ""
		for story in news_stories:
			elegant_story = news_story_template #bind template to current story
			#fetch the keys and values of the news stories dictionary
			for key, value in story.items():
				#replace the placeholder sections of the template based on the dictionary keys.
				elegant_story = elegant_story.replace("***" + key.upper() + "***", value)
			
			#append current story to the list
			elegant_stories = elegant_stories + elegant_story

		#Append list of stories to the html template
		elegant_page = html_template.replace("***NEWS_STORIES***", elegant_stories)
		elegant_page = elegant_page.replace("***day***", day)

		#create the elegant html page
		elegant_page_file = open(normpath(getcwd() + '/extracted.html'), 'w', encoding = "UTF-8")
		elegant_page_file.write(elegant_page)
		elegant_page_file.close()

	# Okay, let's launch our Tkinter GUI
	root = Tk()
	root.title("Sky News Archiver")
	root.configure(background = "#00A7FA")
	frame = Frame(root)
	
	# Logo
	root.objLogoBin = PhotoImage(file = normpath(getcwd() + "/skylogo.gif"))
	root.objLogoBin.zoom(20)
	root.objLogo = Label(frame, image = root.objLogoBin, width = 300, borderwidth = 0)
	
	# create welcome message
	root.objLogoStatusText = StringVar()
	root.objLogoStatusText.set("View archived political news stories from Sky News")
	
	root.objLogoStatus = Label(
		textvar = root.objLogoStatusText,
		font = ("Calibri", 12),
		background = "#00A7FA",
		foreground = "white"
	)
	
	# Display our dropdown of archived items
	root.objArchiveVar = StringVar(root)
	root.objArchiveVar.set("Please Select A Date")
	
	root.objArchive = OptionMenu(root, root.objArchiveVar, None)
	root.objArchive.config(
		background = "#00A7FA",
		foreground = "white",
		borderwidth = 0,
		activebackground = "#00A7EA",
		activeforeground = "white",
		font = ("Calibri", 12)
	)
	root.objArchive["menu"].delete(END)

	#create function to be called when new archive is selected
	def updateSelected(tag):
		#log the event of the archive being selected
		logEvent("Archive " + tag + " has been selected")
		#update the text of the archive list
		root.objArchiveVar.set(tag)

	#create function to insert items into the archive list menu
	def insertItem(tag):
		root.objArchive["menu"].add_command(
			label = tag,
			command = lambda v = tag: updateSelected(tag)
		)
	
	# Populate our dropdown of archived items


	archives = []
	
	#scan the archive directory and insert each archive date into a list
	for archive in glob(normpath(getcwd() + '/' + internet_archive + '/*.xhtml')):
		#extract date information from filepath
		#if on windows, escape using backslash instead of forward slash
		date = archive.split('/') if archive.find('/') != -1 else archive.split("\\")
			
		#add archive data to a dictionary list
		archive = {
			#extract date information by splitting the name from the file extension
			"date": date[len(date) - 1].split('.')[0],
			"path": archive
		}
		#create global list of archives
		archives.append(archive)
		insertItem(archive['date'])

	root.objArchive["menu"].delete(END)
	insertItem("Latest")

	#create GUI buttons
	#styling options added for windows / default styles maintained for mac (default looks fine on mac not so much for windows)
	# Download Archive Button
	root.btnDownload = Button(
		state = "normal",
		text = "ARCHIVE LATEST NEWS",
		background = "#00A7FA",
		activebackground = "#00A7EA",
		highlightbackground = "white",
		foreground = "white",
		activeforeground = "white",
		height = 2,
		borderwidth = 0,
		font = ("Calibri", 12),
		command = handle_latest
	)
	
	# Extract Archive Button
	#  Extracts the currently selected archive to .html file
	root.btnExtract = Button(
		state = "normal",
		text = "EXTRACT SELECTION",
		background = "#00A7FA",
		activebackground = "#00A7EA",
		highlightbackground = "white",
		foreground = "white",
		activeforeground = "white",
		height = 2,
		borderwidth = 0,
		font = ("Calibri", 12),
		command = handle_extract
	)
	
	# Display Article Button
	#  Opens in Web Browser
	root.btnOpen = Button(
		state = "normal",
		text = "OPEN SELECTION",
		background = "#00A7FA",
		activebackground = "#00A7EA",
		highlightbackground = "white",
		foreground = "white",
		activeforeground = "white",
		height = 2,
		borderwidth = 0,
		font = ("Calibri", 12),
		command = handle_display
	)

	#create eventlogging togglable button
	root.btnToggle = Button(
		state = "normal",
		text = "EVENT LOGGING DISABLED",
		background = "#FF0000",
		activebackground = "#BD0000",
		highlightbackground = "white",
		foreground = "white",
		activeforeground = "white",
		height = 2,
		borderwidth = 0,
		font = ("Calibri", 12),
		command = eventLoggingToggle
	)

	#align the GUI elements using the grid manager
	frame.grid(row = 0, column = 0, columnspan = 3)
	root.objLogo.grid(row = 0, column = 0, columnspan = 3)
	root.objLogoStatus.grid(row = 1, column = 0, columnspan = 3, sticky = "NESW")
	root.objArchive.grid(row = 2, column = 0, columnspan = 3, sticky = "NESW")
	root.btnDownload.grid(row = 3, column = 0, sticky = "NESW")
	root.btnExtract.grid(row = 3, column = 1, sticky = "NESW")
	root.btnOpen.grid(row = 3, column = 2, sticky = "NESW")
	root.btnToggle.grid(row = 4, column = 0, columnspan = 3, sticky = "NESW")
	
	#don't allow window to be resized
	root.resizable(width=False, height=False)
	# Start Tkinter Event Loop
	root.mainloop()