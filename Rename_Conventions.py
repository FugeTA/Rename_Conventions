import maya.cmds as cmds
try:
    from PySide2 import QtWidgets,QtCore,QtGui
except:
    from PySide6 import QtWidgets,QtCore,QtGui
from maya.app.general import mayaMixin
import re

def objName(title):
    return(title + '_window')

class MainWindow(mayaMixin.MayaQWidgetBaseMixin,QtWidgets.QWidget):
    def __init__(self,title):
        super().__init__()
        self.title = title
        self.setWindowTitle(title)  # タイトル
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # deleteLater()の自動実行
        self.setObjectName(objName(title))  # ウィジェットとしての名前
        self.type = self.deftype = {'camera':'CAM','mesh':'GEO','joint':'JNT','endjoint':'END',
                                    'locator':'LCT','nurbsCurve':'CON','transform':'GRP'}  # typeの増減可能
        self.side = self.defside = ['R','L']
        self.layout = self.defLayout = '<SIDE>_<NAME>_<TYPE>'
        self.setLayout(self.layouts())
        self.resize(600, 600)
        self.getObjName()  # 起動時の選択反映
        self.sjnum = cmds.scriptJob(e=['SelectionChanged',self.getObjName],p=objName(title),cu=True)  # Maya上で選択されたときにウィンドウにも反映

    def layouts(self):
        mainLayout = QtWidgets.QVBoxLayout()  # メインのレイアウト
        self.tabLayout(mainLayout)  # タブの追加
        self.buttons(mainLayout)  # ボタンの追加
        return(mainLayout)

    def tabLayout(self,mainLayout):
        tabWidget = QtWidgets.QTabWidget()
        tab1 = QtWidgets.QWidget()
        tab2 = QtWidgets.QWidget()
        tabWidget.addTab(tab1,'Select Object')
        tabWidget.addTab(tab2,'Config')
        tab2.setLayout(self.tab2())
        tab1.setLayout(self.tab1())
        self.gridObject()  # グリッドの中身作成
        self.tableView.selectionModel().selectionChanged.connect(self.on_click)  # 表のアイテムを選択したとき
        mainLayout.addWidget(tabWidget)

    def tab2(self):
        mainLayout = QtWidgets.QVBoxLayout()
        vLayout = QtWidgets.QVBoxLayout()
        vLayout.setAlignment(QtCore.Qt.AlignTop)
        titleLabel = QtWidgets.QLabel(self.tr('<b>FORMAT</b>'))
        titleLabel.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        titleLabel.setMargin(5)
        vLayout.addWidget(titleLabel)
        self.lineEdit4 = QtWidgets.QLineEdit(self.defLayout)
        vLayout.addWidget(self.lineEdit4)
        titleLabel2 = QtWidgets.QLabel(self.tr('<b>TYPE</b>'))
        titleLabel2.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        titleLabel2.setMargin(5)
        vLayout.addWidget(titleLabel2)
        self.gridLayout = QtWidgets.QGridLayout()
        vLayout.addLayout(self.gridLayout)
        titleLabel3 = QtWidgets.QLabel(self.tr('<b>SIDE</b>'))
        titleLabel3.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        titleLabel3.setMargin(5)
        vLayout.addWidget(titleLabel3)
        self.lineEdit3 = QtWidgets.QLineEdit(','.join(self.defside))
        vLayout.addWidget(self.lineEdit3)
        # add option
        titleLabel4 = QtWidgets.QLabel(self.tr('<b>OPTION</b>'))
        titleLabel4.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        titleLabel4.setMargin(5)
        vLayout.addWidget(titleLabel4)
        hLayout5 = QtWidgets.QHBoxLayout()
        self.lineEdit5 = QtWidgets.QLineEdit('<OPTION>')  # FORMAT用の名前を追加できる
        hLayout5.addWidget(self.lineEdit5)
        self.lineEdit6 = QtWidgets.QLineEdit('')
        hLayout5.addWidget(self.lineEdit6)
        vLayout.addLayout(hLayout5)
        mainLayout.addLayout(vLayout)
        self.setStyleSheet('QLabel { background-color : rgb(100,100,100); }')
        #button
        hLayout3 = QtWidgets.QHBoxLayout()
        self.button5 = QtWidgets.QPushButton('Apply')  # Configの設定適用
        self.button5.clicked.connect(self.getCheckBox)
        hLayout3.addWidget(self.button5)
        self.button6 = QtWidgets.QPushButton('Reset')  # リセット
        self.button6.clicked.connect(self.resetSurfix)
        hLayout3.addWidget(self.button6)
        mainLayout.addLayout(hLayout3)
        return(mainLayout)
    
    def tab1(self):
        mainLayout = QtWidgets.QVBoxLayout()
        # Sort menu
        hLayout4 = QtWidgets.QHBoxLayout()
        hLayout = QtWidgets.QHBoxLayout()
        hLayout.setAlignment(QtCore.Qt.AlignRight)
        label = QtWidgets.QLabel('Sort by:')
        label.setStyleSheet('QLabel { background-color: none; }')
        hLayout.addWidget(label)
        # dropdown menu
        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.addItems(['Hierechy','Name','Type'])
        self.comboBox.currentIndexChanged.connect(self.sortTable)
        hLayout.addWidget(self.comboBox)
        # リセットボタン
        self.button1 = QtWidgets.QPushButton('Refresh')
        self.button1.clicked.connect(self.reset)  # オブジェクト側に変更があれば読み直せる
        hLayout.addWidget(self.button1)
        hLayout4.addLayout(hLayout)
        mainLayout.addLayout(hLayout4)
        # tablelayout
        tablelayout = QtWidgets.QHBoxLayout()
        self.tableModel = self.makeTable()
        self.tableView = self.makeTableView()
        self.tableView.setModel(self.tableModel)
        tablelayout.addWidget(self.tableView)
        tablelayout.setStretchFactor(self.tableView, 1)
        mainLayout.addLayout(tablelayout)
        return(mainLayout)

    def buttons(self,mainlayout):
        # 実行ボタン
        hLayout2 = QtWidgets.QHBoxLayout()
        self.button2 = QtWidgets.QPushButton('Rename All')
        self.button2.clicked.connect(self.execute_All)
        hLayout2.addWidget(self.button2)
        self.button3 = QtWidgets.QPushButton('Rename Selected')
        self.button3.clicked.connect(self.execute_Select)
        hLayout2.addWidget(self.button3)
        self.button4 = QtWidgets.QPushButton('Close')
        self.button4.clicked.connect(lambda: closeWindow(objName(self.title)))
        hLayout2.addWidget(self.button4)
        mainlayout.addLayout(hLayout2)

    # オプションメニューの中身
    def gridObject(self):
        layout = self.gridLayout
        self.checkBox = [None]*len(self.type)
        self.lineEdit2 = [None]*len(self.type)
        for i, (k, v) in enumerate(self.type.items()):  # typeをもとにその数だけアイテムを作成
            self.checkBox[i] = QtWidgets.QCheckBox(k)
            self.checkBox[i].setChecked(True)
            layout.addWidget(self.checkBox[i],i,0)
            self.lineEdit2[i] = QtWidgets.QLineEdit(v)
            layout.addWidget(self.lineEdit2[i],i,1)
        self.lineEdit2_2 = QtWidgets.QLineEdit('(type)')  # ユーザー追加用
        layout.addWidget(self.lineEdit2_2,len(self.type),0)
        self.lineEdit2_3 = QtWidgets.QLineEdit('')
        layout.addWidget(self.lineEdit2_3,len(self.type),1)
        self.getCheckBox()

    # 表の中身を作る
    def makeTable(self):
        tableModel = QtGui.QStandardItemModel()
        labelList = cmds.ls(dag=True,tr=True)
        readOnly = cmds.ls(dag=True,tr=True,ud=True)
        if (ref:= cmds.ls(dag=True,tr=True,rn=True)):
            readOnly = readOnly.extend(ref)
        labelList = [label for label in labelList if label not in readOnly]  # 名前の変更が不可能なものを排除
        layout = self.lineEdit4.text()
        side = self.lineEdit3.text()
        options = {self.lineEdit5.text():self.lineEdit6.text()}
        tableModel.setRowCount(len(labelList))
        tableModel.setColumnCount(4)
        tableModel.setHorizontalHeaderLabels(['Object','NAME','Type','New Name'])
        for i,label in enumerate(labelList):
            label2, label3, label4 = getName(label,self.type,layout,side,options)  # 実際のオブジェクトとその種類から新しい名前を作成
            tableModel.setItem(i,0,QtGui.QStandardItem(label))
            tableModel.setItem(i,1,QtGui.QStandardItem(label2))
            tableModel.setItem(i,2,QtGui.QStandardItem(label3))
            tableModel.setItem(i,3,QtGui.QStandardItem(label4))
        for row in range(tableModel.rowCount()):  # 3列目をEditableに
            for column in range(tableModel.columnCount()):
                item = tableModel.item(row, column)
                if column == 3:
                    item.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                else:
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        return(tableModel)

    # 表示
    def makeTableView(self):
        tableView = QtWidgets.QTableView()
        tableView.setModel(self.tableModel)
        tableView.resizeRowsToContents()
        tableView.resizeColumnsToContents()
        tableView.sortByColumn(-1, QtCore.Qt.SortOrder.AscendingOrder)
        tableView.verticalHeader().setVisible(False)
        tableView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        tableView.setShowGrid(False)
        tableView.setStyleSheet('border-right-color: rgb(255, 255, 255); border-left-color: rgb(255, 255, 255);')
        tableView.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        return(tableView)
    
    # Mayaでの選択を反映させる
    def getObjName(self):
        s = cmds.ls(sl=True)
        if not s:
            self.tableView.clearSelection()  # 無ければ選択解除
            return()
        self.tableView.selectionModel().selectionChanged.disconnect(self.on_click)  # 再帰回避のため選択での操作を解除
        self.tableView.clearSelection()
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)  # 選択方式を調整
        for name in s:
            items = self.tableModel.findItems(name, QtCore.Qt.MatchExactly)  # Mayaで選択したものを表から探す
            for item in items:
                self.tableView.selectRow(item.row())
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)  # 選択方式を戻す
        self.tableView.selectionModel().selectionChanged.connect(self.on_click)  # 選択での操作を再設定
    
    # ソート
    def sortTable(self):
        sort = self.comboBox.currentIndex()
        if sort == 0:
            self.makeTable()  # ヒエラルキーには戻せないので再度テーブルを作る
            return()
        self.tableView.sortByColumn(sort, QtCore.Qt.SortOrder.AscendingOrder)

    # 選択時
    def on_click(self):
        if cmds.scriptJob(ex=self.sjnum):
            cmds.scriptJob(kill=self.sjnum,f=True)
        cmds.select(cl=True)
        for sel in self.tableView.selectionModel().selectedRows():
            row = sel.row()
            cmds.select(self.tableModel.item(row, 0).text(), add=True)
        self.sjnum = cmds.scriptJob(e=['SelectionChanged',self.getObjName],p=objName(self.title),cu=True)

    # ウィンドウのリセット
    def reset(self):
        self.tableModel = self.makeTable()
        self.tableView.setModel(self.tableModel)
        self.tableView.selectionModel().selectionChanged.connect(self.on_click)
        self.getObjName()


    # チェックボックスを確認
    def getCheckBox(self):
        self.type = {self.checkBox[i].text(): self.lineEdit2[i].text() for i in range(len(self.lineEdit2)) if self.checkBox[i].isChecked()}
        if self.lineEdit2_2.text() and self.lineEdit2_3.text():
            self.type.update({self.lineEdit2_2.text(): self.lineEdit2_3.text()})
        self.reset()

    # 設定のリセット
    def resetSurfix(self):
        self.type = self.deftype
        self.layout = self.defLayout
        for i in range(len(self.lineEdit2)):
            self.checkBox[i].setChecked(True)
            self.lineEdit2[i].setText(self.deftype[self.checkBox[i].text()])
        self.lineEdit3.setText('.'.join(self.defside))
        self.lineEdit4.setText(str(self.defLayout))
        self.reset()
        self.gridObject()

    # すべて変更
    def execute_All(self):
        select_ = self.tableModel.rowCount() 
        cmds.undoInfo(openChunk=True)
        for sel in range(select_):
            self.base = self.tableModel.item(sel, 0).text()
            self.new = self.tableModel.item(sel, 3).text()
            self.rename()
        cmds.undoInfo(closeChunk=True)
        self.reset()

    # 選択して変更
    def execute_Select(self):
        cmds.undoInfo(openChunk=True)
        for sel in self.tableView.selectionModel().selectedRows():
            row = sel.row()
            self.base = self.tableModel.item(row, 0).text()
            self.new = self.tableModel.item(row, 3).text()
            self.rename()
        cmds.undoInfo(closeChunk=True)
        self.reset()

    # 処理
    def rename(self):
        if not self.new or self.base == self.new:  # 新しい名前がない、変更がないなら次へ
            return()
        cmds.rename(self.base,self.new)

