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

def change_cfg(param, value):
    cfg = open(DATA + '/config.cfg', encoding = 'utf-8', mode = 'r+')
    tmp = cfg.read()
    beg = tmp[0:tmp.find(param)]
    end = tmp[tmp.find('\n', len(beg)):]
    strng = param + ' = ' + value
    cfg.seek(0)
    cfg.truncate()
    cfg.write(beg + strng + end)
    cfg.close()

def read_cfg(param):
    cfg = open(DATA + '/config.cfg', encoding = 'utf-8', mode = 'r+')
    tmp = cfg.read()
    value = tmp[tmp.find(param)+len(param)+3:tmp.find('\n', tmp.find(param))]
    cfg.close()
    return value

class Settings(QDialog):
    
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.parent = parent
        self.title = 'Settings'
        self.left = 10
        self.top = 10
        self.width = 400
        self.height = 111
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
        self.lan_box.move(330, 0)
        self.lan_box.resize(65, 20)
        self.lan_box.activated[str].connect(self.onChanged)
        
        self.pic_holder = QLabel(self)
        self.pic_holder.resize(20, 20)
        self.pic_holder.move(300, 55)
        
        self.creator = QLabel(self)
        self.creator.resize(90, 20)
        self.creator.setText(ln.langs.get(self.parent.lang, ln.eng).get('creator', '***'))
        self.creator.move(2, 55)
        
        self.textEdit = QLineEdit(self)
        self.textEdit.move(90, 55)
        self.textEdit.resize(200, 20)
        self.textEdit.setText(read_cfg('creator'))
        self.textEdit.textChanged.connect(self.remove_checkmark)
        
        self.save_cr = QtWidgets.QPushButton(self)   #file dialog button
        self.save_cr.setStyleSheet("border: 1px solid grey")
        self.save_cr.move(330, 53)
        self.save_cr.resize(65, 22)
        self.save_cr.setText(ln.langs.get(self.parent.lang, ln.eng).get('save', '***'))
        self.save_cr.clicked.connect(self.save_creator)
        
        self.lan_txt = QLabel(self)
        self.lan_txt.resize(100, 20)
        self.lan_txt.setText(ln.langs.get(self.parent.lang, ln.eng).get('lang', '***'))
        self.lan_txt.move(2, 0)
        
        self.b1 = QtWidgets.QPushButton(self)   #file dialog button
        self.b1.setStyleSheet("border: 1px solid grey")
        self.b1.move(330, 25)
        self.b1.resize(65, 22)
        self.b1.setText(ln.langs.get(self.parent.lang, ln.eng).get('choose_dir_btn', '***'))
        self.b1.clicked.connect(self.openFileNameDialog)
    
        self.label1 = QLabel(self)  #this label shows directory path once it's chosen
        self.label1.resize(330, 22)
        self.label1.setText(ln.langs.get(self.parent.lang, ln.eng).get('dir_set', '***') + ': ' + self.parent.hgtdir)
        self.label1.move(2, 27)
        
        self.cb = QCheckBox(ln.langs.get(self.parent.lang, ln.eng).get('snap_chk', '***'), self)
        self.cb.move(1, 83)
        self.cb.resize(155, 20)
        print(self.parent.point)
        self.cb.setChecked(self.parent.point)
        self.cb.stateChanged.connect(self.changeState)
    
    def remove_checkmark(self):   
        self.pic_holder.clear()
        
    def save_creator(self):
        change_cfg('creator', self.textEdit.text())
        self.pic_holder.setPixmap(self.parent.checkmark)
     
    def openFileNameDialog(self):
        print(self.parent.point)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        directory = QFileDialog.getExistingDirectory(self,ln.langs.get(self.parent.lang, ln.eng).get('f_dial', '***'), options=options)
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
        self.parent.label3.setText(" ")
        self.parent.label4.setText(" ")
        self.lan_txt.setText(ln.langs.get(self.parent.lang, ln.eng).get('lang', '***'))
        self.parent.label2.setText(ln.langs.get(self.parent.lang, ln.eng).get('wait_stat', '***'))
        self.parent.help.setText(ln.langs.get(self.parent.lang, ln.eng).get('help_btn', '***'))
        self.parent.set.setText(ln.langs.get(self.parent.lang, ln.eng).get('set_btn', '***'))
        self.parent.sign.setPixmap(self.parent.play)
        
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
     
