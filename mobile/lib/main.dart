import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'theme/theme.dart';
import 'routing/app_router.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    const ProviderScope(
      child: PayFlowApp(),
    ),
  );
}

class PayFlowApp extends ConsumerWidget {
  const PayFlowApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Router is a Riverpod provider — its RouterNotifier watches authState
    // and calls notifyListeners() on every auth status change, causing
    // go_router to re-evaluate the redirect callback automatically.
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'PayFlow',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      darkTheme: AppTheme.dark(),
      themeMode: ThemeMode.system,
      routerConfig: router,
    );
  }
}
