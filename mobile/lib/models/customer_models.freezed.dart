// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'customer_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$Customer {

 String get id;@JsonKey(name: 'merchant_id') String get merchantId; String get name; String? get email; String get phone;@JsonKey(name: 'upi_vpa') String? get upiVpa;@JsonKey(name: 'created_at') String? get createdAt;
/// Create a copy of Customer
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CustomerCopyWith<Customer> get copyWith => _$CustomerCopyWithImpl<Customer>(this as Customer, _$identity);

  /// Serializes this Customer to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Customer;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Customer&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.merchantId, _this.merchantId) || other.merchantId == _this.merchantId)&&(identical(other.name, _this.name) || other.name == _this.name)&&(identical(other.email, _this.email) || other.email == _this.email)&&(identical(other.phone, _this.phone) || other.phone == _this.phone)&&(identical(other.upiVpa, _this.upiVpa) || other.upiVpa == _this.upiVpa)&&(identical(other.createdAt, _this.createdAt) || other.createdAt == _this.createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Customer;
  return Object.hash(runtimeType,_this.id,_this.merchantId,_this.name,_this.email,_this.phone,_this.upiVpa,_this.createdAt);
}

@override
String toString() {
  final _this = this as Customer;
  return 'Customer(id: ${_this.id}, merchantId: ${_this.merchantId}, name: ${_this.name}, email: ${_this.email}, phone: ${_this.phone}, upiVpa: ${_this.upiVpa}, createdAt: ${_this.createdAt})';
}


}

