// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'invoice_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$InvoiceItem {

 String? get id; String get name; String? get description; String get quantity;@JsonKey(name: 'unit_price') String get unitPrice;@JsonKey(name: 'tax_rate') String get taxRate;@JsonKey(name: 'discount_amount') String get discountAmount;@JsonKey(name: 'line_total') String get lineTotal;
/// Create a copy of InvoiceItem
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$InvoiceItemCopyWith<InvoiceItem> get copyWith => _$InvoiceItemCopyWithImpl<InvoiceItem>(this as InvoiceItem, _$identity);

  /// Serializes this InvoiceItem to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as InvoiceItem;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is InvoiceItem&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.name, _this.name) || other.name == _this.name)&&(identical(other.description, _this.description) || other.description == _this.description)&&(identical(other.quantity, _this.quantity) || other.quantity == _this.quantity)&&(identical(other.unitPrice, _this.unitPrice) || other.unitPrice == _this.unitPrice)&&(identical(other.taxRate, _this.taxRate) || other.taxRate == _this.taxRate)&&(identical(other.discountAmount, _this.discountAmount) || other.discountAmount == _this.discountAmount)&&(identical(other.lineTotal, _this.lineTotal) || other.lineTotal == _this.lineTotal));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as InvoiceItem;
  return Object.hash(runtimeType,_this.id,_this.name,_this.description,_this.quantity,_this.unitPrice,_this.taxRate,_this.discountAmount,_this.lineTotal);
}

@override
String toString() {
  final _this = this as InvoiceItem;
  return 'InvoiceItem(id: ${_this.id}, name: ${_this.name}, description: ${_this.description}, quantity: ${_this.quantity}, unitPrice: ${_this.unitPrice}, taxRate: ${_this.taxRate}, discountAmount: ${_this.discountAmount}, lineTotal: ${_this.lineTotal})';
}


}

/// @nodoc
abstract mixin class $InvoiceItemCopyWith<$Res>  {
  factory $InvoiceItemCopyWith(InvoiceItem value, $Res Function(InvoiceItem) _then) = _$InvoiceItemCopyWithImpl;
@useResult
$Res call({
 String? id, String name, String? description, String quantity,@JsonKey(name: 'unit_price') String unitPrice,@JsonKey(name: 'tax_rate') String taxRate,@JsonKey(name: 'discount_amount') String discountAmount,@JsonKey(name: 'line_total') String lineTotal
});




}
/// @nodoc
class _$InvoiceItemCopyWithImpl<$Res>
    implements $InvoiceItemCopyWith<$Res> {
  _$InvoiceItemCopyWithImpl(this._self, this._then);

  final InvoiceItem _self;
  final $Res Function(InvoiceItem) _then;

/// Create a copy of InvoiceItem
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = freezed,Object? name = null,Object? description = freezed,Object? quantity = null,Object? unitPrice = null,Object? taxRate = null,Object? discountAmount = null,Object? lineTotal = null,}) {
  return _then(InvoiceItem(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as String,unitPrice: null == unitPrice ? _self.unitPrice : unitPrice // ignore: cast_nullable_to_non_nullable
as String,taxRate: null == taxRate ? _self.taxRate : taxRate // ignore: cast_nullable_to_non_nullable
as String,discountAmount: null == discountAmount ? _self.discountAmount : discountAmount // ignore: cast_nullable_to_non_nullable
as String,lineTotal: null == lineTotal ? _self.lineTotal : lineTotal // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [InvoiceItem].
extension InvoiceItemPatterns on InvoiceItem {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _InvoiceItem value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _InvoiceItem() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _InvoiceItem value)  $default,){
final _that = this;
switch (_that) {
case _InvoiceItem():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _InvoiceItem value)?  $default,){
final _that = this;
switch (_that) {
case _InvoiceItem() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? id,  String name,  String? description,  String quantity, @JsonKey(name: 'unit_price')  String unitPrice, @JsonKey(name: 'tax_rate')  String taxRate, @JsonKey(name: 'discount_amount')  String discountAmount, @JsonKey(name: 'line_total')  String lineTotal)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _InvoiceItem() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.quantity,_that.unitPrice,_that.taxRate,_that.discountAmount,_that.lineTotal);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? id,  String name,  String? description,  String quantity, @JsonKey(name: 'unit_price')  String unitPrice, @JsonKey(name: 'tax_rate')  String taxRate, @JsonKey(name: 'discount_amount')  String discountAmount, @JsonKey(name: 'line_total')  String lineTotal)  $default,) {final _that = this;
switch (_that) {
case _InvoiceItem():
return $default(_that.id,_that.name,_that.description,_that.quantity,_that.unitPrice,_that.taxRate,_that.discountAmount,_that.lineTotal);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? id,  String name,  String? description,  String quantity, @JsonKey(name: 'unit_price')  String unitPrice, @JsonKey(name: 'tax_rate')  String taxRate, @JsonKey(name: 'discount_amount')  String discountAmount, @JsonKey(name: 'line_total')  String lineTotal)?  $default,) {final _that = this;
switch (_that) {
case _InvoiceItem() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.quantity,_that.unitPrice,_that.taxRate,_that.discountAmount,_that.lineTotal);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _InvoiceItem implements InvoiceItem {
  const _InvoiceItem({this.id, required this.name, this.description, this.quantity = '1.00', @JsonKey(name: 'unit_price') required this.unitPrice, @JsonKey(name: 'tax_rate') this.taxRate = '0.00', @JsonKey(name: 'discount_amount') this.discountAmount = '0.00', @JsonKey(name: 'line_total') this.lineTotal = '0.00'});
  factory _InvoiceItem.fromJson(Map<String, dynamic> json) => _$InvoiceItemFromJson(json);

@override final  String? id;
@override final  String name;
@override final  String? description;
@override@JsonKey() final  String quantity;
@override@JsonKey(name: 'unit_price') final  String unitPrice;
@override@JsonKey(name: 'tax_rate') final  String taxRate;
@override@JsonKey(name: 'discount_amount') final  String discountAmount;
@override@JsonKey(name: 'line_total') final  String lineTotal;

/// Create a copy of InvoiceItem
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$InvoiceItemCopyWith<_InvoiceItem> get copyWith => __$InvoiceItemCopyWithImpl<_InvoiceItem>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$InvoiceItemToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _InvoiceItem&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unitPrice, unitPrice) || other.unitPrice == unitPrice)&&(identical(other.taxRate, taxRate) || other.taxRate == taxRate)&&(identical(other.discountAmount, discountAmount) || other.discountAmount == discountAmount)&&(identical(other.lineTotal, lineTotal) || other.lineTotal == lineTotal));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,name,description,quantity,unitPrice,taxRate,discountAmount,lineTotal);
}

@override
String toString() {
    return 'InvoiceItem(id: $id, name: $name, description: $description, quantity: $quantity, unitPrice: $unitPrice, taxRate: $taxRate, discountAmount: $discountAmount, lineTotal: $lineTotal)';
}


}

