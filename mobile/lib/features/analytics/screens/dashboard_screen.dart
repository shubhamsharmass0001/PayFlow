import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../../core/providers.dart';
import '../../../shared/widgets/paginated_list_view.dart';
import '../../../theme/theme.dart';
import '../analytics_providers.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final merchantId = ref.watch(activeMerchantIdProvider);
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;

    final overviewAsync = ref.watch(overviewStatsProvider(merchantId));
    final trendAsync = ref.watch(revenueTrendProvider(merchantId));
    final methodsAsync = ref.watch(paymentMethodsProvider(merchantId));

    final currencyFormatter = NumberFormat.currency(symbol: '₹', decimalDigits: 0);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            tooltip: 'Notifications',
            onPressed: () => context.go('/notifications'),
          ),
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Refresh',
            onPressed: () {
              ref.invalidate(overviewStatsProvider(merchantId));
              ref.invalidate(revenueTrendProvider(merchantId));
              ref.invalidate(paymentMethodsProvider(merchantId));
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(overviewStatsProvider(merchantId));
          ref.invalidate(revenueTrendProvider(merchantId));
          ref.invalidate(paymentMethodsProvider(merchantId));
        },
        child: ListView(
          padding: const EdgeInsets.all(AppSpacing.md),
          children: [
            // Quick action shortcuts
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    style: FilledButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: AppSpacing.md),
                    ),
                    onPressed: () => context.go('/invoices/create'),
                    icon: const Icon(Icons.add_rounded),
                    label: const Text('New Invoice'),
                  ),
                ),
                const SizedBox(width: AppSpacing.md),
                Expanded(
                  child: OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: AppSpacing.md),
                    ),
                    onPressed: () => context.go('/collect'),
                    icon: const Icon(Icons.qr_code_rounded),
                    label: const Text('Collect'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: AppSpacing.lg),

            // ── KPI Section ──────────────────────────────────────────────────
            overviewAsync.when(
              loading: () => const Center(
                child: Padding(
                  padding: EdgeInsets.all(AppSpacing.xl),
                  child: CircularProgressIndicator(),
                ),
              ),
              error: (err, _) => Card(
                color: cs.errorContainer.withAlpha(50),
                child: Padding(
                  padding: const EdgeInsets.all(AppSpacing.md),
                  child: Text('Could not load KPIs: $err', style: TextStyle(color: cs.error)),
                ),
              ),
              data: (stats) => Column(
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: KpiCard(
                          label: 'Collections',
                          value: currencyFormatter.format(stats.totalCollections),
                          icon: Icons.currency_rupee_rounded,
                          iconColor: Colors.green,
                          subtitle: stats.period,
                        ),
                      ),
                      const SizedBox(width: AppSpacing.sm),
                      Expanded(
                        child: KpiCard(
                          label: 'Success Rate',
                          value: '${(stats.successRate > 1.0 ? stats.successRate : stats.successRate * 100).toStringAsFixed(1)}%',
                          icon: Icons.check_circle_outline_rounded,
                          iconColor: Colors.teal,
                          subtitle: '${stats.totalTransactions} txns',
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: AppSpacing.sm),
                  Row(
                    children: [
                      Expanded(
                        child: KpiCard(
                          label: 'Pending Invoices',
                          value: stats.pendingCount.toString(),
                          icon: Icons.schedule_rounded,
                          iconColor: Colors.amber,
                          onTap: () => context.go('/invoices'),
                        ),
                      ),
                      const SizedBox(width: AppSpacing.sm),
                      Expanded(
                        child: KpiCard(
                          label: 'Avg Ticket',
                          value: currencyFormatter.format(stats.avgTransactionValue),
                          icon: Icons.analytics_outlined,
                          iconColor: Colors.indigo,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: AppSpacing.xl),

            // ── Revenue Trend Chart ──────────────────────────────────────────
            Text('Revenue Trend', style: tt.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: AppSpacing.xs),
            Text(
              'Historical volume over time',
              style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant),
            ),
            const SizedBox(height: AppSpacing.md),
            Card(
              elevation: 0,
              shape: RoundedRectangleBorder(
                side: BorderSide(color: cs.outlineVariant.withAlpha(100)),
                borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
              ),
              child: Padding(
                padding: const EdgeInsets.all(AppSpacing.lg),
                child: SizedBox(
                  height: 220,
                  child: trendAsync.when(
                    loading: () => const Center(child: CircularProgressIndicator()),
                    error: (err, _) => Center(child: Text('Chart error: $err')),
                    data: (trend) {
                      if (trend.points.isEmpty) {
                        return const Center(child: Text('No trend data available'));
                      }
                      final spots = trend.points.asMap().entries.map((e) {
                        return FlSpot(e.key.toDouble(), e.value.amount);
                      }).toList();

                      final maxY = spots.map((s) => s.y).reduce((a, b) => a > b ? a : b);

                      return LineChart(
                        LineChartData(
                          gridData: FlGridData(
                            show: true,
                            drawVerticalLine: false,
                            getDrawingHorizontalLine: (v) => FlLine(
                              color: cs.outlineVariant.withAlpha(60),
                              strokeWidth: 1,
                            ),
                          ),
                          titlesData: FlTitlesData(
                            leftTitles: const AxisTitles(
                              sideTitles: SideTitles(showTitles: false),
                            ),
                            topTitles: const AxisTitles(
                              sideTitles: SideTitles(showTitles: false),
                            ),
                            rightTitles: const AxisTitles(
                              sideTitles: SideTitles(showTitles: false),
                            ),
                            bottomTitles: AxisTitles(
                              sideTitles: SideTitles(
                                showTitles: true,
                                reservedSize: 28,
                                interval: (spots.length / 4).ceilToDouble().clamp(1.0, 10.0),
                                getTitlesWidget: (val, meta) {
                                  final idx = val.toInt();
                                  if (idx >= 0 && idx < trend.points.length) {
                                    final rawDate = trend.points[idx].date;
                                    final label = rawDate.length > 5 ? rawDate.substring(5) : rawDate;
                                    return Padding(
                                      padding: const EdgeInsets.only(top: 6),
                                      child: Text(
                                        label,
                                        style: TextStyle(fontSize: 10, color: cs.onSurfaceVariant),
                                      ),
                                    );
                                  }
                                  return const SizedBox.shrink();
                                },
                              ),
                            ),
                          ),
                          borderData: FlBorderData(show: false),
                          minX: 0,
                          maxX: (trend.points.length - 1).toDouble().clamp(0.0, 100.0),
                          minY: 0,
                          maxY: (maxY * 1.2).clamp(1000.0, 10000000.0),
                          lineBarsData: [
                            LineChartBarData(
                              spots: spots,
                              isCurved: true,
                              color: cs.primary,
                              barWidth: 3,
                              isStrokeCapRound: true,
                              dotData: const FlDotData(show: false),
                              belowBarData: BarAreaData(
                                show: true,
                                color: cs.primary.withAlpha(35),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
              ),
            ),
            const SizedBox(height: AppSpacing.xl),

            // ── Payment Methods Breakdown ────────────────────────────────────
            Text('Payment Methods', style: tt.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: AppSpacing.xs),
            Text(
              'Distribution across UPI, Card, Net Banking',
              style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant),
            ),
            const SizedBox(height: AppSpacing.md),
            Card(
              elevation: 0,
              shape: RoundedRectangleBorder(
                side: BorderSide(color: cs.outlineVariant.withAlpha(100)),
                borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
              ),
              child: Padding(
                padding: const EdgeInsets.all(AppSpacing.lg),
                child: methodsAsync.when(
                  loading: () => const SizedBox(height: 120, child: Center(child: CircularProgressIndicator())),
                  error: (err, _) => Text('Could not load breakdown: $err'),
                  data: (methods) {
                    if (methods.isEmpty) {
                      return const Padding(
                        padding: EdgeInsets.all(AppSpacing.lg),
                        child: Center(child: Text('No payment methods recorded yet')),
                      );
                    }
                    final totalAmount = methods.fold<double>(0, (sum, m) => sum + m.amount);

                    return Column(
                      children: methods.map((m) {
                        final pct = totalAmount > 0 ? (m.amount / totalAmount) : 0.0;
                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: AppSpacing.xs),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(
                                    m.method.toUpperCase(),
                                    style: tt.bodyMedium?.copyWith(fontWeight: FontWeight.w600),
                                  ),
                                  Text(
                                    '${currencyFormatter.format(m.amount)} (${(pct * 100).toStringAsFixed(0)}%)',
                                    style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 6),
                              LinearProgressIndicator(
                                value: pct,
                                borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                                minHeight: 8,
                                backgroundColor: cs.primaryContainer.withAlpha(60),
                              ),
                            ],
                          ),
                        );
                      }).toList(),
                    );
                  },
                ),
              ),
            ),
            const SizedBox(height: AppSpacing.xxl),
          ],
        ),
      ),
    );
  }
}
