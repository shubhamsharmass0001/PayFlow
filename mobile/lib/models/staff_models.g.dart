// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'staff_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_MerchantStaff _$MerchantStaffFromJson(Map<String, dynamic> json) =>
    _MerchantStaff(
      id: json['id'] as String,
      merchantId: json['merchant_id'] as String,
      userId: json['user_id'] as String,
      storeId: json['store_id'] as String?,
      role: $enumDecode(_$StaffRoleEnumMap, json['role']),
      isActive: json['is_active'] as bool? ?? true,
      createdAt: json['created_at'] as String?,
      userName: json['user_name'] as String?,
      userEmail: json['user_email'] as String?,
    );

Map<String, dynamic> _$MerchantStaffToJson(_MerchantStaff instance) =>
    <String, dynamic>{
      'id': instance.id,
      'merchant_id': instance.merchantId,
      'user_id': instance.userId,
      'store_id': instance.storeId,
      'role': _$StaffRoleEnumMap[instance.role]!,
      'is_active': instance.isActive,
      'created_at': instance.createdAt,
      'user_name': instance.userName,
      'user_email': instance.userEmail,
    };

const _$StaffRoleEnumMap = {
  StaffRole.owner: 'OWNER',
  StaffRole.admin: 'ADMIN',
  StaffRole.manager: 'MANAGER',
  StaffRole.cashier: 'CASHIER',
  StaffRole.accountant: 'ACCOUNTANT',
};
