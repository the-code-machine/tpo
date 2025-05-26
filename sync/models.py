import uuid
from django.db import models

class Firm(models.Model):
    id = models.CharField(primary_key=True, max_length=100)  # match TEXT in SQLite
    country = models.TextField()
    name = models.TextField()
    phone = models.TextField()
    gstNumber = models.TextField(blank=True, null=True)
    owner = models.TextField(null=True)
    ownerName = models.TextField(blank=True, null=True)
    businessName = models.TextField(blank=True, null=True)
    businessLogo = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    createdAt = models.TextField()
    updatedAt = models.TextField()

    class Meta:
        db_table = 'firms'
        ordering = ['-createdAt']

    def __str__(self):
        return self.name

class Category(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    name = models.TextField()
    firmId = models.TextField()
    description = models.TextField(blank=True, null=True)
    createdAt = models.TextField()
    updatedAt = models.TextField()

    class Meta:
        db_table = 'categories'
        ordering = ['-createdAt']

    def __str__(self):
        return self.name

class Unit(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    firmId = models.TextField()
    fullname = models.TextField()
    shortname = models.TextField()
    createdAt = models.TextField()
    updatedAt = models.TextField()

    class Meta:
        db_table = 'units'
        ordering = ['-createdAt']

    def __str__(self):
        return self.fullname

class UnitConversion(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    firmId = models.TextField()
    primaryUnitId = models.TextField()
    secondaryUnitId = models.TextField()
    conversionRate = models.FloatField()
    createdAt = models.TextField()
    updatedAt = models.TextField()

    class Meta:
        db_table = 'unit_conversions'
        ordering = ['-createdAt']

    def __str__(self):
        return f"{self.primaryUnitId} → {self.secondaryUnitId}"


class Item(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    firmId = models.TextField()

    name = models.TextField()
    type = models.TextField()  # Expected to be 'PRODUCT' or 'SERVICE'
    hsnCode = models.TextField(blank=True, null=True)
    itemCode = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    imageUrl = models.TextField(blank=True, null=True)
    categoryId = models.TextField(blank=True, null=True)
    unit_conversionId = models.TextField(blank=True, null=True)

    salePrice = models.FloatField()
    salePriceTaxInclusive = models.BooleanField(default=False)
    saleDiscount = models.FloatField(blank=True, null=True)
    saleDiscountType = models.TextField(blank=True, null=True)  # 'percentage' or 'amount'
    wholesalePrice = models.FloatField(blank=True, null=True)

    purchasePrice = models.FloatField(blank=True, null=True)
    purchasePriceTaxInclusive = models.BooleanField(default=False)

    taxRate = models.TextField(blank=True, null=True)
    primaryQuantity = models.FloatField(blank=True, null=True)
    secondaryQuantity = models.FloatField(blank=True, null=True)
    primaryOpeningQuantity = models.FloatField(blank=True, null=True)
    secondaryOpeningQuantity = models.FloatField(blank=True, null=True)
    pricePerUnit = models.FloatField(blank=True, null=True)
    minStockLevel = models.FloatField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    openingStockDate = models.TextField(blank=True, null=True)

    enableBatchTracking = models.BooleanField(default=False)
    batchNumber = models.TextField(blank=True, null=True)
    expiryDate = models.TextField(blank=True, null=True)
    mfgDate = models.TextField(blank=True, null=True)

    isActive = models.BooleanField(default=True)
    allowNegativeStock = models.BooleanField(default=False)
    isFavorite = models.BooleanField(default=False)

    customFields = models.TextField(blank=True, null=True)

    createdAt = models.TextField()
    updatedAt = models.TextField()

    class Meta:
        db_table = 'items'
        ordering = ['-createdAt']

    def __str__(self):
        return self.name

class Group(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    firmId = models.TextField()
    groupName = models.TextField()
    description = models.TextField(blank=True, null=True)
    createdAt = models.TextField()
    updatedAt = models.TextField()

    class Meta:
        db_table = 'groups'
        ordering = ['-createdAt']

    def __str__(self):
        return self.groupName


class Party(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    firmId = models.TextField()
    name = models.TextField()
    gstNumber = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    groupId = models.TextField(blank=True, null=True)
    gstType = models.TextField()
    state = models.TextField(blank=True, null=True)
    billingAddress = models.TextField(blank=True, null=True)
    shippingAddress = models.TextField(blank=True, null=True)
    shippingEnabled = models.BooleanField(default=False)

    openingBalance = models.FloatField(blank=True, null=True)
    openingBalanceType = models.TextField(blank=True, null=True)  # 'to_pay' / 'to_receive'
    currentBalance = models.FloatField(blank=True, null=True)
    currentBalanceType = models.TextField(blank=True, null=True)  # 'to_pay' / 'to_receive'
    openingBalanceDate = models.TextField(blank=True, null=True)

    creditLimitType = models.TextField(default='none')  # e.g., 'none'
    creditLimitValue = models.FloatField(blank=True, null=True)

    paymentReminderEnabled = models.BooleanField(default=False)
    paymentReminderDays = models.IntegerField(blank=True, null=True)

    loyaltyPointsEnabled = models.BooleanField(default=False)

    createdAt = models.TextField()
    updatedAt = models.TextField()

    class Meta:
        db_table = 'parties'
        ordering = ['-createdAt']

    def __str__(self):
        return self.name

class PartyAdditionalField(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    firmId = models.TextField()
    partyId = models.TextField()
    fieldKey = models.TextField()
    fieldValue = models.TextField(blank=True, null=True)
    createdAt = models.TextField()
    updatedAt = models.TextField()

    class Meta:
        db_table = 'party_additional_fields'
        ordering = ['-createdAt']

    def __str__(self):
        return f"{self.fieldKey}: {self.fieldValue}"

class Document(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    firmId = models.TextField()
    documentType = models.TextField()  # Enum-like: 'sale_invoice', 'purchase_order', etc.
    documentNumber = models.TextField()
    documentDate = models.TextField()
    documentTime = models.TextField(blank=True, null=True)

    # Party Info
    partyId = models.TextField(blank=True, null=True)
    partyName = models.TextField()
    phone = models.TextField(blank=True, null=True)
    partyType = models.TextField()  # 'customer' or 'supplier'

    # Transaction Details
    transactionType = models.TextField()  # 'cash' or 'credit'
    status = models.TextField(default='draft')

    # Common Fields
    ewaybill = models.TextField(blank=True, null=True)
    billingAddress = models.TextField(blank=True, null=True)
    billingName = models.TextField(blank=True, null=True)
    poDate = models.TextField(blank=True, null=True)
    poNumber = models.TextField(blank=True, null=True)
    stateOfSupply = models.TextField(blank=True, null=True)
    roundOff = models.FloatField(default=0)
    total = models.FloatField()

    # Shipping
    transportName = models.TextField(blank=True, null=True)
    vehicleNumber = models.TextField(blank=True, null=True)
    deliveryDate = models.TextField(blank=True, null=True)
    deliveryLocation = models.TextField(blank=True, null=True)

    # Extra Charges
    shipping = models.FloatField(blank=True, null=True)
    packaging = models.FloatField(blank=True, null=True)
    adjustment = models.FloatField(blank=True, null=True)

    # Payment
    paymentType = models.TextField()
    bankId = models.TextField(blank=True, null=True)
    chequeNumber = models.TextField(blank=True, null=True)
    chequeDate = models.TextField(blank=True, null=True)

    # Other fields
    description = models.TextField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)

    # Discount & Tax
    discountPercentage = models.FloatField(blank=True, null=True)
    discountAmount = models.FloatField(blank=True, null=True)
    taxPercentage = models.FloatField(blank=True, null=True)
    taxAmount = models.FloatField(blank=True, null=True)

    # Payment amounts
    balanceAmount = models.FloatField()
    paidAmount = models.FloatField()

    # Audit
    createdAt = models.TextField()
    updatedAt = models.TextField()

    class Meta:
        db_table = 'documents'
        ordering = ['-createdAt']

    def __str__(self):
        return f"{self.documentType.upper()} - {self.documentNumber}"

class DocumentItem(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    firmId = models.TextField()
    documentId = models.TextField()
    itemId = models.TextField()
    itemName = models.TextField()

    # Quantities
    primaryQuantity = models.FloatField()
    secondaryQuantity = models.FloatField(blank=True, null=True)

    # Units
    primaryUnitId = models.TextField()
    primaryUnitName = models.TextField()
    secondaryUnitId = models.TextField(blank=True, null=True)
    secondaryUnitName = models.TextField(blank=True, null=True)
    unit_conversionId = models.TextField(blank=True, null=True)
    conversionRate = models.FloatField(blank=True, null=True)

    # Pricing
    pricePerUnit = models.FloatField()
    amount = models.FloatField()

    # Batch details
    mfgDate = models.TextField(blank=True, null=True)
    batchNo = models.TextField(blank=True, null=True)
    expDate = models.TextField(blank=True, null=True)

    # Tax
    taxType = models.TextField(blank=True, null=True)
    taxRate = models.TextField(blank=True, null=True)
    taxAmount = models.FloatField(blank=True, null=True)

    # Category
    categoryId = models.TextField(blank=True, null=True)
    categoryName = models.TextField(blank=True, null=True)

    # Additional item details
    itemCode = models.TextField(blank=True, null=True)
    hsnCode = models.TextField(blank=True, null=True)
    serialNo = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    modelNo = models.TextField(blank=True, null=True)
    mrp = models.FloatField(blank=True, null=True)
    size = models.TextField(blank=True, null=True)
    discountPercent = models.FloatField(blank=True, null=True)
    discountAmount = models.FloatField(blank=True, null=True)

    createdAt = models.TextField()
    updatedAt = models.TextField()

    class Meta:
        db_table = 'document_items'
        ordering = ['-createdAt']

    def __str__(self):
        return f"{self.itemName} ({self.documentId})"

class DocumentCharge(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    firmId = models.TextField()
    documentId = models.TextField()
    name = models.TextField()
    amount = models.FloatField()
    createdAt = models.TextField()
    updatedAt = models.TextField()

    class Meta:
        db_table = 'document_charges'
        ordering = ['-createdAt']

    def __str__(self):
        return f"{self.name}: {self.amount}"

class DocumentTransportation(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    firmId = models.TextField()
    documentId = models.TextField()
    type = models.TextField()
    detail = models.TextField()
    amount = models.FloatField(blank=True, null=True)
    createdAt = models.TextField()
    updatedAt = models.TextField()

    class Meta:
        db_table = 'document_transportation'
        ordering = ['-createdAt']

    def __str__(self):
        return f"{self.type}: {self.detail}"

class DocumentRelationship(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    firmId = models.TextField()
    sourceDocumentId = models.TextField()
    targetDocumentId = models.TextField()
    relationshipType = models.TextField()  # 'converted', 'fulfilled', etc.
    createdAt = models.TextField()
    updatedAt = models.TextField()

    class Meta:
        db_table = 'document_relationships'
        ordering = ['-createdAt']

    def __str__(self):
        return f"{self.sourceDocumentId} → {self.targetDocumentId} ({self.relationshipType})"

class StockMovement(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    firmId = models.TextField()
    itemId = models.TextField()
    documentId = models.TextField()
    documentItemId = models.TextField(blank=True, null=True)

    # Movement details
    movementType = models.TextField()  # 'in', 'out', 'adjustment', 'conversion'

    # Primary unit
    primaryQuantity = models.FloatField()
    primaryUnitId = models.TextField()

    # Secondary unit
    secondaryQuantity = models.FloatField(blank=True, null=True)
    secondaryUnitId = models.TextField(blank=True, null=True)

    # Batch / notes
    batchNumber = models.TextField(blank=True, null=True)
    expiryDate = models.TextField(blank=True, null=True)
    mfgDate = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.TextField()
    updatedAt = models.TextField()

    class Meta:
        db_table = 'stock_movements'
        ordering = ['-createdAt']

    def __str__(self):
        return f"{self.movementType.upper()} - {self.itemId}"

class BankAccount(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    firmId = models.TextField()

    displayName = models.TextField()
    bankName = models.TextField()
    accountNumber = models.TextField()
    accountHolderName = models.TextField()
    ifscCode = models.TextField()
    upiId = models.TextField(blank=True, null=True)

    openingBalance = models.FloatField()
    currentBalance = models.FloatField()
    asOfDate = models.TextField()

    printUpiQrOnInvoices = models.BooleanField(default=False)
    printBankDetailsOnInvoices = models.BooleanField(default=False)
    isActive = models.BooleanField(default=True)

    notes = models.TextField(blank=True, null=True)
    createdAt = models.TextField()
    updatedAt = models.TextField()

    class Meta:
        db_table = 'bank_accounts'
        ordering = ['-createdAt']

    def __str__(self):
        return self.displayName

class BankTransaction(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    firmId = models.TextField()
    bankAccountId = models.TextField()
    amount = models.FloatField()

    transactionType = models.TextField()  # 'deposit', 'withdrawal', etc.
    transactionDate = models.TextField()
    description = models.TextField()

    referenceNumber = models.TextField(blank=True, null=True)
    relatedEntityId = models.TextField(blank=True, null=True)
    relatedEntityType = models.TextField(blank=True, null=True)

    createdAt = models.TextField()
    updatedAt = models.TextField()

    class Meta:
        db_table = 'bank_transactions'
        ordering = ['-transactionDate']

    def __str__(self):
        return f"{self.transactionType.upper()} - ₹{self.amount}"

class Payment(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    firmId = models.TextField()

    amount = models.FloatField()
    paymentType = models.TextField()  # 'cash', 'cheque', 'bank'
    paymentDate = models.TextField()
    referenceNumber = models.TextField(blank=True, null=True)

    partyId = models.TextField(blank=True, null=True)
    partyName = models.TextField(blank=True, null=True)

    description = models.TextField(blank=True, null=True)
    receiptNumber = models.TextField(blank=True, null=True)

    bankAccountId = models.TextField(blank=True, null=True)
    chequeNumber = models.TextField(blank=True, null=True)
    chequeDate = models.TextField(blank=True, null=True)

    imageUrl = models.TextField(blank=True, null=True)

    direction = models.TextField()  # 'in' or 'out'
    linkedDocumentId = models.TextField(blank=True, null=True)
    linkedDocumentType = models.TextField(blank=True, null=True)

    isReconciled = models.BooleanField(default=False)

    createdAt = models.TextField()
    updatedAt = models.TextField()

    class Meta:
        db_table = 'payments'
        ordering = ['-paymentDate']

    def __str__(self):
        return f"{self.direction.upper()} ₹{self.amount} - {self.paymentDate}"