/// @nodoc
abstract mixin class _$InvoiceItemCopyWith<$Res> implements $InvoiceItemCopyWith<$Res> {
  factory _$InvoiceItemCopyWith(_InvoiceItem value, $Res Function(_InvoiceItem) _then) = __$InvoiceItemCopyWithImpl;
@override @useResult
$Res call({
 String? id, String name, String? description, String quantity,@JsonKey(name: 'unit_price') String unitPrice,@JsonKey(name: 'tax_rate') String taxRate,@JsonKey(name: 'discount_amount') String discountAmount,@JsonKey(name: 'line_total') String lineTotal
});




}
/// @nodoc
class __$InvoiceItemCopyWithImpl<$Res>
    implements _$InvoiceItemCopyWith<$Res> {
  __$InvoiceItemCopyWithImpl(this._self, this._then);

  final _InvoiceItem _self;
  final $Res Function(_InvoiceItem) _then;

/// Create a copy of InvoiceItem
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? name = null,Object? description = freezed,Object? quantity = null,Object? unitPrice = null,Object? taxRate = null,Object? discountAmount = null,Object? lineTotal = null,}) {
  return _then(_InvoiceItem(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as String,unitPrice: null == unitPrice ? _self.unitPrice : unitPrice // ignore: cast_nullable_to_non_nullable
as String,taxRate: null == taxRate ? _self.taxRate : taxRate // ignore: cast_nullable_to_non_nullable
as String,discountAmount: null == discountAmount ? _self.discountAmount : discountAmount // ignore: cast_nullable_to_non_nullable
as String,lineTotal: null == lineTotal ? _self.lineTotal : lineTotal // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$Invoice {

 String get id;@JsonKey(name: 'merchant_id') String get merchantId;@JsonKey(name: 'invoice_number') String get invoiceNumber;@JsonKey(name: 'customer_id') String? get customerId;@JsonKey(name: 'store_id') String? get storeId; InvoiceStatus get status;@JsonKey(name: 'subtotal') String get subtotal;@JsonKey(name: 'tax_total') String get taxTotal;@JsonKey(name: 'discount_total') String get discountTotal;@JsonKey(name: 'total_amount') String get totalAmount;@JsonKey(name: 'paid_amount') String get paidAmount; String get currency;@JsonKey(name: 'allow_partial_payment') bool get allowPartialPayment;@JsonKey(name: 'allow_split_payment') bool get allowSplitPayment;@JsonKey(name: 'due_date') String? get dueDate; String? get notes;@JsonKey(name: 'created_at') String? get createdAt;@JsonKey(name: 'updated_at') String? get updatedAt; List<InvoiceItem> get items;@JsonKey(name: 'customer_name') String? get customerName;
/// Create a copy of Invoice
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$InvoiceCopyWith<Invoice> get copyWith => _$InvoiceCopyWithImpl<Invoice>(this as Invoice, _$identity);

  /// Serializes this Invoice to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Invoice;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Invoice&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.merchantId, _this.merchantId) || other.merchantId == _this.merchantId)&&(identical(other.invoiceNumber, _this.invoiceNumber) || other.invoiceNumber == _this.invoiceNumber)&&(identical(other.customerId, _this.customerId) || other.customerId == _this.customerId)&&(identical(other.storeId, _this.storeId) || other.storeId == _this.storeId)&&(identical(other.status, _this.status) || other.status == _this.status)&&(identical(other.subtotal, _this.subtotal) || other.subtotal == _this.subtotal)&&(identical(other.taxTotal, _this.taxTotal) || other.taxTotal == _this.taxTotal)&&(identical(other.discountTotal, _this.discountTotal) || other.discountTotal == _this.discountTotal)&&(identical(other.totalAmount, _this.totalAmount) || other.totalAmount == _this.totalAmount)&&(identical(other.paidAmount, _this.paidAmount) || other.paidAmount == _this.paidAmount)&&(identical(other.currency, _this.currency) || other.currency == _this.currency)&&(identical(other.allowPartialPayment, _this.allowPartialPayment) || other.allowPartialPayment == _this.allowPartialPayment)&&(identical(other.allowSplitPayment, _this.allowSplitPayment) || other.allowSplitPayment == _this.allowSplitPayment)&&(identical(other.dueDate, _this.dueDate) || other.dueDate == _this.dueDate)&&(identical(other.notes, _this.notes) || other.notes == _this.notes)&&(identical(other.createdAt, _this.createdAt) || other.createdAt == _this.createdAt)&&(identical(other.updatedAt, _this.updatedAt) || other.updatedAt == _this.updatedAt)&&const DeepCollectionEquality().equals(other.items, _this.items)&&(identical(other.customerName, _this.customerName) || other.customerName == _this.customerName));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Invoice;
  return Object.hashAll([runtimeType,_this.id,_this.merchantId,_this.invoiceNumber,_this.customerId,_this.storeId,_this.status,_this.subtotal,_this.taxTotal,_this.discountTotal,_this.totalAmount,_this.paidAmount,_this.currency,_this.allowPartialPayment,_this.allowSplitPayment,_this.dueDate,_this.notes,_this.createdAt,_this.updatedAt,const DeepCollectionEquality().hash(_this.items),_this.customerName]);
}

@override
String toString() {
  final _this = this as Invoice;
  return 'Invoice(id: ${_this.id}, merchantId: ${_this.merchantId}, invoiceNumber: ${_this.invoiceNumber}, customerId: ${_this.customerId}, storeId: ${_this.storeId}, status: ${_this.status}, subtotal: ${_this.subtotal}, taxTotal: ${_this.taxTotal}, discountTotal: ${_this.discountTotal}, totalAmount: ${_this.totalAmount}, paidAmount: ${_this.paidAmount}, currency: ${_this.currency}, allowPartialPayment: ${_this.allowPartialPayment}, allowSplitPayment: ${_this.allowSplitPayment}, dueDate: ${_this.dueDate}, notes: ${_this.notes}, createdAt: ${_this.createdAt}, updatedAt: ${_this.updatedAt}, items: ${_this.items}, customerName: ${_this.customerName})';
}


}

/// @nodoc
abstract mixin class $InvoiceCopyWith<$Res>  {
  factory $InvoiceCopyWith(Invoice value, $Res Function(Invoice) _then) = _$InvoiceCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId,@JsonKey(name: 'invoice_number') String invoiceNumber,@JsonKey(name: 'customer_id') String? customerId,@JsonKey(name: 'store_id') String? storeId, InvoiceStatus status,@JsonKey(name: 'subtotal') String subtotal,@JsonKey(name: 'tax_total') String taxTotal,@JsonKey(name: 'discount_total') String discountTotal,@JsonKey(name: 'total_amount') String totalAmount,@JsonKey(name: 'paid_amount') String paidAmount, String currency,@JsonKey(name: 'allow_partial_payment') bool allowPartialPayment,@JsonKey(name: 'allow_split_payment') bool allowSplitPayment,@JsonKey(name: 'due_date') String? dueDate, String? notes,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'updated_at') String? updatedAt, List<InvoiceItem> items,@JsonKey(name: 'customer_name') String? customerName
});




}
/// @nodoc
class _$InvoiceCopyWithImpl<$Res>
    implements $InvoiceCopyWith<$Res> {
  _$InvoiceCopyWithImpl(this._self, this._then);

  final Invoice _self;
  final $Res Function(Invoice) _then;

/// Create a copy of Invoice
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? merchantId = null,Object? invoiceNumber = null,Object? customerId = freezed,Object? storeId = freezed,Object? status = null,Object? subtotal = null,Object? taxTotal = null,Object? discountTotal = null,Object? totalAmount = null,Object? paidAmount = null,Object? currency = null,Object? allowPartialPayment = null,Object? allowSplitPayment = null,Object? dueDate = freezed,Object? notes = freezed,Object? createdAt = freezed,Object? updatedAt = freezed,Object? items = null,Object? customerName = freezed,}) {
  return _then(Invoice(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,invoiceNumber: null == invoiceNumber ? _self.invoiceNumber : invoiceNumber // ignore: cast_nullable_to_non_nullable
as String,customerId: freezed == customerId ? _self.customerId : customerId // ignore: cast_nullable_to_non_nullable
as String?,storeId: freezed == storeId ? _self.storeId : storeId // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as InvoiceStatus,subtotal: null == subtotal ? _self.subtotal : subtotal // ignore: cast_nullable_to_non_nullable
as String,taxTotal: null == taxTotal ? _self.taxTotal : taxTotal // ignore: cast_nullable_to_non_nullable
as String,discountTotal: null == discountTotal ? _self.discountTotal : discountTotal // ignore: cast_nullable_to_non_nullable
as String,totalAmount: null == totalAmount ? _self.totalAmount : totalAmount // ignore: cast_nullable_to_non_nullable
as String,paidAmount: null == paidAmount ? _self.paidAmount : paidAmount // ignore: cast_nullable_to_non_nullable
as String,currency: null == currency ? _self.currency : currency // ignore: cast_nullable_to_non_nullable
as String,allowPartialPayment: null == allowPartialPayment ? _self.allowPartialPayment : allowPartialPayment // ignore: cast_nullable_to_non_nullable
as bool,allowSplitPayment: null == allowSplitPayment ? _self.allowSplitPayment : allowSplitPayment // ignore: cast_nullable_to_non_nullable
as bool,dueDate: freezed == dueDate ? _self.dueDate : dueDate // ignore: cast_nullable_to_non_nullable
as String?,notes: freezed == notes ? _self.notes : notes // ignore: cast_nullable_to_non_nullable
as String?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,updatedAt: freezed == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String?,items: null == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as List<InvoiceItem>,customerName: freezed == customerName ? _self.customerName : customerName // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [Invoice].
extension InvoicePatterns on Invoice {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Invoice value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Invoice() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Invoice value)  $default,){
final _that = this;
switch (_that) {
case _Invoice():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Invoice value)?  $default,){
final _that = this;
switch (_that) {
case _Invoice() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'invoice_number')  String invoiceNumber, @JsonKey(name: 'customer_id')  String? customerId, @JsonKey(name: 'store_id')  String? storeId,  InvoiceStatus status, @JsonKey(name: 'subtotal')  String subtotal, @JsonKey(name: 'tax_total')  String taxTotal, @JsonKey(name: 'discount_total')  String discountTotal, @JsonKey(name: 'total_amount')  String totalAmount, @JsonKey(name: 'paid_amount')  String paidAmount,  String currency, @JsonKey(name: 'allow_partial_payment')  bool allowPartialPayment, @JsonKey(name: 'allow_split_payment')  bool allowSplitPayment, @JsonKey(name: 'due_date')  String? dueDate,  String? notes, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'updated_at')  String? updatedAt,  List<InvoiceItem> items, @JsonKey(name: 'customer_name')  String? customerName)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Invoice() when $default != null:
return $default(_that.id,_that.merchantId,_that.invoiceNumber,_that.customerId,_that.storeId,_that.status,_that.subtotal,_that.taxTotal,_that.discountTotal,_that.totalAmount,_that.paidAmount,_that.currency,_that.allowPartialPayment,_that.allowSplitPayment,_that.dueDate,_that.notes,_that.createdAt,_that.updatedAt,_that.items,_that.customerName);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'invoice_number')  String invoiceNumber, @JsonKey(name: 'customer_id')  String? customerId, @JsonKey(name: 'store_id')  String? storeId,  InvoiceStatus status, @JsonKey(name: 'subtotal')  String subtotal, @JsonKey(name: 'tax_total')  String taxTotal, @JsonKey(name: 'discount_total')  String discountTotal, @JsonKey(name: 'total_amount')  String totalAmount, @JsonKey(name: 'paid_amount')  String paidAmount,  String currency, @JsonKey(name: 'allow_partial_payment')  bool allowPartialPayment, @JsonKey(name: 'allow_split_payment')  bool allowSplitPayment, @JsonKey(name: 'due_date')  String? dueDate,  String? notes, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'updated_at')  String? updatedAt,  List<InvoiceItem> items, @JsonKey(name: 'customer_name')  String? customerName)  $default,) {final _that = this;
switch (_that) {
case _Invoice():
return $default(_that.id,_that.merchantId,_that.invoiceNumber,_that.customerId,_that.storeId,_that.status,_that.subtotal,_that.taxTotal,_that.discountTotal,_that.totalAmount,_that.paidAmount,_that.currency,_that.allowPartialPayment,_that.allowSplitPayment,_that.dueDate,_that.notes,_that.createdAt,_that.updatedAt,_that.items,_that.customerName);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'invoice_number')  String invoiceNumber, @JsonKey(name: 'customer_id')  String? customerId, @JsonKey(name: 'store_id')  String? storeId,  InvoiceStatus status, @JsonKey(name: 'subtotal')  String subtotal, @JsonKey(name: 'tax_total')  String taxTotal, @JsonKey(name: 'discount_total')  String discountTotal, @JsonKey(name: 'total_amount')  String totalAmount, @JsonKey(name: 'paid_amount')  String paidAmount,  String currency, @JsonKey(name: 'allow_partial_payment')  bool allowPartialPayment, @JsonKey(name: 'allow_split_payment')  bool allowSplitPayment, @JsonKey(name: 'due_date')  String? dueDate,  String? notes, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'updated_at')  String? updatedAt,  List<InvoiceItem> items, @JsonKey(name: 'customer_name')  String? customerName)?  $default,) {final _that = this;
switch (_that) {
case _Invoice() when $default != null:
return $default(_that.id,_that.merchantId,_that.invoiceNumber,_that.customerId,_that.storeId,_that.status,_that.subtotal,_that.taxTotal,_that.discountTotal,_that.totalAmount,_that.paidAmount,_that.currency,_that.allowPartialPayment,_that.allowSplitPayment,_that.dueDate,_that.notes,_that.createdAt,_that.updatedAt,_that.items,_that.customerName);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Invoice implements Invoice {
  const _Invoice({required this.id, @JsonKey(name: 'merchant_id') required this.merchantId, @JsonKey(name: 'invoice_number') required this.invoiceNumber, @JsonKey(name: 'customer_id') this.customerId, @JsonKey(name: 'store_id') this.storeId, this.status = InvoiceStatus.draft, @JsonKey(name: 'subtotal') required this.subtotal, @JsonKey(name: 'tax_total') required this.taxTotal, @JsonKey(name: 'discount_total') required this.discountTotal, @JsonKey(name: 'total_amount') required this.totalAmount, @JsonKey(name: 'paid_amount') required this.paidAmount, this.currency = 'INR', @JsonKey(name: 'allow_partial_payment') this.allowPartialPayment = false, @JsonKey(name: 'allow_split_payment') this.allowSplitPayment = false, @JsonKey(name: 'due_date') this.dueDate, this.notes, @JsonKey(name: 'created_at') this.createdAt, @JsonKey(name: 'updated_at') this.updatedAt,  List<InvoiceItem> items = const [], @JsonKey(name: 'customer_name') this.customerName}): _items = items;
  factory _Invoice.fromJson(Map<String, dynamic> json) => _$InvoiceFromJson(json);

@override final  String id;
@override@JsonKey(name: 'merchant_id') final  String merchantId;
@override@JsonKey(name: 'invoice_number') final  String invoiceNumber;
@override@JsonKey(name: 'customer_id') final  String? customerId;
@override@JsonKey(name: 'store_id') final  String? storeId;
@override@JsonKey() final  InvoiceStatus status;
@override@JsonKey(name: 'subtotal') final  String subtotal;
@override@JsonKey(name: 'tax_total') final  String taxTotal;
@override@JsonKey(name: 'discount_total') final  String discountTotal;
@override@JsonKey(name: 'total_amount') final  String totalAmount;
@override@JsonKey(name: 'paid_amount') final  String paidAmount;
@override@JsonKey() final  String currency;
@override@JsonKey(name: 'allow_partial_payment') final  bool allowPartialPayment;
@override@JsonKey(name: 'allow_split_payment') final  bool allowSplitPayment;
@override@JsonKey(name: 'due_date') final  String? dueDate;
@override final  String? notes;
@override@JsonKey(name: 'created_at') final  String? createdAt;
@override@JsonKey(name: 'updated_at') final  String? updatedAt;
 final  List<InvoiceItem> _items;
@override@JsonKey() List<InvoiceItem> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}

@override@JsonKey(name: 'customer_name') final  String? customerName;

/// Create a copy of Invoice
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$InvoiceCopyWith<_Invoice> get copyWith => __$InvoiceCopyWithImpl<_Invoice>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$InvoiceToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Invoice&&(identical(other.id, id) || other.id == id)&&(identical(other.merchantId, merchantId) || other.merchantId == merchantId)&&(identical(other.invoiceNumber, invoiceNumber) || other.invoiceNumber == invoiceNumber)&&(identical(other.customerId, customerId) || other.customerId == customerId)&&(identical(other.storeId, storeId) || other.storeId == storeId)&&(identical(other.status, status) || other.status == status)&&(identical(other.subtotal, subtotal) || other.subtotal == subtotal)&&(identical(other.taxTotal, taxTotal) || other.taxTotal == taxTotal)&&(identical(other.discountTotal, discountTotal) || other.discountTotal == discountTotal)&&(identical(other.totalAmount, totalAmount) || other.totalAmount == totalAmount)&&(identical(other.paidAmount, paidAmount) || other.paidAmount == paidAmount)&&(identical(other.currency, currency) || other.currency == currency)&&(identical(other.allowPartialPayment, allowPartialPayment) || other.allowPartialPayment == allowPartialPayment)&&(identical(other.allowSplitPayment, allowSplitPayment) || other.allowSplitPayment == allowSplitPayment)&&(identical(other.dueDate, dueDate) || other.dueDate == dueDate)&&(identical(other.notes, notes) || other.notes == notes)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&const DeepCollectionEquality().equals(other.items, _items)&&(identical(other.customerName, customerName) || other.customerName == customerName));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hashAll([runtimeType,id,merchantId,invoiceNumber,customerId,storeId,status,subtotal,taxTotal,discountTotal,totalAmount,paidAmount,currency,allowPartialPayment,allowSplitPayment,dueDate,notes,createdAt,updatedAt,const DeepCollectionEquality().hash(_items),customerName]);
}

