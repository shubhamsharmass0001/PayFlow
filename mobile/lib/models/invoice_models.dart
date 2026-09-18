import 'package:freezed_annotation/freezed_annotation.dart';

part 'invoice_models.freezed.dart';
part 'invoice_models.g.dart';

enum InvoiceStatus {
  @JsonValue('DRAFT') draft,
  @JsonValue('SENT') sent,
  @JsonValue('ISSUED') issued,
  @JsonValue('PARTIALLY_PAID') partiallyPaid,
  @JsonValue('PAID') paid,
  @JsonValue('CANCELLED') cancelled,
  @JsonValue('OVERDUE') overdue,
  @JsonValue('REFUNDED') refunded,
}

@freezed
abstract class InvoiceItem with _$InvoiceItem {
  const factory InvoiceItem({
    String? id,
    required String name,
    String? description,
    @Default('1.00') String quantity,
    @JsonKey(name: 'unit_price') required String unitPrice,
    @JsonKey(name: 'tax_rate') @Default('0.00') String taxRate,
    @JsonKey(name: 'discount_amount') @Default('0.00') String discountAmount,
    @JsonKey(name: 'line_total') @Default('0.00') String lineTotal,
  }) = _InvoiceItem;

  factory InvoiceItem.fromJson(Map<String, dynamic> json) =>
      _$InvoiceItemFromJson(json);
}

@freezed
abstract class Invoice with _$Invoice {
  const factory Invoice({
    required String id,
    @JsonKey(name: 'merchant_id') required String merchantId,
    @JsonKey(name: 'invoice_number') required String invoiceNumber,
    @JsonKey(name: 'customer_id') String? customerId,
    @JsonKey(name: 'store_id') String? storeId,
    @Default(InvoiceStatus.draft) InvoiceStatus status,
    @JsonKey(name: 'subtotal') required String subtotal,
    @JsonKey(name: 'tax_total') required String taxTotal,
    @JsonKey(name: 'discount_total') required String discountTotal,
    @JsonKey(name: 'total_amount') required String totalAmount,
    @JsonKey(name: 'paid_amount') required String paidAmount,
    @Default('INR') String currency,
    @JsonKey(name: 'allow_partial_payment') @Default(false) bool allowPartialPayment,
    @JsonKey(name: 'allow_split_payment') @Default(false) bool allowSplitPayment,
    @JsonKey(name: 'due_date') String? dueDate,
    String? notes,
    @JsonKey(name: 'created_at') String? createdAt,
    @JsonKey(name: 'updated_at') String? updatedAt,
    @Default([]) List<InvoiceItem> items,
    // Customer name — joined by backend when available
    @JsonKey(name: 'customer_name') String? customerName,
  }) = _Invoice;

  factory Invoice.fromJson(Map<String, dynamic> json) =>
      _$InvoiceFromJson(json);
}

@freezed
abstract class CreateInvoiceRequest with _$CreateInvoiceRequest {
  const factory CreateInvoiceRequest({
    @JsonKey(name: 'customer_id') String? customerId,
    @JsonKey(name: 'store_id') String? storeId,
    @JsonKey(name: 'due_date') String? dueDate,
    String? notes,
    @JsonKey(name: 'allow_partial_payment') @Default(false) bool allowPartialPayment,
    @JsonKey(name: 'allow_split_payment') @Default(false) bool allowSplitPayment,
    @Default([]) List<Map<String, dynamic>> items,
  }) = _CreateInvoiceRequest;

  factory CreateInvoiceRequest.fromJson(Map<String, dynamic> json) =>
      _$CreateInvoiceRequestFromJson(json);
}

// ── Payment Plans ────────────────────────────────────────────────────────────

enum PlanType {
  @JsonValue('DEPOSIT')      deposit,
  @JsonValue('INSTALLMENT')  installment,
  @JsonValue('MILESTONE')    milestone,
  @JsonValue('CUSTOM_SPLIT') customSplit,
}

enum PlanStatus {
  @JsonValue('ACTIVE')     active,
  @JsonValue('COMPLETED')  completed,
  @JsonValue('CANCELLED')  cancelled,
  @JsonValue('DEFAULTED')  defaulted,
}

enum InstallmentStatus {
  @JsonValue('PENDING')       pending,
  @JsonValue('PARTIALLY_PAID') partiallyPaid,
  @JsonValue('PAID')          paid,
  @JsonValue('OVERDUE')       overdue,
  @JsonValue('CANCELLED')     cancelled,
}

@freezed
abstract class Installment with _$Installment {
  const factory Installment({
    required String id,
    @JsonKey(name: 'installment_number') required int installmentNumber,
    String? label,
    required String amount,
    @JsonKey(name: 'paid_amount') required String paidAmount,
    @JsonKey(name: 'due_date') required String dueDate,
    @Default(InstallmentStatus.pending) InstallmentStatus status,
  }) = _Installment;

  factory Installment.fromJson(Map<String, dynamic> json) =>
      _$InstallmentFromJson(json);
}

@freezed
abstract class PaymentPlan with _$PaymentPlan {
  const factory PaymentPlan({
    required String id,
    @JsonKey(name: 'merchant_id') required String merchantId,
    @JsonKey(name: 'invoice_id') String? invoiceId,
    @JsonKey(name: 'customer_id') String? customerId,
    @JsonKey(name: 'plan_type') required PlanType planType,
    @JsonKey(name: 'total_amount') required String totalAmount,
    @Default(PlanStatus.active) PlanStatus status,
    @Default([]) List<Installment> installments,
  }) = _PaymentPlan;

  factory PaymentPlan.fromJson(Map<String, dynamic> json) =>
      _$PaymentPlanFromJson(json);
}
