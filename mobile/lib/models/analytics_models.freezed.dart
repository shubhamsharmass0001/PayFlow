// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'analytics_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$OverviewStats {

@JsonKey(name: 'total_collections') double get totalCollections;@JsonKey(name: 'success_rate') double get successRate;@JsonKey(name: 'pending_count') int get pendingCount;@JsonKey(name: 'avg_transaction_value') double get avgTransactionValue;@JsonKey(name: 'total_transactions') int get totalTransactions;@JsonKey(name: 'period') String get period;
/// Create a copy of OverviewStats
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OverviewStatsCopyWith<OverviewStats> get copyWith => _$OverviewStatsCopyWithImpl<OverviewStats>(this as OverviewStats, _$identity);

  /// Serializes this OverviewStats to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as OverviewStats;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is OverviewStats&&(identical(other.totalCollections, _this.totalCollections) || other.totalCollections == _this.totalCollections)&&(identical(other.successRate, _this.successRate) || other.successRate == _this.successRate)&&(identical(other.pendingCount, _this.pendingCount) || other.pendingCount == _this.pendingCount)&&(identical(other.avgTransactionValue, _this.avgTransactionValue) || other.avgTransactionValue == _this.avgTransactionValue)&&(identical(other.totalTransactions, _this.totalTransactions) || other.totalTransactions == _this.totalTransactions)&&(identical(other.period, _this.period) || other.period == _this.period));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as OverviewStats;
  return Object.hash(runtimeType,_this.totalCollections,_this.successRate,_this.pendingCount,_this.avgTransactionValue,_this.totalTransactions,_this.period);
}

@override
String toString() {
  final _this = this as OverviewStats;
  return 'OverviewStats(totalCollections: ${_this.totalCollections}, successRate: ${_this.successRate}, pendingCount: ${_this.pendingCount}, avgTransactionValue: ${_this.avgTransactionValue}, totalTransactions: ${_this.totalTransactions}, period: ${_this.period})';
}


}

