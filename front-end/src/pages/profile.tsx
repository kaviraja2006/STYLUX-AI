const Profile = () => {
  // Mock user data for public version
  const user = {
    fullName: "Guest User",
    emailAddresses: [{ emailAddress: "guest@example.com" }],
    imageUrl: "https://via.placeholder.com/150",
    username: "guest_user"
  };

  const handleSignOut = () => {
    console.log("Sign out clicked - no auth provider");
    window.location.href = "/";
  };

  return (
    <div>
      <h2>Welcome, {user.fullName}!</h2>
      <p>Email: {user.emailAddresses[0].emailAddress || "No email found"}</p>
      <p>Username: {user.username}</p>
      <img src={user.imageUrl} alt="User Profile" style={{ borderRadius: '50%', width: '100px', height: '100px' }} />
      <button onClick={handleSignOut}>Sign Out</button>
    </div>
  );
}

export default Profile;