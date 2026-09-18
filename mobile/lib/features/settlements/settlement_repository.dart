import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/providers.dart';
import '../../models/settlement_models.dart';
import '../../models/paginated_response.dart';

class SettlementRepository {
  SettlementRepository(this._client);
  final ApiClient _client;

  Future<PaginatedResponse<Settlement>> listSettlements(
    String merchantId, {
    int page = 1,
    int pageSize = 20,
    String? from,
    String? to,
    String? startDate,
    String? endDate,
  }) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/settlements',
      queryParameters: {
        'page': page,
        'page_size': pageSize,
        'start_date': ?startDate,
        'end_date': ?endDate,
      },
    );
    return PaginatedResponse.fromJson(
      r.data!,
      (j) => Settlement.fromJson(j as Map<String, dynamic>),
    );
  }

  Future<Settlement> getSettlement(String merchantId, String settlementId) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/settlements/$settlementId',
    );
    return Settlement.fromJson(r.data!);
  }
}

final settlementRepositoryProvider = Provider<SettlementRepository>((ref) {
  return SettlementRepository(ref.watch(apiClientProvider));
});
