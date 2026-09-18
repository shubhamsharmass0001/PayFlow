import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'api_client.dart';

/// Single source of truth for all core infrastructure providers.
/// Feature-level providers import from here — never instantiate directly.

final secureStorageProvider = Provider<FlutterSecureStorage>((ref) {
  return const FlutterSecureStorage();
});

final apiClientProvider = Provider<ApiClient>((ref) {
  final storage = ref.watch(secureStorageProvider);

  // onLogout is wired lazily — the router's redirect will observe
  // authNotifierProvider and redirect to /login automatically when
  // AuthStatus becomes unauthenticated. The client just clears tokens.
  return ApiClient(storage: storage);
});

class ActiveMerchantNotifier extends Notifier<String> {
  @override
  String build() {
    // Watch user in authNotifierProvider if available
    return '00000000-0000-0000-0000-000000000001';
  }

  void setMerchantId(String id) => state = id;
}

final activeMerchantIdProvider =
    NotifierProvider<ActiveMerchantNotifier, String>(ActiveMerchantNotifier.new);

class UserRoleNotifier extends Notifier<String> {
  @override
  String build() => 'OWNER';

  void setRole(String role) => state = role;
}

final userRoleProvider =
    NotifierProvider<UserRoleNotifier, String>(UserRoleNotifier.new);

