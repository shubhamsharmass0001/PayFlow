import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../features/ai_assistant/screens/ai_assistant_screen.dart';
import '../features/analytics/screens/dashboard_screen.dart';
import '../features/audit/screens/audit_log_detail_screen.dart';
import '../features/audit/screens/audit_logs_screen.dart';
import '../features/auth/auth_providers.dart';
import '../features/auth/screens/login_screen.dart';
import '../features/auth/screens/register_screen.dart';
import '../features/auth/screens/settings_screen.dart';
import '../features/customers/screens/customer_detail_screen.dart';
import '../features/customers/screens/customers_screen.dart';
import '../features/invoices/screens/invoice_detail_screen.dart';
import '../features/invoices/screens/invoice_form_screen.dart';
import '../features/invoices/screens/invoices_screen.dart';
import '../features/merchants/screens/kyc_screen.dart';
import '../features/merchants/screens/merchant_setup_screen.dart';
import '../features/notifications/screens/notifications_screen.dart';
import '../features/risk/screens/risk_alerts_screen.dart';
import '../features/settlements/screens/settlement_detail_screen.dart';
import '../features/settlements/screens/settlements_screen.dart';
import '../features/staff/screens/staff_screen.dart';
import '../features/transactions/screens/transaction_detail_screen.dart';
import '../features/transactions/screens/transactions_screen.dart';
import '../features/upi_qr/screens/collect_screen.dart';
import '../shell/app_shell.dart';

// ── RouterNotifier: bridges Riverpod → go_router refresh ──────────────────────

class RouterNotifier extends ChangeNotifier {
  RouterNotifier(this._ref) {
    _ref.listen<AuthState>(
      authNotifierProvider,
      (_, _) => notifyListeners(),
    );
  }

  final Ref _ref;

  String? redirect(BuildContext context, GoRouterState state) {
    final authState = _ref.read(authNotifierProvider);
    final location = state.uri.path;

    final isLoading = authState.status == AuthStatus.initial;
    final isAuthenticated = authState.status == AuthStatus.authenticated;

    if (isLoading) return null;

    if (location == '/' || location == '/login') {
      return '/dashboard';
    }

    if (isAuthenticated && location == '/register') {
      return '/dashboard';
    }

    return null;
  }
}

// ── Provider ───────────────────────────────────────────────────────────────────

