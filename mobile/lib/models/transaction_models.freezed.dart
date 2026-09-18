// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'transaction_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$TransactionStatusHistory {

 String get id;@JsonKey(name: 'from_status') String? get fromStatus;@JsonKey(name: 'to_status') String get toStatus; String? get reason;@JsonKey(name: 'created_at') String get createdAt;
/// Create a copy of TransactionStatusHistory
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TransactionStatusHistoryCopyWith<TransactionStatusHistory> get copyWith => _$TransactionStatusHistoryCopyWithImpl<TransactionStatusHistory>(this as TransactionStatusHistory, _$identity);

  /// Serializes this TransactionStatusHistory to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as TransactionStatusHistory;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is TransactionStatusHistory&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.fromStatus, _this.fromStatus) || other.fromStatus == _this.fromStatus)&&(identical(other.toStatus, _this.toStatus) || other.toStatus == _this.toStatus)&&(identical(other.reason, _this.reason) || other.reason == _this.reason)&&(identical(other.createdAt, _this.createdAt) || other.createdAt == _this.createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as TransactionStatusHistory;
  return Object.hash(runtimeType,_this.id,_this.fromStatus,_this.toStatus,_this.reason,_this.createdAt);
}

@override
String toString() {
  final _this = this as TransactionStatusHistory;
  return 'TransactionStatusHistory(id: ${_this.id}, fromStatus: ${_this.fromStatus}, toStatus: ${_this.toStatus}, reason: ${_this.reason}, createdAt: ${_this.createdAt})';
}


}

