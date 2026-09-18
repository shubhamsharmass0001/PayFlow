import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers.dart';
import '../../models/settlement_models.dart';
import 'settlement_repository.dart';

class SettlementListState {
  const SettlementListState({
    this.items = const [],
    this.isLoading = false,
    this.hasMore = true,
    this.page = 1,
    this.pageSize = 20,
    this.error,
  });

  final List<Settlement> items;
  final bool isLoading;
  final bool hasMore;
  final int page;
  final int pageSize;
  final String? error;

  SettlementListState copyWith({
    List<Settlement>? items,
    bool? isLoading,
    bool? hasMore,
    int? page,
    int? pageSize,
    String? error,
  }) {
    return SettlementListState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      hasMore: hasMore ?? this.hasMore,
      page: page ?? this.page,
      pageSize: pageSize ?? this.pageSize,
      error: error,
    );
  }
}

class SettlementListNotifier extends Notifier<SettlementListState> {
  @override
  SettlementListState build() {
    Future.microtask(() => loadFirstPage());
    return const SettlementListState(isLoading: true);
  }

  SettlementRepository get _repo => ref.read(settlementRepositoryProvider);
  String get _merchantId => ref.read(activeMerchantIdProvider);

  Future<void> loadFirstPage() async {
    state = state.copyWith(isLoading: true, page: 1, error: null);
    try {
      final res = await _repo.listSettlements(
        _merchantId,
        page: 1,
        pageSize: state.pageSize,
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
      final res = await _repo.listSettlements(
        _merchantId,
        page: nextPage,
        pageSize: state.pageSize,
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
}

final settlementListProvider =
    NotifierProvider<SettlementListNotifier, SettlementListState>(SettlementListNotifier.new);

final settlementDetailProvider =
    FutureProvider.family<Settlement, String>((ref, settlementId) async {
  final repo = ref.watch(settlementRepositoryProvider);
  final merchantId = ref.watch(activeMerchantIdProvider);
  return repo.getSettlement(merchantId, settlementId);
});
