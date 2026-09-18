import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/providers.dart';
import '../../models/merchant_model.dart';

class MerchantRepository {
  MerchantRepository(this._client);
  final ApiClient _client;

  Future<MerchantModel> createMerchant(CreateMerchantRequest req) async {
    final response = await _client.dio.post<Map<String, dynamic>>(
      '/api/v1/merchants',
      data: req.toJson(),
    );
    return MerchantModel.fromJson(response.data!);
  }

  Future<MerchantModel> getMerchant(String merchantId) async {
    final response = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId',
    );
    return MerchantModel.fromJson(response.data!);
  }

  Future<List<KycDocumentModel>> getKycDocuments(String merchantId) async {
    final response = await _client.dio.get<List<dynamic>>(
      '/api/v1/merchants/$merchantId/kyc-documents',
    );
    return (response.data ?? [])
        .cast<Map<String, dynamic>>()
        .map(KycDocumentModel.fromJson)
        .toList();
  }

  Future<KycDocumentModel> submitKycDocument({
    required String merchantId,
    required KycDocumentType documentType,
    required String documentNumber,
    required String fileUrl,
  }) async {
    final response = await _client.dio.post<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/kyc-documents',
      data: {
        'document_type': documentType.name.toUpperCase(),
        'document_number': documentNumber,
        'file_url': fileUrl,
      },
    );
    return KycDocumentModel.fromJson(response.data!);
  }
}

final merchantRepositoryProvider = Provider<MerchantRepository>((ref) {
  return MerchantRepository(ref.watch(apiClientProvider));
});
