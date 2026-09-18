import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers.dart';
import '../../models/invoice_models.dart';
import 'invoice_repository.dart';

class InvoiceListState {
  const InvoiceListState({
    this.items = const [],
    this.isLoading = false,
    this.hasMore = true,
    this.page = 1,
    this.pageSize = 20,
    this.statusFilter,
    this.searchQuery = '',
    this.error,
  });

  final List<Invoice> items;
  final bool isLoading;
  final bool hasMore;
  final int page;
  final int pageSize;
  final String? statusFilter;
  final String searchQuery;
  final String? error;

  InvoiceListState copyWith({
    List<Invoice>? items,
    bool? isLoading,
    bool? hasMore,
    int? page,
    int? pageSize,
    String? statusFilter,
    String? searchQuery,
    String? error,
    bool clearStatusFilter = false,
  }) {
    return InvoiceListState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      hasMore: hasMore ?? this.hasMore,
      page: page ?? this.page,
      pageSize: pageSize ?? this.pageSize,
      statusFilter: clearStatusFilter ? null : (statusFilter ?? this.statusFilter),
      searchQuery: searchQuery ?? this.searchQuery,
      error: error,
    );
  }
}

class InvoiceListNotifier extends Notifier<InvoiceListState> {
  @override
  InvoiceListState build() {
    // Initial fetch
    Future.microtask(() => loadFirstPage());
    return const InvoiceListState(isLoading: true);
  }

  InvoiceRepository get _repo => ref.read(invoiceRepositoryProvider);
  String get _merchantId => ref.read(activeMerchantIdProvider);

  Future<void> loadFirstPage() async {
    state = state.copyWith(isLoading: true, page: 1, error: null);
    try {
      final res = await _repo.listInvoices(
        _merchantId,
        page: 1,
        pageSize: state.pageSize,
        status: state.statusFilter,
        search: state.searchQuery.isEmpty ? null : state.searchQuery,
      );
      state = state.copyWith(
        items: res.items,
        isLoading: false,
        page: 1,
        hasMore: res.page < res.pages,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> loadMore() async {
    if (state.isLoading || !state.hasMore) return;
    final nextPage = state.page + 1;
    state = state.copyWith(isLoading: true);
    try {
      final res = await _repo.listInvoices(
        _merchantId,
        page: nextPage,
        pageSize: state.pageSize,
        status: state.statusFilter,
        search: state.searchQuery.isEmpty ? null : state.searchQuery,
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

  void setStatusFilter(String? status) {
    if (state.statusFilter == status) return;
    state = state.copyWith(
      statusFilter: status,
      clearStatusFilter: status == null,
    );
    loadFirstPage();
  }

  void setSearchQuery(String query) {
    state = state.copyWith(searchQuery: query);
    loadFirstPage();
  }
}

final invoiceListProvider =
    NotifierProvider<InvoiceListNotifier, InvoiceListState>(InvoiceListNotifier.new);

final invoiceDetailProvider = FutureProvider.family<Invoice, String>((ref, invoiceId) async {
  final repo = ref.watch(invoiceRepositoryProvider);
  final merchantId = ref.watch(activeMerchantIdProvider);
  return repo.getInvoice(merchantId, invoiceId);
});
