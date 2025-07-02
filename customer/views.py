from rest_framework import viewsets
from .models import  Customer,SharedFirm
from .serializers import CustomerSerializer,SharedFirmSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
from subscription.models import Subscription,Plan
from datetime import date, timedelta
from django.core.mail import send_mail
from django.core.cache import cache
import random
import string
from sync.models import Firm
API_KEY = "863e3f5d-dc99-11ef-8b17-0200cd936042"  


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer



@api_view(['POST'])
def send_otp_view(request):
    phone = request.data.get("phone")
    email = request.data.get("email")
    if not phone or not phone.isdigit() or len(phone) != 10:
        return Response({"detail": "Invalid phone number."}, status=400)
    if not email:
        return Response({"detail": "Email is required."}, status=400)

    # Generate a 6-digit OTP
    otp = ''.join(random.choices(string.digits, k=6))
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    # Store OTP in cache for 10 minutes
    cache.set(f"otp_{session_id}", {"otp": otp, "phone": phone, "email": email}, timeout=600)

    # Send OTP to email
    send_mail(
        subject="Your OTP Code",
        message=f"Your OTP code is: {otp}",
        from_email="sarthakkhare821@gmail.com",
        recipient_list=[email],
        fail_silently=False,
    )

    return Response({"session_id": session_id})

@api_view(['POST'])
def verify_otp_view(request):
    session_id = request.data.get("session_id")
    otp = request.data.get("otp")
    phone = request.data.get("phone")
    name = request.data.get("name")
    email = request.data.get("email")
    machine_id = request.data.get("machine_id")
    force_replace = request.data.get("force_replace", False)

    if not session_id or not otp or not phone or not machine_id or not email:
        return Response({"detail": "Phone, OTP, Machine ID, Session ID, and Email are required."}, status=400)

    # Get OTP from cache
    otp_data = cache.get(f"otp_{session_id}")
    if not otp_data or otp_data["otp"] != otp or otp_data["phone"] != phone or otp_data["email"] != email:
        return Response({"detail": "Invalid OTP or session."}, status=400)

    # ...existing code for customer creation and device logic...
    customer, created = Customer.objects.get_or_create(phone=phone)

    if name:
        customer.name = name
    if email:
        customer.email = email

    # Assign trial if new
    if created:
        try:
            plan = Plan.objects.get(name__iexact="Free Trial", price=0, duration_days=7)
            existing_trial = Subscription.objects.filter(customer=customer, plan=plan).exists()
            if not existing_trial:
                Subscription.objects.create(
                    customer=customer,
                    plan=plan,
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=plan.duration_days),
                    is_active=True
                )
        except Plan.DoesNotExist:
            return Response({"detail": "Trial plan not configured"}, status=500)

    subscription = customer.subscriptions.filter(is_active=True).order_by('-end_date').first()
    allowed_devices = subscription.plan.max_devices if subscription and subscription.plan else 1

    if not isinstance(customer.machine_ids, list):
        customer.machine_ids = []

    if machine_id not in customer.machine_ids:
        if len(customer.machine_ids) >= allowed_devices:
            if force_replace:
                customer.machine_ids.pop(0)
                customer.machine_ids.append(machine_id)
            else:
                return Response({
                    "detail": f"Device limit exceeded. Plan allows {allowed_devices} device(s).",
                    "force_logout": True,
                    "can_replace": True
                }, status=403)
        else:
            customer.machine_ids.append(machine_id)

    customer.save()

    # Optionally, delete OTP after use
    cache.delete(f"otp_{session_id}")

    return Response({
        "detail": "OTP Verified",
        "customer_id": customer.id,
        "phone": customer.phone,
        "name": customer.name,
        "email": customer.email,
        "new_user": created,
        "force_logout": False
    })
# ...existing code...

@api_view(['GET'])
def get_user_info_view(request):
    phone = request.query_params.get("phone")
    machine_id = request.query_params.get("machine_id")

    if not phone or not machine_id:
        return Response({"detail": "Phone number and Machine ID are required."}, status=400)

    try:
        customer = Customer.objects.get(phone=phone)
    except Customer.DoesNotExist:
        return Response({"detail": "Customer not found."}, status=404)

    subscription = customer.subscriptions.order_by('-end_date').first()

    if subscription and subscription.end_date < date.today():
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
    } if subscription else None

    force_logout = machine_id not in customer.machine_ids

    return Response({
        "customer_id": customer.id,
        "name": customer.name,
        "phone": customer.phone,
        "email": customer.email,
        "subscription": subscription_data,
        "force_logout": force_logout
    })




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

    try:
        firm = Firm.objects.get(id=firm_id)
    except Firm.DoesNotExist:
        return Response({"error": "Firm not found"}, status=404)

    shared_entries = SharedFirm.objects.filter(firm=firm).select_related('customer')
    serializer = SharedFirmSerializer(shared_entries, many=True)

    users = [{
        "name": entry.customer.name,
        "phone": entry.customer.phone,
        "email": entry.customer.email,
        "role": entry.role,
    } for entry in shared_entries]

    return Response({"status": "success", "synced_users": users,"whole":serializer.data})


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
    phone = request.GET.get("phone")
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
            for s in shared_firms if s.firm is not None
        ]
        return Response({"status": "success", "shared_firms": data})
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)

