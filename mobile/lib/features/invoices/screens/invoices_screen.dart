import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../../models/invoice_models.dart';
import '../../../shared/widgets/paginated_list_view.dart';
import '../../../shared/widgets/status_badge.dart';
import '../../../theme/theme.dart';
import '../invoice_providers.dart';

class InvoicesScreen extends ConsumerWidget {
  const InvoicesScreen({super.key});

  static const _statusOptions = [
    'ALL',
    'DRAFT',
    'PENDING',
    'PAID',
    'PARTIALLY_PAID',
    'OVERDUE',
    'CANCELLED',
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(invoiceListProvider);
    final notifier = ref.read(invoiceListProvider.notifier);
    final cs = Theme.of(context).colorScheme;
    final currencyFmt = NumberFormat.currency(symbol: '₹', decimalDigits: 0);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Invoices'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_rounded),
            tooltip: 'Create Invoice',
            onPressed: () => context.go('/invoices/create'),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.go('/invoices/create'),
        icon: const Icon(Icons.add_rounded),
        label: const Text('New Invoice'),
      ),
      body: Column(
        children: [
          // Search Bar
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: AppSpacing.sm),
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Search customer or invoice #...',
                prefixIcon: const Icon(Icons.search_rounded),
                suffixIcon: state.searchQuery.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear_rounded),
                        onPressed: () => notifier.setSearchQuery(''),
                      )
                    : null,
                filled: true,
                fillColor: cs.surfaceContainerHighest.withAlpha(50),
                contentPadding: const EdgeInsets.symmetric(vertical: 0),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
                  borderSide: BorderSide.none,
                ),
              ),
              onSubmitted: (query) => notifier.setSearchQuery(query.trim()),
            ),
          ),

          // Filter Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: AppSpacing.xs),
            child: Row(
              children: _statusOptions.map((status) {
                final isAll = status == 'ALL';
                final isSelected = isAll ? (state.statusFilter == null) : (state.statusFilter == status);

                return Padding(
                  padding: const EdgeInsets.only(right: AppSpacing.xs),
                  child: FilterChip(
                    label: Text(status),
                    selected: isSelected,
                    onSelected: (_) {
                      notifier.setStatusFilter(isAll ? null : status);
                    },
                  ),
                );
              }).toList(),
            ),
          ),
          const Divider(height: 1),

          // Paginated List
          Expanded(
            child: PaginatedListView<Invoice>(
              items: state.items,
              isLoading: state.isLoading,
              hasMore: state.hasMore,
              error: state.error,
              onLoadMore: () => notifier.loadMore(),
              onRefresh: () async => notifier.loadFirstPage(),
              emptyTitle: 'No Invoices Found',
              emptySubtitle: state.searchQuery.isNotEmpty || state.statusFilter != null
                  ? 'Try changing your search or filter options'
                  : 'Tap "+ New Invoice" below to create your first customer invoice',
              emptyIcon: Icons.receipt_long_outlined,
              emptyAction: () => context.go('/invoices/create'),
              emptyActionLabel: 'Create Invoice',
              itemBuilder: (invoice) {
                final total = double.tryParse(invoice.totalAmount) ?? 0.0;
                final paid = double.tryParse(invoice.paidAmount) ?? 0.0;
                final balance = total - paid;

                return Card(
                  margin: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: 4),
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    side: BorderSide(color: cs.outlineVariant.withAlpha(60)),
                    borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
                  ),
                  child: ListTile(
                    onTap: () => context.go('/invoices/${invoice.id}'),
                    title: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            invoice.customerName ?? 'Walk-in Customer',
                            style: const TextStyle(fontWeight: FontWeight.bold),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        StatusBadge(status: invoice.status.name.toUpperCase(), small: true),
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
                              '#${invoice.invoiceNumber}',
                              style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant),
                            ),
                            Text(
                              currencyFmt.format(total),
                              style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                            ),
                          ],
                        ),
                        if (balance > 0 && balance < total) ...[
                          const SizedBox(height: 2),
                          Text(
                            'Due: ${currencyFmt.format(balance)}',
                            style: TextStyle(fontSize: 11, color: cs.primary, fontWeight: FontWeight.w600),
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
