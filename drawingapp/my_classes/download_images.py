import os
import urllib.error
import urllib.request
import json
from datetime import datetime

from pprint import pprint


class ImageDownloader:

    def download_images(self, username):

        image_root = self.__get_image_dir()
        user_dir = os.path.join(image_root, "@" + username)

        # user_dir が存在しない場合はそのディレクトリを作る。
        if not os.path.exists(user_dir):
            os.mkdir(user_dir)

        # urls を取得
        file_path_urls = os.path.join(image_root, "@%s_urls.json" % username)
        urls = self.__load_urls(file_path_urls)

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
    def __get_image_dir():
        # root=server/drawingapp
        root, folder = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        # root=server
        root, folder = os.path.split(root)
        # server/static/images のディレクトリに設定
        image_dir = os.path.join(root, "static", "images")

        # jupyter版
        #image_dir = os.path.join(os.getcwd(), "server", "static", "images")
        
        return image_dir


if __name__=='__main__':

    downloader = ImageDownloader()

    usernames = [
        "sakauchi0",
        "wttn3tpkt",
        ]

    for username in usernames:
        downloader.download_images(username)

