import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/providers.dart';
import '../../models/invoice_models.dart';
import '../../models/paginated_response.dart';

class InvoiceRepository {
  InvoiceRepository(this._client);
  final ApiClient _client;

  Future<PaginatedResponse<Invoice>> listInvoices(
    String merchantId, {
    int page = 1,
    int pageSize = 20,
    String? status,
    String? search,
  }) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/invoices',
      queryParameters: {
        'page': page,
        'page_size': pageSize,
        if (status != null && status != 'ALL') 'status': status,
        if (search != null && search.isNotEmpty) 'search': search,
      },
    );
    return PaginatedResponse.fromJson(
      r.data!,
      (j) => Invoice.fromJson(j as Map<String, dynamic>),
    );
  }

  Future<Invoice> getInvoice(String merchantId, String invoiceId) async {
    final r = await _client.dio.get<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/invoices/$invoiceId',
    );
    return Invoice.fromJson(r.data!);
  }

  Future<Invoice> createInvoice(
    String merchantId,
    CreateInvoiceRequest req,
  ) async {
    final r = await _client.dio.post<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/invoices',
      data: req.toJson(),
    );
    return Invoice.fromJson(r.data!);
  }

  Future<Invoice> updateInvoice(
    String merchantId,
    String invoiceId,
    Map<String, dynamic> updates,
  ) async {
    final r = await _client.dio.patch<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/invoices/$invoiceId',
      data: updates,
    );
    return Invoice.fromJson(r.data!);
  }

  // ── Payment Requests ────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> createPaymentRequest(
    String merchantId,
    String invoiceId, {
    String? amount,
    String? payerVpa,
    String method = 'UPI_QR',
  }) async {
    final r = await _client.dio.post<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/payment-requests',
      data: {
        'invoice_id': invoiceId,
        'payment_method': method,
        'amount': ?amount,
        'payer_vpa': ?payerVpa,
      },
    );
    return r.data!;
  }

  // ── Payment Plans ───────────────────────────────────────────────────────────

  Future<PaymentPlan> createPaymentPlan(
    String merchantId, {
    required String invoiceId,
    required String planType,
    required List<Map<String, dynamic>> installments,
  }) async {
    final r = await _client.dio.post<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/payment-plans',
      data: {
        'invoice_id': invoiceId,
        'plan_type': planType,
        'installments': installments,
      },
    );
    return PaymentPlan.fromJson(r.data!);
  }

  Future<List<PaymentPlan>> getInvoicePaymentPlans(
    String merchantId,
    String invoiceId,
  ) async {
    final r = await _client.dio.get<List<dynamic>>(
      '/api/v1/merchants/$merchantId/invoices/$invoiceId/payment-plans',
    );
    return (r.data ?? [])
        .cast<Map<String, dynamic>>()
        .map(PaymentPlan.fromJson)
        .toList();
  }
}

final invoiceRepositoryProvider = Provider<InvoiceRepository>((ref) {
  return InvoiceRepository(ref.watch(apiClientProvider));
});
