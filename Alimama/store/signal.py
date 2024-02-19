from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    # This assumes you have a mapping of group names to Profile roles
    group_role_mapping = {
        'Customers': Profile.CUSTOMER,
        'Sellers': Profile.SELLER,
        'Seller_admins': Profile.S_ADMIN,
        'Sudos': Profile.SUDO,
    }
    if created:
        # Handle new user creation logic if necessary
        Profile.objects.create(user=instance)
    # Update the role based on groups the user belongs to
    user_groups = instance.groups.all().values_list('name', flat=True)
    for group_name in user_groups:
        if group_name in group_role_mapping:
            profile = instance.profile
            profile.role = group_role_mapping[group_name]
            profile.save()
            break  # Assuming one role per user; remove if multiple roles are allowed

# This signal handles the case where a user's groups are changed


@receiver(m2m_changed, sender=User.groups.through)
def user_groups_changed(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        update_user_profile(sender, instance, False)
