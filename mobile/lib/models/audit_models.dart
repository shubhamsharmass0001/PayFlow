import 'package:freezed_annotation/freezed_annotation.dart';

part 'audit_models.freezed.dart';
part 'audit_models.g.dart';

@freezed
abstract class AuditLog with _$AuditLog {
  const factory AuditLog({
    required String id,
    @JsonKey(name: 'merchant_id') required String merchantId,
    @JsonKey(name: 'actor_user_id') String? actorUserId,
    @JsonKey(name: 'actor_name') String? actorName,
    @JsonKey(name: 'entity_type') required String entityType,
    @JsonKey(name: 'entity_id') required String entityId,
    required String action,
    @JsonKey(name: 'before_state') Map<String, dynamic>? beforeState,
    @JsonKey(name: 'after_state') Map<String, dynamic>? afterState,
    @JsonKey(name: 'ip_address') String? ipAddress,
    @JsonKey(name: 'created_at') required String createdAt,
  }) = _AuditLog;

  factory AuditLog.fromJson(Map<String, dynamic> json) =>
      _$AuditLogFromJson(json);
}