# 子にジョイントがあるか
def getHierarchyType(s):
    s = cmds.listRelatives(s, c=True, ad=True)
    if not s:
        return()
    chl = [cmds.objectType(c) for c in s]
    return('joint' in chl)

# オブジェクトのタイプを確認
def getType(c,fix,s):
    type_ = cmds.objectType(c)
    if type_ == 'joint' or type_ == 'transform':
        type_ = cmds.objectType(s)
    try:
        affix = fix[str(type_)]
    except:
        affix = None
    return(type_,affix)

# オブジェクトタイプと辞書を確認
def getName(s,dict_,layout,side,options):
    if (chl := cmds.listRelatives(s, c=True)):
        # 子のtypeを親のtypeにする
        for c in chl:
            get = getType(c,dict_,s)
            type_ = get[0]
            affix = get[1]
            if affix and type_ =='joint' and not getHierarchyType(s):
                affix = affix+'_'+dict_['endjoint']
            if not type_ == 'transform':
                break
            getName(c,dict_,layout,side,options)
    else:
        type_ = cmds.objectType(s)
        affix = None
        if str(type_) in dict_.keys():
            affix = dict_[str(type_)]
        if (get:= getType(s,dict_,s)[1]) and type_ == 'joint':  
            affix = get+'_'+dict_['endjoint']
    return(subName(s,affix,layout,side,type_,options))

