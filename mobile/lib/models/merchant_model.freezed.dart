// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'merchant_model.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$MerchantModel {

 String get id;@JsonKey(name: 'business_name') String get businessName;@JsonKey(name: 'legal_name') String get legalName; String get email; String get phone;@JsonKey(name: 'kyc_status') KycStatus get kycStatus;@JsonKey(name: 'risk_tier') RiskTier get riskTier;@JsonKey(name: 'upi_vpa') String? get upiVpa;@JsonKey(name: 'mcc_code') String? get mccCode;@JsonKey(name: 'is_active') bool get isActive;@JsonKey(name: 'created_at') String? get createdAt;
/// Create a copy of MerchantModel
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MerchantModelCopyWith<MerchantModel> get copyWith => _$MerchantModelCopyWithImpl<MerchantModel>(this as MerchantModel, _$identity);

  /// Serializes this MerchantModel to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as MerchantModel;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is MerchantModel&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.businessName, _this.businessName) || other.businessName == _this.businessName)&&(identical(other.legalName, _this.legalName) || other.legalName == _this.legalName)&&(identical(other.email, _this.email) || other.email == _this.email)&&(identical(other.phone, _this.phone) || other.phone == _this.phone)&&(identical(other.kycStatus, _this.kycStatus) || other.kycStatus == _this.kycStatus)&&(identical(other.riskTier, _this.riskTier) || other.riskTier == _this.riskTier)&&(identical(other.upiVpa, _this.upiVpa) || other.upiVpa == _this.upiVpa)&&(identical(other.mccCode, _this.mccCode) || other.mccCode == _this.mccCode)&&(identical(other.isActive, _this.isActive) || other.isActive == _this.isActive)&&(identical(other.createdAt, _this.createdAt) || other.createdAt == _this.createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as MerchantModel;
  return Object.hash(runtimeType,_this.id,_this.businessName,_this.legalName,_this.email,_this.phone,_this.kycStatus,_this.riskTier,_this.upiVpa,_this.mccCode,_this.isActive,_this.createdAt);
}

@override
String toString() {
  final _this = this as MerchantModel;
  return 'MerchantModel(id: ${_this.id}, businessName: ${_this.businessName}, legalName: ${_this.legalName}, email: ${_this.email}, phone: ${_this.phone}, kycStatus: ${_this.kycStatus}, riskTier: ${_this.riskTier}, upiVpa: ${_this.upiVpa}, mccCode: ${_this.mccCode}, isActive: ${_this.isActive}, createdAt: ${_this.createdAt})';
}


}

