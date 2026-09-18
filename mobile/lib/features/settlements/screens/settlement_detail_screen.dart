import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../shared/widgets/empty_state.dart';
import '../../../shared/widgets/status_badge.dart';
import '../../../theme/theme.dart';
import '../settlement_providers.dart';

class SettlementDetailScreen extends ConsumerWidget {
  const SettlementDetailScreen({super.key, required this.settlementId});

  final String settlementId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sAsync = ref.watch(settlementDetailProvider(settlementId));
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;
    final currencyFmt = NumberFormat.currency(symbol: '₹', decimalDigits: 2);

    return sAsync.when(
      loading: () => Scaffold(
        appBar: AppBar(title: const Text('Settlement Details')),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (err, _) => Scaffold(
        appBar: AppBar(title: const Text('Settlement Details')),
        body: ErrorState(
          message: 'Failed to load settlement: $err',
          onRetry: () => ref.refresh(settlementDetailProvider(settlementId)),
        ),
      ),
      data: (s) {
        final gross = double.tryParse(s.grossAmount) ?? 0.0;
        final mdr = double.tryParse(s.mdrAmount) ?? 0.0;
        final tax = double.tryParse(s.taxOnMdr) ?? 0.0;
        final net = double.tryParse(s.netAmount) ?? (gross - mdr - tax);

        return Scaffold(
          appBar: AppBar(
            title: Text('Settlement ${s.settlementDate}'),
            actions: [
              IconButton(
                icon: const Icon(Icons.refresh_rounded),
                onPressed: () => ref.refresh(settlementDetailProvider(settlementId)),
              ),
            ],
          ),
          body: ListView(
            padding: const EdgeInsets.all(AppSpacing.md),
            children: [
              // Net Amount Card
              Card(
                elevation: 0,
                color: cs.primaryContainer.withAlpha(50),
                shape: RoundedRectangleBorder(
                  side: BorderSide(color: cs.primary.withAlpha(120)),
                  borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(AppSpacing.lg),
                  child: Column(
                    children: [
                      Text('Net Payout Amount', style: tt.labelMedium?.copyWith(color: cs.onSurfaceVariant)),
                      const SizedBox(height: 4),
                      Text(
                        currencyFmt.format(net),
                        style: tt.displaySmall?.copyWith(fontWeight: FontWeight.w900, color: cs.primary),
                      ),
                      const SizedBox(height: AppSpacing.sm),
                      StatusBadge(status: s.status.name.toUpperCase()),
                      const SizedBox(height: AppSpacing.md),
                      const Divider(),
                      const SizedBox(height: AppSpacing.sm),
                      if (s.utrReference != null)
                        InkWell(
                          onTap: () {
                            Clipboard.setData(ClipboardData(text: s.utrReference!));
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('UTR Reference copied to clipboard!')),
                            );
                          },
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text('Bank UTR Number', style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant)),
                              Row(
                                children: [
                                  Text(s.utrReference!, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                                  const SizedBox(width: 4),
                                  const Icon(Icons.copy_rounded, size: 14),
                                ],
                              ),
                            ],
                          ),
                        ),
                      const SizedBox(height: 4),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Settlement Cycle', style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant)),
                          Text(s.settlementCycle, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Transactions Included', style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant)),
                          Text('${s.transactionCount} transactions', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                        ],
                      ),
                      if (s.bankAccountRef != null) ...[
                        const SizedBox(height: 4),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text('Bank Account', style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant)),
                            Text(s.bankAccountRef!, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: AppSpacing.lg),

              // Deductions Breakdown
              Text('Deductions & Reconciliation', style: tt.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: AppSpacing.sm),
              Card(
                elevation: 0,
                shape: RoundedRectangleBorder(
                  side: BorderSide(color: cs.outlineVariant.withAlpha(80)),
                  borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(AppSpacing.md),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Gross Transactions Total'),
                          Text(currencyFmt.format(gross), style: const TextStyle(fontWeight: FontWeight.w600)),
                        ],
                      ),
                      const SizedBox(height: AppSpacing.xs),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('MDR Platform Fee', style: TextStyle(color: Colors.red)),
                          Text('- ${currencyFmt.format(mdr)}', style: const TextStyle(color: Colors.red, fontWeight: FontWeight.w600)),
                        ],
                      ),
                      const SizedBox(height: AppSpacing.xs),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('GST on MDR (18%)', style: TextStyle(color: Colors.red)),
                          Text('- ${currencyFmt.format(tax)}', style: const TextStyle(color: Colors.red, fontWeight: FontWeight.w600)),
                        ],
                      ),
                      const Divider(height: AppSpacing.lg),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Net Disbursed', style: tt.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                          Text(currencyFmt.format(net), style: tt.titleSmall?.copyWith(fontWeight: FontWeight.bold, color: cs.primary)),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: AppSpacing.lg),

              // Line Items
              Text('Batch Line Items (${s.lineItems.length})', style: tt.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: AppSpacing.sm),
              if (s.lineItems.isEmpty)
                const Card(
                  child: Padding(
                    padding: EdgeInsets.all(AppSpacing.md),
                    child: Center(child: Text('Summary batch settlement (no individual line items)')),
                  ),
                )
              else
                Card(
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    side: BorderSide(color: cs.outlineVariant.withAlpha(80)),
                    borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
                  ),
                  child: ListView.separated(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: s.lineItems.length,
                    separatorBuilder: (_, _) => const Divider(height: 1),
                    itemBuilder: (context, idx) {
                      final item = s.lineItems[idx];
                      final itemGross = double.tryParse(item.amount) ?? 0.0;
                      final itemNet = double.tryParse(item.netAmount) ?? 0.0;

                      return ListTile(
                        dense: true,
                        title: Text('Txn #${item.transactionId.substring(0, 8)}', style: const TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Text('Gross: ${currencyFmt.format(itemGross)} • Fee: ₹${item.feeAmount} • Tax: ₹${item.taxAmount}'),
                        trailing: Text(currencyFmt.format(itemNet), style: const TextStyle(fontWeight: FontWeight.bold)),
                      );
                    },
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
