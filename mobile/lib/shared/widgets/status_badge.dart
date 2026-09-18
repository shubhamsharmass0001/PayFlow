import 'package:flutter/material.dart';
import '../../theme/theme.dart';

/// Central status → colour resolver.
/// Used by StatusBadge and any other widget that needs status colour.
abstract final class StatusColors {
  static StatusColorConfig resolve(String status) {
    switch (status.toUpperCase()) {
      // ── Success family ───────────────────────────────────────────────
      case 'SUCCESS':
      case 'PAID':
      case 'APPROVED':
      case 'SETTLED':
      case 'VERIFIED':
      case 'MATCHED':
      case 'COMPLETED':
      case 'REFUNDED':
        return const StatusColorConfig(
          bg: Color(0xFFDCFCE7),
          fg: Color(0xFF15803D),
          darkBg: Color(0xFF14532D),
          darkFg: Color(0xFF86EFAC),
        );

      // ── Warning / pending family ─────────────────────────────────────
      case 'PENDING':
      case 'PROCESSING':
      case 'INITIATED':
      case 'UNDER_REVIEW':
      case 'PARTIALLY_PAID':
      case 'REFUND_PENDING':
      case 'REFUND_INITIATED':
      case 'ACTIVE':
        return const StatusColorConfig(
          bg: Color(0xFFFEF3C7),
          fg: Color(0xFFB45309),
          darkBg: Color(0xFF78350F),
          darkFg: Color(0xFFFDE68A),
        );

      // ── Error / danger family ────────────────────────────────────────
      case 'FAILED':
      case 'REJECTED':
      case 'REFUND_FAILED':
      case 'OVERDUE':
      case 'DUPLICATE':
      case 'DEFAULTED':
      case 'CRITICAL':
      case 'HIGH':
      case 'PROHIBITED':
        return const StatusColorConfig(
          bg: Color(0xFFFEE2E2),
          fg: Color(0xFFB91C1C),
          darkBg: Color(0xFF7F1D1D),
          darkFg: Color(0xFFFCA5A5),
        );

      // ── Neutral / info family ────────────────────────────────────────
      case 'DRAFT':
      case 'SENT':
      case 'ISSUED':
      case 'CREATED':
      case 'TIMEOUT':
      case 'MEDIUM':
      case 'SUSPECTED':
        return const StatusColorConfig(
          bg: Color(0xFFE0E7FF),
          fg: Color(0xFF3730A3),
          darkBg: Color(0xFF1E1B4B),
          darkFg: Color(0xFFA5B4FC),
        );

      // ── Neutral grey ─────────────────────────────────────────────────
      default:
        return const StatusColorConfig(
          bg: Color(0xFFF1F5F9),
          fg: Color(0xFF475569),
          darkBg: Color(0xFF1E293B),
          darkFg: Color(0xFF94A3B8),
        );
    }
  }
}

class StatusColorConfig {
  const StatusColorConfig({
    required this.bg,
    required this.fg,
    required this.darkBg,
    required this.darkFg,
  });
  final Color bg, fg, darkBg, darkFg;
}

// ── StatusBadge widget ─────────────────────────────────────────────────────────

class StatusBadge extends StatelessWidget {
  const StatusBadge({
    super.key,
    required this.status,
    this.label,
    this.small = false,
  });

  /// The raw status string (e.g. 'SUCCESS', 'OVERDUE'). Resolved to colour
  /// via [StatusColors.resolve]. Pass a human-readable [label] to override
  /// what's displayed in the chip without changing colour logic.
  final String status;
  final String? label;

  /// Small variant — used in list tiles where space is tight.
  final bool small;

  static String _humanise(String s) {
    return s
        .replaceAll('_', ' ')
        .split(' ')
        .map((w) => w.isEmpty ? '' : '${w[0].toUpperCase()}${w.substring(1).toLowerCase()}')
        .join(' ');
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final c      = StatusColors.resolve(status);

    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: small ? AppSpacing.xs : AppSpacing.sm,
        vertical:   small ? 2 : AppSpacing.xs,
      ),
      decoration: BoxDecoration(
        color: isDark ? c.darkBg : c.bg,
        borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
      ),
      child: Text(
        label ?? _humanise(status),
        style: TextStyle(
          color: isDark ? c.darkFg : c.fg,
          fontSize: small ? 10 : 12,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.3,
        ),
      ),
    );
  }
}
