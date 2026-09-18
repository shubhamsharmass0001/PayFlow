// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'audit_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_AuditLog _$AuditLogFromJson(Map<String, dynamic> json) => _AuditLog(
  id: json['id'] as String,
  merchantId: json['merchant_id'] as String,
  actorUserId: json['actor_user_id'] as String?,
  actorName: json['actor_name'] as String?,
  entityType: json['entity_type'] as String,
  entityId: json['entity_id'] as String,
  action: json['action'] as String,
  beforeState: json['before_state'] as Map<String, dynamic>?,
  afterState: json['after_state'] as Map<String, dynamic>?,
  ipAddress: json['ip_address'] as String?,
  createdAt: json['created_at'] as String,
);

Map<String, dynamic> _$AuditLogToJson(_AuditLog instance) => <String, dynamic>{
  'id': instance.id,
  'merchant_id': instance.merchantId,
  'actor_user_id': instance.actorUserId,
  'actor_name': instance.actorName,
  'entity_type': instance.entityType,
  'entity_id': instance.entityId,
  'action': instance.action,
  'before_state': instance.beforeState,
  'after_state': instance.afterState,
  'ip_address': instance.ipAddress,
  'created_at': instance.createdAt,
};
