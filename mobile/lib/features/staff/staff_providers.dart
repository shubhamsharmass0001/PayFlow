import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers.dart';
import '../../models/staff_models.dart';
import 'staff_repository.dart';

final canManageStaffProvider = Provider<bool>((ref) {
  final role = ref.watch(userRoleProvider).toUpperCase();
  return role == 'OWNER' || role == 'MANAGER' || role == 'ADMIN';
});

class StaffListState {
  const StaffListState({
    this.items = const [],
    this.isLoading = false,
    this.error,
  });

  final List<MerchantStaff> items;
  final bool isLoading;
  final String? error;

  StaffListState copyWith({
    List<MerchantStaff>? items,
    bool? isLoading,
    String? error,
  }) {
    return StaffListState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class StaffListNotifier extends Notifier<StaffListState> {
  @override
  StaffListState build() {
    Future.microtask(() => loadStaff());
    return const StaffListState(isLoading: true);
  }

  StaffRepository get _repo => ref.read(staffRepositoryProvider);
  String get _merchantId => ref.read(activeMerchantIdProvider);

  Future<void> loadStaff() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final res = await _repo.listStaff(_merchantId);
      state = state.copyWith(
        items: res.items,
        isLoading: false,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> addStaff({
    required String userId,
    required StaffRole role,
    String? storeId,
  }) async {
    try {
      final newStaff = await _repo.addStaff(
        _merchantId,
        userId: userId,
        role: role,
        storeId: storeId,
      );
      state = state.copyWith(items: [newStaff, ...state.items]);
    } catch (e) {
      state = state.copyWith(error: e.toString());
      rethrow;
    }
  }

  Future<void> updateRole(String staffId, StaffRole newRole) async {
    try {
      final updated = await _repo.updateRole(_merchantId, staffId, newRole);
      final list = state.items.map((s) => s.id == staffId ? updated : s).toList();
      state = state.copyWith(items: list);
    } catch (e) {
      state = state.copyWith(error: e.toString());
      rethrow;
    }
  }

  Future<void> removeStaff(String staffId) async {
    try {
      await _repo.removeStaff(_merchantId, staffId);
      state = state.copyWith(items: state.items.where((s) => s.id != staffId).toList());
    } catch (e) {
      state = state.copyWith(error: e.toString());
      rethrow;
    }
  }
}

final staffListProvider =
    NotifierProvider<StaffListNotifier, StaffListState>(StaffListNotifier.new);