@override
String toString() {
    return 'Invoice(id: $id, merchantId: $merchantId, invoiceNumber: $invoiceNumber, customerId: $customerId, storeId: $storeId, status: $status, subtotal: $subtotal, taxTotal: $taxTotal, discountTotal: $discountTotal, totalAmount: $totalAmount, paidAmount: $paidAmount, currency: $currency, allowPartialPayment: $allowPartialPayment, allowSplitPayment: $allowSplitPayment, dueDate: $dueDate, notes: $notes, createdAt: $createdAt, updatedAt: $updatedAt, items: $items, customerName: $customerName)';
}


}

/// @nodoc
abstract mixin class _$InvoiceCopyWith<$Res> implements $InvoiceCopyWith<$Res> {
  factory _$InvoiceCopyWith(_Invoice value, $Res Function(_Invoice) _then) = __$InvoiceCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId,@JsonKey(name: 'invoice_number') String invoiceNumber,@JsonKey(name: 'customer_id') String? customerId,@JsonKey(name: 'store_id') String? storeId, InvoiceStatus status,@JsonKey(name: 'subtotal') String subtotal,@JsonKey(name: 'tax_total') String taxTotal,@JsonKey(name: 'discount_total') String discountTotal,@JsonKey(name: 'total_amount') String totalAmount,@JsonKey(name: 'paid_amount') String paidAmount, String currency,@JsonKey(name: 'allow_partial_payment') bool allowPartialPayment,@JsonKey(name: 'allow_split_payment') bool allowSplitPayment,@JsonKey(name: 'due_date') String? dueDate, String? notes,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'updated_at') String? updatedAt, List<InvoiceItem> items,@JsonKey(name: 'customer_name') String? customerName
});




}
/// @nodoc
class __$InvoiceCopyWithImpl<$Res>
    implements _$InvoiceCopyWith<$Res> {
  __$InvoiceCopyWithImpl(this._self, this._then);

  final _Invoice _self;
  final $Res Function(_Invoice) _then;

/// Create a copy of Invoice
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? merchantId = null,Object? invoiceNumber = null,Object? customerId = freezed,Object? storeId = freezed,Object? status = null,Object? subtotal = null,Object? taxTotal = null,Object? discountTotal = null,Object? totalAmount = null,Object? paidAmount = null,Object? currency = null,Object? allowPartialPayment = null,Object? allowSplitPayment = null,Object? dueDate = freezed,Object? notes = freezed,Object? createdAt = freezed,Object? updatedAt = freezed,Object? items = null,Object? customerName = freezed,}) {
  return _then(_Invoice(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,invoiceNumber: null == invoiceNumber ? _self.invoiceNumber : invoiceNumber // ignore: cast_nullable_to_non_nullable
as String,customerId: freezed == customerId ? _self.customerId : customerId // ignore: cast_nullable_to_non_nullable
as String?,storeId: freezed == storeId ? _self.storeId : storeId // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as InvoiceStatus,subtotal: null == subtotal ? _self.subtotal : subtotal // ignore: cast_nullable_to_non_nullable
as String,taxTotal: null == taxTotal ? _self.taxTotal : taxTotal // ignore: cast_nullable_to_non_nullable
as String,discountTotal: null == discountTotal ? _self.discountTotal : discountTotal // ignore: cast_nullable_to_non_nullable
as String,totalAmount: null == totalAmount ? _self.totalAmount : totalAmount // ignore: cast_nullable_to_non_nullable
as String,paidAmount: null == paidAmount ? _self.paidAmount : paidAmount // ignore: cast_nullable_to_non_nullable
as String,currency: null == currency ? _self.currency : currency // ignore: cast_nullable_to_non_nullable
as String,allowPartialPayment: null == allowPartialPayment ? _self.allowPartialPayment : allowPartialPayment // ignore: cast_nullable_to_non_nullable
as bool,allowSplitPayment: null == allowSplitPayment ? _self.allowSplitPayment : allowSplitPayment // ignore: cast_nullable_to_non_nullable
as bool,dueDate: freezed == dueDate ? _self.dueDate : dueDate // ignore: cast_nullable_to_non_nullable
as String?,notes: freezed == notes ? _self.notes : notes // ignore: cast_nullable_to_non_nullable
as String?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,updatedAt: freezed == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String?,items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<InvoiceItem>,customerName: freezed == customerName ? _self.customerName : customerName // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$CreateInvoiceRequest {

@JsonKey(name: 'customer_id') String? get customerId;@JsonKey(name: 'store_id') String? get storeId;@JsonKey(name: 'due_date') String? get dueDate; String? get notes;@JsonKey(name: 'allow_partial_payment') bool get allowPartialPayment;@JsonKey(name: 'allow_split_payment') bool get allowSplitPayment; List<Map<String, dynamic>> get items;
/// Create a copy of CreateInvoiceRequest
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CreateInvoiceRequestCopyWith<CreateInvoiceRequest> get copyWith => _$CreateInvoiceRequestCopyWithImpl<CreateInvoiceRequest>(this as CreateInvoiceRequest, _$identity);

  /// Serializes this CreateInvoiceRequest to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as CreateInvoiceRequest;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CreateInvoiceRequest&&(identical(other.customerId, _this.customerId) || other.customerId == _this.customerId)&&(identical(other.storeId, _this.storeId) || other.storeId == _this.storeId)&&(identical(other.dueDate, _this.dueDate) || other.dueDate == _this.dueDate)&&(identical(other.notes, _this.notes) || other.notes == _this.notes)&&(identical(other.allowPartialPayment, _this.allowPartialPayment) || other.allowPartialPayment == _this.allowPartialPayment)&&(identical(other.allowSplitPayment, _this.allowSplitPayment) || other.allowSplitPayment == _this.allowSplitPayment)&&const DeepCollectionEquality().equals(other.items, _this.items));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as CreateInvoiceRequest;
  return Object.hash(runtimeType,_this.customerId,_this.storeId,_this.dueDate,_this.notes,_this.allowPartialPayment,_this.allowSplitPayment,const DeepCollectionEquality().hash(_this.items));
}

@override
String toString() {
  final _this = this as CreateInvoiceRequest;
  return 'CreateInvoiceRequest(customerId: ${_this.customerId}, storeId: ${_this.storeId}, dueDate: ${_this.dueDate}, notes: ${_this.notes}, allowPartialPayment: ${_this.allowPartialPayment}, allowSplitPayment: ${_this.allowSplitPayment}, items: ${_this.items})';
}


}

/// @nodoc
abstract mixin class $CreateInvoiceRequestCopyWith<$Res>  {
  factory $CreateInvoiceRequestCopyWith(CreateInvoiceRequest value, $Res Function(CreateInvoiceRequest) _then) = _$CreateInvoiceRequestCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'customer_id') String? customerId,@JsonKey(name: 'store_id') String? storeId,@JsonKey(name: 'due_date') String? dueDate, String? notes,@JsonKey(name: 'allow_partial_payment') bool allowPartialPayment,@JsonKey(name: 'allow_split_payment') bool allowSplitPayment, List<Map<String, dynamic>> items
});




}
/// @nodoc
class _$CreateInvoiceRequestCopyWithImpl<$Res>
    implements $CreateInvoiceRequestCopyWith<$Res> {
  _$CreateInvoiceRequestCopyWithImpl(this._self, this._then);

  final CreateInvoiceRequest _self;
  final $Res Function(CreateInvoiceRequest) _then;

/// Create a copy of CreateInvoiceRequest
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? customerId = freezed,Object? storeId = freezed,Object? dueDate = freezed,Object? notes = freezed,Object? allowPartialPayment = null,Object? allowSplitPayment = null,Object? items = null,}) {
  return _then(CreateInvoiceRequest(
customerId: freezed == customerId ? _self.customerId : customerId // ignore: cast_nullable_to_non_nullable
as String?,storeId: freezed == storeId ? _self.storeId : storeId // ignore: cast_nullable_to_non_nullable
as String?,dueDate: freezed == dueDate ? _self.dueDate : dueDate // ignore: cast_nullable_to_non_nullable
as String?,notes: freezed == notes ? _self.notes : notes // ignore: cast_nullable_to_non_nullable
as String?,allowPartialPayment: null == allowPartialPayment ? _self.allowPartialPayment : allowPartialPayment // ignore: cast_nullable_to_non_nullable
as bool,allowSplitPayment: null == allowSplitPayment ? _self.allowSplitPayment : allowSplitPayment // ignore: cast_nullable_to_non_nullable
as bool,items: null == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as List<Map<String, dynamic>>,
  ));
}

}


