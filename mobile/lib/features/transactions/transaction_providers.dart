import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers.dart';
import '../../models/transaction_models.dart';
import 'transaction_repository.dart';

class TransactionFilterState {
  const TransactionFilterState({
    this.status,
    this.paymentMethod,
    this.startDate,
    this.endDate,
  });

  final String? status;
  final String? paymentMethod;
  final String? startDate;
  final String? endDate;

  bool get hasActiveFilters =>
      status != null || paymentMethod != null || startDate != null || endDate != null;

  TransactionFilterState copyWith({
    String? status,
    String? paymentMethod,
    String? startDate,
    String? endDate,
    bool clearStatus = false,
    bool clearMethod = false,
    bool clearDates = false,
  }) {
    return TransactionFilterState(
      status: clearStatus ? null : (status ?? this.status),
      paymentMethod: clearMethod ? null : (paymentMethod ?? this.paymentMethod),
      startDate: clearDates ? null : (startDate ?? this.startDate),
      endDate: clearDates ? null : (endDate ?? this.endDate),
    );
  }
}

class TransactionListState {
  const TransactionListState({
    this.items = const [],
    this.isLoading = false,
    this.hasMore = true,
    this.page = 1,
    this.pageSize = 20,
    this.filters = const TransactionFilterState(),
    this.error,
  });

  final List<PaymentTransaction> items;
  final bool isLoading;
  final bool hasMore;
  final int page;
  final int pageSize;
  final TransactionFilterState filters;
  final String? error;

  TransactionListState copyWith({
    List<PaymentTransaction>? items,
    bool? isLoading,
    bool? hasMore,
    int? page,
    int? pageSize,
    TransactionFilterState? filters,
    String? error,
  }) {
    return TransactionListState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      hasMore: hasMore ?? this.hasMore,
      page: page ?? this.page,
      pageSize: pageSize ?? this.pageSize,
      filters: filters ?? this.filters,
      error: error,
    );
  }
}

class TransactionListNotifier extends Notifier<TransactionListState> {
  @override
  TransactionListState build() {
    Future.microtask(() => loadFirstPage());
    return const TransactionListState(isLoading: true);
  }

  TransactionRepository get _repo => ref.read(transactionRepositoryProvider);
  String get _merchantId => ref.read(activeMerchantIdProvider);

  Future<void> loadFirstPage() async {
    state = state.copyWith(isLoading: true, page: 1, error: null);
    try {
      final res = await _repo.listTransactions(
        _merchantId,
        page: 1,
        pageSize: state.pageSize,
        status: state.filters.status,
        method: state.filters.paymentMethod,
        from: state.filters.startDate,
        to: state.filters.endDate,
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
      final res = await _repo.listTransactions(
        _merchantId,
        page: nextPage,
        pageSize: state.pageSize,
        status: state.filters.status,
        method: state.filters.paymentMethod,
        from: state.filters.startDate,
        to: state.filters.endDate,
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

  void updateFilters(TransactionFilterState filters) {
    state = state.copyWith(filters: filters);
    loadFirstPage();
  }

  void clearFilters() {
    state = state.copyWith(filters: const TransactionFilterState());
    loadFirstPage();
  }
}

final transactionListProvider =
    NotifierProvider<TransactionListNotifier, TransactionListState>(
  TransactionListNotifier.new,
);

final transactionDetailProvider =
    FutureProvider.family<PaymentTransaction, String>((ref, transactionId) async {
  final repo = ref.watch(transactionRepositoryProvider);
  final merchantId = ref.watch(activeMerchantIdProvider);
  return repo.getTransaction(merchantId, transactionId);
});
