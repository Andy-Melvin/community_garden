from django.urls import path
from . import views
from .views import analytics_dashboard, export_analytics_csv

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('plots/', views.plot_list, name='plot_list'),
    path('plots/apply/<int:plot_id>/', views.apply_for_plot, name='apply_for_plot'),
    path('events/', views.event_list, name='event_list'),
    path('events/signup/<int:event_id>/', views.sign_up_for_event, name='sign_up_for_event'),
    path('crops/', views.crop_record_list, name='crop_record_list'),
    path('crops/add/', views.add_crop_record, name='add_crop_record'),
            path('analytics/', analytics_dashboard, name='analytics_dashboard'),
    path('analytics/export/', export_analytics_csv, name='export_analytics_csv'),
    path('plots/chart/', views.plot_chart_view, name='plot_chart'),
]
