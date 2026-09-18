// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'customer_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_Customer _$CustomerFromJson(Map<String, dynamic> json) => _Customer(
  id: json['id'] as String,
  merchantId: json['merchant_id'] as String,
  name: json['name'] as String,
  email: json['email'] as String?,
  phone: json['phone'] as String,
  upiVpa: json['upi_vpa'] as String?,
  createdAt: json['created_at'] as String?,
);

Map<String, dynamic> _$CustomerToJson(_Customer instance) => <String, dynamic>{
  'id': instance.id,
  'merchant_id': instance.merchantId,
  'name': instance.name,
  'email': instance.email,
  'phone': instance.phone,
  'upi_vpa': instance.upiVpa,
  'created_at': instance.createdAt,
};

_CreateCustomerRequest _$CreateCustomerRequestFromJson(
  Map<String, dynamic> json,
) => _CreateCustomerRequest(
  name: json['name'] as String,
  phone: json['phone'] as String,
  email: json['email'] as String?,
  upiVpa: json['upi_vpa'] as String?,
);

Map<String, dynamic> _$CreateCustomerRequestToJson(
  _CreateCustomerRequest instance,
) => <String, dynamic>{
  'name': instance.name,
  'phone': instance.phone,
  'email': instance.email,
  'upi_vpa': instance.upiVpa,
};
