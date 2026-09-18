// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'settlement_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_SettlementLineItem _$SettlementLineItemFromJson(Map<String, dynamic> json) =>
    _SettlementLineItem(
      id: json['id'] as String,
      transactionId: json['transaction_id'] as String,
      amount: json['amount'] as String,
      feeAmount: json['fee_amount'] as String,
      taxAmount: json['tax_amount'] as String,
      netAmount: json['net_amount'] as String,
      createdAt: json['created_at'] as String?,
    );

Map<String, dynamic> _$SettlementLineItemToJson(_SettlementLineItem instance) =>
    <String, dynamic>{
      'id': instance.id,
      'transaction_id': instance.transactionId,
      'amount': instance.amount,
      'fee_amount': instance.feeAmount,
      'tax_amount': instance.taxAmount,
      'net_amount': instance.netAmount,
      'created_at': instance.createdAt,
    };

_Settlement _$SettlementFromJson(Map<String, dynamic> json) => _Settlement(
  id: json['id'] as String,
  merchantId: json['merchant_id'] as String,
  settlementDate: json['settlement_date'] as String,
  settlementCycle: json['settlement_cycle'] as String,
  transactionCount: (json['transaction_count'] as num).toInt(),
  grossAmount: json['gross_amount'] as String,
  mdrAmount: json['mdr_amount'] as String,
  taxOnMdr: json['tax_on_mdr'] as String,
  netAmount: json['net_amount'] as String,
  status:
      $enumDecodeNullable(_$SettlementStatusEnumMap, json['status']) ??
      SettlementStatus.pending,
  utrReference: json['utr_reference'] as String?,
  bankAccountRef: json['bank_account_ref'] as String?,
  settledAt: json['settled_at'] as String?,
  createdAt: json['created_at'] as String?,
  lineItems:
      (json['line_items'] as List<dynamic>?)
          ?.map((e) => SettlementLineItem.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
);

Map<String, dynamic> _$SettlementToJson(_Settlement instance) =>
    <String, dynamic>{
      'id': instance.id,
      'merchant_id': instance.merchantId,
      'settlement_date': instance.settlementDate,
      'settlement_cycle': instance.settlementCycle,
      'transaction_count': instance.transactionCount,
      'gross_amount': instance.grossAmount,
      'mdr_amount': instance.mdrAmount,
      'tax_on_mdr': instance.taxOnMdr,
      'net_amount': instance.netAmount,
      'status': _$SettlementStatusEnumMap[instance.status]!,
      'utr_reference': instance.utrReference,
      'bank_account_ref': instance.bankAccountRef,
      'settled_at': instance.settledAt,
      'created_at': instance.createdAt,
      'line_items': instance.lineItems,
    };

const _$SettlementStatusEnumMap = {
  SettlementStatus.pending: 'PENDING',
  SettlementStatus.processing: 'PROCESSING',
  SettlementStatus.settled: 'SETTLED',
  SettlementStatus.failed: 'FAILED',
};
