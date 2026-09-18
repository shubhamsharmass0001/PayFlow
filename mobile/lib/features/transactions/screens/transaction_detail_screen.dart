import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../core/providers.dart';
import '../../../models/transaction_models.dart';
import '../../../shared/widgets/empty_state.dart';
import '../../../shared/widgets/status_badge.dart';
import '../../../theme/theme.dart';
import '../transaction_providers.dart';
import '../transaction_repository.dart';
import 'qr_scanner_screen.dart';

class TransactionDetailScreen extends ConsumerStatefulWidget {
  const TransactionDetailScreen({super.key, required this.transactionId});

  final String transactionId;

  @override
  ConsumerState<TransactionDetailScreen> createState() =>
      _TransactionDetailScreenState();
}

class _TransactionDetailScreenState
    extends ConsumerState<TransactionDetailScreen> {
  bool _refunding = false;

  void _showRefundDialog(PaymentTransaction tx) {
    final amountCtrl = TextEditingController(text: tx.amount);
    final reasonCtrl = TextEditingController();
    final formKey = GlobalKey<FormState>();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Initiate Refund'),
        content: Form(
          key: formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Original Amount: ₹${tx.amount}'),
              const SizedBox(height: AppSpacing.md),
              TextFormField(
                controller: amountCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Refund Amount (₹)',
                  prefixText: '₹',
                ),
                validator: (v) {
                  final parsed = double.tryParse(v ?? '');
                  final orig = double.tryParse(tx.amount) ?? 0.0;
                  if (parsed == null || parsed <= 0) return 'Enter valid amount';
                  if (parsed > orig) return 'Cannot exceed original amount';
                  return null;
                },
              ),
              const SizedBox(height: AppSpacing.sm),
              TextFormField(
                controller: reasonCtrl,
                decoration: const InputDecoration(
                  labelText: 'Reason for refund',
                  hintText: 'e.g. Customer return, duplicate charge',
                ),
                validator: (v) => v == null || v.isEmpty ? 'Required' : null,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () async {
              if (!formKey.currentState!.validate()) return;
              Navigator.of(ctx).pop();
              setState(() => _refunding = true);
              try {
                final merchantId = ref.read(activeMerchantIdProvider);
                final repo = ref.read(transactionRepositoryProvider);
                await repo.createRefund(
                  merchantId,
                  tx.id,
                  CreateRefundRequest(
                    amount: amountCtrl.text.trim(),
                    reason: reasonCtrl.text.trim(),
                  ),
                );
                ref.invalidate(transactionDetailProvider(widget.transactionId));
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Refund initiated successfully!'),
                      backgroundColor: Colors.green,
                    ),
                  );
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Failed to refund: $e'),
                      backgroundColor: Colors.red,
                    ),
                  );
                }
              } finally {
                if (mounted) setState(() => _refunding = false);
              }
            },
            child: const Text('Confirm Refund'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final txAsync = ref.watch(transactionDetailProvider(widget.transactionId));
    final userRole = ref.watch(userRoleProvider);
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;
    final currencyFmt = NumberFormat.currency(symbol: '₹', decimalDigits: 2);

    final canRefund = userRole == 'OWNER' || userRole == 'ADMIN' || userRole == 'MANAGER';

    return txAsync.when(
      loading: () => Scaffold(
        appBar: AppBar(title: const Text('Transaction Details')),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (err, _) => Scaffold(
        appBar: AppBar(title: const Text('Transaction Details')),
        body: ErrorState(
          message: 'Failed to load transaction: $err',
          onRetry: () => ref.refresh(transactionDetailProvider(widget.transactionId)),
        ),
      ),
      data: (tx) {
        final amount = double.tryParse(tx.amount) ?? 0.0;
        final isSuccess = tx.status == TransactionStatus.success;

        return Scaffold(
          appBar: AppBar(
            title: Text('Txn #${tx.id.substring(0, 8)}'),
            actions: [
              IconButton(
                icon: const Icon(Icons.qr_code_scanner_rounded),
                tooltip: 'Scan to Verify',
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => QrScannerScreen(
                        expectedReference: tx.providerRefId ?? tx.id,
                      ),
                    ),
                  );
                },
              ),
              IconButton(
                icon: const Icon(Icons.refresh_rounded),
                onPressed: () => ref.refresh(transactionDetailProvider(widget.transactionId)),
              ),
            ],
          ),
          bottomNavigationBar: canRefund && isSuccess
              ? SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.all(AppSpacing.md),
                    child: OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.red,
                        side: const BorderSide(color: Colors.red),
                        padding: const EdgeInsets.symmetric(vertical: AppSpacing.md),
                      ),
                      onPressed: _refunding ? null : () => _showRefundDialog(tx),
                      icon: _refunding
                          ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                          : const Icon(Icons.undo_rounded),
                      label: const Text('Initiate Refund (RBAC Gated)'),
                    ),
                  ),
                )
              : null,
          body: ListView(
            padding: const EdgeInsets.all(AppSpacing.md),
            children: [
              // Duplicate Flag Warning Banner
              if (tx.duplicateFlags.isNotEmpty) ...[
                Container(
                  padding: const EdgeInsets.all(AppSpacing.md),
                  decoration: BoxDecoration(
                    color: Colors.amber.withAlpha(40),
                    borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
                    border: Border.all(color: Colors.amber),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.warning_amber_rounded, color: Colors.amber, size: 28),
                      const SizedBox(width: AppSpacing.md),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Flagged as Duplicate',
                              style: TextStyle(fontWeight: FontWeight.bold, color: Colors.amber),
                            ),
                            Text(
                              tx.duplicateFlags.first.flagReason,
                              style: const TextStyle(fontSize: 12),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: AppSpacing.md),
              ],

              // Header summary card
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
                    children: [
                      Text('Amount Paid', style: tt.labelMedium?.copyWith(color: cs.onSurfaceVariant)),
                      const SizedBox(height: 4),
                      Text(
                        currencyFmt.format(amount),
                        style: tt.displaySmall?.copyWith(fontWeight: FontWeight.w900, color: cs.primary),
                      ),
                      const SizedBox(height: AppSpacing.sm),
                      StatusBadge(status: tx.status.name.toUpperCase()),
                      const SizedBox(height: AppSpacing.md),
                      const Divider(),
                      const SizedBox(height: AppSpacing.sm),
                      _DetailRow(label: 'Payment Method', value: tx.paymentMethod.name.toUpperCase()),
                      if (tx.payerVpa != null) _DetailRow(label: 'Payer VPA', value: tx.payerVpa!),
                      if (tx.providerRefId != null) _DetailRow(label: 'Bank UTR / Ref', value: tx.providerRefId!),
                      if (tx.invoiceNumber != null) _DetailRow(label: 'Invoice #', value: tx.invoiceNumber!),
                      if (tx.customerName != null) _DetailRow(label: 'Customer', value: tx.customerName!),
                      _DetailRow(label: 'Created At', value: tx.createdAt.substring(0, 19).replaceAll('T', ' ')),
                      if (tx.failureReason != null)
                        _DetailRow(label: 'Failure Reason', value: tx.failureReason!, valueColor: Colors.red),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: AppSpacing.xl),

              // Status History Timeline
              Text('Status History Timeline', style: tt.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: AppSpacing.xs),
              Text('Auditable lifecycle of this transaction', style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant)),
              const SizedBox(height: AppSpacing.md),

              if (tx.statusHistory.isEmpty)
                const Card(
                  child: Padding(
                    padding: EdgeInsets.all(AppSpacing.md),
                    child: Text('Initial transition recorded'),
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
                    padding: const EdgeInsets.all(AppSpacing.lg),
                    child: Column(
                      children: tx.statusHistory.asMap().entries.map((entry) {
                        final idx = entry.key;
                        final hist = entry.value;
                        final isLast = idx == tx.statusHistory.length - 1;

                        return Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Timeline dot and line
                            Column(
                              children: [
                                Container(
                                  width: 16,
                                  height: 16,
                                  decoration: BoxDecoration(
                                    color: isLast ? cs.primary : cs.outlineVariant,
                                    shape: BoxShape.circle,
                                    border: Border.all(color: cs.surface, width: 2),
                                  ),
                                ),
                                if (!isLast)
                                  Container(
                                    width: 2,
                                    height: 48,
                                    color: cs.outlineVariant.withAlpha(120),
                                  ),
                              ],
                            ),
                            const SizedBox(width: AppSpacing.md),
                            // Event content
                            Expanded(
                              child: Padding(
                                padding: const EdgeInsets.only(bottom: AppSpacing.md),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text(
                                          hist.toStatus.toUpperCase(),
                                          style: TextStyle(
                                            fontWeight: FontWeight.bold,
                                            color: isLast ? cs.primary : cs.onSurface,
                                          ),
                                        ),
                                        Text(
                                          hist.createdAt.length >= 19
                                              ? hist.createdAt.substring(11, 19)
                                              : hist.createdAt,
                                          style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant),
                                        ),
                                      ],
                                    ),
                                    if (hist.fromStatus != null)
                                      Text(
                                        'Transitioned from ${hist.fromStatus}',
                                        style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant),
                                      ),
                                    if (hist.reason != null && hist.reason!.isNotEmpty)
                                      Text(
                                        'Reason: ${hist.reason}',
                                        style: const TextStyle(fontSize: 12, fontStyle: FontStyle.italic),
                                      ),
                                  ],
                                ),
                              ),
                            ),
                          ],
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

class _DetailRow extends StatelessWidget {
  const _DetailRow({required this.label, required this.value, this.valueColor});
  final String label;
  final String value;
  final Color? valueColor;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(fontSize: 13, color: cs.onSurfaceVariant)),
          Text(
            value,
            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: valueColor),
          ),
        ],
      ),
    );
  }
}
