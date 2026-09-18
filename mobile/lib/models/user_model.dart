import 'package:freezed_annotation/freezed_annotation.dart';

part 'user_model.freezed.dart';
part 'user_model.g.dart';

@freezed
abstract class UserModel with _$UserModel {
  const factory UserModel({
    required String id,
    required String email,
    @JsonKey(name: 'full_name') String? fullName,
    String? phone,
    @JsonKey(name: 'is_active') @Default(true) bool isActive,
    @JsonKey(name: 'is_superuser') @Default(false) bool isSuperuser,
    /// The merchant this user is the owner/staff of — populated by the
    /// /auth/me or /merchants/me endpoint. May be null for superusers with
    /// no associated merchant.
    @JsonKey(name: 'merchant_id') String? merchantId,
  }) = _UserModel;

  factory UserModel.fromJson(Map<String, dynamic> json) =>
      _$UserModelFromJson(json);
}
