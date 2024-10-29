// src/components/Profile.js
import React, { useState, useEffect } from 'react';
import './Profile.css';

const Profile = ({ userId }) => {
  const [user, setUser] = useState({
    id: '',
    username: '',
    bio: '',
    headerImage: '',
    profileImage: '',
    artworks: [],
  });

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await fetch(`http://localhost:5000/api/user/${userId}`);
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          console.error('Failed to fetch user data');
        }
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    };

    fetchUserData();
  }, [userId]);

  const [headerImage, setHeaderImage] = useState(null);
  const [profileImage, setProfileImage] = useState(null);
  const [artworkImage, setArtworkImage] = useState(null);
  const [artworkTitle, setArtworkTitle] = useState('');

  const handleHeaderChange = (e) => {
    setHeaderImage(e.target.files[0]);
  };

  const handleProfileChange = (e) => {
    setProfileImage(e.target.files[0]);
  };

  const handleArtworkChange = (e) => {
    setArtworkImage(e.target.files[0]);
  };

  const handleUploadHeader = async () => {
    if (!headerImage) return;

    const formData = new FormData();
    formData.append('image', headerImage);
    formData.append('type', 'header');

    try {
      const response = await fetch(`http://localhost:5000/api/user/${user.id}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const updatedUser = await response.json();
        setUser(updatedUser.user);
        setHeaderImage(null);
      } else {
        alert('Failed to upload header image');
      }
    } catch (error) {
      console.error('Error uploading header image:', error);
    }
  };

  const handleUploadProfile = async () => {
    if (!profileImage) return;

    const formData = new FormData();
    formData.append('image', profileImage);
    formData.append('type', 'profile');

    try {
      const response = await fetch(`http://localhost:5000/api/user/${user.id}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const updatedUser = await response.json();
        setUser(updatedUser.user);
        setProfileImage(null);
      } else {
        alert('Failed to upload profile image');
      }
    } catch (error) {
      console.error('Error uploading profile image:', error);
    }
  };

  const handleUploadArtwork = async () => {
    if (!artworkImage || !artworkTitle) return;

    const formData = new FormData();
    formData.append('title', artworkTitle);
    formData.append('image', artworkImage);
    formData.append('userId', user.id);

    try {
      const response = await fetch('http://localhost:5000/api/artworks', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const uploadedArtwork = await response.json();
        setUser((prevUser) => ({
          ...prevUser,
          artworks: [...prevUser.artworks, uploadedArtwork.artwork],
        }));
        setArtworkImage(null);
        setArtworkTitle('');
      } else {
        alert('Failed to upload artwork');
      }
    } catch (error) {
      console.error('Error uploading artwork:', error);
    }
  };

  const timestamp = new Date().getTime(); // Use this to prevent caching issues

  return (
    <div className="profile-container">
      <div className="header-image-container">
        {user.headerImage && (
          <img
            src={`${user.headerImage}?t=${timestamp}`}
            alt="Header"
            className="header-image"
          />
        )}
        <input type="file" accept="image/*" onChange={handleHeaderChange} />
        <button onClick={handleUploadHeader}>Upload Header</button>
      </div>
      <div className="profile-details">
        <div className="profile-image-container">
          <img
            src={`${user.profileImage}?t=${timestamp}`}
            alt="Profile"
            className="profile-image"
          />
        </div>
        <div className="profile-upload-controls">
          <input type="file" accept="image/*" onChange={handleProfileChange} />
          <button onClick={handleUploadProfile}>Upload Profile</button>
        </div>
        <h2>{user.username}</h2>
        <p>{user.bio}</p>
      </div>

      <h3>Uploaded Artwork</h3>
      <div className="artwork-grid">
        {user.artworks.length > 0 ? (
          user.artworks.map((artwork) => (
            <div key={artwork.id} className="artwork-item">
              <img
                src={`${artwork.imageUrl}?t=${timestamp}`}
                alt={artwork.title}
                className="artwork-image"
              />
              <div className="artwork-info">
                <h4>{artwork.title}</h4>
              </div>
            </div>
          ))
        ) : (
          <p>No artworks uploaded yet.</p>
        )}
      </div>

      <h3>Upload New Artwork</h3>
      <input type="file" accept="image/*" onChange={handleArtworkChange} />
      <input
        type="text"
        placeholder="Artwork Title"
        value={artworkTitle}
        onChange={(e) => setArtworkTitle(e.target.value)}
      />
      <button onClick={handleUploadArtwork}>Upload Artwork</button>
    </div>
  );
};

export default Profile;