/// Adds pattern-matching-related methods to [CreateInvoiceRequest].
extension CreateInvoiceRequestPatterns on CreateInvoiceRequest {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CreateInvoiceRequest value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CreateInvoiceRequest() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CreateInvoiceRequest value)  $default,){
final _that = this;
switch (_that) {
case _CreateInvoiceRequest():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CreateInvoiceRequest value)?  $default,){
final _that = this;
switch (_that) {
case _CreateInvoiceRequest() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'customer_id')  String? customerId, @JsonKey(name: 'store_id')  String? storeId, @JsonKey(name: 'due_date')  String? dueDate,  String? notes, @JsonKey(name: 'allow_partial_payment')  bool allowPartialPayment, @JsonKey(name: 'allow_split_payment')  bool allowSplitPayment,  List<Map<String, dynamic>> items)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CreateInvoiceRequest() when $default != null:
return $default(_that.customerId,_that.storeId,_that.dueDate,_that.notes,_that.allowPartialPayment,_that.allowSplitPayment,_that.items);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'customer_id')  String? customerId, @JsonKey(name: 'store_id')  String? storeId, @JsonKey(name: 'due_date')  String? dueDate,  String? notes, @JsonKey(name: 'allow_partial_payment')  bool allowPartialPayment, @JsonKey(name: 'allow_split_payment')  bool allowSplitPayment,  List<Map<String, dynamic>> items)  $default,) {final _that = this;
switch (_that) {
case _CreateInvoiceRequest():
return $default(_that.customerId,_that.storeId,_that.dueDate,_that.notes,_that.allowPartialPayment,_that.allowSplitPayment,_that.items);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'customer_id')  String? customerId, @JsonKey(name: 'store_id')  String? storeId, @JsonKey(name: 'due_date')  String? dueDate,  String? notes, @JsonKey(name: 'allow_partial_payment')  bool allowPartialPayment, @JsonKey(name: 'allow_split_payment')  bool allowSplitPayment,  List<Map<String, dynamic>> items)?  $default,) {final _that = this;
switch (_that) {
case _CreateInvoiceRequest() when $default != null:
return $default(_that.customerId,_that.storeId,_that.dueDate,_that.notes,_that.allowPartialPayment,_that.allowSplitPayment,_that.items);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CreateInvoiceRequest implements CreateInvoiceRequest {
  const _CreateInvoiceRequest({@JsonKey(name: 'customer_id') this.customerId, @JsonKey(name: 'store_id') this.storeId, @JsonKey(name: 'due_date') this.dueDate, this.notes, @JsonKey(name: 'allow_partial_payment') this.allowPartialPayment = false, @JsonKey(name: 'allow_split_payment') this.allowSplitPayment = false,  List<Map<String, dynamic>> items = const []}): _items = items;
  factory _CreateInvoiceRequest.fromJson(Map<String, dynamic> json) => _$CreateInvoiceRequestFromJson(json);

@override@JsonKey(name: 'customer_id') final  String? customerId;
@override@JsonKey(name: 'store_id') final  String? storeId;
@override@JsonKey(name: 'due_date') final  String? dueDate;
@override final  String? notes;
@override@JsonKey(name: 'allow_partial_payment') final  bool allowPartialPayment;
@override@JsonKey(name: 'allow_split_payment') final  bool allowSplitPayment;
 final  List<Map<String, dynamic>> _items;
@override@JsonKey() List<Map<String, dynamic>> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}


/// Create a copy of CreateInvoiceRequest
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CreateInvoiceRequestCopyWith<_CreateInvoiceRequest> get copyWith => __$CreateInvoiceRequestCopyWithImpl<_CreateInvoiceRequest>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CreateInvoiceRequestToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _CreateInvoiceRequest&&(identical(other.customerId, customerId) || other.customerId == customerId)&&(identical(other.storeId, storeId) || other.storeId == storeId)&&(identical(other.dueDate, dueDate) || other.dueDate == dueDate)&&(identical(other.notes, notes) || other.notes == notes)&&(identical(other.allowPartialPayment, allowPartialPayment) || other.allowPartialPayment == allowPartialPayment)&&(identical(other.allowSplitPayment, allowSplitPayment) || other.allowSplitPayment == allowSplitPayment)&&const DeepCollectionEquality().equals(other.items, _items));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,customerId,storeId,dueDate,notes,allowPartialPayment,allowSplitPayment,const DeepCollectionEquality().hash(_items));
}

