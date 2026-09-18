import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers.dart';
import '../../models/customer_models.dart';
import '../../models/invoice_models.dart';
import '../../models/transaction_models.dart';
import 'customer_repository.dart';

class CustomerListState {
  const CustomerListState({
    this.items = const [],
    this.isLoading = false,
    this.hasMore = true,
    this.page = 1,
    this.pageSize = 20,
    this.search = '',
    this.error,
  });

  final List<Customer> items;
  final bool isLoading;
  final bool hasMore;
  final int page;
  final int pageSize;
  final String search;
  final String? error;

  CustomerListState copyWith({
    List<Customer>? items,
    bool? isLoading,
    bool? hasMore,
    int? page,
    int? pageSize,
    String? search,
    String? error,
  }) {
    return CustomerListState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      hasMore: hasMore ?? this.hasMore,
      page: page ?? this.page,
      pageSize: pageSize ?? this.pageSize,
      search: search ?? this.search,
      error: error,
    );
  }
}

class CustomerListNotifier extends Notifier<CustomerListState> {
  @override
  CustomerListState build() {
    Future.microtask(() => loadFirstPage());
    return const CustomerListState(isLoading: true);
  }

  CustomerRepository get _repo => ref.read(customerRepositoryProvider);
  String get _merchantId => ref.read(activeMerchantIdProvider);

  Future<void> loadFirstPage() async {
    state = state.copyWith(isLoading: true, page: 1, error: null);
    try {
      final res = await _repo.listCustomers(
        _merchantId,
        page: 1,
        pageSize: state.pageSize,
        search: state.search.isEmpty ? null : state.search,
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
      final res = await _repo.listCustomers(
        _merchantId,
        page: nextPage,
        pageSize: state.pageSize,
        search: state.search.isEmpty ? null : state.search,
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

  void setSearch(String query) {
    state = state.copyWith(search: query);
    loadFirstPage();
  }
}

final customerListProvider =
    NotifierProvider<CustomerListNotifier, CustomerListState>(CustomerListNotifier.new);

final customerDetailProvider =
    FutureProvider.family<Customer, String>((ref, customerId) async {
  final repo = ref.watch(customerRepositoryProvider);
  final merchantId = ref.watch(activeMerchantIdProvider);
  return repo.getCustomer(merchantId, customerId);
});

final customerInvoicesProvider =
    FutureProvider.family<List<Invoice>, String>((ref, customerId) async {
  final repo = ref.watch(customerRepositoryProvider);
  final merchantId = ref.watch(activeMerchantIdProvider);
  final res = await repo.getCustomerInvoices(merchantId, customerId);
  return res.items;
});

final customerTransactionsProvider =
    FutureProvider.family<List<PaymentTransaction>, String>((ref, customerId) async {
  final repo = ref.watch(customerRepositoryProvider);
  final merchantId = ref.watch(activeMerchantIdProvider);
  final res = await repo.getCustomerTransactions(merchantId, customerId);
  return res.items;
});
