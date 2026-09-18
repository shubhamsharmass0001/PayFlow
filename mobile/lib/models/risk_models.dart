import 'package:freezed_annotation/freezed_annotation.dart';

part 'risk_models.freezed.dart';
part 'risk_models.g.dart';

enum RiskLevel {
  @JsonValue('LOW')      low,
  @JsonValue('MEDIUM')   medium,
  @JsonValue('HIGH')     high,
  @JsonValue('CRITICAL') critical,
}

@freezed
abstract class RiskSignal with _$RiskSignal {
  const factory RiskSignal({
    required String id,
    @JsonKey(name: 'merchant_id') required String merchantId,
    @JsonKey(name: 'transaction_id') String? transactionId,
    @JsonKey(name: 'risk_score') required double riskScore,
    @JsonKey(name: 'risk_level') required RiskLevel riskLevel,
    @JsonKey(name: 'rule_triggered') required String ruleTriggered,
    @JsonKey(name: 'action_taken') required String actionTaken,
    @JsonKey(name: 'is_reviewed') @Default(false) bool isReviewed,
    @JsonKey(name: 'resolution_note') String? resolutionNote,
    @JsonKey(name: 'reviewed_at') String? reviewedAt,
    @JsonKey(name: 'created_at') required String createdAt,
  }) = _RiskSignal;

  factory RiskSignal.fromJson(Map<String, dynamic> json) =>
      _$RiskSignalFromJson(json);
}
