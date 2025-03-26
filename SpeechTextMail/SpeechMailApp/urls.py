from django.urls import path

from . import views

urlpatterns = [path("indexPage.html", views.indexPage, name="indexPage"),
	       path('UserLogin', views.UserLogin, name="UserLogin"),
	       path('Signup', views.Signup, name="Signup"),
	       path('SignupAction', views.SignupAction, name="SignupAction"),
	       path('ViewMails', views.ViewMails, name="ViewMails"),
	       path('ComposeMails', views.ComposeMails, name="ComposeMails"),
	       path('Readout', views.Readout, name="Readout"),
]
