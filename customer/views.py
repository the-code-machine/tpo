from rest_framework import viewsets
from .models import  Customer,SharedFirm
from .serializers import CustomerSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
from subscription.models import Subscription
from datetime import date
from .serializers import CustomerSyncToggleSerializer
from sync.models import Firm
API_KEY = "863e3f5d-dc99-11ef-8b17-0200cd936042"  


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

    # ✅ Update name/email if provided
    if name:
        customer.name = name
    if email:
        customer.email = email
    customer.save()

    # ✅ Assign Free Trial if new
    # ✅ Assign Free Trial if new
    if created:
        try:
            free_plan = Plan.objects.get(
                name__iexact="Free Trial",
                price=0,
                duration_days=7
            )
            Subscription.objects.create(
                customer=customer,
                plan=free_plan,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=free_plan.duration_days),
                is_active=True
            )
        except Plan.DoesNotExist:
            return Response({"detail": "Valid Free Trial plan not found"}, status=500)

    return Response({
        "detail": "OTP Verified",
        "customer_id": customer.id,
        "phone": customer.phone,
        "name": customer.name,
        "email": customer.email,
        "new_user": created
    }, status=200)


@api_view(['GET'])
def get_user_info_view(request):
    phone = request.query_params.get("phone")  # or use customer_id

    if not phone:
        return Response({"detail": "Phone number is required."}, status=400)

    try:
        customer = Customer.objects.get(phone=phone)
    except Customer.DoesNotExist:
        return Response({"detail": "Customer not found."}, status=404)

    # Get latest subscription
    subscription = customer.subscriptions.order_by('-end_date').first()

    subscription_data = None
    if subscription:
        # Update status if expired
        if subscription.end_date < date.today():
            subscription.is_active = False
            subscription.save()

        subscription_data = {
            "plan_name": subscription.plan.name,
            "description": subscription.plan.description,
            "start_date": subscription.start_date,
            "end_date": subscription.end_date,
            "is_active": subscription.is_active,
            "price": float(subscription.plan.price),
            "discount": float(subscription.plan.discount),
            "final_price": float(subscription.plan.discounted_price),
        }

    return Response({
        "customer_id": customer.id,
        "name": customer.name,
        "phone": customer.phone,
        "email": customer.email,
        "sync_enabled":customer.sync_enabled,
        "subscription": subscription_data
    })

@api_view(["POST"])
def toggle_customer_sync(request):
    phone = request.data.get("phone")
    if not phone:
        return Response({"error": "Phone number is required."}, status=400)

    customer = Customer.objects.filter(phone=phone).first()
    if not customer:
        return Response({"error": "Customer not found."}, status=404)

    serializer = CustomerSyncToggleSerializer(customer, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"status": "success", "sync_enabled": serializer.data["sync_enabled"]})
    else:
        return Response(serializer.errors, status=400)


@api_view(['POST'])
def share_firm_to_customer(request):
    phone = request.data.get("phone")
    firm_id = request.data.get("firm_id")
    role = request.data.get("role")

    if not phone or not firm_id:
        return Response({"error": "phone and firm_id required"}, status=400)

    try:
        customer = Customer.objects.get(phone=phone)
    except Customer.DoesNotExist:
        return Response({"error": "Customer with this phone does not exist"}, status=404)

    firm = Firm.objects.filter(id=firm_id).first()
    if not firm:
        return Response({"error": "Firm not found"}, status=404)

    SharedFirm.objects.update_or_create(firm=firm, customer=customer, defaults={"role": role})
    return Response({"status": "success", "message": "Firm shared successfully"})


@api_view(['GET'])
def get_firm_users(request):
    firm_id = request.query_params.get('firmId')
    if not firm_id:
        return Response({"error": "firmId is required"}, status=400)

    shared_entries = SharedFirm.objects.filter(firm_id=firm_id).select_related('customer')
    users = [{
        "name": entry.customer.name,
        "phone": entry.customer.phone,
        "email": entry.customer.email,
        "role": entry.role,
    } for entry in shared_entries]

    return Response({"status": "success", "synced_users": users})


@api_view(['POST'])
def change_shared_role(request):
    phone = request.data.get("phone")
    firm_id = request.data.get("firm_id")
    new_role = request.data.get("role")

    if not (phone and firm_id and new_role):
        return Response({"error": "phone, firm_id and role are required"}, status=400)

    try:
        customer = Customer.objects.get(phone=phone)
        shared = SharedFirm.objects.get(customer=customer, firm_id=firm_id)
        shared.role = new_role
        shared.save()
        return Response({"status": "success", "message": "Role updated"})
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)
    except SharedFirm.DoesNotExist:
        return Response({"error": "SharedFirm not found"}, status=404)

@api_view(['POST'])
def remove_shared_firm(request):
    phone = request.data.get("phone")
    firm_id = request.data.get("firm_id")

    if not (phone and firm_id):
        return Response({"error": "phone and firm_id are required"}, status=400)

    try:
        customer = Customer.objects.get(phone=phone)
        shared = SharedFirm.objects.get(customer=customer, firm_id=firm_id)
        shared.delete()
        return Response({"status": "success", "message": "User removed from shared firm"})
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)
    except SharedFirm.DoesNotExist:
        return Response({"error": "SharedFirm not found"}, status=404)

@api_view(['GET'])
def get_shared_firms_by_phone(request):
    phone = request.query_params.get("phone")

    if not phone:
        return Response({"error": "phone is required"}, status=400)

    try:
        customer = Customer.objects.get(phone=phone)
        shared_firms = SharedFirm.objects.filter(customer=customer).select_related('firm')
        data = [
            {
                "firm_id": s.firm.id,
                "firm_name": s.firm.name,
                "role": s.role
            }
            for s in shared_firms
        ]
        return Response({"status": "success", "shared_firms": data})
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)