# 名前の部分が辞書にあれば変更
def subName(s,affix,layout,side,type_,options):
    newName = []
    for i in layout.split('_'):
        if affix and i == '<TYPE>':
            if re.search(affix, s):
                s = re.sub(rf'_{affix}|{affix}_','',s)
            newName.append(affix)
            continue
        if i == '<SIDE>':
            for j in side.split(','):
                if re.search(rf'_{j}$|^{j}_',s):
                    s = re.sub(rf'_{j}$|^{j}_','',s)
                    newName.append(j)
                    break
            continue
        if i == '<NAME>' or not re.search(r'<.*>',i):
            newName.append(i)
        if i in list(options.keys()):
            s = re.sub(rf'_{options[i]}$|_{options[i]}_|^{options[i]}_', '', s)
            newName.append(options[i])
        # 並び変え
    if not newName:
        return(s,None,type_)
    newName[newName.index('<NAME>')] = s
    name = '_'.join(newName)
    return(s,type_,name)

#  ウィンドウがすでに起動していれば閉じる
def closeWindow(title):
    if cmds.window(title, q=True, ex=True):  # ウィジェットの名前で削除
        cmds.deleteUI(title)

# ウィンドウのオブジェクト名
def objName(title):
    return(title + '_window')

#  アプリの実行と終了
def openWindow():
    title = 'Name_Format'
    closeWindow(objName(title))
    app = QtWidgets.QApplication.instance()
    window = MainWindow(title)
    window.show()
    app.exec_()

# 直接実行されたら
if __name__ == '__main__':
    openWindow()
