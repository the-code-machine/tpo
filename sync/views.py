from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.apps import apps
from django.db import transaction
from .models import (
    Firm, Category, Unit, UnitConversion, Item, Group, Party, PartyAdditionalField,
    Document, DocumentItem, DocumentCharge, DocumentTransportation, DocumentRelationship,
    StockMovement, BankAccount, BankTransaction, Payment
)

# Table name to model mapping
MODEL_MAP = {
    "firms": Firm,
    "categories": Category,
    "units": Unit,
    "unit_conversions": UnitConversion,
    "items": Item,
    "groups": Group,
    "parties": Party,
    "party_additional_fields": PartyAdditionalField,
    "documents": Document,
    "document_items": DocumentItem,
    "document_charges": DocumentCharge,
    "document_transportation": DocumentTransportation,
    "document_relationships": DocumentRelationship,
    "stock_movements": StockMovement,
    "bank_accounts": BankAccount,
    "bank_transactions": BankTransaction,
    "payments": Payment,
}

@api_view(['POST'])
def sync_data(request):
    table = request.data.get("table")
    records = request.data.get("records")

    if not table or not records:
        return Response({"error": "Both 'table' and 'records' are required."}, status=400)

    model = MODEL_MAP.get(table)
    if not model:
        return Response({"error": f"Invalid table name: {table}"}, status=400)

    created, updated = 0, 0

    with transaction.atomic():
        for record in records:
            obj_id = record.get("id")
            if not obj_id:
                continue

            obj, is_new = model.objects.update_or_create(
                id=obj_id,
                defaults=record
            )
            if is_new:
                created += 1
            else:
                updated += 1

    return Response({
        "status": "success",
        "table": table,
        "created": created,
        "updated": updated
    }, status=200)


@api_view(['GET'])
def fetch_data(request):
    table = request.query_params.get("table")
    firm_id = request.query_params.get("firmId")
    updated_after = request.query_params.get("updatedAfter")  # optional ISO datetime

    if not table:
        return Response({"error": "'table' parameter is required"}, status=400)

    model = MODEL_MAP.get(table)
    if not model:
        return Response({"error": f"Invalid table name: {table}"}, status=400)

    queryset = model.objects.all()

    if firm_id and hasattr(model, 'firmId'):
        queryset = queryset.filter(firmId=firm_id)

    if updated_after and hasattr(model, 'updatedAt'):
        try:
            queryset = queryset.filter(updatedAt__gt=updated_after)
        except Exception:
            return Response({"error": "Invalid 'updatedAfter' format"}, status=400)

    # Return list of dicts (not JSON string) for JS parsing
    records = [model_to_dict(obj) for obj in queryset]

    return Response({
        "table": table,
        "count": len(records),
        "records": records
    }, status=200)