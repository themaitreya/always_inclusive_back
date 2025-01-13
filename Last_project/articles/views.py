from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Article
from .serializers import ArticleSerializer


# Create your views here.

# 서울 자가에 대기업 다니는 김 부장 이야기
# 운명을 보는 회사원
# 재벌집 막내아들
# 신입사원 강 회장
# 상남자



# @api_view(["GET"])
# def json_drf(request):
#     articles = Article.objects.all()
#     serializer = ArticleSerializer(articles, many=True)
#     return Response(serializer.data)
