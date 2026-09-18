import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../../core/providers.dart';
import '../../../models/invoice_models.dart';
import '../../../theme/theme.dart';
import '../invoice_providers.dart';
import '../invoice_repository.dart';

class _LineItemDraft {
  _LineItemDraft({
    required this.nameCtrl,
    required this.qtyCtrl,
    required this.priceCtrl,
    required this.taxCtrl,
  });

  final TextEditingController nameCtrl;
  final TextEditingController qtyCtrl;
  final TextEditingController priceCtrl;
  final TextEditingController taxCtrl;

  double get quantity => double.tryParse(qtyCtrl.text) ?? 1.0;
  double get unitPrice => double.tryParse(priceCtrl.text) ?? 0.0;
  double get taxRate => double.tryParse(taxCtrl.text) ?? 18.0;

  double get lineTotal => quantity * unitPrice;
  double get lineTax => lineTotal * (taxRate / 100);

  void dispose() {
    nameCtrl.dispose();
    qtyCtrl.dispose();
    priceCtrl.dispose();
    taxCtrl.dispose();
  }
}

class InvoiceFormScreen extends ConsumerStatefulWidget {
  const InvoiceFormScreen({super.key});

  @override
  ConsumerState<InvoiceFormScreen> createState() => _InvoiceFormScreenState();
}