/// @nodoc
abstract mixin class $TransactionStatusHistoryCopyWith<$Res>  {
  factory $TransactionStatusHistoryCopyWith(TransactionStatusHistory value, $Res Function(TransactionStatusHistory) _then) = _$TransactionStatusHistoryCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'from_status') String? fromStatus,@JsonKey(name: 'to_status') String toStatus, String? reason,@JsonKey(name: 'created_at') String createdAt
});




}
/// @nodoc
class _$TransactionStatusHistoryCopyWithImpl<$Res>
    implements $TransactionStatusHistoryCopyWith<$Res> {
  _$TransactionStatusHistoryCopyWithImpl(this._self, this._then);

  final TransactionStatusHistory _self;
  final $Res Function(TransactionStatusHistory) _then;

/// Create a copy of TransactionStatusHistory
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? fromStatus = freezed,Object? toStatus = null,Object? reason = freezed,Object? createdAt = null,}) {
  return _then(TransactionStatusHistory(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,fromStatus: freezed == fromStatus ? _self.fromStatus : fromStatus // ignore: cast_nullable_to_non_nullable
as String?,toStatus: null == toStatus ? _self.toStatus : toStatus // ignore: cast_nullable_to_non_nullable
as String,reason: freezed == reason ? _self.reason : reason // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [TransactionStatusHistory].
extension TransactionStatusHistoryPatterns on TransactionStatusHistory {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TransactionStatusHistory value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TransactionStatusHistory() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TransactionStatusHistory value)  $default,){
final _that = this;
switch (_that) {
case _TransactionStatusHistory():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TransactionStatusHistory value)?  $default,){
final _that = this;
switch (_that) {
case _TransactionStatusHistory() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'from_status')  String? fromStatus, @JsonKey(name: 'to_status')  String toStatus,  String? reason, @JsonKey(name: 'created_at')  String createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TransactionStatusHistory() when $default != null:
return $default(_that.id,_that.fromStatus,_that.toStatus,_that.reason,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'from_status')  String? fromStatus, @JsonKey(name: 'to_status')  String toStatus,  String? reason, @JsonKey(name: 'created_at')  String createdAt)  $default,) {final _that = this;
switch (_that) {
case _TransactionStatusHistory():
return $default(_that.id,_that.fromStatus,_that.toStatus,_that.reason,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'from_status')  String? fromStatus, @JsonKey(name: 'to_status')  String toStatus,  String? reason, @JsonKey(name: 'created_at')  String createdAt)?  $default,) {final _that = this;
switch (_that) {
case _TransactionStatusHistory() when $default != null:
return $default(_that.id,_that.fromStatus,_that.toStatus,_that.reason,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _TransactionStatusHistory implements TransactionStatusHistory {
  const _TransactionStatusHistory({required this.id, @JsonKey(name: 'from_status') this.fromStatus, @JsonKey(name: 'to_status') required this.toStatus, this.reason, @JsonKey(name: 'created_at') required this.createdAt});
  factory _TransactionStatusHistory.fromJson(Map<String, dynamic> json) => _$TransactionStatusHistoryFromJson(json);

@override final  String id;
@override@JsonKey(name: 'from_status') final  String? fromStatus;
@override@JsonKey(name: 'to_status') final  String toStatus;
@override final  String? reason;
@override@JsonKey(name: 'created_at') final  String createdAt;

/// Create a copy of TransactionStatusHistory
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TransactionStatusHistoryCopyWith<_TransactionStatusHistory> get copyWith => __$TransactionStatusHistoryCopyWithImpl<_TransactionStatusHistory>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TransactionStatusHistoryToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _TransactionStatusHistory&&(identical(other.id, id) || other.id == id)&&(identical(other.fromStatus, fromStatus) || other.fromStatus == fromStatus)&&(identical(other.toStatus, toStatus) || other.toStatus == toStatus)&&(identical(other.reason, reason) || other.reason == reason)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,fromStatus,toStatus,reason,createdAt);
}

@override
String toString() {
    return 'TransactionStatusHistory(id: $id, fromStatus: $fromStatus, toStatus: $toStatus, reason: $reason, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$TransactionStatusHistoryCopyWith<$Res> implements $TransactionStatusHistoryCopyWith<$Res> {
  factory _$TransactionStatusHistoryCopyWith(_TransactionStatusHistory value, $Res Function(_TransactionStatusHistory) _then) = __$TransactionStatusHistoryCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'from_status') String? fromStatus,@JsonKey(name: 'to_status') String toStatus, String? reason,@JsonKey(name: 'created_at') String createdAt
});




}
/// @nodoc
class __$TransactionStatusHistoryCopyWithImpl<$Res>
    implements _$TransactionStatusHistoryCopyWith<$Res> {
  __$TransactionStatusHistoryCopyWithImpl(this._self, this._then);

  final _TransactionStatusHistory _self;
  final $Res Function(_TransactionStatusHistory) _then;

/// Create a copy of TransactionStatusHistory
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? fromStatus = freezed,Object? toStatus = null,Object? reason = freezed,Object? createdAt = null,}) {
  return _then(_TransactionStatusHistory(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,fromStatus: freezed == fromStatus ? _self.fromStatus : fromStatus // ignore: cast_nullable_to_non_nullable
as String?,toStatus: null == toStatus ? _self.toStatus : toStatus // ignore: cast_nullable_to_non_nullable
as String,reason: freezed == reason ? _self.reason : reason // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$DuplicateFlag {

 String get id;@JsonKey(name: 'flag_reason') String get flagReason;@JsonKey(name: 'confidence_score') double get confidenceScore; String get status;@JsonKey(name: 'match_reason') String? get matchReason;
/// Create a copy of DuplicateFlag
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DuplicateFlagCopyWith<DuplicateFlag> get copyWith => _$DuplicateFlagCopyWithImpl<DuplicateFlag>(this as DuplicateFlag, _$identity);

  /// Serializes this DuplicateFlag to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as DuplicateFlag;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DuplicateFlag&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.flagReason, _this.flagReason) || other.flagReason == _this.flagReason)&&(identical(other.confidenceScore, _this.confidenceScore) || other.confidenceScore == _this.confidenceScore)&&(identical(other.status, _this.status) || other.status == _this.status)&&(identical(other.matchReason, _this.matchReason) || other.matchReason == _this.matchReason));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as DuplicateFlag;
  return Object.hash(runtimeType,_this.id,_this.flagReason,_this.confidenceScore,_this.status,_this.matchReason);
}

@override
String toString() {
  final _this = this as DuplicateFlag;
  return 'DuplicateFlag(id: ${_this.id}, flagReason: ${_this.flagReason}, confidenceScore: ${_this.confidenceScore}, status: ${_this.status}, matchReason: ${_this.matchReason})';
}


}

/// @nodoc
abstract mixin class $DuplicateFlagCopyWith<$Res>  {
  factory $DuplicateFlagCopyWith(DuplicateFlag value, $Res Function(DuplicateFlag) _then) = _$DuplicateFlagCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'flag_reason') String flagReason,@JsonKey(name: 'confidence_score') double confidenceScore, String status,@JsonKey(name: 'match_reason') String? matchReason
});




}
/// @nodoc
class _$DuplicateFlagCopyWithImpl<$Res>
    implements $DuplicateFlagCopyWith<$Res> {
  _$DuplicateFlagCopyWithImpl(this._self, this._then);

  final DuplicateFlag _self;
  final $Res Function(DuplicateFlag) _then;

/// Create a copy of DuplicateFlag
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? flagReason = null,Object? confidenceScore = null,Object? status = null,Object? matchReason = freezed,}) {
  return _then(DuplicateFlag(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,flagReason: null == flagReason ? _self.flagReason : flagReason // ignore: cast_nullable_to_non_nullable
as String,confidenceScore: null == confidenceScore ? _self.confidenceScore : confidenceScore // ignore: cast_nullable_to_non_nullable
as double,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,matchReason: freezed == matchReason ? _self.matchReason : matchReason // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [DuplicateFlag].
extension DuplicateFlagPatterns on DuplicateFlag {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _DuplicateFlag value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _DuplicateFlag() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _DuplicateFlag value)  $default,){
final _that = this;
switch (_that) {
case _DuplicateFlag():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _DuplicateFlag value)?  $default,){
final _that = this;
switch (_that) {
case _DuplicateFlag() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'flag_reason')  String flagReason, @JsonKey(name: 'confidence_score')  double confidenceScore,  String status, @JsonKey(name: 'match_reason')  String? matchReason)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _DuplicateFlag() when $default != null:
return $default(_that.id,_that.flagReason,_that.confidenceScore,_that.status,_that.matchReason);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'flag_reason')  String flagReason, @JsonKey(name: 'confidence_score')  double confidenceScore,  String status, @JsonKey(name: 'match_reason')  String? matchReason)  $default,) {final _that = this;
switch (_that) {
case _DuplicateFlag():
return $default(_that.id,_that.flagReason,_that.confidenceScore,_that.status,_that.matchReason);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'flag_reason')  String flagReason, @JsonKey(name: 'confidence_score')  double confidenceScore,  String status, @JsonKey(name: 'match_reason')  String? matchReason)?  $default,) {final _that = this;
switch (_that) {
case _DuplicateFlag() when $default != null:
return $default(_that.id,_that.flagReason,_that.confidenceScore,_that.status,_that.matchReason);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _DuplicateFlag implements DuplicateFlag {
  const _DuplicateFlag({required this.id, @JsonKey(name: 'flag_reason') required this.flagReason, @JsonKey(name: 'confidence_score') required this.confidenceScore, required this.status, @JsonKey(name: 'match_reason') this.matchReason});
  factory _DuplicateFlag.fromJson(Map<String, dynamic> json) => _$DuplicateFlagFromJson(json);

@override final  String id;
@override@JsonKey(name: 'flag_reason') final  String flagReason;
@override@JsonKey(name: 'confidence_score') final  double confidenceScore;
@override final  String status;
@override@JsonKey(name: 'match_reason') final  String? matchReason;

/// Create a copy of DuplicateFlag
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DuplicateFlagCopyWith<_DuplicateFlag> get copyWith => __$DuplicateFlagCopyWithImpl<_DuplicateFlag>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DuplicateFlagToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _DuplicateFlag&&(identical(other.id, id) || other.id == id)&&(identical(other.flagReason, flagReason) || other.flagReason == flagReason)&&(identical(other.confidenceScore, confidenceScore) || other.confidenceScore == confidenceScore)&&(identical(other.status, status) || other.status == status)&&(identical(other.matchReason, matchReason) || other.matchReason == matchReason));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,flagReason,confidenceScore,status,matchReason);
}

