import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../models/risk_models.dart';
import '../../../shared/widgets/paginated_list_view.dart';
import '../../../shared/widgets/status_badge.dart';
import '../../../theme/theme.dart';
import '../risk_providers.dart';

class RiskAlertsScreen extends ConsumerWidget {
  const RiskAlertsScreen({super.key});

  static const _severities = [
    'ALL',
    'CRITICAL',
    'HIGH',
    'MEDIUM',
    'LOW',
  ];

  void _showReviewSheet(BuildContext context, WidgetRef ref, RiskSignal signal) {
    final noteCtrl = TextEditingController(text: 'Reviewed and confirmed legitimate transaction.');
    final formKey = GlobalKey<FormState>();
    bool submitting = false;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setStateModal) {
          final cs = Theme.of(ctx).colorScheme;
          return Container(
            decoration: BoxDecoration(
              color: cs.surface,
              borderRadius: const BorderRadius.vertical(top: Radius.circular(AppSpacing.radiusXl)),
            ),
            padding: EdgeInsets.only(
              bottom: MediaQuery.of(ctx).viewInsets.bottom + AppSpacing.lg,
              top: AppSpacing.md,
              left: AppSpacing.lg,
              right: AppSpacing.lg,
            ),
            child: SafeArea(
              child: Form(
                key: formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Center(
                      child: Container(
                        width: 36,
                        height: 4,
                        decoration: BoxDecoration(
                          color: cs.outlineVariant,
                          borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                        ),
                      ),
                    ),
                    const SizedBox(height: AppSpacing.md),
                    Text('Review Risk Signal', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                    const SizedBox(height: 4),
                    Text('Rule: ${signal.ruleTriggered} • Score: ${signal.riskScore.toStringAsFixed(2)}', style: TextStyle(color: cs.onSurfaceVariant)),
                    const SizedBox(height: AppSpacing.md),
                    TextFormField(
                      controller: noteCtrl,
                      maxLines: 3,
                      decoration: const InputDecoration(
                        labelText: 'Resolution / Audit Note *',
                        hintText: 'Describe review findings, merchant contact, or explanation...',
                      ),
                      validator: (v) => v == null || v.isEmpty ? 'Please enter a resolution note' : null,
                    ),
                    const SizedBox(height: AppSpacing.lg),
                    Row(
                      children: [
                        OutlinedButton(
                          onPressed: () => Navigator.of(ctx).pop(),
                          child: const Text('Cancel'),
                        ),
                        const Spacer(),
                        FilledButton(
                          onPressed: submitting
                              ? null
                              : () async {
                                  if (!formKey.currentState!.validate()) return;
                                  setStateModal(() => submitting = true);
                                  try {
                                    await ref.read(riskSignalListProvider.notifier).reviewSignal(
                                          signal.id,
                                          noteCtrl.text.trim(),
                                        );
                                    if (context.mounted) {
                                      Navigator.of(ctx).pop();
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        const SnackBar(
                                          content: Text('Risk signal marked as reviewed!'),
                                          backgroundColor: Colors.green,
                                        ),
                                      );
                                    }
                                  } catch (e) {
                                    setStateModal(() => submitting = false);
                                    if (context.mounted) {
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        SnackBar(content: Text('Failed: $e'), backgroundColor: Colors.red),
                                      );
                                    }
                                  }
                                },
                          child: submitting
                              ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                              : const Text('Mark as Reviewed'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(riskSignalListProvider);
    final notifier = ref.read(riskSignalListProvider.notifier);
    final cs = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Risk Alerts'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => notifier.loadFirstPage(),
          ),
        ],
      ),
      body: Column(
        children: [
          // Filter Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: AppSpacing.xs),
            child: Row(
              children: [
                ..._severities.map((sev) {
                  final isAll = sev == 'ALL';
                  final isSelected = isAll ? (state.severityFilter == null) : (state.severityFilter == sev);
                  return Padding(
                    padding: const EdgeInsets.only(right: AppSpacing.xs),
                    child: FilterChip(
                      label: Text(sev),
                      selected: isSelected,
                      onSelected: (_) => notifier.setSeverity(isAll ? null : sev),
                    ),
                  );
                }),
                Padding(
                  padding: const EdgeInsets.only(left: AppSpacing.xs),
                  child: FilterChip(
                    label: const Text('Unreviewed Only'),
                    selected: state.unreviewedOnly,
                    onSelected: (_) => notifier.toggleUnreviewedOnly(),
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 1),

          Expanded(
            child: PaginatedListView<RiskSignal>(
              items: state.items,
              isLoading: state.isLoading,
              hasMore: state.hasMore,
              error: state.error,
              onLoadMore: () => notifier.loadMore(),
              onRefresh: () async => notifier.loadFirstPage(),
              emptyTitle: 'No Risk Alerts',
              emptySubtitle: state.unreviewedOnly || state.severityFilter != null
                  ? 'No risk alerts matching current filters'
                  : 'All transactions are running within standard risk velocity parameters',
              emptyIcon: Icons.gpp_good_rounded,
              itemBuilder: (signal) {
                final isCritical = signal.riskLevel == RiskLevel.critical;
                final isHigh = signal.riskLevel == RiskLevel.high;

                return Card(
                  margin: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: 4),
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    side: BorderSide(
                      color: isCritical
                          ? Colors.red
                          : (isHigh ? Colors.orange : cs.outlineVariant.withAlpha(60)),
                      width: isCritical || isHigh ? 1.5 : 1.0,
                    ),
                    borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(AppSpacing.md),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Row(
                              children: [
                                StatusBadge(status: signal.riskLevel.name.toUpperCase(), small: true),
                                const SizedBox(width: AppSpacing.sm),
                                Text(
                                  signal.ruleTriggered.replaceAll('_', ' '),
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                                ),
                              ],
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: cs.surfaceContainerHighest,
                                borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
                              ),
                              child: Text(
                                'Score: ${signal.riskScore.toStringAsFixed(2)}',
                                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Text(
                          'Action Taken: ${signal.actionTaken} ${signal.transactionId != null ? "• Txn: #${signal.transactionId!.substring(0, 8)}" : ""}',
                          style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          signal.createdAt.substring(0, 19).replaceAll('T', ' '),
                          style: TextStyle(fontSize: 11, color: cs.onSurfaceVariant),
                        ),
                        const SizedBox(height: AppSpacing.sm),

                        // Resolution Status / Action
                        if (signal.isReviewed) ...[
                          Container(
                            padding: const EdgeInsets.all(AppSpacing.sm),
                            decoration: BoxDecoration(
                              color: Colors.green.withAlpha(20),
                              borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
                              border: Border.all(color: Colors.green.withAlpha(60)),
                            ),
                            child: Row(
                              children: [
                                const Icon(Icons.check_circle_outline, color: Colors.green, size: 16),
                                const SizedBox(width: AppSpacing.xs),
                                Expanded(
                                  child: Text(
                                    'Reviewed: ${signal.resolutionNote ?? "Resolved"}',
                                    style: const TextStyle(fontSize: 11, color: Colors.green, fontWeight: FontWeight.w500),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ] else ...[
                          Align(
                            alignment: Alignment.centerRight,
                            child: FilledButton.tonalIcon(
                              style: FilledButton.styleFrom(
                                visualDensity: VisualDensity.compact,
                              ),
                              onPressed: () => _showReviewSheet(context, ref, signal),
                              icon: const Icon(Icons.rate_review_outlined, size: 16),
                              label: const Text('Review Signal'),
                            ),
                          ),
                        ],
                      ],
                    ),
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
