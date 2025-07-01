import razorpay
import hmac
import hashlib
from datetime import date, timedelta
from rest_framework.decorators import api_view
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework import viewsets
from .models import *
from .serializers import *
from django.http import FileResponse, Http404
from .models import ExecutableFile
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def download_exe(request):
    try:
        exe = ExecutableFile.objects.latest('id')
        filepath = exe.file.path
        return FileResponse(open(filepath, 'rb'), as_attachment=True, filename='app.exe')
    except ExecutableFile.DoesNotExist:
        raise Http404("Executable not found.")
    

@api_view(['GET'])
def get_latest_version(request):
    windows_file = ExecutableFile.objects.filter(platform='windows').order_by('-uploaded_at').first()
    mac_file = ExecutableFile.objects.filter(platform='mac').order_by('-uploaded_at').first()

    if not windows_file and not mac_file:
        return Response({"detail": "No executables found."}, status=status.HTTP_404_NOT_FOUND)

    def build_url(file):
        return request.build_absolute_uri(file.file.url) if file else None

    return Response({
        "version": windows_file.version if windows_file else (mac_file.version if mac_file else None),
        "windows_url": build_url(windows_file),
        "mac_url": build_url(mac_file),
    })
    
class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

class CreatePaymentOrder(APIView):
    permission_classes = []

    def post(self, request):
        plan_id = request.data.get('plan_id')
        user_id = request.data.get('user_id')  # Authenticated customer

        try:
            plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            return Response({"error": "Invalid plan ID"}, status=404)

        amount = int(plan.discounted_price * 100)  # in paise

        razorpay_order = razorpay_client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1,
            "notes": {
                "customer_id": str(user_id),
                "plan_id": str(plan.id),
            }
        })

        return Response({
            "order_id": razorpay_order["id"],
            "amount": amount,
            "currency": "INR",
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "plan": {
                "id": plan.id,
                "name": plan.name,
                "price": str(plan.price),
                "discount": str(plan.discount),
                "discounted_price": str(plan.discounted_price),
            }
        }, status=201)


class VerifyPaymentAndSubscribe(APIView):
    permission_classes = []  # Remove auth for now if testing

    def post(self, request):
        data = request.data

        order_id = data.get("razorpay_order_id")
        payment_id = data.get("razorpay_payment_id")
        signature = data.get("razorpay_signature")
        plan_id = data.get("plan_id")
        user_id = data.get("user", {}).get("id")  # ✅ Nested dict

        if not (order_id and payment_id and signature and user_id):
            return Response({"error": "Missing required fields"}, status=400)

        # 🔐 Verify signature
        generated_signature = hmac.new(
            key=bytes(settings.RAZORPAY_KEY_SECRET, 'utf-8'),
            msg=bytes(f"{order_id}|{payment_id}", 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        if generated_signature != signature:
            return Response({"status": "Invalid signature"}, status=400)

        # 🔎 Get Plan
        try:
            plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            return Response({"error": "Invalid plan ID"}, status=404)

        # 🔎 Get Customer
        try:
            customer = Customer.objects.get(id=user_id)
        except Customer.DoesNotExist:
            return Response({"error": "Invalid user ID"}, status=404)

        # ✅ Create Subscription
        Subscription.objects.create(
            customer=customer,
            plan=plan,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=plan.duration_days),
            is_active=True
        )

        return Response({"status": "Payment verified and subscription activated"}, status=200)