@override
String toString() {
    return 'DuplicateFlag(id: $id, flagReason: $flagReason, confidenceScore: $confidenceScore, status: $status, matchReason: $matchReason)';
}


}

/// @nodoc
abstract mixin class _$DuplicateFlagCopyWith<$Res> implements $DuplicateFlagCopyWith<$Res> {
  factory _$DuplicateFlagCopyWith(_DuplicateFlag value, $Res Function(_DuplicateFlag) _then) = __$DuplicateFlagCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'flag_reason') String flagReason,@JsonKey(name: 'confidence_score') double confidenceScore, String status,@JsonKey(name: 'match_reason') String? matchReason
});




}
/// @nodoc
class __$DuplicateFlagCopyWithImpl<$Res>
    implements _$DuplicateFlagCopyWith<$Res> {
  __$DuplicateFlagCopyWithImpl(this._self, this._then);

  final _DuplicateFlag _self;
  final $Res Function(_DuplicateFlag) _then;

/// Create a copy of DuplicateFlag
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? flagReason = null,Object? confidenceScore = null,Object? status = null,Object? matchReason = freezed,}) {
  return _then(_DuplicateFlag(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,flagReason: null == flagReason ? _self.flagReason : flagReason // ignore: cast_nullable_to_non_nullable
as String,confidenceScore: null == confidenceScore ? _self.confidenceScore : confidenceScore // ignore: cast_nullable_to_non_nullable
as double,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,matchReason: freezed == matchReason ? _self.matchReason : matchReason // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$PaymentTransaction {

 String get id;@JsonKey(name: 'merchant_id') String get merchantId;@JsonKey(name: 'invoice_id') String? get invoiceId;@JsonKey(name: 'customer_id') String? get customerId;@JsonKey(name: 'idempotency_key') String get idempotencyKey; String get amount; String get currency; TransactionStatus get status;@JsonKey(name: 'payment_method') PaymentMethod get paymentMethod;@JsonKey(name: 'mock_scenario') String? get mockScenario;@JsonKey(name: 'provider_ref_id') String? get providerRefId;@JsonKey(name: 'payer_vpa') String? get payerVpa;@JsonKey(name: 'failure_reason') String? get failureReason;@JsonKey(name: 'completed_at') String? get completedAt;@JsonKey(name: 'created_at') String get createdAt;@JsonKey(name: 'status_history') List<TransactionStatusHistory> get statusHistory;@JsonKey(name: 'duplicate_flags') List<DuplicateFlag> get duplicateFlags;@JsonKey(name: 'customer_name') String? get customerName;@JsonKey(name: 'invoice_number') String? get invoiceNumber;
/// Create a copy of PaymentTransaction
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PaymentTransactionCopyWith<PaymentTransaction> get copyWith => _$PaymentTransactionCopyWithImpl<PaymentTransaction>(this as PaymentTransaction, _$identity);

  /// Serializes this PaymentTransaction to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as PaymentTransaction;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PaymentTransaction&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.merchantId, _this.merchantId) || other.merchantId == _this.merchantId)&&(identical(other.invoiceId, _this.invoiceId) || other.invoiceId == _this.invoiceId)&&(identical(other.customerId, _this.customerId) || other.customerId == _this.customerId)&&(identical(other.idempotencyKey, _this.idempotencyKey) || other.idempotencyKey == _this.idempotencyKey)&&(identical(other.amount, _this.amount) || other.amount == _this.amount)&&(identical(other.currency, _this.currency) || other.currency == _this.currency)&&(identical(other.status, _this.status) || other.status == _this.status)&&(identical(other.paymentMethod, _this.paymentMethod) || other.paymentMethod == _this.paymentMethod)&&(identical(other.mockScenario, _this.mockScenario) || other.mockScenario == _this.mockScenario)&&(identical(other.providerRefId, _this.providerRefId) || other.providerRefId == _this.providerRefId)&&(identical(other.payerVpa, _this.payerVpa) || other.payerVpa == _this.payerVpa)&&(identical(other.failureReason, _this.failureReason) || other.failureReason == _this.failureReason)&&(identical(other.completedAt, _this.completedAt) || other.completedAt == _this.completedAt)&&(identical(other.createdAt, _this.createdAt) || other.createdAt == _this.createdAt)&&const DeepCollectionEquality().equals(other.statusHistory, _this.statusHistory)&&const DeepCollectionEquality().equals(other.duplicateFlags, _this.duplicateFlags)&&(identical(other.customerName, _this.customerName) || other.customerName == _this.customerName)&&(identical(other.invoiceNumber, _this.invoiceNumber) || other.invoiceNumber == _this.invoiceNumber));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as PaymentTransaction;
  return Object.hashAll([runtimeType,_this.id,_this.merchantId,_this.invoiceId,_this.customerId,_this.idempotencyKey,_this.amount,_this.currency,_this.status,_this.paymentMethod,_this.mockScenario,_this.providerRefId,_this.payerVpa,_this.failureReason,_this.completedAt,_this.createdAt,const DeepCollectionEquality().hash(_this.statusHistory),const DeepCollectionEquality().hash(_this.duplicateFlags),_this.customerName,_this.invoiceNumber]);
}

@override
String toString() {
  final _this = this as PaymentTransaction;
  return 'PaymentTransaction(id: ${_this.id}, merchantId: ${_this.merchantId}, invoiceId: ${_this.invoiceId}, customerId: ${_this.customerId}, idempotencyKey: ${_this.idempotencyKey}, amount: ${_this.amount}, currency: ${_this.currency}, status: ${_this.status}, paymentMethod: ${_this.paymentMethod}, mockScenario: ${_this.mockScenario}, providerRefId: ${_this.providerRefId}, payerVpa: ${_this.payerVpa}, failureReason: ${_this.failureReason}, completedAt: ${_this.completedAt}, createdAt: ${_this.createdAt}, statusHistory: ${_this.statusHistory}, duplicateFlags: ${_this.duplicateFlags}, customerName: ${_this.customerName}, invoiceNumber: ${_this.invoiceNumber})';
}


}

/// @nodoc
abstract mixin class $PaymentTransactionCopyWith<$Res>  {
  factory $PaymentTransactionCopyWith(PaymentTransaction value, $Res Function(PaymentTransaction) _then) = _$PaymentTransactionCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId,@JsonKey(name: 'invoice_id') String? invoiceId,@JsonKey(name: 'customer_id') String? customerId,@JsonKey(name: 'idempotency_key') String idempotencyKey, String amount, String currency, TransactionStatus status,@JsonKey(name: 'payment_method') PaymentMethod paymentMethod,@JsonKey(name: 'mock_scenario') String? mockScenario,@JsonKey(name: 'provider_ref_id') String? providerRefId,@JsonKey(name: 'payer_vpa') String? payerVpa,@JsonKey(name: 'failure_reason') String? failureReason,@JsonKey(name: 'completed_at') String? completedAt,@JsonKey(name: 'created_at') String createdAt,@JsonKey(name: 'status_history') List<TransactionStatusHistory> statusHistory,@JsonKey(name: 'duplicate_flags') List<DuplicateFlag> duplicateFlags,@JsonKey(name: 'customer_name') String? customerName,@JsonKey(name: 'invoice_number') String? invoiceNumber
});




}
/// @nodoc
class _$PaymentTransactionCopyWithImpl<$Res>
    implements $PaymentTransactionCopyWith<$Res> {
  _$PaymentTransactionCopyWithImpl(this._self, this._then);

  final PaymentTransaction _self;
  final $Res Function(PaymentTransaction) _then;

/// Create a copy of PaymentTransaction
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? merchantId = null,Object? invoiceId = freezed,Object? customerId = freezed,Object? idempotencyKey = null,Object? amount = null,Object? currency = null,Object? status = null,Object? paymentMethod = null,Object? mockScenario = freezed,Object? providerRefId = freezed,Object? payerVpa = freezed,Object? failureReason = freezed,Object? completedAt = freezed,Object? createdAt = null,Object? statusHistory = null,Object? duplicateFlags = null,Object? customerName = freezed,Object? invoiceNumber = freezed,}) {
  return _then(PaymentTransaction(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,invoiceId: freezed == invoiceId ? _self.invoiceId : invoiceId // ignore: cast_nullable_to_non_nullable
as String?,customerId: freezed == customerId ? _self.customerId : customerId // ignore: cast_nullable_to_non_nullable
as String?,idempotencyKey: null == idempotencyKey ? _self.idempotencyKey : idempotencyKey // ignore: cast_nullable_to_non_nullable
as String,amount: null == amount ? _self.amount : amount // ignore: cast_nullable_to_non_nullable
as String,currency: null == currency ? _self.currency : currency // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as TransactionStatus,paymentMethod: null == paymentMethod ? _self.paymentMethod : paymentMethod // ignore: cast_nullable_to_non_nullable
as PaymentMethod,mockScenario: freezed == mockScenario ? _self.mockScenario : mockScenario // ignore: cast_nullable_to_non_nullable
as String?,providerRefId: freezed == providerRefId ? _self.providerRefId : providerRefId // ignore: cast_nullable_to_non_nullable
as String?,payerVpa: freezed == payerVpa ? _self.payerVpa : payerVpa // ignore: cast_nullable_to_non_nullable
as String?,failureReason: freezed == failureReason ? _self.failureReason : failureReason // ignore: cast_nullable_to_non_nullable
as String?,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,statusHistory: null == statusHistory ? _self.statusHistory : statusHistory // ignore: cast_nullable_to_non_nullable
as List<TransactionStatusHistory>,duplicateFlags: null == duplicateFlags ? _self.duplicateFlags : duplicateFlags // ignore: cast_nullable_to_non_nullable
as List<DuplicateFlag>,customerName: freezed == customerName ? _self.customerName : customerName // ignore: cast_nullable_to_non_nullable
as String?,invoiceNumber: freezed == invoiceNumber ? _self.invoiceNumber : invoiceNumber // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [PaymentTransaction].
extension PaymentTransactionPatterns on PaymentTransaction {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PaymentTransaction value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PaymentTransaction() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PaymentTransaction value)  $default,){
final _that = this;
switch (_that) {
case _PaymentTransaction():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PaymentTransaction value)?  $default,){
final _that = this;
switch (_that) {
case _PaymentTransaction() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'invoice_id')  String? invoiceId, @JsonKey(name: 'customer_id')  String? customerId, @JsonKey(name: 'idempotency_key')  String idempotencyKey,  String amount,  String currency,  TransactionStatus status, @JsonKey(name: 'payment_method')  PaymentMethod paymentMethod, @JsonKey(name: 'mock_scenario')  String? mockScenario, @JsonKey(name: 'provider_ref_id')  String? providerRefId, @JsonKey(name: 'payer_vpa')  String? payerVpa, @JsonKey(name: 'failure_reason')  String? failureReason, @JsonKey(name: 'completed_at')  String? completedAt, @JsonKey(name: 'created_at')  String createdAt, @JsonKey(name: 'status_history')  List<TransactionStatusHistory> statusHistory, @JsonKey(name: 'duplicate_flags')  List<DuplicateFlag> duplicateFlags, @JsonKey(name: 'customer_name')  String? customerName, @JsonKey(name: 'invoice_number')  String? invoiceNumber)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PaymentTransaction() when $default != null:
return $default(_that.id,_that.merchantId,_that.invoiceId,_that.customerId,_that.idempotencyKey,_that.amount,_that.currency,_that.status,_that.paymentMethod,_that.mockScenario,_that.providerRefId,_that.payerVpa,_that.failureReason,_that.completedAt,_that.createdAt,_that.statusHistory,_that.duplicateFlags,_that.customerName,_that.invoiceNumber);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'invoice_id')  String? invoiceId, @JsonKey(name: 'customer_id')  String? customerId, @JsonKey(name: 'idempotency_key')  String idempotencyKey,  String amount,  String currency,  TransactionStatus status, @JsonKey(name: 'payment_method')  PaymentMethod paymentMethod, @JsonKey(name: 'mock_scenario')  String? mockScenario, @JsonKey(name: 'provider_ref_id')  String? providerRefId, @JsonKey(name: 'payer_vpa')  String? payerVpa, @JsonKey(name: 'failure_reason')  String? failureReason, @JsonKey(name: 'completed_at')  String? completedAt, @JsonKey(name: 'created_at')  String createdAt, @JsonKey(name: 'status_history')  List<TransactionStatusHistory> statusHistory, @JsonKey(name: 'duplicate_flags')  List<DuplicateFlag> duplicateFlags, @JsonKey(name: 'customer_name')  String? customerName, @JsonKey(name: 'invoice_number')  String? invoiceNumber)  $default,) {final _that = this;
switch (_that) {
case _PaymentTransaction():
return $default(_that.id,_that.merchantId,_that.invoiceId,_that.customerId,_that.idempotencyKey,_that.amount,_that.currency,_that.status,_that.paymentMethod,_that.mockScenario,_that.providerRefId,_that.payerVpa,_that.failureReason,_that.completedAt,_that.createdAt,_that.statusHistory,_that.duplicateFlags,_that.customerName,_that.invoiceNumber);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'invoice_id')  String? invoiceId, @JsonKey(name: 'customer_id')  String? customerId, @JsonKey(name: 'idempotency_key')  String idempotencyKey,  String amount,  String currency,  TransactionStatus status, @JsonKey(name: 'payment_method')  PaymentMethod paymentMethod, @JsonKey(name: 'mock_scenario')  String? mockScenario, @JsonKey(name: 'provider_ref_id')  String? providerRefId, @JsonKey(name: 'payer_vpa')  String? payerVpa, @JsonKey(name: 'failure_reason')  String? failureReason, @JsonKey(name: 'completed_at')  String? completedAt, @JsonKey(name: 'created_at')  String createdAt, @JsonKey(name: 'status_history')  List<TransactionStatusHistory> statusHistory, @JsonKey(name: 'duplicate_flags')  List<DuplicateFlag> duplicateFlags, @JsonKey(name: 'customer_name')  String? customerName, @JsonKey(name: 'invoice_number')  String? invoiceNumber)?  $default,) {final _that = this;
switch (_that) {
case _PaymentTransaction() when $default != null:
return $default(_that.id,_that.merchantId,_that.invoiceId,_that.customerId,_that.idempotencyKey,_that.amount,_that.currency,_that.status,_that.paymentMethod,_that.mockScenario,_that.providerRefId,_that.payerVpa,_that.failureReason,_that.completedAt,_that.createdAt,_that.statusHistory,_that.duplicateFlags,_that.customerName,_that.invoiceNumber);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PaymentTransaction implements PaymentTransaction {
  const _PaymentTransaction({required this.id, @JsonKey(name: 'merchant_id') required this.merchantId, @JsonKey(name: 'invoice_id') this.invoiceId, @JsonKey(name: 'customer_id') this.customerId, @JsonKey(name: 'idempotency_key') required this.idempotencyKey, required this.amount, this.currency = 'INR', this.status = TransactionStatus.initiated, @JsonKey(name: 'payment_method') required this.paymentMethod, @JsonKey(name: 'mock_scenario') this.mockScenario, @JsonKey(name: 'provider_ref_id') this.providerRefId, @JsonKey(name: 'payer_vpa') this.payerVpa, @JsonKey(name: 'failure_reason') this.failureReason, @JsonKey(name: 'completed_at') this.completedAt, @JsonKey(name: 'created_at') required this.createdAt, @JsonKey(name: 'status_history')  List<TransactionStatusHistory> statusHistory = const [], @JsonKey(name: 'duplicate_flags')  List<DuplicateFlag> duplicateFlags = const [], @JsonKey(name: 'customer_name') this.customerName, @JsonKey(name: 'invoice_number') this.invoiceNumber}): _statusHistory = statusHistory,_duplicateFlags = duplicateFlags;
  factory _PaymentTransaction.fromJson(Map<String, dynamic> json) => _$PaymentTransactionFromJson(json);

@override final  String id;
@override@JsonKey(name: 'merchant_id') final  String merchantId;
@override@JsonKey(name: 'invoice_id') final  String? invoiceId;
@override@JsonKey(name: 'customer_id') final  String? customerId;
@override@JsonKey(name: 'idempotency_key') final  String idempotencyKey;
@override final  String amount;
@override@JsonKey() final  String currency;
@override@JsonKey() final  TransactionStatus status;
@override@JsonKey(name: 'payment_method') final  PaymentMethod paymentMethod;
@override@JsonKey(name: 'mock_scenario') final  String? mockScenario;
@override@JsonKey(name: 'provider_ref_id') final  String? providerRefId;
@override@JsonKey(name: 'payer_vpa') final  String? payerVpa;
@override@JsonKey(name: 'failure_reason') final  String? failureReason;
@override@JsonKey(name: 'completed_at') final  String? completedAt;
@override@JsonKey(name: 'created_at') final  String createdAt;
 final  List<TransactionStatusHistory> _statusHistory;
@override@JsonKey(name: 'status_history') List<TransactionStatusHistory> get statusHistory {
  if (_statusHistory is EqualUnmodifiableListView) return _statusHistory;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_statusHistory);
}

 final  List<DuplicateFlag> _duplicateFlags;
@override@JsonKey(name: 'duplicate_flags') List<DuplicateFlag> get duplicateFlags {
  if (_duplicateFlags is EqualUnmodifiableListView) return _duplicateFlags;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_duplicateFlags);
}

@override@JsonKey(name: 'customer_name') final  String? customerName;
@override@JsonKey(name: 'invoice_number') final  String? invoiceNumber;

/// Create a copy of PaymentTransaction
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PaymentTransactionCopyWith<_PaymentTransaction> get copyWith => __$PaymentTransactionCopyWithImpl<_PaymentTransaction>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PaymentTransactionToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _PaymentTransaction&&(identical(other.id, id) || other.id == id)&&(identical(other.merchantId, merchantId) || other.merchantId == merchantId)&&(identical(other.invoiceId, invoiceId) || other.invoiceId == invoiceId)&&(identical(other.customerId, customerId) || other.customerId == customerId)&&(identical(other.idempotencyKey, idempotencyKey) || other.idempotencyKey == idempotencyKey)&&(identical(other.amount, amount) || other.amount == amount)&&(identical(other.currency, currency) || other.currency == currency)&&(identical(other.status, status) || other.status == status)&&(identical(other.paymentMethod, paymentMethod) || other.paymentMethod == paymentMethod)&&(identical(other.mockScenario, mockScenario) || other.mockScenario == mockScenario)&&(identical(other.providerRefId, providerRefId) || other.providerRefId == providerRefId)&&(identical(other.payerVpa, payerVpa) || other.payerVpa == payerVpa)&&(identical(other.failureReason, failureReason) || other.failureReason == failureReason)&&(identical(other.completedAt, completedAt) || other.completedAt == completedAt)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&const DeepCollectionEquality().equals(other.statusHistory, _statusHistory)&&const DeepCollectionEquality().equals(other.duplicateFlags, _duplicateFlags)&&(identical(other.customerName, customerName) || other.customerName == customerName)&&(identical(other.invoiceNumber, invoiceNumber) || other.invoiceNumber == invoiceNumber));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hashAll([runtimeType,id,merchantId,invoiceId,customerId,idempotencyKey,amount,currency,status,paymentMethod,mockScenario,providerRefId,payerVpa,failureReason,completedAt,createdAt,const DeepCollectionEquality().hash(_statusHistory),const DeepCollectionEquality().hash(_duplicateFlags),customerName,invoiceNumber]);
}