/// @nodoc
abstract mixin class $MerchantModelCopyWith<$Res>  {
  factory $MerchantModelCopyWith(MerchantModel value, $Res Function(MerchantModel) _then) = _$MerchantModelCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'business_name') String businessName,@JsonKey(name: 'legal_name') String legalName, String email, String phone,@JsonKey(name: 'kyc_status') KycStatus kycStatus,@JsonKey(name: 'risk_tier') RiskTier riskTier,@JsonKey(name: 'upi_vpa') String? upiVpa,@JsonKey(name: 'mcc_code') String? mccCode,@JsonKey(name: 'is_active') bool isActive,@JsonKey(name: 'created_at') String? createdAt
});




}
/// @nodoc
class _$MerchantModelCopyWithImpl<$Res>
    implements $MerchantModelCopyWith<$Res> {
  _$MerchantModelCopyWithImpl(this._self, this._then);

  final MerchantModel _self;
  final $Res Function(MerchantModel) _then;

/// Create a copy of MerchantModel
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? businessName = null,Object? legalName = null,Object? email = null,Object? phone = null,Object? kycStatus = null,Object? riskTier = null,Object? upiVpa = freezed,Object? mccCode = freezed,Object? isActive = null,Object? createdAt = freezed,}) {
  return _then(MerchantModel(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,businessName: null == businessName ? _self.businessName : businessName // ignore: cast_nullable_to_non_nullable
as String,legalName: null == legalName ? _self.legalName : legalName // ignore: cast_nullable_to_non_nullable
as String,email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,phone: null == phone ? _self.phone : phone // ignore: cast_nullable_to_non_nullable
as String,kycStatus: null == kycStatus ? _self.kycStatus : kycStatus // ignore: cast_nullable_to_non_nullable
as KycStatus,riskTier: null == riskTier ? _self.riskTier : riskTier // ignore: cast_nullable_to_non_nullable
as RiskTier,upiVpa: freezed == upiVpa ? _self.upiVpa : upiVpa // ignore: cast_nullable_to_non_nullable
as String?,mccCode: freezed == mccCode ? _self.mccCode : mccCode // ignore: cast_nullable_to_non_nullable
as String?,isActive: null == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [MerchantModel].
extension MerchantModelPatterns on MerchantModel {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MerchantModel value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MerchantModel() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MerchantModel value)  $default,){
final _that = this;
switch (_that) {
case _MerchantModel():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MerchantModel value)?  $default,){
final _that = this;
switch (_that) {
case _MerchantModel() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'business_name')  String businessName, @JsonKey(name: 'legal_name')  String legalName,  String email,  String phone, @JsonKey(name: 'kyc_status')  KycStatus kycStatus, @JsonKey(name: 'risk_tier')  RiskTier riskTier, @JsonKey(name: 'upi_vpa')  String? upiVpa, @JsonKey(name: 'mcc_code')  String? mccCode, @JsonKey(name: 'is_active')  bool isActive, @JsonKey(name: 'created_at')  String? createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MerchantModel() when $default != null:
return $default(_that.id,_that.businessName,_that.legalName,_that.email,_that.phone,_that.kycStatus,_that.riskTier,_that.upiVpa,_that.mccCode,_that.isActive,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'business_name')  String businessName, @JsonKey(name: 'legal_name')  String legalName,  String email,  String phone, @JsonKey(name: 'kyc_status')  KycStatus kycStatus, @JsonKey(name: 'risk_tier')  RiskTier riskTier, @JsonKey(name: 'upi_vpa')  String? upiVpa, @JsonKey(name: 'mcc_code')  String? mccCode, @JsonKey(name: 'is_active')  bool isActive, @JsonKey(name: 'created_at')  String? createdAt)  $default,) {final _that = this;
switch (_that) {
case _MerchantModel():
return $default(_that.id,_that.businessName,_that.legalName,_that.email,_that.phone,_that.kycStatus,_that.riskTier,_that.upiVpa,_that.mccCode,_that.isActive,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'business_name')  String businessName, @JsonKey(name: 'legal_name')  String legalName,  String email,  String phone, @JsonKey(name: 'kyc_status')  KycStatus kycStatus, @JsonKey(name: 'risk_tier')  RiskTier riskTier, @JsonKey(name: 'upi_vpa')  String? upiVpa, @JsonKey(name: 'mcc_code')  String? mccCode, @JsonKey(name: 'is_active')  bool isActive, @JsonKey(name: 'created_at')  String? createdAt)?  $default,) {final _that = this;
switch (_that) {
case _MerchantModel() when $default != null:
return $default(_that.id,_that.businessName,_that.legalName,_that.email,_that.phone,_that.kycStatus,_that.riskTier,_that.upiVpa,_that.mccCode,_that.isActive,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _MerchantModel implements MerchantModel {
  const _MerchantModel({required this.id, @JsonKey(name: 'business_name') required this.businessName, @JsonKey(name: 'legal_name') required this.legalName, required this.email, required this.phone, @JsonKey(name: 'kyc_status') this.kycStatus = KycStatus.pending, @JsonKey(name: 'risk_tier') this.riskTier = RiskTier.medium, @JsonKey(name: 'upi_vpa') this.upiVpa, @JsonKey(name: 'mcc_code') this.mccCode, @JsonKey(name: 'is_active') this.isActive = true, @JsonKey(name: 'created_at') this.createdAt});
  factory _MerchantModel.fromJson(Map<String, dynamic> json) => _$MerchantModelFromJson(json);

@override final  String id;
@override@JsonKey(name: 'business_name') final  String businessName;
@override@JsonKey(name: 'legal_name') final  String legalName;
@override final  String email;
@override final  String phone;
@override@JsonKey(name: 'kyc_status') final  KycStatus kycStatus;
@override@JsonKey(name: 'risk_tier') final  RiskTier riskTier;
@override@JsonKey(name: 'upi_vpa') final  String? upiVpa;
@override@JsonKey(name: 'mcc_code') final  String? mccCode;
@override@JsonKey(name: 'is_active') final  bool isActive;
@override@JsonKey(name: 'created_at') final  String? createdAt;

/// Create a copy of MerchantModel
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MerchantModelCopyWith<_MerchantModel> get copyWith => __$MerchantModelCopyWithImpl<_MerchantModel>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MerchantModelToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _MerchantModel&&(identical(other.id, id) || other.id == id)&&(identical(other.businessName, businessName) || other.businessName == businessName)&&(identical(other.legalName, legalName) || other.legalName == legalName)&&(identical(other.email, email) || other.email == email)&&(identical(other.phone, phone) || other.phone == phone)&&(identical(other.kycStatus, kycStatus) || other.kycStatus == kycStatus)&&(identical(other.riskTier, riskTier) || other.riskTier == riskTier)&&(identical(other.upiVpa, upiVpa) || other.upiVpa == upiVpa)&&(identical(other.mccCode, mccCode) || other.mccCode == mccCode)&&(identical(other.isActive, isActive) || other.isActive == isActive)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,businessName,legalName,email,phone,kycStatus,riskTier,upiVpa,mccCode,isActive,createdAt);
}

@override
String toString() {
    return 'MerchantModel(id: $id, businessName: $businessName, legalName: $legalName, email: $email, phone: $phone, kycStatus: $kycStatus, riskTier: $riskTier, upiVpa: $upiVpa, mccCode: $mccCode, isActive: $isActive, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$MerchantModelCopyWith<$Res> implements $MerchantModelCopyWith<$Res> {
  factory _$MerchantModelCopyWith(_MerchantModel value, $Res Function(_MerchantModel) _then) = __$MerchantModelCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'business_name') String businessName,@JsonKey(name: 'legal_name') String legalName, String email, String phone,@JsonKey(name: 'kyc_status') KycStatus kycStatus,@JsonKey(name: 'risk_tier') RiskTier riskTier,@JsonKey(name: 'upi_vpa') String? upiVpa,@JsonKey(name: 'mcc_code') String? mccCode,@JsonKey(name: 'is_active') bool isActive,@JsonKey(name: 'created_at') String? createdAt
});




}
/// @nodoc
class __$MerchantModelCopyWithImpl<$Res>
    implements _$MerchantModelCopyWith<$Res> {
  __$MerchantModelCopyWithImpl(this._self, this._then);

  final _MerchantModel _self;
  final $Res Function(_MerchantModel) _then;

/// Create a copy of MerchantModel
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? businessName = null,Object? legalName = null,Object? email = null,Object? phone = null,Object? kycStatus = null,Object? riskTier = null,Object? upiVpa = freezed,Object? mccCode = freezed,Object? isActive = null,Object? createdAt = freezed,}) {
  return _then(_MerchantModel(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,businessName: null == businessName ? _self.businessName : businessName // ignore: cast_nullable_to_non_nullable
as String,legalName: null == legalName ? _self.legalName : legalName // ignore: cast_nullable_to_non_nullable
as String,email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,phone: null == phone ? _self.phone : phone // ignore: cast_nullable_to_non_nullable
as String,kycStatus: null == kycStatus ? _self.kycStatus : kycStatus // ignore: cast_nullable_to_non_nullable
as KycStatus,riskTier: null == riskTier ? _self.riskTier : riskTier // ignore: cast_nullable_to_non_nullable
as RiskTier,upiVpa: freezed == upiVpa ? _self.upiVpa : upiVpa // ignore: cast_nullable_to_non_nullable
as String?,mccCode: freezed == mccCode ? _self.mccCode : mccCode // ignore: cast_nullable_to_non_nullable
as String?,isActive: null == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$CreateMerchantRequest {

@JsonKey(name: 'business_name') String get businessName;@JsonKey(name: 'legal_name') String get legalName; String get email; String get phone;@JsonKey(name: 'upi_vpa') String? get upiVpa;@JsonKey(name: 'mcc_code') String? get mccCode;
/// Create a copy of CreateMerchantRequest
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CreateMerchantRequestCopyWith<CreateMerchantRequest> get copyWith => _$CreateMerchantRequestCopyWithImpl<CreateMerchantRequest>(this as CreateMerchantRequest, _$identity);

  /// Serializes this CreateMerchantRequest to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as CreateMerchantRequest;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CreateMerchantRequest&&(identical(other.businessName, _this.businessName) || other.businessName == _this.businessName)&&(identical(other.legalName, _this.legalName) || other.legalName == _this.legalName)&&(identical(other.email, _this.email) || other.email == _this.email)&&(identical(other.phone, _this.phone) || other.phone == _this.phone)&&(identical(other.upiVpa, _this.upiVpa) || other.upiVpa == _this.upiVpa)&&(identical(other.mccCode, _this.mccCode) || other.mccCode == _this.mccCode));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as CreateMerchantRequest;
  return Object.hash(runtimeType,_this.businessName,_this.legalName,_this.email,_this.phone,_this.upiVpa,_this.mccCode);
}

@override
String toString() {
  final _this = this as CreateMerchantRequest;
  return 'CreateMerchantRequest(businessName: ${_this.businessName}, legalName: ${_this.legalName}, email: ${_this.email}, phone: ${_this.phone}, upiVpa: ${_this.upiVpa}, mccCode: ${_this.mccCode})';
}


}

/// @nodoc
abstract mixin class $CreateMerchantRequestCopyWith<$Res>  {
  factory $CreateMerchantRequestCopyWith(CreateMerchantRequest value, $Res Function(CreateMerchantRequest) _then) = _$CreateMerchantRequestCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'business_name') String businessName,@JsonKey(name: 'legal_name') String legalName, String email, String phone,@JsonKey(name: 'upi_vpa') String? upiVpa,@JsonKey(name: 'mcc_code') String? mccCode
});




}
/// @nodoc
class _$CreateMerchantRequestCopyWithImpl<$Res>
    implements $CreateMerchantRequestCopyWith<$Res> {
  _$CreateMerchantRequestCopyWithImpl(this._self, this._then);

  final CreateMerchantRequest _self;
  final $Res Function(CreateMerchantRequest) _then;

/// Create a copy of CreateMerchantRequest
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? businessName = null,Object? legalName = null,Object? email = null,Object? phone = null,Object? upiVpa = freezed,Object? mccCode = freezed,}) {
  return _then(CreateMerchantRequest(
businessName: null == businessName ? _self.businessName : businessName // ignore: cast_nullable_to_non_nullable
as String,legalName: null == legalName ? _self.legalName : legalName // ignore: cast_nullable_to_non_nullable
as String,email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,phone: null == phone ? _self.phone : phone // ignore: cast_nullable_to_non_nullable
as String,upiVpa: freezed == upiVpa ? _self.upiVpa : upiVpa // ignore: cast_nullable_to_non_nullable
as String?,mccCode: freezed == mccCode ? _self.mccCode : mccCode // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [CreateMerchantRequest].
extension CreateMerchantRequestPatterns on CreateMerchantRequest {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CreateMerchantRequest value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CreateMerchantRequest() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CreateMerchantRequest value)  $default,){
final _that = this;
switch (_that) {
case _CreateMerchantRequest():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CreateMerchantRequest value)?  $default,){
final _that = this;
switch (_that) {
case _CreateMerchantRequest() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'business_name')  String businessName, @JsonKey(name: 'legal_name')  String legalName,  String email,  String phone, @JsonKey(name: 'upi_vpa')  String? upiVpa, @JsonKey(name: 'mcc_code')  String? mccCode)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CreateMerchantRequest() when $default != null:
return $default(_that.businessName,_that.legalName,_that.email,_that.phone,_that.upiVpa,_that.mccCode);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'business_name')  String businessName, @JsonKey(name: 'legal_name')  String legalName,  String email,  String phone, @JsonKey(name: 'upi_vpa')  String? upiVpa, @JsonKey(name: 'mcc_code')  String? mccCode)  $default,) {final _that = this;
switch (_that) {
case _CreateMerchantRequest():
return $default(_that.businessName,_that.legalName,_that.email,_that.phone,_that.upiVpa,_that.mccCode);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'business_name')  String businessName, @JsonKey(name: 'legal_name')  String legalName,  String email,  String phone, @JsonKey(name: 'upi_vpa')  String? upiVpa, @JsonKey(name: 'mcc_code')  String? mccCode)?  $default,) {final _that = this;
switch (_that) {
case _CreateMerchantRequest() when $default != null:
return $default(_that.businessName,_that.legalName,_that.email,_that.phone,_that.upiVpa,_that.mccCode);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CreateMerchantRequest implements CreateMerchantRequest {
  const _CreateMerchantRequest({@JsonKey(name: 'business_name') required this.businessName, @JsonKey(name: 'legal_name') required this.legalName, required this.email, required this.phone, @JsonKey(name: 'upi_vpa') this.upiVpa, @JsonKey(name: 'mcc_code') this.mccCode});
  factory _CreateMerchantRequest.fromJson(Map<String, dynamic> json) => _$CreateMerchantRequestFromJson(json);

@override@JsonKey(name: 'business_name') final  String businessName;
@override@JsonKey(name: 'legal_name') final  String legalName;
@override final  String email;
@override final  String phone;
@override@JsonKey(name: 'upi_vpa') final  String? upiVpa;
@override@JsonKey(name: 'mcc_code') final  String? mccCode;

/// Create a copy of CreateMerchantRequest
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CreateMerchantRequestCopyWith<_CreateMerchantRequest> get copyWith => __$CreateMerchantRequestCopyWithImpl<_CreateMerchantRequest>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CreateMerchantRequestToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _CreateMerchantRequest&&(identical(other.businessName, businessName) || other.businessName == businessName)&&(identical(other.legalName, legalName) || other.legalName == legalName)&&(identical(other.email, email) || other.email == email)&&(identical(other.phone, phone) || other.phone == phone)&&(identical(other.upiVpa, upiVpa) || other.upiVpa == upiVpa)&&(identical(other.mccCode, mccCode) || other.mccCode == mccCode));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,businessName,legalName,email,phone,upiVpa,mccCode);
}

