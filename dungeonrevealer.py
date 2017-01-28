#!/usr/bin/python3

import sys
from PIL import Image
from PIL import ImageTk as itk
import tkinter as tk
import numpy as np
#import cProfile as cp
def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.create_circle = _create_circle

#from profilehooks import profile
im_fg=None
im_bg=None
num_players=2
fu=None
zoomfac=1.2
class MaxCanvas(tk.Canvas):
    def __init__(self,master=None,images=None):
        tk.Canvas.__init__(self,master,height=100,width=100)
        self.pack(fill=tk.BOTH, expand=tk.YES)
        self.redrawPending=None
        self.images=images
        self.images_=self.images[:]
        self.__zoom=1
        self.cent=np.array([0.5,.5])
        self.dot=None
        self.dotPos=None
        self.pos0=np.zeros(2)
    def __real_redraw(self,event=None):
        old=self.find_all()
        self.update_idletasks()
        self.redrawPending=None
        self.win_size=win_size=np.array([self.winfo_width(),self.winfo_height()])
        mymin(win_size,100)
        for iid,image in enumerate(self.images):
            self.size=img_size=np.array([image.width,image.height])
            fac=win_size/img_size
            self.fac=fac=min(fac)*self.__zoom
            new_size=(img_size*fac).astype('int')
            image__=image.resize((new_size))
            self.images_[iid] = itk.PhotoImage(image__)
            [x0,y0]=((win_size-new_size)/2)
            #print(x0,y0)
            if x0<0:
                x0=x0*self.cent[0]*2
            if y0<0:
                y0=y0*self.cent[1]*2
            self.pos0=np.array([x0,y0]).astype('int')
            #print(self.pos0)
            [x0,y0]=self.pos0
            #print(self.cent/self.size,self.pos0)
            #print(x0,y0)
            #print(x0,y0,self.pos0,img_size,new_size)
            self.create_image(x0,y0,
                              image=self.images_[iid],anchor=tk.NW)
        if self.dotPos is not None:
            self.drawDot(self.dotPos)
        for i in old:
            self.delete(i)
    def drawDot(self,pos):
        self.dotPos=pos
        pos=(pos)*self.fac+self.pos0
        if self.dot:
            self.delete(self.dot)
        self.dot=self.create_circle(pos[0],pos[1],5,fill="#f00")
        
    def getRelative(self,pos):
        pos=np.array([pos.x,pos.y])
        rela=(pos-self.pos0)/self.fac
        return rela
        
    def redraw(self,event=None):
        if self.redrawPending is None:
            self.redrawPending=self.after_idle(self.__real_redraw)
    def zoom(self,fac):
        if fac<1 or self.__zoom < 2:
            self.__zoom*=fac
        self.redraw()

class Player(tk.Frame):
    def __init__(self,master=None,parent=None):
        tk.Frame.__init__(self,master)
        global im_fg,im_bg
        self.img=MaxCanvas(self,images=[im_bg,im_fg])
        self.master.title('Player Version')
        self.pack(fill=tk.BOTH, expand=tk.YES)
        self.bind_all('<Escape>',self.__exit)
        self.bind_all('<Configure>',self.__redraw)
        self.parent=parent
    def __redraw(self,event=None):
        self.parent.redraw()
        
    def redraw(self,event=None):
        self.img.redraw(event)
    def __exit(self,event):
        exit