/// @nodoc
abstract mixin class $OverviewStatsCopyWith<$Res>  {
  factory $OverviewStatsCopyWith(OverviewStats value, $Res Function(OverviewStats) _then) = _$OverviewStatsCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'total_collections') double totalCollections,@JsonKey(name: 'success_rate') double successRate,@JsonKey(name: 'pending_count') int pendingCount,@JsonKey(name: 'avg_transaction_value') double avgTransactionValue,@JsonKey(name: 'total_transactions') int totalTransactions,@JsonKey(name: 'period') String period
});




}
/// @nodoc
class _$OverviewStatsCopyWithImpl<$Res>
    implements $OverviewStatsCopyWith<$Res> {
  _$OverviewStatsCopyWithImpl(this._self, this._then);

  final OverviewStats _self;
  final $Res Function(OverviewStats) _then;

/// Create a copy of OverviewStats
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? totalCollections = null,Object? successRate = null,Object? pendingCount = null,Object? avgTransactionValue = null,Object? totalTransactions = null,Object? period = null,}) {
  return _then(OverviewStats(
totalCollections: null == totalCollections ? _self.totalCollections : totalCollections // ignore: cast_nullable_to_non_nullable
as double,successRate: null == successRate ? _self.successRate : successRate // ignore: cast_nullable_to_non_nullable
as double,pendingCount: null == pendingCount ? _self.pendingCount : pendingCount // ignore: cast_nullable_to_non_nullable
as int,avgTransactionValue: null == avgTransactionValue ? _self.avgTransactionValue : avgTransactionValue // ignore: cast_nullable_to_non_nullable
as double,totalTransactions: null == totalTransactions ? _self.totalTransactions : totalTransactions // ignore: cast_nullable_to_non_nullable
as int,period: null == period ? _self.period : period // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [OverviewStats].
extension OverviewStatsPatterns on OverviewStats {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _OverviewStats value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _OverviewStats() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _OverviewStats value)  $default,){
final _that = this;
switch (_that) {
case _OverviewStats():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _OverviewStats value)?  $default,){
final _that = this;
switch (_that) {
case _OverviewStats() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'total_collections')  double totalCollections, @JsonKey(name: 'success_rate')  double successRate, @JsonKey(name: 'pending_count')  int pendingCount, @JsonKey(name: 'avg_transaction_value')  double avgTransactionValue, @JsonKey(name: 'total_transactions')  int totalTransactions, @JsonKey(name: 'period')  String period)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OverviewStats() when $default != null:
return $default(_that.totalCollections,_that.successRate,_that.pendingCount,_that.avgTransactionValue,_that.totalTransactions,_that.period);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'total_collections')  double totalCollections, @JsonKey(name: 'success_rate')  double successRate, @JsonKey(name: 'pending_count')  int pendingCount, @JsonKey(name: 'avg_transaction_value')  double avgTransactionValue, @JsonKey(name: 'total_transactions')  int totalTransactions, @JsonKey(name: 'period')  String period)  $default,) {final _that = this;
switch (_that) {
case _OverviewStats():
return $default(_that.totalCollections,_that.successRate,_that.pendingCount,_that.avgTransactionValue,_that.totalTransactions,_that.period);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'total_collections')  double totalCollections, @JsonKey(name: 'success_rate')  double successRate, @JsonKey(name: 'pending_count')  int pendingCount, @JsonKey(name: 'avg_transaction_value')  double avgTransactionValue, @JsonKey(name: 'total_transactions')  int totalTransactions, @JsonKey(name: 'period')  String period)?  $default,) {final _that = this;
switch (_that) {
case _OverviewStats() when $default != null:
return $default(_that.totalCollections,_that.successRate,_that.pendingCount,_that.avgTransactionValue,_that.totalTransactions,_that.period);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _OverviewStats implements OverviewStats {
  const _OverviewStats({@JsonKey(name: 'total_collections') required this.totalCollections, @JsonKey(name: 'success_rate') required this.successRate, @JsonKey(name: 'pending_count') required this.pendingCount, @JsonKey(name: 'avg_transaction_value') required this.avgTransactionValue, @JsonKey(name: 'total_transactions') required this.totalTransactions, @JsonKey(name: 'period') required this.period});
  factory _OverviewStats.fromJson(Map<String, dynamic> json) => _$OverviewStatsFromJson(json);

@override@JsonKey(name: 'total_collections') final  double totalCollections;
@override@JsonKey(name: 'success_rate') final  double successRate;
@override@JsonKey(name: 'pending_count') final  int pendingCount;
@override@JsonKey(name: 'avg_transaction_value') final  double avgTransactionValue;
@override@JsonKey(name: 'total_transactions') final  int totalTransactions;
@override@JsonKey(name: 'period') final  String period;

/// Create a copy of OverviewStats
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OverviewStatsCopyWith<_OverviewStats> get copyWith => __$OverviewStatsCopyWithImpl<_OverviewStats>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OverviewStatsToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _OverviewStats&&(identical(other.totalCollections, totalCollections) || other.totalCollections == totalCollections)&&(identical(other.successRate, successRate) || other.successRate == successRate)&&(identical(other.pendingCount, pendingCount) || other.pendingCount == pendingCount)&&(identical(other.avgTransactionValue, avgTransactionValue) || other.avgTransactionValue == avgTransactionValue)&&(identical(other.totalTransactions, totalTransactions) || other.totalTransactions == totalTransactions)&&(identical(other.period, period) || other.period == period));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,totalCollections,successRate,pendingCount,avgTransactionValue,totalTransactions,period);
}

@override
String toString() {
    return 'OverviewStats(totalCollections: $totalCollections, successRate: $successRate, pendingCount: $pendingCount, avgTransactionValue: $avgTransactionValue, totalTransactions: $totalTransactions, period: $period)';
}


}