@override
String toString() {
    return 'CreateMerchantRequest(businessName: $businessName, legalName: $legalName, email: $email, phone: $phone, upiVpa: $upiVpa, mccCode: $mccCode)';
}


}

/// @nodoc
abstract mixin class _$CreateMerchantRequestCopyWith<$Res> implements $CreateMerchantRequestCopyWith<$Res> {
  factory _$CreateMerchantRequestCopyWith(_CreateMerchantRequest value, $Res Function(_CreateMerchantRequest) _then) = __$CreateMerchantRequestCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'business_name') String businessName,@JsonKey(name: 'legal_name') String legalName, String email, String phone,@JsonKey(name: 'upi_vpa') String? upiVpa,@JsonKey(name: 'mcc_code') String? mccCode
});




}
/// @nodoc
class __$CreateMerchantRequestCopyWithImpl<$Res>
    implements _$CreateMerchantRequestCopyWith<$Res> {
  __$CreateMerchantRequestCopyWithImpl(this._self, this._then);

  final _CreateMerchantRequest _self;
  final $Res Function(_CreateMerchantRequest) _then;

/// Create a copy of CreateMerchantRequest
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? businessName = null,Object? legalName = null,Object? email = null,Object? phone = null,Object? upiVpa = freezed,Object? mccCode = freezed,}) {
  return _then(_CreateMerchantRequest(
businessName: null == businessName ? _self.businessName : businessName // ignore: cast_nullable_to_non_nullable
as String,legalName: null == legalName ? _self.legalName : legalName // ignore: cast_nullable_to_non_nullable
as String,email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,phone: null == phone ? _self.phone : phone // ignore: cast_nullable_to_non_nullable
as String,upiVpa: freezed == upiVpa ? _self.upiVpa : upiVpa // ignore: cast_nullable_to_non_nullable
as String?,mccCode: freezed == mccCode ? _self.mccCode : mccCode // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$KycDocumentModel {

 String get id;@JsonKey(name: 'merchant_id') String get merchantId;@JsonKey(name: 'document_type') KycDocumentType get documentType;@JsonKey(name: 'document_number') String get documentNumber;@JsonKey(name: 'file_url') String get fileUrl; String get status;
/// Create a copy of KycDocumentModel
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$KycDocumentModelCopyWith<KycDocumentModel> get copyWith => _$KycDocumentModelCopyWithImpl<KycDocumentModel>(this as KycDocumentModel, _$identity);

  /// Serializes this KycDocumentModel to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as KycDocumentModel;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is KycDocumentModel&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.merchantId, _this.merchantId) || other.merchantId == _this.merchantId)&&(identical(other.documentType, _this.documentType) || other.documentType == _this.documentType)&&(identical(other.documentNumber, _this.documentNumber) || other.documentNumber == _this.documentNumber)&&(identical(other.fileUrl, _this.fileUrl) || other.fileUrl == _this.fileUrl)&&(identical(other.status, _this.status) || other.status == _this.status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as KycDocumentModel;
  return Object.hash(runtimeType,_this.id,_this.merchantId,_this.documentType,_this.documentNumber,_this.fileUrl,_this.status);
}

@override
String toString() {
  final _this = this as KycDocumentModel;
  return 'KycDocumentModel(id: ${_this.id}, merchantId: ${_this.merchantId}, documentType: ${_this.documentType}, documentNumber: ${_this.documentNumber}, fileUrl: ${_this.fileUrl}, status: ${_this.status})';
}


}

/// @nodoc
abstract mixin class $KycDocumentModelCopyWith<$Res>  {
  factory $KycDocumentModelCopyWith(KycDocumentModel value, $Res Function(KycDocumentModel) _then) = _$KycDocumentModelCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId,@JsonKey(name: 'document_type') KycDocumentType documentType,@JsonKey(name: 'document_number') String documentNumber,@JsonKey(name: 'file_url') String fileUrl, String status
});




}
/// @nodoc
class _$KycDocumentModelCopyWithImpl<$Res>
    implements $KycDocumentModelCopyWith<$Res> {
  _$KycDocumentModelCopyWithImpl(this._self, this._then);

  final KycDocumentModel _self;
  final $Res Function(KycDocumentModel) _then;

/// Create a copy of KycDocumentModel
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? merchantId = null,Object? documentType = null,Object? documentNumber = null,Object? fileUrl = null,Object? status = null,}) {
  return _then(KycDocumentModel(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,documentType: null == documentType ? _self.documentType : documentType // ignore: cast_nullable_to_non_nullable
as KycDocumentType,documentNumber: null == documentNumber ? _self.documentNumber : documentNumber // ignore: cast_nullable_to_non_nullable
as String,fileUrl: null == fileUrl ? _self.fileUrl : fileUrl // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [KycDocumentModel].
extension KycDocumentModelPatterns on KycDocumentModel {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _KycDocumentModel value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _KycDocumentModel() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _KycDocumentModel value)  $default,){
final _that = this;
switch (_that) {
case _KycDocumentModel():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _KycDocumentModel value)?  $default,){
final _that = this;
switch (_that) {
case _KycDocumentModel() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'document_type')  KycDocumentType documentType, @JsonKey(name: 'document_number')  String documentNumber, @JsonKey(name: 'file_url')  String fileUrl,  String status)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _KycDocumentModel() when $default != null:
return $default(_that.id,_that.merchantId,_that.documentType,_that.documentNumber,_that.fileUrl,_that.status);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'document_type')  KycDocumentType documentType, @JsonKey(name: 'document_number')  String documentNumber, @JsonKey(name: 'file_url')  String fileUrl,  String status)  $default,) {final _that = this;
switch (_that) {
case _KycDocumentModel():
return $default(_that.id,_that.merchantId,_that.documentType,_that.documentNumber,_that.fileUrl,_that.status);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'document_type')  KycDocumentType documentType, @JsonKey(name: 'document_number')  String documentNumber, @JsonKey(name: 'file_url')  String fileUrl,  String status)?  $default,) {final _that = this;
switch (_that) {
case _KycDocumentModel() when $default != null:
return $default(_that.id,_that.merchantId,_that.documentType,_that.documentNumber,_that.fileUrl,_that.status);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _KycDocumentModel implements KycDocumentModel {
  const _KycDocumentModel({required this.id, @JsonKey(name: 'merchant_id') required this.merchantId, @JsonKey(name: 'document_type') required this.documentType, @JsonKey(name: 'document_number') required this.documentNumber, @JsonKey(name: 'file_url') required this.fileUrl, this.status = 'SUBMITTED'});
  factory _KycDocumentModel.fromJson(Map<String, dynamic> json) => _$KycDocumentModelFromJson(json);

@override final  String id;
@override@JsonKey(name: 'merchant_id') final  String merchantId;
@override@JsonKey(name: 'document_type') final  KycDocumentType documentType;
@override@JsonKey(name: 'document_number') final  String documentNumber;
@override@JsonKey(name: 'file_url') final  String fileUrl;
@override@JsonKey() final  String status;

/// Create a copy of KycDocumentModel
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$KycDocumentModelCopyWith<_KycDocumentModel> get copyWith => __$KycDocumentModelCopyWithImpl<_KycDocumentModel>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$KycDocumentModelToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _KycDocumentModel&&(identical(other.id, id) || other.id == id)&&(identical(other.merchantId, merchantId) || other.merchantId == merchantId)&&(identical(other.documentType, documentType) || other.documentType == documentType)&&(identical(other.documentNumber, documentNumber) || other.documentNumber == documentNumber)&&(identical(other.fileUrl, fileUrl) || other.fileUrl == fileUrl)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,merchantId,documentType,documentNumber,fileUrl,status);
}

@override
String toString() {
    return 'KycDocumentModel(id: $id, merchantId: $merchantId, documentType: $documentType, documentNumber: $documentNumber, fileUrl: $fileUrl, status: $status)';
}


}

