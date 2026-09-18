import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../../shared/widgets/empty_state.dart';
import '../../../shared/widgets/status_badge.dart';
import '../../../theme/theme.dart';
import '../customer_providers.dart';

class CustomerDetailScreen extends ConsumerWidget {
  const CustomerDetailScreen({super.key, required this.customerId});

  final String customerId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final customerAsync = ref.watch(customerDetailProvider(customerId));
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;
    final currencyFmt = NumberFormat.currency(symbol: '₹', decimalDigits: 0);

    return customerAsync.when(
      loading: () => Scaffold(
        appBar: AppBar(title: const Text('Customer Profile')),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (err, _) => Scaffold(
        appBar: AppBar(title: const Text('Customer Profile')),
        body: ErrorState(
          message: 'Could not load customer: $err',
          onRetry: () => ref.refresh(customerDetailProvider(customerId)),
        ),
      ),
      data: (customer) {
        return DefaultTabController(
          length: 2,
          child: Scaffold(
            appBar: AppBar(
              title: Text(customer.name),
              bottom: const TabBar(
                tabs: [
                  Tab(icon: Icon(Icons.receipt_long_rounded), text: 'Invoice History'),
                  Tab(icon: Icon(Icons.swap_horiz_rounded), text: 'Transaction History'),
                ],
              ),
            ),
            body: Column(
              children: [
                // Header Card
                Container(
                  padding: const EdgeInsets.all(AppSpacing.md),
                  color: cs.surfaceContainerHighest.withAlpha(30),
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 28,
                        backgroundColor: cs.primaryContainer,
                        child: Text(
                          customer.name.isNotEmpty ? customer.name[0].toUpperCase() : 'C',
                          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: cs.primary),
                        ),
                      ),
                      const SizedBox(width: AppSpacing.md),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(customer.name, style: tt.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                            const SizedBox(height: 2),
                            Text('Phone: ${customer.phone}', style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant)),
                            if (customer.email != null)
                              Text('Email: ${customer.email}', style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant)),
                            if (customer.upiVpa != null)
                              Text('UPI VPA: ${customer.upiVpa}', style: tt.bodySmall?.copyWith(color: cs.primary, fontWeight: FontWeight.w600)),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const Divider(height: 1),

                // Tabs content
                Expanded(
                  child: TabBarView(
                    children: [
                      // TAB 1: Invoices
                      Consumer(
                        builder: (context, ref, _) {
                          final invoicesAsync = ref.watch(customerInvoicesProvider(customerId));
                          return invoicesAsync.when(
                            loading: () => const Center(child: CircularProgressIndicator()),
                            error: (err, _) => Center(child: Text('Error loading invoices: $err')),
                            data: (invoices) {
                              if (invoices.isEmpty) {
                                return const EmptyState(
                                  title: 'No Invoices Yet',
                                  subtitle: 'No invoices issued to this customer',
                                  icon: Icons.receipt_long_outlined,
                                );
                              }
                              return ListView.separated(
                                padding: const EdgeInsets.all(AppSpacing.md),
                                itemCount: invoices.length,
                                separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.sm),
                                itemBuilder: (context, i) {
                                  final inv = invoices[i];
                                  final total = double.tryParse(inv.totalAmount) ?? 0.0;
                                  return Card(
                                    elevation: 0,
                                    shape: RoundedRectangleBorder(
                                      side: BorderSide(color: cs.outlineVariant.withAlpha(60)),
                                      borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
                                    ),
                                    child: ListTile(
                                      onTap: () => context.go('/invoices/${inv.id}'),
                                      title: Text('Invoice #${inv.invoiceNumber}', style: const TextStyle(fontWeight: FontWeight.bold)),
                                      subtitle: Text(inv.dueDate != null ? 'Due: ${inv.dueDate!.substring(0, 10)}' : 'No due date'),
                                      trailing: Column(
                                        mainAxisAlignment: MainAxisAlignment.center,
                                        crossAxisAlignment: CrossAxisAlignment.end,
                                        children: [
                                          Text(currencyFmt.format(total), style: const TextStyle(fontWeight: FontWeight.bold)),
                                          const SizedBox(height: 4),
                                          StatusBadge(status: inv.status.name.toUpperCase(), small: true),
                                        ],
                                      ),
                                    ),
                                  );
                                },
                              );
                            },
                          );
                        },
                      ),

                      // TAB 2: Transactions
                      Consumer(
                        builder: (context, ref, _) {
                          final txAsync = ref.watch(customerTransactionsProvider(customerId));
                          return txAsync.when(
                            loading: () => const Center(child: CircularProgressIndicator()),
                            error: (err, _) => Center(child: Text('Error loading transactions: $err')),
                            data: (transactions) {
                              if (transactions.isEmpty) {
                                return const EmptyState(
                                  title: 'No Transactions',
                                  subtitle: 'No payments processed for this customer',
                                  icon: Icons.swap_horiz_rounded,
                                );
                              }
                              return ListView.separated(
                                padding: const EdgeInsets.all(AppSpacing.md),
                                itemCount: transactions.length,
                                separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.sm),
                                itemBuilder: (context, i) {
                                  final tx = transactions[i];
                                  final amount = double.tryParse(tx.amount) ?? 0.0;
                                  return Card(
                                    elevation: 0,
                                    shape: RoundedRectangleBorder(
                                      side: BorderSide(color: cs.outlineVariant.withAlpha(60)),
                                      borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
                                    ),
                                    child: ListTile(
                                      onTap: () => context.go('/transactions/${tx.id}'),
                                      title: Text(tx.paymentMethod.name.toUpperCase(), style: const TextStyle(fontWeight: FontWeight.bold)),
                                      subtitle: Text(tx.createdAt.length >= 16 ? tx.createdAt.substring(0, 16).replaceAll('T', ' ') : tx.createdAt),
                                      trailing: Column(
                                        mainAxisAlignment: MainAxisAlignment.center,
                                        crossAxisAlignment: CrossAxisAlignment.end,
                                        children: [
                                          Text(currencyFmt.format(amount), style: const TextStyle(fontWeight: FontWeight.bold)),
                                          const SizedBox(height: 4),
                                          StatusBadge(status: tx.status.name.toUpperCase(), small: true),
                                        ],
                                      ),
                                    ),
                                  );
                                },
                              );
                            },
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
