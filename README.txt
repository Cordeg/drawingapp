必要なパッケージ：
Django


Web app実行：
serverディレクトリで
python manage.py runserver
というコマンドを実行する。
アプリにアクセスするには、ブラウザで http://127.0.0.1:8000/app/display/ へ飛ぶ。


機能：
ページに一枚だけ画像が表示されて、ボタンをクリックするとランダムに別の画像が表示される。
画像はserver/static/imagesの下のディレクトリにある画像からランダムに選ばれる。


追加機能（Advanced）：
ツイッターのアカウントから画像をダウンロードする機能について。
この機能を使うにはツイッターAPIのトークンが必要。

まず、ダウンロードしたいアカウントのユーザー名を列挙したusernames.txtというファイルををserver/static/imagesにおいておく。usernames.txtの形式は
=============
@AAA
@BBB
@CCC
=============
のような形式。

さらに、server/drawingapp/my_classesのconfig.pyに
=============
API_KEY = ""
API_SECRET = ""
BEARER_TOKEN = ""
=============
のように、ツイッターAPIのトークン等を書いて置いておく。

その後、server/drawingapp/my_classesで
python tw_API_image_urls.py
と
python download_image.py
を実行する。
ひとつ目で過去のツイートから画像のURLを抽出、二つ目でURLから画像をダウンロードしている。
server/static/imagesにユーザー名ごとに@****#newというフォルダが作成される。

#new付きのはランダムな画像の表示にかからないようになってる。
あとは必要な画像・描きたい画像を取り出して別のフォルダに移せば良い。

ちなみに初回は4年遡ってツイートを取得している。
毎回検索した範囲を記憶しており、2回目からは前回終了した時点まで遡ることになる。