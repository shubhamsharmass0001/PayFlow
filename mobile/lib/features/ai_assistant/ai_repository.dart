import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/providers.dart';

class AiRepository {
  AiRepository(this._client);
  final ApiClient _client;

  Future<Map<String, dynamic>> query(
    String merchantId,
    String question,
  ) async {
    final r = await _client.dio.post<Map<String, dynamic>>(
      '/api/v1/merchants/$merchantId/ai-assistant/query',
      data: {'question': question},
    );
    return r.data!;
  }
}

final aiRepositoryProvider = Provider<AiRepository>((ref) {
  return AiRepository(ref.watch(apiClientProvider));
});
