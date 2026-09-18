import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../theme/theme.dart';
import '../features/auth/auth_providers.dart';
import '../features/staff/staff_providers.dart';
import '../features/audit/audit_providers.dart';

/// Nav destination used by both bottom bar and Drawer.
class _NavItem {
  const _NavItem({
    required this.label,
    required this.icon,
    required this.selectedIcon,
    required this.path,
  });
  final String label;
  final IconData icon;
  final IconData selectedIcon;
  final String path;
}

// ── All 13 app sections ────────────────────────────────────────────────────────
const _allItems = [
  // 0 — bottom bar tab 0
  _NavItem(
    label: 'Dashboard',
    icon: Icons.dashboard_outlined,
    selectedIcon: Icons.dashboard_rounded,
    path: '/dashboard',
  ),
  // 1 — bottom bar tab 1
  _NavItem(
    label: 'Invoices',
    icon: Icons.receipt_long_outlined,
    selectedIcon: Icons.receipt_long_rounded,
    path: '/invoices',
  ),
  // 2 — bottom bar tab 2
  _NavItem(
    label: 'Collect',
    icon: Icons.qr_code_scanner_outlined,
    selectedIcon: Icons.qr_code_scanner_rounded,
    path: '/collect',
  ),
  // 3 — bottom bar tab 3
  _NavItem(
    label: 'Transactions',
    icon: Icons.swap_horiz_outlined,
    selectedIcon: Icons.swap_horiz_rounded,
    path: '/transactions',
  ),
  // 4–12 — Drawer-only
  _NavItem(
    label: 'Customers',
    icon: Icons.people_outline,
    selectedIcon: Icons.people_rounded,
    path: '/customers',
  ),
  _NavItem(
    label: 'Settlements',
    icon: Icons.account_balance_outlined,
    selectedIcon: Icons.account_balance_rounded,
    path: '/settlements',
  ),
  _NavItem(
    label: 'Analytics',
    icon: Icons.bar_chart_outlined,
    selectedIcon: Icons.bar_chart_rounded,
    path: '/analytics',
  ),
  _NavItem(
    label: 'Staff',
    icon: Icons.badge_outlined,
    selectedIcon: Icons.badge_rounded,
    path: '/staff',
  ),
  _NavItem(
    label: 'Notifications',
    icon: Icons.notifications_outlined,
    selectedIcon: Icons.notifications_rounded,
    path: '/notifications',
  ),
  _NavItem(
    label: 'Audit Logs',
    icon: Icons.history_outlined,
    selectedIcon: Icons.history_rounded,
    path: '/audit-logs',
  ),
  _NavItem(
    label: 'Risk Alerts',
    icon: Icons.gpp_maybe_outlined,
    selectedIcon: Icons.gpp_maybe_rounded,
    path: '/risk-alerts',
  ),
  _NavItem(
    label: 'AI Assistant',
    icon: Icons.auto_awesome_outlined,
    selectedIcon: Icons.auto_awesome_rounded,
    path: '/ai-assistant',
  ),
  _NavItem(
    label: 'Settings',
    icon: Icons.settings_outlined,
    selectedIcon: Icons.settings_rounded,
    path: '/settings',
  ),
];

// First 4 items appear in the bottom nav bar.
final _bottomBarItems = [
  _allItems[0],
  _allItems[1],
  _allItems[2],
  _allItems[3],
];

// ── Shell widget ───────────────────────────────────────────────────────────────

class AppShell extends ConsumerWidget {
  const AppShell({super.key, required this.navigationShell});

  final StatefulNavigationShell navigationShell;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final location     = GoRouterState.of(context).uri.path;
    final currentPath  = _resolveActivePath(location);
    final bottomIndex  = _bottomBarItems.indexWhere((i) => i.path == currentPath);
    final isBottomTab  = bottomIndex != -1;

    return Scaffold(
      drawer: _AppDrawer(
        currentPath: currentPath,
        onNavigate: (path) {
          Navigator.of(context).pop();  // close drawer
          _navigateTo(context, path, navigationShell);
        },
        onLogout: () async {
          Navigator.of(context).pop();
          await ref.read(authNotifierProvider.notifier).logout();
        },
        ref: ref,
      ),
      body: navigationShell,
      bottomNavigationBar: NavigationBar(
        selectedIndex: isBottomTab ? bottomIndex : 0,
        onDestinationSelected: (i) =>
            _navigateTo(context, _bottomBarItems[i].path, navigationShell),
        destinations: _bottomBarItems
            .map(
              (item) => NavigationDestination(
                icon: Icon(item.icon),
                selectedIcon: Icon(item.selectedIcon),
                label: item.label,
              ),
            )
            .toList(),
      ),
    );
  }

  String _resolveActivePath(String location) {
    for (final item in _allItems) {
      if (location == item.path || location.startsWith('${item.path}/')) {
        return item.path;
      }
    }
    return '/dashboard';
  }

  void _navigateTo(
    BuildContext context,
    String path,
    StatefulNavigationShell shell,
  ) {
    final bottomIndex = _bottomBarItems.indexWhere((i) => i.path == path);
    if (bottomIndex != -1) {
      shell.goBranch(bottomIndex, initialLocation: bottomIndex == shell.currentIndex);
    } else {
      context.go(path);
    }
  }
}

// ── Drawer ─────────────────────────────────────────────────────────────────────

class _AppDrawer extends StatelessWidget {
  const _AppDrawer({
    required this.currentPath,
    required this.onNavigate,
    required this.onLogout,
    required this.ref,
  });
  final String currentPath;
  final ValueChanged<String> onNavigate;
  final VoidCallback onLogout;
  final WidgetRef ref;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;
    final user = ref.watch(authNotifierProvider).user;
    final canManageStaff = ref.watch(canManageStaffProvider);
    final canViewAuditLogs = ref.watch(canViewAuditLogsProvider);

