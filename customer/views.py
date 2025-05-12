from rest_framework import viewsets
from .models import Employer, Customer
from .serializers import EmployerSerializer, CustomerSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
API_KEY = "863e3f5d-dc99-11ef-8b17-0200cd936042"  

class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

@api_view(['POST'])
def send_otp_view(request):
    phone = request.data.get("phone")
    if not phone or not phone.isdigit() or len(phone) != 10:
        return Response({"detail": "Invalid phone number."}, status=400)

    try:
        url = f"https://2factor.in/API/V1/{API_KEY}/SMS/{phone}/AUTOGEN"
        response = requests.get(url)
        print("2Factor response:", response.status_code, response.text)  # 🐞 debug line
        data = response.json()

        if data.get("Status") == "Success":
            return Response({"session_id": data.get("Details")})
        return Response({"detail": data.get("Details", "Failed to send OTP.")}, status=500)
    except Exception as e:
        return Response({"detail": f"Unexpected error: {str(e)}"}, status=500)

@api_view(['POST'])
def verify_otp_view(request):
    session_id = request.data.get("session_id")
    otp = request.data.get("otp")
    phone = request.data.get("phone")
    name = request.data.get("name")  # optional
    email = request.data.get("email")  # optional

    if not session_id or not otp or not phone:
        return Response({"detail": "Phone, Session ID and OTP are required."}, status=400)

    # ✅ OTP verification
    url = f"https://2factor.in/API/V1/{API_KEY}/SMS/VERIFY/{session_id}/{otp}"
    response = requests.get(url)
    data = response.json()

    if data.get("Status") != "Success":
        return Response({"detail": "Invalid OTP"}, status=400)

    # ✅ Get or create customer
    customer, created = Customer.objects.get_or_create(phone=phone)

    # ✅ If new user, or if you want to update info:
    if created or not customer.name or not customer.email:
        if name:
            customer.name = name
        if email:
            customer.email = email
        customer.save()

    return Response({
        "detail": "OTP Verified",
        "customer_id": customer.id,
        "phone": customer.phone,
        "name": customer.name,
        "email": customer.email,
        "new_user": created
    }, status=200)