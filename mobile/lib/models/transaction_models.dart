import 'package:freezed_annotation/freezed_annotation.dart';

part 'transaction_models.freezed.dart';
part 'transaction_models.g.dart';

enum TransactionStatus {
  @JsonValue('CREATED')            created,
  @JsonValue('INITIATED')          initiated,
  @JsonValue('PENDING')            pending,
  @JsonValue('SUCCESS')            success,
  @JsonValue('FAILED')             failed,
  @JsonValue('TIMEOUT')            timeout,
  @JsonValue('DUPLICATE')          duplicate,
  @JsonValue('REFUND_INITIATED')   refundInitiated,
  @JsonValue('REFUND_PENDING')     refundPending,
  @JsonValue('REFUNDED')           refunded,
  @JsonValue('REFUND_FAILED')      refundFailed,
  @JsonValue('PARTIALLY_REFUNDED') partiallyRefunded,
}

enum PaymentMethod {
  @JsonValue('UPI_COLLECT') upiCollect,
  @JsonValue('UPI_INTENT')  upiIntent,
  @JsonValue('UPI_QR')      upiQr,
  @JsonValue('CARD')        card,
  @JsonValue('NET_BANKING') netBanking,
  @JsonValue('WALLET')      wallet,
}

@freezed
abstract class TransactionStatusHistory with _$TransactionStatusHistory {
  const factory TransactionStatusHistory({
    required String id,
    @JsonKey(name: 'from_status') String? fromStatus,
    @JsonKey(name: 'to_status') required String toStatus,
    String? reason,
    @JsonKey(name: 'created_at') required String createdAt,
  }) = _TransactionStatusHistory;

  factory TransactionStatusHistory.fromJson(Map<String, dynamic> json) =>
      _$TransactionStatusHistoryFromJson(json);
}

@freezed
abstract class DuplicateFlag with _$DuplicateFlag {
  const factory DuplicateFlag({
    required String id,
    @JsonKey(name: 'flag_reason') required String flagReason,
    @JsonKey(name: 'confidence_score') required double confidenceScore,
    required String status,
    @JsonKey(name: 'match_reason') String? matchReason,
  }) = _DuplicateFlag;

  factory DuplicateFlag.fromJson(Map<String, dynamic> json) =>
      _$DuplicateFlagFromJson(json);
}

@freezed
abstract class PaymentTransaction with _$PaymentTransaction {
  const factory PaymentTransaction({
    required String id,
    @JsonKey(name: 'merchant_id') required String merchantId,
    @JsonKey(name: 'invoice_id') String? invoiceId,
    @JsonKey(name: 'customer_id') String? customerId,
    @JsonKey(name: 'idempotency_key') required String idempotencyKey,
    required String amount,
    @Default('INR') String currency,
    @Default(TransactionStatus.initiated) TransactionStatus status,
    @JsonKey(name: 'payment_method') required PaymentMethod paymentMethod,
    @JsonKey(name: 'mock_scenario') String? mockScenario,
    @JsonKey(name: 'provider_ref_id') String? providerRefId,
    @JsonKey(name: 'payer_vpa') String? payerVpa,
    @JsonKey(name: 'failure_reason') String? failureReason,
    @JsonKey(name: 'completed_at') String? completedAt,
    @JsonKey(name: 'created_at') required String createdAt,
    @JsonKey(name: 'status_history') @Default([]) List<TransactionStatusHistory> statusHistory,
    @JsonKey(name: 'duplicate_flags') @Default([]) List<DuplicateFlag> duplicateFlags,
    // joined fields
    @JsonKey(name: 'customer_name') String? customerName,
    @JsonKey(name: 'invoice_number') String? invoiceNumber,
  }) = _PaymentTransaction;

  factory PaymentTransaction.fromJson(Map<String, dynamic> json) =>
      _$PaymentTransactionFromJson(json);
}

@freezed
abstract class CreateRefundRequest with _$CreateRefundRequest {
  const factory CreateRefundRequest({
    required String amount,
    required String reason,
  }) = _CreateRefundRequest;

  factory CreateRefundRequest.fromJson(Map<String, dynamic> json) =>
      _$CreateRefundRequestFromJson(json);
}
