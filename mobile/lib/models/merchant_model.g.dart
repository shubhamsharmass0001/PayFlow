// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'merchant_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_MerchantModel _$MerchantModelFromJson(Map<String, dynamic> json) =>
    _MerchantModel(
      id: json['id'] as String,
      businessName: json['business_name'] as String,
      legalName: json['legal_name'] as String,
      email: json['email'] as String,
      phone: json['phone'] as String,
      kycStatus:
          $enumDecodeNullable(_$KycStatusEnumMap, json['kyc_status']) ??
          KycStatus.pending,
      riskTier:
          $enumDecodeNullable(_$RiskTierEnumMap, json['risk_tier']) ??
          RiskTier.medium,
      upiVpa: json['upi_vpa'] as String?,
      mccCode: json['mcc_code'] as String?,
      isActive: json['is_active'] as bool? ?? true,
      createdAt: json['created_at'] as String?,
    );

Map<String, dynamic> _$MerchantModelToJson(_MerchantModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'business_name': instance.businessName,
      'legal_name': instance.legalName,
      'email': instance.email,
      'phone': instance.phone,
      'kyc_status': _$KycStatusEnumMap[instance.kycStatus]!,
      'risk_tier': _$RiskTierEnumMap[instance.riskTier]!,
      'upi_vpa': instance.upiVpa,
      'mcc_code': instance.mccCode,
      'is_active': instance.isActive,
      'created_at': instance.createdAt,
    };

const _$KycStatusEnumMap = {
  KycStatus.pending: 'PENDING',
  KycStatus.underReview: 'UNDER_REVIEW',
  KycStatus.approved: 'APPROVED',
  KycStatus.rejected: 'REJECTED',
};

const _$RiskTierEnumMap = {
  RiskTier.low: 'LOW',
  RiskTier.medium: 'MEDIUM',
  RiskTier.high: 'HIGH',
  RiskTier.prohibited: 'PROHIBITED',
};

_CreateMerchantRequest _$CreateMerchantRequestFromJson(
  Map<String, dynamic> json,
) => _CreateMerchantRequest(
  businessName: json['business_name'] as String,
  legalName: json['legal_name'] as String,
  email: json['email'] as String,
  phone: json['phone'] as String,
  upiVpa: json['upi_vpa'] as String?,
  mccCode: json['mcc_code'] as String?,
);

Map<String, dynamic> _$CreateMerchantRequestToJson(
  _CreateMerchantRequest instance,
) => <String, dynamic>{
  'business_name': instance.businessName,
  'legal_name': instance.legalName,
  'email': instance.email,
  'phone': instance.phone,
  'upi_vpa': instance.upiVpa,
  'mcc_code': instance.mccCode,
};

_KycDocumentModel _$KycDocumentModelFromJson(Map<String, dynamic> json) =>
    _KycDocumentModel(
      id: json['id'] as String,
      merchantId: json['merchant_id'] as String,
      documentType: $enumDecode(
        _$KycDocumentTypeEnumMap,
        json['document_type'],
      ),
      documentNumber: json['document_number'] as String,
      fileUrl: json['file_url'] as String,
      status: json['status'] as String? ?? 'SUBMITTED',
    );

Map<String, dynamic> _$KycDocumentModelToJson(_KycDocumentModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'merchant_id': instance.merchantId,
      'document_type': _$KycDocumentTypeEnumMap[instance.documentType]!,
      'document_number': instance.documentNumber,
      'file_url': instance.fileUrl,
      'status': instance.status,
    };

const _$KycDocumentTypeEnumMap = {
  KycDocumentType.pan: 'PAN',
  KycDocumentType.gstin: 'GSTIN',
  KycDocumentType.incorporationCert: 'INCORPORATION_CERT',
  KycDocumentType.bankStatement: 'BANK_STATEMENT',
  KycDocumentType.aadhaar: 'AADHAAR',
  KycDocumentType.other: 'OTHER',
};