/// @nodoc
abstract mixin class _$OverviewStatsCopyWith<$Res> implements $OverviewStatsCopyWith<$Res> {
  factory _$OverviewStatsCopyWith(_OverviewStats value, $Res Function(_OverviewStats) _then) = __$OverviewStatsCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'total_collections') double totalCollections,@JsonKey(name: 'success_rate') double successRate,@JsonKey(name: 'pending_count') int pendingCount,@JsonKey(name: 'avg_transaction_value') double avgTransactionValue,@JsonKey(name: 'total_transactions') int totalTransactions,@JsonKey(name: 'period') String period
});




}
/// @nodoc
class __$OverviewStatsCopyWithImpl<$Res>
    implements _$OverviewStatsCopyWith<$Res> {
  __$OverviewStatsCopyWithImpl(this._self, this._then);

  final _OverviewStats _self;
  final $Res Function(_OverviewStats) _then;

/// Create a copy of OverviewStats
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? totalCollections = null,Object? successRate = null,Object? pendingCount = null,Object? avgTransactionValue = null,Object? totalTransactions = null,Object? period = null,}) {
  return _then(_OverviewStats(
totalCollections: null == totalCollections ? _self.totalCollections : totalCollections // ignore: cast_nullable_to_non_nullable
as double,successRate: null == successRate ? _self.successRate : successRate // ignore: cast_nullable_to_non_nullable
as double,pendingCount: null == pendingCount ? _self.pendingCount : pendingCount // ignore: cast_nullable_to_non_nullable
as int,avgTransactionValue: null == avgTransactionValue ? _self.avgTransactionValue : avgTransactionValue // ignore: cast_nullable_to_non_nullable
as double,totalTransactions: null == totalTransactions ? _self.totalTransactions : totalTransactions // ignore: cast_nullable_to_non_nullable
as int,period: null == period ? _self.period : period // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$RevenueTrendPoint {

 String get date; double get amount; int get count;
/// Create a copy of RevenueTrendPoint
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RevenueTrendPointCopyWith<RevenueTrendPoint> get copyWith => _$RevenueTrendPointCopyWithImpl<RevenueTrendPoint>(this as RevenueTrendPoint, _$identity);

  /// Serializes this RevenueTrendPoint to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as RevenueTrendPoint;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RevenueTrendPoint&&(identical(other.date, _this.date) || other.date == _this.date)&&(identical(other.amount, _this.amount) || other.amount == _this.amount)&&(identical(other.count, _this.count) || other.count == _this.count));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as RevenueTrendPoint;
  return Object.hash(runtimeType,_this.date,_this.amount,_this.count);
}

@override
String toString() {
  final _this = this as RevenueTrendPoint;
  return 'RevenueTrendPoint(date: ${_this.date}, amount: ${_this.amount}, count: ${_this.count})';
}


}

/// @nodoc
abstract mixin class $RevenueTrendPointCopyWith<$Res>  {
  factory $RevenueTrendPointCopyWith(RevenueTrendPoint value, $Res Function(RevenueTrendPoint) _then) = _$RevenueTrendPointCopyWithImpl;
@useResult
$Res call({
 String date, double amount, int count
});




}
/// @nodoc
class _$RevenueTrendPointCopyWithImpl<$Res>
    implements $RevenueTrendPointCopyWith<$Res> {
  _$RevenueTrendPointCopyWithImpl(this._self, this._then);

  final RevenueTrendPoint _self;
  final $Res Function(RevenueTrendPoint) _then;

/// Create a copy of RevenueTrendPoint
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? date = null,Object? amount = null,Object? count = null,}) {
  return _then(RevenueTrendPoint(
date: null == date ? _self.date : date // ignore: cast_nullable_to_non_nullable
as String,amount: null == amount ? _self.amount : amount // ignore: cast_nullable_to_non_nullable
as double,count: null == count ? _self.count : count // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [RevenueTrendPoint].
extension RevenueTrendPointPatterns on RevenueTrendPoint {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RevenueTrendPoint value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RevenueTrendPoint() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RevenueTrendPoint value)  $default,){
final _that = this;
switch (_that) {
case _RevenueTrendPoint():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RevenueTrendPoint value)?  $default,){
final _that = this;
switch (_that) {
case _RevenueTrendPoint() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String date,  double amount,  int count)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RevenueTrendPoint() when $default != null:
return $default(_that.date,_that.amount,_that.count);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String date,  double amount,  int count)  $default,) {final _that = this;
switch (_that) {
case _RevenueTrendPoint():
return $default(_that.date,_that.amount,_that.count);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String date,  double amount,  int count)?  $default,) {final _that = this;
switch (_that) {
case _RevenueTrendPoint() when $default != null:
return $default(_that.date,_that.amount,_that.count);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _RevenueTrendPoint implements RevenueTrendPoint {
  const _RevenueTrendPoint({required this.date, required this.amount, required this.count});
  factory _RevenueTrendPoint.fromJson(Map<String, dynamic> json) => _$RevenueTrendPointFromJson(json);

@override final  String date;
@override final  double amount;
@override final  int count;

/// Create a copy of RevenueTrendPoint
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RevenueTrendPointCopyWith<_RevenueTrendPoint> get copyWith => __$RevenueTrendPointCopyWithImpl<_RevenueTrendPoint>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RevenueTrendPointToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _RevenueTrendPoint&&(identical(other.date, date) || other.date == date)&&(identical(other.amount, amount) || other.amount == amount)&&(identical(other.count, count) || other.count == count));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,date,amount,count);
}

@override
String toString() {
    return 'RevenueTrendPoint(date: $date, amount: $amount, count: $count)';
}


}

