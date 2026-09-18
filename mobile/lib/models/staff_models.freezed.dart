// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'staff_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$MerchantStaff {

 String get id;@JsonKey(name: 'merchant_id') String get merchantId;@JsonKey(name: 'user_id') String get userId;@JsonKey(name: 'store_id') String? get storeId; StaffRole get role;@JsonKey(name: 'is_active') bool get isActive;@JsonKey(name: 'created_at') String? get createdAt;@JsonKey(name: 'user_name') String? get userName;@JsonKey(name: 'user_email') String? get userEmail;
/// Create a copy of MerchantStaff
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MerchantStaffCopyWith<MerchantStaff> get copyWith => _$MerchantStaffCopyWithImpl<MerchantStaff>(this as MerchantStaff, _$identity);

  /// Serializes this MerchantStaff to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as MerchantStaff;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is MerchantStaff&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.merchantId, _this.merchantId) || other.merchantId == _this.merchantId)&&(identical(other.userId, _this.userId) || other.userId == _this.userId)&&(identical(other.storeId, _this.storeId) || other.storeId == _this.storeId)&&(identical(other.role, _this.role) || other.role == _this.role)&&(identical(other.isActive, _this.isActive) || other.isActive == _this.isActive)&&(identical(other.createdAt, _this.createdAt) || other.createdAt == _this.createdAt)&&(identical(other.userName, _this.userName) || other.userName == _this.userName)&&(identical(other.userEmail, _this.userEmail) || other.userEmail == _this.userEmail));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as MerchantStaff;
  return Object.hash(runtimeType,_this.id,_this.merchantId,_this.userId,_this.storeId,_this.role,_this.isActive,_this.createdAt,_this.userName,_this.userEmail);
}

@override
String toString() {
  final _this = this as MerchantStaff;
  return 'MerchantStaff(id: ${_this.id}, merchantId: ${_this.merchantId}, userId: ${_this.userId}, storeId: ${_this.storeId}, role: ${_this.role}, isActive: ${_this.isActive}, createdAt: ${_this.createdAt}, userName: ${_this.userName}, userEmail: ${_this.userEmail})';
}


}

