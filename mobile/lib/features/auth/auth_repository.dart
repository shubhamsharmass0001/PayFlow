import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/providers.dart';
import '../../models/auth_models.dart';
import '../../models/user_model.dart';

class AuthRepository {
  AuthRepository(this._client);

  final ApiClient _client;

  // ── Login ──────────────────────────────────────────────────────────────────
  Future<LoginResponse> login(LoginRequest req) async {
    final response = await _client.dio.post<Map<String, dynamic>>(
      '/api/v1/auth/login',
      data: req.toJson(),
    );
    final data = response.data!;
    final loginResp = LoginResponse.fromJson(data);

    // Persist tokens immediately
    await _client.saveTokens(
      accessToken: loginResp.accessToken,
      refreshToken: loginResp.refreshToken,
    );
    return loginResp;
  }

  // ── Register ───────────────────────────────────────────────────────────────
  Future<RegisterResponse> register(RegisterRequest req) async {
    final response = await _client.dio.post<Map<String, dynamic>>(
      '/api/v1/auth/register',
      data: req.toJson(),
    );
    return RegisterResponse.fromJson(response.data!);
  }

  // ── Fetch current user ─────────────────────────────────────────────────────
  Future<UserModel> getMe() async {
    final response = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/auth/me',
    );
    return UserModel.fromJson(response.data!);
  }

  // ── Logout ─────────────────────────────────────────────────────────────────
  Future<void> logout() async {
    try {
      await _client.dio.post<void>('/api/v1/auth/logout');
    } on DioException catch (_) {
      // Best-effort — always clear local tokens even if server call fails
    } finally {
      await _client.clearTokens();
    }
  }
}

// ── Provider ──────────────────────────────────────────────────────────────────
final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final client = ref.watch(apiClientProvider);
  return AuthRepository(client);
});
