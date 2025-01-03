from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('adm/', views.adm_view, name='adm'),
    path('stf/', views.stf_view, name='stf'),
    path('usr/', views.usr_view, name='usr'),
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/edit/<int:eid>/', views.edit_event, name='edit_event'),
    path('events/delete/<int:eid>/', views.delete_event, name='delete_event'),
    path('user/<uuid:uid>/toggle/', views.toggle_staff, name='toggle_staff'),
    path('setup/', views.setup, name='setup'),
    path('user/<uuid:uid>/toggle-admin/', views.toggle_admin, name='toggle_admin'),
    path('account/', views.account, name='account'),
    path('account/delete/', views.account_delete, name='account_delete'),
    path('about/', views.about, name='about'),
    path('logout/', views.logout_view, name='logout'),
    path('save-theme/', views.save_theme, name='save_theme'),
    path('membership/apply/', views.apply_membership, name='apply_membership'),
    path('membership/status/', views.membership_status, name='membership_status'),
    path('memberships/', views.manage_memberships, name='manage_memberships'),
    path('memberships/<int:mid>/', views.membership_detail, name='membership_detail'),
    path('memberships/<int:mid>/verify/', views.verify_payment, name='verify_payment'),
    path('memberships/<int:mid>/delete/', views.membership_delete, name='membership_delete'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
