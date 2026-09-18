import 'package:freezed_annotation/freezed_annotation.dart';

part 'analytics_models.freezed.dart';
part 'analytics_models.g.dart';

@freezed
abstract class OverviewStats with _$OverviewStats {
  const factory OverviewStats({
    @JsonKey(name: 'total_collections') required double totalCollections,
    @JsonKey(name: 'success_rate') required double successRate,
    @JsonKey(name: 'pending_count') required int pendingCount,
    @JsonKey(name: 'avg_transaction_value') required double avgTransactionValue,
    @JsonKey(name: 'total_transactions') required int totalTransactions,
    @JsonKey(name: 'period') required String period,
  }) = _OverviewStats;

  factory OverviewStats.fromJson(Map<String, dynamic> json) =>
      _$OverviewStatsFromJson(json);
}

@freezed
abstract class RevenueTrendPoint with _$RevenueTrendPoint {
  const factory RevenueTrendPoint({
    required String date,
    required double amount,
    required int count,
  }) = _RevenueTrendPoint;

  factory RevenueTrendPoint.fromJson(Map<String, dynamic> json) =>
      _$RevenueTrendPointFromJson(json);
}

@freezed
abstract class RevenueTrend with _$RevenueTrend {
  const factory RevenueTrend({
    required List<RevenueTrendPoint> points,
    required String granularity,
    required String from,
    required String to,
  }) = _RevenueTrend;

  factory RevenueTrend.fromJson(Map<String, dynamic> json) =>
      _$RevenueTrendFromJson(json);
}

@freezed
abstract class PaymentMethodStat with _$PaymentMethodStat {
  const factory PaymentMethodStat({
    required String method,
    required int count,
    required double amount,
  }) = _PaymentMethodStat;

  factory PaymentMethodStat.fromJson(Map<String, dynamic> json) =>
      _$PaymentMethodStatFromJson(json);
}
