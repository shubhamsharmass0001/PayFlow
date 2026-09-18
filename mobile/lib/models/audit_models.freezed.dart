// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'audit_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$AuditLog {

 String get id;@JsonKey(name: 'merchant_id') String get merchantId;@JsonKey(name: 'actor_user_id') String? get actorUserId;@JsonKey(name: 'actor_name') String? get actorName;@JsonKey(name: 'entity_type') String get entityType;@JsonKey(name: 'entity_id') String get entityId; String get action;@JsonKey(name: 'before_state') Map<String, dynamic>? get beforeState;@JsonKey(name: 'after_state') Map<String, dynamic>? get afterState;@JsonKey(name: 'ip_address') String? get ipAddress;@JsonKey(name: 'created_at') String get createdAt;
/// Create a copy of AuditLog
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AuditLogCopyWith<AuditLog> get copyWith => _$AuditLogCopyWithImpl<AuditLog>(this as AuditLog, _$identity);

  /// Serializes this AuditLog to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as AuditLog;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AuditLog&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.merchantId, _this.merchantId) || other.merchantId == _this.merchantId)&&(identical(other.actorUserId, _this.actorUserId) || other.actorUserId == _this.actorUserId)&&(identical(other.actorName, _this.actorName) || other.actorName == _this.actorName)&&(identical(other.entityType, _this.entityType) || other.entityType == _this.entityType)&&(identical(other.entityId, _this.entityId) || other.entityId == _this.entityId)&&(identical(other.action, _this.action) || other.action == _this.action)&&const DeepCollectionEquality().equals(other.beforeState, _this.beforeState)&&const DeepCollectionEquality().equals(other.afterState, _this.afterState)&&(identical(other.ipAddress, _this.ipAddress) || other.ipAddress == _this.ipAddress)&&(identical(other.createdAt, _this.createdAt) || other.createdAt == _this.createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as AuditLog;
  return Object.hash(runtimeType,_this.id,_this.merchantId,_this.actorUserId,_this.actorName,_this.entityType,_this.entityId,_this.action,const DeepCollectionEquality().hash(_this.beforeState),const DeepCollectionEquality().hash(_this.afterState),_this.ipAddress,_this.createdAt);
}

@override
String toString() {
  final _this = this as AuditLog;
  return 'AuditLog(id: ${_this.id}, merchantId: ${_this.merchantId}, actorUserId: ${_this.actorUserId}, actorName: ${_this.actorName}, entityType: ${_this.entityType}, entityId: ${_this.entityId}, action: ${_this.action}, beforeState: ${_this.beforeState}, afterState: ${_this.afterState}, ipAddress: ${_this.ipAddress}, createdAt: ${_this.createdAt})';
}


}