    return Drawer(
      child: SafeArea(
        child: Column(
          children: [
            // ── Header ───────────────────────────────────────────────────
            Padding(
              padding: const EdgeInsets.all(AppSpacing.lg),
              child: Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [cs.primary, cs.secondary],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
                    ),
                    child: Icon(Icons.account_balance_wallet_rounded,
                        color: cs.onPrimary, size: 22),
                  ),
                  const SizedBox(width: AppSpacing.md),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'PayFlow',
                          style: tt.titleMedium?.copyWith(fontWeight: FontWeight.w800),
                        ),
                        if (user?.fullName != null)
                          Text(
                            user!.fullName!,
                            style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const Divider(height: 1),
            // ── Nav items ────────────────────────────────────────────────
            Expanded(
              child: ListView(
                padding: const EdgeInsets.symmetric(
                  vertical: AppSpacing.sm,
                  horizontal: AppSpacing.sm,
                ),
                children: [
                  // Section: core (bottom bar items shown in drawer too)
                  _SectionLabel(label: 'Core', tt: tt),
                  ..._bottomBarItems.map((item) => _DrawerTile(
                        item: item,
                        isSelected: currentPath == item.path,
                        onTap: () => onNavigate(item.path),
                        cs: cs,
                        tt: tt,
                      )),
                  const SizedBox(height: AppSpacing.sm),
                  _SectionLabel(label: 'Finance', tt: tt),
                  ...[_allItems[4], _allItems[5], _allItems[6]].map(
                    (item) => _DrawerTile(
                      item: item,
                      isSelected: currentPath == item.path,
                      onTap: () => onNavigate(item.path),
                      cs: cs,
                      tt: tt,
                    ),
                  ),
                  const SizedBox(height: AppSpacing.sm),
                  _SectionLabel(label: 'Operations', tt: tt),
                  ...[
                    if (canManageStaff) _allItems[7],
                    _allItems[8],
                    if (canViewAuditLogs) _allItems[9],
                    _allItems[10],
                  ].map(
                    (item) => _DrawerTile(
                      item: item,
                      isSelected: currentPath == item.path,
                      onTap: () => onNavigate(item.path),
                      cs: cs,
                      tt: tt,
                    ),
                  ),
                  const SizedBox(height: AppSpacing.sm),
                  _SectionLabel(label: 'Intelligence', tt: tt),
                  _DrawerTile(
                    item: _allItems[11],
                    isSelected: currentPath == _allItems[11].path,
                    onTap: () => onNavigate(_allItems[11].path),
                    cs: cs,
                    tt: tt,
                  ),
                ],
              ),
            ),
            const Divider(height: 1),
            // ── Footer: Settings + Logout ────────────────────────────────
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.sm,
                vertical: AppSpacing.sm,
              ),
              child: Column(
                children: [
                  _DrawerTile(
                    item: _allItems[12],
                    isSelected: currentPath == _allItems[12].path,
                    onTap: () => onNavigate(_allItems[12].path),
                    cs: cs,
                    tt: tt,
                  ),
                  ListTile(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
                    ),
                    leading: Icon(
                      Icons.logout_rounded,
                      color: cs.error,
                    ),
                    title: Text(
                      'Sign out',
                      style: tt.bodyMedium?.copyWith(
                        color: cs.error,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    onTap: onLogout,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DrawerTile extends StatelessWidget {
  const _DrawerTile({
    required this.item,
    required this.isSelected,
    required this.onTap,
    required this.cs,
    required this.tt,
  });
  final _NavItem item;
  final bool isSelected;
  final VoidCallback onTap;
  final ColorScheme cs;
  final TextTheme tt;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      dense: true,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
      ),
      selected: isSelected,
      selectedTileColor: cs.primaryContainer.withAlpha(128),
      leading: Icon(
        isSelected ? item.selectedIcon : item.icon,
        color: isSelected ? cs.primary : cs.onSurfaceVariant,
        size: AppSpacing.iconMd,
      ),
      title: Text(
        item.label,
        style: tt.bodyMedium?.copyWith(
          color: isSelected ? cs.primary : cs.onSurface,
          fontWeight: isSelected ? FontWeight.w700 : FontWeight.w400,
        ),
      ),
      onTap: onTap,
    );
  }
}

class _SectionLabel extends StatelessWidget {
  const _SectionLabel({required this.label, required this.tt});
  final String label;
  final TextTheme tt;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(
        left: AppSpacing.md,
        bottom: AppSpacing.xs,
        top: AppSpacing.xs,
      ),
      child: Text(
        label.toUpperCase(),
        style: tt.labelSmall?.copyWith(
          letterSpacing: 1.2,
          color: Theme.of(context).colorScheme.onSurfaceVariant,
        ),
      ),
    );
  }
}

// ── Placeholder screens for not-yet-built sections ─────────────────────────────

class PlaceholderScreen extends StatelessWidget {
  const PlaceholderScreen({super.key, required this.title});
  final String title;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;

    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.construction_rounded,
              size: AppSpacing.iconXl,
              color: cs.primary.withAlpha(128),
            ),
            const SizedBox(height: AppSpacing.md),
            Text(title, style: tt.titleLarge),
            const SizedBox(height: AppSpacing.sm),
            Text(
              'Coming in a future phase',
              style: tt.bodyMedium?.copyWith(color: cs.onSurfaceVariant),
            ),
          ],
        ),
      ),
    );
  }
}