@override
String toString() {
    return 'PaymentTransaction(id: $id, merchantId: $merchantId, invoiceId: $invoiceId, customerId: $customerId, idempotencyKey: $idempotencyKey, amount: $amount, currency: $currency, status: $status, paymentMethod: $paymentMethod, mockScenario: $mockScenario, providerRefId: $providerRefId, payerVpa: $payerVpa, failureReason: $failureReason, completedAt: $completedAt, createdAt: $createdAt, statusHistory: $statusHistory, duplicateFlags: $duplicateFlags, customerName: $customerName, invoiceNumber: $invoiceNumber)';
}


}

/// @nodoc
abstract mixin class _$PaymentTransactionCopyWith<$Res> implements $PaymentTransactionCopyWith<$Res> {
  factory _$PaymentTransactionCopyWith(_PaymentTransaction value, $Res Function(_PaymentTransaction) _then) = __$PaymentTransactionCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId,@JsonKey(name: 'invoice_id') String? invoiceId,@JsonKey(name: 'customer_id') String? customerId,@JsonKey(name: 'idempotency_key') String idempotencyKey, String amount, String currency, TransactionStatus status,@JsonKey(name: 'payment_method') PaymentMethod paymentMethod,@JsonKey(name: 'mock_scenario') String? mockScenario,@JsonKey(name: 'provider_ref_id') String? providerRefId,@JsonKey(name: 'payer_vpa') String? payerVpa,@JsonKey(name: 'failure_reason') String? failureReason,@JsonKey(name: 'completed_at') String? completedAt,@JsonKey(name: 'created_at') String createdAt,@JsonKey(name: 'status_history') List<TransactionStatusHistory> statusHistory,@JsonKey(name: 'duplicate_flags') List<DuplicateFlag> duplicateFlags,@JsonKey(name: 'customer_name') String? customerName,@JsonKey(name: 'invoice_number') String? invoiceNumber
});




}
/// @nodoc
class __$PaymentTransactionCopyWithImpl<$Res>
    implements _$PaymentTransactionCopyWith<$Res> {
  __$PaymentTransactionCopyWithImpl(this._self, this._then);

  final _PaymentTransaction _self;
  final $Res Function(_PaymentTransaction) _then;

/// Create a copy of PaymentTransaction
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? merchantId = null,Object? invoiceId = freezed,Object? customerId = freezed,Object? idempotencyKey = null,Object? amount = null,Object? currency = null,Object? status = null,Object? paymentMethod = null,Object? mockScenario = freezed,Object? providerRefId = freezed,Object? payerVpa = freezed,Object? failureReason = freezed,Object? completedAt = freezed,Object? createdAt = null,Object? statusHistory = null,Object? duplicateFlags = null,Object? customerName = freezed,Object? invoiceNumber = freezed,}) {
  return _then(_PaymentTransaction(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,invoiceId: freezed == invoiceId ? _self.invoiceId : invoiceId // ignore: cast_nullable_to_non_nullable
as String?,customerId: freezed == customerId ? _self.customerId : customerId // ignore: cast_nullable_to_non_nullable
as String?,idempotencyKey: null == idempotencyKey ? _self.idempotencyKey : idempotencyKey // ignore: cast_nullable_to_non_nullable
as String,amount: null == amount ? _self.amount : amount // ignore: cast_nullable_to_non_nullable
as String,currency: null == currency ? _self.currency : currency // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as TransactionStatus,paymentMethod: null == paymentMethod ? _self.paymentMethod : paymentMethod // ignore: cast_nullable_to_non_nullable
as PaymentMethod,mockScenario: freezed == mockScenario ? _self.mockScenario : mockScenario // ignore: cast_nullable_to_non_nullable
as String?,providerRefId: freezed == providerRefId ? _self.providerRefId : providerRefId // ignore: cast_nullable_to_non_nullable
as String?,payerVpa: freezed == payerVpa ? _self.payerVpa : payerVpa // ignore: cast_nullable_to_non_nullable
as String?,failureReason: freezed == failureReason ? _self.failureReason : failureReason // ignore: cast_nullable_to_non_nullable
as String?,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,statusHistory: null == statusHistory ? _self._statusHistory : statusHistory // ignore: cast_nullable_to_non_nullable
as List<TransactionStatusHistory>,duplicateFlags: null == duplicateFlags ? _self._duplicateFlags : duplicateFlags // ignore: cast_nullable_to_non_nullable
as List<DuplicateFlag>,customerName: freezed == customerName ? _self.customerName : customerName // ignore: cast_nullable_to_non_nullable
as String?,invoiceNumber: freezed == invoiceNumber ? _self.invoiceNumber : invoiceNumber // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$CreateRefundRequest {

 String get amount; String get reason;
/// Create a copy of CreateRefundRequest
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CreateRefundRequestCopyWith<CreateRefundRequest> get copyWith => _$CreateRefundRequestCopyWithImpl<CreateRefundRequest>(this as CreateRefundRequest, _$identity);

  /// Serializes this CreateRefundRequest to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as CreateRefundRequest;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CreateRefundRequest&&(identical(other.amount, _this.amount) || other.amount == _this.amount)&&(identical(other.reason, _this.reason) || other.reason == _this.reason));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as CreateRefundRequest;
  return Object.hash(runtimeType,_this.amount,_this.reason);
}

@override
String toString() {
  final _this = this as CreateRefundRequest;
  return 'CreateRefundRequest(amount: ${_this.amount}, reason: ${_this.reason})';
}


}

/// @nodoc
abstract mixin class $CreateRefundRequestCopyWith<$Res>  {
  factory $CreateRefundRequestCopyWith(CreateRefundRequest value, $Res Function(CreateRefundRequest) _then) = _$CreateRefundRequestCopyWithImpl;
@useResult
$Res call({
 String amount, String reason
});




}
/// @nodoc
class _$CreateRefundRequestCopyWithImpl<$Res>
    implements $CreateRefundRequestCopyWith<$Res> {
  _$CreateRefundRequestCopyWithImpl(this._self, this._then);

  final CreateRefundRequest _self;
  final $Res Function(CreateRefundRequest) _then;

/// Create a copy of CreateRefundRequest
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? amount = null,Object? reason = null,}) {
  return _then(CreateRefundRequest(
amount: null == amount ? _self.amount : amount // ignore: cast_nullable_to_non_nullable
as String,reason: null == reason ? _self.reason : reason // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [CreateRefundRequest].
extension CreateRefundRequestPatterns on CreateRefundRequest {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CreateRefundRequest value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CreateRefundRequest() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CreateRefundRequest value)  $default,){
final _that = this;
switch (_that) {
case _CreateRefundRequest():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CreateRefundRequest value)?  $default,){
final _that = this;
switch (_that) {
case _CreateRefundRequest() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String amount,  String reason)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CreateRefundRequest() when $default != null:
return $default(_that.amount,_that.reason);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String amount,  String reason)  $default,) {final _that = this;
switch (_that) {
case _CreateRefundRequest():
return $default(_that.amount,_that.reason);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String amount,  String reason)?  $default,) {final _that = this;
switch (_that) {
case _CreateRefundRequest() when $default != null:
return $default(_that.amount,_that.reason);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CreateRefundRequest implements CreateRefundRequest {
  const _CreateRefundRequest({required this.amount, required this.reason});
  factory _CreateRefundRequest.fromJson(Map<String, dynamic> json) => _$CreateRefundRequestFromJson(json);

@override final  String amount;
@override final  String reason;

/// Create a copy of CreateRefundRequest
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CreateRefundRequestCopyWith<_CreateRefundRequest> get copyWith => __$CreateRefundRequestCopyWithImpl<_CreateRefundRequest>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CreateRefundRequestToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _CreateRefundRequest&&(identical(other.amount, amount) || other.amount == amount)&&(identical(other.reason, reason) || other.reason == reason));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,amount,reason);
}

@override
String toString() {
    return 'CreateRefundRequest(amount: $amount, reason: $reason)';
}


}

/// @nodoc
abstract mixin class _$CreateRefundRequestCopyWith<$Res> implements $CreateRefundRequestCopyWith<$Res> {
  factory _$CreateRefundRequestCopyWith(_CreateRefundRequest value, $Res Function(_CreateRefundRequest) _then) = __$CreateRefundRequestCopyWithImpl;
@override @useResult
$Res call({
 String amount, String reason
});




}
/// @nodoc
class __$CreateRefundRequestCopyWithImpl<$Res>
    implements _$CreateRefundRequestCopyWith<$Res> {
  __$CreateRefundRequestCopyWithImpl(this._self, this._then);

  final _CreateRefundRequest _self;
  final $Res Function(_CreateRefundRequest) _then;

/// Create a copy of CreateRefundRequest
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? amount = null,Object? reason = null,}) {
  return _then(_CreateRefundRequest(
amount: null == amount ? _self.amount : amount // ignore: cast_nullable_to_non_nullable
as String,reason: null == reason ? _self.reason : reason // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
