import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers.dart';
import '../../models/risk_models.dart';
import 'risk_repository.dart';

class RiskSignalListState {
  const RiskSignalListState({
    this.items = const [],
    this.isLoading = false,
    this.hasMore = true,
    this.page = 1,
    this.pageSize = 20,
    this.severityFilter,
    this.unreviewedOnly = false,
    this.error,
  });

  final List<RiskSignal> items;
  final bool isLoading;
  final bool hasMore;
  final int page;
  final int pageSize;
  final String? severityFilter;
  final bool unreviewedOnly;
  final String? error;

  RiskSignalListState copyWith({
    List<RiskSignal>? items,
    bool? isLoading,
    bool? hasMore,
    int? page,
    int? pageSize,
    String? severityFilter,
    bool? unreviewedOnly,
    String? error,
    bool clearSeverity = false,
  }) {
    return RiskSignalListState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      hasMore: hasMore ?? this.hasMore,
      page: page ?? this.page,
      pageSize: pageSize ?? this.pageSize,
      severityFilter: clearSeverity ? null : (severityFilter ?? this.severityFilter),
      unreviewedOnly: unreviewedOnly ?? this.unreviewedOnly,
      error: error,
    );
  }
}

class RiskSignalListNotifier extends Notifier<RiskSignalListState> {
  @override
  RiskSignalListState build() {
    Future.microtask(() => loadFirstPage());
    return const RiskSignalListState(isLoading: true);
  }

  RiskRepository get _repo => ref.read(riskRepositoryProvider);
  String get _merchantId => ref.read(activeMerchantIdProvider);

  Future<void> loadFirstPage() async {
    state = state.copyWith(isLoading: true, page: 1, error: null);
    try {
      final res = await _repo.listSignals(
        _merchantId,
        page: 1,
        pageSize: state.pageSize,
        severity: state.severityFilter,
        reviewed: state.unreviewedOnly ? false : null,
      );
      state = state.copyWith(
        items: res.items,
        isLoading: false,
        page: 1,
        hasMore: res.page < res.pages,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> loadMore() async {
    if (state.isLoading || !state.hasMore) return;
    final nextPage = state.page + 1;
    state = state.copyWith(isLoading: true);
    try {
      final res = await _repo.listSignals(
        _merchantId,
        page: nextPage,
        pageSize: state.pageSize,
        severity: state.severityFilter,
        reviewed: state.unreviewedOnly ? false : null,
      );
      state = state.copyWith(
        items: [...state.items, ...res.items],
        isLoading: false,
        page: nextPage,
        hasMore: res.page < res.pages,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void setSeverity(String? sev) {
    state = state.copyWith(severityFilter: sev, clearSeverity: sev == null);
    loadFirstPage();
  }

  void toggleUnreviewedOnly() {
    state = state.copyWith(unreviewedOnly: !state.unreviewedOnly);
    loadFirstPage();
  }

  Future<void> reviewSignal(String signalId, String resolutionNote) async {
    // Optimistic local update
    state = state.copyWith(
      items: state.items.map((s) {
        if (s.id == signalId) {
          return s.copyWith(
            isReviewed: true,
            resolutionNote: resolutionNote,
            reviewedAt: DateTime.now().toIso8601String(),
          );
        }
        return s;
      }).toList(),
    );

    try {
      await _repo.reviewSignal(
        signalId,
        resolutionNote: resolutionNote,
      );
    } catch (e) {
      // Revert if error
      loadFirstPage();
      rethrow;
    }
  }
}

final riskSignalListProvider =
    NotifierProvider<RiskSignalListNotifier, RiskSignalListState>(
  RiskSignalListNotifier.new,
);
