import 'package:flutter/foundation.dart';

class AppConfig {
  /// Base API URL configured via --dart-define=BASE_URL=https://api.example.com
  static const String _definedBaseUrl = String.fromEnvironment('BASE_URL');

  /// Fallback base URL depending on execution environment:
  /// - Android Emulator: `10.0.2.2:8000`
  /// - iOS Simulator / macOS / Desktop / Web: `127.0.0.1:8000` / `localhost:8000`
  /// - Physical device: override via `--dart-define=BASE_URL=http://<YOUR_LAN_IP>:8000`
  static String get baseUrl {
    if (_definedBaseUrl.isNotEmpty) {
      return _definedBaseUrl;
    }

    if (kIsWeb) {
      return 'http://localhost:8000';
    }

    if (defaultTargetPlatform == TargetPlatform.android) {
      return 'http://10.0.2.2:8000';
    }

    // iOS simulator / desktop default
    return 'http://localhost:8000';
  }

  static const Duration connectTimeout = Duration(seconds: 15);
  static const Duration receiveTimeout = Duration(seconds: 15);
}
