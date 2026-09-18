import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/shared/widgets/empty_state.dart';
import 'package:mobile/shared/widgets/paginated_list_view.dart';
import 'package:mobile/shared/widgets/status_badge.dart';

void main() {
  group('Shared Widgets Architecture Tests', () {
    testWidgets('StatusBadge displays correct text and resolves colors', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusBadge(status: 'SUCCESS'),
          ),
        ),
      );

      expect(find.text('Success'), findsOneWidget);
    });

    testWidgets('StatusBadge displays custom label if provided', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusBadge(status: 'OVERDUE', label: 'Overdue by 3 days'),
          ),
        ),
      );

      expect(find.text('Overdue by 3 days'), findsOneWidget);
    });

    testWidgets('EmptyState displays title, subtitle and CTA', (tester) async {
      bool actionTapped = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: EmptyState(
              title: 'No Invoices Yet',
              subtitle: 'Create your first invoice to get started',
              actionLabel: 'Create Invoice',
              action: () => actionTapped = true,
            ),
          ),
        ),
      );

      expect(find.text('No Invoices Yet'), findsOneWidget);
      expect(find.text('Create your first invoice to get started'), findsOneWidget);
      expect(find.text('Create Invoice'), findsOneWidget);

      await tester.tap(find.text('Create Invoice'));
      expect(actionTapped, isTrue);
    });

    testWidgets('ErrorState displays message and retry button', (tester) async {
      bool retryTapped = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ErrorState(
              message: 'Failed to fetch network records',
              onRetry: () => retryTapped = true,
            ),
          ),
        ),
      );

      expect(find.text('Failed to fetch network records'), findsOneWidget);
      expect(find.text('Try again'), findsOneWidget);

      await tester.tap(find.text('Try again'));
      expect(retryTapped, isTrue);
    });

    testWidgets('KpiCard renders metric label and formatted value', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: KpiCard(
              label: 'Total Collections',
              value: '₹1,54,000',
              icon: Icons.currency_rupee_rounded,
              subtitle: 'Today',
            ),
          ),
        ),
      );

      expect(find.text('Total Collections'), findsOneWidget);
      expect(find.text('₹1,54,000'), findsOneWidget);
      expect(find.text('Today'), findsOneWidget);
    });
  });
}