/// @nodoc
abstract mixin class $CustomerCopyWith<$Res>  {
  factory $CustomerCopyWith(Customer value, $Res Function(Customer) _then) = _$CustomerCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId, String name, String? email, String phone,@JsonKey(name: 'upi_vpa') String? upiVpa,@JsonKey(name: 'created_at') String? createdAt
});




}
/// @nodoc
class _$CustomerCopyWithImpl<$Res>
    implements $CustomerCopyWith<$Res> {
  _$CustomerCopyWithImpl(this._self, this._then);

  final Customer _self;
  final $Res Function(Customer) _then;

/// Create a copy of Customer
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? merchantId = null,Object? name = null,Object? email = freezed,Object? phone = null,Object? upiVpa = freezed,Object? createdAt = freezed,}) {
  return _then(Customer(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,email: freezed == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String?,phone: null == phone ? _self.phone : phone // ignore: cast_nullable_to_non_nullable
as String,upiVpa: freezed == upiVpa ? _self.upiVpa : upiVpa // ignore: cast_nullable_to_non_nullable
as String?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [Customer].
extension CustomerPatterns on Customer {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Customer value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Customer() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Customer value)  $default,){
final _that = this;
switch (_that) {
case _Customer():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Customer value)?  $default,){
final _that = this;
switch (_that) {
case _Customer() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId,  String name,  String? email,  String phone, @JsonKey(name: 'upi_vpa')  String? upiVpa, @JsonKey(name: 'created_at')  String? createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Customer() when $default != null:
return $default(_that.id,_that.merchantId,_that.name,_that.email,_that.phone,_that.upiVpa,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId,  String name,  String? email,  String phone, @JsonKey(name: 'upi_vpa')  String? upiVpa, @JsonKey(name: 'created_at')  String? createdAt)  $default,) {final _that = this;
switch (_that) {
case _Customer():
return $default(_that.id,_that.merchantId,_that.name,_that.email,_that.phone,_that.upiVpa,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'merchant_id')  String merchantId,  String name,  String? email,  String phone, @JsonKey(name: 'upi_vpa')  String? upiVpa, @JsonKey(name: 'created_at')  String? createdAt)?  $default,) {final _that = this;
switch (_that) {
case _Customer() when $default != null:
return $default(_that.id,_that.merchantId,_that.name,_that.email,_that.phone,_that.upiVpa,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Customer implements Customer {
  const _Customer({required this.id, @JsonKey(name: 'merchant_id') required this.merchantId, required this.name, this.email, required this.phone, @JsonKey(name: 'upi_vpa') this.upiVpa, @JsonKey(name: 'created_at') this.createdAt});
  factory _Customer.fromJson(Map<String, dynamic> json) => _$CustomerFromJson(json);

@override final  String id;
@override@JsonKey(name: 'merchant_id') final  String merchantId;
@override final  String name;
@override final  String? email;
@override final  String phone;
@override@JsonKey(name: 'upi_vpa') final  String? upiVpa;
@override@JsonKey(name: 'created_at') final  String? createdAt;

/// Create a copy of Customer
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CustomerCopyWith<_Customer> get copyWith => __$CustomerCopyWithImpl<_Customer>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CustomerToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Customer&&(identical(other.id, id) || other.id == id)&&(identical(other.merchantId, merchantId) || other.merchantId == merchantId)&&(identical(other.name, name) || other.name == name)&&(identical(other.email, email) || other.email == email)&&(identical(other.phone, phone) || other.phone == phone)&&(identical(other.upiVpa, upiVpa) || other.upiVpa == upiVpa)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,merchantId,name,email,phone,upiVpa,createdAt);
}

@override
String toString() {
    return 'Customer(id: $id, merchantId: $merchantId, name: $name, email: $email, phone: $phone, upiVpa: $upiVpa, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$CustomerCopyWith<$Res> implements $CustomerCopyWith<$Res> {
  factory _$CustomerCopyWith(_Customer value, $Res Function(_Customer) _then) = __$CustomerCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId, String name, String? email, String phone,@JsonKey(name: 'upi_vpa') String? upiVpa,@JsonKey(name: 'created_at') String? createdAt
});




}
/// @nodoc
class __$CustomerCopyWithImpl<$Res>
    implements _$CustomerCopyWith<$Res> {
  __$CustomerCopyWithImpl(this._self, this._then);

  final _Customer _self;
  final $Res Function(_Customer) _then;

/// Create a copy of Customer
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? merchantId = null,Object? name = null,Object? email = freezed,Object? phone = null,Object? upiVpa = freezed,Object? createdAt = freezed,}) {
  return _then(_Customer(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,email: freezed == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String?,phone: null == phone ? _self.phone : phone // ignore: cast_nullable_to_non_nullable
as String,upiVpa: freezed == upiVpa ? _self.upiVpa : upiVpa // ignore: cast_nullable_to_non_nullable
as String?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$CreateCustomerRequest {

 String get name; String get phone; String? get email;@JsonKey(name: 'upi_vpa') String? get upiVpa;
/// Create a copy of CreateCustomerRequest
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CreateCustomerRequestCopyWith<CreateCustomerRequest> get copyWith => _$CreateCustomerRequestCopyWithImpl<CreateCustomerRequest>(this as CreateCustomerRequest, _$identity);

  /// Serializes this CreateCustomerRequest to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as CreateCustomerRequest;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CreateCustomerRequest&&(identical(other.name, _this.name) || other.name == _this.name)&&(identical(other.phone, _this.phone) || other.phone == _this.phone)&&(identical(other.email, _this.email) || other.email == _this.email)&&(identical(other.upiVpa, _this.upiVpa) || other.upiVpa == _this.upiVpa));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as CreateCustomerRequest;
  return Object.hash(runtimeType,_this.name,_this.phone,_this.email,_this.upiVpa);
}

@override
String toString() {
  final _this = this as CreateCustomerRequest;
  return 'CreateCustomerRequest(name: ${_this.name}, phone: ${_this.phone}, email: ${_this.email}, upiVpa: ${_this.upiVpa})';
}


}

/// @nodoc
abstract mixin class $CreateCustomerRequestCopyWith<$Res>  {
  factory $CreateCustomerRequestCopyWith(CreateCustomerRequest value, $Res Function(CreateCustomerRequest) _then) = _$CreateCustomerRequestCopyWithImpl;
@useResult
$Res call({
 String name, String phone, String? email,@JsonKey(name: 'upi_vpa') String? upiVpa
});




}
/// @nodoc
class _$CreateCustomerRequestCopyWithImpl<$Res>
    implements $CreateCustomerRequestCopyWith<$Res> {
  _$CreateCustomerRequestCopyWithImpl(this._self, this._then);

  final CreateCustomerRequest _self;
  final $Res Function(CreateCustomerRequest) _then;

/// Create a copy of CreateCustomerRequest
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? phone = null,Object? email = freezed,Object? upiVpa = freezed,}) {
  return _then(CreateCustomerRequest(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,phone: null == phone ? _self.phone : phone // ignore: cast_nullable_to_non_nullable
as String,email: freezed == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String?,upiVpa: freezed == upiVpa ? _self.upiVpa : upiVpa // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [CreateCustomerRequest].
extension CreateCustomerRequestPatterns on CreateCustomerRequest {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CreateCustomerRequest value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CreateCustomerRequest() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CreateCustomerRequest value)  $default,){
final _that = this;
switch (_that) {
case _CreateCustomerRequest():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CreateCustomerRequest value)?  $default,){
final _that = this;
switch (_that) {
case _CreateCustomerRequest() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String name,  String phone,  String? email, @JsonKey(name: 'upi_vpa')  String? upiVpa)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CreateCustomerRequest() when $default != null:
return $default(_that.name,_that.phone,_that.email,_that.upiVpa);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String name,  String phone,  String? email, @JsonKey(name: 'upi_vpa')  String? upiVpa)  $default,) {final _that = this;
switch (_that) {
case _CreateCustomerRequest():
return $default(_that.name,_that.phone,_that.email,_that.upiVpa);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String name,  String phone,  String? email, @JsonKey(name: 'upi_vpa')  String? upiVpa)?  $default,) {final _that = this;
switch (_that) {
case _CreateCustomerRequest() when $default != null:
return $default(_that.name,_that.phone,_that.email,_that.upiVpa);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CreateCustomerRequest implements CreateCustomerRequest {
  const _CreateCustomerRequest({required this.name, required this.phone, this.email, @JsonKey(name: 'upi_vpa') this.upiVpa});
  factory _CreateCustomerRequest.fromJson(Map<String, dynamic> json) => _$CreateCustomerRequestFromJson(json);

@override final  String name;
@override final  String phone;
@override final  String? email;
@override@JsonKey(name: 'upi_vpa') final  String? upiVpa;

/// Create a copy of CreateCustomerRequest
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CreateCustomerRequestCopyWith<_CreateCustomerRequest> get copyWith => __$CreateCustomerRequestCopyWithImpl<_CreateCustomerRequest>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CreateCustomerRequestToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _CreateCustomerRequest&&(identical(other.name, name) || other.name == name)&&(identical(other.phone, phone) || other.phone == phone)&&(identical(other.email, email) || other.email == email)&&(identical(other.upiVpa, upiVpa) || other.upiVpa == upiVpa));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,name,phone,email,upiVpa);
}

@override
String toString() {
    return 'CreateCustomerRequest(name: $name, phone: $phone, email: $email, upiVpa: $upiVpa)';
}


}

/// @nodoc
abstract mixin class _$CreateCustomerRequestCopyWith<$Res> implements $CreateCustomerRequestCopyWith<$Res> {
  factory _$CreateCustomerRequestCopyWith(_CreateCustomerRequest value, $Res Function(_CreateCustomerRequest) _then) = __$CreateCustomerRequestCopyWithImpl;
@override @useResult
$Res call({
 String name, String phone, String? email,@JsonKey(name: 'upi_vpa') String? upiVpa
});




}
/// @nodoc
class __$CreateCustomerRequestCopyWithImpl<$Res>
    implements _$CreateCustomerRequestCopyWith<$Res> {
  __$CreateCustomerRequestCopyWithImpl(this._self, this._then);

  final _CreateCustomerRequest _self;
  final $Res Function(_CreateCustomerRequest) _then;

/// Create a copy of CreateCustomerRequest
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? phone = null,Object? email = freezed,Object? upiVpa = freezed,}) {
  return _then(_CreateCustomerRequest(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,phone: null == phone ? _self.phone : phone // ignore: cast_nullable_to_non_nullable
as String,email: freezed == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String?,upiVpa: freezed == upiVpa ? _self.upiVpa : upiVpa // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