class Main_window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'TrackGen'
        self.left = 10
        self.top = 10
        self.width = 400
        self.height = 111
        self.settng = None
        self.initUI()
    
    def initUI(self):
        
        self.langs = list(ln.langs)
                
        if not os.path.isfile(DATA + "/config.cfg"): 
            self.cfg_file = open(DATA + '/config.cfg', 'w')
            self.cfg_file.write('lan = eng\nhgtdir = data\ncreator = Советские военные карты\npoints = false\n')
            self.cfg_file.close()
        
        self.lang = read_cfg('lan')
        
        self.hgtdir = read_cfg('hgtdir')    #name of the folder containing AW3D30 DSM files
        
        self.creator = read_cfg('creator')
        
        self.do_points = read_cfg('points')
        if self.do_points == 'true':
            self.point = True
        else:
            self.point = False
        
        self.b1 = QtWidgets.QPushButton(self)   #file dialog button
        self.b1.setStyleSheet("border: 1px solid grey")
        self.b1.resize(90, 22)
        self.b1.setText(ln.langs.get(self.lang, ln.eng).get('choose_file_btn', '***'))
        self.b1.clicked.connect(self.openFileNameDialog)
        
        #icons for info and fun
        self.play = QPixmap(DATA + '/play.png').scaled(20, 20, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.checkmark = QPixmap(DATA + '/checkmark.png').scaled(20, 20, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.warning = QPixmap(DATA + '/warning.png').scaled(20, 20, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.hourglass = QMovie(DATA + "/hourglass.gif")
        self.hourglass.start()
        
        self.b2 = QtWidgets.QPushButton(self)   #starting button that calls generate() function
        self.b2.setStyleSheet("border: 1px solid grey")
        self.b2.resize(90, 20)
        self.b2.setText(ln.langs.get('lang_name', ln.eng).get('gen_btn', '***'))
        self.b2.move(0, 80)
        self.b2.clicked.connect(self.generate)
        self.b2.setEnabled(False)
        
        self.label1 = QLabel(self)  #this label shows file path once it's chosen
        self.label1.resize(400, 20)
        self.label1.setText("...")
        self.label1.move(90, 0)
        
        self.endlabel = QLabel(self)    #label just for any text
        self.endlabel.resize(400, 20)
        self.endlabel.setText("TrackGen v1.0 - by Me, I wrote it all by myself (JK)||||sugarapplebombs@gmail.com")
        self.endlabel.move(0, 94)
        
        self.sign = QLabel(self)    #label for holding info and fun icons
        self.sign.resize(30, 30)
        self.sign.move(90, 75)
        self.sign.setPixmap(self.play)
        
        self.label2 = QLabel(self)  #status label
        self.label2.resize(400, 20)
        self.label2.setAlignment(Qt.AlignCenter)
        self.label2.setText(ln.langs.get(self.lang, ln.eng).get('wait_stat', '***'))
        self.label2.move(0, 62)
        
        self.label3 = QLabel(self)  #this label shows how many tracks are found and processed
        self.label3.resize(400, 20)
        self.label3.setAlignment(Qt.AlignCenter)
        self.label3.setText(" ")
        self.label3.move(0, 48)
        
        self.label4 = QLabel(self)  #this label shows how many points are found and processed
        self.label4.resize(400, 20)
        self.label4.setAlignment(Qt.AlignCenter)
        self.label4.setText(" ")
        self.label4.move(0, 34)
        
        self.set = QtWidgets.QPushButton(self)
        self.set.setStyleSheet("border: 1px solid grey")
        self.set.resize(70, 20)
        self.set.setText(ln.langs.get(self.lang, ln.eng).get('set_btn', '***'))
        self.set.move(260, 80)
        self.set.clicked.connect(self.open_settings)
        
        self.help = QtWidgets.QPushButton(self)
        self.help.setStyleSheet("border: 1px solid grey")
        self.help.resize(70, 20)
        self.help.setText(ln.langs.get(self.lang, ln.eng).get('help_btn', '***'))
        self.help.move(330, 80)
        self.help.clicked.connect(self.open_help)
        
        self.gif = QLabel(self)
        self.gif.resize(63, 80)
        self.gif.setAlignment(Qt.AlignCenter)
        self.gif.move(337, 0)
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
        settngs = Settings(parent = self)
        settngs.exec_()
        settngs.deleteLater()
    
    def open_help(self):
        self.help_path = DATA + "/help.pdf"
        webbrowser.open_new(os.path.abspath(self.help_path))
    
    def openFileNameDialog(self):
        print(self.point)
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
                file = open(path, 'rb')
                file.readline()
                file.readline()
                file.read(2)
                self.sign.setMovie(self.hourglass)
                self.label2.setText(ln.langs.get(self.lang, ln.eng).get('doing_stat', '***') + "...")
                self.label2.repaint()
                path = self.label1.text()
                self.label3.setText(ln.langs.get(self.lang, ln.eng).get('no_trks', '***'))
                self.label4.setText(ln.langs.get(self.lang, ln.eng).get('no_pnts', '***'))
                working_thread = threading.Thread(target=gen.generate, args=(path, self))
                working_thread.start()    #main calculating is called
                file.close()
            else:
                self.label2.setText(ln.langs.get(self.lang, ln.eng).get('format_wrn', '***'))
                self.sign.setPixmap(self.warning)
                self.b2.setEnabled(False)
        else:
            self.label2.setText(ln.langs.get(self.lang, ln.eng).get('no_file_wrn', '***'))
            self.sign.setPixmap(self.warning)
            self.b2.setEnabled(False)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main_window()
    ex.show()
    if ex.flag:
        ex.movie.stop()
    sys.exit(app.exec_())
    ex.hourglass.stop()