import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../theme/theme.dart';
import '../../../features/auth/auth_providers.dart';
import '../../../models/merchant_model.dart';
import '../merchant_repository.dart';

class KycScreen extends ConsumerStatefulWidget {
  const KycScreen({super.key});

  @override
  ConsumerState<KycScreen> createState() => _KycScreenState();
}

class _KycScreenState extends ConsumerState<KycScreen> {
  KycDocumentType _selectedType = KycDocumentType.pan;
  final _numberCtrl = TextEditingController();
  bool _submitting  = false;
  String? _error;
  bool _submitted   = false;

  // For prototype — a real implementation would upload a file and return a URL
  String get _mockFileUrl =>
      'https://storage.payflow.dev/kyc/${_selectedType.name}_${DateTime.now().millisecondsSinceEpoch}.pdf';

  String _merchantId() {
    return ref.read(authNotifierProvider).user?.merchantId ?? '';
  }

  Future<void> _submit() async {
    if (_numberCtrl.text.trim().isEmpty) {
      setState(() => _error = 'Document number is required');
      return;
    }
    final mid = _merchantId();
    if (mid.isEmpty) {
      setState(() => _error = 'Merchant profile not found. Please complete business setup first.');
      return;
    }
    setState(() { _submitting = true; _error = null; });
    try {
      await ref.read(merchantRepositoryProvider).submitKycDocument(
        merchantId:     mid,
        documentType:   _selectedType,
        documentNumber: _numberCtrl.text.trim(),
        fileUrl:        _mockFileUrl,
      );
      if (!mounted) return;
      setState(() { _submitted = true; _submitting = false; });
    } catch (e) {
      setState(() {
        _error = 'Could not submit document. Please try again.';
        _submitting = false;
      });
    }
  }

  @override
  void dispose() {
    _numberCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;

    return Scaffold(
      backgroundColor: cs.surface,
      appBar: AppBar(title: const Text('KYC verification')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _StepIndicator(current: 2, total: 2, cs: cs),
              const SizedBox(height: AppSpacing.xl),
              if (_submitted) ...[
                _SuccessCard(cs: cs, tt: tt, onContinue: () => context.go('/dashboard')),
              ] else ...[
                Text('Verify your identity', style: tt.headlineSmall),
                const SizedBox(height: AppSpacing.xs),
                Text(
                  'Submit at least one document. Our team will review within 24–48 hours.',
                  style: tt.bodyMedium?.copyWith(color: cs.onSurfaceVariant),
                ),
                const SizedBox(height: AppSpacing.xl),
                if (_error != null)
                  _ErrorBanner(
                    message: _error!,
                    onDismiss: () => setState(() => _error = null),
                  ),
                // ── Document type picker ────────────────────────────────────
                Text(
                  'Document type',
                  style: tt.labelMedium?.copyWith(color: cs.onSurfaceVariant),
                ),
                const SizedBox(height: AppSpacing.xs),
                _DocTypePicker(
                  selected: _selectedType,
                  onChanged: (t) => setState(() => _selectedType = t),
                  cs: cs,
                ),
                const SizedBox(height: AppSpacing.md),
                Text(
                  'Document number',
                  style: tt.labelMedium?.copyWith(color: cs.onSurfaceVariant),
                ),
                const SizedBox(height: AppSpacing.xs),
                TextFormField(
                  controller: _numberCtrl,
                  textCapitalization: TextCapitalization.characters,
                  decoration: InputDecoration(
                    hintText: _hintForType(_selectedType),
                    prefixIcon: const Icon(Icons.badge_outlined),
                  ),
                ),
                const SizedBox(height: AppSpacing.md),
                // ── File upload placeholder ─────────────────────────────────
                _UploadPlaceholder(cs: cs, tt: tt),
                const SizedBox(height: AppSpacing.xl),
                _submitting
                    ? _LoadingButton(cs: cs)
                    : ElevatedButton(
                        onPressed: _submit,
                        child: const Text('Submit document'),
                      ),
                const SizedBox(height: AppSpacing.md),
                OutlinedButton(
                  onPressed: () => context.go('/dashboard'),
                  child: const Text('Skip for now'),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  String _hintForType(KycDocumentType type) {
    switch (type) {
      case KycDocumentType.pan:             return 'ABCDE1234F';
      case KycDocumentType.gstin:           return '22AAAAA0000A1Z5';
      case KycDocumentType.aadhaar:         return 'XXXX XXXX XXXX';
      case KycDocumentType.incorporationCert: return 'U12345MH2020PTC000000';
      case KycDocumentType.bankStatement:   return 'Account number';
      case KycDocumentType.other:           return 'Document number';
    }
  }
}

// ── Sub-widgets ────────────────────────────────────────────────────────────────

class _DocTypePicker extends StatelessWidget {
  const _DocTypePicker({
    required this.selected,
    required this.onChanged,
    required this.cs,
  });
  final KycDocumentType selected;
  final ValueChanged<KycDocumentType> onChanged;
  final ColorScheme cs;

  static const _labels = {
    KycDocumentType.pan:             'PAN Card',
    KycDocumentType.gstin:           'GSTIN',
    KycDocumentType.aadhaar:         'Aadhaar',
    KycDocumentType.incorporationCert: 'Incorporation Certificate',
    KycDocumentType.bankStatement:   'Bank Statement',
    KycDocumentType.other:           'Other',
  };

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: AppSpacing.sm,
      runSpacing: AppSpacing.sm,
      children: KycDocumentType.values.map((type) {
        final isSelected = type == selected;
        return FilterChip(
          label: Text(_labels[type]!),
          selected: isSelected,
          onSelected: (_) => onChanged(type),
          selectedColor: cs.primaryContainer,
          checkmarkColor: cs.primary,
          labelStyle: TextStyle(
            color: isSelected ? cs.primary : cs.onSurfaceVariant,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
          ),
        );
      }).toList(),
    );
  }
}

class _UploadPlaceholder extends StatelessWidget {
  const _UploadPlaceholder({required this.cs, required this.tt});
  final ColorScheme cs;
  final TextTheme tt;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () {/* TODO: file picker integration */},
      borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
      child: DottedBorder(
        cs: cs,
        child: Column(
          children: [
            Icon(Icons.upload_file_outlined,
                size: AppSpacing.iconXl, color: cs.onSurfaceVariant),
            const SizedBox(height: AppSpacing.sm),
            Text('Tap to upload document', style: tt.bodyMedium),
            const SizedBox(height: AppSpacing.xs),
            Text('PDF, JPG or PNG · max 5 MB',
                style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant)),
          ],
        ),
      ),
    );
  }
}

