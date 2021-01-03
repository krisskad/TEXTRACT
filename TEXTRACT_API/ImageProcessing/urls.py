from django.urls import include, path, re_path
from . import views

urlpatterns = [
    path('textract/',  # urls list all and create new one
         views.Process_Image.as_view(),
         name='Process_Image'
         )
]
