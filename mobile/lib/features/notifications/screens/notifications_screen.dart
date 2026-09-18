import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../models/notification_models.dart';
import '../../../shared/widgets/paginated_list_view.dart';
import '../../../theme/theme.dart';
import '../notification_providers.dart';

class NotificationsScreen extends ConsumerWidget {
  const NotificationsScreen({super.key});

  IconData _channelIcon(NotificationChannel channel) {
    switch (channel) {
      case NotificationChannel.sms:
        return Icons.sms_outlined;
      case NotificationChannel.email:
        return Icons.email_outlined;
      case NotificationChannel.whatsapp:
        return Icons.chat_outlined;
      case NotificationChannel.push:
      case NotificationChannel.inApp:
        return Icons.notifications_active_outlined;
      case NotificationChannel.webhook:
        return Icons.webhook_outlined;
    }
  }

  void _showNotificationDialog(BuildContext context, AppNotification n, WidgetRef ref) {
    ref.read(notificationListProvider.notifier).markAsRead(n.id);

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Row(
          children: [
            Icon(_channelIcon(n.channel), color: Theme.of(ctx).colorScheme.primary),
            const SizedBox(width: AppSpacing.sm),
            Expanded(child: Text(n.title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold))),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(n.content, style: const TextStyle(fontSize: 14)),
            const SizedBox(height: AppSpacing.md),
            const Divider(),
            Text('Recipient: ${n.recipient}', style: const TextStyle(fontSize: 12, color: Colors.grey)),
            if (n.sentAt != null)
              Text('Sent: ${n.sentAt!.substring(0, 19).replaceAll('T', ' ')}', style: const TextStyle(fontSize: 12, color: Colors.grey)),
          ],
        ),
        actions: [
          FilledButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Dismiss'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(notificationListProvider);
    final notifier = ref.read(notificationListProvider.notifier);
    final cs = Theme.of(context).colorScheme;

    final displayedItems = state.unreadOnly
        ? state.items.where((n) => !n.isRead).toList()
        : state.items;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => notifier.loadFirstPage(),
          ),
        ],
      ),
      body: Column(
        children: [
          // Filter Row
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: AppSpacing.xs),
            child: Row(
              children: [
                FilterChip(
                  label: const Text('All'),
                  selected: !state.unreadOnly,
                  onSelected: (_) {
                    if (state.unreadOnly) notifier.toggleUnreadFilter();
                  },
                ),
                const SizedBox(width: AppSpacing.xs),
                FilterChip(
                  label: Text('Unread (${state.unreadCount})'),
                  selected: state.unreadOnly,
                  onSelected: (_) {
                    if (!state.unreadOnly) notifier.toggleUnreadFilter();
                  },
                ),
              ],
            ),
          ),
          const Divider(height: 1),

          Expanded(
            child: PaginatedListView<AppNotification>(
              items: displayedItems,
              isLoading: state.isLoading,
              hasMore: state.hasMore,
              error: state.error,
              onLoadMore: () => notifier.loadMore(),
              onRefresh: () async => notifier.loadFirstPage(),
              emptyTitle: 'No Notifications',
              emptySubtitle: state.unreadOnly
                  ? 'All caught up! No unread notifications.'
                  : 'Payment alerts, settlements, and risk updates will appear here.',
              emptyIcon: Icons.notifications_none_rounded,
              itemBuilder: (n) {
                final isUnread = !n.isRead;

                return Card(
                  margin: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: 4),
                  elevation: 0,
                  color: isUnread ? cs.primaryContainer.withAlpha(30) : cs.surface,
                  shape: RoundedRectangleBorder(
                    side: BorderSide(
                      color: isUnread ? cs.primary.withAlpha(100) : cs.outlineVariant.withAlpha(50),
                    ),
                    borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
                  ),
                  child: ListTile(
                    onTap: () => _showNotificationDialog(context, n, ref),
                    leading: Stack(
                      clipBehavior: Clip.none,
                      children: [
                        CircleAvatar(
                          backgroundColor: isUnread ? cs.primaryContainer : cs.surfaceContainerHighest,
                          child: Icon(_channelIcon(n.channel), color: isUnread ? cs.primary : cs.onSurfaceVariant, size: 20),
                        ),
                        if (isUnread)
                          Positioned(
                            top: -2,
                            right: -2,
                            child: Container(
                              width: 10,
                              height: 10,
                              decoration: BoxDecoration(
                                color: cs.primary,
                                shape: BoxShape.circle,
                                border: Border.all(color: cs.surface, width: 2),
                              ),
                            ),
                          ),
                      ],
                    ),
                    title: Text(
                      n.title,
                      style: TextStyle(
                        fontWeight: isUnread ? FontWeight.bold : FontWeight.w500,
                        fontSize: 14,
                      ),
                    ),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 2),
                        Text(
                          n.content,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            fontSize: 12,
                            color: isUnread ? cs.onSurface : cs.onSurfaceVariant,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          n.sentAt != null && n.sentAt!.length >= 16
                              ? n.sentAt!.substring(0, 16).replaceAll('T', ' ')
                              : (n.createdAt != null && n.createdAt!.length >= 16
                                  ? n.createdAt!.substring(0, 16).replaceAll('T', ' ')
                                  : ''),
                          style: TextStyle(fontSize: 10, color: cs.onSurfaceVariant),
                        ),
                      ],
                    ),
                    trailing: isUnread
                        ? IconButton(
                            icon: const Icon(Icons.mark_email_read_outlined, size: 18),
                            tooltip: 'Mark as read',
                            onPressed: () => notifier.markAsRead(n.id),
                          )
                        : null,
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
