import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../../models/transaction_models.dart';
import '../../../shared/widgets/paginated_list_view.dart';
import '../../../shared/widgets/status_badge.dart';
import '../../../theme/theme.dart';
import '../transaction_providers.dart';
import 'transaction_filter_sheet.dart';

class TransactionsScreen extends ConsumerWidget {
  const TransactionsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(transactionListProvider);
    final notifier = ref.read(transactionListProvider.notifier);
    final cs = Theme.of(context).colorScheme;
    final currencyFmt = NumberFormat.currency(symbol: '₹', decimalDigits: 2);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Transactions'),
        actions: [
          IconButton(
            icon: Badge(
              isLabelVisible: state.filters.hasActiveFilters,
              child: const Icon(Icons.filter_list_rounded),
            ),
            tooltip: 'Filter',
            onPressed: () {
              TransactionFilterSheet.show(
                context,
                initialFilters: state.filters,
                onApply: (f) => notifier.updateFilters(f),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Active filter indicator
          if (state.filters.hasActiveFilters)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: AppSpacing.xs),
              color: cs.primaryContainer.withAlpha(40),
              child: Row(
                children: [
                  const Icon(Icons.filter_alt_outlined, size: 16),
                  const SizedBox(width: AppSpacing.xs),
                  Expanded(
                    child: Text(
                      'Filters: ${[
                        if (state.filters.status != null) 'Status: ${state.filters.status}',
                        if (state.filters.paymentMethod != null) 'Method: ${state.filters.paymentMethod}',
                      ].join(', ')}',
                      style: const TextStyle(fontSize: 12),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  TextButton(
                    onPressed: () => notifier.clearFilters(),
                    child: const Text('Clear', style: TextStyle(fontSize: 12)),
                  ),
                ],
              ),
            ),

          // List
          Expanded(
            child: PaginatedListView<PaymentTransaction>(
              items: state.items,
              isLoading: state.isLoading,
              hasMore: state.hasMore,
              error: state.error,
              onLoadMore: () => notifier.loadMore(),
              onRefresh: () async => notifier.loadFirstPage(),
              emptyTitle: 'No Transactions',
              emptySubtitle: state.filters.hasActiveFilters
                  ? 'No transactions matched your filters'
                  : 'Processed payments and collections will appear here',
              emptyIcon: Icons.swap_horiz_rounded,
              emptyAction: state.filters.hasActiveFilters ? () => notifier.clearFilters() : null,
              emptyActionLabel: 'Reset Filters',
              itemBuilder: (tx) {
                final amount = double.tryParse(tx.amount) ?? 0.0;
                final isDup = tx.duplicateFlags.isNotEmpty;

                return Card(
                  margin: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: 4),
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    side: BorderSide(
                      color: isDup ? Colors.amber : cs.outlineVariant.withAlpha(60),
                      width: isDup ? 1.5 : 1.0,
                    ),
                    borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
                  ),
                  child: ListTile(
                    onTap: () => context.go('/transactions/${tx.id}'),
                    leading: Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: cs.surfaceContainerHighest,
                        borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
                      ),
                      child: Icon(
                        tx.paymentMethod == PaymentMethod.upiQr ||
                                tx.paymentMethod == PaymentMethod.upiCollect ||
                                tx.paymentMethod == PaymentMethod.upiIntent
                            ? Icons.qr_code_2_rounded
                            : Icons.credit_card_rounded,
                        color: cs.primary,
                        size: 20,
                      ),
                    ),
                    title: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            tx.customerName ?? (tx.payerVpa ?? 'UPI Payment'),
                            style: const TextStyle(fontWeight: FontWeight.bold),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        StatusBadge(status: tx.status.name.toUpperCase(), small: true),
                      ],
                    ),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 4),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              tx.createdAt.length >= 16 ? tx.createdAt.substring(0, 16).replaceAll('T', ' ') : tx.createdAt,
                              style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant),
                            ),
                            Text(
                              currencyFmt.format(amount),
                              style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                            ),
                          ],
                        ),
                        if (isDup) ...[
                          const SizedBox(height: 2),
                          const Row(
                            children: [
                              Icon(Icons.warning_amber_rounded, color: Colors.amber, size: 14),
                              SizedBox(width: 4),
                              Text('Duplicate Flagged', style: TextStyle(fontSize: 11, color: Colors.amber, fontWeight: FontWeight.bold)),
                            ],
                          ),
                        ],
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
