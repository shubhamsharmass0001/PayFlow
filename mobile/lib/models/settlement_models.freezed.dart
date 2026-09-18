// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'settlement_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$SettlementLineItem {

 String get id;@JsonKey(name: 'transaction_id') String get transactionId; String get amount;@JsonKey(name: 'fee_amount') String get feeAmount;@JsonKey(name: 'tax_amount') String get taxAmount;@JsonKey(name: 'net_amount') String get netAmount;@JsonKey(name: 'created_at') String? get createdAt;
/// Create a copy of SettlementLineItem
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SettlementLineItemCopyWith<SettlementLineItem> get copyWith => _$SettlementLineItemCopyWithImpl<SettlementLineItem>(this as SettlementLineItem, _$identity);

  /// Serializes this SettlementLineItem to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as SettlementLineItem;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SettlementLineItem&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.transactionId, _this.transactionId) || other.transactionId == _this.transactionId)&&(identical(other.amount, _this.amount) || other.amount == _this.amount)&&(identical(other.feeAmount, _this.feeAmount) || other.feeAmount == _this.feeAmount)&&(identical(other.taxAmount, _this.taxAmount) || other.taxAmount == _this.taxAmount)&&(identical(other.netAmount, _this.netAmount) || other.netAmount == _this.netAmount)&&(identical(other.createdAt, _this.createdAt) || other.createdAt == _this.createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as SettlementLineItem;
  return Object.hash(runtimeType,_this.id,_this.transactionId,_this.amount,_this.feeAmount,_this.taxAmount,_this.netAmount,_this.createdAt);
}

@override
String toString() {
  final _this = this as SettlementLineItem;
  return 'SettlementLineItem(id: ${_this.id}, transactionId: ${_this.transactionId}, amount: ${_this.amount}, feeAmount: ${_this.feeAmount}, taxAmount: ${_this.taxAmount}, netAmount: ${_this.netAmount}, createdAt: ${_this.createdAt})';
}


}

