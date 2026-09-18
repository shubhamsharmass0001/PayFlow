import 'package:freezed_annotation/freezed_annotation.dart';

part 'merchant_model.freezed.dart';
part 'merchant_model.g.dart';

// ── Enums (mirror backend) ──────────────────────────────────────────────────

enum KycStatus {
  @JsonValue('PENDING')       pending,
  @JsonValue('UNDER_REVIEW')  underReview,
  @JsonValue('APPROVED')      approved,
  @JsonValue('REJECTED')      rejected,
}

enum RiskTier {
  @JsonValue('LOW')        low,
  @JsonValue('MEDIUM')     medium,
  @JsonValue('HIGH')       high,
  @JsonValue('PROHIBITED') prohibited,
}

// ── Models ──────────────────────────────────────────────────────────────────

@freezed
abstract class MerchantModel with _$MerchantModel {
  const factory MerchantModel({
    required String id,
    @JsonKey(name: 'business_name') required String businessName,
    @JsonKey(name: 'legal_name')    required String legalName,
    required String email,
    required String phone,
    @JsonKey(name: 'kyc_status')  @Default(KycStatus.pending) KycStatus kycStatus,
    @JsonKey(name: 'risk_tier')   @Default(RiskTier.medium)   RiskTier riskTier,
    @JsonKey(name: 'upi_vpa')     String? upiVpa,
    @JsonKey(name: 'mcc_code')    String? mccCode,
    @JsonKey(name: 'is_active')   @Default(true) bool isActive,
    @JsonKey(name: 'created_at')  String? createdAt,
  }) = _MerchantModel;

  factory MerchantModel.fromJson(Map<String, dynamic> json) =>
      _$MerchantModelFromJson(json);
}

@freezed
abstract class CreateMerchantRequest with _$CreateMerchantRequest {
  const factory CreateMerchantRequest({
    @JsonKey(name: 'business_name') required String businessName,
    @JsonKey(name: 'legal_name')    required String legalName,
    required String email,
    required String phone,
    @JsonKey(name: 'upi_vpa')  String? upiVpa,
    @JsonKey(name: 'mcc_code') String? mccCode,
  }) = _CreateMerchantRequest;

  factory CreateMerchantRequest.fromJson(Map<String, dynamic> json) =>
      _$CreateMerchantRequestFromJson(json);
}

// ── KYC document submission ─────────────────────────────────────────────────

enum KycDocumentType {
  @JsonValue('PAN')               pan,
  @JsonValue('GSTIN')             gstin,
  @JsonValue('INCORPORATION_CERT') incorporationCert,
  @JsonValue('BANK_STATEMENT')    bankStatement,
  @JsonValue('AADHAAR')           aadhaar,
  @JsonValue('OTHER')             other,
}

@freezed
abstract class KycDocumentModel with _$KycDocumentModel {
  const factory KycDocumentModel({
    required String id,
    @JsonKey(name: 'merchant_id')    required String merchantId,
    @JsonKey(name: 'document_type')  required KycDocumentType documentType,
    @JsonKey(name: 'document_number') required String documentNumber,
    @JsonKey(name: 'file_url')       required String fileUrl,
    @Default('SUBMITTED') String status,
  }) = _KycDocumentModel;

  factory KycDocumentModel.fromJson(Map<String, dynamic> json) =>
      _$KycDocumentModelFromJson(json);
}
