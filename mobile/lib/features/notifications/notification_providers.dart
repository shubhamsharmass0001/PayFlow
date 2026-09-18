import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers.dart';
import '../../models/notification_models.dart';
import 'notification_repository.dart';

class NotificationListState {
  const NotificationListState({
    this.items = const [],
    this.isLoading = false,
    this.hasMore = true,
    this.page = 1,
    this.pageSize = 20,
    this.unreadOnly = false,
    this.error,
  });

  final List<AppNotification> items;
  final bool isLoading;
  final bool hasMore;
  final int page;
  final int pageSize;
  final bool unreadOnly;
  final String? error;

  int get unreadCount => items.where((n) => !n.isRead).length;

  NotificationListState copyWith({
    List<AppNotification>? items,
    bool? isLoading,
    bool? hasMore,
    int? page,
    int? pageSize,
    bool? unreadOnly,
    String? error,
  }) {
    return NotificationListState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      hasMore: hasMore ?? this.hasMore,
      page: page ?? this.page,
      pageSize: pageSize ?? this.pageSize,
      unreadOnly: unreadOnly ?? this.unreadOnly,
      error: error,
    );
  }
}

class NotificationListNotifier extends Notifier<NotificationListState> {
  @override
  NotificationListState build() {
    Future.microtask(() => loadFirstPage());
    return const NotificationListState(isLoading: true);
  }

  NotificationRepository get _repo => ref.read(notificationRepositoryProvider);
  String get _merchantId => ref.read(activeMerchantIdProvider);

  Future<void> loadFirstPage() async {
    state = state.copyWith(isLoading: true, page: 1, error: null);
    try {
      final res = await _repo.listNotifications(
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
      final res = await _repo.listNotifications(
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

  Future<void> markAsRead(String id) async {
    // Optimistic local update
    state = state.copyWith(
      items: state.items.map((n) {
        if (n.id == id) {
          return n.copyWith(isRead: true, readAt: DateTime.now().toIso8601String());
        }
        return n;
      }).toList(),
    );

    try {
      await _repo.markAsRead(id);
    } catch (_) {
      // Best-effort
    }
  }

  void toggleUnreadFilter() {
    state = state.copyWith(unreadOnly: !state.unreadOnly);
  }
}

final notificationListProvider =
    NotifierProvider<NotificationListNotifier, NotificationListState>(
  NotificationListNotifier.new,
);
