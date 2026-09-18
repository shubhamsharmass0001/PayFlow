// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'transaction_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_TransactionStatusHistory _$TransactionStatusHistoryFromJson(
  Map<String, dynamic> json,
) => _TransactionStatusHistory(
  id: json['id'] as String,
  fromStatus: json['from_status'] as String?,
  toStatus: json['to_status'] as String,
  reason: json['reason'] as String?,
  createdAt: json['created_at'] as String,
);

Map<String, dynamic> _$TransactionStatusHistoryToJson(
  _TransactionStatusHistory instance,
) => <String, dynamic>{
  'id': instance.id,
  'from_status': instance.fromStatus,
  'to_status': instance.toStatus,
  'reason': instance.reason,
  'created_at': instance.createdAt,
};

_DuplicateFlag _$DuplicateFlagFromJson(Map<String, dynamic> json) =>
    _DuplicateFlag(
      id: json['id'] as String,
      flagReason: json['flag_reason'] as String,
      confidenceScore: (json['confidence_score'] as num).toDouble(),
      status: json['status'] as String,
      matchReason: json['match_reason'] as String?,
    );

Map<String, dynamic> _$DuplicateFlagToJson(_DuplicateFlag instance) =>
    <String, dynamic>{
      'id': instance.id,
      'flag_reason': instance.flagReason,
      'confidence_score': instance.confidenceScore,
      'status': instance.status,
      'match_reason': instance.matchReason,
    };

_PaymentTransaction _$PaymentTransactionFromJson(
  Map<String, dynamic> json,
) => _PaymentTransaction(
  id: json['id'] as String,
  merchantId: json['merchant_id'] as String,
  invoiceId: json['invoice_id'] as String?,
  customerId: json['customer_id'] as String?,
  idempotencyKey: json['idempotency_key'] as String,
  amount: json['amount'] as String,
  currency: json['currency'] as String? ?? 'INR',
  status:
      $enumDecodeNullable(_$TransactionStatusEnumMap, json['status']) ??
      TransactionStatus.initiated,
  paymentMethod: $enumDecode(_$PaymentMethodEnumMap, json['payment_method']),
  mockScenario: json['mock_scenario'] as String?,
  providerRefId: json['provider_ref_id'] as String?,
  payerVpa: json['payer_vpa'] as String?,
  failureReason: json['failure_reason'] as String?,
  completedAt: json['completed_at'] as String?,
  createdAt: json['created_at'] as String,
  statusHistory:
      (json['status_history'] as List<dynamic>?)
          ?.map(
            (e) => TransactionStatusHistory.fromJson(e as Map<String, dynamic>),
          )
          .toList() ??
      const [],
  duplicateFlags:
      (json['duplicate_flags'] as List<dynamic>?)
          ?.map((e) => DuplicateFlag.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  customerName: json['customer_name'] as String?,
  invoiceNumber: json['invoice_number'] as String?,
);

Map<String, dynamic> _$PaymentTransactionToJson(_PaymentTransaction instance) =>
    <String, dynamic>{
      'id': instance.id,
      'merchant_id': instance.merchantId,
      'invoice_id': instance.invoiceId,
      'customer_id': instance.customerId,
      'idempotency_key': instance.idempotencyKey,
      'amount': instance.amount,
      'currency': instance.currency,
      'status': _$TransactionStatusEnumMap[instance.status]!,
      'payment_method': _$PaymentMethodEnumMap[instance.paymentMethod]!,
      'mock_scenario': instance.mockScenario,
      'provider_ref_id': instance.providerRefId,
      'payer_vpa': instance.payerVpa,
      'failure_reason': instance.failureReason,
      'completed_at': instance.completedAt,
      'created_at': instance.createdAt,
      'status_history': instance.statusHistory,
      'duplicate_flags': instance.duplicateFlags,
      'customer_name': instance.customerName,
      'invoice_number': instance.invoiceNumber,
    };

const _$TransactionStatusEnumMap = {
  TransactionStatus.created: 'CREATED',
  TransactionStatus.initiated: 'INITIATED',
  TransactionStatus.pending: 'PENDING',
  TransactionStatus.success: 'SUCCESS',
  TransactionStatus.failed: 'FAILED',
  TransactionStatus.timeout: 'TIMEOUT',
  TransactionStatus.duplicate: 'DUPLICATE',
  TransactionStatus.refundInitiated: 'REFUND_INITIATED',
  TransactionStatus.refundPending: 'REFUND_PENDING',
  TransactionStatus.refunded: 'REFUNDED',
  TransactionStatus.refundFailed: 'REFUND_FAILED',
  TransactionStatus.partiallyRefunded: 'PARTIALLY_REFUNDED',
};

const _$PaymentMethodEnumMap = {
  PaymentMethod.upiCollect: 'UPI_COLLECT',
  PaymentMethod.upiIntent: 'UPI_INTENT',
  PaymentMethod.upiQr: 'UPI_QR',
  PaymentMethod.card: 'CARD',
  PaymentMethod.netBanking: 'NET_BANKING',
  PaymentMethod.wallet: 'WALLET',
};

_CreateRefundRequest _$CreateRefundRequestFromJson(Map<String, dynamic> json) =>
    _CreateRefundRequest(
      amount: json['amount'] as String,
      reason: json['reason'] as String,
    );

Map<String, dynamic> _$CreateRefundRequestToJson(
  _CreateRefundRequest instance,
) => <String, dynamic>{'amount': instance.amount, 'reason': instance.reason};
