import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/analytics_models.dart';
import 'analytics_repository.dart';

final overviewStatsProvider = FutureProvider.family<OverviewStats, String>((ref, merchantId) async {
  final repo = ref.watch(analyticsRepositoryProvider);
  return repo.getOverviewStats(merchantId);
});

final revenueTrendProvider = FutureProvider.family<RevenueTrend, String>((ref, merchantId) async {
  final repo = ref.watch(analyticsRepositoryProvider);
  return repo.getRevenueTrend(merchantId);
});

final paymentMethodsProvider = FutureProvider.family<List<PaymentMethodStat>, String>((ref, merchantId) async {
  final repo = ref.watch(analyticsRepositoryProvider);
  return repo.getPaymentMethods(merchantId);
});
