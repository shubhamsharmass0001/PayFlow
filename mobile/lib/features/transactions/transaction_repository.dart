import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/providers.dart';
import '../../models/transaction_models.dart';
import '../../models/paginated_response.dart';

class TransactionRepository {
  TransactionRepository(this._client);
  final ApiClient _client;

  Future<PaginatedResponse<PaymentTransaction>> listTransactions(
    String merchantId, {
    int page = 1,
    int pageSize = 20,
    String? status,
    String? method,
    String? from,
    String? to,
  }) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/transactions',
      queryParameters: {
        'page': page,
        'page_size': pageSize,
        if (status != null && status != 'ALL') 'status': status,
        if (method != null && method != 'ALL') 'payment_method': method,
        'from': ?from,
        'to': ?to,
      },
    );
    return PaginatedResponse.fromJson(
      r.data!,
      (j) => PaymentTransaction.fromJson(j as Map<String, dynamic>),
    );
  }

  Future<PaymentTransaction> getTransaction(
    String merchantId,
    String transactionId,
  ) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/transactions/$transactionId',
    );
    return PaymentTransaction.fromJson(r.data!);
  }

  Future<Map<String, dynamic>> createRefund(
    String merchantId,
    String transactionId,
    CreateRefundRequest req,
  ) async {
    final r = await _client.dio.post<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/transactions/$transactionId/refunds',
      data: req.toJson(),
    );
    return r.data!;
  }
}

final transactionRepositoryProvider = Provider<TransactionRepository>((ref) {
  return TransactionRepository(ref.watch(apiClientProvider));
});
