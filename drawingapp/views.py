from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views import View
from django.urls import reverse

from drawingapp.my_classes import image_holder

holder = image_holder.ImageHolder()
print(holder.image_path)


class Display(View):
    def get(self, request, *args, **kwargs):
        """GETリクエスト用のメソッド"""
        self.content = {
            'image_path': holder.image_path #'images/@tkmiz/C_3pOZ0UMAAAf9u.jpg'
        }

        print("get")

        return render(request, 'drawingapp/display.html', self.content)

    def post(self, request, *args, **kwargs):
        """POSTリクエスト用のメソッド"""
        
        # holderの画像を更新
        holder.set_random_image()
        holder.update_history()

        self.content = {
            'image_path': holder.image_path #'images/@tkmiz/C_cFbqTXYAAWchy.jpg'
        }

        print("post")
        print(request.POST)

        if 'button_1' in request.POST:
            pass


        return redirect(reverse('app:display'))


display = Display.as_view()