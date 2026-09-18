import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/providers.dart';
import '../../models/customer_models.dart';
import '../../models/invoice_models.dart';
import '../../models/paginated_response.dart';
import '../../models/transaction_models.dart';

class CustomerRepository {
  CustomerRepository(this._client);
  final ApiClient _client;

  Future<PaginatedResponse<Customer>> listCustomers(
    String merchantId, {
    int page = 1,
    int pageSize = 20,
    String? search,
  }) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/customers',
      queryParameters: {
        'page': page,
        'page_size': pageSize,
        if (search != null && search.isNotEmpty) 'search': search,
      },
    );
    return PaginatedResponse.fromJson(
      r.data!,
      (j) => Customer.fromJson(j as Map<String, dynamic>),
    );
  }

  Future<Customer> getCustomer(String merchantId, String customerId) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/customers/$customerId',
    );
    return Customer.fromJson(r.data!);
  }

  Future<Customer> createCustomer(
    String merchantId,
    CreateCustomerRequest req,
  ) async {
    final r = await _client.dio.post<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/customers',
      data: req.toJson(),
    );
    return Customer.fromJson(r.data!);
  }

  Future<PaginatedResponse<Invoice>> getCustomerInvoices(
    String merchantId,
    String customerId, {
    int page = 1,
    int pageSize = 10,
  }) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/invoices',
      queryParameters: {
        'customer_id': customerId,
        'page': page,
        'page_size': pageSize,
      },
    );
    return PaginatedResponse.fromJson(
      r.data!,
      (j) => Invoice.fromJson(j as Map<String, dynamic>),
    );
  }

  Future<PaginatedResponse<PaymentTransaction>> getCustomerTransactions(
    String merchantId,
    String customerId, {
    int page = 1,
    int pageSize = 10,
  }) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/transactions',
      queryParameters: {
        'customer_id': customerId,
        'page': page,
        'page_size': pageSize,
      },
    );
    return PaginatedResponse.fromJson(
      r.data!,
      (j) => PaymentTransaction.fromJson(j as Map<String, dynamic>),
    );
  }
}

final customerRepositoryProvider = Provider<CustomerRepository>((ref) {
  return CustomerRepository(ref.watch(apiClientProvider));
});
