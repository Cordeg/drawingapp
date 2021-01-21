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
        
        if folders==None:
            current_path = self.image_dir
            folders = self.get_folders(current_path)
        
        # ランダムにフォルダを取得
        folder = random.choice(folders)
        # 取得したフォルダのパスを取得
        current_path = os.path.join(current_path, folder)
        
        files = self.get_files(current_path)
        file = random.choice(files)
        
        self.image_path = "images/%s/%s" % (folder, file)
        
        return self.image_path
        
        
    def get_folders(self, path):
        path, folders, files = next(walk(path))
        return folders
    
    def get_files(self, path):
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