/// @nodoc
abstract mixin class _$KycDocumentModelCopyWith<$Res> implements $KycDocumentModelCopyWith<$Res> {
  factory _$KycDocumentModelCopyWith(_KycDocumentModel value, $Res Function(_KycDocumentModel) _then) = __$KycDocumentModelCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId,@JsonKey(name: 'document_type') KycDocumentType documentType,@JsonKey(name: 'document_number') String documentNumber,@JsonKey(name: 'file_url') String fileUrl, String status
});




}
/// @nodoc
class __$KycDocumentModelCopyWithImpl<$Res>
    implements _$KycDocumentModelCopyWith<$Res> {
  __$KycDocumentModelCopyWithImpl(this._self, this._then);

  final _KycDocumentModel _self;
  final $Res Function(_KycDocumentModel) _then;

/// Create a copy of KycDocumentModel
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? merchantId = null,Object? documentType = null,Object? documentNumber = null,Object? fileUrl = null,Object? status = null,}) {
  return _then(_KycDocumentModel(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,documentType: null == documentType ? _self.documentType : documentType // ignore: cast_nullable_to_non_nullable
as KycDocumentType,documentNumber: null == documentNumber ? _self.documentNumber : documentNumber // ignore: cast_nullable_to_non_nullable
as String,fileUrl: null == fileUrl ? _self.fileUrl : fileUrl // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