/// @nodoc
abstract mixin class _$RevenueTrendPointCopyWith<$Res> implements $RevenueTrendPointCopyWith<$Res> {
  factory _$RevenueTrendPointCopyWith(_RevenueTrendPoint value, $Res Function(_RevenueTrendPoint) _then) = __$RevenueTrendPointCopyWithImpl;
@override @useResult
$Res call({
 String date, double amount, int count
});




}
/// @nodoc
class __$RevenueTrendPointCopyWithImpl<$Res>
    implements _$RevenueTrendPointCopyWith<$Res> {
  __$RevenueTrendPointCopyWithImpl(this._self, this._then);

  final _RevenueTrendPoint _self;
  final $Res Function(_RevenueTrendPoint) _then;

/// Create a copy of RevenueTrendPoint
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? date = null,Object? amount = null,Object? count = null,}) {
  return _then(_RevenueTrendPoint(
date: null == date ? _self.date : date // ignore: cast_nullable_to_non_nullable
as String,amount: null == amount ? _self.amount : amount // ignore: cast_nullable_to_non_nullable
as double,count: null == count ? _self.count : count // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$RevenueTrend {

 List<RevenueTrendPoint> get points; String get granularity; String get from; String get to;
/// Create a copy of RevenueTrend
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RevenueTrendCopyWith<RevenueTrend> get copyWith => _$RevenueTrendCopyWithImpl<RevenueTrend>(this as RevenueTrend, _$identity);

  /// Serializes this RevenueTrend to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as RevenueTrend;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RevenueTrend&&const DeepCollectionEquality().equals(other.points, _this.points)&&(identical(other.granularity, _this.granularity) || other.granularity == _this.granularity)&&(identical(other.from, _this.from) || other.from == _this.from)&&(identical(other.to, _this.to) || other.to == _this.to));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as RevenueTrend;
  return Object.hash(runtimeType,const DeepCollectionEquality().hash(_this.points),_this.granularity,_this.from,_this.to);
}

@override
String toString() {
  final _this = this as RevenueTrend;
  return 'RevenueTrend(points: ${_this.points}, granularity: ${_this.granularity}, from: ${_this.from}, to: ${_this.to})';
}


}

/// @nodoc
abstract mixin class $RevenueTrendCopyWith<$Res>  {
  factory $RevenueTrendCopyWith(RevenueTrend value, $Res Function(RevenueTrend) _then) = _$RevenueTrendCopyWithImpl;
@useResult
$Res call({
 List<RevenueTrendPoint> points, String granularity, String from, String to
});




}
/// @nodoc
class _$RevenueTrendCopyWithImpl<$Res>
    implements $RevenueTrendCopyWith<$Res> {
  _$RevenueTrendCopyWithImpl(this._self, this._then);

  final RevenueTrend _self;
  final $Res Function(RevenueTrend) _then;

/// Create a copy of RevenueTrend
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? points = null,Object? granularity = null,Object? from = null,Object? to = null,}) {
  return _then(RevenueTrend(
points: null == points ? _self.points : points // ignore: cast_nullable_to_non_nullable
as List<RevenueTrendPoint>,granularity: null == granularity ? _self.granularity : granularity // ignore: cast_nullable_to_non_nullable
as String,from: null == from ? _self.from : from // ignore: cast_nullable_to_non_nullable
as String,to: null == to ? _self.to : to // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [RevenueTrend].
extension RevenueTrendPatterns on RevenueTrend {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RevenueTrend value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RevenueTrend() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RevenueTrend value)  $default,){
final _that = this;
switch (_that) {
case _RevenueTrend():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RevenueTrend value)?  $default,){
final _that = this;
switch (_that) {
case _RevenueTrend() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( List<RevenueTrendPoint> points,  String granularity,  String from,  String to)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RevenueTrend() when $default != null:
return $default(_that.points,_that.granularity,_that.from,_that.to);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( List<RevenueTrendPoint> points,  String granularity,  String from,  String to)  $default,) {final _that = this;
switch (_that) {
case _RevenueTrend():
return $default(_that.points,_that.granularity,_that.from,_that.to);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( List<RevenueTrendPoint> points,  String granularity,  String from,  String to)?  $default,) {final _that = this;
switch (_that) {
case _RevenueTrend() when $default != null:
return $default(_that.points,_that.granularity,_that.from,_that.to);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _RevenueTrend implements RevenueTrend {
  const _RevenueTrend({required  List<RevenueTrendPoint> points, required this.granularity, required this.from, required this.to}): _points = points;
  factory _RevenueTrend.fromJson(Map<String, dynamic> json) => _$RevenueTrendFromJson(json);

 final  List<RevenueTrendPoint> _points;
@override List<RevenueTrendPoint> get points {
  if (_points is EqualUnmodifiableListView) return _points;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_points);
}

@override final  String granularity;
@override final  String from;
@override final  String to;

/// Create a copy of RevenueTrend
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RevenueTrendCopyWith<_RevenueTrend> get copyWith => __$RevenueTrendCopyWithImpl<_RevenueTrend>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RevenueTrendToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _RevenueTrend&&const DeepCollectionEquality().equals(other.points, _points)&&(identical(other.granularity, granularity) || other.granularity == granularity)&&(identical(other.from, from) || other.from == from)&&(identical(other.to, to) || other.to == to));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,const DeepCollectionEquality().hash(_points),granularity,from,to);
}

@override
String toString() {
    return 'RevenueTrend(points: $points, granularity: $granularity, from: $from, to: $to)';
}


}

/// @nodoc
abstract mixin class _$RevenueTrendCopyWith<$Res> implements $RevenueTrendCopyWith<$Res> {
  factory _$RevenueTrendCopyWith(_RevenueTrend value, $Res Function(_RevenueTrend) _then) = __$RevenueTrendCopyWithImpl;
@override @useResult
$Res call({
 List<RevenueTrendPoint> points, String granularity, String from, String to
});




}
/// @nodoc
class __$RevenueTrendCopyWithImpl<$Res>
    implements _$RevenueTrendCopyWith<$Res> {
  __$RevenueTrendCopyWithImpl(this._self, this._then);

  final _RevenueTrend _self;
  final $Res Function(_RevenueTrend) _then;

/// Create a copy of RevenueTrend
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? points = null,Object? granularity = null,Object? from = null,Object? to = null,}) {
  return _then(_RevenueTrend(
points: null == points ? _self._points : points // ignore: cast_nullable_to_non_nullable
as List<RevenueTrendPoint>,granularity: null == granularity ? _self.granularity : granularity // ignore: cast_nullable_to_non_nullable
as String,from: null == from ? _self.from : from // ignore: cast_nullable_to_non_nullable
as String,to: null == to ? _self.to : to // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$PaymentMethodStat {

 String get method; int get count; double get amount;
/// Create a copy of PaymentMethodStat
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PaymentMethodStatCopyWith<PaymentMethodStat> get copyWith => _$PaymentMethodStatCopyWithImpl<PaymentMethodStat>(this as PaymentMethodStat, _$identity);

  /// Serializes this PaymentMethodStat to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as PaymentMethodStat;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PaymentMethodStat&&(identical(other.method, _this.method) || other.method == _this.method)&&(identical(other.count, _this.count) || other.count == _this.count)&&(identical(other.amount, _this.amount) || other.amount == _this.amount));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as PaymentMethodStat;
  return Object.hash(runtimeType,_this.method,_this.count,_this.amount);
}

@override
String toString() {
  final _this = this as PaymentMethodStat;
  return 'PaymentMethodStat(method: ${_this.method}, count: ${_this.count}, amount: ${_this.amount})';
}


}

/// @nodoc
abstract mixin class $PaymentMethodStatCopyWith<$Res>  {
  factory $PaymentMethodStatCopyWith(PaymentMethodStat value, $Res Function(PaymentMethodStat) _then) = _$PaymentMethodStatCopyWithImpl;
@useResult
$Res call({
 String method, int count, double amount
});




}
/// @nodoc
class _$PaymentMethodStatCopyWithImpl<$Res>
    implements $PaymentMethodStatCopyWith<$Res> {
  _$PaymentMethodStatCopyWithImpl(this._self, this._then);

  final PaymentMethodStat _self;
  final $Res Function(PaymentMethodStat) _then;

/// Create a copy of PaymentMethodStat
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? method = null,Object? count = null,Object? amount = null,}) {
  return _then(PaymentMethodStat(
method: null == method ? _self.method : method // ignore: cast_nullable_to_non_nullable
as String,count: null == count ? _self.count : count // ignore: cast_nullable_to_non_nullable
as int,amount: null == amount ? _self.amount : amount // ignore: cast_nullable_to_non_nullable
as double,
  ));
}

}


