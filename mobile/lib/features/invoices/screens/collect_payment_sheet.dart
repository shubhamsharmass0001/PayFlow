import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers.dart';
import '../../../models/invoice_models.dart';
import '../../../theme/theme.dart';
import '../invoice_repository.dart';
import 'qr_display_screen.dart';

class CollectPaymentSheet extends ConsumerStatefulWidget {
  const CollectPaymentSheet({super.key, required this.invoice});

  final Invoice invoice;

  static Future<void> show(BuildContext context, Invoice invoice) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => CollectPaymentSheet(invoice: invoice),
    );
  }

  @override
  ConsumerState<CollectPaymentSheet> createState() => _CollectPaymentSheetState();
}

class _CollectPaymentSheetState extends ConsumerState<CollectPaymentSheet> {
  bool _isLoading = false;
  String? _error;

  // Plan configuration state
  bool _showPlanForm = false;
  String _planType = 'DEPOSIT_BALANCE';
  int _depositPct = 50;
  int _installmentCount = 2;

  double get remainingBalance {
    final total = double.tryParse(widget.invoice.totalAmount) ?? 0.0;
    final paid = double.tryParse(widget.invoice.paidAmount) ?? 0.0;
    return (total - paid).clamp(0.0, double.infinity);
  }

  Future<void> _handleSinglePayment() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final merchantId = ref.read(activeMerchantIdProvider);
      final repo = ref.read(invoiceRepositoryProvider);

      final resp = await repo.createPaymentRequest(
        merchantId,
        widget.invoice.id,
        amount: remainingBalance.toStringAsFixed(2),
        method: 'UPI_QR',
      );

      if (!mounted) return;
      Navigator.of(context).pop(); // Close bottom sheet

      final qrString = (resp['qr_code_string'] ?? resp['upi_intent_uri'] ??
          'upi://pay?pa=merchant@payflow&pn=PayFlow&am=${remainingBalance.toStringAsFixed(2)}&cu=INR&tn=Inv-${widget.invoice.invoiceNumber}') as String;