class Application(tk.Frame):
    def __init__(self, master=None):
        self.master=master
        tk.Frame.__init__(self,master)
        global im_fg,im_bg
        self.im_fg=im_fg.convert('RGBA')
        self.alpha = np.array(self.im_fg.split()[-1])
        #print(self.alpha)
        self.im_fg.putalpha(Image.fromarray(self.alpha//2))
        self.img=MaxCanvas(self,images=[im_bg,self.im_fg])
        self.master.title('Dungeon Master')
        self.pack(fill=tk.BOTH,expand=tk.YES)
        self.save_queue=None
        self.xs=None
        self.cent=np.array([0.5,.5])
        self.bind_all('<Escape>',self.__exit)
        self.bind_all('<Configure>',self.redraw)
        self.bind_all('<Control-Button-1>',self.__drawDot)
        self.img.bind('<Motion>',self.__motion)
        self.img.bind('<Button-1>',self.__left)
        self.img.bind('<ButtonRelease-1>',self.__left)
        self.img.bind('<Button-3>',self.__right)
        self.img.bind('<ButtonRelease-3>',self.__right)
        self.img.bind('<Button-4>',self.__larger)
        self.img.bind('<Button-5>',self.__smaller)
        self.move=False
        self.player=self.newWindow=[]
        for i in range(num_players):
            self.newWindow=tk.Toplevel(self.master)
            self.player.append(Player(self.newWindow,parent=self))
        self.circ=None
        self.circSize=10
    def __drawDot(self,event):
        pos=self.img.getRelative(event)
        #print(self.player + [self])
        for i in self.player + [self]:
            i.img.drawDot(pos)
    def redraw(self,event=None):
        #print(self.player + [self])
        for i in self.player + [self]:
            i.img.redraw(event)
    def __exit(self,event):
        exit
    def __motion(self,event=None):
        if event.state == 276:
            self.__drawDot(event)
        #print(event.state)
        self.img.delete(self.circ)
        if event.state == 1040:
            self.circ=self.img.create_rectangle(self.xs,self.ys,event.x,event.y,outline="#f00")
        if event.state == 1044:
            evpos=np.array([event.x,event.y])
            self.cent-=np.array(evpos-self.start)/self.img.win_size
            self.cent=mylimit(0,self.cent,1)
            self.start=evpos
            for i in self.player+[self]:
                i.img.cent=self.cent
                i.img.redraw()
            #print(self.cent/self.img.size)
        else:
            self.circ=self.img.create_circle(event.x,event.y,self.circSize,outline="#f00")
    def __smaller(self,event):
        if event.state == 10:
            if self.circSize>5:
                self.circSize-=5
            self.__motion(event)
        elif event.state == 20:
            for i in [self]+self.player:
                i.img.zoom(1/zoomfac)
    def __larger(self,event):
        if event.state == 16:
            self.circSize+=5
            self.__motion(event)
        elif event.state == 20:
            for i in [self]+self.player:
                i.img.zoom(zoomfac)
    def __debug(self,event):
        print(event.num) # in __debug
    def __left(self,event):
        if event.state in [16,272]:
            #print("fuck!",event.state)
            fac=1/self.img.fac
            size=self.circSize*fac
            x0,y0=pos0=(np.array([event.x,event.y])-self.img.pos0)*fac
            #x0=(event.x-self.img.x0)*fac
            #y0=(event.y-self.img.y0)*fac
            ashape=self.alpha.shape
            #print(pos0)
            xs=max(int(x0-size),0)
            ys=max(int(y0-size),0)
            xe=min(int(x0+size+2),ashape[1])
            ye=min(int(y0+size+2),ashape[0])
            #print(xs,xe,ys,ye,x0,y0)
            for x in range(xs,xe):
                for y in range(ys,ye):
                    if (x-x0)**2+(y-y0)**2 < size**2:
                        self.alpha[y,x]=0
            if int(event.type) == 4:
                self.img.bind('<Motion>',self.__left)
            elif int(event.type) == 5:
                self.im_fg.putalpha(Image.fromarray(self.alpha//2))
                im_fg.putalpha(Image.fromarray(self.alpha))
                self.img.bind('<Motion>',self.__motion)
                self.redraw()
                if self.save_queue:
                    self.after_cancel(self.save_queue)
                self.save_queue=self.after(5000,self.__save)
    def __right(self,event):
        #print(event.state)
        if int(event.type) == 4:
            self.xs=event.x
            self.ys=event.y
            self.start=[event.x,event.y]
        if event.state%16 == 0:
            if int(event.type) == 5:
                fac=1/self.img.fac
                self.xs=int((self.xs-self.img.pos0[0])*fac)
                self.ys=int((self.ys-self.img.pos0[1])*fac)
                xe=int((event.x-self.img.pos0[0])*fac)
                ye=int((event.y-self.img.pos0[1])*fac)
                ashape=self.alpha.shape
                xs=max(min(xe,self.xs),0)
                ys=max(min(ye,self.ys),0)
                xe=min(max(xe,self.xs),ashape[1])
                ye=min(max(ye,self.ys),ashape[0])
                self.xs=None
                for x in range(xs,xe):
                    for y in range(ys,ye):
                        self.alpha[y,x]=0
                self.im_fg.putalpha(Image.fromarray(self.alpha//2))
                im_fg.putalpha(Image.fromarray(self.alpha))
                self.redraw()
                if self.save_queue:
                    self.after_cancel(self.save_queue)
                self.save_queue=self.after(5000,self.__save)
        elif event.state%16 == 4:
            if int(event.type) == 4:
                self.move=True
            else:
                self.move=False
        
    def __save(self,event=None):
        print("saving")
        #of=sys.argv[1][:-4]+".png"
        global outfile
        im_fg.save(outfile,"PNG")
            

def limit(lower,value,upper):
    return min(upper,max(lower,value))

def mymin(arr,lower):
    np.putmask(arr,arr<lower,lower)
    return arr

def mymax(arr,upper):
    np.putmask(arr,arr>upper,upper)
    return arr

def mylimit(lower,arr,upper):
    #arr=arr.copy()
    np.putmask(arr,arr<lower,lower)
    np.putmask(arr,arr>upper,upper)
    return arr

        
try:
    im_bg=Image.open(sys.argv[1])
except e:
    print("Usage:")
    print("\t%s <path-to-bg-image>"%sys.argv[0])
    sys.exit(1)
import os
outfile,ext=os.path.splitext(sys.argv[1])
outfile+="_Player.png"
try:
    im_fg=Image.open(outfile)
except:
    dat = np.array(im_bg.convert("RGB"))
    im_fg=Image.fromarray(dat*0)
def main():
    root=tk.Tk()
    app = Application(root)
    root.mainloop()

if __name__ == '__main__':
    main()
