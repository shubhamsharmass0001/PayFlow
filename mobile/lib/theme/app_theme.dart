import 'package:flutter/material.dart';
import 'app_colors.dart';
import 'app_spacing.dart';

abstract final class AppTheme {
  // ── Light ──────────────────────────────────────────────────────────────────
  static ThemeData light() {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: AppColors.brandIndigo,
      brightness: Brightness.light,
      primary: AppColors.brandIndigo,
      secondary: AppColors.brandViolet,
      tertiary: AppColors.brandCyan,
      surface: AppColors.surfaceLight,
      error: AppColors.error,
    );
    return _base(colorScheme);
  }

  // ── Dark ───────────────────────────────────────────────────────────────────
  static ThemeData dark() {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: AppColors.brandIndigo,
      brightness: Brightness.dark,
      primary: const Color(0xFF818CF8),      // indigo-400 — readable on dark
      secondary: const Color(0xFFA78BFA),    // violet-400
      tertiary: AppColors.brandCyan,
      surface: AppColors.surfaceDark,
      error: AppColors.error,
    );
    return _base(colorScheme);
  }

  static ThemeData _base(ColorScheme cs) {
    final textTheme = _buildTextTheme(cs);

    return ThemeData(
      useMaterial3: true,
      colorScheme: cs,
      textTheme: textTheme,

      // ── AppBar ─────────────────────────────────────────────────────────────
      appBarTheme: AppBarTheme(
        elevation: 0,
        scrolledUnderElevation: 1,
        centerTitle: false,
        backgroundColor: cs.surface,
        foregroundColor: cs.onSurface,
        titleTextStyle: textTheme.titleLarge?.copyWith(
          fontWeight: FontWeight.w700,
          color: cs.onSurface,
        ),
      ),

      // ── Cards ──────────────────────────────────────────────────────────────
      cardTheme: CardThemeData(
        elevation: AppSpacing.elevationSm,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
        ),
        color: cs.brightness == Brightness.dark
            ? AppColors.surfaceCardDark
            : AppColors.surfaceCardLight,
        clipBehavior: Clip.antiAlias,
      ),

      // ── Inputs ─────────────────────────────────────────────────────────────
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: cs.brightness == Brightness.dark
            ? AppColors.surfaceCardDark
            : const Color(0xFFF1F5F9),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.md,
          vertical: AppSpacing.md,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
          borderSide: BorderSide(
            color: cs.brightness == Brightness.dark
                ? AppColors.outlineDark
                : AppColors.outlineLight,
          ),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
          borderSide: BorderSide(
            color: cs.brightness == Brightness.dark
                ? AppColors.outlineDark
                : AppColors.outlineLight,
          ),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
          borderSide: BorderSide(color: cs.primary, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
          borderSide: BorderSide(color: cs.error),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
          borderSide: BorderSide(color: cs.error, width: 2),
        ),
        labelStyle: TextStyle(color: cs.onSurfaceVariant),
        hintStyle: TextStyle(
          color: cs.onSurfaceVariant.withAlpha(153),
          fontSize: 14,
        ),
      ),

      // ── Elevated button ────────────────────────────────────────────────────
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: cs.primary,
          foregroundColor: cs.onPrimary,
          minimumSize: const Size(double.infinity, 52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
          ),
          textStyle: textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w600),
          elevation: 0,
        ),
      ),

      // ── Outlined button ────────────────────────────────────────────────────
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: cs.primary,
          minimumSize: const Size(double.infinity, 52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
          ),
          side: BorderSide(color: cs.primary),
          textStyle: textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w600),
        ),
      ),

      // ── Text button ────────────────────────────────────────────────────────
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: cs.primary,
          textStyle: textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w600),
        ),
      ),

      // ── Drawer ─────────────────────────────────────────────────────────────
      drawerTheme: DrawerThemeData(
        backgroundColor: cs.brightness == Brightness.dark
            ? AppColors.surfaceCardDark
            : AppColors.surfaceCardLight,
        elevation: AppSpacing.elevationLg,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.only(
            topRight: Radius.circular(AppSpacing.radiusXl),
            bottomRight: Radius.circular(AppSpacing.radiusXl),
          ),
        ),
      ),

      // ── BottomNavBar ───────────────────────────────────────────────────────
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: cs.brightness == Brightness.dark
            ? AppColors.surfaceCardDark
            : AppColors.surfaceCardLight,
        indicatorColor: cs.primaryContainer,
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          final selected = states.contains(WidgetState.selected);
          return TextStyle(
            fontSize: 11,
            fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
            color: selected ? cs.primary : cs.onSurfaceVariant,
          );
        }),
        elevation: AppSpacing.elevationMd,
      ),

      // ── Chips ──────────────────────────────────────────────────────────────
      chipTheme: ChipThemeData(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
        ),
        labelStyle: textTheme.labelSmall,
      ),

      // ── Divider ────────────────────────────────────────────────────────────
      dividerTheme: DividerThemeData(
        color: cs.brightness == Brightness.dark
            ? AppColors.outlineDark
            : AppColors.outlineLight,
        thickness: 1,
        space: 1,
      ),

      // ── SnackBar ───────────────────────────────────────────────────────────
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
        ),
      ),
    );
  }

  static TextTheme _buildTextTheme(ColorScheme cs) {
    // Using system font stack — avoids google_fonts network dependency.
    // Swap fontFamily to 'Inter' here once google_fonts is added.
    const fontFamily = null;
    final onSurface = cs.onSurface;
    final onSurfaceVariant = cs.onSurfaceVariant;

    return TextTheme(
      displayLarge: TextStyle(
        fontFamily: fontFamily, fontSize: 57, fontWeight: FontWeight.w400,
        color: onSurface, letterSpacing: -0.25,
      ),
      displayMedium: TextStyle(
        fontFamily: fontFamily, fontSize: 45, fontWeight: FontWeight.w400,
        color: onSurface,
      ),
      displaySmall: TextStyle(
        fontFamily: fontFamily, fontSize: 36, fontWeight: FontWeight.w400,
        color: onSurface,
      ),
      headlineLarge: TextStyle(
        fontFamily: fontFamily, fontSize: 32, fontWeight: FontWeight.w700,
        color: onSurface,
      ),
      headlineMedium: TextStyle(
        fontFamily: fontFamily, fontSize: 28, fontWeight: FontWeight.w700,
        color: onSurface,
      ),
      headlineSmall: TextStyle(
        fontFamily: fontFamily, fontSize: 24, fontWeight: FontWeight.w600,
        color: onSurface,
      ),
      titleLarge: TextStyle(
        fontFamily: fontFamily, fontSize: 22, fontWeight: FontWeight.w600,
        color: onSurface,
      ),
      titleMedium: TextStyle(
        fontFamily: fontFamily, fontSize: 16, fontWeight: FontWeight.w600,
        color: onSurface, letterSpacing: 0.15,
      ),
      titleSmall: TextStyle(
        fontFamily: fontFamily, fontSize: 14, fontWeight: FontWeight.w500,
        color: onSurface, letterSpacing: 0.1,
      ),
      bodyLarge: TextStyle(
        fontFamily: fontFamily, fontSize: 16, fontWeight: FontWeight.w400,
        color: onSurface, letterSpacing: 0.5,
      ),
      bodyMedium: TextStyle(
        fontFamily: fontFamily, fontSize: 14, fontWeight: FontWeight.w400,
        color: onSurface, letterSpacing: 0.25,
      ),
      bodySmall: TextStyle(
        fontFamily: fontFamily, fontSize: 12, fontWeight: FontWeight.w400,
        color: onSurfaceVariant, letterSpacing: 0.4,
      ),
      labelLarge: TextStyle(
        fontFamily: fontFamily, fontSize: 14, fontWeight: FontWeight.w600,
        color: onSurface, letterSpacing: 0.1,
      ),
      labelMedium: TextStyle(
        fontFamily: fontFamily, fontSize: 12, fontWeight: FontWeight.w500,
        color: onSurfaceVariant, letterSpacing: 0.5,
      ),
      labelSmall: TextStyle(
        fontFamily: fontFamily, fontSize: 11, fontWeight: FontWeight.w500,
        color: onSurfaceVariant, letterSpacing: 0.5,
      ),
    );
  }
}