@override
String toString() {
    return 'CreateInvoiceRequest(customerId: $customerId, storeId: $storeId, dueDate: $dueDate, notes: $notes, allowPartialPayment: $allowPartialPayment, allowSplitPayment: $allowSplitPayment, items: $items)';
}


}

/// @nodoc
abstract mixin class _$CreateInvoiceRequestCopyWith<$Res> implements $CreateInvoiceRequestCopyWith<$Res> {
  factory _$CreateInvoiceRequestCopyWith(_CreateInvoiceRequest value, $Res Function(_CreateInvoiceRequest) _then) = __$CreateInvoiceRequestCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'customer_id') String? customerId,@JsonKey(name: 'store_id') String? storeId,@JsonKey(name: 'due_date') String? dueDate, String? notes,@JsonKey(name: 'allow_partial_payment') bool allowPartialPayment,@JsonKey(name: 'allow_split_payment') bool allowSplitPayment, List<Map<String, dynamic>> items
});




}
/// @nodoc
class __$CreateInvoiceRequestCopyWithImpl<$Res>
    implements _$CreateInvoiceRequestCopyWith<$Res> {
  __$CreateInvoiceRequestCopyWithImpl(this._self, this._then);

  final _CreateInvoiceRequest _self;
  final $Res Function(_CreateInvoiceRequest) _then;

/// Create a copy of CreateInvoiceRequest
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? customerId = freezed,Object? storeId = freezed,Object? dueDate = freezed,Object? notes = freezed,Object? allowPartialPayment = null,Object? allowSplitPayment = null,Object? items = null,}) {
  return _then(_CreateInvoiceRequest(
customerId: freezed == customerId ? _self.customerId : customerId // ignore: cast_nullable_to_non_nullable
as String?,storeId: freezed == storeId ? _self.storeId : storeId // ignore: cast_nullable_to_non_nullable
as String?,dueDate: freezed == dueDate ? _self.dueDate : dueDate // ignore: cast_nullable_to_non_nullable
as String?,notes: freezed == notes ? _self.notes : notes // ignore: cast_nullable_to_non_nullable
as String?,allowPartialPayment: null == allowPartialPayment ? _self.allowPartialPayment : allowPartialPayment // ignore: cast_nullable_to_non_nullable
as bool,allowSplitPayment: null == allowSplitPayment ? _self.allowSplitPayment : allowSplitPayment // ignore: cast_nullable_to_non_nullable
as bool,items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<Map<String, dynamic>>,
  ));
}


}


