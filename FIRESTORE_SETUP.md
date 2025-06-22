# Firestore Security Rules Setup

## Issue
Other users can't modify their Bear Bucks because of Firestore security rules. By default, Firestore denies all read/write access unless explicitly allowed.

## Solution
You need to update your Firestore security rules in the Firebase Console.

### Step 1: Access Firestore Security Rules
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your BerkeleyBets project
3. Navigate to **Firestore Database**
4. Click on the **Rules** tab

### Step 2: Update Security Rules
Replace the existing rules with the following:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow users to read and write their own documents
    match /Users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Optional: Allow users to read other users' basic info (without sensitive data)
    match /Users/{userId} {
      allow read: if request.auth != null;
    }
  }
}
```

### Step 3: Publish the Rules
1. Click **Publish** to deploy the new rules
2. The rules should take effect immediately

## What These Rules Do

1. **Authentication Required**: Users must be logged in (`request.auth != null`)
2. **User Isolation**: Users can only modify their own documents (`request.auth.uid == userId`)
3. **Read Access**: Users can read other users' documents (for leaderboards, etc.)
4. **Write Access**: Users can only write to their own user document

## Testing the Rules

### For Logged-in Users:
- ✅ Can read/write `/Users/{their-own-uid}`
- ✅ Can read `/Users/{other-user-uid}` 
- ❌ Cannot write to `/Users/{other-user-uid}`

### For Non-authenticated Users:
- ❌ Cannot read any documents
- ❌ Cannot write any documents

## Alternative: Development Mode (NOT RECOMMENDED FOR PRODUCTION)

If you want to temporarily allow all access for testing (NOT secure):

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## Troubleshooting

### Common Errors:
- **"Permission denied"**: User not authenticated or trying to access wrong document
- **"Missing or insufficient permissions"**: Security rules blocking the operation

### Debug Steps:
1. Check browser console for detailed error messages
2. Verify user is logged in (`console.log(auth.currentUser)`)
3. Verify document path matches security rules
4. Test rules in Firebase Console using the **Rules Playground**

## Document Structure

The app expects user documents in this format:
```javascript
{
  bearBucks: 1500,
  activeBets: 0,
  wins: 0,
  losses: 0
}
```

## Next Steps

1. Update your Firestore security rules as shown above
2. Test with a different user account
3. Check browser console for any remaining errors
4. The Bear Bucks functionality should now work for all authenticated users