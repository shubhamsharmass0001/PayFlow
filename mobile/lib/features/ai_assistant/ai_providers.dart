import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers.dart';
import 'ai_repository.dart';

class ChatMessage {
  const ChatMessage({
    required this.id,
    required this.isUser,
    required this.content,
    this.intent,
    this.sources = const [],
    required this.timestamp,
  });

  final String id;
  final bool isUser;
  final String content;
  final String? intent;
  final List<dynamic> sources;
  final DateTime timestamp;
}

class AiChatState {
  const AiChatState({
    this.messages = const [],
    this.isLoading = false,
    this.error,
  });

  final List<ChatMessage> messages;
  final bool isLoading;
  final String? error;

  AiChatState copyWith({
    List<ChatMessage>? messages,
    bool? isLoading,
    String? error,
  }) {
    return AiChatState(
      messages: messages ?? this.messages,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class AiChatNotifier extends Notifier<AiChatState> {
  @override
  AiChatState build() {
    return AiChatState(
      messages: [
        ChatMessage(
          id: 'welcome',
          isUser: false,
          content:
              'Hello! I am your PayFlow Merchant Intelligence Assistant. I can analyze your sales, overdue invoices, settlement statuses, and transaction volume grounded strictly in your real business data.\n\nHow can I assist you today?',
          timestamp: DateTime.now(),
        ),
      ],
    );
  }

  AiRepository get _repo => ref.read(aiRepositoryProvider);
  String get _merchantId => ref.read(activeMerchantIdProvider);

  Future<void> sendMessage(String question) async {
    final trimmed = question.trim();
    if (trimmed.isEmpty) return;

    final userMsg = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      isUser: true,
      content: trimmed,
      timestamp: DateTime.now(),
    );

    state = state.copyWith(
      messages: [...state.messages, userMsg],
      isLoading: true,
      error: null,
    );

    try {
      final resp = await _repo.query(_merchantId, trimmed);

      final answer = resp['answer'] as String? ?? 'No response received.';
      final intent = resp['intent'] as String?;
      final sources = (resp['sources_cited'] as List<dynamic>?) ?? [];

      final botMsg = ChatMessage(
        id: (DateTime.now().millisecondsSinceEpoch + 1).toString(),
        isUser: false,
        content: answer,
        intent: intent,
        sources: sources,
        timestamp: DateTime.now(),
      );

      state = state.copyWith(
        messages: [...state.messages, botMsg],
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to get answer: $e',
      );
    }
  }

  void clearChat() {
    state = build();
  }
}

final aiChatProvider = NotifierProvider<AiChatNotifier, AiChatState>(AiChatNotifier.new);
