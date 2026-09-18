import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../models/invoice_models.dart';
import '../../../shared/widgets/empty_state.dart';
import '../../../shared/widgets/status_badge.dart';
import '../../../theme/theme.dart';
import '../invoice_providers.dart';
import 'collect_payment_sheet.dart';

class InvoiceDetailScreen extends ConsumerWidget {
  const InvoiceDetailScreen({super.key, required this.invoiceId});

  final String invoiceId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final invoiceAsync = ref.watch(invoiceDetailProvider(invoiceId));
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;
    final currencyFmt = NumberFormat.currency(symbol: '₹', decimalDigits: 2);

    return invoiceAsync.when(
      loading: () => Scaffold(
        appBar: AppBar(title: const Text('Invoice Details')),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (err, _) => Scaffold(
        appBar: AppBar(title: const Text('Invoice Details')),
        body: ErrorState(
          message: 'Could not load invoice: $err',
          onRetry: () => ref.refresh(invoiceDetailProvider(invoiceId)),
        ),
      ),
      data: (invoice) {
        final total = double.tryParse(invoice.totalAmount) ?? 0.0;
        final paid = double.tryParse(invoice.paidAmount) ?? 0.0;
        final balance = (total - paid).clamp(0.0, double.infinity);
        final isPaid = invoice.status == InvoiceStatus.paid || balance <= 0;

        return Scaffold(
          appBar: AppBar(
            title: Text('#${invoice.invoiceNumber}'),
            actions: [
              IconButton(
                icon: const Icon(Icons.refresh_rounded),
                onPressed: () => ref.refresh(invoiceDetailProvider(invoiceId)),
              ),
            ],
          ),
          bottomNavigationBar: SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(AppSpacing.md),
              child: isPaid
                  ? Container(
                      padding: const EdgeInsets.symmetric(vertical: AppSpacing.md),
                      decoration: BoxDecoration(
                        color: Colors.green.withAlpha(30),
                        borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
                        border: Border.all(color: Colors.green.withAlpha(100)),
                      ),
                      child: const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.check_circle_rounded, color: Colors.green),
                          SizedBox(width: AppSpacing.sm),
                          Text(
                            'Invoice Fully Paid',
                            style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    )
                  : FilledButton.icon(
                      style: FilledButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: AppSpacing.md),
                      ),
                      onPressed: () => CollectPaymentSheet.show(context, invoice),
                      icon: const Icon(Icons.qr_code_2_rounded),
                      label: Text('Collect Payment (${currencyFmt.format(balance)})'),
                    ),
            ),
          ),
          body: ListView(
            padding: const EdgeInsets.all(AppSpacing.md),
            children: [
              // Header Card
              Card(
                elevation: 0,
                color: cs.surfaceContainerHighest.withAlpha(40),
                shape: RoundedRectangleBorder(
                  side: BorderSide(color: cs.outlineVariant.withAlpha(80)),
                  borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(AppSpacing.lg),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                            child: Text(
                              invoice.customerName ?? 'Walk-in Customer',
                              style: tt.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                            ),
                          ),
                          StatusBadge(status: invoice.status.name.toUpperCase()),
                        ],
                      ),
                      const SizedBox(height: AppSpacing.xs),
                      Text(
                        'Invoice #${invoice.invoiceNumber}',
                        style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant),
                      ),
                      if (invoice.dueDate != null) ...[
                        const SizedBox(height: 2),
                        Text(
                          'Due: ${invoice.dueDate!.substring(0, 10)}',
                          style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant),
                        ),
                      ],
                      const Divider(height: AppSpacing.xl),

                      // Balances
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Total Amount', style: tt.labelSmall?.copyWith(color: cs.onSurfaceVariant)),
                              Text(currencyFmt.format(total), style: tt.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                            ],
                          ),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              Text('Paid', style: tt.labelSmall?.copyWith(color: cs.onSurfaceVariant)),
                              Text(currencyFmt.format(paid), style: tt.titleMedium?.copyWith(color: Colors.green, fontWeight: FontWeight.bold)),
                            ],
                          ),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Text('Remaining', style: tt.labelSmall?.copyWith(color: cs.onSurfaceVariant)),
                              Text(currencyFmt.format(balance), style: tt.titleMedium?.copyWith(color: cs.primary, fontWeight: FontWeight.bold)),
                            ],
                          ),
                        ],
                      ),
                      if (total > 0) ...[
                        const SizedBox(height: AppSpacing.md),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                          child: LinearProgressIndicator(
                            value: (paid / total).clamp(0.0, 1.0),
                            minHeight: 6,
                            backgroundColor: cs.outlineVariant.withAlpha(60),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: AppSpacing.lg),

              // Line Items
              Text('Line Items (${invoice.items.length})', style: tt.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: AppSpacing.sm),
              Card(
                elevation: 0,
                shape: RoundedRectangleBorder(
                  side: BorderSide(color: cs.outlineVariant.withAlpha(80)),
                  borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
                ),
                child: ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: invoice.items.length,
                  separatorBuilder: (_, _) => const Divider(height: 1),
                  itemBuilder: (context, idx) {
                    final item = invoice.items[idx];
                    final qty = double.tryParse(item.quantity) ?? 1.0;
                    final price = double.tryParse(item.unitPrice) ?? 0.0;
                    final totalItem = double.tryParse(item.lineTotal) ?? (qty * price);

                    return ListTile(
                      title: Text(item.name, style: const TextStyle(fontWeight: FontWeight.w600)),
                      subtitle: Text('${qty.toStringAsFixed(0)} x ${currencyFmt.format(price)}  •  GST ${item.taxRate}%'),
                      trailing: Text(currencyFmt.format(totalItem), style: const TextStyle(fontWeight: FontWeight.bold)),
                    );
                  },
                ),
              ),
              const SizedBox(height: AppSpacing.lg),

              // Financial Breakdown Summary
              Card(
                elevation: 0,
                color: cs.surfaceContainerLowest,
                shape: RoundedRectangleBorder(
                  side: BorderSide(color: cs.outlineVariant.withAlpha(60)),
                  borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(AppSpacing.md),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Subtotal', style: tt.bodySmall),
                          Text(currencyFmt.format(double.tryParse(invoice.subtotal) ?? 0.0), style: tt.bodySmall),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Tax Total', style: tt.bodySmall),
                          Text(currencyFmt.format(double.tryParse(invoice.taxTotal) ?? 0.0), style: tt.bodySmall),
                        ],
                      ),
                      if ((double.tryParse(invoice.discountTotal) ?? 0.0) > 0) ...[
                        const SizedBox(height: 6),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text('Discount', style: tt.bodySmall?.copyWith(color: Colors.green)),
                            Text('- ${currencyFmt.format(double.tryParse(invoice.discountTotal) ?? 0.0)}', style: tt.bodySmall?.copyWith(color: Colors.green)),
                          ],
                        ),
                      ],
                      const Divider(height: AppSpacing.md),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Total', style: tt.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                          Text(currencyFmt.format(total), style: tt.titleSmall?.copyWith(fontWeight: FontWeight.bold, color: cs.primary)),
                        ],
                      ),
                    ],
                  ),
                ),
              ),

              if (invoice.notes != null && invoice.notes!.isNotEmpty) ...[
                const SizedBox(height: AppSpacing.lg),
                Text('Notes', style: tt.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: AppSpacing.xs),
                Text(invoice.notes!, style: tt.bodyMedium?.copyWith(color: cs.onSurfaceVariant)),
              ],
              const SizedBox(height: AppSpacing.xxl),
            ],
          ),
        );
      },
    );
  }
}
