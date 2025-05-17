from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.forms.models import model_to_dict
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
    failed_records = []

    model_fields = {field.name for field in model._meta.fields}

    with transaction.atomic():
        for record in records:
            obj_id = record.get("id")
            if not obj_id:
                continue

            # Strip 'firmId' from defaults if the model does not have it
            defaults = {
                k: v for k, v in record.items()
                if k in model_fields
            }

            try:
                _, is_new = model.objects.update_or_create(id=obj_id, defaults=defaults)
                created += int(is_new)
                updated += int(not is_new)
            except Exception as e:
                failed_records.append({"id": obj_id, "error": str(e), "table": table})

    return Response({
        "status": "success" if not failed_records else "partial",
        "table": table,
        "created": created,
        "updated": updated,
        "failed": len(failed_records),
        "errors": failed_records
    }, status=200)


@api_view(['GET'])
def fetch_data(request):
    table = request.query_params.get("table")
    firm_id = request.query_params.get("firmId")
    updated_after = request.query_params.get("updatedAfter")

    if not table:
        return Response({"error": "'table' parameter is required"}, status=400)

    model = MODEL_MAP.get(table)
    if not model:
        return Response({"error": f"Invalid table name: {table}"}, status=400)

    queryset = model.objects.all()
    model_fields = {field.name for field in model._meta.fields}

    if firm_id and 'firmId' in model_fields:
        queryset = queryset.filter(firmId=firm_id)

    if updated_after and 'updatedAt' in model_fields:
        try:
            queryset = queryset.filter(updatedAt__gt=updated_after)
        except Exception:
            return Response({"error": "Invalid 'updatedAfter' format"}, status=400)

    records = [model_to_dict(obj) for obj in queryset]

    return Response({
        "table": table,
        "count": len(records),
        "records": records
    }, status=200)
