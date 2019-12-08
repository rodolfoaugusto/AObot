import sys
if sys.argv[1] is not 'read':
  import cv2 as cv
  import numpy as np
  import logging
  import win32gui, win32ui, win32con, win32api, win32clipboard, win32com.client
  import pyautogui
  import time
  import pytesseract
  import pickle
  import matplotlib.pyplot as plt
  import re
  import scapy
  import os
elif sys.argv[1]=='read':
  import pickle
  import logging

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=logging.DEBUG)

try:
  pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'
except NameError as e:
  logging.WARNING(e)
  pass


items = []
tier = 3
quality = 3
data = []
itemtype = 'staff'
repeat = 25
money = []
level = 4

def getClientWindow():
    # returns ((position),(size))
    hwnd = win32gui.FindWindow(None, "Albion Online Client")
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    return ((x,y),(w,h))

def grab_screen(hwin,region=None):
    rect = win32gui.GetWindowRect(hwin)
    x = rect[0]
    y = rect[1]
    width = rect[2] - x - 5
    height = rect[3] - y - 30
    left = 3
    top = 25
    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)
    
    signedIntsArray = bmp.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (height,width,4)
    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())
    img = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    return img,(x,y)

def read_BMoffers(img):
    img = img[275:335,430:800]
    img[:,200:248] = 255
    img[img>180] = 255
    #cv.imshow('e',img)
    #cv.waitKey(0)
    text = pytesseract.image_to_string(img)
    logging.debug(f'read BM text: {text}')
    _list = text.split(' ')
    price = _list.pop()
    logging.debug(f'is it correct price?: {matchPrice(price)}')
    assert matchPrice(price)
    price = price.replace(',','')
    assert price.isdigit()
    #_list.pop(0)
    _list = ['Grandmaster\'s' if re.match('^.*randmaste.*$',x) is not None else x for x in _list]
    _list = ['Master\'s' if re.match('^.*ast.r.*$',x) is not None else x for x in _list]
    _list = ['Adept\'s' if x in ['Adepes','Adept’','Adept’s','Adepe’s','Adept','Adepts', 'Adeprs','Adepr’s','depes','depts'] else x for x in _list]
    _list = ['Expert\'s' if x in ['Experts','Expert’','Expert’s','Expere’s','Expert','Ecpert', 'Experrs'] else x for x in _list]
    _list = ['Quarterstaff' if x in ['Quarterstaft','Quarterstaf','Quarterstatt'] else x for x in _list]
    _list = ['Staff' if x in ['Stat','Statt','staff','statt','stat','Scatt','Scaft','Staft','staf','Staf','start','Scat','scat','Saft','staft','statf','Statf','Start','Seatt','seatf'] else x for x in _list]
    if not _list:
        return None
    
    itemname = ' '.join([c for c in _list])
    return (itemname,int(price))

def read_AHoffers(img):
    img = img[275:325,430:800]
    img[:,170:287] = 255
    img[img>180] = 255
    #cv.imshow('e',img)
    #cv.waitKey(0)
    text = pytesseract.image_to_string(img)
    _list = text.split(' ')
    price = _list.pop()
    if not _list:
        return None
    if len(_list)>1:
        _list.pop(0)
    #if len(_list)>1 and 'Balance' not in _list:
    #    _list.pop()
    itemname = ' '.join([c for c in _list])
    assert matchPrice(price)
    price = price.replace(',','')
    assert price.isdigit()
    return (itemname,int(price))

def read_title(img):
    img = img[133:165,421:650]
    img[(img>125) & (img < 255)]=0
    img[(img<125) & (img > 0)]=255
    #cv.imshow('img',img)
    #cv.waitKey(0)
    return pytesseract.image_to_string(img)

def read_money(img):
    img = img[133:165,780:920]
    img[(img>140)]=255
    img[(img>115) & (img < 255)]=0
    img[(img<115) & (img > 0)]=255
    #cv.imshow('img',img)
    #cv.waitKey(0)
    return pytesseract.image_to_string(img,config="-c tessedit_char_whitelist=0123456789mk.")

def focus_action(hwin,active,func,*args):
    win32gui.SetForegroundWindow(hwin)
    func(*args)
    win32gui.SetForegroundWindow(active)