      Navigator.of(context).push(
        MaterialPageRoute(
          fullscreenDialog: true,
          builder: (_) => QrDisplayScreen(
            qrString: qrString,
            amount: remainingBalance.toStringAsFixed(2),
            invoiceNumber: widget.invoice.invoiceNumber,
            customerName: widget.invoice.customerName,
          ),
        ),
      );
    } catch (e) {
      setState(() {
        _isLoading = false;
        _error = 'Failed to create payment request: $e';
      });
    }
  }

  Future<void> _handleCreatePlan() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final merchantId = ref.read(activeMerchantIdProvider);
      final repo = ref.read(invoiceRepositoryProvider);
      final balance = remainingBalance;

      List<Map<String, dynamic>> installments = [];
      if (_planType == 'DEPOSIT_BALANCE') {
        final depositAmt = (balance * (_depositPct / 100)).roundToDouble();
        final balanceAmt = balance - depositAmt;
        final now = DateTime.now();
        installments = [
          {
            'installment_number': 1,
            'amount': depositAmt.toStringAsFixed(2),
            'due_date': now.toIso8601String(),
            'notes': 'Upfront Deposit ($_depositPct%)',
          },
          {
            'installment_number': 2,
            'amount': balanceAmt.toStringAsFixed(2),
            'due_date': now.add(const Duration(days: 30)).toIso8601String(),
            'notes': 'Final Balance (${100 - _depositPct}%)',
          },
        ];
      } else {
        final perInst = (balance / _installmentCount).roundToDouble();
        final now = DateTime.now();
        for (int i = 1; i <= _installmentCount; i++) {
          installments.add({
            'installment_number': i,
            'amount': (i == _installmentCount ? (balance - (perInst * (_installmentCount - 1))) : perInst).toStringAsFixed(2),
            'due_date': now.add(Duration(days: 15 * (i - 1))).toIso8601String(),
            'notes': 'Installment $i of $_installmentCount',
          });
        }
      }

      await repo.createPaymentPlan(
        merchantId,
        invoiceId: widget.invoice.id,
        planType: _planType,
        installments: installments,
      );

      if (!mounted) return;
      Navigator.of(context).pop();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Payment plan created with ${installments.length} installments!'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      setState(() {
        _isLoading = false;
        _error = 'Failed to create plan: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;

    return Container(
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(AppSpacing.radiusXl)),
      ),
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom + AppSpacing.lg,
        top: AppSpacing.md,
        left: AppSpacing.lg,
        right: AppSpacing.lg,
      ),
      child: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Grab handle
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

              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Collect Payment', style: tt.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                  IconButton(
                    icon: const Icon(Icons.close_rounded),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
              Text(
                'Invoice #${widget.invoice.invoiceNumber} • Remaining: ₹${remainingBalance.toStringAsFixed(2)}',
                style: tt.bodyMedium?.copyWith(color: cs.onSurfaceVariant),
              ),
              const SizedBox(height: AppSpacing.md),

              if (_error != null) ...[
                Container(
                  padding: const EdgeInsets.all(AppSpacing.sm),
                  decoration: BoxDecoration(
                    color: cs.errorContainer.withAlpha(80),
                    borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
                  ),
                  child: Text(_error!, style: TextStyle(color: cs.error, fontSize: 13)),
                ),
                const SizedBox(height: AppSpacing.md),
              ],

              if (!_showPlanForm) ...[
                // OPTION 1: Single Payment Flow
                Card(
                  elevation: 0,
                  color: cs.primaryContainer.withAlpha(50),
                  shape: RoundedRectangleBorder(
                    side: BorderSide(color: cs.primary.withAlpha(100)),
                    borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(AppSpacing.lg),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(AppSpacing.xs),
                              decoration: BoxDecoration(
                                color: cs.primary,
                                borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
                              ),
                              child: const Icon(Icons.qr_code_2_rounded, color: Colors.white, size: 20),
                            ),
                            const SizedBox(width: AppSpacing.sm),
                            Text(
                              'Single Payment Request',
                              style: tt.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                        const SizedBox(height: AppSpacing.xs),
                        Text(
                          'Generate a full instant UPI QR to show the customer in person for ₹${remainingBalance.toStringAsFixed(2)}.',
                          style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant),
                        ),
                        const SizedBox(height: AppSpacing.md),
                        FilledButton.icon(
                          onPressed: _isLoading ? null : _handleSinglePayment,
                          icon: _isLoading
                              ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                              : const Icon(Icons.qr_code_rounded),
                          label: const Text('Generate Full QR Code'),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: AppSpacing.md),

                // OPTION 2: Deposit / Installment Plan Flow
                Card(
                  elevation: 0,
                  color: cs.secondaryContainer.withAlpha(40),
                  shape: RoundedRectangleBorder(
                    side: BorderSide(color: cs.outlineVariant),
                    borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(AppSpacing.lg),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(AppSpacing.xs),
                              decoration: BoxDecoration(
                                color: cs.secondary,
                                borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
                              ),
                              child: const Icon(Icons.calendar_month_rounded, color: Colors.white, size: 20),
                            ),
                            const SizedBox(width: AppSpacing.sm),
                            Text(
                              'Deposit / Installment Plan',
                              style: tt.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                        const SizedBox(height: AppSpacing.xs),
                        Text(
                          'Legitimately split this payment into deposit + installments. Avoid unstructured multiple sub-₹2,000 transactions.',
                          style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant),
                        ),
                        const SizedBox(height: AppSpacing.md),
                        OutlinedButton.icon(
                          onPressed: () => setState(() => _showPlanForm = true),
                          icon: const Icon(Icons.tune_rounded),
                          label: const Text('Configure Payment Plan'),
                        ),
                      ],
                    ),
                  ),
                ),
              ] else ...[
                // Plan Form Configuration
                Text('Configure Payment Plan', style: tt.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: AppSpacing.sm),
                SegmentedButton<String>(
                  segments: const [
                    ButtonSegment(value: 'DEPOSIT_BALANCE', label: Text('Deposit + Balance')),
                    ButtonSegment(value: 'EQUAL_INSTALLMENTS', label: Text('Equal Splits')),
                  ],
                  selected: {_planType},
                  onSelectionChanged: (val) => setState(() => _planType = val.first),
                ),
                const SizedBox(height: AppSpacing.md),

                if (_planType == 'DEPOSIT_BALANCE') ...[
                  Text('Advance Deposit: $_depositPct% (₹${(remainingBalance * (_depositPct / 100)).toStringAsFixed(0)})'),
                  Slider(
                    value: _depositPct.toDouble(),
                    min: 10,
                    max: 90,
                    divisions: 8,
                    label: '$_depositPct%',
                    onChanged: (v) => setState(() => _depositPct = v.toInt()),
                  ),
                ] else ...[
                  Text('Number of Installments: $_installmentCount (₹${(remainingBalance / _installmentCount).toStringAsFixed(0)} each)'),
                  Slider(
                    value: _installmentCount.toDouble(),
                    min: 2,
                    max: 6,
                    divisions: 4,
                    label: '$_installmentCount installments',
                    onChanged: (v) => setState(() => _installmentCount = v.toInt()),
                  ),
                ],
                const SizedBox(height: AppSpacing.lg),

                Row(
                  children: [
                    TextButton(
                      onPressed: () => setState(() => _showPlanForm = false),
                      child: const Text('Back'),
                    ),
                    const Spacer(),
                    FilledButton(
                      onPressed: _isLoading ? null : _handleCreatePlan,
                      child: _isLoading
                          ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                          : const Text('Create Plan'),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
