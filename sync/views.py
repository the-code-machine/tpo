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

# Mapping table name to model class
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
        return Response({"error": "Both 'table' and 'records' are required."}, status=status.HTTP_400_BAD_REQUEST)

    model = MODEL_MAP.get(table)
    if not model:
        return Response({"error": f"Invalid table name: {table}"}, status=status.HTTP_400_BAD_REQUEST)

    model_fields = {field.name for field in model._meta.fields}
    existing_ids = set(model.objects.values_list("id", flat=True))
    incoming_ids = set([r.get("id") for r in records if r.get("id")])

    to_delete_ids = existing_ids - incoming_ids  # ❌ Delete records not present in local

    created, updated = 0, 0
    failed_records = []

    with transaction.atomic():
        # Step 1: Delete removed records
        if to_delete_ids:
            model.objects.filter(id__in=to_delete_ids).delete()

        # Step 2: Create or update incoming records
        for record in records:
            obj_id = record.get("id")
            if not obj_id:
                failed_records.append({"id": None, "table": table, "error": "Missing 'id'"})
                continue

            defaults = {
                k: v for k, v in record.items()
                if k in model_fields
            }

            try:
                _, is_new = model.objects.update_or_create(id=obj_id, defaults=defaults)
                if is_new:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                failed_records.append({"id": obj_id, "table": table, "error": str(e)})

    return Response({
        "status": "success" if not failed_records else "partial",
        "table": table,
        "created": created,
        "updated": updated,
        "deleted": len(to_delete_ids),
        "failed": len(failed_records),
        "errors": failed_records
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def fetch_data(request):
    table = request.query_params.get("table")
    firm_id = request.query_params.get("firmId")
    updated_after = request.query_params.get("updatedAfter")

    if not table:
        return Response({"error": "'table' parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    model = MODEL_MAP.get(table)
    if not model:
        return Response({"error": f"Invalid table name: {table}"}, status=status.HTTP_400_BAD_REQUEST)

    model_fields = {field.name for field in model._meta.fields}
    queryset = model.objects.all()

    # Skip firmId filter for "firms"
    if table != "firms" and firm_id and 'firmId' in model_fields:
        queryset = queryset.filter(firmId=firm_id)

    if updated_after and 'updatedAt' in model_fields:
        try:
            queryset = queryset.filter(updatedAt__gt=updated_after)
        except Exception:
            return Response({"error": "Invalid 'updatedAfter' format"}, status=status.HTTP_400_BAD_REQUEST)

    records = [model_to_dict(obj) for obj in queryset]

    return Response({
        "table": table,
        "count": len(records),
        "records": records
    }, status=status.HTTP_200_OK)