/// @nodoc
abstract mixin class $MerchantStaffCopyWith<$Res>  {
  factory $MerchantStaffCopyWith(MerchantStaff value, $Res Function(MerchantStaff) _then) = _$MerchantStaffCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId,@JsonKey(name: 'user_id') String userId,@JsonKey(name: 'store_id') String? storeId, StaffRole role,@JsonKey(name: 'is_active') bool isActive,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'user_name') String? userName,@JsonKey(name: 'user_email') String? userEmail
});




}
/// @nodoc
class _$MerchantStaffCopyWithImpl<$Res>
    implements $MerchantStaffCopyWith<$Res> {
  _$MerchantStaffCopyWithImpl(this._self, this._then);

  final MerchantStaff _self;
  final $Res Function(MerchantStaff) _then;

/// Create a copy of MerchantStaff
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? merchantId = null,Object? userId = null,Object? storeId = freezed,Object? role = null,Object? isActive = null,Object? createdAt = freezed,Object? userName = freezed,Object? userEmail = freezed,}) {
  return _then(MerchantStaff(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,userId: null == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String,storeId: freezed == storeId ? _self.storeId : storeId // ignore: cast_nullable_to_non_nullable
as String?,role: null == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as StaffRole,isActive: null == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,userName: freezed == userName ? _self.userName : userName // ignore: cast_nullable_to_non_nullable
as String?,userEmail: freezed == userEmail ? _self.userEmail : userEmail // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [MerchantStaff].
extension MerchantStaffPatterns on MerchantStaff {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MerchantStaff value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MerchantStaff() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MerchantStaff value)  $default,){
final _that = this;
switch (_that) {
case _MerchantStaff():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MerchantStaff value)?  $default,){
final _that = this;
switch (_that) {
case _MerchantStaff() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'store_id')  String? storeId,  StaffRole role, @JsonKey(name: 'is_active')  bool isActive, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'user_name')  String? userName, @JsonKey(name: 'user_email')  String? userEmail)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MerchantStaff() when $default != null:
return $default(_that.id,_that.merchantId,_that.userId,_that.storeId,_that.role,_that.isActive,_that.createdAt,_that.userName,_that.userEmail);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'store_id')  String? storeId,  StaffRole role, @JsonKey(name: 'is_active')  bool isActive, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'user_name')  String? userName, @JsonKey(name: 'user_email')  String? userEmail)  $default,) {final _that = this;
switch (_that) {
case _MerchantStaff():
return $default(_that.id,_that.merchantId,_that.userId,_that.storeId,_that.role,_that.isActive,_that.createdAt,_that.userName,_that.userEmail);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'store_id')  String? storeId,  StaffRole role, @JsonKey(name: 'is_active')  bool isActive, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'user_name')  String? userName, @JsonKey(name: 'user_email')  String? userEmail)?  $default,) {final _that = this;
switch (_that) {
case _MerchantStaff() when $default != null:
return $default(_that.id,_that.merchantId,_that.userId,_that.storeId,_that.role,_that.isActive,_that.createdAt,_that.userName,_that.userEmail);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _MerchantStaff implements MerchantStaff {
  const _MerchantStaff({required this.id, @JsonKey(name: 'merchant_id') required this.merchantId, @JsonKey(name: 'user_id') required this.userId, @JsonKey(name: 'store_id') this.storeId, required this.role, @JsonKey(name: 'is_active') this.isActive = true, @JsonKey(name: 'created_at') this.createdAt, @JsonKey(name: 'user_name') this.userName, @JsonKey(name: 'user_email') this.userEmail});
  factory _MerchantStaff.fromJson(Map<String, dynamic> json) => _$MerchantStaffFromJson(json);

@override final  String id;
@override@JsonKey(name: 'merchant_id') final  String merchantId;
@override@JsonKey(name: 'user_id') final  String userId;
@override@JsonKey(name: 'store_id') final  String? storeId;
@override final  StaffRole role;
@override@JsonKey(name: 'is_active') final  bool isActive;
@override@JsonKey(name: 'created_at') final  String? createdAt;
@override@JsonKey(name: 'user_name') final  String? userName;
@override@JsonKey(name: 'user_email') final  String? userEmail;

/// Create a copy of MerchantStaff
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MerchantStaffCopyWith<_MerchantStaff> get copyWith => __$MerchantStaffCopyWithImpl<_MerchantStaff>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MerchantStaffToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _MerchantStaff&&(identical(other.id, id) || other.id == id)&&(identical(other.merchantId, merchantId) || other.merchantId == merchantId)&&(identical(other.userId, userId) || other.userId == userId)&&(identical(other.storeId, storeId) || other.storeId == storeId)&&(identical(other.role, role) || other.role == role)&&(identical(other.isActive, isActive) || other.isActive == isActive)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.userName, userName) || other.userName == userName)&&(identical(other.userEmail, userEmail) || other.userEmail == userEmail));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,merchantId,userId,storeId,role,isActive,createdAt,userName,userEmail);
}

@override
String toString() {
    return 'MerchantStaff(id: $id, merchantId: $merchantId, userId: $userId, storeId: $storeId, role: $role, isActive: $isActive, createdAt: $createdAt, userName: $userName, userEmail: $userEmail)';
}


}

/// @nodoc
abstract mixin class _$MerchantStaffCopyWith<$Res> implements $MerchantStaffCopyWith<$Res> {
  factory _$MerchantStaffCopyWith(_MerchantStaff value, $Res Function(_MerchantStaff) _then) = __$MerchantStaffCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId,@JsonKey(name: 'user_id') String userId,@JsonKey(name: 'store_id') String? storeId, StaffRole role,@JsonKey(name: 'is_active') bool isActive,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'user_name') String? userName,@JsonKey(name: 'user_email') String? userEmail
});




}
/// @nodoc
class __$MerchantStaffCopyWithImpl<$Res>
    implements _$MerchantStaffCopyWith<$Res> {
  __$MerchantStaffCopyWithImpl(this._self, this._then);

  final _MerchantStaff _self;
  final $Res Function(_MerchantStaff) _then;

/// Create a copy of MerchantStaff
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? merchantId = null,Object? userId = null,Object? storeId = freezed,Object? role = null,Object? isActive = null,Object? createdAt = freezed,Object? userName = freezed,Object? userEmail = freezed,}) {
  return _then(_MerchantStaff(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,userId: null == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String,storeId: freezed == storeId ? _self.storeId : storeId // ignore: cast_nullable_to_non_nullable
as String?,role: null == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as StaffRole,isActive: null == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,userName: freezed == userName ? _self.userName : userName // ignore: cast_nullable_to_non_nullable
as String?,userEmail: freezed == userEmail ? _self.userEmail : userEmail // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
