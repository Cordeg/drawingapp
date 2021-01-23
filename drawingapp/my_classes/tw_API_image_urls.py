import urllib3
import json
import os
from datetime import datetime, timedelta
from config import BEARER_TOKEN

from pprint import pprint


class ImageURLs:
    """
    Twitter APIを叩いて投稿画像のURLを取得する。
    関数型っぽくなるよう心掛ける。
    """
    
    def __init__(self):
        self.http = urllib3.PoolManager()
        self.key  = BEARER_TOKEN
        
    
    def query_users_by(self, query_param={}):
        url = 'https://api.twitter.com/2/users/by'
        req = self.http.request('GET',
                            url,
                            headers= {'Authorization': 'Bearer ' + self.key},
                            fields = query_param
                          )

        result = json.loads(req.data)
        if (req.status == 200):
            return result
        else:
            print(req.status)
            return result['errors']
    
    
    def get_users_info(self, usernames):
        """
        query_users_byからデータを取ってきてuser_idからusernameへの辞書を返す。
        return: {user_id1: username1, user_id2: username2, ...}
        """
        params = {
            'usernames' : ','.join(usernames)
        }
        data = self.query_users_by(params)
        
        return {d['id']: d['username'] for d in data['data']}
    
    
    def query_tweets_by_user_id(self, user_id, query_params={}):
        url = 'https://api.twitter.com/2/users/' + str(user_id) + '/tweets'
        req = self.http.request('GET',
                            url,
                            headers= {'Authorization': 'Bearer ' + self.key},
                            fields = query_params
                          )

        result = json.loads(req.data)
        if (req.status == 200):
            return result
        else:
            print(req.status)
            return result['errors']
        
        
    def export_image_urls(self, username, user_id, days=366):
        """
        ・end_time, start_timeの変数を保持する。適時更新する。
        ・file_path_date, file_path_urlsを作る。
        ・file_path_urlsに画像のURLを追加する。
        　予顕：このURLから画像を取得するのは別のクラスが行う。取得したURLはこのファイルから削除する。
        ・paramsを作るときに、timedelta(seconds=1)する。
        """
        
        # ファイルの場所と名前を指定
        image_root = self.__get_image_dir()
        file_path_date = os.path.join(image_root, "@%s_date.json" % username)
        file_path_urls = os.path.join(image_root, "@%s_urls.json" % username)
        
        # ツイートの最大/最小時刻
        end_time, start_time = self.__load_dates(file_path_date)
        
        urls = self.__load_urls(file_path_urls)
        
        if end_time==None:
            """
            このときstart_timeもNoneである。
            """
            end_time = datetime.today()
            start_time = end_time - timedelta(days=days)
            
            end_time = self.str_from_datetime(end_time)
            start_time = self.str_from_datetime(start_time)
            
            # end_time, start_time, new_urlsを取得
            new_urls, end_time, start_time = self.get_image_urls(user_id, end_time, start_time)
            if new_urls:
                urls = new_urls + urls
                # export
                self.__export_dates(end_time, start_time, file_path_date)
                self.__export_urls(urls, file_path_urls)

        else:
            # 現在の時間を新たなend_timeに。
            new_end_time = datetime.today()
            new_end_time = self.str_from_datetime(new_end_time)
            
            # 現在から end_time までの urls を取得し、end_time と urls を更新。start_timeは更新しない。
            new_urls, tmp_end_time, _ = self.get_image_urls(user_id, new_end_time, end_time)
            if new_urls:
                urls = new_urls + urls
                # export
                # end_time を tmp_end_time に更新する
                self.__export_dates(tmp_end_time, start_time, file_path_date)
                self.__export_urls(urls, file_path_urls)
            
            if start_time != 'got_last_tweet' and timedelta(days=days) > datetime.today() - self.datetime_from_str(start_time):
                """
                daysの範囲がstart_timeを超えていたとき。start_time から today - days までのurlsを取得する。
                """
                new_start_time = datetime.today() - timedelta(days=days)
                new_start_time = self.str_from_datetime(new_start_time)
                
                # start_time から today - days までの urls を取得し、start_time, urls を更新。
                new_urls, _, tmp_start_time = self.get_image_urls(user_id, start_time, new_start_time)
                if new_urls:
                    urls = urls + new_urls
                    # export
                    # start_time を tmp_start_time に更新する
                    self.__export_dates(end_time, tmp_start_time, file_path_date)
                    self.__export_urls(urls, file_path_urls)        
            
    
    def get_image_urls(self, user_id, end_time, start_time):
        """
        end_timeからstart_timeまでのツイートを取得し、image_urlsを抽出する。先頭と末尾のツイートからend_timeとstart_timeを計算する。
        return: urls, end_time, start_time
        """
        # ツイートの重複をなくすため、１秒だけずらす。
        fixed_end_time = self.str_from_datetime(self.datetime_from_str(end_time) - timedelta(seconds=1))
        fixed_start_time = self.str_from_datetime(self.datetime_from_str(start_time) + timedelta(seconds=1))
        # urls
        urls = []

        params = {
            'expansions' :'attachments.media_keys',
            'media.fields' : 'url,type',
            'tweet.fields' : 'created_at',
            'exclude' : 'retweets,replies',
            'end_time' : fixed_end_time,
            'start_time' : fixed_start_time,
            'max_results' : 100,
        }
        
        # image_urls 等を取得。
        image_urls, tmp_end_time, tmp_start_time, next_token = self.__get_tweets_info(user_id, params)
        urls = image_urls
        # 取得したツイートのうち、最大の end_time を max_end_time, 最小の start_time を min_start_time とする。
        # 期間内にツイートが存在しない場合は None となる。
        max_end_time = tmp_end_time
        min_start_time = tmp_start_time
        
        while(True):
            
            if next_token:
                params = {
                    'expansions' :'attachments.media_keys',
                    'media.fields' : 'url,type',
                    'tweet.fields' : 'created_at',
                    'exclude' : 'retweets,replies',
                    'start_time' : fixed_start_time,
                    'max_results' : 100,
                    'pagination_token' : next_token,
                }
                
                # image_urls 等を取得。
                image_urls, tmp_end_time, tmp_start_time, next_token = self.__get_tweets_info(user_id, params)
                urls += image_urls
                # max_end_time を更新。mp_end_time が None でないとき、tmp_end_time と max_end_time のうち最大値を採用。
                if tmp_end_time:
                    if self.datetime_from_str(tmp_end_time) > self.datetime_from_str(max_end_time):
                        max_end_time = tmp_end_time
                # min_start_time を更新。tmp_start_time が None でないとき、tmp_start_time と min_start_time のうち最小値を採用。
                if tmp_start_time:
                    if self.datetime_from_str(tmp_start_time) < self.datetime_from_str(min_start_time):
                        min_start_time = tmp_start_time
                
            else:
                break
        
        return urls, max_end_time, min_start_time
        
            
    def __get_tweets_info(self, user_id, params):
        
        tweets = self.query_tweets_by_user_id(user_id, params)
        
        # image urls を抽出
        image_urls = []
        """
        image_urls の要素は [created_at ('2020-12-23T19:12:22.000Z'のような文字列）, url] としたいが、
        created_at は tweets['data'] に、url は tweets['includes']['media'] にあるので以下のようにする。
        """
        if 'data' in tweets and 'includes' in tweets:            
            tweets_data = tweets['data']
            tweets_media = tweets['includes']['media']
            
            # media のうち、type が photo のものからなる、media_key から url への辞書。
            key_url_dict = {x['media_key']: x['url'] for x in tweets['includes']['media'] if x['type']=='photo'}
            
            for tw in tweets_data:
                # attachments を持つとき、media_keys を持つ。上で定義したkey_url_dictから検索し、created_at と url の組を作る。
                if 'attachments' in tw:
                    media_keys = tw['attachments']['media_keys']
                    created_at = tw['created_at']
                    for key in media_keys:
                        image_urls.append([key_url_dict[key], created_at])

                    
        # この tweets の先頭と末尾のツイートから日時を取得
        if 'data' in tweets:
            tmp_end_time = tweets['data'][0]['created_at']
            tmp_start_time = tweets['data'][-1]['created_at']
            # 2021-01-21T06:00:45.000Z という形式なので、2021-01-21T06:00:45Zという形式に変える。
            tmp_end_time = tmp_end_time[:-5] + "Z"
            tmp_start_time = tmp_start_time[:-5] + "Z"
        else:
            tmp_end_time = None
            tmp_start_time = None
        
        # next_token。pagination_tokenに設定することで、次のページのtweetsが得られる。
        if 'next_token' in tweets['meta']:
            next_token = tweets['meta']['next_token']
        else:
            next_token = None
            start_time = 'got_last_tweet'
        
        return image_urls, tmp_end_time, tmp_start_time, next_token
        
    
    @staticmethod
    def __load_dates(path):
        """
        path から end_time, start_time を取得する。
        """
        if os.path.exists(path):
            with open(path, 'r') as f:
                end_time, start_time = json.load(f)
        else:
            end_time, start_time = [None, None]
        
        return end_time, start_time
    
    
    @staticmethod
    def __export_dates(end_time, start_time, path):
        """
        path に end_time, start_time を書き込む。
        """
        with open(path, 'w') as f:
            json.dump([end_time, start_time], f)
    
    
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
    def __export_urls(urls, path):
        """
        path に urls を書き込む。
        """
        with open(path, 'w') as f:
            json.dump(urls, f)
            
        
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


    @staticmethod
    def str_from_datetime(dt):
        # YYYY-MM-DDTHH:mm:ssZ
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        
        return dt.strftime(date_format)

    
    @staticmethod
    def datetime_from_str(s):
        # YYYY-MM-DDTHH:mm:ssZ
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        
        return datetime.strptime(s, date_format)
            

if __name__=='__main__':

    usernames = [
        "sakauchi0",
        "wttn3tpkt",
        ]

    cl = ImageURLs()
    user_info = cl.get_users_info(usernames)
    print(user_info)

    for user_id in user_info:
        username = user_info[user_id]

        # username の image_urls を取得しエクスポート
        cl.export_image_urls(username, user_id, days=300)