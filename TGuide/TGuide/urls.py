from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from main import views, views1, journey_views
from main.forms import EmailLoginForm
from main.views import search_place


urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    #path('', auth_views.LoginView.as_view(template_name='login.html', authentication_form=EmailLoginForm), name='home'),
    path('', views.home, name='home'),  # Home page
    path('get_trip_plan/', views.dashboard, name='get_trip_plan'),  # Placeholder for trip planning
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('search/', search_place, name='search_place'),
    path('plan_trip/', views.plan_trip, name='plan_trip'),
    path("trip_result/", views.trip_result, name="trip_result"),
    path('get_place_details/', views.get_place_details, name='get_place_details'),
    path('get_spots_details/', views.get_spots_details, name='get_spots_details'),
    path('fetch_hotels/', views.fetch_hotels, name='fetch_hotels'),
    path('get_bot_response/', views.get_bot_response, name='get_bot_response'),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('verify_otp_ajax/', views.verify_otp_ajax, name='verify_otp_ajax'),
   
    


    #views1
    path("save_trip_plan/", views1.save_trip_plan, name="save_trip_plan"),
    path("saved_plans/<int:plan_id>/", views1.view_saved_plans, name="view_saved_plans"),
    path("view_trip_plans/", views1.view_trip_plans, name="view_trip_plans"),
    path("view_trip_plan/<int:plan_id>/", views1.view_trip_plan_detail, name="view_trip_plan_detail"),
    path("delete_trip_plan/<int:plan_id>/", views1.delete_trip_plan, name="delete_trip_plan"),
    path('mark_trip_completed/', views1.mark_trip_completed, name='mark_trip_completed'),
    path('update-profile/', views1.update_profile, name='update_profile'),
    path('edit_profile/', views1.edit_profile, name='edit_profile'),
    path('profile/', views1.profile, name='profile'),
    path('contact/', views1.contact, name='contact'),
    path('faqs/', views1.faqs, name='faqs'),
    path('info1/', views1.info1, name='info1'),
    path('info2/', views1.info2, name='info2'),
    path('load/', views1.load, name='load'),
    path('emergency/', views1.emergency, name='emergency'),
    path('get_spots/<str:district_name>/', views1.get_tourist_spots_by_district, name='get_spots'),
    


    #journey_views
    path("start_journey/<int:plan_id>/", journey_views.start_journey, name="start_journey"),
    # In urls.py:
    


    path("test", views.test, name="test"),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)