/// @nodoc
abstract mixin class $SettlementLineItemCopyWith<$Res>  {
  factory $SettlementLineItemCopyWith(SettlementLineItem value, $Res Function(SettlementLineItem) _then) = _$SettlementLineItemCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'transaction_id') String transactionId, String amount,@JsonKey(name: 'fee_amount') String feeAmount,@JsonKey(name: 'tax_amount') String taxAmount,@JsonKey(name: 'net_amount') String netAmount,@JsonKey(name: 'created_at') String? createdAt
});




}
/// @nodoc
class _$SettlementLineItemCopyWithImpl<$Res>
    implements $SettlementLineItemCopyWith<$Res> {
  _$SettlementLineItemCopyWithImpl(this._self, this._then);

  final SettlementLineItem _self;
  final $Res Function(SettlementLineItem) _then;

/// Create a copy of SettlementLineItem
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? transactionId = null,Object? amount = null,Object? feeAmount = null,Object? taxAmount = null,Object? netAmount = null,Object? createdAt = freezed,}) {
  return _then(SettlementLineItem(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,transactionId: null == transactionId ? _self.transactionId : transactionId // ignore: cast_nullable_to_non_nullable
as String,amount: null == amount ? _self.amount : amount // ignore: cast_nullable_to_non_nullable
as String,feeAmount: null == feeAmount ? _self.feeAmount : feeAmount // ignore: cast_nullable_to_non_nullable
as String,taxAmount: null == taxAmount ? _self.taxAmount : taxAmount // ignore: cast_nullable_to_non_nullable
as String,netAmount: null == netAmount ? _self.netAmount : netAmount // ignore: cast_nullable_to_non_nullable
as String,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [SettlementLineItem].
extension SettlementLineItemPatterns on SettlementLineItem {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SettlementLineItem value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SettlementLineItem() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SettlementLineItem value)  $default,){
final _that = this;
switch (_that) {
case _SettlementLineItem():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SettlementLineItem value)?  $default,){
final _that = this;
switch (_that) {
case _SettlementLineItem() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'transaction_id')  String transactionId,  String amount, @JsonKey(name: 'fee_amount')  String feeAmount, @JsonKey(name: 'tax_amount')  String taxAmount, @JsonKey(name: 'net_amount')  String netAmount, @JsonKey(name: 'created_at')  String? createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SettlementLineItem() when $default != null:
return $default(_that.id,_that.transactionId,_that.amount,_that.feeAmount,_that.taxAmount,_that.netAmount,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'transaction_id')  String transactionId,  String amount, @JsonKey(name: 'fee_amount')  String feeAmount, @JsonKey(name: 'tax_amount')  String taxAmount, @JsonKey(name: 'net_amount')  String netAmount, @JsonKey(name: 'created_at')  String? createdAt)  $default,) {final _that = this;
switch (_that) {
case _SettlementLineItem():
return $default(_that.id,_that.transactionId,_that.amount,_that.feeAmount,_that.taxAmount,_that.netAmount,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'transaction_id')  String transactionId,  String amount, @JsonKey(name: 'fee_amount')  String feeAmount, @JsonKey(name: 'tax_amount')  String taxAmount, @JsonKey(name: 'net_amount')  String netAmount, @JsonKey(name: 'created_at')  String? createdAt)?  $default,) {final _that = this;
switch (_that) {
case _SettlementLineItem() when $default != null:
return $default(_that.id,_that.transactionId,_that.amount,_that.feeAmount,_that.taxAmount,_that.netAmount,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _SettlementLineItem implements SettlementLineItem {
  const _SettlementLineItem({required this.id, @JsonKey(name: 'transaction_id') required this.transactionId, required this.amount, @JsonKey(name: 'fee_amount') required this.feeAmount, @JsonKey(name: 'tax_amount') required this.taxAmount, @JsonKey(name: 'net_amount') required this.netAmount, @JsonKey(name: 'created_at') this.createdAt});
  factory _SettlementLineItem.fromJson(Map<String, dynamic> json) => _$SettlementLineItemFromJson(json);

@override final  String id;
@override@JsonKey(name: 'transaction_id') final  String transactionId;
@override final  String amount;
@override@JsonKey(name: 'fee_amount') final  String feeAmount;
@override@JsonKey(name: 'tax_amount') final  String taxAmount;
@override@JsonKey(name: 'net_amount') final  String netAmount;
@override@JsonKey(name: 'created_at') final  String? createdAt;

/// Create a copy of SettlementLineItem
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SettlementLineItemCopyWith<_SettlementLineItem> get copyWith => __$SettlementLineItemCopyWithImpl<_SettlementLineItem>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SettlementLineItemToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _SettlementLineItem&&(identical(other.id, id) || other.id == id)&&(identical(other.transactionId, transactionId) || other.transactionId == transactionId)&&(identical(other.amount, amount) || other.amount == amount)&&(identical(other.feeAmount, feeAmount) || other.feeAmount == feeAmount)&&(identical(other.taxAmount, taxAmount) || other.taxAmount == taxAmount)&&(identical(other.netAmount, netAmount) || other.netAmount == netAmount)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,transactionId,amount,feeAmount,taxAmount,netAmount,createdAt);
}

@override
String toString() {
    return 'SettlementLineItem(id: $id, transactionId: $transactionId, amount: $amount, feeAmount: $feeAmount, taxAmount: $taxAmount, netAmount: $netAmount, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$SettlementLineItemCopyWith<$Res> implements $SettlementLineItemCopyWith<$Res> {
  factory _$SettlementLineItemCopyWith(_SettlementLineItem value, $Res Function(_SettlementLineItem) _then) = __$SettlementLineItemCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'transaction_id') String transactionId, String amount,@JsonKey(name: 'fee_amount') String feeAmount,@JsonKey(name: 'tax_amount') String taxAmount,@JsonKey(name: 'net_amount') String netAmount,@JsonKey(name: 'created_at') String? createdAt
});




}
/// @nodoc
class __$SettlementLineItemCopyWithImpl<$Res>
    implements _$SettlementLineItemCopyWith<$Res> {
  __$SettlementLineItemCopyWithImpl(this._self, this._then);

  final _SettlementLineItem _self;
  final $Res Function(_SettlementLineItem) _then;

/// Create a copy of SettlementLineItem
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? transactionId = null,Object? amount = null,Object? feeAmount = null,Object? taxAmount = null,Object? netAmount = null,Object? createdAt = freezed,}) {
  return _then(_SettlementLineItem(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,transactionId: null == transactionId ? _self.transactionId : transactionId // ignore: cast_nullable_to_non_nullable
as String,amount: null == amount ? _self.amount : amount // ignore: cast_nullable_to_non_nullable
as String,feeAmount: null == feeAmount ? _self.feeAmount : feeAmount // ignore: cast_nullable_to_non_nullable
as String,taxAmount: null == taxAmount ? _self.taxAmount : taxAmount // ignore: cast_nullable_to_non_nullable
as String,netAmount: null == netAmount ? _self.netAmount : netAmount // ignore: cast_nullable_to_non_nullable
as String,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$Settlement {

 String get id;@JsonKey(name: 'merchant_id') String get merchantId;@JsonKey(name: 'settlement_date') String get settlementDate;@JsonKey(name: 'settlement_cycle') String get settlementCycle;@JsonKey(name: 'transaction_count') int get transactionCount;@JsonKey(name: 'gross_amount') String get grossAmount;@JsonKey(name: 'mdr_amount') String get mdrAmount;@JsonKey(name: 'tax_on_mdr') String get taxOnMdr;@JsonKey(name: 'net_amount') String get netAmount; SettlementStatus get status;@JsonKey(name: 'utr_reference') String? get utrReference;@JsonKey(name: 'bank_account_ref') String? get bankAccountRef;@JsonKey(name: 'settled_at') String? get settledAt;@JsonKey(name: 'created_at') String? get createdAt;@JsonKey(name: 'line_items') List<SettlementLineItem> get lineItems;
/// Create a copy of Settlement
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SettlementCopyWith<Settlement> get copyWith => _$SettlementCopyWithImpl<Settlement>(this as Settlement, _$identity);

  /// Serializes this Settlement to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Settlement;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Settlement&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.merchantId, _this.merchantId) || other.merchantId == _this.merchantId)&&(identical(other.settlementDate, _this.settlementDate) || other.settlementDate == _this.settlementDate)&&(identical(other.settlementCycle, _this.settlementCycle) || other.settlementCycle == _this.settlementCycle)&&(identical(other.transactionCount, _this.transactionCount) || other.transactionCount == _this.transactionCount)&&(identical(other.grossAmount, _this.grossAmount) || other.grossAmount == _this.grossAmount)&&(identical(other.mdrAmount, _this.mdrAmount) || other.mdrAmount == _this.mdrAmount)&&(identical(other.taxOnMdr, _this.taxOnMdr) || other.taxOnMdr == _this.taxOnMdr)&&(identical(other.netAmount, _this.netAmount) || other.netAmount == _this.netAmount)&&(identical(other.status, _this.status) || other.status == _this.status)&&(identical(other.utrReference, _this.utrReference) || other.utrReference == _this.utrReference)&&(identical(other.bankAccountRef, _this.bankAccountRef) || other.bankAccountRef == _this.bankAccountRef)&&(identical(other.settledAt, _this.settledAt) || other.settledAt == _this.settledAt)&&(identical(other.createdAt, _this.createdAt) || other.createdAt == _this.createdAt)&&const DeepCollectionEquality().equals(other.lineItems, _this.lineItems));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Settlement;
  return Object.hash(runtimeType,_this.id,_this.merchantId,_this.settlementDate,_this.settlementCycle,_this.transactionCount,_this.grossAmount,_this.mdrAmount,_this.taxOnMdr,_this.netAmount,_this.status,_this.utrReference,_this.bankAccountRef,_this.settledAt,_this.createdAt,const DeepCollectionEquality().hash(_this.lineItems));
}

@override
String toString() {
  final _this = this as Settlement;
  return 'Settlement(id: ${_this.id}, merchantId: ${_this.merchantId}, settlementDate: ${_this.settlementDate}, settlementCycle: ${_this.settlementCycle}, transactionCount: ${_this.transactionCount}, grossAmount: ${_this.grossAmount}, mdrAmount: ${_this.mdrAmount}, taxOnMdr: ${_this.taxOnMdr}, netAmount: ${_this.netAmount}, status: ${_this.status}, utrReference: ${_this.utrReference}, bankAccountRef: ${_this.bankAccountRef}, settledAt: ${_this.settledAt}, createdAt: ${_this.createdAt}, lineItems: ${_this.lineItems})';
}


}

/// @nodoc
abstract mixin class $SettlementCopyWith<$Res>  {
  factory $SettlementCopyWith(Settlement value, $Res Function(Settlement) _then) = _$SettlementCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId,@JsonKey(name: 'settlement_date') String settlementDate,@JsonKey(name: 'settlement_cycle') String settlementCycle,@JsonKey(name: 'transaction_count') int transactionCount,@JsonKey(name: 'gross_amount') String grossAmount,@JsonKey(name: 'mdr_amount') String mdrAmount,@JsonKey(name: 'tax_on_mdr') String taxOnMdr,@JsonKey(name: 'net_amount') String netAmount, SettlementStatus status,@JsonKey(name: 'utr_reference') String? utrReference,@JsonKey(name: 'bank_account_ref') String? bankAccountRef,@JsonKey(name: 'settled_at') String? settledAt,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'line_items') List<SettlementLineItem> lineItems
});




}
/// @nodoc
class _$SettlementCopyWithImpl<$Res>
    implements $SettlementCopyWith<$Res> {
  _$SettlementCopyWithImpl(this._self, this._then);

  final Settlement _self;
  final $Res Function(Settlement) _then;

/// Create a copy of Settlement
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? merchantId = null,Object? settlementDate = null,Object? settlementCycle = null,Object? transactionCount = null,Object? grossAmount = null,Object? mdrAmount = null,Object? taxOnMdr = null,Object? netAmount = null,Object? status = null,Object? utrReference = freezed,Object? bankAccountRef = freezed,Object? settledAt = freezed,Object? createdAt = freezed,Object? lineItems = null,}) {
  return _then(Settlement(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,settlementDate: null == settlementDate ? _self.settlementDate : settlementDate // ignore: cast_nullable_to_non_nullable
as String,settlementCycle: null == settlementCycle ? _self.settlementCycle : settlementCycle // ignore: cast_nullable_to_non_nullable
as String,transactionCount: null == transactionCount ? _self.transactionCount : transactionCount // ignore: cast_nullable_to_non_nullable
as int,grossAmount: null == grossAmount ? _self.grossAmount : grossAmount // ignore: cast_nullable_to_non_nullable
as String,mdrAmount: null == mdrAmount ? _self.mdrAmount : mdrAmount // ignore: cast_nullable_to_non_nullable
as String,taxOnMdr: null == taxOnMdr ? _self.taxOnMdr : taxOnMdr // ignore: cast_nullable_to_non_nullable
as String,netAmount: null == netAmount ? _self.netAmount : netAmount // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as SettlementStatus,utrReference: freezed == utrReference ? _self.utrReference : utrReference // ignore: cast_nullable_to_non_nullable
as String?,bankAccountRef: freezed == bankAccountRef ? _self.bankAccountRef : bankAccountRef // ignore: cast_nullable_to_non_nullable
as String?,settledAt: freezed == settledAt ? _self.settledAt : settledAt // ignore: cast_nullable_to_non_nullable
as String?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,lineItems: null == lineItems ? _self.lineItems : lineItems // ignore: cast_nullable_to_non_nullable
as List<SettlementLineItem>,
  ));
}

}


