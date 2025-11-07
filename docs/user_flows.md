# User Flow Documentation

## 1. User Registration & Authentication

### Registration Flow
```
1. User visits /sign-up
2. Enters email, first_name, password1, password2
3. System validates:
   - Email > 3 chars, unique
   - First name > 1 char
   - Passwords match, >= 7 chars
4. Creates user account (is_admin=False)
5. Redirects to login with success message
```

### Login Flow
```
1. User visits /login
2. Enters email, password
3. System verifies:
   - Email exists
   - Password hash matches
4. Creates session with remember=True
5. Redirects to home with success message
```

## 2. Team Management

### Creating a New Team
```
1. User clicks "Register Team" from home or "Create Team" from teams
2. System redirects to team_create with predefined game_name/location (if from tournament)
3. User enters:
   - Team name (unique)
   - Game selection (dropdown from tournaments)
   - Captain phone
   - Player names (1-max_players, default 5)
4. System validates:
   - Game selected
   - Player names not empty
   - Team name unique (case-insensitive)
5. Creates team, players, optional tournament registration
6. Redirects to teams list with success message
```

### Editing a Team
```
1. User selects team from /teams
2. Clicks "Edit" on team_detail
3. Modifies team details and player names
4. System validates game selection
5. Updates team and players
6. Redirects to team_detail with success message
```

### Joining Tournament with Existing Team
```
1. User clicks "Join" on tournament from home
2. System shows eligible teams (matching game, not approved in active tournament)
3. User selects team
4. System validates:
   - Team belongs to user
   - Game matches
   - Not already registered
   - Not approved in active tournament
5. Creates registration (status='pending')
6. Redirects to home with success message
```

## 3. Tournament Management (Admin Only)

### Creating Tournament
```
1. Admin visits /tournaments
2. Clicks "Create Tournament"
3. Enters:
   - Name, game_name, location (point-a/b), date, max_players
4. System validates max_players is integer
5. Creates tournament (archived=False)
6. Redirects to tournaments list with success message
```

### Managing Registrations
```
1. Admin views tournament registrations
2. For each registration:
   - Approve: sets status='approved'
   - Reject: sets status='rejected'
3. System commits changes
4. Shows flash message for each action
```

### Archiving Tournament
```
1. Admin clicks "Archive" on tournament
2. System sets archived=True
3. Redirects to tournaments list with success message
```

## 4. Power Rankings

### Viewing Rankings
```
1. User visits home page
2. Selects category from dropdown (VALORANT default, or other games)
3. Chooses sort (rank, name, points, wins) and order (asc/desc)
4. System filters teams with approved registrations
5. Updates rankings dynamically (points desc, wins desc)
6. Displays table with team info
```

### Admin Editing Rankings
```
1. Admin visits /manage-rankings
2. Sees teams with approved registrations
3. Clicks "Edit" on team
4. Enters new points and wins
5. System validates numeric inputs
6. Updates team stats
7. Recalculates global rankings
8. Redirects to manage_rankings with success message
```

## 5. Search and Filtering

### Category Search
```
1. User selects game from category dropdown
2. System queries teams by game_name (case-insensitive)
3. If no teams, falls back to tournament names
4. Updates rankings table
5. Shows filtered results
```

## 6. Error Handling

### Authentication Errors
```
- Invalid email/password: flash error, stay on login
- Email exists on signup: flash error, stay on signup
- Password mismatch: flash error, stay on signup
```

### Team Creation Errors
```
- Team name exists: flash error, stay on form
- Game not selected: flash error, stay on form
- Player name empty: flash error, stay on form
- Admins cannot create teams: flash error, redirect home
```

### Tournament Registration Errors
```
- No team exists: flash error, redirect home
- Game mismatch: flash error, redirect home
- Already registered: flash error, redirect home
- Already approved in active tournament: flash error, redirect home
- Tournament not found: flash error, redirect home
```

### Admin Access Errors
```
- Non-admin tries admin routes: abort(403)
```

## 7. Data Updates

### Real-time Ranking Updates
```
- On home page load: recalculates ranks for filtered teams
- After admin edits: updates points/wins, commits, recalculates ranks
```

### Registration Status Notifications
```
- On team_detail: shows flash messages for approved/rejected registrations
```