/// Adds pattern-matching-related methods to [PaymentMethodStat].
extension PaymentMethodStatPatterns on PaymentMethodStat {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PaymentMethodStat value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PaymentMethodStat() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PaymentMethodStat value)  $default,){
final _that = this;
switch (_that) {
case _PaymentMethodStat():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PaymentMethodStat value)?  $default,){
final _that = this;
switch (_that) {
case _PaymentMethodStat() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String method,  int count,  double amount)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PaymentMethodStat() when $default != null:
return $default(_that.method,_that.count,_that.amount);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String method,  int count,  double amount)  $default,) {final _that = this;
switch (_that) {
case _PaymentMethodStat():
return $default(_that.method,_that.count,_that.amount);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String method,  int count,  double amount)?  $default,) {final _that = this;
switch (_that) {
case _PaymentMethodStat() when $default != null:
return $default(_that.method,_that.count,_that.amount);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PaymentMethodStat implements PaymentMethodStat {
  const _PaymentMethodStat({required this.method, required this.count, required this.amount});
  factory _PaymentMethodStat.fromJson(Map<String, dynamic> json) => _$PaymentMethodStatFromJson(json);

@override final  String method;
@override final  int count;
@override final  double amount;

/// Create a copy of PaymentMethodStat
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PaymentMethodStatCopyWith<_PaymentMethodStat> get copyWith => __$PaymentMethodStatCopyWithImpl<_PaymentMethodStat>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PaymentMethodStatToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _PaymentMethodStat&&(identical(other.method, method) || other.method == method)&&(identical(other.count, count) || other.count == count)&&(identical(other.amount, amount) || other.amount == amount));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,method,count,amount);
}

