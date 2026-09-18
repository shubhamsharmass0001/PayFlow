/// Named spacing constants.
/// Usage: SizedBox(height: AppSpacing.md)
///        Padding(padding: EdgeInsets.all(AppSpacing.lg))
abstract final class AppSpacing {
  static const double xxs =  2.0;
  static const double xs  =  4.0;
  static const double sm  =  8.0;
  static const double md  = 16.0;
  static const double lg  = 24.0;
  static const double xl  = 32.0;
  static const double xxl = 48.0;
  static const double xxxl = 64.0;

  // Border radii
  static const double radiusSm  =  8.0;
  static const double radiusMd  = 12.0;
  static const double radiusLg  = 16.0;
  static const double radiusXl  = 24.0;
  static const double radiusFull = 999.0;

  // Icon sizes
  static const double iconSm  = 16.0;
  static const double iconMd  = 24.0;
  static const double iconLg  = 32.0;
  static const double iconXl  = 48.0;

  // Card elevation
  static const double elevationNone = 0;
  static const double elevationSm   = 1;
  static const double elevationMd   = 3;
  static const double elevationLg   = 6;
}
