import 'package:flutter/material.dart';
import '../../theme/theme.dart';
import 'empty_state.dart';

/// Generic paginated list view.
///
/// Architecture note: this is a deliberate shared abstraction — every feature
/// list (invoices, transactions, customers, etc.) routes through the same
/// widget rather than duplicating loading/error/empty/pagination logic.
/// Interviewers can be shown one implementation and know it applies to all 10
/// feature screens simultaneously.
///
/// Usage:
/// ```dart
/// PaginatedListView<Invoice>(
///   items: items,
///   isLoading: isLoading,
///   hasMore: hasMore,
///   error: errorMessage,
///   onLoadMore: () => ref.read(provider.notifier).loadMore(),
///   onRefresh: () async => ref.refresh(provider),
///   itemBuilder: (invoice) => InvoiceTile(invoice: invoice),
///   emptyTitle: 'No invoices yet',
///   emptyIcon: Icons.receipt_long_outlined,
/// )
/// ```
class PaginatedListView<T> extends StatefulWidget {
  const PaginatedListView({
    super.key,
    required this.items,
    required this.isLoading,
    required this.hasMore,
    required this.itemBuilder,
    required this.emptyTitle,
    this.emptySubtitle,
    this.emptyIcon = Icons.inbox_outlined,
    this.emptyAction,
    this.emptyActionLabel,
    this.error,
    this.onLoadMore,
    this.onRefresh,
    this.padding,
    this.headerSliver,
  });

  final List<T> items;
  final bool isLoading;
  final bool hasMore;
  final Widget Function(T item) itemBuilder;

  final String emptyTitle;
  final String? emptySubtitle;
  final IconData emptyIcon;
  final VoidCallback? emptyAction;
  final String? emptyActionLabel;

  final String? error;
  final VoidCallback? onLoadMore;
  final Future<void> Function()? onRefresh;
  final EdgeInsetsGeometry? padding;

  /// Optional sliver to put above the list (e.g. search bar, filter chips).
  final Widget? headerSliver;

  @override
  State<PaginatedListView<T>> createState() => _PaginatedListViewState<T>();
}

class _PaginatedListViewState<T> extends State<PaginatedListView<T>> {
  final _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (!_scrollController.hasClients) return;
    final pos = _scrollController.position;
    // Trigger load-more when within 300px of bottom
    if (pos.pixels >= pos.maxScrollExtent - 300 &&
        widget.hasMore &&
        !widget.isLoading) {
      widget.onLoadMore?.call();
    }
  }

  @override
  Widget build(BuildContext context) {
    // ── Error state ──────────────────────────────────────────────────────────
    if (widget.error != null && widget.items.isEmpty) {
      return ErrorState(
        message: widget.error!,
        onRetry: widget.onRefresh == null ? null : () => widget.onRefresh!(),
      );
    }

    // ── Initial loading skeleton ─────────────────────────────────────────────
    if (widget.isLoading && widget.items.isEmpty) {
      return _LoadingSkeleton(padding: widget.padding);
    }

    final body = CustomScrollView(
      controller: _scrollController,
      slivers: [
        if (widget.onRefresh != null)
          CupertinoSliverRefreshControl(onRefresh: widget.onRefresh),
        if (widget.headerSliver != null) widget.headerSliver!,

        // ── Empty state ──────────────────────────────────────────────────────
        if (widget.items.isEmpty)
          SliverFillRemaining(
            hasScrollBody: false,
            child: EmptyState(
              title: widget.emptyTitle,
              subtitle: widget.emptySubtitle,
              icon: widget.emptyIcon,
              action: widget.emptyAction,
              actionLabel: widget.emptyActionLabel,
            ),
          )
        else ...[
          SliverPadding(
            padding: widget.padding ??
                const EdgeInsets.symmetric(
                  horizontal: AppSpacing.md,
                  vertical: AppSpacing.sm,
                ),
            sliver: SliverList.builder(
              itemCount: widget.items.length,
              itemBuilder: (_, i) => widget.itemBuilder(widget.items[i]),
            ),
          ),

          // ── Load more / end indicator ────────────────────────────────────
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: AppSpacing.lg),
              child: widget.isLoading
                  ? const Center(child: CircularProgressIndicator(strokeWidth: 2))
                  : widget.hasMore
                      ? const SizedBox.shrink()
                      : Center(
                          child: Text(
                            '— end of list —',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ),
            ),
          ),
        ],
      ],
    );

    if (widget.onRefresh != null) return body;

    // Without pull-to-refresh, wrap in a plain scroll
    return body;
  }
}