/// @nodoc
mixin _$Installment {

 String get id;@JsonKey(name: 'installment_number') int get installmentNumber; String? get label; String get amount;@JsonKey(name: 'paid_amount') String get paidAmount;@JsonKey(name: 'due_date') String get dueDate; InstallmentStatus get status;
/// Create a copy of Installment
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$InstallmentCopyWith<Installment> get copyWith => _$InstallmentCopyWithImpl<Installment>(this as Installment, _$identity);

  /// Serializes this Installment to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Installment;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Installment&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.installmentNumber, _this.installmentNumber) || other.installmentNumber == _this.installmentNumber)&&(identical(other.label, _this.label) || other.label == _this.label)&&(identical(other.amount, _this.amount) || other.amount == _this.amount)&&(identical(other.paidAmount, _this.paidAmount) || other.paidAmount == _this.paidAmount)&&(identical(other.dueDate, _this.dueDate) || other.dueDate == _this.dueDate)&&(identical(other.status, _this.status) || other.status == _this.status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Installment;
  return Object.hash(runtimeType,_this.id,_this.installmentNumber,_this.label,_this.amount,_this.paidAmount,_this.dueDate,_this.status);
}

@override
String toString() {
  final _this = this as Installment;
  return 'Installment(id: ${_this.id}, installmentNumber: ${_this.installmentNumber}, label: ${_this.label}, amount: ${_this.amount}, paidAmount: ${_this.paidAmount}, dueDate: ${_this.dueDate}, status: ${_this.status})';
}


}

/// @nodoc
abstract mixin class $InstallmentCopyWith<$Res>  {
  factory $InstallmentCopyWith(Installment value, $Res Function(Installment) _then) = _$InstallmentCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'installment_number') int installmentNumber, String? label, String amount,@JsonKey(name: 'paid_amount') String paidAmount,@JsonKey(name: 'due_date') String dueDate, InstallmentStatus status
});




}
/// @nodoc
class _$InstallmentCopyWithImpl<$Res>
    implements $InstallmentCopyWith<$Res> {
  _$InstallmentCopyWithImpl(this._self, this._then);

  final Installment _self;
  final $Res Function(Installment) _then;

/// Create a copy of Installment
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? installmentNumber = null,Object? label = freezed,Object? amount = null,Object? paidAmount = null,Object? dueDate = null,Object? status = null,}) {
  return _then(Installment(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,installmentNumber: null == installmentNumber ? _self.installmentNumber : installmentNumber // ignore: cast_nullable_to_non_nullable
as int,label: freezed == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String?,amount: null == amount ? _self.amount : amount // ignore: cast_nullable_to_non_nullable
as String,paidAmount: null == paidAmount ? _self.paidAmount : paidAmount // ignore: cast_nullable_to_non_nullable
as String,dueDate: null == dueDate ? _self.dueDate : dueDate // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as InstallmentStatus,
  ));
}

}


