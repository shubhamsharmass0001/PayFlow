import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../../../core/providers.dart';
import '../../../theme/theme.dart';

class CollectScreen extends ConsumerStatefulWidget {
  const CollectScreen({super.key});

  @override
  ConsumerState<CollectScreen> createState() => _CollectScreenState();
}

class _CollectScreenState extends ConsumerState<CollectScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _amountController = TextEditingController(text: '5000');
  final TextEditingController _noteController = TextEditingController(text: 'Store Order');

  int _selectedSplitIndex = 0;
  MobileScannerController? _scannerController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    if (!kIsWeb) {
      _scannerController = MobileScannerController(
        detectionSpeed: DetectionSpeed.noDuplicates,
      );
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    _amountController.dispose();
    _noteController.dispose();
    _scannerController?.dispose();
    super.dispose();
  }

  double get _totalAmount => double.tryParse(_amountController.text) ?? 0.0;

  /// Breaks down any amount > ₹2,000 into chunks of max ₹1,999
  List<double> _calculateSplits(double total) {
    if (total <= 0) return [0.0];
    if (total <= 2000.0) {
      return [double.parse(total.toStringAsFixed(2))];
    }
    final List<double> splits = [];
    double remaining = total;
    while (remaining > 0.001) {
      if (remaining > 1999.0) {
        splits.add(1999.0);
        remaining -= 1999.0;
      } else {
        splits.add(double.parse(remaining.toStringAsFixed(2)));
        remaining = 0.0;
      }
    }
    return splits;
  }

  String _buildQrString(double amount, {int? trancheIndex}) {
    final merchantId = ref.read(activeMerchantIdProvider);
    final suffix = trancheIndex != null ? '-T${trancheIndex + 1}' : '';
    return 'upi://pay?pa=apex.electronics@payflow&pn=Apex%20Electronics&am=${amount.toStringAsFixed(2)}&cu=INR&tn=${Uri.encodeComponent("${_noteController.text}$suffix")}&mc=5732&tr=MCH-$merchantId-${DateTime.now().millisecondsSinceEpoch}$suffix';
  }

  void _onBarcodeDetected(BarcodeCapture capture) {
    final barcode = capture.barcodes.firstOrNull;
    if (barcode?.rawValue != null && barcode!.rawValue!.isNotEmpty) {
      _showScannedDialog(barcode.rawValue!);
    }
  }

  /// Dialog triggered upon camera QR scan
  void _showScannedDialog(String raw) {
    double detectedAmount = 5000.0;
    try {
      final uri = Uri.parse(raw);
      final amStr = uri.queryParameters['am'];
      if (amStr != null) {
        detectedAmount = double.tryParse(amStr) ?? 5000.0;
      }
    } catch (_) {}

    final splits = _calculateSplits(detectedAmount);
    final isSplit = detectedAmount > 2000.0;

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.qr_code_scanner_rounded, color: Colors.indigo),
            SizedBox(width: 8),
            Text('Scanned Payment'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Total Amount: ₹${detectedAmount.toStringAsFixed(2)}',
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            if (isSplit) ...[
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.amber.withAlpha(40),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.amber.shade700),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.bolt_rounded, color: Colors.amber.shade800, size: 18),
                        const SizedBox(width: 6),
                        const Text(
                          'Amount > ₹2,000 Auto-Split Applied',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Broken down into ${splits.length} simultaneous payments (max ₹1,999 each):',
                      style: const TextStyle(fontSize: 11),
                    ),
                    const SizedBox(height: 4),
                    Wrap(
                      spacing: 6,
                      children: splits.asMap().entries.map((e) {
                        return Chip(
                          visualDensity: VisualDensity.compact,
                          label: Text('Split ${e.key + 1}: ₹${e.value.toStringAsFixed(0)}'),
                          backgroundColor: Colors.white,
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 10),
            ],
            const Text(
              'Raw URI / Details:',
              style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12),
            ),
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.grey.withAlpha(30),
                borderRadius: BorderRadius.circular(6),
              ),
              child: SelectableText(
                raw,
                style: const TextStyle(fontFamily: 'monospace', fontSize: 11),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Cancel'),
          ),
          FilledButton.icon(
            icon: const Icon(Icons.flash_on_rounded),
            label: Text(
              isSplit ? 'Pay ${splits.length} Splits Simultaneously' : 'Pay ₹${detectedAmount.toStringAsFixed(0)}',
            ),
            onPressed: () {
              Navigator.of(ctx).pop();
              _runSimultaneousPaymentSimulation(splits, detectedAmount);
            },
          ),
        ],
      ),
    );
  }

  /// Runs simultaneous animated payment simulation with live progress bars
  void _runSimultaneousPaymentSimulation(List<double> splits, double total) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => _SimultaneousPaymentDialog(
        splits: splits,
        totalAmount: total,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;
    final splits = _calculateSplits(_totalAmount);
    final isSplit = _totalAmount > 2000.0;

    if (_selectedSplitIndex >= splits.length) {
      _selectedSplitIndex = 0;
    }

    final currentDisplayAmount = isSplit ? splits[_selectedSplitIndex] : _totalAmount;
    final currentQrString = _buildQrString(
      currentDisplayAmount,
      trancheIndex: isSplit ? _selectedSplitIndex : null,
    );

    return Scaffold(
      appBar: AppBar(
        title: const Text('Collect & Pay'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.qr_code_2_rounded), text: 'Show QR (Receive)'),
            Tab(icon: Icon(Icons.qr_code_scanner_rounded), text: 'Scan QR (Camera)'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // ── Tab 1: Show QR to Receive ──
          SingleChildScrollView(
            padding: const EdgeInsets.all(AppSpacing.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Amount Input Card
                Card(
                  elevation: 0,
                  color: cs.surfaceContainerHighest.withAlpha(100),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                    side: BorderSide(color: cs.outlineVariant.withAlpha(100)),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(AppSpacing.md),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Point-of-Sale (POS) Total Amount',
                          style: tt.titleSmall?.copyWith(fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: AppSpacing.sm),
                        TextField(
                          controller: _amountController,
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          style: tt.headlineMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: cs.primary,
                          ),
                          decoration: InputDecoration(
                            prefixText: '₹ ',
                            prefixStyle: tt.headlineMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: cs.primary,
                            ),
                            border: const OutlineInputBorder(),
                            labelText: 'Enter payment amount',
                            hintText: 'e.g. 5000',
                          ),
                          onChanged: (_) => setState(() {
                            _selectedSplitIndex = 0;
                          }),
                        ),
                        const SizedBox(height: AppSpacing.sm),

                        // Quick amount chips
                        Wrap(
                          spacing: 8,
                          runSpacing: 6,
                          children: [500, 1500, 2500, 4000, 5000, 10000].map((amt) {
                            final isAboveLimit = amt > 2000;
                            return ActionChip(
                              avatar: isAboveLimit
                                  ? const Icon(Icons.auto_awesome, size: 14, color: Colors.orange)
                                  : null,
                              label: Text('₹$amt${isAboveLimit ? " (Split)" : ""}'),
                              onPressed: () {
                                _amountController.text = amt.toString();
                                setState(() {
                                  _selectedSplitIndex = 0;
                                });
                              },
                            );
                          }).toList(),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: AppSpacing.md),

                // Auto-Split Banner (if amount > ₹2000)
                if (isSplit) ...[
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(AppSpacing.md),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [Colors.purple.shade900.withAlpha(200), Colors.indigo.shade900.withAlpha(200)],
                      ),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.purpleAccent.withAlpha(120)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(6),
                              decoration: BoxDecoration(
                                color: Colors.purpleAccent.withAlpha(60),
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(Icons.call_split_rounded, color: Colors.purpleAccent, size: 20),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text(
                                    'Smart Auto-Split Activated (> ₹2,000)',
                                    style: TextStyle(
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 14,
                                    ),
                                  ),
                                  Text(
                                    'Broken into ${splits.length} tranches of max ₹1,999 for instant clearance',
                                    style: TextStyle(color: Colors.white.withAlpha(200), fontSize: 11),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),

                        // Split selector pills
                        SingleChildScrollView(
                          scrollDirection: Axis.horizontal,
                          child: Row(
                            children: splits.asMap().entries.map((entry) {
                              final idx = entry.key;
                              final val = entry.value;
                              final isSelected = _selectedSplitIndex == idx;
                              return Padding(
                                padding: const EdgeInsets.only(right: 8),
                                child: ChoiceChip(
                                  selectedColor: Colors.purpleAccent,
                                  backgroundColor: Colors.white.withAlpha(30),
                                  label: Text(
                                    'Split ${idx + 1}: ₹${val.toStringAsFixed(0)}',
                                    style: TextStyle(
                                      color: isSelected ? Colors.black : Colors.white,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  selected: isSelected,
                                  onSelected: (selected) {
                                    if (selected) {
                                      setState(() {
                                        _selectedSplitIndex = idx;
                                      });
                                    }
                                  },
                                ),
                              );
                            }).toList(),
                          ),
                        ),
                        const SizedBox(height: 12),

                        // Pay simultaneously action button
                        SizedBox(
                          width: double.infinity,
                          child: FilledButton.icon(
                            style: FilledButton.styleFrom(
                              backgroundColor: Colors.purpleAccent,
                              foregroundColor: Colors.black,
                              padding: const EdgeInsets.symmetric(vertical: 12),
                            ),
                            icon: const Icon(Icons.flash_on_rounded),
                            label: Text(
                              'Pay All ${splits.length} Splits Simultaneously (Simulate)',
                              style: const TextStyle(fontWeight: FontWeight.bold),
                            ),
                            onPressed: () => _runSimultaneousPaymentSimulation(splits, _totalAmount),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: AppSpacing.md),
                ],

                // Dynamic QR Display Card
                Container(
                  padding: const EdgeInsets.all(AppSpacing.lg),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withAlpha(30),
                        blurRadius: 16,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      QrImageView(
                        data: currentQrString,
                        version: QrVersions.auto,
                        size: 210.0,
                        backgroundColor: Colors.white,
                      ),
                      const SizedBox(height: AppSpacing.sm),
                      Text(
                        isSplit
                            ? 'TRANCHE ${_selectedSplitIndex + 1} OF ${splits.length} (₹${currentDisplayAmount.toStringAsFixed(0)})'
                            : 'BHARAT UPI QR (₹${_totalAmount.toStringAsFixed(0)})',
                        style: const TextStyle(
                          color: Colors.black87,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1.5,
                          fontSize: 12,
                        ),
                      ),
                      const SizedBox(height: 2),
                      const Text(
                        'Scan with Google Pay, PhonePe, or Paytm',
                        style: TextStyle(color: Colors.black54, fontSize: 11),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: AppSpacing.md),

                // Soundbox & Share Buttons
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    FilledButton.tonalIcon(
                      icon: const Icon(Icons.volume_up_rounded),
                      label: const Text('Soundbox Test'),
                      onPressed: () {
                        final msg = isSplit
                            ? '🔊 PayFlow Soundbox: "Split payment of ₹${currentDisplayAmount.toStringAsFixed(0)} received on UPI"'
                            : '🔊 PayFlow Soundbox: "₹${_totalAmount.toStringAsFixed(0)} received successfully on UPI"';
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(msg),
                            backgroundColor: Colors.teal,
                            duration: const Duration(seconds: 3),
                          ),
                        );
                      },
                    ),
                    const SizedBox(width: AppSpacing.sm),
                    OutlinedButton.icon(
                      icon: const Icon(Icons.copy_rounded),
                      label: const Text('Copy Link'),
                      onPressed: () {
                        Clipboard.setData(ClipboardData(text: currentQrString));
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('UPI Intent link copied!')),
                        );
                      },
                    ),
                  ],
                ),
              ],
            ),
          ),

          // ── Tab 2: Scan QR with Camera ──
          Column(
            children: [
              Container(
                padding: const EdgeInsets.all(AppSpacing.md),
                color: cs.surfaceContainerHighest.withAlpha(80),
                child: Row(
                  children: [
                    const Icon(Icons.camera_alt_outlined, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Scan any QR code. If amount > ₹2,000, it automatically splits into ₹1,999 for simultaneous payment.',
                        style: tt.bodySmall,
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    if (!kIsWeb && _scannerController != null)
                      MobileScanner(
                        controller: _scannerController!,
                        onDetect: _onBarcodeDetected,
                      )
                    else
                      Container(
                        color: Colors.black87,
                        child: Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(Icons.qr_code_scanner_rounded, size: 64, color: Colors.white54),
                              const SizedBox(height: 16),
                              Text(
                                'Camera Scanner',
                                style: tt.titleMedium?.copyWith(color: Colors.white),
                              ),
                              const SizedBox(height: 8),
                              const Text(
                                'Web/Desktop View: Camera active on physical phone',
                                style: TextStyle(color: Colors.white60),
                              ),
                              const SizedBox(height: 20),
                              FilledButton.icon(
                                icon: const Icon(Icons.bolt_rounded),
                                label: const Text('Test Sample QR: ₹5,000 (> ₹2,000 Split)'),
                                onPressed: () {
                                  _showScannedDialog(
                                    'upi://pay?pa=merchant.vendor@upi&pn=Supplier&am=5000.00&cu=INR&tn=Invoice-PO-9841',
                                  );
                                },
                              ),
                            ],
                          ),
                        ),
                      ),

                    // Viewfinder reticle overlay
                    Container(
                      width: 260,
                      height: 260,
                      decoration: BoxDecoration(
                        border: Border.all(color: cs.primary, width: 3),
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),

                    // Scanner controls
                    Positioned(
                      bottom: 24,
                      child: Row(
                        children: [
                          IconButton.filledTonal(
                            icon: const Icon(Icons.flash_on_rounded),
                            tooltip: 'Toggle Flash',
                            onPressed: () => _scannerController?.toggleTorch(),
                          ),
                          const SizedBox(width: 20),
                          IconButton.filled(
                            icon: const Icon(Icons.flip_camera_ios_rounded),
                            tooltip: 'Switch Camera',
                            onPressed: () => _scannerController?.switchCamera(),
                          ),
                          const SizedBox(width: 20),
                          IconButton.filledTonal(
                            icon: const Icon(Icons.bug_report_rounded),
                            tooltip: 'Test ₹5,000 Sample',
                            onPressed: () {
                              _showScannedDialog(
                                'upi://pay?pa=merchant.vendor@upi&pn=Supplier&am=5000.00&cu=INR&tn=Invoice-PO-9841',
                              );
                            },
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Simultaneous Payment Execution Dialog with Live Parallel Progress
// ─────────────────────────────────────────────────────────────────────────────

class _SimultaneousPaymentDialog extends StatefulWidget {
  const _SimultaneousPaymentDialog({
    required this.splits,
    required this.totalAmount,
  });

  final List<double> splits;
  final double totalAmount;

  @override
  State<_SimultaneousPaymentDialog> createState() => _SimultaneousPaymentDialogState();
}

class _SimultaneousPaymentDialogState extends State<_SimultaneousPaymentDialog> {
  late List<double> _progresses;
  late List<bool> _isCompleted;
  bool _allDone = false;

  @override
  void initState() {
    super.initState();
    _progresses = List.generate(widget.splits.length, (_) => 0.0);
    _isCompleted = List.generate(widget.splits.length, (_) => false);
    _startSimultaneousPayments();
  }

  void _startSimultaneousPayments() {
    // Launch all split payments concurrently!
    for (int i = 0; i < widget.splits.length; i++) {
      final index = i;
      // Slight stagger to visualize parallel async execution nicely
      final stepDelay = Duration(milliseconds: 150 + (index * 80));
      Timer.periodic(stepDelay, (timer) {
        if (!mounted) {
          timer.cancel();
          return;
        }
        setState(() {
          if (_progresses[index] < 1.0) {
            _progresses[index] += 0.25;
            if (_progresses[index] >= 1.0) {
              _progresses[index] = 1.0;
              _isCompleted[index] = true;
              timer.cancel();
              _checkAllCompleted();
            }
          }
        });
      });
    }
  }

  void _checkAllCompleted() {
    if (_isCompleted.every((c) => c)) {
      setState(() {
        _allDone = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return AlertDialog(
      title: Row(
        children: [
          Icon(
            _allDone ? Icons.check_circle_rounded : Icons.sync_rounded,
            color: _allDone ? Colors.green : cs.primary,
          ),
          const SizedBox(width: 8),
          Text(
            _allDone ? 'Simultaneous Payment Complete!' : 'Processing ${widget.splits.length} Splits Simultaneously',
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
        ],
      ),
      content: SizedBox(
        width: double.maxFinite,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Total Authorized: ₹${widget.totalAmount.toStringAsFixed(2)}',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
            ),
            const SizedBox(height: 4),
            Text(
              'Each split is capped under ₹2,000 for instant zero-fee clearance.',
              style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
            ),
            const Divider(height: 24),

            // Live progress bars for each tranche
            ...widget.splits.asMap().entries.map((entry) {
              final idx = entry.key;
              final amt = entry.value;
              final done = _isCompleted[idx];
              final prog = _progresses[idx];

              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Split ${idx + 1}: ₹${amt.toStringAsFixed(2)}',
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            color: done ? Colors.green.shade700 : cs.onSurface,
                          ),
                        ),
                        Text(
                          done ? '✓ Paid' : '${(prog * 100).toInt()}%',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                            color: done ? Colors.green.shade700 : cs.primary,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    LinearProgressIndicator(
                      value: prog,
                      backgroundColor: Colors.grey.withAlpha(40),
                      color: done ? Colors.green : Colors.purpleAccent,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ],
                ),
              );
            }),

            if (_allDone) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.green.withAlpha(30),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.verified_rounded, color: Colors.green, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'All ${widget.splits.length} splits cleared simultaneously via instant UPI settlement.',
                        style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
      actions: [
        if (_allDone)
          FilledButton.icon(
            icon: const Icon(Icons.check_rounded),
            label: const Text('Done / View Receipt'),
            onPressed: () {
              Navigator.of(context).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Consolidated receipt for ₹${widget.totalAmount.toStringAsFixed(2)} generated!'),
                  backgroundColor: Colors.green,
                ),
              );
            },
          ),
      ],
    );
  }
}
