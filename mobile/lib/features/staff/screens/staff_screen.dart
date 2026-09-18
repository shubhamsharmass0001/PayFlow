import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../models/staff_models.dart';
import '../../../shared/widgets/empty_state.dart';
import '../../../shared/widgets/status_badge.dart';
import '../../../theme/theme.dart';
import '../staff_providers.dart';

class StaffScreen extends ConsumerWidget {
  const StaffScreen({super.key});

  void _showAddStaffDialog(BuildContext context, WidgetRef ref) {
    final userCtrl = TextEditingController();
    StaffRole selectedRole = StaffRole.cashier;
    final formKey = GlobalKey<FormState>();

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setStateDialog) => AlertDialog(
          title: const Text('Add Staff Member'),
          content: Form(
            key: formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextFormField(
                  controller: userCtrl,
                  decoration: const InputDecoration(
                    labelText: 'User ID or Email *',
                    hintText: 'e.g. staff@store.com or UUID',
                  ),
                  validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                ),
                const SizedBox(height: AppSpacing.md),
                DropdownButtonFormField<StaffRole>(
                  initialValue: selectedRole,
                  decoration: const InputDecoration(labelText: 'Assigned Role'),
                  items: StaffRole.values.map((r) {
                    return DropdownMenuItem(
                      value: r,
                      child: Text(r.name.toUpperCase()),
                    );
                  }).toList(),
                  onChanged: (val) {
                    if (val != null) setStateDialog(() => selectedRole = val);
                  },
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(ctx).pop(),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () async {
                if (!formKey.currentState!.validate()) return;
                Navigator.of(ctx).pop();
                try {
                  await ref.read(staffListProvider.notifier).addStaff(
                        userId: userCtrl.text.trim(),
                        role: selectedRole,
                      );
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Staff member added successfully!'), backgroundColor: Colors.green),
                    );
                  }
                } catch (e) {
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Failed to add staff: $e'), backgroundColor: Colors.red),
                    );
                  }
                }
              },
              child: const Text('Assign Role'),
            ),
          ],
        ),
      ),
    );
  }

  void _showEditRoleSheet(BuildContext context, WidgetRef ref, MerchantStaff staff) {
    StaffRole newRole = staff.role;

    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setStateSheet) {
          final cs = Theme.of(ctx).colorScheme;
          return Container(
            decoration: BoxDecoration(
              color: cs.surface,
              borderRadius: const BorderRadius.vertical(top: Radius.circular(AppSpacing.radiusXl)),
            ),
            padding: const EdgeInsets.all(AppSpacing.lg),
            child: SafeArea(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text('Manage Staff Role', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                  const SizedBox(height: 4),
                  Text(staff.userName ?? staff.userEmail ?? staff.userId, style: TextStyle(color: cs.onSurfaceVariant)),
                  const SizedBox(height: AppSpacing.md),
                  DropdownButtonFormField<StaffRole>(
                    initialValue: newRole,
                    decoration: const InputDecoration(labelText: 'Role'),
                    items: StaffRole.values.map((r) {
                      return DropdownMenuItem(value: r, child: Text(r.name.toUpperCase()));
                    }).toList(),
                    onChanged: (val) {
                      if (val != null) setStateSheet(() => newRole = val);
                    },
                  ),
                  const SizedBox(height: AppSpacing.lg),
                  Row(
                    children: [
                      TextButton.icon(
                        style: TextButton.styleFrom(foregroundColor: Colors.red),
                        onPressed: () async {
                          Navigator.of(ctx).pop();
                          try {
                            await ref.read(staffListProvider.notifier).removeStaff(staff.id);
                            if (context.mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Staff member removed')),
                              );
                            }
                          } catch (e) {
                            if (context.mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
                              );
                            }
                          }
                        },
                        icon: const Icon(Icons.person_remove_rounded),
                        label: const Text('Remove'),
                      ),
                      const Spacer(),
                      FilledButton(
                        onPressed: () async {
                          Navigator.of(ctx).pop();
                          try {
                            await ref.read(staffListProvider.notifier).updateRole(staff.id, newRole);
                            if (context.mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Role updated successfully!'), backgroundColor: Colors.green),
                              );
                            }
                          } catch (e) {
                            if (context.mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
                              );
                            }
                          }
                        },
                        child: const Text('Save Role'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final canManage = ref.watch(canManageStaffProvider);
    final cs = Theme.of(context).colorScheme;

    // RBAC: If not Owner/Manager, hide the screen entirely!
    if (!canManage) {
      return Scaffold(
        appBar: AppBar(title: const Text('Staff')),
        body: const EmptyState(
          title: 'Access Restricted',
          subtitle: 'Staff management is restricted to Merchant Owners and Managers only.',
          icon: Icons.lock_outline_rounded,
        ),
      );
    }

    final state = ref.watch(staffListProvider);
    final notifier = ref.read(staffListProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Staff Management'),
        actions: [
          IconButton(
            icon: const Icon(Icons.person_add_rounded),
            tooltip: 'Add Staff',
            onPressed: () => _showAddStaffDialog(context, ref),
          ),
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => notifier.loadStaff(),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showAddStaffDialog(context, ref),
        icon: const Icon(Icons.person_add_rounded),
        label: const Text('Add Staff'),
      ),
      body: RefreshIndicator(
        onRefresh: () => notifier.loadStaff(),
        child: state.isLoading
            ? const Center(child: CircularProgressIndicator())
            : state.items.isEmpty
                ? const EmptyState(
                    title: 'No Staff Assigned',
                    subtitle: 'Add staff members to assign cashier, manager, or accountant roles',
                    icon: Icons.badge_outlined,
                  )
                : ListView.separated(
                    padding: const EdgeInsets.all(AppSpacing.md),
                    itemCount: state.items.length,
                    separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.sm),
                    itemBuilder: (context, idx) {
                      final staff = state.items[idx];
                      return Card(
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          side: BorderSide(color: cs.outlineVariant.withAlpha(60)),
                          borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
                        ),
                        child: ListTile(
                          onTap: () => _showEditRoleSheet(context, ref, staff),
                          leading: CircleAvatar(
                            backgroundColor: cs.primaryContainer,
                            child: Icon(Icons.person_rounded, color: cs.primary),
                          ),
                          title: Text(
                            staff.userName ?? staff.userEmail ?? staff.userId,
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          subtitle: Text(
                            staff.userEmail ?? 'Staff ID: ${staff.userId.substring(0, 8)}',
                            style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant),
                          ),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              StatusBadge(status: staff.role.name.toUpperCase(), small: true),
                              const SizedBox(width: 4),
                              const Icon(Icons.edit_outlined, size: 16),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
      ),
    );
  }
}