class _InvoiceFormScreenState extends ConsumerState<InvoiceFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _customerNameCtrl = TextEditingController();
  final _notesCtrl = TextEditingController();
  DateTime _dueDate = DateTime.now().add(const Duration(days: 15));
  bool _submitting = false;

  final List<_LineItemDraft> _items = [];

  @override
  void initState() {
    super.initState();
    _addNewItem();
  }

  void _addNewItem() {
    setState(() {
      _items.add(
        _LineItemDraft(
          nameCtrl: TextEditingController(),
          qtyCtrl: TextEditingController(text: '1'),
          priceCtrl: TextEditingController(),
          taxCtrl: TextEditingController(text: '18'),
        ),
      );
    });
  }

  void _removeItem(int index) {
    if (_items.length <= 1) return;
    setState(() {
      final item = _items.removeAt(index);
      item.dispose();
    });
  }

  @override
  void dispose() {
    _customerNameCtrl.dispose();
    _notesCtrl.dispose();
    for (final item in _items) {
      item.dispose();
    }
    super.dispose();
  }

  double get subtotal => _items.fold(0.0, (sum, i) => sum + i.lineTotal);
  double get taxTotal => _items.fold(0.0, (sum, i) => sum + i.lineTax);
  double get grandTotal => subtotal + taxTotal;

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _submitting = true);

    try {
      final merchantId = ref.read(activeMerchantIdProvider);
      final repo = ref.read(invoiceRepositoryProvider);

      final lineItemMaps = _items.map((i) {
        return {
          'name': i.nameCtrl.text.trim(),
          'description': i.nameCtrl.text.trim(),
          'quantity': i.quantity.toStringAsFixed(2),
          'unit_price': i.unitPrice.toStringAsFixed(2),
          'tax_rate': i.taxRate.toStringAsFixed(2),
        };
      }).toList();

      final created = await repo.createInvoice(
        merchantId,
        CreateInvoiceRequest(
          customerId: null,
          dueDate: _dueDate.toIso8601String(),
          notes: _notesCtrl.text.trim().isEmpty ? null : _notesCtrl.text.trim(),
          items: lineItemMaps,
        ),
      );

      ref.read(invoiceListProvider.notifier).loadFirstPage();

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Invoice #${created.invoiceNumber} created successfully!'),
          backgroundColor: Colors.green,
        ),
      );
      context.go('/invoices/${created.id}');
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to create invoice: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;
    final dateFmt = DateFormat.yMMMd();

    return Scaffold(
      appBar: AppBar(
        title: const Text('New Invoice'),
        actions: [
          TextButton(
            onPressed: _submitting ? null : _submit,
            child: _submitting
                ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                : const Text('Save', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(AppSpacing.md),
          children: [
            // Customer Info
            Card(
              elevation: 0,
              shape: RoundedRectangleBorder(
                side: BorderSide(color: cs.outlineVariant),
                borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
              ),
              child: Padding(
                padding: const EdgeInsets.all(AppSpacing.md),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Customer & Terms', style: tt.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                    const SizedBox(height: AppSpacing.sm),
                    TextFormField(
                      controller: _customerNameCtrl,
                      decoration: const InputDecoration(
                        labelText: 'Customer Name / Reference',
                        prefixIcon: Icon(Icons.person_outline),
                        hintText: 'e.g. Acme Corp or John Doe',
                      ),
                    ),
                    const SizedBox(height: AppSpacing.md),
                    ListTile(
                      contentPadding: EdgeInsets.zero,
                      leading: const Icon(Icons.calendar_today_rounded),
                      title: const Text('Due Date'),
                      subtitle: Text(dateFmt.format(_dueDate)),
                      trailing: const Icon(Icons.edit_calendar_rounded),
                      onTap: () async {
                        final picked = await showDatePicker(
                          context: context,
                          initialDate: _dueDate,
                          firstDate: DateTime.now(),
                          lastDate: DateTime.now().add(const Duration(days: 365)),
                        );
                        if (picked != null) setState(() => _dueDate = picked);
                      },
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: AppSpacing.lg),

            // Line Items header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Line Items (${_items.length})', style: tt.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                TextButton.icon(
                  onPressed: _addNewItem,
                  icon: const Icon(Icons.add_rounded),
                  label: const Text('Add Item'),
                ),
              ],
            ),
            const SizedBox(height: AppSpacing.xs),

            // Dynamic items list
            ..._items.asMap().entries.map((entry) {
              final idx = entry.key;
              final item = entry.value;

              return Card(
                key: ObjectKey(item),
                margin: const EdgeInsets.only(bottom: AppSpacing.sm),
                elevation: 0,
                shape: RoundedRectangleBorder(
                  side: BorderSide(color: cs.outlineVariant.withAlpha(120)),
                  borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(AppSpacing.md),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: TextFormField(
                              controller: item.nameCtrl,
                              decoration: InputDecoration(
                                labelText: 'Item #${idx + 1} Description',
                                hintText: 'Product or service',
                                isDense: true,
                              ),
                              validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                            ),
                          ),
                          if (_items.length > 1)
                            IconButton(
                              icon: const Icon(Icons.delete_outline_rounded, color: Colors.red),
                              onPressed: () => _removeItem(idx),
                            ),
                        ],
                      ),
                      const SizedBox(height: AppSpacing.sm),
                      Row(
                        children: [
                          Expanded(
                            flex: 2,
                            child: TextFormField(
                              controller: item.qtyCtrl,
                              keyboardType: TextInputType.number,
                              decoration: const InputDecoration(labelText: 'Qty', isDense: true),
                              onChanged: (_) => setState(() {}),
                              validator: (v) => (double.tryParse(v ?? '') ?? 0) <= 0 ? 'Invalid' : null,
                            ),
                          ),
                          const SizedBox(width: AppSpacing.sm),
                          Expanded(
                            flex: 3,
                            child: TextFormField(
                              controller: item.priceCtrl,
                              keyboardType: TextInputType.number,
                              decoration: const InputDecoration(
                                labelText: 'Price (₹)',
                                prefixText: '₹',
                                isDense: true,
                              ),
                              onChanged: (_) => setState(() {}),
                              validator: (v) => (double.tryParse(v ?? '') ?? 0) < 0 ? 'Invalid' : null,
                            ),
                          ),
                          const SizedBox(width: AppSpacing.sm),
                          Expanded(
                            flex: 2,
                            child: TextFormField(
                              controller: item.taxCtrl,
                              keyboardType: TextInputType.number,
                              decoration: const InputDecoration(
                                labelText: 'GST %',
                                suffixText: '%',
                                isDense: true,
                              ),
                              onChanged: (_) => setState(() {}),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              );
            }),
            const SizedBox(height: AppSpacing.md),

            // Summary Totals
            Card(
              elevation: 0,
              color: cs.surfaceContainerHighest.withAlpha(50),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
              ),
              child: Padding(
                padding: const EdgeInsets.all(AppSpacing.lg),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Subtotal', style: tt.bodyMedium),
                        Text('₹${subtotal.toStringAsFixed(2)}', style: tt.bodyMedium?.copyWith(fontWeight: FontWeight.w600)),
                      ],
                    ),
                    const SizedBox(height: AppSpacing.xs),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Tax (GST)', style: tt.bodyMedium),
                        Text('₹${taxTotal.toStringAsFixed(2)}', style: tt.bodyMedium?.copyWith(fontWeight: FontWeight.w600)),
                      ],
                    ),
                    const Divider(height: AppSpacing.lg),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Total Amount', style: tt.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                        Text(
                          '₹${grandTotal.toStringAsFixed(2)}',
                          style: tt.titleLarge?.copyWith(
                            fontWeight: FontWeight.w900,
                            color: cs.primary,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: AppSpacing.lg),

            TextFormField(
              controller: _notesCtrl,
              maxLines: 2,
              decoration: const InputDecoration(
                labelText: 'Notes & Payment Instructions (optional)',
                hintText: 'e.g. Thanks for your business!',
              ),
            ),
            const SizedBox(height: AppSpacing.xl),

            FilledButton.icon(
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: AppSpacing.md),
              ),
              onPressed: _submitting ? null : _submit,
              icon: _submitting
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Icon(Icons.check_rounded),
              label: const Text('Create & Issue Invoice'),
            ),
            const SizedBox(height: AppSpacing.xxl),
          ],
        ),
      ),
    );
  }
}
