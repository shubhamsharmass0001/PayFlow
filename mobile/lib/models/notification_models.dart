import 'package:freezed_annotation/freezed_annotation.dart';

part 'notification_models.freezed.dart';
part 'notification_models.g.dart';

enum NotificationChannel {
  @JsonValue('SMS')      sms,
  @JsonValue('EMAIL')    email,
  @JsonValue('WHATSAPP') whatsapp,
  @JsonValue('WEBHOOK')  webhook,
  @JsonValue('IN_APP')   inApp,
  @JsonValue('PUSH')     push,
}

@freezed
abstract class AppNotification with _$AppNotification {
  const factory AppNotification({
    required String id,
    @JsonKey(name: 'merchant_id') String? merchantId,
    @JsonKey(name: 'user_id') String? userId,
    required String recipient,
    required NotificationChannel channel,
    String? template,
    required String title,
    required String content,
    @JsonKey(name: 'is_read') @Default(false) bool isRead,
    @JsonKey(name: 'read_at') String? readAt,
    @JsonKey(name: 'sent_at') String? sentAt,
    @JsonKey(name: 'created_at') String? createdAt,
  }) = _AppNotification;

  factory AppNotification.fromJson(Map<String, dynamic> json) =>
      _$AppNotificationFromJson(json);
}
