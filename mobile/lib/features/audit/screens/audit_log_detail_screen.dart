import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../shared/widgets/empty_state.dart';
import '../../../theme/theme.dart';
import '../audit_providers.dart';

class AuditLogDetailScreen extends ConsumerWidget {
  const AuditLogDetailScreen({super.key, required this.logId});

  final String logId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final logAsync = ref.watch(auditLogDetailProvider(logId));
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;

    return logAsync.when(
      loading: () => Scaffold(
        appBar: AppBar(title: const Text('Audit Record')),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (err, _) => Scaffold(
        appBar: AppBar(title: const Text('Audit Record')),
        body: ErrorState(
          message: 'Failed to load log: $err',
          onRetry: () => ref.refresh(auditLogDetailProvider(logId)),
        ),
      ),
      data: (log) {
        final before = log.beforeState ?? {};
        final after = log.afterState ?? {};

        // Find all unique keys across before and after states
        final allKeys = {...before.keys, ...after.keys}.toList()..sort();

        return Scaffold(
          appBar: AppBar(
            title: Text('${log.action} on ${log.entityType}'),
            actions: [
              IconButton(
                icon: const Icon(Icons.refresh_rounded),
                onPressed: () => ref.refresh(auditLogDetailProvider(logId)),
              ),
            ],
          ),
          body: ListView(
            padding: const EdgeInsets.all(AppSpacing.md),
            children: [
              // Metadata card
              Card(
                elevation: 0,
                color: cs.surfaceContainerHighest.withAlpha(40),
                shape: RoundedRectangleBorder(
                  side: BorderSide(color: cs.outlineVariant.withAlpha(80)),
                  borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(AppSpacing.md),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Audit Metadata', style: tt.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                      const SizedBox(height: AppSpacing.sm),
                      _MetaRow(label: 'Action', value: log.action),
                      _MetaRow(label: 'Entity Type', value: log.entityType),
                      _MetaRow(label: 'Entity ID', value: log.entityId),
                      if (log.actorName != null || log.actorUserId != null)
                        _MetaRow(label: 'Actor', value: log.actorName ?? log.actorUserId!),
                      if (log.ipAddress != null) _MetaRow(label: 'IP Address', value: log.ipAddress!),
                      _MetaRow(label: 'Timestamp', value: log.createdAt.substring(0, 19).replaceAll('T', ' ')),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: AppSpacing.lg),

              // Before / After State Diff
              Text('State Difference (Before vs After)', style: tt.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: AppSpacing.xs),
              Text(
                'Green indicates additions/updates; red indicates previous values',
                style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant),
              ),
              const SizedBox(height: AppSpacing.md),

              if (allKeys.isEmpty)
                const Card(
                  child: Padding(
                    padding: EdgeInsets.all(AppSpacing.lg),
                    child: Center(child: Text('No state capture available for this action')),
                  ),
                )
              else
                Card(
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    side: BorderSide(color: cs.outlineVariant.withAlpha(80)),
                    borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(AppSpacing.md),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: allKeys.map((key) {
                        final bVal = before[key];
                        final aVal = after[key];
                        final isChanged = bVal != aVal;

                        return Container(
                          margin: const EdgeInsets.only(bottom: AppSpacing.sm),
                          padding: const EdgeInsets.all(AppSpacing.sm),
                          decoration: BoxDecoration(
                            color: isChanged ? cs.primaryContainer.withAlpha(20) : Colors.transparent,
                            borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
                            border: isChanged ? Border.all(color: cs.primary.withAlpha(60)) : null,
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(key, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                              const SizedBox(height: 4),
                              if (bVal != null && isChanged)
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: Colors.red.withAlpha(30),
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(
                                    '- Before: ${bVal is Map || bVal is List ? jsonEncode(bVal) : bVal.toString()}',
                                    style: const TextStyle(color: Colors.red, fontSize: 12, fontFamily: 'monospace'),
                                  ),
                                ),
                              if (bVal != null && isChanged && aVal != null) const SizedBox(height: 2),
                              if (aVal != null)
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: isChanged ? Colors.green.withAlpha(30) : Colors.grey.withAlpha(20),
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(
                                    '${isChanged ? "+ After: " : ""}${aVal is Map || aVal is List ? jsonEncode(aVal) : aVal.toString()}',
                                    style: TextStyle(
                                      color: isChanged ? Colors.green : cs.onSurface,
                                      fontSize: 12,
                                      fontFamily: 'monospace',
                                    ),
                                  ),
                                ),
                            ],
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                ),
              const SizedBox(height: AppSpacing.xxl),
            ],
          ),
        );
      },
    );
  }
}

class _MetaRow extends StatelessWidget {
  const _MetaRow({required this.label, required this.value});
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant)),
          Flexible(
            child: Text(
              value,
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}
