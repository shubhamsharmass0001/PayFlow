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
  final TextEditingController _amountController = TextEditingController(text: '500');
  final TextEditingController _noteController = TextEditingController(text: 'Store Sale');

  String _generatedQr = '';
  MobileScannerController? _scannerController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _generateDefaultQr();
    if (!kIsWeb) {
      _scannerController = MobileScannerController(
        detectionSpeed: DetectionSpeed.noDuplicates,
      );
    }
  }

  void _generateDefaultQr() {
    final merchantId = ref.read(activeMerchantIdProvider);
    final amt = double.tryParse(_amountController.text) ?? 500.0;
    setState(() {
      _generatedQr =
          'upi://pay?pa=apex.electronics@payflow&pn=Apex%20Electronics&am=${amt.toStringAsFixed(2)}&cu=INR&tn=${Uri.encodeComponent(_noteController.text)}&mc=5732&tr=MCH-$merchantId-${DateTime.now().millisecondsSinceEpoch}';
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _amountController.dispose();
    _noteController.dispose();
    _scannerController?.dispose();
    super.dispose();
  }

  void _onBarcodeDetected(BarcodeCapture capture) {
    final barcode = capture.barcodes.firstOrNull;
    if (barcode?.rawValue != null && barcode!.rawValue!.isNotEmpty) {
      _showScannedDialog(barcode.rawValue!);
    }
  }

  void _showScannedDialog(String raw) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.check_circle_rounded, color: Colors.green),
            SizedBox(width: 8),
            Text('QR Code Detected'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Scanned Payload:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.grey.withAlpha(40),
                borderRadius: BorderRadius.circular(8),
              ),
              child: SelectableText(
                raw,
                style: const TextStyle(fontFamily: 'monospace', fontSize: 13),
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
            icon: const Icon(Icons.send_rounded),
            label: const Text('Send / Process Payment'),
            onPressed: () {
              Navigator.of(ctx).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Payment simulated successfully!'),
                  backgroundColor: Colors.green,
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;

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
                          'Point-of-Sale (POS) Amount',
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
                            labelText: 'Enter amount to collect',
                          ),
                          onChanged: (_) => _generateDefaultQr(),
                        ),
                        const SizedBox(height: AppSpacing.sm),
                        // Quick amount chips
                        Wrap(
                          spacing: 8,
                          children: [100, 250, 500, 1000, 2500].map((amt) {
                            return ActionChip(
                              label: Text('₹$amt'),
                              onPressed: () {
                                _amountController.text = amt.toString();
                                _generateDefaultQr();
                              },
                            );
                          }).toList(),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: AppSpacing.lg),

                // Dynamic QR Display
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
                        data: _generatedQr.isNotEmpty
                            ? _generatedQr
                            : 'upi://pay?pa=apex.electronics@payflow&pn=Apex%20Electronics',
                        version: QrVersions.auto,
                        size: 220.0,
                        backgroundColor: Colors.white,
                      ),
                      const SizedBox(height: AppSpacing.sm),
                      const Text(
                        'BHARAT UPI QR',
                        style: TextStyle(
                          color: Colors.black87,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 2.0,
                          fontSize: 12,
                        ),
                      ),
                      const Text(
                        'Scan with Google Pay, PhonePe, or Paytm',
                        style: TextStyle(color: Colors.black54, fontSize: 11),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: AppSpacing.md),

                // Soundbox Simulation & Share
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    FilledButton.tonalIcon(
                      icon: const Icon(Icons.volume_up_rounded),
                      label: const Text('Soundbox Test'),
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('🔊 PayFlow Soundbox: "₹${_amountController.text} received successfully on UPI"'),
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
                        Clipboard.setData(ClipboardData(text: _generatedQr));
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
                color: cs.surfaceContainerHighest.withOpacity(0.3),
                child: Row(
                  children: [
                    const Icon(Icons.info_outline, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Align the camera with any UPI QR code or invoice barcode to send money or process payment.',
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
                              const Icon(Icons.camera_alt_outlined, size: 64, color: Colors.white54),
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
                                icon: const Icon(Icons.qr_code_scanner_rounded),
                                label: const Text('Simulate Scan Sample UPI QR'),
                                onPressed: () {
                                  _showScannedDialog(
                                    'upi://pay?pa=merchant.vendor@upi&pn=Supplier&am=1250.00&cu=INR&tn=Invoice-PO-9841',
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

                    // Scanner action controls (torch, switch camera)
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
                            tooltip: 'Test Sample QR',
                            onPressed: () {
                              _showScannedDialog(
                                'upi://pay?pa=merchant.vendor@upi&pn=Supplier&am=1250.00&cu=INR&tn=Invoice-PO-9841',
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
