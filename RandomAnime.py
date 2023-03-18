#Imports that are all required for script to work. Random picks random integer. Element Tree handles json responses and makes XML work easy. Requests and webbrowser to communicate with server.
import random
import xml.etree.ElementTree as ET
import requests
import webbrowser
from tkinter import *
from tkinter import messagebox

#Random library to choose random title
def randomint(min,max): return random.randint(min,max)

#Whole method to parse previously downloaded animes from selected site, argument is name of the xml file
def grabFromFile(filename):
  #If file exists, parse it into Element Tree, otherwise inform User and let him try again
  try:
    tree = ET.parse(filename)
  except:
    messagebox.showerror("Error!","Last anime list doesn't exist!")
    return
  #Empty lists for titles and their urls on the sites
  titleArray=[]
  urls=[] 
  #Root for Element Tree
  root = tree.getroot()
  #Titles and urls are added to their lists in the same time so they have same position in both lists
  for anime in root.findall('anime'):
      titleArray.append(anime.find('series_title').text)
      urls.append(anime.find('my_url').text)
  #Random title and it's url are choosen and put on the screen for the User
  rand = randomint(0,len(titleArray)-1)
  msgBox = messagebox.askquestion('Result','Your next anime is: ' + titleArray[rand] + ". Would you like to open anime's site?")
  if(msgBox) == 'yes': webbrowser.open(urls[rand])

#Request to AniList api      
def queryReqAL(name):
  #Query needed for AniList api that gets necessary info to be later link: https://anilist.gitbook.io/anilist-apiv2-docs/overview/graphql/getting-started
  if name:
    query = """
     query ($username: String) {
      MediaListCollection(userName: $username, type: ANIME, status: PLANNING) {
        lists {
          entries {
            media {
              title { romaji }
              siteUrl
              }
            }
          }
        }
      }   
    """
    #Lib containing single name of the user (if was given, otherwise this section won't be executed)
    variables = {
    'username': name,
    }
    #Sends post to the server and gets json back then uses Element Tree to handle response
    response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables})
    data_json = response.json()
    root = ET.Element("myanimelist")
    #If json was fine script is searching for animes in json and puts names with urls inside Element Tree. If json is empty shows error message that user doesn't exist in the base
    try:
      for anime in data_json["data"]["MediaListCollection"]["lists"][0]["entries"]:
        newAnime = ET.SubElement(root,"anime")
        ET.SubElement(newAnime,"series_title").text = str(anime["media"]["title"]["romaji"])
        ET.SubElement(newAnime,"my_url").text = str(anime["media"]["siteUrl"])
    except:
      messagebox.showerror("Error!","No user found! Check spelling!")
      return
    #Saves Element Tree to the file and executes method to pick random anime
    save = ET.ElementTree(root)
    save.write("listAL.xml")
    grabFromFile("listAL.xml")
  if not name: messagebox.showerror("Name not given!","Input field is empty!")

#Request to MAL "api"
def queryReqMAL(name):
  if name:
    #Tries getting response from MAL site (it's json response). If not shows error that user isn't in MAL's base
    url = 'https://myanimelist.net/animelist/{}/load.json?status=7&offset=0'.format(name)
    response = requests.get(url)
    if response.text == '{"errors":[{"message":"invalid request"}]}':
      messagebox.showerror("Error!","No user found! Check spelling!")
      return
    data_json = response.json()
    #If first try went smooth offset increments to the high point where it's nearly impossible for users to have such big lists. When response returns error or hits max offset loop breaks.
    offset = 300
    while True:
      url = 'https://myanimelist.net/animelist/{}/load.json?status=7&offset={}'.format(name,offset)
      response = requests.get(url)
      if len(response.text) < 4: break
      data_json += response.json()
      offset += 300
    #Response is handled by Element Tree where it finds Plan to Watch animes and puts their title with urls in the tree
    root = ET.Element("myanimelist")
    for anime in data_json:
      if int(anime["status"])==6:
        newAnime = ET.SubElement(root,"anime")
        ET.SubElement(newAnime,"series_title").text=str(anime["anime_title"])
        temp = str(anime["anime_id"])
        ET.SubElement(newAnime,"my_url").text = "https://myanimelist.net/anime/" + temp
    #Element Tree is saved to the file and method to pick anime is executed
    save = ET.ElementTree(root)
    save.write("listMAL.xml")
    grabFromFile("listMAL.xml")
  if not name: messagebox.showerror("Name not given!","Input field is empty!")

#Tkinter window to communicate with user (yes everyone loves clickable interfaces). It has fixed window size.
def main():
  win = Tk()
  win.title("Random Anime Generator")
  win.geometry("600x400+660+340")
  win.resizable(False,False)
  mainTitle = Label(win,text="Input your MAL/AL nickname below!",font=40,width=40)
  mainTitle.pack(pady=25)
  userEntry = Entry(win,width=40)
  userEntry.pack(pady=10)
  buttonMAL = Button(win,text="Load MAL List",width=15,command=lambda:{queryReqMAL(userEntry.get()),userEntry.delete(0,"end")})
  buttonMAL.place(x=180,y=120)
  buttonAL = Button(win,text="Load AL List",width=15,command=lambda:{queryReqAL(userEntry.get()),userEntry.delete(0,"end")})
  buttonAL.place(x=305,y=120)
  buttonListMAL = Button(win,text="Load Last MAL List",width=15,command=lambda:grabFromFile("listMAL.xml"))
  buttonListMAL.place(x=180,y=150)
  buttonListAL = Button(win,text="Load Last AL List",width=15,command=lambda:grabFromFile("listAL.xml"))
  buttonListAL.place(x=305,y=150)
  warning = Label(win,text="DISCLAMER: Scrapping MAL list for the first time takes long time due to site's old API!",fg="red")
  warning.pack(pady=125)
  win.mainloop()

#No explanation needed
if __name__=="__main__":
  main()