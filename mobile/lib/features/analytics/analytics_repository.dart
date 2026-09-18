import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/providers.dart';
import '../../models/analytics_models.dart';

class AnalyticsRepository {
  AnalyticsRepository(this._client);
  final ApiClient _client;

  Future<OverviewStats> getOverview(String merchantId, {String period = 'today'}) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/analytics/overview',
      queryParameters: {'period': period},
    );
    final data = r.data!;
    return OverviewStats(
      totalCollections: double.tryParse('${data['this_month_collections'] ?? data['today_collections'] ?? data['total_collections'] ?? 0}') ?? 0.0,
      successRate: (data['success_rate'] as num?)?.toDouble() ?? 0.0,
      pendingCount: (data['pending_count'] as num?)?.toInt() ?? 0,
      avgTransactionValue: double.tryParse('${data['average_transaction_value'] ?? data['avg_transaction_value'] ?? 0}') ?? 0.0,
      totalTransactions: (data['this_month_transaction_count'] ?? data['today_transaction_count'] ?? data['total_transactions'] as num?)?.toInt() ?? 0,
      period: (data['period'] as String?) ?? period,
    );
  }

  Future<OverviewStats> getOverviewStats(String merchantId, {String period = 'today'}) =>
      getOverview(merchantId, period: period);

  Future<RevenueTrend> getRevenueTrend(
    String merchantId, {
    String granularity = 'day',
    String? from,
    String? to,
  }) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/analytics/revenue-trend',
      queryParameters: {
        'granularity': granularity,
        'from': ?from,
        'to': ?to,
      },
    );
    final data = r.data!;
    final pointsRaw = (data['points'] as List?) ?? [];
    final points = pointsRaw.map((p) {
      final pMap = p as Map<String, dynamic>;
      return RevenueTrendPoint(
        date: (pMap['date'] ?? pMap['label'] ?? pMap['period'] ?? '') as String,
        amount: double.tryParse('${pMap['amount'] ?? 0}') ?? 0.0,
        count: (pMap['count'] ?? pMap['transaction_count'] as num?)?.toInt() ?? 0,
      );
    }).toList();
    return RevenueTrend(
      points: points,
      granularity: (data['granularity'] as String?) ?? granularity,
      from: (data['from'] ?? data['from_date'] as String?) ?? '',
      to: (data['to'] ?? data['to_date'] as String?) ?? '',
    );
  }

  Future<List<PaymentMethodStat>> getPaymentMethods(String merchantId) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/analytics/payment-methods',
    );
    final rawList = (r.data?['methods_summary'] ?? r.data?['breakdown']) as List? ?? [];
    final List<PaymentMethodStat> result = [];
    for (final item in rawList) {
      if (item is Map) {
        result.add(
          PaymentMethodStat(
            method: (item['payment_method'] ?? item['method'] ?? 'UPI').toString(),
            count: (item['total_count'] ?? item['count'] as num?)?.toInt() ?? 0,
            amount: double.tryParse('${item['total_amount'] ?? item['amount'] ?? 0}') ?? 0.0,
          ),
        );
      }
    }
    return result;
  }
}

final analyticsRepositoryProvider = Provider<AnalyticsRepository>((ref) {
  return AnalyticsRepository(ref.watch(apiClientProvider));
});
