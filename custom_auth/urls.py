from django.urls import path
from .views import create_user, login_user, get_active_labs, get_all_labs, start_lab, rejoin_lab, get_all_emails, get_all_collaborators_by_email, accept_collab, get_email_and_verification, verify_lab_from_socket
urlpatterns = [
    path("create_user/", create_user, name="create_user"),  # Create user endpoint
    path("login_user/", login_user, name="login_user"),     # Login user endpoint
    path("get_active_labs/", get_active_labs, name="get_active_labs"),  # Get active labs endpoint
    path("get_all_labs/", get_all_labs, name="get_all_labs"),  # Get all labs endpoint
    path("start_lab/", start_lab, name="start_lab"),  # Start lab endpoint
    path("rejoin_lab/", rejoin_lab, name="rejoin_lab"),  # Rejoin lab endpoint
    path("get_all_emails/", get_all_emails, name="get_all_emails"),  # Get all emails endpoint
    path("get_all_collaborators_by_email/", get_all_collaborators_by_email, name="get_all_collaborators_by_email"),  # Get all collaborators by email endpoint
    path("accept_collaboration/", accept_collab, name="accept_collaboration"),  # Accept collaboration endpoint
    path("get_email_and_verification/", get_email_and_verification, name="get_email_and_verification"), 
    path("verify_lab_from_socket/", verify_lab_from_socket, name="verify_lab_from_socket"),
]
