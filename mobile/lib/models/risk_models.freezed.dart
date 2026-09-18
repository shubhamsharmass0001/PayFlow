// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'risk_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$RiskSignal {

 String get id;@JsonKey(name: 'merchant_id') String get merchantId;@JsonKey(name: 'transaction_id') String? get transactionId;@JsonKey(name: 'risk_score') double get riskScore;@JsonKey(name: 'risk_level') RiskLevel get riskLevel;@JsonKey(name: 'rule_triggered') String get ruleTriggered;@JsonKey(name: 'action_taken') String get actionTaken;@JsonKey(name: 'is_reviewed') bool get isReviewed;@JsonKey(name: 'resolution_note') String? get resolutionNote;@JsonKey(name: 'reviewed_at') String? get reviewedAt;@JsonKey(name: 'created_at') String get createdAt;
/// Create a copy of RiskSignal
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RiskSignalCopyWith<RiskSignal> get copyWith => _$RiskSignalCopyWithImpl<RiskSignal>(this as RiskSignal, _$identity);

  /// Serializes this RiskSignal to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as RiskSignal;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RiskSignal&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.merchantId, _this.merchantId) || other.merchantId == _this.merchantId)&&(identical(other.transactionId, _this.transactionId) || other.transactionId == _this.transactionId)&&(identical(other.riskScore, _this.riskScore) || other.riskScore == _this.riskScore)&&(identical(other.riskLevel, _this.riskLevel) || other.riskLevel == _this.riskLevel)&&(identical(other.ruleTriggered, _this.ruleTriggered) || other.ruleTriggered == _this.ruleTriggered)&&(identical(other.actionTaken, _this.actionTaken) || other.actionTaken == _this.actionTaken)&&(identical(other.isReviewed, _this.isReviewed) || other.isReviewed == _this.isReviewed)&&(identical(other.resolutionNote, _this.resolutionNote) || other.resolutionNote == _this.resolutionNote)&&(identical(other.reviewedAt, _this.reviewedAt) || other.reviewedAt == _this.reviewedAt)&&(identical(other.createdAt, _this.createdAt) || other.createdAt == _this.createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as RiskSignal;
  return Object.hash(runtimeType,_this.id,_this.merchantId,_this.transactionId,_this.riskScore,_this.riskLevel,_this.ruleTriggered,_this.actionTaken,_this.isReviewed,_this.resolutionNote,_this.reviewedAt,_this.createdAt);
}

@override
String toString() {
  final _this = this as RiskSignal;
  return 'RiskSignal(id: ${_this.id}, merchantId: ${_this.merchantId}, transactionId: ${_this.transactionId}, riskScore: ${_this.riskScore}, riskLevel: ${_this.riskLevel}, ruleTriggered: ${_this.ruleTriggered}, actionTaken: ${_this.actionTaken}, isReviewed: ${_this.isReviewed}, resolutionNote: ${_this.resolutionNote}, reviewedAt: ${_this.reviewedAt}, createdAt: ${_this.createdAt})';
}


}

