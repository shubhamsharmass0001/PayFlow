import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers.dart';
import '../../models/audit_models.dart';
import 'audit_repository.dart';

final canViewAuditLogsProvider = Provider<bool>((ref) {
  final role = ref.watch(userRoleProvider).toUpperCase();
  return role == 'OWNER' || role == 'AUDITOR' || role == 'ADMIN';
});

class AuditLogListState {
  const AuditLogListState({
    this.items = const [],
    this.isLoading = false,
    this.hasMore = true,
    this.page = 1,
    this.pageSize = 20,
    this.entityType,
    this.action,
    this.error,
  });

  final List<AuditLog> items;
  final bool isLoading;
  final bool hasMore;
  final int page;
  final int pageSize;
  final String? entityType;
  final String? action;
  final String? error;

  AuditLogListState copyWith({
    List<AuditLog>? items,
    bool? isLoading,
    bool? hasMore,
    int? page,
    int? pageSize,
    String? entityType,
    String? action,
    String? error,
    bool clearEntity = false,
    bool clearAction = false,
  }) {
    return AuditLogListState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      hasMore: hasMore ?? this.hasMore,
      page: page ?? this.page,
      pageSize: pageSize ?? this.pageSize,
      entityType: clearEntity ? null : (entityType ?? this.entityType),
      action: clearAction ? null : (action ?? this.action),
      error: error,
    );
  }
}

class AuditLogListNotifier extends Notifier<AuditLogListState> {
  @override
  AuditLogListState build() {
    Future.microtask(() => loadFirstPage());
    return const AuditLogListState(isLoading: true);
  }

  AuditRepository get _repo => ref.read(auditRepositoryProvider);
  String get _merchantId => ref.read(activeMerchantIdProvider);

  Future<void> loadFirstPage() async {
    state = state.copyWith(isLoading: true, page: 1, error: null);
    try {
      final res = await _repo.listAuditLogs(
        _merchantId,
        page: 1,
        pageSize: state.pageSize,
        entityType: state.entityType,
        action: state.action,
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
      final res = await _repo.listAuditLogs(
        _merchantId,
        page: nextPage,
        pageSize: state.pageSize,
        entityType: state.entityType,
        action: state.action,
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

  void setEntityTypeFilter(String? entityType) {
    state = state.copyWith(
      entityType: entityType,
      clearEntity: entityType == null,
    );
    loadFirstPage();
  }

  void setActionFilter(String? action) {
    state = state.copyWith(
      action: action,
      clearAction: action == null,
    );
    loadFirstPage();
  }
}

final auditLogListProvider =
    NotifierProvider<AuditLogListNotifier, AuditLogListState>(AuditLogListNotifier.new);

final auditLogDetailProvider =
    FutureProvider.family<AuditLog, String>((ref, logId) async {
  final repo = ref.watch(auditRepositoryProvider);
  final merchantId = ref.watch(activeMerchantIdProvider);
  return repo.getAuditLog(merchantId, logId);
});
