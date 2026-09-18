import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../../models/settlement_models.dart';
import '../../../shared/widgets/paginated_list_view.dart';
import '../../../shared/widgets/status_badge.dart';
import '../../../theme/theme.dart';
import '../settlement_providers.dart';

class SettlementsScreen extends ConsumerWidget {
  const SettlementsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(settlementListProvider);
    final notifier = ref.read(settlementListProvider.notifier);
    final cs = Theme.of(context).colorScheme;
    final currencyFmt = NumberFormat.currency(symbol: '₹', decimalDigits: 0);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settlements'),
      ),
      body: PaginatedListView<Settlement>(
        items: state.items,
        isLoading: state.isLoading,
        hasMore: state.hasMore,
        error: state.error,
        onLoadMore: () => notifier.loadMore(),
        onRefresh: () async => notifier.loadFirstPage(),
        emptyTitle: 'No Settlements Yet',
        emptySubtitle: 'Daily settlement batches and bank transfers will appear here',
        emptyIcon: Icons.account_balance_rounded,
        itemBuilder: (s) {
          final net = double.tryParse(s.netAmount) ?? 0.0;
          final gross = double.tryParse(s.grossAmount) ?? 0.0;

          return Card(
            margin: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: 4),
            elevation: 0,
            shape: RoundedRectangleBorder(
              side: BorderSide(color: cs.outlineVariant.withAlpha(60)),
              borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
            ),
            child: ListTile(
              onTap: () => context.go('/settlements/${s.id}'),
              leading: Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: cs.primaryContainer.withAlpha(80),
                  borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
                ),
                child: Icon(Icons.account_balance_rounded, color: cs.primary, size: 20),
              ),
              title: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Batch ${s.settlementDate}', style: const TextStyle(fontWeight: FontWeight.bold)),
                  StatusBadge(status: s.status.name.toUpperCase(), small: true),
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
                        '${s.transactionCount} txns • Cycle: ${s.settlementCycle}',
                        style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant),
                      ),
                      Text(
                        currencyFmt.format(net),
                        style: TextStyle(fontWeight: FontWeight.w800, fontSize: 14, color: cs.primary),
                      ),
                    ],
                  ),
                  if (gross != net) ...[
                    const SizedBox(height: 2),
                    Text(
                      'Gross: ${currencyFmt.format(gross)}',
                      style: TextStyle(fontSize: 11, color: cs.onSurfaceVariant),
                    ),
                  ],
                ],
              ),
              trailing: const Icon(Icons.chevron_right_rounded),
            ),
          );
        },
      ),
    );
  }
}
