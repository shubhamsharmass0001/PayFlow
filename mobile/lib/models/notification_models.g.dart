// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'notification_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_AppNotification _$AppNotificationFromJson(Map<String, dynamic> json) =>
    _AppNotification(
      id: json['id'] as String,
      merchantId: json['merchant_id'] as String?,
      userId: json['user_id'] as String?,
      recipient: json['recipient'] as String,
      channel: $enumDecode(_$NotificationChannelEnumMap, json['channel']),
      template: json['template'] as String?,
      title: json['title'] as String,
      content: json['content'] as String,
      isRead: json['is_read'] as bool? ?? false,
      readAt: json['read_at'] as String?,
      sentAt: json['sent_at'] as String?,
      createdAt: json['created_at'] as String?,
    );

Map<String, dynamic> _$AppNotificationToJson(_AppNotification instance) =>
    <String, dynamic>{
      'id': instance.id,
      'merchant_id': instance.merchantId,
      'user_id': instance.userId,
      'recipient': instance.recipient,
      'channel': _$NotificationChannelEnumMap[instance.channel]!,
      'template': instance.template,
      'title': instance.title,
      'content': instance.content,
      'is_read': instance.isRead,
      'read_at': instance.readAt,
      'sent_at': instance.sentAt,
      'created_at': instance.createdAt,
    };

const _$NotificationChannelEnumMap = {
  NotificationChannel.sms: 'SMS',
  NotificationChannel.email: 'EMAIL',
  NotificationChannel.whatsapp: 'WHATSAPP',
  NotificationChannel.webhook: 'WEBHOOK',
  NotificationChannel.inApp: 'IN_APP',
  NotificationChannel.push: 'PUSH',
};