/// Adds pattern-matching-related methods to [Settlement].
extension SettlementPatterns on Settlement {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Settlement value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Settlement() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Settlement value)  $default,){
final _that = this;
switch (_that) {
case _Settlement():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Settlement value)?  $default,){
final _that = this;
switch (_that) {
case _Settlement() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'settlement_date')  String settlementDate, @JsonKey(name: 'settlement_cycle')  String settlementCycle, @JsonKey(name: 'transaction_count')  int transactionCount, @JsonKey(name: 'gross_amount')  String grossAmount, @JsonKey(name: 'mdr_amount')  String mdrAmount, @JsonKey(name: 'tax_on_mdr')  String taxOnMdr, @JsonKey(name: 'net_amount')  String netAmount,  SettlementStatus status, @JsonKey(name: 'utr_reference')  String? utrReference, @JsonKey(name: 'bank_account_ref')  String? bankAccountRef, @JsonKey(name: 'settled_at')  String? settledAt, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'line_items')  List<SettlementLineItem> lineItems)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Settlement() when $default != null:
return $default(_that.id,_that.merchantId,_that.settlementDate,_that.settlementCycle,_that.transactionCount,_that.grossAmount,_that.mdrAmount,_that.taxOnMdr,_that.netAmount,_that.status,_that.utrReference,_that.bankAccountRef,_that.settledAt,_that.createdAt,_that.lineItems);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'settlement_date')  String settlementDate, @JsonKey(name: 'settlement_cycle')  String settlementCycle, @JsonKey(name: 'transaction_count')  int transactionCount, @JsonKey(name: 'gross_amount')  String grossAmount, @JsonKey(name: 'mdr_amount')  String mdrAmount, @JsonKey(name: 'tax_on_mdr')  String taxOnMdr, @JsonKey(name: 'net_amount')  String netAmount,  SettlementStatus status, @JsonKey(name: 'utr_reference')  String? utrReference, @JsonKey(name: 'bank_account_ref')  String? bankAccountRef, @JsonKey(name: 'settled_at')  String? settledAt, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'line_items')  List<SettlementLineItem> lineItems)  $default,) {final _that = this;
switch (_that) {
case _Settlement():
return $default(_that.id,_that.merchantId,_that.settlementDate,_that.settlementCycle,_that.transactionCount,_that.grossAmount,_that.mdrAmount,_that.taxOnMdr,_that.netAmount,_that.status,_that.utrReference,_that.bankAccountRef,_that.settledAt,_that.createdAt,_that.lineItems);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'settlement_date')  String settlementDate, @JsonKey(name: 'settlement_cycle')  String settlementCycle, @JsonKey(name: 'transaction_count')  int transactionCount, @JsonKey(name: 'gross_amount')  String grossAmount, @JsonKey(name: 'mdr_amount')  String mdrAmount, @JsonKey(name: 'tax_on_mdr')  String taxOnMdr, @JsonKey(name: 'net_amount')  String netAmount,  SettlementStatus status, @JsonKey(name: 'utr_reference')  String? utrReference, @JsonKey(name: 'bank_account_ref')  String? bankAccountRef, @JsonKey(name: 'settled_at')  String? settledAt, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'line_items')  List<SettlementLineItem> lineItems)?  $default,) {final _that = this;
switch (_that) {
case _Settlement() when $default != null:
return $default(_that.id,_that.merchantId,_that.settlementDate,_that.settlementCycle,_that.transactionCount,_that.grossAmount,_that.mdrAmount,_that.taxOnMdr,_that.netAmount,_that.status,_that.utrReference,_that.bankAccountRef,_that.settledAt,_that.createdAt,_that.lineItems);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Settlement implements Settlement {
  const _Settlement({required this.id, @JsonKey(name: 'merchant_id') required this.merchantId, @JsonKey(name: 'settlement_date') required this.settlementDate, @JsonKey(name: 'settlement_cycle') required this.settlementCycle, @JsonKey(name: 'transaction_count') required this.transactionCount, @JsonKey(name: 'gross_amount') required this.grossAmount, @JsonKey(name: 'mdr_amount') required this.mdrAmount, @JsonKey(name: 'tax_on_mdr') required this.taxOnMdr, @JsonKey(name: 'net_amount') required this.netAmount, this.status = SettlementStatus.pending, @JsonKey(name: 'utr_reference') this.utrReference, @JsonKey(name: 'bank_account_ref') this.bankAccountRef, @JsonKey(name: 'settled_at') this.settledAt, @JsonKey(name: 'created_at') this.createdAt, @JsonKey(name: 'line_items')  List<SettlementLineItem> lineItems = const []}): _lineItems = lineItems;
  factory _Settlement.fromJson(Map<String, dynamic> json) => _$SettlementFromJson(json);

@override final  String id;
@override@JsonKey(name: 'merchant_id') final  String merchantId;
@override@JsonKey(name: 'settlement_date') final  String settlementDate;
@override@JsonKey(name: 'settlement_cycle') final  String settlementCycle;
@override@JsonKey(name: 'transaction_count') final  int transactionCount;
@override@JsonKey(name: 'gross_amount') final  String grossAmount;
@override@JsonKey(name: 'mdr_amount') final  String mdrAmount;
@override@JsonKey(name: 'tax_on_mdr') final  String taxOnMdr;
@override@JsonKey(name: 'net_amount') final  String netAmount;
@override@JsonKey() final  SettlementStatus status;
@override@JsonKey(name: 'utr_reference') final  String? utrReference;
@override@JsonKey(name: 'bank_account_ref') final  String? bankAccountRef;
@override@JsonKey(name: 'settled_at') final  String? settledAt;
@override@JsonKey(name: 'created_at') final  String? createdAt;
 final  List<SettlementLineItem> _lineItems;
@override@JsonKey(name: 'line_items') List<SettlementLineItem> get lineItems {
  if (_lineItems is EqualUnmodifiableListView) return _lineItems;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_lineItems);
}


/// Create a copy of Settlement
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SettlementCopyWith<_Settlement> get copyWith => __$SettlementCopyWithImpl<_Settlement>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SettlementToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Settlement&&(identical(other.id, id) || other.id == id)&&(identical(other.merchantId, merchantId) || other.merchantId == merchantId)&&(identical(other.settlementDate, settlementDate) || other.settlementDate == settlementDate)&&(identical(other.settlementCycle, settlementCycle) || other.settlementCycle == settlementCycle)&&(identical(other.transactionCount, transactionCount) || other.transactionCount == transactionCount)&&(identical(other.grossAmount, grossAmount) || other.grossAmount == grossAmount)&&(identical(other.mdrAmount, mdrAmount) || other.mdrAmount == mdrAmount)&&(identical(other.taxOnMdr, taxOnMdr) || other.taxOnMdr == taxOnMdr)&&(identical(other.netAmount, netAmount) || other.netAmount == netAmount)&&(identical(other.status, status) || other.status == status)&&(identical(other.utrReference, utrReference) || other.utrReference == utrReference)&&(identical(other.bankAccountRef, bankAccountRef) || other.bankAccountRef == bankAccountRef)&&(identical(other.settledAt, settledAt) || other.settledAt == settledAt)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&const DeepCollectionEquality().equals(other.lineItems, _lineItems));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,merchantId,settlementDate,settlementCycle,transactionCount,grossAmount,mdrAmount,taxOnMdr,netAmount,status,utrReference,bankAccountRef,settledAt,createdAt,const DeepCollectionEquality().hash(_lineItems));
}

