import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div className="container mt-5">
      <div className="jumbotron">
        <h1 className="display-4">Welcome to Art Critique</h1>
        <p className="lead">
          A community platform for artists to share work and receive constructive feedback
        </p>
        <hr className="my-4" />
        <p>
          Explore artwork, give meaningful critiques, and improve your craft through community feedback.
        </p>
        <div className="mt-4">
          <Link to="/artworks" className="btn btn-primary me-3">
            Browse Artwork
          </Link>
          <Link to="/login" className="btn btn-outline-secondary">
            Sign In
          </Link>
        </div>
      </div>
      
      <div className="row mt-5">
        <div className="col-md-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Share Your Work</h5>
              <p className="card-text">
                Upload your artwork and get valuable feedback from fellow artists and art enthusiasts.
              </p>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Give Critiques</h5>
              <p className="card-text">
                Provide thoughtful feedback on others' work and earn karma points in our community.
              </p>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Grow as an Artist</h5>
              <p className="card-text">
                Learn from feedback, improve your skills, and connect with other artists.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;