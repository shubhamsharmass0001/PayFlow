import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/providers.dart';
import '../../models/risk_models.dart';
import '../../models/paginated_response.dart';

class RiskRepository {
  RiskRepository(this._client);
  final ApiClient _client;

  Future<PaginatedResponse<RiskSignal>> listSignals(
    String merchantId, {
    int page = 1,
    int pageSize = 20,
    String? severity,
    bool? reviewed,
  }) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/risk/signals',
      queryParameters: {
        'page': page,
        'page_size': pageSize,
        if (severity != null && severity != 'ALL') 'severity': severity,
        'reviewed': ?reviewed,
      },
    );
    return PaginatedResponse.fromJson(
      r.data!,
      (j) => RiskSignal.fromJson(j as Map<String, dynamic>),
    );
  }

  Future<RiskSignal> reviewSignal(
    String signalId, {
    required String resolutionNote,
  }) async {
    final r = await _client.dio.patch<Map<String, dynamic>>(
      '/api/v1/risk/signals/$signalId/review',
      data: {'resolution_note': resolutionNote},
    );
    return RiskSignal.fromJson(r.data!);
  }
}

final riskRepositoryProvider = Provider<RiskRepository>((ref) {
  return RiskRepository(ref.watch(apiClientProvider));
});
