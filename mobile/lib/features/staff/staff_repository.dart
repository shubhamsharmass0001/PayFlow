import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/providers.dart';
import '../../models/staff_models.dart';
import '../../models/paginated_response.dart';

class StaffRepository {
  StaffRepository(this._client);
  final ApiClient _client;

  Future<PaginatedResponse<MerchantStaff>> listStaff(
    String merchantId, {
    int page = 1,
    int pageSize = 30,
  }) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/staff',
      queryParameters: {'page': page, 'page_size': pageSize},
    );
    return PaginatedResponse.fromJson(
      r.data!,
      (j) => MerchantStaff.fromJson(j as Map<String, dynamic>),
    );
  }

  Future<MerchantStaff> addStaff(
    String merchantId, {
    required String userId,
    required StaffRole role,
    String? storeId,
  }) async {
    final r = await _client.dio.post<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/staff',
      data: {
        'user_id': userId,
        'role': role.name.toUpperCase(),
        'store_id': ?storeId,
      },
    );
    return MerchantStaff.fromJson(r.data!);
  }

  Future<MerchantStaff> updateRole(
    String merchantId,
    String staffId,
    StaffRole role,
  ) async {
    final r = await _client.dio.patch<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/staff/$staffId',
      data: {'role': role.name.toUpperCase()},
    );
    return MerchantStaff.fromJson(r.data!);
  }

  Future<void> removeStaff(String merchantId, String staffId) async {
    await _client.dio.delete<void>(
      '/api/v1/merchants/$merchantId/staff/$staffId',
    );
  }
}

final staffRepositoryProvider = Provider<StaffRepository>((ref) {
  return StaffRepository(ref.watch(apiClientProvider));
});