/// @nodoc
abstract mixin class $RiskSignalCopyWith<$Res>  {
  factory $RiskSignalCopyWith(RiskSignal value, $Res Function(RiskSignal) _then) = _$RiskSignalCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId,@JsonKey(name: 'transaction_id') String? transactionId,@JsonKey(name: 'risk_score') double riskScore,@JsonKey(name: 'risk_level') RiskLevel riskLevel,@JsonKey(name: 'rule_triggered') String ruleTriggered,@JsonKey(name: 'action_taken') String actionTaken,@JsonKey(name: 'is_reviewed') bool isReviewed,@JsonKey(name: 'resolution_note') String? resolutionNote,@JsonKey(name: 'reviewed_at') String? reviewedAt,@JsonKey(name: 'created_at') String createdAt
});




}
/// @nodoc
class _$RiskSignalCopyWithImpl<$Res>
    implements $RiskSignalCopyWith<$Res> {
  _$RiskSignalCopyWithImpl(this._self, this._then);

  final RiskSignal _self;
  final $Res Function(RiskSignal) _then;

/// Create a copy of RiskSignal
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? merchantId = null,Object? transactionId = freezed,Object? riskScore = null,Object? riskLevel = null,Object? ruleTriggered = null,Object? actionTaken = null,Object? isReviewed = null,Object? resolutionNote = freezed,Object? reviewedAt = freezed,Object? createdAt = null,}) {
  return _then(RiskSignal(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,transactionId: freezed == transactionId ? _self.transactionId : transactionId // ignore: cast_nullable_to_non_nullable
as String?,riskScore: null == riskScore ? _self.riskScore : riskScore // ignore: cast_nullable_to_non_nullable
as double,riskLevel: null == riskLevel ? _self.riskLevel : riskLevel // ignore: cast_nullable_to_non_nullable
as RiskLevel,ruleTriggered: null == ruleTriggered ? _self.ruleTriggered : ruleTriggered // ignore: cast_nullable_to_non_nullable
as String,actionTaken: null == actionTaken ? _self.actionTaken : actionTaken // ignore: cast_nullable_to_non_nullable
as String,isReviewed: null == isReviewed ? _self.isReviewed : isReviewed // ignore: cast_nullable_to_non_nullable
as bool,resolutionNote: freezed == resolutionNote ? _self.resolutionNote : resolutionNote // ignore: cast_nullable_to_non_nullable
as String?,reviewedAt: freezed == reviewedAt ? _self.reviewedAt : reviewedAt // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [RiskSignal].
extension RiskSignalPatterns on RiskSignal {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RiskSignal value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RiskSignal() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RiskSignal value)  $default,){
final _that = this;
switch (_that) {
case _RiskSignal():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RiskSignal value)?  $default,){
final _that = this;
switch (_that) {
case _RiskSignal() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'transaction_id')  String? transactionId, @JsonKey(name: 'risk_score')  double riskScore, @JsonKey(name: 'risk_level')  RiskLevel riskLevel, @JsonKey(name: 'rule_triggered')  String ruleTriggered, @JsonKey(name: 'action_taken')  String actionTaken, @JsonKey(name: 'is_reviewed')  bool isReviewed, @JsonKey(name: 'resolution_note')  String? resolutionNote, @JsonKey(name: 'reviewed_at')  String? reviewedAt, @JsonKey(name: 'created_at')  String createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RiskSignal() when $default != null:
return $default(_that.id,_that.merchantId,_that.transactionId,_that.riskScore,_that.riskLevel,_that.ruleTriggered,_that.actionTaken,_that.isReviewed,_that.resolutionNote,_that.reviewedAt,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'transaction_id')  String? transactionId, @JsonKey(name: 'risk_score')  double riskScore, @JsonKey(name: 'risk_level')  RiskLevel riskLevel, @JsonKey(name: 'rule_triggered')  String ruleTriggered, @JsonKey(name: 'action_taken')  String actionTaken, @JsonKey(name: 'is_reviewed')  bool isReviewed, @JsonKey(name: 'resolution_note')  String? resolutionNote, @JsonKey(name: 'reviewed_at')  String? reviewedAt, @JsonKey(name: 'created_at')  String createdAt)  $default,) {final _that = this;
switch (_that) {
case _RiskSignal():
return $default(_that.id,_that.merchantId,_that.transactionId,_that.riskScore,_that.riskLevel,_that.ruleTriggered,_that.actionTaken,_that.isReviewed,_that.resolutionNote,_that.reviewedAt,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'merchant_id')  String merchantId, @JsonKey(name: 'transaction_id')  String? transactionId, @JsonKey(name: 'risk_score')  double riskScore, @JsonKey(name: 'risk_level')  RiskLevel riskLevel, @JsonKey(name: 'rule_triggered')  String ruleTriggered, @JsonKey(name: 'action_taken')  String actionTaken, @JsonKey(name: 'is_reviewed')  bool isReviewed, @JsonKey(name: 'resolution_note')  String? resolutionNote, @JsonKey(name: 'reviewed_at')  String? reviewedAt, @JsonKey(name: 'created_at')  String createdAt)?  $default,) {final _that = this;
switch (_that) {
case _RiskSignal() when $default != null:
return $default(_that.id,_that.merchantId,_that.transactionId,_that.riskScore,_that.riskLevel,_that.ruleTriggered,_that.actionTaken,_that.isReviewed,_that.resolutionNote,_that.reviewedAt,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _RiskSignal implements RiskSignal {
  const _RiskSignal({required this.id, @JsonKey(name: 'merchant_id') required this.merchantId, @JsonKey(name: 'transaction_id') this.transactionId, @JsonKey(name: 'risk_score') required this.riskScore, @JsonKey(name: 'risk_level') required this.riskLevel, @JsonKey(name: 'rule_triggered') required this.ruleTriggered, @JsonKey(name: 'action_taken') required this.actionTaken, @JsonKey(name: 'is_reviewed') this.isReviewed = false, @JsonKey(name: 'resolution_note') this.resolutionNote, @JsonKey(name: 'reviewed_at') this.reviewedAt, @JsonKey(name: 'created_at') required this.createdAt});
  factory _RiskSignal.fromJson(Map<String, dynamic> json) => _$RiskSignalFromJson(json);

@override final  String id;
@override@JsonKey(name: 'merchant_id') final  String merchantId;
@override@JsonKey(name: 'transaction_id') final  String? transactionId;
@override@JsonKey(name: 'risk_score') final  double riskScore;
@override@JsonKey(name: 'risk_level') final  RiskLevel riskLevel;
@override@JsonKey(name: 'rule_triggered') final  String ruleTriggered;
@override@JsonKey(name: 'action_taken') final  String actionTaken;
@override@JsonKey(name: 'is_reviewed') final  bool isReviewed;
@override@JsonKey(name: 'resolution_note') final  String? resolutionNote;
@override@JsonKey(name: 'reviewed_at') final  String? reviewedAt;
@override@JsonKey(name: 'created_at') final  String createdAt;

/// Create a copy of RiskSignal
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RiskSignalCopyWith<_RiskSignal> get copyWith => __$RiskSignalCopyWithImpl<_RiskSignal>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RiskSignalToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _RiskSignal&&(identical(other.id, id) || other.id == id)&&(identical(other.merchantId, merchantId) || other.merchantId == merchantId)&&(identical(other.transactionId, transactionId) || other.transactionId == transactionId)&&(identical(other.riskScore, riskScore) || other.riskScore == riskScore)&&(identical(other.riskLevel, riskLevel) || other.riskLevel == riskLevel)&&(identical(other.ruleTriggered, ruleTriggered) || other.ruleTriggered == ruleTriggered)&&(identical(other.actionTaken, actionTaken) || other.actionTaken == actionTaken)&&(identical(other.isReviewed, isReviewed) || other.isReviewed == isReviewed)&&(identical(other.resolutionNote, resolutionNote) || other.resolutionNote == resolutionNote)&&(identical(other.reviewedAt, reviewedAt) || other.reviewedAt == reviewedAt)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,merchantId,transactionId,riskScore,riskLevel,ruleTriggered,actionTaken,isReviewed,resolutionNote,reviewedAt,createdAt);
}

@override
String toString() {
    return 'RiskSignal(id: $id, merchantId: $merchantId, transactionId: $transactionId, riskScore: $riskScore, riskLevel: $riskLevel, ruleTriggered: $ruleTriggered, actionTaken: $actionTaken, isReviewed: $isReviewed, resolutionNote: $resolutionNote, reviewedAt: $reviewedAt, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$RiskSignalCopyWith<$Res> implements $RiskSignalCopyWith<$Res> {
  factory _$RiskSignalCopyWith(_RiskSignal value, $Res Function(_RiskSignal) _then) = __$RiskSignalCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'merchant_id') String merchantId,@JsonKey(name: 'transaction_id') String? transactionId,@JsonKey(name: 'risk_score') double riskScore,@JsonKey(name: 'risk_level') RiskLevel riskLevel,@JsonKey(name: 'rule_triggered') String ruleTriggered,@JsonKey(name: 'action_taken') String actionTaken,@JsonKey(name: 'is_reviewed') bool isReviewed,@JsonKey(name: 'resolution_note') String? resolutionNote,@JsonKey(name: 'reviewed_at') String? reviewedAt,@JsonKey(name: 'created_at') String createdAt
});




}
/// @nodoc
class __$RiskSignalCopyWithImpl<$Res>
    implements _$RiskSignalCopyWith<$Res> {
  __$RiskSignalCopyWithImpl(this._self, this._then);

  final _RiskSignal _self;
  final $Res Function(_RiskSignal) _then;

/// Create a copy of RiskSignal
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? merchantId = null,Object? transactionId = freezed,Object? riskScore = null,Object? riskLevel = null,Object? ruleTriggered = null,Object? actionTaken = null,Object? isReviewed = null,Object? resolutionNote = freezed,Object? reviewedAt = freezed,Object? createdAt = null,}) {
  return _then(_RiskSignal(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,merchantId: null == merchantId ? _self.merchantId : merchantId // ignore: cast_nullable_to_non_nullable
as String,transactionId: freezed == transactionId ? _self.transactionId : transactionId // ignore: cast_nullable_to_non_nullable
as String?,riskScore: null == riskScore ? _self.riskScore : riskScore // ignore: cast_nullable_to_non_nullable
as double,riskLevel: null == riskLevel ? _self.riskLevel : riskLevel // ignore: cast_nullable_to_non_nullable
as RiskLevel,ruleTriggered: null == ruleTriggered ? _self.ruleTriggered : ruleTriggered // ignore: cast_nullable_to_non_nullable
as String,actionTaken: null == actionTaken ? _self.actionTaken : actionTaken // ignore: cast_nullable_to_non_nullable
as String,isReviewed: null == isReviewed ? _self.isReviewed : isReviewed // ignore: cast_nullable_to_non_nullable
as bool,resolutionNote: freezed == resolutionNote ? _self.resolutionNote : resolutionNote // ignore: cast_nullable_to_non_nullable
as String?,reviewedAt: freezed == reviewedAt ? _self.reviewedAt : reviewedAt // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
