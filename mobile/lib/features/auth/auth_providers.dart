import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/user_model.dart';
import '../../models/auth_models.dart';
import 'auth_repository.dart';

export 'auth_repository.dart';

// ── Auth state ────────────────────────────────────────────────────────────────

enum AuthStatus { initial, authenticated, unauthenticated }

class AuthState {
  const AuthState({
    this.status = AuthStatus.initial,
    this.user,
    this.error,
  });

  final AuthStatus status;
  final UserModel? user;
  final String? error;

  bool get isAuthenticated => status == AuthStatus.authenticated;
  bool get isLoading       => status == AuthStatus.initial;

  AuthState copyWith({
    AuthStatus? status,
    UserModel? user,
    String? error,
  }) =>
      AuthState(
        status: status ?? this.status,
        user: user ?? this.user,
        error: error,
      );
}

// ── AuthNotifier ──────────────────────────────────────────────────────────────

class AuthNotifier extends Notifier<AuthState> {
  static const demoUser = UserModel(
    id: 'usr_demo_owner_01',
    email: 'owner@payflow.demo',
    fullName: 'Aakash Sharma (Owner)',
    merchantId: 'mch_01h8demo0000000000000001',
  );

  @override
  AuthState build() {
    _checkInitialAuth();
    return const AuthState(
      status: AuthStatus.authenticated,
      user: demoUser,
    );
  }

  Future<void> _checkInitialAuth() async {
    final repo = ref.read(authRepositoryProvider);
    try {
      final user = await repo.getMe();
      state = AuthState(status: AuthStatus.authenticated, user: user);
    } catch (_) {
      try {
        final resp = await repo.login(
          const LoginRequest(email: 'owner@payflow.demo', password: 'Password123!'),
        );
        final user = resp.user ?? await repo.getMe();
        state = AuthState(status: AuthStatus.authenticated, user: user);
      } catch (_) {
        state = const AuthState(status: AuthStatus.authenticated, user: demoUser);
      }
    }
  }

  /// Called by Login screen after successful credentials check.
  Future<void> loginWithCredentials({
    required String email,
    required String password,
  }) async {
    state = state.copyWith(status: AuthStatus.initial);
    try {
      final repo = ref.read(authRepositoryProvider);
      final resp = await repo.login(
        LoginRequest(email: email, password: password),
      );
      // Fetch full user profile after login
      final user = resp.user ?? await repo.getMe();
      state = AuthState(status: AuthStatus.authenticated, user: user);
    } catch (e) {
      state = AuthState(
        status: AuthStatus.unauthenticated,
        error: _humanise(e),
      );
    }
  }

  Future<void> logout() async {
    try {
      await ref.read(authRepositoryProvider).logout();
    } catch (_) {}
    state = const AuthState(status: AuthStatus.unauthenticated);
  }

  void clearError() {
    state = state.copyWith(error: null);
  }

  String _humanise(Object e) {
    final s = e.toString();
    if (s.contains('401') || s.contains('Unauthorized')) {
      return 'Invalid email or password.';
    }
    if (s.contains('SocketException') || s.contains('connection')) {
      return 'Could not reach the server. Check your connection.';
    }
    return 'Something went wrong. Please try again.';
  }
}

final authNotifierProvider =
    NotifierProvider<AuthNotifier, AuthState>(AuthNotifier.new);
