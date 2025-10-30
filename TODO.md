# TODO: Separate Admin and User Functions

## Steps to Complete
- [ ] Update User model to add is_admin flag
- [ ] Create @admin_required decorator
- [ ] Protect tournament CRUD routes with @admin_required
- [ ] Add is_active field to Team model for archiving
- [ ] Restrict user team edits to before registration
- [ ] Restrict adding players after team registration
- [ ] Add routes for admins to manage points and wins
- [ ] Update templates to conditionally show admin features
- [ ] Add archive team functionality for users
- [ ] Test role-based access
