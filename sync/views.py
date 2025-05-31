from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.forms.models import model_to_dict
from django.db import transaction
from customer.models import SharedFirm
from .models import (
    Firm, Category, Unit, UnitConversion, Item, Group, Party, PartyAdditionalField,
    Document, DocumentItem, DocumentCharge, DocumentTransportation, DocumentRelationship,
    StockMovement, BankAccount, BankTransaction, Payment
)

def has_access_to_firm(firm_id, owner):
    return Firm.objects.filter(id=firm_id, owner=owner).exists() or \
           SharedFirm.objects.filter(firm_id=firm_id, customer__mobile=owner).exists()

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
    owner = request.data.get("owner")  # 👈 Required: mobile number of current user

    if not table or not records or not owner:
        return Response({"error": "Parameters 'table', 'records', and 'owner' are required."}, status=status.HTTP_400_BAD_REQUEST)

    model = MODEL_MAP.get(table)
    if not model:
        return Response({"error": f"Invalid table name: {table}"}, status=status.HTTP_400_BAD_REQUEST)

    model_fields = {field.name for field in model._meta.fields}

    # Verify firmId ownership for tables that have firmId (except "firms" table itself)
    if table != "firms" and 'firmId' in model_fields:
        firm_ids = set(r.get("firmId") for r in records if r.get("firmId"))
        for fid in firm_ids:
            if not has_access_to_firm(fid, owner):
                return Response({"error": f"Access denied: You do not have access to firmId {fid}"}, status=status.HTTP_403_FORBIDDEN)

    # For firms table, verify that only owned firm(s) are modified
    if table == "firms":
        firm_ids = set(r.get("id") for r in records if r.get("id"))
        allowed_firm_ids = set(Firm.objects.filter(id__in=firm_ids, owner=owner).values_list("id", flat=True))
        new_firm_ids = firm_ids - allowed_firm_ids
        # Allow new firms if they include owner=owner
        for r in records:
            if r.get("id") in new_firm_ids and r.get("owner") != owner:
                return Response({"error": f"New firm record with id {r.get('id')} must have owner = {owner}"}, status=status.HTTP_403_FORBIDDEN)

    # Continue with sync logic
    model_objects = model.objects.all()
    if 'firmId' in model_fields:
        model_objects = model_objects.filter(firmId__in=firm_ids)

    existing_ids = set(model_objects.values_list("id", flat=True))
    incoming_ids = set([r.get("id") for r in records if r.get("id")])
    to_delete_ids = existing_ids - incoming_ids

    created, updated = 0, 0
    failed_records = []

    with transaction.atomic():
        if to_delete_ids:
            model.objects.filter(id__in=to_delete_ids).delete()

        for record in records:
            obj_id = record.get("id")
            if not obj_id:
                failed_records.append({"id": None, "table": table, "error": "Missing 'id'"})
                continue

            defaults = {k: v for k, v in record.items() if k in model_fields}
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
    owner = request.query_params.get("owner")  # 👈 Require owner to verify access

    if not table or not owner:
        return Response({"error": "'table' and 'owner' parameters are required"}, status=status.HTTP_400_BAD_REQUEST)

    model = MODEL_MAP.get(table)
    if not model:
        return Response({"error": f"Invalid table name: {table}"}, status=status.HTTP_400_BAD_REQUEST)

    model_fields = {field.name for field in model._meta.fields}
    queryset = model.objects.all()

    if table != "firms":
        if not firm_id:
            return Response({"error": "'firmId' parameter is required for this table"}, status=status.HTTP_400_BAD_REQUEST)

        if not has_access_to_firm(firm_id, owner):
            return Response({"error": "Access denied: You do not have access to this firm"}, status=status.HTTP_403_FORBIDDEN)

        if 'firmId' in model_fields:
            queryset = queryset.filter(firmId=firm_id)

    else:
        queryset = queryset.filter(owner=owner)

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


@api_view(["POST"])
def toggle_firm_sync_enabled(request):
    firm_id = request.data.get("firmId")
    owner = request.data.get("owner")  # required to verify access

    if not firm_id or not owner:
        return Response({"error": "'firmId' and 'owner' are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Validate firm access
        firm = Firm.objects.get(id=firm_id)
        if firm.owner != owner:
            return Response({"error": "Access denied: Not the owner of this firm."}, status=status.HTTP_403_FORBIDDEN)
    except Firm.DoesNotExist:
        return Response({"error": "Firm not found."}, status=status.HTTP_404_NOT_FOUND)

    # Toggle sync_enabled
    firm.sync_enabled = not firm.sync_enabled
    firm.save(update_fields=["sync_enabled"])

    return Response({
        "status": "success",
        "firmId": firm_id,
        "sync_enabled": firm.sync_enabled
    }, status=status.HTTP_200_OK)