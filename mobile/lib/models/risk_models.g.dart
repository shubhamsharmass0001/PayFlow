// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'risk_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_RiskSignal _$RiskSignalFromJson(Map<String, dynamic> json) => _RiskSignal(
  id: json['id'] as String,
  merchantId: json['merchant_id'] as String,
  transactionId: json['transaction_id'] as String?,
  riskScore: (json['risk_score'] as num).toDouble(),
  riskLevel: $enumDecode(_$RiskLevelEnumMap, json['risk_level']),
  ruleTriggered: json['rule_triggered'] as String,
  actionTaken: json['action_taken'] as String,
  isReviewed: json['is_reviewed'] as bool? ?? false,
  resolutionNote: json['resolution_note'] as String?,
  reviewedAt: json['reviewed_at'] as String?,
  createdAt: json['created_at'] as String,
);

Map<String, dynamic> _$RiskSignalToJson(_RiskSignal instance) =>
    <String, dynamic>{
      'id': instance.id,
      'merchant_id': instance.merchantId,
      'transaction_id': instance.transactionId,
      'risk_score': instance.riskScore,
      'risk_level': _$RiskLevelEnumMap[instance.riskLevel]!,
      'rule_triggered': instance.ruleTriggered,
      'action_taken': instance.actionTaken,
      'is_reviewed': instance.isReviewed,
      'resolution_note': instance.resolutionNote,
      'reviewed_at': instance.reviewedAt,
      'created_at': instance.createdAt,
    };

const _$RiskLevelEnumMap = {
  RiskLevel.low: 'LOW',
  RiskLevel.medium: 'MEDIUM',
  RiskLevel.high: 'HIGH',
  RiskLevel.critical: 'CRITICAL',
};
