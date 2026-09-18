import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/providers.dart';
import '../../models/notification_models.dart';
import '../../models/paginated_response.dart';

class NotificationRepository {
  NotificationRepository(this._client);
  final ApiClient _client;

  Future<PaginatedResponse<AppNotification>> listNotifications(
    String merchantId, {
    int page = 1,
    int pageSize = 30,
  }) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/notifications',
      queryParameters: {'page': page, 'page_size': pageSize},
    );
    return PaginatedResponse.fromJson(
      r.data!,
      (j) => AppNotification.fromJson(j as Map<String, dynamic>),
    );
  }

  Future<void> markRead(String notificationId) async {
    await _client.dio.patch<void>(
      '/api/v1/notifications/$notificationId/read',
    );
  }

  Future<void> markAsRead(String notificationId) => markRead(notificationId);
}

final notificationRepositoryProvider = Provider<NotificationRepository>((ref) {
  return NotificationRepository(ref.watch(apiClientProvider));
});