/// Adds pattern-matching-related methods to [Installment].
extension InstallmentPatterns on Installment {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Installment value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Installment() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Installment value)  $default,){
final _that = this;
switch (_that) {
case _Installment():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Installment value)?  $default,){
final _that = this;
switch (_that) {
case _Installment() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'installment_number')  int installmentNumber,  String? label,  String amount, @JsonKey(name: 'paid_amount')  String paidAmount, @JsonKey(name: 'due_date')  String dueDate,  InstallmentStatus status)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Installment() when $default != null:
return $default(_that.id,_that.installmentNumber,_that.label,_that.amount,_that.paidAmount,_that.dueDate,_that.status);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'installment_number')  int installmentNumber,  String? label,  String amount, @JsonKey(name: 'paid_amount')  String paidAmount, @JsonKey(name: 'due_date')  String dueDate,  InstallmentStatus status)  $default,) {final _that = this;
switch (_that) {
case _Installment():
return $default(_that.id,_that.installmentNumber,_that.label,_that.amount,_that.paidAmount,_that.dueDate,_that.status);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'installment_number')  int installmentNumber,  String? label,  String amount, @JsonKey(name: 'paid_amount')  String paidAmount, @JsonKey(name: 'due_date')  String dueDate,  InstallmentStatus status)?  $default,) {final _that = this;
switch (_that) {
case _Installment() when $default != null:
return $default(_that.id,_that.installmentNumber,_that.label,_that.amount,_that.paidAmount,_that.dueDate,_that.status);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Installment implements Installment {
  const _Installment({required this.id, @JsonKey(name: 'installment_number') required this.installmentNumber, this.label, required this.amount, @JsonKey(name: 'paid_amount') required this.paidAmount, @JsonKey(name: 'due_date') required this.dueDate, this.status = InstallmentStatus.pending});
  factory _Installment.fromJson(Map<String, dynamic> json) => _$InstallmentFromJson(json);

@override final  String id;
@override@JsonKey(name: 'installment_number') final  int installmentNumber;
@override final  String? label;
@override final  String amount;
@override@JsonKey(name: 'paid_amount') final  String paidAmount;
@override@JsonKey(name: 'due_date') final  String dueDate;
@override@JsonKey() final  InstallmentStatus status;

/// Create a copy of Installment
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$InstallmentCopyWith<_Installment> get copyWith => __$InstallmentCopyWithImpl<_Installment>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$InstallmentToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Installment&&(identical(other.id, id) || other.id == id)&&(identical(other.installmentNumber, installmentNumber) || other.installmentNumber == installmentNumber)&&(identical(other.label, label) || other.label == label)&&(identical(other.amount, amount) || other.amount == amount)&&(identical(other.paidAmount, paidAmount) || other.paidAmount == paidAmount)&&(identical(other.dueDate, dueDate) || other.dueDate == dueDate)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,installmentNumber,label,amount,paidAmount,dueDate,status);
}

@override
String toString() {
    return 'Installment(id: $id, installmentNumber: $installmentNumber, label: $label, amount: $amount, paidAmount: $paidAmount, dueDate: $dueDate, status: $status)';
}


}

/// @nodoc
abstract mixin class _$InstallmentCopyWith<$Res> implements $InstallmentCopyWith<$Res> {
  factory _$InstallmentCopyWith(_Installment value, $Res Function(_Installment) _then) = __$InstallmentCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'installment_number') int installmentNumber, String? label, String amount,@JsonKey(name: 'paid_amount') String paidAmount,@JsonKey(name: 'due_date') String dueDate, InstallmentStatus status
});




}
/// @nodoc
class __$InstallmentCopyWithImpl<$Res>
    implements _$InstallmentCopyWith<$Res> {
  __$InstallmentCopyWithImpl(this._self, this._then);

  final _Installment _self;
  final $Res Function(_Installment) _then;

/// Create a copy of Installment
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? installmentNumber = null,Object? label = freezed,Object? amount = null,Object? paidAmount = null,Object? dueDate = null,Object? status = null,}) {
  return _then(_Installment(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,installmentNumber: null == installmentNumber ? _self.installmentNumber : installmentNumber // ignore: cast_nullable_to_non_nullable
as int,label: freezed == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String?,amount: null == amount ? _self.amount : amount // ignore: cast_nullable_to_non_nullable
as String,paidAmount: null == paidAmount ? _self.paidAmount : paidAmount // ignore: cast_nullable_to_non_nullable
as String,dueDate: null == dueDate ? _self.dueDate : dueDate // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as InstallmentStatus,
  ));
}


}


/// @nodoc
mixin _$PaymentPlan {

 String get id;@JsonKey(name: 'merchant_id') String get merchantId;@JsonKey(name: 'invoice_id') String? get invoiceId;@JsonKey(name: 'customer_id') String? get customerId;@JsonKey(name: 'plan_type') PlanType get planType;@JsonKey(name: 'total_amount') String get totalAmount; PlanStatus get status; List<Installment> get installments;
/// Create a copy of PaymentPlan
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PaymentPlanCopyWith<PaymentPlan> get copyWith => _$PaymentPlanCopyWithImpl<PaymentPlan>(this as PaymentPlan, _$identity);

  /// Serializes this PaymentPlan to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as PaymentPlan;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PaymentPlan&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.merchantId, _this.merchantId) || other.merchantId == _this.merchantId)&&(identical(other.invoiceId, _this.invoiceId) || other.invoiceId == _this.invoiceId)&&(identical(other.customerId, _this.customerId) || other.customerId == _this.customerId)&&(identical(other.planType, _this.planType) || other.planType == _this.planType)&&(identical(other.totalAmount, _this.totalAmount) || other.totalAmount == _this.totalAmount)&&(identical(other.status, _this.status) || other.status == _this.status)&&const DeepCollectionEquality().equals(other.installments, _this.installments));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as PaymentPlan;
  return Object.hash(runtimeType,_this.id,_this.merchantId,_this.invoiceId,_this.customerId,_this.planType,_this.totalAmount,_this.status,const DeepCollectionEquality().hash(_this.installments));
}

@override
String toString() {
  final _this = this as PaymentPlan;
  return 'PaymentPlan(id: ${_this.id}, merchantId: ${_this.merchantId}, invoiceId: ${_this.invoiceId}, customerId: ${_this.customerId}, planType: ${_this.planType}, totalAmount: ${_this.totalAmount}, status: ${_this.status}, installments: ${_this.installments})';
}


}

