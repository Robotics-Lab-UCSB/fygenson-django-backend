from django.contrib.auth import get_user_model, authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json
from .models import LabsActive, Collaboration, CustomUser
from functools import wraps
from datetime import datetime, timedelta

# Dynamically get the custom user model
User = get_user_model()

def api_login_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapped_view

@csrf_exempt
def create_user(request):
    if request.method == "POST":
        try:
            # Parse JSON data
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")

            # Validate input
            if not email or not password:
                return JsonResponse({"error": "Email and password are required"}, status=400)

            # Check if the user already exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "User with this email already exists"}, status=400)

            # Create the user using the custom user model
            user = User.objects.create_user(email=email, password=password)
            return JsonResponse({"message": f"User with email {user.email} created successfully"}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def login_user(request):
    if request.method == "POST":
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")

            # Validate input
            if not email or not password:
                return JsonResponse({"error": "Email and password are required"}, status=400)

            # Authenticate the user
            user = authenticate(request, username=email, password=password)
            if user is not None:
                # Log the user in (create session)
                login(request, user)
                return JsonResponse({"message": "Login successful"}, status=200)
            else:
                return JsonResponse({"error": "Invalid email or password"}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
@api_login_required
def get_active_labs(request):
    if request.method == "GET":
        try:
            # Print all received headers
            print("Request Headers:")
            for header, value in request.headers.items():
                print(f"{header}: {value}")

            # Get the logged-in user's email
            user_email = request.user.email
            print("Authenticated User Email:", user_email)

            # Query labs associated with the user
            # labs = LabsActive.objects.filter(started_by__email=user_email)
            # lab_details = [{"lab_id": lab.lab_id, "lab_name": lab.lab_name} for lab in labs]
            
            labs_shared = Collaboration.objects.filter(collab_email=user_email, accepted=True)
            shared_lab_details = [{"owner_email": lab.lab.started_by.email,"lab_id": lab.lab.lab_id, "lab_name": lab.lab.lab_name, "permission": lab.permission} for lab in labs_shared] #subject to change for owner_email

            # Return the lab details
            return JsonResponse({"labs_shared": shared_lab_details}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
@api_login_required
def get_all_labs(request):
    if request.method == "GET":
        try:
            # Print all received headers
            print("Request Headers:")
            for header, value in request.headers.items():
                print(f"{header}: {value}")

            # Get the logged-in user's email
            user_email = request.user.email
            print("Authenticated User Email:", user_email)

            # Define all labs
            all_lab_IDs = [
                "photoeletriceffect1", "photoeletriceffect2", "atomicsepctroscopy1", "atomicsepctroscopy2", 
                "frankhertz1", "frankhertz2", "diffractionandinterference1", "diffractionandinterference2", 
                "gammaradiationabsorption1", "gammaradiationabsorption2"
            ]
            all_lab_names = [
                "Photoelectric Effect 1", "Photoelectric Effect 2", "Atomic Spectroscopy 1", "Atomic Spectroscopy 2", 
                "Frank-Hertz 1", "Frank-Hertz 2", "Diffraction and Interference 1", "Diffraction and Interference 2", 
                "Gamma Radiation Absorption 1", "Gamma Radiation Absorption 2"
            ]
            time_remaining = [0] * len(all_lab_IDs)

            # Get active lab IDs
            active_lab_ids = LabsActive.objects.values_list('lab_id', flat=True)
            active_lab_ids_list = list(active_lab_ids)
            print("active labs: ", active_lab_ids)
            
            labs_start_by_user = LabsActive.objects.filter(started_by__email=user_email).values_list('lab_id', flat=True)
            labs_start_by_user_list = list(labs_start_by_user)

            labs_owned = [False] * 10
            # Update time_remaining logic

            for i in range(len(all_lab_IDs)):
                if all_lab_IDs[i] not in active_lab_ids_list:
                    time_remaining[i] = 0  #TODO: Placeholder logic for time remaining
                else:
                    if all_lab_IDs[i] in labs_start_by_user_list:
                        labs_owned[i] = True
                    time_remaining[i] = 1000 #TODO: Get the remaining time of each lab
                # if all_lab_IDs[i] == "frankhertz1":
                #     time_remaining[i] = 0

            labs_with_time = [
                {"lab_id": all_lab_IDs[i], "name": all_lab_names[i], "time_remaining": time_remaining[i], "owned_by_user": labs_owned[i]}
                for i in range(len(all_lab_names))
            ]

            # Return the lab details
            return JsonResponse({"labs": labs_with_time}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
@api_login_required
def start_lab(request):
    if request.method == "POST":
        try:
            # Parse JSON data
            data = json.loads(request.body)
            lab_id = data.get("lab_id")
            lab_name = data.get("lab_name")
            # allow_collab = data.get("allow_collab")
            collaborators = data.get("collaborators") # List of collab emails 
            time_restraint = data.get("time_restraint")

            # Validate input
            if not lab_id or not lab_name:
                return JsonResponse({"error": "Lab ID and lab name are required", "success": False}, status=400)
            
            # Get the logged-in user's email
            user_email = request.user.email
            # Check if the lab is already active
            if LabsActive.objects.filter(lab_id=lab_id).exists():
                return JsonResponse({"error": "Lab is already active", "success": False}, status=400)

            # Start the lab
            start_time = datetime.now()

            user = CustomUser.objects.get(email=user_email)  # Retrieve the user instance
            lab = LabsActive.objects.create(
                lab_id=lab_id,
                lab_name=lab_name,
                started_by=user,
                allow_collab=True,
                start_time=start_time,
                max_time=timedelta(hours=time_restraint),
            )
            
            if collaborators:
                for email in collaborators:
                    # Optionally, validate email format
                    Collaboration.objects.create(
                        lab=lab,
                        collab_email=email,
                        permission='write',  # TODO: Default permission to write
                        accepted=False,  # Default to not accepted until confirmed
                    )

            # Save the verification token in the user's session
            request.session['lab_unique_id'] = lab.verification_token

            return JsonResponse({
                "message": f"Lab {lab.lab_name} started successfully",
                "verification_token": lab.verification_token, 
                "success": True, 
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON", "success": False}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e), "success": False}, status=500)

    return JsonResponse({"error": "Invalid request method", "success": False}, status=405)

@csrf_exempt
@api_login_required
def invite_person(request):
    if request.method == "POST":
        try:
            # Parse the request data
            data = json.loads(request.body)
            lab_id = data.get("lab_id")
            collab_email = data.get("collab_email")
            if collab_email == request.user.email:
                return JsonResponse({"error": "You can't invite yourself!"}, status=403)
            permission = data.get("permission", "read")  # Default permission to 'read'

            # Validate required fields
            if not lab_id or not collab_email:
                return JsonResponse({"error": "Lab ID and collaborator email are required."}, status=400)

            # Check if the logged-in user started the lab
            lab = LabsActive.objects.filter(lab_id=lab_id, started_by=request.user).first()
            if not lab:
                return JsonResponse({"error": "You are not the owner of this lab."}, status=403)

            # Add collaboration
            
            Collaboration.objects.create(
                lab=lab,
                collab_email=collab_email,
                permission=permission,
                accepted=False  # Default to not accepted
            )

            return JsonResponse({"success": f"{collab_email} invited to lab {lab.lab_name}."}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
@api_login_required
def accept_collab(request):
    if request.method == "POST":
        try:
            # Parse the request data
            data = json.loads(request.body)
            lab_id = data.get("lab_id")
            user_email = request.user.email  # Get the logged-in user's email

            # Validate required fields
            if not lab_id:
                return JsonResponse({"error": "Lab ID is required."}, status=400)

            # Check if the collaboration exists
            collaboration = Collaboration.objects.filter(
                lab__lab_id=lab_id,
                collab_email=user_email
            ).first()

            if not collaboration:
                return JsonResponse({"error": "No collaboration found for this lab and user."}, status=404)

            # Update the collaboration to accepted
            if (collaboration.accepted == True):
                return JsonResponse({"error": "Invite Expired"}, status=404)

            collaboration.accepted = True
            collaboration.save()

            return JsonResponse({"success": f"Collaboration for lab {lab_id} accepted by {user_email}."}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
@api_login_required
def rejoin_lab(request):
    if request.method == "POST":
        try:
            # Parse JSON data
            data = json.loads(request.body)
            lab_id = data.get("lab_id")

            # Validate input
            if not lab_id:
                return JsonResponse({"error": "Lab ID is required", "success": False}, status=400)

            # Get the logged-in user's email
            user_email = request.user.email

            # Check for owned lab
            lab = LabsActive.objects.filter(started_by__email=user_email, lab_id=lab_id).first()

            # If not found in owned labs, check in shared labs
            if not lab:
                collaboration = Collaboration.objects.filter(collab_email=user_email, lab__lab_id=lab_id, accepted=True).first()
                if collaboration:
                    lab = collaboration.lab  # Access the related lab

            # If no lab is found in either owned or shared
            if not lab:
                return JsonResponse({"error": "No access or lab not found", "success": False}, status=404)

            # Save the verification token in the user's session
            request.session['lab_unique_id'] = lab.verification_token

            return JsonResponse({
                "message": f"Lab '{lab.lab_name}' rejoined successfully",
                "verification_token": lab.verification_token,
                "success": True,
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON", "success": False}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e), "success": False}, status=500)

    return JsonResponse({"error": "Invalid request method", "success": False}, status=405)

@csrf_exempt
@api_login_required
def get_all_emails(request):
    if request.method == "GET":
        try:
            # Get all user emails
            emails = CustomUser.objects.exclude(email=request.user.email).values_list('email', flat=True)
            email_list = list(emails)

            return JsonResponse({"emails": email_list}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
@api_login_required
def get_all_collaborators_by_email(request):
    if request.method == "GET":
        try:
            # Get the logged-in user's email
            user_email = request.user.email

            # Get all lab IDs for collaborations associated with the user
            lab_ids = list(
                Collaboration.objects.filter(collab_email=user_email, accepted=False).values_list("lab__lab_id", flat=True)
            )
            
            if not lab_ids:
                return JsonResponse({"message": "No pending collaborations found."}, status=200)

            return JsonResponse({"lab_ids": lab_ids}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import LabsActive, Collaboration

@csrf_exempt
def verify_lab_from_socket(request):
    if request.method == "POST":
        try:
            # Parse request body
            data = json.loads(request.body)
            email = data.get("email")
            verification_token = data.get("verification_token")
            lab_id = data.get("lab_id")

            # Validate required fields
            if not (email and verification_token and lab_id):
                return JsonResponse({"success": False, "error": "Missing required fields"}, status=400)

            # Check if the lab exists under LabsActive
            lab = LabsActive.objects.filter(
                started_by__email=email,
                lab_id=lab_id,
                verification_token=verification_token
            ).first()

            if lab:
                return JsonResponse({"success": True}, status=200)

            # Check if the lab exists under Collaborations
            collaboration = Collaboration.objects.filter(
                collab_email=email,
                lab__lab_id=lab_id,
                lab__verification_token=verification_token,
                accepted=True
            ).first()

            if collaboration:
                return JsonResponse({"success": True}, status=200)

            # If neither exists, return failure
            return JsonResponse({"success": False, "error": "Lab not found or verification failed"}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON payload"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

@csrf_exempt
@api_login_required
def get_email_and_verification(request):
    if request.method == "POST":
        try:
            # Parse request body
            data = json.loads(request.body)
            lab_id = data.get("lab_id")

            # Retrieve user email
            user_email = request.user.email

            # Check if the lab exists in LabsActive
            lab = LabsActive.objects.filter(
                started_by__email=user_email,
                lab_id=lab_id
            ).first()

            if lab:
                return JsonResponse({
                    "verification_token": lab.verification_token,
                    "user_email": user_email,
                    "lab_id": lab.lab_id, 
                }, status=200)

            # Check if the lab exists in Collaborations
            collaboration = Collaboration.objects.filter(
                collab_email=user_email,
                accepted=True,
                lab__lab_id=lab_id
            ).first()

            if collaboration:
                return JsonResponse({
                    "verification_token": collaboration.lab.verification_token,
                    "user_email": user_email,
                    "lab_id": collaboration.lab.lab_id, 
                }, status=200)

            # If neither exists, return an error
            return JsonResponse({"error": "Lab not found or access denied"}, status=404)

        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
