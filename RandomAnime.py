import random
import xml.etree.ElementTree as ET
import requests
import webbrowser
from tkinter import *
from tkinter import messagebox

def randomint(min,max): return random.randint(min,max)

def grabFromFile(filename):
  try:
    tree = ET.parse(filename)
  except:
    messagebox.showerror("Error!","Last anime list doesn't exist!")
    return
  titleArray=[]
  urls=[] 
  root = tree.getroot()
  for anime in root.findall('anime'):
      title = anime.find('series_title').text
      url = anime.find('my_url').text
      titleArray.append(title)
      urls.append(url)
  rand = randomint(0,len(titleArray)-1)
  msgBox = messagebox.askquestion('Result','Your next anime is: ' + titleArray[rand] + ". Would you like to open anime's site?")
  if(msgBox) == 'yes': webbrowser.open(urls[rand])
      
def queryReqAL(name):
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
    variables = {
    'username': name,
    }
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': variables})
    data_json = response.json()
    root = ET.Element("myanimelist")
    try:
      for anime in data_json["data"]["MediaListCollection"]["lists"][0]["entries"]:
        newAnime = ET.SubElement(root,"anime")
        ET.SubElement(newAnime,"series_title").text = str(anime["media"]["title"]["romaji"])
        ET.SubElement(newAnime,"my_url").text = str(anime["media"]["siteUrl"])
    except:
      messagebox.showerror("Error!","No user found! Check spelling!")
      return
    save = ET.ElementTree(root)
    save.write("listAL.xml")
    grabFromFile("listAL.xml")
  if not name: messagebox.showerror("Name not given!","Input field is empty!")

def queryReqMAL(name):
  if name:
    try:
      url = 'https://myanimelist.net/animelist/{}/load.json?status=7&offset=0'.format(name)
      response = requests.get(url)
      data_json = response.json()
      url = 'https://myanimelist.net/animelist/{}/load.json?status=7&offset=300'.format(name)
      response = requests.get(url)
      data_json = data_json + response.json()
      url = 'https://myanimelist.net/animelist/{}/load.json?status=7&offset=600'.format(name)
      response = requests.get(url)
      data_json = data_json + response.json()
    except:
      messagebox.showerror("Error!","No user found! Check spelling!")
      return
    root = ET.Element("myanimelist")
    for anime in data_json:
      if int(anime["status"])==6:
        newAnime = ET.SubElement(root,"anime")
        ET.SubElement(newAnime,"series_title").text=str(anime["anime_title"])
        temp = str(anime["anime_id"])
        ET.SubElement(newAnime,"my_url").text = "https://myanimelist.net/anime/" + temp
    save = ET.ElementTree(root)
    save.write("listMAL.xml")
    grabFromFile("listMAL.xml")
  if not name: messagebox.showerror("Name not given!","Input field is empty!")
  
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

if __name__=="__main__":
  main()