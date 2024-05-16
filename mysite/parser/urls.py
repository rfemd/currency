from django.urls import path

from .views import *

app_name = "parser"

urlpatterns = [
    path("",HomeView.as_view(), name="home"),
    path("for_parsing/",ParseInputView.as_view(), name="parse_user_input"),
    path("for_chart/",ChartInputView.as_view(), name="chart_user_input"),
    path("start_parsing/",ParsingView.as_view(), name="parsing"),
    path("chart/",ChartView.as_view(), name="chart_display"),
]
