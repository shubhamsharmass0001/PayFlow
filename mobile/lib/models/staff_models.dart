import 'package:freezed_annotation/freezed_annotation.dart';

part 'staff_models.freezed.dart';
part 'staff_models.g.dart';

enum StaffRole {
  @JsonValue('OWNER')      owner,
  @JsonValue('ADMIN')      admin,
  @JsonValue('MANAGER')    manager,
  @JsonValue('CASHIER')    cashier,
  @JsonValue('ACCOUNTANT') accountant,
}

@freezed
abstract class MerchantStaff with _$MerchantStaff {
  const factory MerchantStaff({
    required String id,
    @JsonKey(name: 'merchant_id') required String merchantId,
    @JsonKey(name: 'user_id') required String userId,
    @JsonKey(name: 'store_id') String? storeId,
    required StaffRole role,
    @JsonKey(name: 'is_active') @Default(true) bool isActive,
    @JsonKey(name: 'created_at') String? createdAt,
    // joined fields
    @JsonKey(name: 'user_name') String? userName,
    @JsonKey(name: 'user_email') String? userEmail,
  }) = _MerchantStaff;

  factory MerchantStaff.fromJson(Map<String, dynamic> json) =>
      _$MerchantStaffFromJson(json);
}
