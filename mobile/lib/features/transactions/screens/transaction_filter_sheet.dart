import 'package:flutter/material.dart';
import '../../../theme/theme.dart';
import '../transaction_providers.dart';

class TransactionFilterSheet extends StatefulWidget {
  const TransactionFilterSheet({
    super.key,
    required this.initialFilters,
    required this.onApply,
  });

  final TransactionFilterState initialFilters;
  final ValueChanged<TransactionFilterState> onApply;

  static Future<void> show(
    BuildContext context, {
    required TransactionFilterState initialFilters,
    required ValueChanged<TransactionFilterState> onApply,
  }) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => TransactionFilterSheet(
        initialFilters: initialFilters,
        onApply: onApply,
      ),
    );
  }

  @override
  State<TransactionFilterSheet> createState() => _TransactionFilterSheetState();
}

class _TransactionFilterSheetState extends State<TransactionFilterSheet> {
  late String? _selectedStatus;
  late String? _selectedMethod;
  late String? _startDate;
  late String? _endDate;

  static const _statuses = [
    'SUCCESS',
    'INITIATED',
    'PENDING',
    'FAILED',
    'TIMEOUT',
    'DUPLICATE',
    'REFUNDED',
  ];

  static const _methods = [
    'UPI_QR',
    'UPI_INTENT',
    'UPI_COLLECT',
    'CARD',
    'NET_BANKING',
    'WALLET',
  ];

  @override
  void initState() {
    super.initState();
    _selectedStatus = widget.initialFilters.status;
    _selectedMethod = widget.initialFilters.paymentMethod;
    _startDate = widget.initialFilters.startDate;
    _endDate = widget.initialFilters.endDate;
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
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: SafeArea(
        child: SingleChildScrollView(
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

              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Filter Transactions', style: tt.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                  TextButton(
                    onPressed: () {
                      setState(() {
                        _selectedStatus = null;
                        _selectedMethod = null;
                        _startDate = null;
                        _endDate = null;
                      });
                    },
                    child: const Text('Reset All'),
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.md),

              // Status Chips
              Text('Status', style: tt.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: AppSpacing.xs),
              Wrap(
                spacing: AppSpacing.xs,
                runSpacing: AppSpacing.xs,
                children: _statuses.map((s) {
                  final isSelected = _selectedStatus == s;
                  return ChoiceChip(
                    label: Text(s),
                    selected: isSelected,
                    onSelected: (selected) {
                      setState(() => _selectedStatus = selected ? s : null);
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: AppSpacing.lg),

              // Payment Method Chips
              Text('Payment Method', style: tt.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: AppSpacing.xs),
              Wrap(
                spacing: AppSpacing.xs,
                runSpacing: AppSpacing.xs,
                children: _methods.map((m) {
                  final isSelected = _selectedMethod == m;
                  return ChoiceChip(
                    label: Text(m),
                    selected: isSelected,
                    onSelected: (selected) {
                      setState(() => _selectedMethod = selected ? m : null);
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: AppSpacing.xl),

              // Action Buttons
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.of(context).pop(),
                      child: const Text('Cancel'),
                    ),
                  ),
                  const SizedBox(width: AppSpacing.md),
                  Expanded(
                    child: FilledButton(
                      onPressed: () {
                        widget.onApply(
                          TransactionFilterState(
                            status: _selectedStatus,
                            paymentMethod: _selectedMethod,
                            startDate: _startDate,
                            endDate: _endDate,
                          ),
                        );
                        Navigator.of(context).pop();
                      },
                      child: const Text('Apply Filters'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
