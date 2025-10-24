# Template Structure Documentation

## Base Template (base.html)
```
base.html
├── Navigation Bar
│   ├── Home Link
│   ├── Login/Register (if not authenticated)
│   └── User Menu (if authenticated)
├── Flash Messages
├── Main Content Block
└── Footer
```

## Home Page (home.html)
```
home.html
├── Hero Section
│   └── Title and Description
├── Search Section
│   ├── Search Input
│   ├── Available Categories
│   └── Search Feedback
├── Power Rankings
│   ├── Sorting Controls
│   └── Team Rankings Table
└── Tournament Section
    ├── Upcoming Tournaments
    └── Registration Modal
```

## Authentication Templates
```
login.html
├── Login Form
└── Sign Up Link

sign_up.html
├── Registration Form
└── Login Link
```

## Team Management
```
team_form.html
├── Team Details
│   ├── Team Name
│   ├── Game Selection
│   └── Captain Info
└── Player Roster

team_list.html
├── Team Filters
├── Search
└── Team Cards
```

## Tournament Management
```
tournament_form.html
├── Tournament Details
│   ├── Name
│   ├── Date
│   ├── Location
│   └── Max Teams
└── Submit Button

tournament_list.html
├── Filters
├── Tournament Cards
└── Registration Status

tournament_registrations.html
├── Registration List
├── Team Details
└── Status Updates
```

## Template Features

### 1. Responsive Design
- Bootstrap grid system
- Mobile-friendly layouts
- Responsive tables
- Collapsible navigation

### 2. Interactive Elements
- Sort controls
- Search functionality
- Modal forms
- Dynamic feedback

### 3. User Experience
- Clear navigation
- Consistent styling
- Error feedback
- Loading states

### 4. Data Display
- Tabular data
- Card layouts
- Status indicators
- Sort indicators