# Template Structure Documentation

## Base Template (base.html)
```
base.html
├── Navigation Bar (Dark theme, responsive)
│   ├── Home Link
│   ├── My Teams (authenticated users)
│   ├── Tournaments (admins only)
│   ├── Manage Rankings (admins only)
│   ├── Login/Sign Up (non-authenticated)
│   └── Logout (authenticated)
├── Flash Messages (Toast notifications)
├── Main Content Block
└── Bootstrap 4 Darkly Theme Scripts
```

## Home Page (home.html)
```
home.html
├── Hero Section
│   └── Title and Description
├── Search Section
│   ├── Category Dropdown
│   ├── Sort Controls (rank, name, points, wins)
│   └── Order Toggle (asc/desc)
├── Power Rankings Table
│   ├── Team Name
│   ├── Game
│   ├── Points
│   ├── Wins
│   └── Rank
└── Tournament Section
    ├── Upcoming Tournaments List
    └── Register/Join Buttons
```

## Authentication Templates
```
login.html
├── Login Form
│   ├── Email Input
│   ├── Password Input
│   └── Submit Button
└── Sign Up Link

sign_up.html
├── Registration Form
│   ├── Email Input
│   ├── First Name Input
│   ├── Password Inputs
│   └── Submit Button
└── Login Link
```

## Team Management
```
team_form.html (Create/Edit)
├── Team Details
│   ├── Team Name
│   ├── Game Selection (dropdown)
│   ├── Captain Phone
│   └── Tournament Location (predefined)
├── Player Roster (dynamic, 1-5 players)
└── Submit Button

team_list.html
├── User's Teams List
└── Create New Team Button

team_detail.html
├── Team Info
│   ├── Name, Game, Captain
│   ├── Points, Wins, Rank
│   └── Registration Status
├── Player Roster (editable)
└── Edit/Delete Buttons
```

## Tournament Management (Admin)
```
tournament_form.html (Create/Edit)
├── Tournament Details
│   ├── Name
│   ├── Game Name
│   ├── Location (point-a/point-b)
│   ├── Date
│   └── Max Players
└── Submit Button

tournament_list.html
├── Tournament Filters
├── Tournament Cards
│   ├── Name, Game, Date, Location
│   └── View Registrations Button
└── Create New Tournament Button

tournament_registrations.html
├── Registration List
│   ├── Team Name
│   ├── Captain
│   ├── Status (pending/approved/rejected)
│   └── Approve/Reject Buttons
└── Back to Tournaments Button

tournament_join.html
├── Tournament Info
├── Eligible Teams Dropdown
└── Join Tournament Button
```

## Ranking Management (Admin)
```
manage_rankings.html
├── Teams with Approved Registrations
│   ├── Team Name
│   ├── Current Points/Wins
│   └── Edit Ranking Button
└── Back to Home Button

edit_ranking.html
├── Team Info
├── Points Input
├── Wins Input
└── Update Button
```

## Player Management
```
player_form.html (Edit Player)
├── Player Name Input
└── Submit Button
```

## Template Features

### 1. Responsive Design
- Bootstrap 4 Darkly theme
- Mobile-first approach
- Collapsible navigation
- Responsive tables and cards

### 2. Interactive Elements
- AJAX player editing
- Dynamic form fields
- Toast notifications
- Sort and filter controls

### 3. User Experience
- Dark theme for gaming aesthetic
- Consistent navigation
- Flash message feedback
- Loading states and validation

### 4. Data Display
- Tabular rankings
- Card-based listings
- Status badges
- Sort indicators