def BM(hwin,active,repeat):
    global tier, itemtype, money, level
    img,pos = grab_screen(hwin)
    sell(pos)
    money.append(read_money(img))
    if tier < 3:
        changeTier(pos,tier+1)
    else:
        changeTier(pos,0)
        if quality < 2:
            changeQuality(pos,quality+1)
        else:
            changeQuality(pos,0)
            if level == 4:
                changeLevel(pos,3)
            else:
                changeLevel(pos,level+1)

    focus_action(hwin,active,typeInSearch,itemtype,pos)
    time.sleep(0.2)
    full={}
    if 'Black' in read_title(img):
        for _ in range(repeat):
            img,pos = grab_screen(hwin)
            try:
                res = read_BMoffers(img)
                focus_action(hwin,active,dragup,pos)
            except AssertionError:
                logging.debug('Assertion error (cant process item text)')
                focus_action(hwin,active,dragup,pos)
                continue
            try:
                if res[0] not in full:
                    full[res[0]]=res[1]
            except TypeError as e:
                logging.debug(e)
                continue
    else:
        try:
            if sys.argv[2]=='shutdown':
                os.system("shutdown /s /t 1")
        except:
            pass
        raise RuntimeError('Not in BM')
    
    return full

def AH(hwin,active,BMfull):
    global data
    img,pos = grab_screen(hwin)
    if 'Marketplace' in read_title(img):
        for itemname in BMfull:
            focus_action(hwin,active,typeInSearch,itemname,pos)
            time.sleep(0.4)
            img,pos = grab_screen(hwin)
            try:
                res = read_AHoffers(img)
                val = (BMfull[itemname]-res[1])/res[1]
                shouldbuy = val>0.1
                if shouldbuy:
                    logging.info(f'BUYING {itemname}')
                    logging.info(f'BM: {BMfull[itemname]}, AH: {res[1]}')
                    buy(pos,itemname)
                    data.append((time.process_time(),BMfull[itemname]-res[1]))
            except Exception as e:
                logging.info(e)
                continue
    else:
        try:
            if sys.argv[2]=='shutdown':
                os.system("shutdown /s /t 1")
        except:
            pass
        raise RuntimeError('Not in AH')
    
            

def dragup(pos):
    pyautogui.moveTo(pos[0]+600,pos[1]+365)
    pyautogui.dragTo(pos[0]+600,pos[1]+322,0.2)
    time.sleep(0.1)

def typeInSearch(query,pos):
    pyautogui.moveTo(pos[0]+462,pos[1]+211)  # click reset
    pyautogui.mouseDown()
    time.sleep(0.08)
    pyautogui.mouseUp()
    time.sleep(1.2)
    pyautogui.moveTo(pos[0]+412,pos[1]+211)  # click searchbar
    pyautogui.mouseDown()
    time.sleep(0.08)
    pyautogui.mouseUp()
    #pyautogui.typewrite(query, interval=0.15)
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT,query)
    win32clipboard.CloseClipboard()
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.15)

def sell(pos):
    global items
    if items:
        pyautogui.click(pos[0]+944,pos[1]+313)
        pyautogui.click(pos[0]+944,pos[1]+313)
        time.sleep(0.1)
        for itemname in items:
            typeInSearch(itemname,pos)
            pyautogui.click(pos[0]+866,pos[1]+325)
            time.sleep(0.1)
            pyautogui.click(pos[0]+582,pos[1]+543)
            time.sleep(0.1)
        items=[]
        pyautogui.click(pos[0]+944,pos[1]+255)
        pyautogui.click(pos[0]+944,pos[1]+255)

def buy(pos,itemname):
    global items
    pyautogui.click(pos[0]+866,pos[1]+325)
    time.sleep(0.1)
    pyautogui.click(pos[0]+582,pos[1]+543)
    time.sleep(0.1)
    items.append(itemname)

def BMtoAH(hwin):
    img,pos = grab_screen(hwin)
    pyautogui.keyDown('esc')
    time.sleep(0.28)
    pyautogui.keyUp('esc')
    pyautogui.mouseDown(pos[0]+1100,pos[1]+500,button='right')
    time.sleep(0.28)
    pyautogui.mouseUp(button='right')
    time.sleep(2.5)
    pyautogui.mouseDown(pos[0]+1200,pos[1]+400,button='right')
    time.sleep(0.28)
    pyautogui.mouseUp(button='right')
    time.sleep(2.5)
    pyautogui.mouseDown(pos[0]+1200,pos[1]+400,button='right')
    time.sleep(0.28)
    pyautogui.mouseUp(button='right')
    time.sleep(2.5)
    pyautogui.mouseDown(pos[0]+1200,pos[1]+400,button='right')
    time.sleep(0.28)
    pyautogui.mouseUp(button='right')
    time.sleep(6)
    while blackscreen(hwin):
        logging.debug('found blackscreen. waiting...')
        logging.debug(blackscreen(hwin))
        time.sleep(6)
    time.sleep(2)
    pyautogui.mouseDown(pos[0]+660,pos[1]+100,button='right')
    time.sleep(0.28)
    pyautogui.mouseUp(button='right')
    time.sleep(2)
    pyautogui.mouseDown(pos[0]+860,pos[1]+100,button='left')
    time.sleep(0.28)
    pyautogui.mouseUp(button='left')
    time.sleep(1.5)

