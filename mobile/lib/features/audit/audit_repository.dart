import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/providers.dart';
import '../../models/audit_models.dart';
import '../../models/paginated_response.dart';

class AuditRepository {
  AuditRepository(this._client);
  final ApiClient _client;

  Future<PaginatedResponse<AuditLog>> listLogs(
    String merchantId, {
    int page = 1,
    int pageSize = 20,
    String? actorUserId,
    String? entityType,
    String? action,
    String? from,
    String? to,
  }) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/audit-logs',
      queryParameters: {
        'page': page,
        'page_size': pageSize,
        'actor_user_id': ?actorUserId,
        if (entityType != null && entityType != 'ALL') 'entity_type': entityType,
        if (action != null && action != 'ALL') 'action': action,
        'from': ?from,
        'to': ?to,
      },
    );
    return PaginatedResponse.fromJson(
      r.data!,
      (j) => AuditLog.fromJson(j as Map<String, dynamic>),
    );
  }

  Future<AuditLog> getLog(String logId) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/audit-logs/$logId',
    );
    return AuditLog.fromJson(r.data!);
  }

  Future<PaginatedResponse<AuditLog>> listAuditLogs(
    String merchantId, {
    int page = 1,
    int pageSize = 20,
    String? actorUserId,
    String? entityType,
    String? action,
    String? from,
    String? to,
  }) =>
      listLogs(
        merchantId,
        page: page,
        pageSize: pageSize,
        actorUserId: actorUserId,
        entityType: entityType,
        action: action,
        from: from,
        to: to,
      );

  Future<AuditLog> getAuditLog(String merchantId, String logId) => getLog(logId);
}

final auditRepositoryProvider = Provider<AuditRepository>((ref) {
  return AuditRepository(ref.watch(apiClientProvider));
});
