// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'analytics_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_OverviewStats _$OverviewStatsFromJson(Map<String, dynamic> json) =>
    _OverviewStats(
      totalCollections: (json['total_collections'] as num).toDouble(),
      successRate: (json['success_rate'] as num).toDouble(),
      pendingCount: (json['pending_count'] as num).toInt(),
      avgTransactionValue: (json['avg_transaction_value'] as num).toDouble(),
      totalTransactions: (json['total_transactions'] as num).toInt(),
      period: json['period'] as String,
    );

Map<String, dynamic> _$OverviewStatsToJson(_OverviewStats instance) =>
    <String, dynamic>{
      'total_collections': instance.totalCollections,
      'success_rate': instance.successRate,
      'pending_count': instance.pendingCount,
      'avg_transaction_value': instance.avgTransactionValue,
      'total_transactions': instance.totalTransactions,
      'period': instance.period,
    };

_RevenueTrendPoint _$RevenueTrendPointFromJson(Map<String, dynamic> json) =>
    _RevenueTrendPoint(
      date: json['date'] as String,
      amount: (json['amount'] as num).toDouble(),
      count: (json['count'] as num).toInt(),
    );

Map<String, dynamic> _$RevenueTrendPointToJson(_RevenueTrendPoint instance) =>
    <String, dynamic>{
      'date': instance.date,
      'amount': instance.amount,
      'count': instance.count,
    };

_RevenueTrend _$RevenueTrendFromJson(Map<String, dynamic> json) =>
    _RevenueTrend(
      points: (json['points'] as List<dynamic>)
          .map((e) => RevenueTrendPoint.fromJson(e as Map<String, dynamic>))
          .toList(),
      granularity: json['granularity'] as String,
      from: json['from'] as String,
      to: json['to'] as String,
    );

Map<String, dynamic> _$RevenueTrendToJson(_RevenueTrend instance) =>
    <String, dynamic>{
      'points': instance.points,
      'granularity': instance.granularity,
      'from': instance.from,
      'to': instance.to,
    };

_PaymentMethodStat _$PaymentMethodStatFromJson(Map<String, dynamic> json) =>
    _PaymentMethodStat(
      method: json['method'] as String,
      count: (json['count'] as num).toInt(),
      amount: (json['amount'] as num).toDouble(),
    );

Map<String, dynamic> _$PaymentMethodStatToJson(_PaymentMethodStat instance) =>
    <String, dynamic>{
      'method': instance.method,
      'count': instance.count,
      'amount': instance.amount,
    };
