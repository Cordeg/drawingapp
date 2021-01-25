import os
from os import walk
import random

class ImageHolder:
    
    def __init__(self):
        
        # root=server/drawingapp
        root, folder = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        # root=server
        root, folder = os.path.split(root)
        # server/static/images のディレクトリに設定
        self.image_dir = os.path.join(root, "static", "images")

        self.image_path = None
        self.set_random_image()
        
        self.history = []
        self.update_history()
            
    
    def set_random_image(self, folders=None):
        """
        ランダムにfolder_nameとfile_nameを取得し、images/folder_name/file_nameの形式で返す。
        """
        
        # folders が None のときは全フォルダを取得
        if folders==None:
            folders = self.get_folders(self.image_dir)
            # jpg or png を含むフォルダのみセレクト
            folders = [x for x in folders if self.has_image(x)]
            # フォルダ名に '#new' を含まない
            folders = [x for x in folders if '#new' not in x]
        
        # ランダムにフォルダを取得
        folder = random.choice(folders)
        # 取得したフォルダのパスを取得
        current_path = os.path.join(self.image_dir, folder)
        
        files = self.get_files(current_path)
        files = self.select_images(files)
        file = random.choice(files)
        
        self.image_path = "images/%s/%s" % (folder, file)
        
        return self.image_path
        

    def has_image(self, dir_name):
        """
        self.image_dir/dir_name に画像ファイルがあればTrue, なければFalseを返す。
        """
        path = os.path.join(self.image_dir, dir_name)
        for filename in self.get_files(path):
            if '.png' in filename or '.jpeg' in filename or '.jpg' in filename:
                return True

        return False


    @staticmethod
    def select_images(filenames):
        """
        filenames のリストの中から、画像ファイルのみ取り出す。
        """
        filenames = [x for x in filenames if '.png' in x or '.jpeg' in x or '.jpg' in x]

        return filenames


    @staticmethod
    def get_folders(path):
        path, folders, files = next(walk(path))
        return folders
    

    @staticmethod
    def get_files(path):
        path, folders, files = next(walk(path))
        return files
    

    def update_history(self):
        if self.history:
            # 重複しているときには追加しない
            if self.history[-1]==self.image_path:
                return 0
        
        self.history.append(self.image_path)


if __name__=='__main__':
    
    image_holder = ImageHolder()
    print(image_holder.image_path)

    image_holder.update_history()
    print(image_holder.set_random_image())
    
    image_holder.update_history()
    print(image_holder.history)