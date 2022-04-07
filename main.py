import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog, QLabel, QDesktopWidget, QCheckBox, QComboBox, QMainWindow, QDialog, QLineEdit
from PyQt5.QtGui import QIcon, QPixmap, QMovie
from PyQt5.QtCore import Qt
import os
import threading
import webbrowser
import langs as ln
import gen
DATA = 'data'   #name of the folder containing misc files
CONFIG = 'lan = eng\nhgtdir = data\ncreator = Советские военные карты\npoints = false\ntimeshift = +0\ninterpolate = true\n'
def change_cfg(param, value):
    if not os.path.isfile(DATA + "/config.cfg"): 
        cfg_file = open(DATA + '/config.cfg', encoding = 'utf-8', mode = 'w')
        tmp = CONFIG
        cfg_file.write(tmp)
        cfg_file.close()
    
    cfg = open(DATA + '/config.cfg', encoding = 'utf-8', mode = 'r+')
    tmp = cfg.read()
    pos = tmp.find(param)
    if pos != -1:
        beg = tmp[0:pos]
        end = tmp[tmp.find('\n', len(beg)):]
        strng = param + ' = ' + value
        cfg.seek(0)
        cfg.truncate()
        cfg.write(beg + strng + end)
        cfg.close()
    else:
        cfg.close()
        add_cfg(param, value)

def delete_cfg(param):
    if not os.path.isfile(DATA + "/config.cfg"): 
        cfg_file = open(DATA + '/config.cfg', encoding = 'utf-8', mode = 'w')
        tmp = CONFIG
        cfg_file.write(tmp)
        cfg_file.close()
    
    cfg = open(DATA + '/config.cfg', encoding = 'utf-8', mode = 'r+')
    tmp = cfg.read()
    if tmp.find(param) != -1:
        beg = tmp.find(param)
        end = tmp.find('\n', beg) + 1
        tmp = tmp[0:beg] + tmp[end:]
        cfg.seek(0)
        cfg.truncate()
        cfg.write(tmp)
    cfg.close()

def add_cfg(param, value):
    if not os.path.isfile(DATA + "/config.cfg"): 
        cfg_file = open(DATA + '/config.cfg', encoding = 'utf-8', mode = 'w')
        tmp = CONFIG
        cfg_file.write(tmp)
        cfg_file.close()
    
    cfg = open(DATA + '/config.cfg', encoding = 'utf-8', mode = 'r+')
    tmp = cfg.read()
    if tmp.find(param) == -1:
        cfg.write(param + ' = ' + value + '\n')
    cfg.close()
    
def read_cfg(param):
    if not os.path.isfile(DATA + "/config.cfg"): 
        cfg_file = open(DATA + '/config.cfg', encoding = 'utf-8', mode = 'w')
        tmp = CONFIG
        cfg_file.write(tmp)
        cfg_file.close()
    
    cfg = open(DATA + '/config.cfg', encoding = 'utf-8', mode = 'r+')
    tmp = cfg.read()
    start = tmp.find(param)+len(param)+3
    end = tmp.find('\n', tmp.find(param))
    value = tmp[start:end] if tmp.find(param)!= -1 else None
    cfg.close()
    return value

