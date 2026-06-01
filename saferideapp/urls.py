from django.urls import path
from . import views

urlpatterns = [

    path('', views.index),
    path('index.html', views.index),

    # LOGIN
    path('login/', views.Login),
    path('LoginAction', views.LoginAction),

    # SIGNUP
    path('signup/', views.Signup),
    path('SignupAction', views.SignupAction),

    # USER DASHBOARD
    path('user_screen/', views.UserScreen),

    # DRIVER DASHBOARD
    path('driver_screen/', views.DriverScreen),

    # DRIVER LOCATION
    path('driver_location/', views.DriverLocation),
    path('DriverLocationAction', views.DriverLocationAction),

    # BOOK RIDE
    path('share_location/', views.ShareLocation),
    path('ShareLocationAction', views.ShareLocationAction),

    # SEND REQUEST
    path('send_request/<str:driver>/', views.SendRequest),

    # DRIVER REQUESTS
    path('driver_requests/', views.DriverRequests),

    # RIDE FLOW
    path('accept/<int:ride_id>/', views.AcceptRide),
    path('start/<int:ride_id>/', views.StartRide),
    path('complete/<int:ride_id>/', views.CompleteRide),

    # ✅ CANCEL RIDE
    path('cancel/<int:ride_id>/', views.CancelRide),

    # ALERT
    path('panic/', views.Panic),
    path('PanicAction', views.PanicAction),

    # HISTORY
    path('past_rides/', views.PastRides),

    # FEEDBACK
    path('feedback/<int:ride_id>/', views.Feedback),

    # LOGOUT
    path('logout/', views.Logout),
]