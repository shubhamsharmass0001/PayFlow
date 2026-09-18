// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'invoice_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_InvoiceItem _$InvoiceItemFromJson(Map<String, dynamic> json) => _InvoiceItem(
  id: json['id'] as String?,
  name: json['name'] as String,
  description: json['description'] as String?,
  quantity: json['quantity'] as String? ?? '1.00',
  unitPrice: json['unit_price'] as String,
  taxRate: json['tax_rate'] as String? ?? '0.00',
  discountAmount: json['discount_amount'] as String? ?? '0.00',
  lineTotal: json['line_total'] as String? ?? '0.00',
);

Map<String, dynamic> _$InvoiceItemToJson(_InvoiceItem instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'quantity': instance.quantity,
      'unit_price': instance.unitPrice,
      'tax_rate': instance.taxRate,
      'discount_amount': instance.discountAmount,
      'line_total': instance.lineTotal,
    };

_Invoice _$InvoiceFromJson(Map<String, dynamic> json) => _Invoice(
  id: json['id'] as String,
  merchantId: json['merchant_id'] as String,
  invoiceNumber: json['invoice_number'] as String,
  customerId: json['customer_id'] as String?,
  storeId: json['store_id'] as String?,
  status:
      $enumDecodeNullable(_$InvoiceStatusEnumMap, json['status']) ??
      InvoiceStatus.draft,
  subtotal: json['subtotal'] as String,
  taxTotal: json['tax_total'] as String,
  discountTotal: json['discount_total'] as String,
  totalAmount: json['total_amount'] as String,
  paidAmount: json['paid_amount'] as String,
  currency: json['currency'] as String? ?? 'INR',
  allowPartialPayment: json['allow_partial_payment'] as bool? ?? false,
  allowSplitPayment: json['allow_split_payment'] as bool? ?? false,
  dueDate: json['due_date'] as String?,
  notes: json['notes'] as String?,
  createdAt: json['created_at'] as String?,
  updatedAt: json['updated_at'] as String?,
  items:
      (json['items'] as List<dynamic>?)
          ?.map((e) => InvoiceItem.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  customerName: json['customer_name'] as String?,
);

Map<String, dynamic> _$InvoiceToJson(_Invoice instance) => <String, dynamic>{
  'id': instance.id,
  'merchant_id': instance.merchantId,
  'invoice_number': instance.invoiceNumber,
  'customer_id': instance.customerId,
  'store_id': instance.storeId,
  'status': _$InvoiceStatusEnumMap[instance.status]!,
  'subtotal': instance.subtotal,
  'tax_total': instance.taxTotal,
  'discount_total': instance.discountTotal,
  'total_amount': instance.totalAmount,
  'paid_amount': instance.paidAmount,
  'currency': instance.currency,
  'allow_partial_payment': instance.allowPartialPayment,
  'allow_split_payment': instance.allowSplitPayment,
  'due_date': instance.dueDate,
  'notes': instance.notes,
  'created_at': instance.createdAt,
  'updated_at': instance.updatedAt,
  'items': instance.items,
  'customer_name': instance.customerName,
};

const _$InvoiceStatusEnumMap = {
  InvoiceStatus.draft: 'DRAFT',
  InvoiceStatus.sent: 'SENT',
  InvoiceStatus.issued: 'ISSUED',
  InvoiceStatus.partiallyPaid: 'PARTIALLY_PAID',
  InvoiceStatus.paid: 'PAID',
  InvoiceStatus.cancelled: 'CANCELLED',
  InvoiceStatus.overdue: 'OVERDUE',
  InvoiceStatus.refunded: 'REFUNDED',
};

_CreateInvoiceRequest _$CreateInvoiceRequestFromJson(
  Map<String, dynamic> json,
) => _CreateInvoiceRequest(
  customerId: json['customer_id'] as String?,
  storeId: json['store_id'] as String?,
  dueDate: json['due_date'] as String?,
  notes: json['notes'] as String?,
  allowPartialPayment: json['allow_partial_payment'] as bool? ?? false,
  allowSplitPayment: json['allow_split_payment'] as bool? ?? false,
  items:
      (json['items'] as List<dynamic>?)
          ?.map((e) => e as Map<String, dynamic>)
          .toList() ??
      const [],
);

Map<String, dynamic> _$CreateInvoiceRequestToJson(
  _CreateInvoiceRequest instance,
) => <String, dynamic>{
  'customer_id': instance.customerId,
  'store_id': instance.storeId,
  'due_date': instance.dueDate,
  'notes': instance.notes,
  'allow_partial_payment': instance.allowPartialPayment,
  'allow_split_payment': instance.allowSplitPayment,
  'items': instance.items,
};

_Installment _$InstallmentFromJson(Map<String, dynamic> json) => _Installment(
  id: json['id'] as String,
  installmentNumber: (json['installment_number'] as num).toInt(),
  label: json['label'] as String?,
  amount: json['amount'] as String,
  paidAmount: json['paid_amount'] as String,
  dueDate: json['due_date'] as String,
  status:
      $enumDecodeNullable(_$InstallmentStatusEnumMap, json['status']) ??
      InstallmentStatus.pending,
);

Map<String, dynamic> _$InstallmentToJson(_Installment instance) =>
    <String, dynamic>{
      'id': instance.id,
      'installment_number': instance.installmentNumber,
      'label': instance.label,
      'amount': instance.amount,
      'paid_amount': instance.paidAmount,
      'due_date': instance.dueDate,
      'status': _$InstallmentStatusEnumMap[instance.status]!,
    };

const _$InstallmentStatusEnumMap = {
  InstallmentStatus.pending: 'PENDING',
  InstallmentStatus.partiallyPaid: 'PARTIALLY_PAID',
  InstallmentStatus.paid: 'PAID',
  InstallmentStatus.overdue: 'OVERDUE',
  InstallmentStatus.cancelled: 'CANCELLED',
};

_PaymentPlan _$PaymentPlanFromJson(Map<String, dynamic> json) => _PaymentPlan(
  id: json['id'] as String,
  merchantId: json['merchant_id'] as String,
  invoiceId: json['invoice_id'] as String?,
  customerId: json['customer_id'] as String?,
  planType: $enumDecode(_$PlanTypeEnumMap, json['plan_type']),
  totalAmount: json['total_amount'] as String,
  status:
      $enumDecodeNullable(_$PlanStatusEnumMap, json['status']) ??
      PlanStatus.active,
  installments:
      (json['installments'] as List<dynamic>?)
          ?.map((e) => Installment.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
);

Map<String, dynamic> _$PaymentPlanToJson(_PaymentPlan instance) =>
    <String, dynamic>{
      'id': instance.id,
      'merchant_id': instance.merchantId,
      'invoice_id': instance.invoiceId,
      'customer_id': instance.customerId,
      'plan_type': _$PlanTypeEnumMap[instance.planType]!,
      'total_amount': instance.totalAmount,
      'status': _$PlanStatusEnumMap[instance.status]!,
      'installments': instance.installments,
    };

const _$PlanTypeEnumMap = {
  PlanType.deposit: 'DEPOSIT',
  PlanType.installment: 'INSTALLMENT',
  PlanType.milestone: 'MILESTONE',
  PlanType.customSplit: 'CUSTOM_SPLIT',
};

const _$PlanStatusEnumMap = {
  PlanStatus.active: 'ACTIVE',
  PlanStatus.completed: 'COMPLETED',
  PlanStatus.cancelled: 'CANCELLED',
  PlanStatus.defaulted: 'DEFAULTED',
};
