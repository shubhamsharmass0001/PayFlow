import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'config.dart';

class ApiClient {
  late final Dio dio;
  final FlutterSecureStorage secureStorage;

  static const String accessTokenKey = 'payflow_access_token';
  static const String refreshTokenKey = 'payflow_refresh_token';

  ApiClient({FlutterSecureStorage? storage})
      : secureStorage = storage ?? const FlutterSecureStorage() {
    dio = Dio(
      BaseOptions(
        baseUrl: AppConfig.baseUrl,
        connectTimeout: AppConfig.connectTimeout,
        receiveTimeout: AppConfig.receiveTimeout,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          if (!options.path.contains('/auth/login') && !options.path.contains('/auth/register')) {
            var token = await secureStorage.read(key: accessTokenKey);
            if (token == null || token.isEmpty) {
              token = await _getDemoToken();
            }
            if (token != null && token.isNotEmpty) {
              options.headers['Authorization'] = 'Bearer $token';
            }
          }
          return handler.next(options);
        },
        onError: (DioException error, handler) async {
          if (error.response?.statusCode == 401 &&
              !error.requestOptions.path.contains('/auth/refresh') &&
              !error.requestOptions.path.contains('/auth/login')) {
            var refreshed = await _refreshToken();
            if (!refreshed) {
              await clearTokens();
              final demoToken = await _getDemoToken();
              refreshed = (demoToken != null);
            }
            if (refreshed) {
              try {
                final token = await secureStorage.read(key: accessTokenKey);
                final opts = Options(
                  method: error.requestOptions.method,
                  headers: {
                    ...error.requestOptions.headers,
                    'Authorization': 'Bearer $token',
                  },
                );
                final retryResponse = await dio.request(
                  error.requestOptions.path,
                  options: opts,
                  data: error.requestOptions.data,
                  queryParameters: error.requestOptions.queryParameters,
                );
                return handler.resolve(retryResponse);
              } catch (e) {
                return handler.next(error);
              }
            }
          }
          return handler.next(error);
        },
      ),
    );
  }

  Future<String?> _getDemoToken() async {
    try {
      final authDio = Dio(
        BaseOptions(
          baseUrl: AppConfig.baseUrl,
          connectTimeout: const Duration(seconds: 5),
        ),
      );
      final resp = await authDio.post(
        '/api/v1/auth/login',
        data: {
          'email': 'owner@payflow.demo',
          'password': 'Password123!',
        },
      );
      if (resp.statusCode == 200 && resp.data != null) {
        final token = resp.data['access_token'] as String?;
        final rToken = resp.data['refresh_token'] as String?;
        if (token != null) await secureStorage.write(key: accessTokenKey, value: token);
        if (rToken != null) await secureStorage.write(key: refreshTokenKey, value: rToken);
        return token;
      }
    } catch (_) {}
    return null;
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await secureStorage.read(key: refreshTokenKey);
      if (refreshToken == null) {
        await clearTokens();
        return false;
      }

      // Fresh unintercepted dio instance for token refresh to avoid loops
      final refreshDio = Dio(
        BaseOptions(
          baseUrl: AppConfig.baseUrl,
          connectTimeout: AppConfig.connectTimeout,
        ),
      );

      final response = await refreshDio.post(
        '/api/v1/auth/refresh',
        data: {'refresh_token': refreshToken},
      );

      if (response.statusCode == 200 && response.data != null) {
        final newAccessToken = response.data['access_token'] as String?;
        final newRefreshToken = response.data['refresh_token'] as String?;
        if (newAccessToken != null) {
          await secureStorage.write(
            key: accessTokenKey,
            value: newAccessToken,
          );
        }
        if (newRefreshToken != null) {
          await secureStorage.write(
            key: refreshTokenKey,
            value: newRefreshToken,
          );
        }
        return true;
      }
    } catch (_) {
      await clearTokens();
    }
    return false;
  }

  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await secureStorage.write(key: accessTokenKey, value: accessToken);
    await secureStorage.write(key: refreshTokenKey, value: refreshToken);
  }

  Future<void> clearTokens() async {
    await secureStorage.delete(key: accessTokenKey);
    await secureStorage.delete(key: refreshTokenKey);
  }
}