class Settings(QDialog):
    
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.parent = parent
        self.title = 'Settings'
        self.left = 10
        self.top = 10
        self.width = 420
        self.height = 185
        self.initUI(parent)
    
    def initUI(self, parent):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width, self.height)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        self.setWindowIcon(QIcon(DATA + '/knuckles.png'))
        
        self.lan_box = QComboBox(self)      #language choice
        for i, language in enumerate(parent.langs):
            self.lan_box.addItem(language)
            if parent.lang == parent.langs[i]:
                self.lan_box.setCurrentIndex(i)
        self.lan_box.move(341, 0)
        self.lan_box.resize(78, 30)
        self.lan_box.activated[str].connect(self.onChanged)
        
        self.pic_holder = QLabel(self)
        self.pic_holder.resize(20, 20)
        self.pic_holder.move(310, 85)
        
        self.creator = QLabel(self)
        self.creator.resize(90, 30)
        self.creator.setText(ln.langs.get(self.parent.lang, ln.eng).get('creator', '***'))
        self.creator.move(2, 80)
        
        self.textEdit = QLineEdit(self)
        self.textEdit.move(100, 81)
        self.textEdit.resize(200, 28)
        self.textEdit.setText(read_cfg('creator'))
        self.textEdit.textChanged.connect(self.remove_checkmark)
        
        self.save = QtWidgets.QPushButton(self)   #save button
        #self.save_cr.setStyleSheet("border: 1px solid grey")
        self.save.move(330, 75)
        self.save.resize(0, 0)
        self.save.setText('ээ')
        
        self.save_cr = QtWidgets.QPushButton(self)   #save button
        #self.save_cr.setStyleSheet("border: 1px solid grey")
        self.save_cr.move(340, 80)
        self.save_cr.resize(80, 30)
        self.save_cr.setText(ln.langs.get(self.parent.lang, ln.eng).get('save', '***'))
        self.save_cr.clicked.connect(self.save_creator)
        
        self.lan_txt = QLabel(self)
        self.lan_txt.resize(100, 20)
        self.lan_txt.setText(ln.langs.get(self.parent.lang, ln.eng).get('lang', '***'))
        self.lan_txt.move(2, 5)
        
        self.b1 = QtWidgets.QPushButton(self)   #file dialog button
        #self.b1.setStyleSheet("border: 1px solid grey")
        self.b1.move(340, 40)
        self.b1.resize(80, 30)
        self.b1.setText(ln.langs.get(self.parent.lang, ln.eng).get('choose_dir_btn', '***'))
        self.b1.clicked.connect(self.openFileNameDialog)
    
        self.label1 = QLabel(self)  #this label shows directory path once it's chosen
        self.label1.resize(330, 30)
        self.label1.setText(ln.langs.get(self.parent.lang, ln.eng).get('dir_set', '***') + ': ' + self.parent.hgtdir)
        self.label1.move(2, 40)
        
        self.cb = QCheckBox(ln.langs.get(self.parent.lang, ln.eng).get('snap_chk', '***'), self)
        self.cb.move(1, 160)
        self.cb.resize(155, 20)
        self.cb.setChecked(self.parent.point)
        self.cb.stateChanged.connect(self.changeState)
        
        self.cb1 = QCheckBox(ln.langs.get(self.parent.lang, ln.eng).get('inter', '***'), self)
        self.cb1.move(240, 160)
        self.cb1.resize(155, 20)
        self.cb1.setChecked(self.parent.inter)
        self.cb1.stateChanged.connect(self.changeState1)
        
        self.timeshift = QLabel(self)
        self.timeshift.resize(200, 30)
        self.timeshift.setText(ln.langs.get(self.parent.lang, ln.eng).get('timeshift', '***'))
        self.timeshift.move(2, 120)
        
        self.timeshifttxt = QLineEdit(self)
        self.timeshifttxt.move(180, 121)
        self.timeshifttxt.resize(50, 28)
        self.timeshifttxt.setText(read_cfg('timeshift'))
        self.timeshifttxt.textChanged.connect(self.remove_checkmark1)
        
        self.savetime = QtWidgets.QPushButton(self)   #save button
        #self.save_cr.setStyleSheet("border: 1px solid grey")
        self.savetime.move(340, 120)
        self.savetime.resize(80, 30)
        self.savetime.setText(ln.langs.get(self.parent.lang, ln.eng).get('save', '***'))
        self.savetime.clicked.connect(self.save_time)
        
        self.pic_holder1 = QLabel(self)
        self.pic_holder1.resize(20, 20)
        self.pic_holder1.move(310, 120)
        
    def remove_checkmark(self):   
        self.pic_holder.clear()
        
    def remove_checkmark1(self):   
        self.pic_holder1.clear()
        
    def save_creator(self):
        self.parent.creator = self.textEdit.text()
        change_cfg('creator', self.parent.creator)
        self.pic_holder.setPixmap(self.parent.checkmark)
    
    def save_time(self):
        text = self.timeshifttxt.text()
        
        if text[0]!='+' and text[0]!='-':
            text = '+' + text
            
        if text[1:].isdecimal():
            if -12 <= int(text[1:]) <= 12:
                self.parent.timeshift = text
                change_cfg('timeshift', self.parent.timeshift)
                self.timeshifttxt.setText(text)
                self.pic_holder1.setPixmap(self.parent.checkmark)
            else:
                self.pic_holder1.setPixmap(self.parent.warning)
        elif len(text[1:].split(':')) == 2:
            temp = text[1:].split(':')
            if temp[0].isdecimal() and temp[1].isdecimal():
                if -12 <= int(temp[0]) <= 12 and 0 <= int(temp[1]) <= 59:
                    self.parent.timeshift = text
                    change_cfg('timeshift', self.parent.timeshift)
                    self.timeshifttxt.setText(text)
                    self.pic_holder1.setPixmap(self.parent.checkmark)
                else:
                    self.pic_holder1.setPixmap(self.parent.warning)
            else:
                self.pic_holder1.setPixmap(self.parent.warning)
                
        else:
            self.pic_holder1.setPixmap(self.parent.warning)
            
     
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        directory = QFileDialog.getExistingDirectory(self,ln.langs.get(self.parent.lang, ln.eng).get('d_dial', '***'), options=options)
        if directory:
            self.parent.hgtdir = directory
            self.label1.setText(ln.langs.get(self.parent.lang, ln.eng).get('dir_set', '***') + ': ' + self.parent.hgtdir)
            change_cfg('hgtdir', directory)
            
        
    def onChanged(self, text):      # changing GUI language and repainting all the text
        change_cfg('lan', text)
        self.parent.lang = text
        
        self.save_cr.setText(ln.langs.get(self.parent.lang, ln.eng).get('save', '***'))
        self.creator.setText(ln.langs.get(self.parent.lang, ln.eng).get('creator', '***'))
        self.label1.setText(ln.langs.get(self.parent.lang, ln.eng).get('dir_set', '***') + ': ' + self.parent.hgtdir)
        self.b1.setText(ln.langs.get(self.parent.lang, ln.eng).get('choose_dir_btn', '***'))
        self.parent.b1.setText(ln.langs.get(self.parent.lang, ln.eng).get('choose_file_btn', '***'))
        self.parent.b2.setText(ln.langs.get(self.parent.lang, ln.eng).get('gen_btn', '***'))
        self.cb.setText(ln.langs.get(self.parent.lang, ln.eng).get('snap_chk', '***'))
        self.cb1.setText(ln.langs.get(self.parent.lang, ln.eng).get('inter', '***'))
        self.parent.label3.setText(" ")
        self.parent.label4.setText(" ")
        self.lan_txt.setText(ln.langs.get(self.parent.lang, ln.eng).get('lang', '***'))
        self.parent.label2.setText(ln.langs.get(self.parent.lang, ln.eng).get('wait_stat', '***'))
        self.parent.help.setText(ln.langs.get(self.parent.lang, ln.eng).get('help_btn', '***'))
        self.parent.set.setText(ln.langs.get(self.parent.lang, ln.eng).get('set_btn', '***'))
        self.parent.sign.setPixmap(self.parent.play)
        self.timeshift.setText(ln.langs.get(self.parent.lang, ln.eng).get('timeshift', '***'))
        self.savetime.setText(ln.langs.get(self.parent.lang, ln.eng).get('save', '***'))
        
    def changeState(self):
        self.parent.point = not self.parent.point
        if self.parent.point:
            self.tmp = 'true'
        else:
            self.tmp = 'false'
        change_cfg('points', self.tmp)
        if not self.parent.easter_flag:
            self.parent.easter_counter += 1
            if self.parent.easter_counter == 10:
                if self.parent.flag and self.parent.dim.width()<=63 and self.parent.dim.height()<=80:
                    self.parent.movie.start()
                else:
                    self.parent.gif.setText("There should\nhave been\na kitten\nbut someone\nstole it")
                self.parent.easter_flag = True
                
    def changeState1(self):
        self.parent.inter = not self.parent.inter
        if self.parent.inter:
            self.tmp = 'true'
        else:
            self.tmp = 'false'
        change_cfg('interpolate', self.tmp)
        