@override
String toString() {
    return 'PaymentMethodStat(method: $method, count: $count, amount: $amount)';
}


}

/// @nodoc
abstract mixin class _$PaymentMethodStatCopyWith<$Res> implements $PaymentMethodStatCopyWith<$Res> {
  factory _$PaymentMethodStatCopyWith(_PaymentMethodStat value, $Res Function(_PaymentMethodStat) _then) = __$PaymentMethodStatCopyWithImpl;
@override @useResult
$Res call({
 String method, int count, double amount
});




}
/// @nodoc
class __$PaymentMethodStatCopyWithImpl<$Res>
    implements _$PaymentMethodStatCopyWith<$Res> {
  __$PaymentMethodStatCopyWithImpl(this._self, this._then);

  final _PaymentMethodStat _self;
  final $Res Function(_PaymentMethodStat) _then;

/// Create a copy of PaymentMethodStat
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? method = null,Object? count = null,Object? amount = null,}) {
  return _then(_PaymentMethodStat(
method: null == method ? _self.method : method // ignore: cast_nullable_to_non_nullable
as String,count: null == count ? _self.count : count // ignore: cast_nullable_to_non_nullable
as int,amount: null == amount ? _self.amount : amount // ignore: cast_nullable_to_non_nullable
as double,
  ));
}


}

// dart format on