class DottedBorder extends StatelessWidget {
  const DottedBorder({super.key, required this.cs, required this.child});
  final ColorScheme cs;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        border: Border.all(
          color: cs.outlineVariant,
          style: BorderStyle.solid,
          width: 1.5,
        ),
        borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
        color: cs.surfaceContainerHighest.withAlpha(77),
      ),
      child: child,
    );
  }
}

class _SuccessCard extends StatelessWidget {
  const _SuccessCard({
    required this.cs,
    required this.tt,
    required this.onContinue,
  });
  final ColorScheme cs;
  final TextTheme tt;
  final VoidCallback onContinue;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const SizedBox(height: AppSpacing.xxl),
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            color: const Color(0xFFDCFCE7),
            borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
          ),
          child: const Icon(
            Icons.check_circle_outline_rounded,
            color: Color(0xFF15803D),
            size: 48,
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        Text('Document submitted!', style: tt.headlineSmall),
        const SizedBox(height: AppSpacing.sm),
        Text(
          'We\'ve received your KYC document and will verify it within 24–48 hours. '
          'You can start using PayFlow while we review.',
          textAlign: TextAlign.center,
          style: tt.bodyMedium?.copyWith(color: cs.onSurfaceVariant),
        ),
        const SizedBox(height: AppSpacing.xxl),
        ElevatedButton(
          onPressed: onContinue,
          child: const Text('Go to Dashboard'),
        ),
      ],
    );
  }
}

class _StepIndicator extends StatelessWidget {
  const _StepIndicator({required this.current, required this.total, required this.cs});
  final int current;
  final int total;
  final ColorScheme cs;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: List.generate(total, (i) {
        return Expanded(
          child: Container(
            margin: EdgeInsets.only(right: i < total - 1 ? AppSpacing.xs : 0),
            height: 4,
            decoration: BoxDecoration(
              color: i < current ? cs.primary : cs.outlineVariant,
              borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
            ),
          ),
        );
      }),
    );
  }
}

class _ErrorBanner extends StatelessWidget {
  const _ErrorBanner({required this.message, required this.onDismiss});
  final String message;
  final VoidCallback onDismiss;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      margin: const EdgeInsets.only(bottom: AppSpacing.md),
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: cs.errorContainer,
        borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
      ),
      child: Row(children: [
        Icon(Icons.error_outline, color: cs.onErrorContainer),
        const SizedBox(width: AppSpacing.sm),
        Expanded(child: Text(message, style: TextStyle(color: cs.onErrorContainer))),
        IconButton(
          icon: Icon(Icons.close, color: cs.onErrorContainer),
          onPressed: onDismiss,
          padding: EdgeInsets.zero,
          constraints: const BoxConstraints(),
        ),
      ]),
    );
  }
}

class _LoadingButton extends StatelessWidget {
  const _LoadingButton({required this.cs});
  final ColorScheme cs;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 52,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: cs.primary.withAlpha(178),
          borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
        ),
        child: Center(
          child: SizedBox(
            width: 24,
            height: 24,
            child: CircularProgressIndicator(strokeWidth: 2.5, color: cs.onPrimary),
          ),
        ),
      ),
    );
  }
}
