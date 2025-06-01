from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.forms.models import model_to_dict
from django.db import transaction
from django.db.models import Q
from customer.models import SharedFirm
from .models import (
    Firm, Category, Unit, UnitConversion, Item, Group, Party, PartyAdditionalField,
    Document, DocumentItem, DocumentCharge, DocumentTransportation, DocumentRelationship,
    StockMovement, BankAccount, BankTransaction, Payment, FirmSyncFlag
)

def has_access_to_firm(firm_id, owner):
    return Firm.objects.filter(id=firm_id, owner=owner).exists() or \
           SharedFirm.objects.filter(firm_id=firm_id, customer__phone=owner).exists()

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
    owner = request.data.get("owner")  # 👈 Mobile number

    if not table or not records or not owner:
        return Response({"error": "Parameters 'table', 'records', and 'owner' are required."},
                        status=status.HTTP_400_BAD_REQUEST)

    model = MODEL_MAP.get(table)
    if not model:
        return Response({"error": f"Invalid table name: {table}"}, status=status.HTTP_400_BAD_REQUEST)

    model_fields = {field.name for field in model._meta.fields}
    created, updated = 0, 0
    failed_records = []

    # Safety check for firm access
    firm_ids = set()
    if table != "firms" and 'firmId' in model_fields:
        firm_ids = set(r.get("firmId") for r in records if r.get("firmId"))
        if not firm_ids:
            return Response({"error": "Each record must have a 'firmId'"}, status=status.HTTP_400_BAD_REQUEST)
        for fid in firm_ids:
            if not has_access_to_firm(fid, owner):
                return Response({"error": f"Access denied: You do not have access to firmId {fid}"}, 
                                status=status.HTTP_403_FORBIDDEN)

    elif table == "firms":
        for r in records:
            if not r.get("owner") or r.get("owner") != owner:
                return Response({"error": f"Each firm record must have owner = {owner}"},
                                status=status.HTTP_403_FORBIDDEN)

    # Build per-firm deletion plan
    to_delete_ids = set()
    if table != "firms" and 'firmId' in model_fields:
        for fid in firm_ids:
            existing_ids = set(model.objects.filter(firmId=fid).values_list("id", flat=True))
            incoming_ids = set(r["id"] for r in records if r.get("firmId") == fid and r.get("id"))
            to_delete_ids.update(existing_ids - incoming_ids)
    elif table == "firms":
        # For firms, delete only firms owned by the user
        existing_ids = set(model.objects.filter(owner=owner).values_list("id", flat=True))
        incoming_ids = set(r.get("id") for r in records if r.get("id"))
        to_delete_ids = existing_ids - incoming_ids

    with transaction.atomic():
        # Delete safely
        if to_delete_ids:
            model.objects.filter(id__in=to_delete_ids).delete()
            for del_id in to_delete_ids:
                firm_id = next((r.get("firmId") for r in records if r.get("id") == del_id), None)
                if firm_id:
                    FirmSyncFlag.objects.create(
                        firm_id=firm_id,
                        changed_by_mobile=owner,
                        change_type='delete',
                        target_table=table
                    )

        # Create or update
        for record in records:
            obj_id = record.get("id")
            if not obj_id:
                failed_records.append({"id": None, "table": table, "error": "Missing 'id'"})
                continue

            defaults = {k: v for k, v in record.items() if k in model_fields}
            try:
                obj, is_new = model.objects.update_or_create(id=obj_id, defaults=defaults)

                firm_id = record.get("firmId") if 'firmId' in record else None
                if firm_id:
                    FirmSyncFlag.objects.create(
                        firm_id=firm_id,
                        changed_by_mobile=owner,
                        change_type='create' if is_new else 'update',
                        target_table=table
                    )

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
        queryset = queryset.filter(
        Q(owner=owner) | Q(shared_with__customer__phone=owner)
         ).distinct()


    if updated_after and 'updatedAt' in model_fields:
        try:
            queryset = queryset.filter(updatedAt__gt=updated_after)
        except Exception:
            return Response({"error": "Invalid 'updatedAfter' format"}, status=status.HTTP_400_BAD_REQUEST)

    records = [model_to_dict(obj) for obj in queryset]

    # # 👇 Mark sync flags as resolved
    # if firm_id and table != "firms":
    #     from sync.models import FirmSyncFlag  # make sure import path is correct

    #     FirmSyncFlag.objects.filter(
    #         firm_id=firm_id,
    #         target_table=table,
    #         resolved=False,
    #         changed_by_mobile__ne=owner  # exclude changes made by the current device
    #     ).update(resolved=True)

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