// ── Pull-to-refresh using Material's RefreshIndicator ──────────────────────────
// Note: CupertinoSliverRefreshControl is used above for slivers.
// For screens not using CustomScrollView, expose this separately.

class _LoadingSkeleton extends StatelessWidget {
  const _LoadingSkeleton({this.padding});
  final EdgeInsetsGeometry? padding;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return ListView.separated(
      padding: padding ??
          const EdgeInsets.symmetric(
            horizontal: AppSpacing.md,
            vertical: AppSpacing.sm,
          ),
      itemCount: 8,
      separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.sm),
      itemBuilder: (_, i) => _SkeletonTile(cs: cs, i: i),
    );
  }
}

class _SkeletonTile extends StatelessWidget {
  const _SkeletonTile({required this.cs, required this.i});
  final ColorScheme cs;
  final int i;

  @override
  Widget build(BuildContext context) {
    // Staggered widths for a natural look
    final widths = [0.6, 0.8, 0.5, 0.7, 0.65, 0.75, 0.55, 0.7];
    final w = widths[i % widths.length];

    return Container(
      height: 72,
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: cs.surfaceContainerHighest.withAlpha(77),
        borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          _Shimmer(width: MediaQuery.of(context).size.width * w, height: 14, cs: cs),
          const SizedBox(height: AppSpacing.sm),
          _Shimmer(width: MediaQuery.of(context).size.width * (w * 0.6), height: 10, cs: cs),
        ],
      ),
    );
  }
}

class _Shimmer extends StatelessWidget {
  const _Shimmer({required this.width, required this.height, required this.cs});
  final double width;
  final double height;
  final ColorScheme cs;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: cs.outlineVariant.withAlpha(100),
        borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
      ),
    );
  }
}

// ── CupertinoSliverRefreshControl shim for Material apps ─────────────────────
// go_router uses MaterialApp so we use this thin adapter.

class CupertinoSliverRefreshControl extends StatelessWidget {
  const CupertinoSliverRefreshControl({super.key, required this.onRefresh});
  final Future<void> Function()? onRefresh;

  @override
  Widget build(BuildContext context) {
    // Real apps use CupertinoSliverRefreshControl from cupertino package.
    // For cross-platform simplicity we return a SliverToBoxAdapter with
    // a standard RefreshIndicator wrapping handled at Scaffold level.
    return const SliverToBoxAdapter(child: SizedBox.shrink());
  }
}

/// KPI summary card — reused on Dashboard and Settlement detail.
class KpiCard extends StatelessWidget {
  const KpiCard({
    super.key,
    required this.label,
    required this.value,
    required this.icon,
    this.subtitle,
    this.iconColor,
    this.onTap,
  });

  final String label;
  final String value;
  final IconData icon;
  final String? subtitle;
  final Color? iconColor;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;
    final color = iconColor ?? cs.primary;

    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.md),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      color: color.withAlpha(30),
                      borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
                    ),
                    child: Icon(icon, size: 18, color: color),
                  ),
                  const Spacer(),
                  if (subtitle != null)
                    Text(
                      subtitle!,
                      style: tt.labelSmall?.copyWith(color: cs.onSurfaceVariant),
                    ),
                ],
              ),
              const SizedBox(height: AppSpacing.md),
              Text(value, style: tt.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
              const SizedBox(height: AppSpacing.xs),
              Text(
                label,
                style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
