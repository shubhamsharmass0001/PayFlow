import 'package:freezed_annotation/freezed_annotation.dart';

part 'settlement_models.freezed.dart';
part 'settlement_models.g.dart';

enum SettlementStatus {
  @JsonValue('PENDING')    pending,
  @JsonValue('PROCESSING') processing,
  @JsonValue('SETTLED')    settled,
  @JsonValue('FAILED')     failed,
}

@freezed
abstract class SettlementLineItem with _$SettlementLineItem {
  const factory SettlementLineItem({
    required String id,
    @JsonKey(name: 'transaction_id') required String transactionId,
    required String amount,
    @JsonKey(name: 'fee_amount') required String feeAmount,
    @JsonKey(name: 'tax_amount') required String taxAmount,
    @JsonKey(name: 'net_amount') required String netAmount,
    @JsonKey(name: 'created_at') String? createdAt,
  }) = _SettlementLineItem;

  factory SettlementLineItem.fromJson(Map<String, dynamic> json) =>
      _$SettlementLineItemFromJson(json);
}

@freezed
abstract class Settlement with _$Settlement {
  const factory Settlement({
    required String id,
    @JsonKey(name: 'merchant_id') required String merchantId,
    @JsonKey(name: 'settlement_date') required String settlementDate,
    @JsonKey(name: 'settlement_cycle') required String settlementCycle,
    @JsonKey(name: 'transaction_count') required int transactionCount,
    @JsonKey(name: 'gross_amount') required String grossAmount,
    @JsonKey(name: 'mdr_amount') required String mdrAmount,
    @JsonKey(name: 'tax_on_mdr') required String taxOnMdr,
    @JsonKey(name: 'net_amount') required String netAmount,
    @Default(SettlementStatus.pending) SettlementStatus status,
    @JsonKey(name: 'utr_reference') String? utrReference,
    @JsonKey(name: 'bank_account_ref') String? bankAccountRef,
    @JsonKey(name: 'settled_at') String? settledAt,
    @JsonKey(name: 'created_at') String? createdAt,
    @JsonKey(name: 'line_items') @Default([]) List<SettlementLineItem> lineItems,
  }) = _Settlement;

  factory Settlement.fromJson(Map<String, dynamic> json) =>
      _$SettlementFromJson(json);
}
