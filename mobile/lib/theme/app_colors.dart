import 'package:flutter/material.dart';

/// PayFlow brand palette — Material 3 seed-based with explicit overrides.
/// Every screen should pull from Theme.of(context).colorScheme rather than
/// referencing these constants directly; they exist to build the ThemeData.
abstract final class AppColors {
  // ── Brand seeds ────────────────────────────────────────────────────────────
  static const Color brandIndigo = Color(0xFF4F46E5);   // primary
  static const Color brandViolet = Color(0xFF7C3AED);   // secondary
  static const Color brandCyan   = Color(0xFF06B6D4);   // tertiary / accent

  // ── Semantic ───────────────────────────────────────────────────────────────
  static const Color success  = Color(0xFF22C55E);
  static const Color warning  = Color(0xFFF59E0B);
  static const Color error    = Color(0xFFEF4444);
  static const Color info     = Color(0xFF3B82F6);

  // ── Neutral surface scale (light) ──────────────────────────────────────────
  static const Color surfaceLight      = Color(0xFFF8F9FE);
  static const Color surfaceCardLight  = Color(0xFFFFFFFF);
  static const Color outlineLight      = Color(0xFFE2E8F0);

  // ── Neutral surface scale (dark) ───────────────────────────────────────────
  static const Color surfaceDark       = Color(0xFF0F0E17);
  static const Color surfaceCardDark   = Color(0xFF1C1B2E);
  static const Color outlineDark       = Color(0xFF2D2B45);

  // ── Status chip colours ────────────────────────────────────────────────────
  static const Color chipSuccess        = Color(0xFFDCFCE7);
  static const Color chipSuccessText    = Color(0xFF15803D);
  static const Color chipPending        = Color(0xFFFEF3C7);
  static const Color chipPendingText    = Color(0xFFB45309);
  static const Color chipFailed         = Color(0xFFFEE2E2);
  static const Color chipFailedText     = Color(0xFFB91C1C);
  static const Color chipNeutral        = Color(0xFFF1F5F9);
  static const Color chipNeutralText    = Color(0xFF475569);

  // ── Dark equivalents for status chips ─────────────────────────────────────
  static const Color chipSuccessDark     = Color(0xFF14532D);
  static const Color chipSuccessTextDark = Color(0xFF86EFAC);
  static const Color chipPendingDark     = Color(0xFF78350F);
  static const Color chipPendingTextDark = Color(0xFFFDE68A);
  static const Color chipFailedDark      = Color(0xFF7F1D1D);
  static const Color chipFailedTextDark  = Color(0xFFFCA5A5);
}
