# Rename_Conventions
![screenshot](images/Texture_Connector_Window.PNG)  
[English](README_EN.md)
## 概要
Mayaのオブジェクトの命名規則を自動で設定するツールです。
## 要件
なし
## 使い方
1.ドキュメントのmaya/使用バージョン/script内に.pyファイルを移動する。  
2.以下のコマンドを実行する。
```
import Rename_Conventions
Rename_Conventions.openWindow()
```  
またはscriptEditor上で直に実行する。
## 説明
・すべてを変更する場合
1."Rename All"ボタンを押す。
・選択したオブジェクトを変更する場合
1.名前を変更したいオブジェクトを選択。
2."Rename Selected"ボタンを押す。
・オプション
1."Config"タブに移動する。   
2.命名規則を手動で変更する。  
2-1.FORMATエリアで順序を決定する。  
(&lt;SIDE&gt;は左右、&lt;NAME&gt;はオブジェクトの名前、&lt;TYPE&gt;はオブジェクトの種類)  
2-2.TYPEエリアで種類ごとの名前を決定する。  
2-3.SIDEエリアで左右の名前を決定する。  
2-4.OPTIONエリアで追加の規則を決定する。  
(&lt;CHR&gt;、"char1"を設定し、FORMATを&lt;CHR&gt;&#095;&lt;TYPE&gt;&#095;&lt;NAME&gt;に設定すると、  
char1_bodyなどの名前をchar1_GEO_bodyにできる)  
## 作者
[Twitter](https://x.com/cotte_921)

## ライセンス
[MIT](LICENSE)
