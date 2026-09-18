import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../theme/theme.dart';
import '../../../models/merchant_model.dart';
import '../merchant_repository.dart';

class MerchantSetupScreen extends ConsumerStatefulWidget {
  const MerchantSetupScreen({super.key});

  @override
  ConsumerState<MerchantSetupScreen> createState() =>
      _MerchantSetupScreenState();
}

class _MerchantSetupScreenState extends ConsumerState<MerchantSetupScreen> {
  final _formKey        = GlobalKey<FormState>();
  final _bizNameCtrl    = TextEditingController();
  final _legalNameCtrl  = TextEditingController();
  final _emailCtrl      = TextEditingController();
  final _phoneCtrl      = TextEditingController();
  final _upiCtrl        = TextEditingController();
  final _mccCtrl        = TextEditingController();
  bool _submitting      = false;
  String? _error;

  @override
  void dispose() {
    _bizNameCtrl.dispose();
    _legalNameCtrl.dispose();
    _emailCtrl.dispose();
    _phoneCtrl.dispose();
    _upiCtrl.dispose();
    _mccCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _submitting = true; _error = null; });
    try {
      await ref.read(merchantRepositoryProvider).createMerchant(
        CreateMerchantRequest(
          businessName: _bizNameCtrl.text.trim(),
          legalName:    _legalNameCtrl.text.trim(),
          email:        _emailCtrl.text.trim(),
          phone:        _phoneCtrl.text.trim(),
          upiVpa:       _upiCtrl.text.trim().isEmpty ? null : _upiCtrl.text.trim(),
          mccCode:      _mccCtrl.text.trim().isEmpty ? null : _mccCtrl.text.trim(),
        ),
      );
      if (!mounted) return;
      context.go('/onboarding/kyc');
    } catch (e) {
      setState(() => _error = 'Could not save merchant details. Please try again.');
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;

    return Scaffold(
      backgroundColor: cs.surface,
      appBar: AppBar(title: const Text('Business setup')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── Progress indicator ──────────────────────────────────────
              _StepIndicator(current: 1, total: 2, cs: cs),
              const SizedBox(height: AppSpacing.xl),
              Text('Tell us about your business', style: tt.headlineSmall),
              const SizedBox(height: AppSpacing.xs),
              Text(
                'This information is used for KYC verification and payment settlements.',
                style: tt.bodyMedium?.copyWith(color: cs.onSurfaceVariant),
              ),
              const SizedBox(height: AppSpacing.xl),
              if (_error != null)
                _ErrorBanner(message: _error!, onDismiss: () => setState(() => _error = null)),
              Form(
                key: _formKey,
                child: Column(
                  children: [
                    _LabeledField(
                      label: 'Business / trading name *',
                      child: TextFormField(
                        controller: _bizNameCtrl,
                        textCapitalization: TextCapitalization.words,
                        textInputAction: TextInputAction.next,
                        decoration: const InputDecoration(
                          hintText: 'e.g. Sharma Electronics',
                          prefixIcon: Icon(Icons.store_outlined),
                        ),
                        validator: (v) => (v == null || v.trim().isEmpty)
                            ? 'Business name is required'
                            : null,
                      ),
                    ),
                    const SizedBox(height: AppSpacing.md),
                    _LabeledField(
                      label: 'Legal / registered name *',
                      child: TextFormField(
                        controller: _legalNameCtrl,
                        textCapitalization: TextCapitalization.words,
                        textInputAction: TextInputAction.next,
                        decoration: const InputDecoration(
                          hintText: 'As per incorporation certificate',
                          prefixIcon: Icon(Icons.business_outlined),
                        ),
                        validator: (v) => (v == null || v.trim().isEmpty)
                            ? 'Legal name is required'
                            : null,
                      ),
                    ),
                    const SizedBox(height: AppSpacing.md),
                    _LabeledField(
                      label: 'Business email *',
                      child: TextFormField(
                        controller: _emailCtrl,
                        keyboardType: TextInputType.emailAddress,
                        textInputAction: TextInputAction.next,
                        decoration: const InputDecoration(
                          hintText: 'settlements@mybusiness.com',
                          prefixIcon: Icon(Icons.email_outlined),
                        ),
                        validator: (v) {
                          if (v == null || v.trim().isEmpty) return 'Email is required';
                          if (!v.contains('@')) return 'Enter a valid email';
                          return null;
                        },
                      ),
                    ),
                    const SizedBox(height: AppSpacing.md),
                    _LabeledField(
                      label: 'Business phone *',
                      child: TextFormField(
                        controller: _phoneCtrl,
                        keyboardType: TextInputType.phone,
                        textInputAction: TextInputAction.next,
                        decoration: const InputDecoration(
                          hintText: '+91 98765 43210',
                          prefixIcon: Icon(Icons.phone_outlined),
                        ),
                        validator: (v) => (v == null || v.trim().isEmpty)
                            ? 'Phone is required'
                            : null,
                      ),
                    ),
                    const SizedBox(height: AppSpacing.md),
                    _LabeledField(
                      label: 'UPI VPA (optional)',
                      child: TextFormField(
                        controller: _upiCtrl,
                        keyboardType: TextInputType.emailAddress,
                        textInputAction: TextInputAction.next,
                        decoration: const InputDecoration(
                          hintText: 'mybusiness@okaxis',
                          prefixIcon: Icon(Icons.qr_code_outlined),
                        ),
                      ),
                    ),
                    const SizedBox(height: AppSpacing.md),
                    _LabeledField(
                      label: 'MCC code (optional)',
                      child: TextFormField(
                        controller: _mccCtrl,
                        keyboardType: TextInputType.number,
                        textInputAction: TextInputAction.done,
                        maxLength: 4,
                        decoration: const InputDecoration(
                          hintText: '5411',
                          prefixIcon: Icon(Icons.category_outlined),
                          counterText: '',
                        ),
                      ),
                    ),
                    const SizedBox(height: AppSpacing.xl),
                    _submitting
                        ? _LoadingButton(cs: cs)
                        : ElevatedButton(
                            onPressed: _submit,
                            child: const Text('Continue to KYC'),
                          ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ────────────────────────────────────────────────────────────────────────────

class _StepIndicator extends StatelessWidget {
  const _StepIndicator({
    required this.current,
    required this.total,
    required this.cs,
  });
  final int current;
  final int total;
  final ColorScheme cs;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: List.generate(total, (i) {
        final active = i < current;
        return Expanded(
          child: Container(
            margin: EdgeInsets.only(right: i < total - 1 ? AppSpacing.xs : 0),
            height: 4,
            decoration: BoxDecoration(
              color: active ? cs.primary : cs.outlineVariant,
              borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
            ),
          ),
        );
      }),
    );
  }
}

class _LabeledField extends StatelessWidget {
  const _LabeledField({required this.label, required this.child});
  final String label;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label,
            style: Theme.of(context)
                .textTheme
                .labelMedium
                ?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant)),
        const SizedBox(height: AppSpacing.xs),
        child,
      ],
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