class Main_window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'TrackGen'
        self.left = 10
        self.top = 10
        self.width = 600
        self.height = 180
        self.settngs = None
        self.initUI()
    
    def initUI(self):
        
        self.langs = list(ln.langs)
                
        if not os.path.isfile(DATA + "/config.cfg"): 
            self.cfg_file = open(DATA + '/config.cfg', encoding = 'utf-8', mode = 'w')
            self.tmp = CONFIG
            self.cfg_file.write(self.tmp)
            self.cfg_file.close()
        
        self.lang = read_cfg('lan')
        if self.lang is None:
            self.lang = 'eng'
            add_cfg('lan', self.lang)
        
        self.hgtdir = read_cfg('hgtdir')    #name of the folder containing AW3D30 DSM files
        if self.hgtdir is None:
            self.hgtdir = 'data'
            add_cfg('hgtdir', self.lang)
            
        self.creator = read_cfg('creator')
        if self.creator is None:
            self.creator = 'Советские военные карты'
            add_cfg('creator', self.creator)
            
        self.timeshift = read_cfg('timeshift')
        if self.timeshift is None:
            self.timeshift = '+0'
            add_cfg('timeshift', self.timeshift)
            
        self.do_points = read_cfg('points')
        if self.do_points == 'true':
            self.point = True
        else:
            self.point = False
        if self.do_points == None:
            self.point = False
            add_cfg('points', 'false')
            
        self.do_inter = read_cfg('interpolate')
        if self.do_inter == 'true':
            self.inter = True
        else:
            self.inter = False
        if self.do_inter == None:
            self.inter = True
            add_cfg('interpolate', 'true')
            
        self.b1 = QtWidgets.QPushButton(self)   #file dialog button
        #self.b1.setStyleSheet("border: 1px solid grey")
        self.b1.resize(100, 30)
        self.b1.setText(ln.langs.get(self.lang, ln.eng).get('choose_file_btn', '***'))
        self.b1.clicked.connect(self.openFileNameDialog)
        
        #icons for info and fun
        self.play = QPixmap(DATA + '/play.png').scaled(20, 20, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.checkmark = QPixmap(DATA + '/checkmark.png').scaled(20, 20, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.warning = QPixmap(DATA + '/warning.png').scaled(20, 20, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.gear = QPixmap(DATA + '/gear.png').scaled(20, 20, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.hourglass = QMovie(DATA + "/hourglass.gif")
        self.hourglass.start()
        
        self.b2 = QtWidgets.QPushButton(self)   #starting button that calls generate() function
        #self.b2.setStyleSheet("border: 1px solid grey")
        self.b2.resize(100, 30)
        self.b2.setText(ln.langs.get(self.lang, ln.eng).get('gen_btn', '***'))
        self.b2.move(0, 130)
        self.b2.clicked.connect(self.generate)
        self.b2.setEnabled(False)
        
        self.label1 = QLabel(self)  #this label shows file path once it's chosen
        self.label1.resize(500, 20)
        self.label1.setText("...")
        self.label1.move(100, 5)
        
        self.endlabel = QLabel(self)    #label just for any text
        self.endlabel.resize(400, 20)
        self.endlabel.setText("TrackGen v1.2 - by Me, I wrote it all by myself (JK)||||sugarapplebombs@gmail.com")
        self.endlabel.move(1, 160)
        
        self.sign = QLabel(self)    #label for holding info and fun icons
        self.sign.resize(30, 30)
        self.sign.move(100, 130)
        self.sign.setPixmap(self.play)
        
        self.label2 = QLabel(self)  #status label
        self.label2.resize(600, 20)
        self.label2.setAlignment(Qt.AlignCenter)
        self.label2.setText(ln.langs.get(self.lang, ln.eng).get('wait_stat', '***'))
        self.label2.move(0, 85)
        
        self.label3 = QLabel(self)  #this label shows how many tracks are found and processed
        self.label3.resize(600, 20)
        self.label3.setAlignment(Qt.AlignCenter)
        self.label3.setText(" ")
        self.label3.move(0, 60)
        
        self.label4 = QLabel(self)  #this label shows how many points are found and processed
        self.label4.resize(600, 20)
        self.label4.setAlignment(Qt.AlignCenter)
        self.label4.setText(" ")
        self.label4.move(0, 35)
        
        self.set = QtWidgets.QPushButton(self)
        #self.set.setStyleSheet("border: 1px solid grey")
        self.set.resize(80, 30)
        self.set.setText(ln.langs.get(self.lang, ln.eng).get('set_btn', '***'))
        self.set.move(520, 120)
        self.set.clicked.connect(self.open_settings)
        
        self.set_icon = QLabel(self)
        self.set_icon.resize(30, 30)
        self.set_icon.move(497, 120)
        self.set_icon.setPixmap(self.gear)
        
        self.help = QtWidgets.QPushButton(self)
        #self.help.setStyleSheet("border: 1px solid grey")
        self.help.resize(80, 30)
        self.help.setText(ln.langs.get(self.lang, ln.eng).get('help_btn', '***'))
        self.help.move(520, 150)
        self.help.clicked.connect(self.open_help)
        
        self.gif = QLabel(self)
        self.gif.resize(63, 80)
        self.gif.setAlignment(Qt.AlignCenter)
        self.gif.move(537, 0)
        self.flag = False
        if os.path.isfile(DATA + "/giphy.gif"):
            self.flag = True
            self.movie_frame = QPixmap(DATA + "/giphy.gif")
            self.dim = QPixmap.size(self.movie_frame)
            self.movie = QMovie(DATA + "/giphy.gif")
            self.gif.setMovie(self.movie)
        self.easter_counter = 0
        self.easter_flag = False

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width, self.height)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        self.setWindowIcon(QIcon(DATA + '/knuckles.png'))
    
    def open_settings(self, checked):
        if self.settngs is None:
            self.settngs = Settings(parent = self)
        self.settngs.show()
    
    def open_help(self):
        self.help_path = DATA + "/help.pdf"
        webbrowser.open_new(os.path.abspath(self.help_path))
    
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,ln.langs.get(self.lang, ln.eng).get('f_dial', '***'), "","All Files (*);;GPX Files (*.gpx)", options=options)
        if fileName:
            self.label1.setText(fileName)
            self.label3.setText(" ")
            self.label2.setText(ln.langs.get(self.lang, ln.eng).get('ready_stat', '***'))
            self.sign.setPixmap(self.play)
            self.b2.setEnabled(True)
           
    def generate(self):
        path = self.label1.text()
        form = path[len(path)-3] + path[len(path)-2] + path[len(path)-1]
        
        if os.path.isfile(path):
            if form == "gpx":
                self.sign.setMovie(self.hourglass)
                self.label2.setText(ln.langs.get(self.lang, ln.eng).get('doing_stat', '***') + "...")
                self.label2.repaint()
                path = self.label1.text()
                self.label3.setText(ln.langs.get(self.lang, ln.eng).get('no_trks', '***'))
                self.label4.setText(ln.langs.get(self.lang, ln.eng).get('no_pnts', '***'))
                working_thread = threading.Thread(target=gen.generate, args=(path, self))
                self.b1.setEnabled(False)
                self.b2.setEnabled(False)
                self.set.setEnabled(False)
                working_thread.start()    #main calculating is called
            else:
                self.label2.setText(ln.langs.get(self.lang, ln.eng).get('format_wrn', '***'))
                self.sign.setPixmap(self.warning)
                self.b2.setEnabled(False)
        else:
            self.label2.setText(ln.langs.get(self.lang, ln.eng).get('no_file_wrn', '***'))
            self.sign.setPixmap(self.warning)
            self.b2.setEnabled(False)
        
if __name__ == '__main__':
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    main = Main_window()
    main.show()
    sys.exit(app.exec_())