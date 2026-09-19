import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../../../core/providers.dart';

class CollectScreen extends ConsumerStatefulWidget {
  const CollectScreen({super.key});

  @override
  ConsumerState<CollectScreen> createState() => _CollectScreenState();
}

class _CollectScreenState extends ConsumerState<CollectScreen> {
  int _activeTab = 0; // 0: Receive Slip (Multiple QRs), 1: Scan & Pay (Camera)
  final TextEditingController _amountController = TextEditingController(text: '5000');
  final TextEditingController _noteController = TextEditingController(text: 'Store Order');

  // Track paid status per tranche for live slip updates
  final Set<int> _paidTranches = {};
  bool _allTranchesPaid = false;

  MobileScannerController? _scannerController;

  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
    _amountController.dispose();
    _noteController.dispose();
    _scannerController?.dispose();
    super.dispose();
  }

  void _initScannerIfNeeded() {
    if (_scannerController == null && !kIsWeb) {
      try {
        _scannerController = MobileScannerController(
          detectionSpeed: DetectionSpeed.noDuplicates,
        );
      } catch (_) {}
    }
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
                  border: Border.all(color: Colors.orange),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.auto_awesome, color: Colors.orange, size: 16),
                        SizedBox(width: 6),
                        Text(
                          'Amount > ₹2,000 Auto-Split',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Split into ${splits.length} sub-transactions under ₹2,000:',
                      style: const TextStyle(fontSize: 12),
                    ),
                    const SizedBox(height: 6),
                    Wrap(
                      spacing: 6,
                      runSpacing: 4,
                      children: splits.asMap().entries.map((e) {
                        return Chip(
                          visualDensity: VisualDensity.compact,
                          label: Text(
                            'T${e.key + 1}: ₹${e.value.toStringAsFixed(0)}',
                            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                          ),
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

  void _runSimultaneousPaymentSimulation(List<double> splits, double total) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => _SimultaneousPaymentDialog(
        splits: splits,
        totalAmount: total,
        onSuccess: () {
          setState(() {
            _allTranchesPaid = true;
            for (int i = 0; i < splits.length; i++) {
              _paidTranches.add(i);
            }
          });
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text('POS Collect & Pay'),
        elevation: 0,
        actions: [
          IconButton(
            tooltip: 'Soundbox Status',
            icon: const Icon(Icons.speaker_phone_rounded),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('PayFlow Smart Soundbox Online (Wi-Fi 5G & 4G SIM Connected)'),
                  backgroundColor: Colors.teal,
                ),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Top Mode Switcher (Pill Style)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            color: isDark ? const Color(0xFF141923) : Colors.grey.shade100,
            child: Row(
              children: [
                Expanded(
                  child: _ModeTabButton(
                    icon: Icons.receipt_long_rounded,
                    label: 'Receive POS Slip (QRs)',
                    isSelected: _activeTab == 0,
                    onTap: () => setState(() => _activeTab = 0),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _ModeTabButton(
                    icon: Icons.qr_code_scanner_rounded,
                    label: 'Scan & Pay (Camera)',
                    isSelected: _activeTab == 1,
                    onTap: () {
                      _initScannerIfNeeded();
                      setState(() => _activeTab = 1);
                    },
                  ),
                ),
              ],
            ),
          ),

          // Content area
          Expanded(
            child: _activeTab == 0
                ? _buildReceiveSlipView(context)
                : _buildCameraScannerView(context),
          ),
        ],
      ),
    );
  }

  // ══════════════════════════════════════════════════════════════════════════
  // TAB 1: RECEIVE POS SLIP (DISPLAYS MULTIPLE QRS FOR AMOUNTS > ₹2,000)
  // ══════════════════════════════════════════════════════════════════════════
  Widget _buildReceiveSlipView(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    final splits = _calculateSplits(_totalAmount);
    final isSplit = _totalAmount > 2000.0;

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // ── Quick Controls Card ──
          Card(
            elevation: 0,
            color: isDark ? const Color(0xFF161C28) : Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
              side: BorderSide(
                color: isDark ? const Color(0xFF2A3447) : Colors.grey.shade300,
              ),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Total Bill Amount',
                        style: tt.titleSmall?.copyWith(fontWeight: FontWeight.bold),
                      ),
                      if (isSplit)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.amber.withAlpha(35),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(color: Colors.orange.shade700),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Icon(Icons.call_split_rounded, size: 14, color: Colors.orange),
                              const SizedBox(width: 4),
                              Text(
                                '${splits.length} QRs Auto-Split',
                                style: TextStyle(
                                  color: Colors.orange.shade300,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 11,
                                ),
                              ),
                            ],
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 8),
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
                      labelText: 'Enter amount to collect',
                      hintText: 'e.g. 5000',
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    ),
                    onChanged: (_) {
                      setState(() {
                        _paidTranches.clear();
                        _allTranchesPaid = false;
                      });
                    },
                  ),
                  const SizedBox(height: 10),

                  // Quick Amount Chips
                  Wrap(
                    spacing: 8,
                    runSpacing: 6,
                    children: [500, 1500, 2500, 4000, 5000, 10000].map((amt) {
                      final hasSplit = amt > 2000;
                      return ActionChip(
                        avatar: hasSplit
                            ? const Icon(Icons.auto_awesome, size: 13, color: Colors.orange)
                            : null,
                        label: Text('₹$amt${hasSplit ? " (Split)" : ""}'),
                        onPressed: () {
                          _amountController.text = amt.toString();
                          setState(() {
                            _paidTranches.clear();
                            _allTranchesPaid = false;
                          });
                        },
                      );
                    }).toList(),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 14),

          // ── If Split > ₹2,000: Banner & Simultaneous Simulation Button ──
          if (isSplit) ...[
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF3B1E6D), Color(0xFF1F2B5B)],
                ),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: Colors.purpleAccent.withAlpha(150)),
              ),
              child: Column(
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.purpleAccent.withAlpha(60),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.bolt_rounded, color: Colors.purpleAccent, size: 22),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Payment > ₹2,000 broken into ${splits.length} QRs',
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 14,
                              ),
                            ),
                            const Text(
                              'Max ₹1,999 per QR for instant zero-fee NPCI settlement',
                              style: TextStyle(color: Colors.white70, fontSize: 11),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton.icon(
                      style: FilledButton.styleFrom(
                        backgroundColor: _allTranchesPaid ? Colors.green : Colors.purpleAccent,
                        foregroundColor: Colors.black,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      icon: Icon(_allTranchesPaid ? Icons.check_circle_rounded : Icons.flash_on_rounded),
                      label: Text(
                        _allTranchesPaid
                            ? 'All ${splits.length} Splits Paid & Cleared!'
                            : 'Simulate Payer Paying All ${splits.length} Splits Simultaneously',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      onPressed: () => _runSimultaneousPaymentSimulation(splits, _totalAmount),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
          ],

          // ── THE POS PAYMENT SLIP (RECEIPT STYLE) ──
          _buildThermalSlipReceipt(context, splits, isSplit),

          const SizedBox(height: 20),

          // Bottom Action Buttons
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              FilledButton.tonalIcon(
                icon: const Icon(Icons.volume_up_rounded),
                label: const Text('Soundbox Test'),
                onPressed: () {
                  final msg = isSplit
                      ? '🔊 PayFlow Soundbox: "${splits.length} split payments received simultaneously totaling ₹${_totalAmount.toStringAsFixed(0)} on UPI"'
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
              const SizedBox(width: 10),
              OutlinedButton.icon(
                icon: const Icon(Icons.share_rounded),
                label: const Text('Share Receipt Slip'),
                onPressed: () {
                  Clipboard.setData(
                    ClipboardData(
                      text: 'PayFlow POS Slip: Bill ₹${_totalAmount.toStringAsFixed(2)} broken into ${splits.length} QRs at Apex Electronics.',
                    ),
                  );
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('POS Slip summary copied to clipboard!')),
                  );
                },
              ),
            ],
          ),

          const SizedBox(height: 32),
        ],
      ),
    );
  }

  // ══════════════════════════════════════════════════════════════════════════
  // THERMAL POS BILLING SLIP COMPONENT (CONTAINS ALL SPLIT QRS)
  // ══════════════════════════════════════════════════════════════════════════
  Widget _buildThermalSlipReceipt(BuildContext context, List<double> splits, bool isSplit) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(50),
            blurRadius: 20,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Receipt Top Bar
          Container(
            padding: const EdgeInsets.symmetric(vertical: 8),
            decoration: const BoxDecoration(
              color: Color(0xFF1E293B),
              borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
            ),
            child: const Center(
              child: Text(
                '★ OFFICIAL MERCHANT POS RECEIPT SLIP ★',
                style: TextStyle(
                  color: Colors.white,
                  letterSpacing: 1.5,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),

          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            child: Column(
              children: [
                // Merchant Header
                const Text(
                  'APEX ELECTRONICS & RETAIL',
                  style: TextStyle(
                    color: Colors.black,
                    fontWeight: FontWeight.w900,
                    fontSize: 18,
                    letterSpacing: 0.5,
                  ),
                ),
                const SizedBox(height: 2),
                const Text(
                  'UPI ID: apex.electronics@payflow  •  Terminal: #01-BLR',
                  style: TextStyle(color: Colors.black54, fontSize: 11),
                ),
                const Text(
                  'GSTIN: 29AAAAA0000A1Z5  •  Token: PF-883492',
                  style: TextStyle(color: Colors.black45, fontSize: 10),
                ),

                const SizedBox(height: 12),
                // Perforated line
                _buildDottedSeparator(),
                const SizedBox(height: 12),

                // Bill Summary
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Invoice Total:', style: TextStyle(color: Colors.black87, fontSize: 14)),
                    Text(
                      '₹${_totalAmount.toStringAsFixed(2)}',
                      style: const TextStyle(
                        color: Colors.black,
                        fontWeight: FontWeight.w900,
                        fontSize: 20,
                      ),
                    ),
                  ],
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Payment Method:',
                      style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                    ),
                    Text(
                      isSplit ? 'Bharat UPI Smart Split (${splits.length} Tranches)' : 'Bharat UPI QR Code',
                      style: const TextStyle(
                        color: Colors.indigo,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 16),
                _buildDottedSeparator(),
                const SizedBox(height: 16),

                // ── MULTIPLE QR CODES IN SLIP ──
                if (!isSplit) ...[
                  // Single QR Code (<= ₹2000)
                  _buildSlipQrCard(
                    context: context,
                    trancheIndex: 0,
                    totalTranches: 1,
                    amount: _totalAmount,
                    isPaid: _paidTranches.contains(0) || _allTranchesPaid,
                  ),
                ] else ...[
                  // Multiple QRs in the Slip (> ₹2000)
                  Text(
                    'SCAN EACH QR BELOW TO PAY (ALL TRANCHES ≤ ₹1,999)',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.grey.shade800,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 1.0,
                      fontSize: 11,
                    ),
                  ),
                  const SizedBox(height: 12),

                  // Display EACH QR code in the slip sequentially
                  ...splits.asMap().entries.map((entry) {
                    final idx = entry.key;
                    final amt = entry.value;
                    final isPaid = _paidTranches.contains(idx) || _allTranchesPaid;

                    return Padding(
                      padding: const EdgeInsets.only(bottom: 16),
                      child: _buildSlipQrCard(
                        context: context,
                        trancheIndex: idx,
                        totalTranches: splits.length,
                        amount: amt,
                        isPaid: isPaid,
                      ),
                    );
                  }),
                ],

                const SizedBox(height: 8),
                _buildDottedSeparator(),
                const SizedBox(height: 12),

                // Slip Footer
                const Text(
                  'Powered by PayFlow • NPCI Compliant Smart Routing',
                  style: TextStyle(color: Colors.black45, fontSize: 10, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 4),
                const Text(
                  'Instant Zero-Fee Settlement • 100% Secure',
                  style: TextStyle(color: Colors.black38, fontSize: 9),
                ),
              ],
            ),
          ),

          // Jagged Sawtooth Receipt Bottom
          CustomPaint(
            size: const Size(double.infinity, 12),
            painter: _SawtoothReceiptBottomPainter(),
          ),
        ],
      ),
    );
  }

  // ══════════════════════════════════════════════════════════════════════════
  // INDIVIDUAL QR CARD IN SLIP
  // ══════════════════════════════════════════════════════════════════════════
  Widget _buildSlipQrCard({
    required BuildContext context,
    required int trancheIndex,
    required int totalTranches,
    required double amount,
    required bool isPaid,
  }) {
    final qrString = _buildQrString(
      amount,
      trancheIndex: totalTranches > 1 ? trancheIndex : null,
    );

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isPaid ? const Color(0xFFF0FDF4) : const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isPaid ? Colors.green.shade600 : Colors.grey.shade300,
          width: isPaid ? 2 : 1,
        ),
      ),
      child: Column(
        children: [
          // Header of this QR
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: isPaid ? Colors.green : const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  totalTranches > 1
                      ? 'TRANCHE ${trancheIndex + 1} OF $totalTranches'
                      : 'BHARAT UPI QR',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 11,
                    letterSpacing: 0.8,
                  ),
                ),
              ),
              Row(
                children: [
                  Text(
                    '₹${amount.toStringAsFixed(2)}',
                    style: TextStyle(
                      color: isPaid ? Colors.green.shade800 : Colors.black87,
                      fontWeight: FontWeight.w900,
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(width: 6),
                  if (isPaid)
                    const Icon(Icons.verified_rounded, color: Colors.green, size: 18)
                  else
                    const Icon(Icons.pending_actions_rounded, color: Colors.orange, size: 16),
                ],
              ),
            ],
          ),

          const SizedBox(height: 10),

          // The QR Code
          Stack(
            alignment: Alignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey.shade200),
                ),
                child: QrImageView(
                  data: qrString,
                  version: QrVersions.auto,
                  size: 170.0,
                  backgroundColor: Colors.white,
                ),
              ),
              if (isPaid)
                Container(
                  width: 170,
                  height: 170,
                  decoration: BoxDecoration(
                    color: Colors.white.withAlpha(220),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.check_circle_rounded, color: Colors.green, size: 48),
                      const SizedBox(height: 4),
                      const Text(
                        'PAID & SETTLED',
                        style: TextStyle(
                          color: Colors.green,
                          fontWeight: FontWeight.w900,
                          fontSize: 14,
                          letterSpacing: 1.0,
                        ),
                      ),
                      Text(
                        '₹${amount.toStringAsFixed(0)}',
                        style: const TextStyle(
                          color: Colors.green,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),

          const SizedBox(height: 8),

          // Quick actions for this specific tranche
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              TextButton.icon(
                style: TextButton.styleFrom(
                  visualDensity: VisualDensity.compact,
                  foregroundColor: Colors.indigo,
                ),
                icon: const Icon(Icons.volume_up_rounded, size: 14),
                label: Text('Soundbox Tranche ${trancheIndex + 1}'),
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(
                        '🔊 PayFlow Soundbox: "Tranche ${trancheIndex + 1} payment of ₹${amount.toStringAsFixed(0)} received on UPI"',
                      ),
                      backgroundColor: Colors.teal,
                      duration: const Duration(seconds: 2),
                    ),
                  );
                },
              ),
              const SizedBox(width: 8),
              TextButton.icon(
                style: TextButton.styleFrom(
                  visualDensity: VisualDensity.compact,
                  foregroundColor: Colors.black87,
                ),
                icon: const Icon(Icons.copy_rounded, size: 14),
                label: const Text('Copy Link'),
                onPressed: () {
                  Clipboard.setData(ClipboardData(text: qrString));
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('UPI Intent link for Tranche ${trancheIndex + 1} copied!')),
                  );
                },
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildDottedSeparator() {
    return Row(
      children: List.generate(
        40,
        (i) => Expanded(
          child: Container(
            color: i.isEven ? Colors.grey.shade400 : Colors.transparent,
            height: 1.5,
          ),
        ),
      ),
    );
  }

  // ══════════════════════════════════════════════════════════════════════════
  // TAB 2: CAMERA SCANNER (LAZILY INITIALIZED TO PREVENT CRASHES)
  // ══════════════════════════════════════════════════════════════════════════
  Widget _buildCameraScannerView(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;

    return Column(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          color: cs.surfaceContainerHighest.withAlpha(60),
          child: const Row(
            children: [
              Icon(Icons.camera_alt_outlined, size: 18),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Point camera at any UPI QR code. Amounts > ₹2,000 auto-split for simultaneous payment.',
                  style: TextStyle(fontSize: 12),
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
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.qr_code_scanner_rounded, size: 64, color: Colors.white54),
                          const SizedBox(height: 16),
                          Text(
                            'Camera QR Scanner',
                            style: tt.titleMedium?.copyWith(color: Colors.white),
                          ),
                          const SizedBox(height: 6),
                          const Text(
                            'Active on Vivo phone with instant auto-split detection',
                            style: TextStyle(color: Colors.white60, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),

              // Scanner overlay reticle
              Container(
                width: 250,
                height: 250,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.purpleAccent, width: 2.5),
                  borderRadius: BorderRadius.circular(16),
                ),
              ),

              // Simulated Test Buttons
              Positioned(
                bottom: 24,
                left: 16,
                right: 16,
                child: Column(
                  children: [
                    FilledButton.icon(
                      style: FilledButton.styleFrom(
                        backgroundColor: Colors.purpleAccent,
                        foregroundColor: Colors.black,
                      ),
                      icon: const Icon(Icons.bolt_rounded),
                      label: const Text('Simulate Scan: ₹5,000 (Split > ₹2k)'),
                      onPressed: () {
                        _showScannedDialog('upi://pay?pa=vendor@upi&pn=Retail%20Store&am=5000.00&cu=INR');
                      },
                    ),
                    const SizedBox(height: 8),
                    FilledButton.tonalIcon(
                      icon: const Icon(Icons.flash_on_rounded),
                      label: const Text('Simulate Scan: ₹10,000 (6 Splits)'),
                      onPressed: () {
                        _showScannedDialog('upi://pay?pa=wholesaler@upi&pn=Bulk%20Supplier&am=10000.00&cu=INR');
                      },
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

// ── Top Mode Switcher Button ──
class _ModeTabButton extends StatelessWidget {
  const _ModeTabButton({
    required this.icon,
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
        decoration: BoxDecoration(
          color: isSelected ? Colors.indigo : Colors.transparent,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: isSelected ? Colors.indigoAccent : Colors.grey.withAlpha(50),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 16,
              color: isSelected ? Colors.white : Colors.grey.shade400,
            ),
            const SizedBox(width: 6),
            Flexible(
              child: Text(
                label,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  color: isSelected ? Colors.white : Colors.grey.shade400,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                  fontSize: 12,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Custom Painter for Jagged Thermal Receipt Bottom ──
class _SawtoothReceiptBottomPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;

    final path = Path();
    path.moveTo(0, 0);

    const toothWidth = 14.0;
    final toothHeight = size.height;
    final teeth = (size.width / toothWidth).ceil();

    for (int i = 0; i < teeth; i++) {
      final x = i * toothWidth;
      path.lineTo(x + toothWidth / 2, toothHeight);
      path.lineTo(x + toothWidth, 0);
    }

    path.close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

// ── Simultaneous Parallel Payment Simulation Dialog ──
class _SimultaneousPaymentDialog extends StatefulWidget {
  const _SimultaneousPaymentDialog({
    required this.splits,
    required this.totalAmount,
    this.onSuccess,
  });

  final List<double> splits;
  final double totalAmount;
  final VoidCallback? onSuccess;

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
    _progresses = List.filled(widget.splits.length, 0.0);
    _isCompleted = List.filled(widget.splits.length, false);
    _startSimultaneousSimulation();
  }

  void _startSimultaneousSimulation() {
    for (int i = 0; i < widget.splits.length; i++) {
      final index = i;
      final stepDelay = 150 + (index * 80);
      Timer.periodic(Duration(milliseconds: stepDelay), (timer) {
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
      widget.onSuccess?.call();
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
          Expanded(
            child: Text(
              _allDone
                  ? 'All Payments Completed!'
                  : 'Processing ${widget.splits.length} Splits Simultaneously',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
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
                          'Tranche ${idx + 1}: ₹${amt.toStringAsFixed(2)}',
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
            label: const Text('Done / View Updated Slip'),
            onPressed: () {
              Navigator.of(context).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(
                    'Consolidated slip updated: All ${widget.splits.length} tranches marked PAID!',
                  ),
                  backgroundColor: Colors.green,
                ),
              );
            },
          ),
      ],
    );
  }
}
