"""Deterministic reel lettering and paytable source art; marquee is ImageGen artwork."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
P=Path(__file__).parent/'textures'
def font(s): return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',s)
def center(d,xy,t,size,fill): d.text(xy,t,font=font(size),fill=fill,anchor='mm')
im=Image.new('RGB',(512,2048),(244,233,202)); d=ImageDraw.Draw(im)
for i,t in enumerate(['7','BAR','CHERRY','BELL','7','LEMON','BAR','STAR']):
    y=i*256
    d.rectangle((14,y+10,497,y+245),outline=(166,128,61),width=3)
    if t=='7': center(d,(256,y+134),'7',218,(183,27,27))
    elif t=='BAR':
        d.rounded_rectangle((65,y+60,447,y+195),radius=15,fill=(23,43,40))
        center(d,(256,y+128),'BAR',96,(250,239,207))
    elif t=='CHERRY':
        d.line([(201,y+134),(260,y+43),(316,y+140)],fill=(34,91,52),width=12)
        d.ellipse((143,y+117,247,y+221),fill=(176,25,28));d.ellipse((271,y+117,375,y+221),fill=(195,30,31))
        d.ellipse((164,y+131,183,y+150),fill=(255,176,133));d.ellipse((291,y+131,310,y+150),fill=(255,176,133))
    elif t=='BELL':
        d.ellipse((176,y+43,337,y+205),fill=(199,145,37)); d.polygon([(195,y+99),(157,y+192),(356,y+192),(317,y+99)],fill=(219,165,46));d.rectangle((144,y+191,368,y+209),fill=(97,71,27));d.ellipse((235,y+208,277,y+234),fill=(165,103,22))
    elif t=='LEMON': d.ellipse((133,y+65,380,y+198),fill=(224,184,30),outline=(96,111,31),width=6)
    else:
        import math
        pts=[(256+ (99 if j%2==0 else 44)*math.sin(j*math.pi/5),y+128-(99 if j%2==0 else 44)*math.cos(j*math.pi/5)) for j in range(10)]
        d.polygon(pts,fill=(193,128,28))
# UV v=0 is the bottom of the image: first symbol at bottom.
im=im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
# Flip individual tiles back so each symbol stays upright in UV coordinates.
for i in range(8):
    tile=im.crop((0,i*256,512,(i+1)*256)).transpose(Image.Transpose.FLIP_TOP_BOTTOM); im.paste(tile,(0,i*256))
im.save(P/'Reel_Source.png')
im=Image.new('RGB',(1536,640),(239,226,189));d=ImageDraw.Draw(im)
d.rounded_rectangle((20,20,1516,620),radius=22,outline=(151,102,36),width=8)
center(d,(768,101),'JACKPOT  •  777',114,(170,32,29))
for x,a,b in [(285,'7  7  7','PAYS  100'),(768,'BAR  BAR  BAR','PAYS  20'),(1250,'CHERRIES','PAYS  10')]:
    center(d,(x,272),a,59,(24,69,60));center(d,(x,367),b,54,(126,85,35))
d.line((86,463,1450,463),fill=(151,102,36),width=3)
center(d,(768,543),'INSERT 25¢   •   PULL HANDLE   •   GOOD LUCK',45,(24,69,60))
im.save(P/'Paytable_Source.png')
im=Image.new('RGB',(1024,256),(17,57,51));d=ImageDraw.Draw(im)
center(d,(512,132),'WINNER  •  JACKPOT',83,(255,219,119));im.save(P/'Winner_Source.png')