/// @nodoc
abstract mixin class $PaymentPlanCopyWith<$Res>  {
  factory $PaymentPlanCopyWith(PaymentPlan value, $Res Function(PaymentPlan) _then) = _$PaymentPlanCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId,@JsonKey(name: 'invoice_id') String? invoiceId,@JsonKey(name: 'customer_id') String? customerId,@JsonKey(name: 'plan_type') PlanType planType,@JsonKey(name: 'total_amount') String totalAmount, PlanStatus status, List<Installment> installments
});




}
/// @nodoc
class _$PaymentPlanCopyWithImpl<$Res>
    implements $PaymentPlanCopyWith<$Res> {
  _$PaymentPlanCopyWithImpl(this._self, this._then);

  final PaymentPlan _self;
  final $Res Function(PaymentPlan) _then;

/// Create a copy of PaymentPlan
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? merchantId = null,Object? invoiceId = freezed,Object? customerId = freezed,Object? planType = null,Object? totalAmount = null,Object? status = null,Object? installments = null,}) {
  return _then(PaymentPlan(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,invoiceId: freezed == invoiceId ? _self.invoiceId : invoiceId // ignore: cast_nullable_to_non_nullable
as String?,customerId: freezed == customerId ? _self.customerId : customerId // ignore: cast_nullable_to_non_nullable
as String?,planType: null == planType ? _self.planType : planType // ignore: cast_nullable_to_non_nullable
as PlanType,totalAmount: null == totalAmount ? _self.totalAmount : totalAmount // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as PlanStatus,installments: null == installments ? _self.installments : installments // ignore: cast_nullable_to_non_nullable
as List<Installment>,
  ));
}

}


/// Adds pattern-matching-related methods to [PaymentPlan].
extension PaymentPlanPatterns on PaymentPlan {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PaymentPlan value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PaymentPlan() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PaymentPlan value)  $default,){
final _that = this;
switch (_that) {
case _PaymentPlan():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PaymentPlan value)?  $default,){
final _that = this;
switch (_that) {
case _PaymentPlan() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'invoice_id')  String? invoiceId, @JsonKey(name: 'customer_id')  String? customerId, @JsonKey(name: 'plan_type')  PlanType planType, @JsonKey(name: 'total_amount')  String totalAmount,  PlanStatus status,  List<Installment> installments)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PaymentPlan() when $default != null:
return $default(_that.id,_that.merchantId,_that.invoiceId,_that.customerId,_that.planType,_that.totalAmount,_that.status,_that.installments);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'invoice_id')  String? invoiceId, @JsonKey(name: 'customer_id')  String? customerId, @JsonKey(name: 'plan_type')  PlanType planType, @JsonKey(name: 'total_amount')  String totalAmount,  PlanStatus status,  List<Installment> installments)  $default,) {final _that = this;
switch (_that) {
case _PaymentPlan():
return $default(_that.id,_that.merchantId,_that.invoiceId,_that.customerId,_that.planType,_that.totalAmount,_that.status,_that.installments);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'invoice_id')  String? invoiceId, @JsonKey(name: 'customer_id')  String? customerId, @JsonKey(name: 'plan_type')  PlanType planType, @JsonKey(name: 'total_amount')  String totalAmount,  PlanStatus status,  List<Installment> installments)?  $default,) {final _that = this;
switch (_that) {
case _PaymentPlan() when $default != null:
return $default(_that.id,_that.merchantId,_that.invoiceId,_that.customerId,_that.planType,_that.totalAmount,_that.status,_that.installments);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PaymentPlan implements PaymentPlan {
  const _PaymentPlan({required this.id, @JsonKey(name: 'merchant_id') required this.merchantId, @JsonKey(name: 'invoice_id') this.invoiceId, @JsonKey(name: 'customer_id') this.customerId, @JsonKey(name: 'plan_type') required this.planType, @JsonKey(name: 'total_amount') required this.totalAmount, this.status = PlanStatus.active,  List<Installment> installments = const []}): _installments = installments;
  factory _PaymentPlan.fromJson(Map<String, dynamic> json) => _$PaymentPlanFromJson(json);

@override final  String id;
@override@JsonKey(name: 'merchant_id') final  String merchantId;
@override@JsonKey(name: 'invoice_id') final  String? invoiceId;
@override@JsonKey(name: 'customer_id') final  String? customerId;
@override@JsonKey(name: 'plan_type') final  PlanType planType;
@override@JsonKey(name: 'total_amount') final  String totalAmount;
@override@JsonKey() final  PlanStatus status;
 final  List<Installment> _installments;
@override@JsonKey() List<Installment> get installments {
  if (_installments is EqualUnmodifiableListView) return _installments;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_installments);
}


/// Create a copy of PaymentPlan
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PaymentPlanCopyWith<_PaymentPlan> get copyWith => __$PaymentPlanCopyWithImpl<_PaymentPlan>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PaymentPlanToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _PaymentPlan&&(identical(other.id, id) || other.id == id)&&(identical(other.merchantId, merchantId) || other.merchantId == merchantId)&&(identical(other.invoiceId, invoiceId) || other.invoiceId == invoiceId)&&(identical(other.customerId, customerId) || other.customerId == customerId)&&(identical(other.planType, planType) || other.planType == planType)&&(identical(other.totalAmount, totalAmount) || other.totalAmount == totalAmount)&&(identical(other.status, status) || other.status == status)&&const DeepCollectionEquality().equals(other.installments, _installments));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,merchantId,invoiceId,customerId,planType,totalAmount,status,const DeepCollectionEquality().hash(_installments));
}

@override
String toString() {
    return 'PaymentPlan(id: $id, merchantId: $merchantId, invoiceId: $invoiceId, customerId: $customerId, planType: $planType, totalAmount: $totalAmount, status: $status, installments: $installments)';
}


}

/// @nodoc
abstract mixin class _$PaymentPlanCopyWith<$Res> implements $PaymentPlanCopyWith<$Res> {
  factory _$PaymentPlanCopyWith(_PaymentPlan value, $Res Function(_PaymentPlan) _then) = __$PaymentPlanCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId,@JsonKey(name: 'invoice_id') String? invoiceId,@JsonKey(name: 'customer_id') String? customerId,@JsonKey(name: 'plan_type') PlanType planType,@JsonKey(name: 'total_amount') String totalAmount, PlanStatus status, List<Installment> installments
});




}
/// @nodoc
class __$PaymentPlanCopyWithImpl<$Res>
    implements _$PaymentPlanCopyWith<$Res> {
  __$PaymentPlanCopyWithImpl(this._self, this._then);

  final _PaymentPlan _self;
  final $Res Function(_PaymentPlan) _then;

/// Create a copy of PaymentPlan
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? merchantId = null,Object? invoiceId = freezed,Object? customerId = freezed,Object? planType = null,Object? totalAmount = null,Object? status = null,Object? installments = null,}) {
  return _then(_PaymentPlan(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,invoiceId: freezed == invoiceId ? _self.invoiceId : invoiceId // ignore: cast_nullable_to_non_nullable
as String?,customerId: freezed == customerId ? _self.customerId : customerId // ignore: cast_nullable_to_non_nullable
as String?,planType: null == planType ? _self.planType : planType // ignore: cast_nullable_to_non_nullable
as PlanType,totalAmount: null == totalAmount ? _self.totalAmount : totalAmount // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as PlanStatus,installments: null == installments ? _self._installments : installments // ignore: cast_nullable_to_non_nullable
as List<Installment>,
  ));
}


}

// dart format on
