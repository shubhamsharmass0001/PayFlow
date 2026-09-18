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
    return OverviewStats.fromJson(r.data!);
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
    return RevenueTrend.fromJson(r.data!);
  }

  Future<List<PaymentMethodStat>> getPaymentMethods(String merchantId) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/analytics/payment-methods',
    );
    final list = (r.data!['breakdown'] as List?) ?? [];
    return list.cast<Map<String, dynamic>>().map(PaymentMethodStat.fromJson).toList();
  }
}

final analyticsRepositoryProvider = Provider<AnalyticsRepository>((ref) {
  return AnalyticsRepository(ref.watch(apiClientProvider));
});