final routerProvider = Provider<GoRouter>((ref) {
  final notifier = RouterNotifier(ref);

  return GoRouter(
    debugLogDiagnostics: true,
    initialLocation: '/dashboard',
    refreshListenable: notifier,
    redirect: notifier.redirect,
    routes: [
      // ── Auth ──────────────────────────────────────────────────────────────
      GoRoute(
        path: '/login',
        name: 'login',
        pageBuilder: (context, state) => _fadeTransition(
          state: state,
          child: const LoginScreen(),
        ),
      ),
      GoRoute(
        path: '/register',
        name: 'register',
        pageBuilder: (context, state) => _slideTransition(
          state: state,
          child: const RegisterScreen(),
        ),
      ),

      // ── Onboarding ────────────────────────────────────────────────────────
      GoRoute(
        path: '/onboarding/merchant-setup',
        name: 'merchantSetup',
        pageBuilder: (context, state) => _slideTransition(
          state: state,
          child: const MerchantSetupScreen(),
        ),
      ),
      GoRoute(
        path: '/onboarding/kyc',
        name: 'kyc',
        pageBuilder: (context, state) => _slideTransition(
          state: state,
          child: const KycScreen(),
        ),
      ),

      // ── Authenticated shell (StatefulShellRoute) ──────────────────────────
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) =>
            AppShell(navigationShell: navigationShell),
        branches: [
          // Branch 0 — Dashboard
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/dashboard',
                name: 'dashboard',
                builder: (context, state) => const DashboardScreen(),
              ),
            ],
          ),
          // Branch 1 — Invoices
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/invoices',
                name: 'invoices',
                builder: (context, state) => const InvoicesScreen(),
                routes: [
                  GoRoute(
                    path: 'create',
                    name: 'invoiceCreate',
                    builder: (context, state) => const InvoiceFormScreen(),
                  ),
                  GoRoute(
                    path: ':id',
                    name: 'invoiceDetail',
                    builder: (context, state) => InvoiceDetailScreen(
                      invoiceId: state.pathParameters['id']!,
                    ),
                  ),
                ],
              ),
            ],
          ),
          // Branch 2 — Collect
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/collect',
                name: 'collect',
                builder: (context, state) => const CollectScreen(),
              ),
            ],
          ),
          // Branch 3 — Transactions
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/transactions',
                name: 'transactions',
                builder: (context, state) => const TransactionsScreen(),
                routes: [
                  GoRoute(
                    path: ':id',
                    name: 'transactionDetail',
                    builder: (context, state) => TransactionDetailScreen(
                      transactionId: state.pathParameters['id']!,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),

      // ── Drawer-accessible routes ──────────────────────────────────────────
      GoRoute(
        path: '/customers',
        name: 'customers',
        builder: (context, state) => const CustomersScreen(),
        routes: [
          GoRoute(
            path: ':id',
            name: 'customerDetail',
            builder: (context, state) => CustomerDetailScreen(
              customerId: state.pathParameters['id']!,
            ),
          ),
        ],
      ),
      GoRoute(
        path: '/settlements',
        name: 'settlements',
        builder: (context, state) => const SettlementsScreen(),
        routes: [
          GoRoute(
            path: ':id',
            name: 'settlementDetail',
            builder: (context, state) => SettlementDetailScreen(
              settlementId: state.pathParameters['id']!,
            ),
          ),
        ],
      ),
      GoRoute(
        path: '/analytics',
        name: 'analytics',
        builder: (context, state) => const DashboardScreen(),
      ),
      GoRoute(
        path: '/staff',
        name: 'staff',
        builder: (context, state) => const StaffScreen(),
      ),
      GoRoute(
        path: '/notifications',
        name: 'notifications',
        builder: (context, state) => const NotificationsScreen(),
      ),
      GoRoute(
        path: '/audit-logs',
        name: 'auditLogs',
        builder: (context, state) => const AuditLogsScreen(),
        routes: [
          GoRoute(
            path: ':id',
            name: 'auditLogDetail',
            builder: (context, state) => AuditLogDetailScreen(
              logId: state.pathParameters['id']!,
            ),
          ),
        ],
      ),
      GoRoute(
        path: '/risk-alerts',
        name: 'riskAlerts',
        builder: (context, state) => const RiskAlertsScreen(),
      ),
      GoRoute(
        path: '/ai-assistant',
        name: 'aiAssistant',
        builder: (context, state) => const AiAssistantScreen(),
      ),
      GoRoute(
        path: '/settings',
        name: 'settings',
        builder: (context, state) => const SettingsScreen(),
      ),
    ],
  );
});

// ── Page transitions ───────────────────────────────────────────────────────────

CustomTransitionPage<void> _fadeTransition({
  required GoRouterState state,
  required Widget child,
}) =>
    CustomTransitionPage(
      key: state.pageKey,
      child: child,
      transitionsBuilder: (ctx, animation, _, child) =>
          FadeTransition(opacity: animation, child: child),
      transitionDuration: const Duration(milliseconds: 300),
    );

CustomTransitionPage<void> _slideTransition({
  required GoRouterState state,
  required Widget child,
}) =>
    CustomTransitionPage(
      key: state.pageKey,
      child: child,
      transitionsBuilder: (ctx, animation, _, child) {
        final tween = Tween(
          begin: const Offset(1, 0),
          end: Offset.zero,
        ).chain(CurveTween(curve: Curves.easeInOutCubic));
        return SlideTransition(
          position: animation.drive(tween),
          child: child,
        );
      },
      transitionDuration: const Duration(milliseconds: 350),
    );
