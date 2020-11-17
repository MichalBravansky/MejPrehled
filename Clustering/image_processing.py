from io import BytesIO
from PIL import Image
import requests
from PIL import ImageFont
from PIL import ImageDraw 


def get_image(url,text, background_type, size=15):
    
    #downloads the image
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))

    #selects the font
    font = ImageFont.truetype("DIN Condensed Bold.ttf", int(img.size[1]/size))
    w, h = img.size

    #crops the image to be a perfect square
    img=img.crop(((w-h)/2, 0, h+(w-h)/2, h))

    w, h = img.size
    background_img=None

    #picks a frame based on a category
    if background_type==0:
        background_img=Image.open('Žlutá-1.png')
    elif background_type==1:
        background_img=Image.open('modrá-1.png')
    elif background_type==2:
        background_img=Image.open('Oranžová-1.png')

    #applies the background
    background_img=background_img.resize((w,w), Image.ANTIALIAS)

    img.paste(background_img, (0,0), mask=background_img)

    draw = ImageDraw.Draw(img)

    headLine=text
    splitted=headLine.split()

    #splits lines so they fit the frame
    lastLength=0
    writing=""
    lastYPos=0
    allLines=[]
    heightSizes=[]
    for item in splitted:
        writing+=item
        if(font.getsize(writing)[0]<=img.size[0]*1/2):
            lastLength=len(writing)
            writing+=" "
        else:
            allLines.append(writing[:lastLength])
            heightSizes.append(lastYPos)
            lastYPos+=font.getsize("y")[1]+2
            lastLength=0
            writing=item+" "


    allLines.append(writing)
    heightSizes.append(lastYPos)

    #if the lines are too big, changes the font size
    if size==15 and len(allLines)>3:
        return get_image(url,text, background_type, 20)

    text_high=0

    for text in allLines:
        text_high+=font.getsize(text)[1]

    #constants so the text fits the frame perfectly
    startY=int(0.68*h+((0.92-0.68)*h-text_high)/2)

    #draws the title
    numberOfRounds=0
    for item in allLines:
        draw.text((int(img.size[0]*1/20), int(startY+heightSizes[numberOfRounds])),item,(255,255,255),font=font)
        numberOfRounds+=1


    return img