@override
String toString() {
    return 'Settlement(id: $id, merchantId: $merchantId, settlementDate: $settlementDate, settlementCycle: $settlementCycle, transactionCount: $transactionCount, grossAmount: $grossAmount, mdrAmount: $mdrAmount, taxOnMdr: $taxOnMdr, netAmount: $netAmount, status: $status, utrReference: $utrReference, bankAccountRef: $bankAccountRef, settledAt: $settledAt, createdAt: $createdAt, lineItems: $lineItems)';
}


}

/// @nodoc
abstract mixin class _$SettlementCopyWith<$Res> implements $SettlementCopyWith<$Res> {
  factory _$SettlementCopyWith(_Settlement value, $Res Function(_Settlement) _then) = __$SettlementCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId,@JsonKey(name: 'settlement_date') String settlementDate,@JsonKey(name: 'settlement_cycle') String settlementCycle,@JsonKey(name: 'transaction_count') int transactionCount,@JsonKey(name: 'gross_amount') String grossAmount,@JsonKey(name: 'mdr_amount') String mdrAmount,@JsonKey(name: 'tax_on_mdr') String taxOnMdr,@JsonKey(name: 'net_amount') String netAmount, SettlementStatus status,@JsonKey(name: 'utr_reference') String? utrReference,@JsonKey(name: 'bank_account_ref') String? bankAccountRef,@JsonKey(name: 'settled_at') String? settledAt,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'line_items') List<SettlementLineItem> lineItems
});




}
/// @nodoc
class __$SettlementCopyWithImpl<$Res>
    implements _$SettlementCopyWith<$Res> {
  __$SettlementCopyWithImpl(this._self, this._then);

  final _Settlement _self;
  final $Res Function(_Settlement) _then;

/// Create a copy of Settlement
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? merchantId = null,Object? settlementDate = null,Object? settlementCycle = null,Object? transactionCount = null,Object? grossAmount = null,Object? mdrAmount = null,Object? taxOnMdr = null,Object? netAmount = null,Object? status = null,Object? utrReference = freezed,Object? bankAccountRef = freezed,Object? settledAt = freezed,Object? createdAt = freezed,Object? lineItems = null,}) {
  return _then(_Settlement(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,settlementDate: null == settlementDate ? _self.settlementDate : settlementDate // ignore: cast_nullable_to_non_nullable
as String,settlementCycle: null == settlementCycle ? _self.settlementCycle : settlementCycle // ignore: cast_nullable_to_non_nullable
as String,transactionCount: null == transactionCount ? _self.transactionCount : transactionCount // ignore: cast_nullable_to_non_nullable
as int,grossAmount: null == grossAmount ? _self.grossAmount : grossAmount // ignore: cast_nullable_to_non_nullable
as String,mdrAmount: null == mdrAmount ? _self.mdrAmount : mdrAmount // ignore: cast_nullable_to_non_nullable
as String,taxOnMdr: null == taxOnMdr ? _self.taxOnMdr : taxOnMdr // ignore: cast_nullable_to_non_nullable
as String,netAmount: null == netAmount ? _self.netAmount : netAmount // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as SettlementStatus,utrReference: freezed == utrReference ? _self.utrReference : utrReference // ignore: cast_nullable_to_non_nullable
as String?,bankAccountRef: freezed == bankAccountRef ? _self.bankAccountRef : bankAccountRef // ignore: cast_nullable_to_non_nullable
as String?,settledAt: freezed == settledAt ? _self.settledAt : settledAt // ignore: cast_nullable_to_non_nullable
as String?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,lineItems: null == lineItems ? _self._lineItems : lineItems // ignore: cast_nullable_to_non_nullable
as List<SettlementLineItem>,
  ));
}


}

// dart format on
