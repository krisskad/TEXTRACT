from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from .models import ImageRecord
from .permissions import IsAuthenticated
from .serializers import ImageSerializer
from .pagination import CustomPagination
from pathlib import Path
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
from .src.slicer import image_slicer
from .src.extract_text import detect_text


class Process_Image(ListCreateAPIView):
    serializer_class = ImageRecord
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    # Take base64 string and save into user_dir
    def save(self, image64, filename):
        starter = image64.find(',')
        image_data = image64[starter + 1:]
        image_data = bytes(image_data, encoding="ascii")
        im = Image.open(BytesIO(base64.b64decode(image_data)))
        im.save(filename)

    # Create a new Image
    def post(self, request):
        # Get Jsondata from user
        json_data = request.data
        image64 = json_data['Image']

        # create directories for temp data
        user_dir = "uploads/" + str(request.user) + "/"
        user_dir_bin = user_dir + "bin/"
        Path(user_dir).mkdir(parents=True, exist_ok=True)
        Path(user_dir_bin).mkdir(parents=True, exist_ok=True)

        # datetime object containing current date and time
        now = datetime.now()
        now = str(now).replace(" ","")
        now = str(now).replace(".", "")
        now = str(now).replace("-", "")
        now = str(now).replace(":", "")

        # convert base64 string into image and save into user dir
        image_name = str(request.user) + str(now) + ".png"
        image_file_location = str(user_dir) + str(image_name)
        self.save(image64, image_file_location)

        #store image path into database
        serializer = ImageSerializer(data={"Image": image_file_location})

        if serializer.is_valid():
            # store owner of the token into database
            serializer.save(creator=request.user)

            # slice all the boxes and save into user_dir_bin
            image_slicer(image_file_location, user_dir_bin)

            # get all text into json format
            json_data = detect_text(user_dir_bin)
            # print(json_data)

            return Response(json_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