/// @nodoc
abstract mixin class $AuditLogCopyWith<$Res>  {
  factory $AuditLogCopyWith(AuditLog value, $Res Function(AuditLog) _then) = _$AuditLogCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId,@JsonKey(name: 'actor_user_id') String? actorUserId,@JsonKey(name: 'actor_name') String? actorName,@JsonKey(name: 'entity_type') String entityType,@JsonKey(name: 'entity_id') String entityId, String action,@JsonKey(name: 'before_state') Map<String, dynamic>? beforeState,@JsonKey(name: 'after_state') Map<String, dynamic>? afterState,@JsonKey(name: 'ip_address') String? ipAddress,@JsonKey(name: 'created_at') String createdAt
});




}
/// @nodoc
class _$AuditLogCopyWithImpl<$Res>
    implements $AuditLogCopyWith<$Res> {
  _$AuditLogCopyWithImpl(this._self, this._then);

  final AuditLog _self;
  final $Res Function(AuditLog) _then;

/// Create a copy of AuditLog
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? merchantId = null,Object? actorUserId = freezed,Object? actorName = freezed,Object? entityType = null,Object? entityId = null,Object? action = null,Object? beforeState = freezed,Object? afterState = freezed,Object? ipAddress = freezed,Object? createdAt = null,}) {
  return _then(AuditLog(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,actorUserId: freezed == actorUserId ? _self.actorUserId : actorUserId // ignore: cast_nullable_to_non_nullable
as String?,actorName: freezed == actorName ? _self.actorName : actorName // ignore: cast_nullable_to_non_nullable
as String?,entityType: null == entityType ? _self.entityType : entityType // ignore: cast_nullable_to_non_nullable
as String,entityId: null == entityId ? _self.entityId : entityId // ignore: cast_nullable_to_non_nullable
as String,action: null == action ? _self.action : action // ignore: cast_nullable_to_non_nullable
as String,beforeState: freezed == beforeState ? _self.beforeState : beforeState // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,afterState: freezed == afterState ? _self.afterState : afterState // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,ipAddress: freezed == ipAddress ? _self.ipAddress : ipAddress // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [AuditLog].
extension AuditLogPatterns on AuditLog {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AuditLog value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AuditLog() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AuditLog value)  $default,){
final _that = this;
switch (_that) {
case _AuditLog():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AuditLog value)?  $default,){
final _that = this;
switch (_that) {
case _AuditLog() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'actor_user_id')  String? actorUserId, @JsonKey(name: 'actor_name')  String? actorName, @JsonKey(name: 'entity_type')  String entityType, @JsonKey(name: 'entity_id')  String entityId,  String action, @JsonKey(name: 'before_state')  Map<String, dynamic>? beforeState, @JsonKey(name: 'after_state')  Map<String, dynamic>? afterState, @JsonKey(name: 'ip_address')  String? ipAddress, @JsonKey(name: 'created_at')  String createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AuditLog() when $default != null:
return $default(_that.id,_that.merchantId,_that.actorUserId,_that.actorName,_that.entityType,_that.entityId,_that.action,_that.beforeState,_that.afterState,_that.ipAddress,_that.createdAt);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'actor_user_id')  String? actorUserId, @JsonKey(name: 'actor_name')  String? actorName, @JsonKey(name: 'entity_type')  String entityType, @JsonKey(name: 'entity_id')  String entityId,  String action, @JsonKey(name: 'before_state')  Map<String, dynamic>? beforeState, @JsonKey(name: 'after_state')  Map<String, dynamic>? afterState, @JsonKey(name: 'ip_address')  String? ipAddress, @JsonKey(name: 'created_at')  String createdAt)  $default,) {final _that = this;
switch (_that) {
case _AuditLog():
return $default(_that.id,_that.merchantId,_that.actorUserId,_that.actorName,_that.entityType,_that.entityId,_that.action,_that.beforeState,_that.afterState,_that.ipAddress,_that.createdAt);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'actor_user_id')  String? actorUserId, @JsonKey(name: 'actor_name')  String? actorName, @JsonKey(name: 'entity_type')  String entityType, @JsonKey(name: 'entity_id')  String entityId,  String action, @JsonKey(name: 'before_state')  Map<String, dynamic>? beforeState, @JsonKey(name: 'after_state')  Map<String, dynamic>? afterState, @JsonKey(name: 'ip_address')  String? ipAddress, @JsonKey(name: 'created_at')  String createdAt)?  $default,) {final _that = this;
switch (_that) {
case _AuditLog() when $default != null:
return $default(_that.id,_that.merchantId,_that.actorUserId,_that.actorName,_that.entityType,_that.entityId,_that.action,_that.beforeState,_that.afterState,_that.ipAddress,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _AuditLog implements AuditLog {
  const _AuditLog({required this.id, @JsonKey(name: 'merchant_id') required this.merchantId, @JsonKey(name: 'actor_user_id') this.actorUserId, @JsonKey(name: 'actor_name') this.actorName, @JsonKey(name: 'entity_type') required this.entityType, @JsonKey(name: 'entity_id') required this.entityId, required this.action, @JsonKey(name: 'before_state')  Map<String, dynamic>? beforeState, @JsonKey(name: 'after_state')  Map<String, dynamic>? afterState, @JsonKey(name: 'ip_address') this.ipAddress, @JsonKey(name: 'created_at') required this.createdAt}): _beforeState = beforeState,_afterState = afterState;
  factory _AuditLog.fromJson(Map<String, dynamic> json) => _$AuditLogFromJson(json);

@override final  String id;
@override@JsonKey(name: 'merchant_id') final  String merchantId;
@override@JsonKey(name: 'actor_user_id') final  String? actorUserId;
@override@JsonKey(name: 'actor_name') final  String? actorName;
@override@JsonKey(name: 'entity_type') final  String entityType;
@override@JsonKey(name: 'entity_id') final  String entityId;
@override final  String action;
 final  Map<String, dynamic>? _beforeState;
@override@JsonKey(name: 'before_state') Map<String, dynamic>? get beforeState {
  final value = _beforeState;
  if (value == null) return null;
  if (_beforeState is EqualUnmodifiableMapView) return _beforeState;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _afterState;
@override@JsonKey(name: 'after_state') Map<String, dynamic>? get afterState {
  final value = _afterState;
  if (value == null) return null;
  if (_afterState is EqualUnmodifiableMapView) return _afterState;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'ip_address') final  String? ipAddress;
@override@JsonKey(name: 'created_at') final  String createdAt;

/// Create a copy of AuditLog
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AuditLogCopyWith<_AuditLog> get copyWith => __$AuditLogCopyWithImpl<_AuditLog>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AuditLogToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _AuditLog&&(identical(other.id, id) || other.id == id)&&(identical(other.merchantId, merchantId) || other.merchantId == merchantId)&&(identical(other.actorUserId, actorUserId) || other.actorUserId == actorUserId)&&(identical(other.actorName, actorName) || other.actorName == actorName)&&(identical(other.entityType, entityType) || other.entityType == entityType)&&(identical(other.entityId, entityId) || other.entityId == entityId)&&(identical(other.action, action) || other.action == action)&&const DeepCollectionEquality().equals(other.beforeState, _beforeState)&&const DeepCollectionEquality().equals(other.afterState, _afterState)&&(identical(other.ipAddress, ipAddress) || other.ipAddress == ipAddress)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,merchantId,actorUserId,actorName,entityType,entityId,action,const DeepCollectionEquality().hash(_beforeState),const DeepCollectionEquality().hash(_afterState),ipAddress,createdAt);
}

@override
String toString() {
    return 'AuditLog(id: $id, merchantId: $merchantId, actorUserId: $actorUserId, actorName: $actorName, entityType: $entityType, entityId: $entityId, action: $action, beforeState: $beforeState, afterState: $afterState, ipAddress: $ipAddress, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$AuditLogCopyWith<$Res> implements $AuditLogCopyWith<$Res> {
  factory _$AuditLogCopyWith(_AuditLog value, $Res Function(_AuditLog) _then) = __$AuditLogCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId,@JsonKey(name: 'actor_user_id') String? actorUserId,@JsonKey(name: 'actor_name') String? actorName,@JsonKey(name: 'entity_type') String entityType,@JsonKey(name: 'entity_id') String entityId, String action,@JsonKey(name: 'before_state') Map<String, dynamic>? beforeState,@JsonKey(name: 'after_state') Map<String, dynamic>? afterState,@JsonKey(name: 'ip_address') String? ipAddress,@JsonKey(name: 'created_at') String createdAt
});




}
/// @nodoc
class __$AuditLogCopyWithImpl<$Res>
    implements _$AuditLogCopyWith<$Res> {
  __$AuditLogCopyWithImpl(this._self, this._then);

  final _AuditLog _self;
  final $Res Function(_AuditLog) _then;

/// Create a copy of AuditLog
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? merchantId = null,Object? actorUserId = freezed,Object? actorName = freezed,Object? entityType = null,Object? entityId = null,Object? action = null,Object? beforeState = freezed,Object? afterState = freezed,Object? ipAddress = freezed,Object? createdAt = null,}) {
  return _then(_AuditLog(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,actorUserId: freezed == actorUserId ? _self.actorUserId : actorUserId // ignore: cast_nullable_to_non_nullable
as String?,actorName: freezed == actorName ? _self.actorName : actorName // ignore: cast_nullable_to_non_nullable
as String?,entityType: null == entityType ? _self.entityType : entityType // ignore: cast_nullable_to_non_nullable
as String,entityId: null == entityId ? _self.entityId : entityId // ignore: cast_nullable_to_non_nullable
as String,action: null == action ? _self.action : action // ignore: cast_nullable_to_non_nullable
as String,beforeState: freezed == beforeState ? _self._beforeState : beforeState // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,afterState: freezed == afterState ? _self._afterState : afterState // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,ipAddress: freezed == ipAddress ? _self.ipAddress : ipAddress // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
