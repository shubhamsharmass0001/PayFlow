import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../models/audit_models.dart';
import '../../../shared/widgets/empty_state.dart';
import '../../../shared/widgets/paginated_list_view.dart';
import '../../../theme/theme.dart';
import '../audit_providers.dart';

class AuditLogsScreen extends ConsumerWidget {
  const AuditLogsScreen({super.key});

  static const _actions = [
    'ALL',
    'CREATE',
    'UPDATE',
    'REFUND',
    'STATUS_CHANGE',
    'DELETE',
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final canView = ref.watch(canViewAuditLogsProvider);
    final cs = Theme.of(context).colorScheme;

    // RBAC: Auditor / Owner only!
    if (!canView) {
      return Scaffold(
        appBar: AppBar(title: const Text('Audit Logs')),
        body: const EmptyState(
          title: 'Auditor Access Only',
          subtitle: 'Audit logs and system change tracking are restricted to Auditors and Organization Owners.',
          icon: Icons.security_rounded,
        ),
      );
    }

    final state = ref.watch(auditLogListProvider);
    final notifier = ref.read(auditLogListProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Audit Logs'),
      ),
      body: Column(
        children: [
          // Filter Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: AppSpacing.xs),
            child: Row(
              children: _actions.map((act) {
                final isAll = act == 'ALL';
                final isSelected = isAll ? (state.action == null) : (state.action == act);

                return Padding(
                  padding: const EdgeInsets.only(right: AppSpacing.xs),
                  child: FilterChip(
                    label: Text(act),
                    selected: isSelected,
                    onSelected: (_) {
                      notifier.setActionFilter(isAll ? null : act);
                    },
                  ),
                );
              }).toList(),
            ),
          ),
          const Divider(height: 1),

          Expanded(
            child: PaginatedListView<AuditLog>(
              items: state.items,
              isLoading: state.isLoading,
              hasMore: state.hasMore,
              error: state.error,
              onLoadMore: () => notifier.loadMore(),
              onRefresh: () async => notifier.loadFirstPage(),
              emptyTitle: 'No Audit Records',
              emptySubtitle: 'System mutations and state transitions will be recorded here',
              emptyIcon: Icons.history_rounded,
              itemBuilder: (log) {
                return Card(
                  margin: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: 4),
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    side: BorderSide(color: cs.outlineVariant.withAlpha(60)),
                    borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
                  ),
                  child: ListTile(
                    onTap: () => context.go('/audit-logs/${log.id}'),
                    leading: Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: cs.surfaceContainerHighest,
                        borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
                      ),
                      child: Icon(Icons.history_rounded, color: cs.primary, size: 20),
                    ),
                    title: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          '${log.action} ${log.entityType}',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: cs.secondaryContainer.withAlpha(80),
                            borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                          ),
                          child: Text(
                            log.entityType,
                            style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: cs.onSecondaryContainer),
                          ),
                        ),
                      ],
                    ),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 2),
                        Text(
                          'Actor: ${log.actorName ?? log.actorUserId ?? "System"} • IP: ${log.ipAddress ?? "Internal"}',
                          style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          log.createdAt.substring(0, 19).replaceAll('T', ' '),
                          style: TextStyle(fontSize: 11, color: cs.onSurfaceVariant),
                        ),
                      ],
                    ),
                    trailing: const Icon(Icons.chevron_right_rounded),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