def AHtoBM(hwin):
    time.sleep(0.2)
    img,pos = grab_screen(hwin)
    pyautogui.keyDown('esc')
    time.sleep(0.28)
    pyautogui.keyUp('esc')
    pyautogui.click(pos[0]+610,pos[1]+720,button='right')
    pyautogui.mouseDown(pos[0]+610,pos[1]+720,button='right')
    time.sleep(0.28)
    pyautogui.mouseUp(button='right')
    time.sleep(2)
    pyautogui.mouseDown(pos[0]+740,pos[1]+720,button='right')
    time.sleep(0.28)
    pyautogui.mouseUp(button='right')
    time.sleep(2)
    pyautogui.mouseDown(pos[0]+740,pos[1]+720,button='right')
    time.sleep(0.28)
    pyautogui.mouseUp(button='right')
    time.sleep(6)
    while blackscreen(hwin):
        logging.debug('found blackscreen. waiting...')
        time.sleep(6)
    time.sleep(2)
    pyautogui.mouseDown(pos[0]+30,pos[1]+240,button='right')
    time.sleep(0.28)
    pyautogui.mouseUp(button='right')
    time.sleep(2.5)
    pyautogui.mouseDown(pos[0]+30,pos[1]+240,button='right')
    time.sleep(0.28)
    pyautogui.mouseUp(button='right')
    time.sleep(2.5)
    pyautogui.mouseDown(pos[0]+130,pos[1]+240,button='right')
    time.sleep(0.28)
    pyautogui.mouseUp(button='right')
    time.sleep(2.5)
    pyautogui.mouseDown(pos[0]+500,pos[1]+230,button='left')
    time.sleep(0.28)
    pyautogui.mouseUp(button='left')
    time.sleep(1)

def blackscreen(hwin):
    img,pos = grab_screen(hwin)
    logging.debug(f'sample screen color is {img[30,20]}')
    return np.max(img[30:40,10:20]) < 15

def changeTier(pos,changetier):
    global tier
    pyautogui.click(pos[0]+728,pos[1]+211)
    pyautogui.click(pos[0]+728,pos[1]+251+20*changetier)
    tier = changetier
    time.sleep(0.1)

def changeQuality(pos,changequality):
    global quality
    pyautogui.click(pos[0]+838,pos[1]+211)
    pyautogui.click(pos[0]+838,pos[1]+251+20*changequality)
    quality = changequality
    time.sleep(0.1)

def changeLevel(pos,changelevel):
    global level
    pyautogui.click(pos[0]+618,pos[1]+211)
    pyautogui.click(pos[0]+618,pos[1]+251+20*changelevel)
    level = changelevel
    time.sleep(0.1)

def main():
    time.sleep(2)
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    active = win32gui.GetForegroundWindow()
    hwin = win32gui.FindWindow(None, "Albion Online Client")
    i=0
    global data, money, repeat
    while True:
        if i%4 == 0 and i != 0:
            logging.info('Writing datafile. i == '+str(i))
            with open('data', 'wb') as fp:
                pickle.dump(data, fp)
            with open('money', 'wb') as fp:
                pickle.dump(money, fp)
        BMfull = BM(hwin,active,repeat)
        logging.debug(f'BMfull is {BMfull}')
        BMtoAH(hwin)
        AH(hwin,active,BMfull)
        AHtoBM(hwin)
        i+=1

def testRoad():
    time.sleep(2)
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    active = win32gui.GetForegroundWindow()
    hwin = win32gui.FindWindow(None, "Albion Online Client")
    while True:
        BMtoAH(hwin)
        AHtoBM(hwin)

def testMoney(imgpath):
  img = cv.imread(imgpath,0)
  logging.info(read_money(img))

def readData(filename):
    with open (filename, 'rb') as fp:
        data = pickle.load(fp)
    plt.scatter(list(zip(*data))[0],list(zip(*data))[1])
    plt.show()

def readMoney(filename):
    with open (filename, 'rb') as fp:
        data = pickle.load(fp)
    logging.info(data)

def matchPrice(string):
  return (re.match('^\d{1,3}(,\d{3})+$',string) is not None)

def sniffPackets():
    pass

if __name__ == '__main__':
    if sys.argv[1]=='go':
        main()
    elif sys.argv[1]=='read':
        readMoney('money') 
    elif sys.argv[1]=='testRoad':
        testRoad()
    elif sys.argv[1]=='readData':
        readData('data')
