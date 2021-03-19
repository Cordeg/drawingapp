import os
import shutil
import urllib.error
import urllib.request
import json
from datetime import datetime

from pprint import pprint


class ImageDownloader:

    def download_images(self, username):

        image_root = self.get_image_dir()

        # urls を取得
        file_path_urls = os.path.join(image_root, "@%s_urls.json" % username)
        urls = self.__load_urls(file_path_urls)

        # 新しい画像を入れるためのディレクトリ
        user_dir = os.path.join(image_root, "@%s#new" % username)

        # urlsがあり、user_dir が存在しない場合はそのディレクトリを作る。
        if urls and not os.path.exists(user_dir):
            os.mkdir(user_dir)
            # 不要な画像を削除したかのステータスを持つJSONファイルを生成する
            self.mk_status_file(user_dir)

        # ついでに、#newでない（厳選された画像の入った）ディレクトリがなければ作っておく
        user_dir_to_show = os.path.join(image_root, "@%s" % username)
        if not os.path.exists(user_dir_to_show):
            os.mkdir(user_dir_to_show)


        # urlsの要素は(url, created_at)。urlから画像をダウンロードし、created_atはファイル名に使用する。
        for url, created_at in urls:
            # url からファイル名を抽出
            file_name = url.split('/')[-1]
            # created_atから"2020-07-28_"のような日付の文字列を作る
            time_dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.000Z")
            time_str = time_dt.strftime("%Y-%m-%d_")
            # 日付の文字列をファイル名に結合
            file_name = time_str + file_name
            # ファイルのパスを決定
            file_path = os.path.join(user_dir, file_name)

            # ダウンロードしてフォルダに格納
            self.__download_file(url, file_path)

        # url を消去
        if os.path.exists(file_path_urls):
            os.remove(file_path_urls)


    @staticmethod
    def __download_file(url, path):
        try:
            with urllib.request.urlopen(url) as web_file:
                data = web_file.read()
                with open(path, mode='wb') as local_file:
                    local_file.write(data)
        except urllib.error.URLError as e:
            print(e)


    @staticmethod
    def __load_urls(path):
        """
        path から urls を取得する。
        """
        if os.path.exists(path):
            with open(path, 'r') as f:
                urls = json.load(f)
        else:
            urls = []
            
        return urls


    @staticmethod
    def get_image_dir():
        # root=server/drawingapp
        root, folder = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        # root=server
        root, folder = os.path.split(root)
        # server/static/images のディレクトリに設定
        image_dir = os.path.join(root, "static", "images")

        # jupyter版
        #image_dir = os.path.join(os.getcwd(), "server", "static", "images")
        
        return image_dir


    @staticmethod
    def mk_status_file(path):
        file_name = os.path.join(path, "00_status.txt")
        with open(file_name, 'w') as f:
            status = {'delete unnecessary images': False}
            json.dump(status, f)
            
    @staticmethod
    def load_status(path):
        file_name = os.path.join(path, "00_status.txt")
        with open(file_name, 'r') as f:
            status = json.load(f)
        
        return status
        

    def transfer_new_images(self, username):
        image_root = self.get_image_dir()

        # 新しい画像を入れるためのディレクトリ
        user_dir = os.path.join(image_root, "@%s#new" % username)
        user_dir_to_show = os.path.join(image_root, "@%s" % username)

        if os.path.exists(user_dir):
            status = self.load_status(user_dir)

            # delete unnecessary images が True のときはディレクトリ内の画像を user_dir_to_show へ移動。
            if status['delete unnecessary images']:
                listdir = os.listdir(user_dir)
                for d in listdir:
                    if '.png' in d or '.jpeg' in d or '.jpg' in d:
                        # 画像ファイルは user_dir_to_show へ移動する。
                        shutil.move(os.path.join(user_dir, d), user_dir_to_show)
                
                shutil.rmtree(user_dir)


def load_usernames(filename):
        # root=server/drawingapp
        root, folder = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        # root=server
        root, folder = os.path.split(root)
        # server/static/images のディレクトリに設定
        image_dir = os.path.join(root, "static", "images")

        file_path = os.path.join(image_dir, filename)

        with open(file_path, 'r') as f:
            lines = f.readlines()
            lines = list(map(lambda x: x.strip(), lines))
        
        usernames = []
        for s in lines:
            if s and s[0]!='#':
                # #で始まる行はコメント
                if s[0]=='@':
                    usernames.append(s[1:])
                else:
                    usernames.append(s)
        
        return usernames


if __name__=='__main__':

    downloader = ImageDownloader()

    usernames = [
        "",
        ]

    usernames = load_usernames("usernames.txt")

    for username in usernames:
        print(username)

        downloader.download_images(username)
        
        downloader.transfer_new_images(username)

